# -*- coding: utf-8 -*-
"""Tool for calling external agents from within a StarClaw agent."""

from __future__ import annotations

import json
import logging
from typing import Optional

import httpx
from agentscope.message import TextBlock
from agentscope.tool import ToolResponse

from ...config.config import (
    ExternalAgentConfig,
    load_agent_config,
)
from ...external.caller import (
    build_request_headers,
    build_request_payload,
    detect_api_format,
    extract_response_text,
    extract_sse_text,
)

logger = logging.getLogger(__name__)

_CALL_TIMEOUT = 300.0  # 5 minutes


def create_call_external_agent_tool(agent_id: str):
    """Create a call_external_agent tool bound to a specific agent config.

    Args:
        agent_id: The agent ID to load external config from.

    Returns:
        An async tool function for calling external agents.
    """

    async def call_external_agent(
        agent_key: str,
        text: str,
        stream: Optional[bool] = None,
    ) -> ToolResponse:
        """Call an external agent by key and return its response.

        Use this tool when you need to delegate a task to an external
        agent that has been configured in the External Agents settings.
        Use `list_external_agents` first if you don't know which agents
        are available.

        Args:
            agent_key: The unique key of the external agent to call.
            text: The user input / question to send to the external agent.
            stream: Override streaming setting (None uses agent default).

        Returns:
            `ToolResponse`: The external agent's response text.
        """
        try:
            config = load_agent_config(agent_id)
        except Exception as e:
            return _error(f"Failed to load agent config: {e}")

        if config.external is None or not config.external.agents:
            return _error(
                "No external agents configured. "
                "Configure them in Console > Agent > External."
            )

        ext_agent = config.external.agents.get(agent_key)
        if ext_agent is None:
            available = ", ".join(config.external.agents.keys())
            return _error(
                f"External agent '{agent_key}' not found. "
                f"Available: {available}"
            )

        if not ext_agent.enabled:
            return _error(f"External agent '{agent_key}' is disabled.")

        if not ext_agent.url:
            return _error(
                f"External agent '{agent_key}' has no URL configured."
            )

        return await _do_call(ext_agent, text, stream)

    return call_external_agent


def create_list_external_agents_tool(agent_id: str):
    """Create a list_external_agents tool bound to a specific agent config.

    Args:
        agent_id: The agent ID to load external config from.

    Returns:
        An async tool function that lists available external agents.
    """

    async def list_external_agents() -> ToolResponse:
        """List all configured external agents and their status.

        Call this tool to discover which external agents are available
        before calling `call_external_agent`.

        Returns:
            `ToolResponse`: A list of external agents with their keys,
                names, descriptions, and enabled status.
        """
        try:
            config = load_agent_config(agent_id)
        except Exception as e:
            return _error(f"Failed to load agent config: {e}")

        if config.external is None or not config.external.agents:
            return _text("No external agents configured.")

        lines = []
        for key, agent in config.external.agents.items():
            status = "enabled" if agent.enabled else "disabled"
            desc = agent.description or "(no description)"
            lines.append(
                f"- {key}: {agent.name} [{status}] — {desc}"
            )

        return _text("\n".join(lines))

    return list_external_agents


async def _do_call(
    ext_agent: ExternalAgentConfig,
    text: str,
    stream: Optional[bool] = None,
) -> ToolResponse:
    """Execute the HTTP call to the external agent."""
    use_stream = stream if stream is not None else ext_agent.stream
    fmt = detect_api_format(ext_agent)
    headers = build_request_headers(ext_agent, use_stream)
    payload = build_request_payload(ext_agent, text, use_stream)

    try:
        async with httpx.AsyncClient(timeout=_CALL_TIMEOUT) as client:
            if use_stream:
                return await _call_streaming(client, ext_agent, headers,
                                             payload, fmt)
            else:
                return await _call_non_streaming(client, ext_agent,
                                                 headers, payload, fmt)
    except httpx.TimeoutException:
        return _error(
            f"External agent '{ext_agent.name}' timed out "
            f"after {_CALL_TIMEOUT}s."
        )
    except httpx.ConnectError:
        return _error(
            f"Cannot connect to external agent '{ext_agent.name}' "
            f"at {ext_agent.url}."
        )
    except Exception as e:
        logger.exception("External agent call failed: %s", e)
        return _error(f"External agent call failed: {e}")


async def _call_streaming(
    client: httpx.AsyncClient,
    ext_agent: ExternalAgentConfig,
    headers: dict,
    payload: dict,
    fmt: str,
) -> ToolResponse:
    """Handle streaming response from external agent."""
    parts = []
    async with client.stream(
        "POST", ext_agent.url, headers=headers, json=payload,
    ) as resp:
        if resp.status_code != 200:
            body = await resp.aread()
            return _error(
                f"HTTP {resp.status_code}: "
                f"{body.decode('utf-8', errors='replace')}"
            )
        async for line in resp.aiter_lines():
            line = line.strip()
            if not line:
                continue
            if line.startswith("data:"):
                data_str = line[5:].strip()
                if data_str == "[DONE]":
                    break
                try:
                    data = json.loads(data_str)
                    chunk = extract_sse_text(data, fmt)
                    if chunk:
                        parts.append(chunk)
                except json.JSONDecodeError:
                    parts.append(data_str)

    result = "".join(parts)
    if not result:
        return _text("(External agent returned empty response)")
    return _text(result)


async def _call_non_streaming(
    client: httpx.AsyncClient,
    ext_agent: ExternalAgentConfig,
    headers: dict,
    payload: dict,
    fmt: str,
) -> ToolResponse:
    """Handle non-streaming response from external agent."""
    resp = await client.post(
        ext_agent.url, headers=headers, json=payload,
    )
    if resp.status_code != 200:
        return _error(f"HTTP {resp.status_code}: {resp.text}")

    try:
        data = resp.json()
        text = extract_response_text(data, fmt)
        if text:
            return _text(text)
    except (json.JSONDecodeError, ValueError):
        pass

    return _text(resp.text or "(External agent returned empty response)")


def _text(text: str) -> ToolResponse:
    return ToolResponse(
        content=[TextBlock(type="text", text=text)],
    )


def _error(msg: str) -> ToolResponse:
    return ToolResponse(
        content=[TextBlock(type="text", text=f"Error: {msg}")],
    )
