# -*- coding: utf-8 -*-
"""API routes for External agents management."""

from __future__ import annotations

import json
import logging
from typing import AsyncGenerator, Dict, List, Optional

import httpx
from fastapi import APIRouter, Body, HTTPException, Path, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from ..utils import schedule_agent_reload
from ...config.config import ExternalAgentConfig

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/external", tags=["external"])


class ExternalAgentInfo(BaseModel):
    """External agent information for API responses."""

    key: str = Field(..., description="Unique agent key identifier")
    name: str = Field(..., description="Agent display name")
    description: str = Field(default="", description="Agent description")
    enabled: bool = Field(..., description="Whether the agent is enabled")
    url: str = Field(default="", description="Agent API endpoint URL")
    api_key: str = Field(default="", description="API key (masked)")
    headers: Dict[str, str] = Field(
        default_factory=dict,
        description="HTTP headers",
    )
    stream: bool = Field(default=True, description="Enable streaming output")
    background: bool = Field(
        default=False,
        description="Enable async execution",
    )
    format: str = Field(
        default="auto",
        description="API format: auto, dashscope_v1, openai_responses",
    )


class ExternalAgentCreateRequest(BaseModel):
    """Request body for creating an external agent."""

    name: str = Field(..., description="Agent display name")
    description: str = Field(default="", description="Agent description")
    enabled: bool = Field(
        default=True,
        description="Whether to enable the agent",
    )
    url: str = Field(default="", description="Agent API endpoint URL")
    api_key: str = Field(default="", description="API key")
    headers: Dict[str, str] = Field(
        default_factory=dict,
        description="HTTP headers",
    )
    stream: bool = Field(default=True, description="Enable streaming output")
    background: bool = Field(
        default=False,
        description="Enable async execution",
    )
    format: str = Field(
        default="auto",
        description="API format: auto, dashscope_v1, openai_responses",
    )


class ExternalAgentUpdateRequest(BaseModel):
    """Request body for updating an external agent (all fields optional)."""

    name: Optional[str] = Field(None, description="Agent display name")
    description: Optional[str] = Field(None, description="Agent description")
    enabled: Optional[bool] = Field(
        None,
        description="Whether to enable the agent",
    )
    url: Optional[str] = Field(None, description="Agent API endpoint URL")
    api_key: Optional[str] = Field(None, description="API key")
    headers: Optional[Dict[str, str]] = Field(
        None,
        description="HTTP headers",
    )
    stream: Optional[bool] = Field(
        None,
        description="Enable streaming output",
    )
    background: Optional[bool] = Field(
        None,
        description="Enable async execution",
    )
    format: Optional[str] = Field(
        None,
        description="API format: auto, dashscope_v1, openai_responses",
    )


def _mask_value(value: str) -> str:
    """Mask sensitive value showing first 2-3 chars and last 4 chars."""
    if not value:
        return value

    length = len(value)
    if length <= 8:
        return "*" * length

    prefix_len = 3 if length > 2 and value[2] == "-" else 2
    prefix = value[:prefix_len]
    suffix = value[-4:]
    masked_len = max(length - prefix_len - 4, 4)

    return f"{prefix}{'*' * masked_len}{suffix}"


def _build_agent_info(
    key: str, agent: ExternalAgentConfig
) -> ExternalAgentInfo:
    """Build ExternalAgentInfo from config with masked sensitive values."""
    masked_headers = (
        {k: _mask_value(v) for k, v in agent.headers.items()}
        if agent.headers
        else {}
    )

    return ExternalAgentInfo(
        key=key,
        name=agent.name,
        description=agent.description,
        enabled=agent.enabled,
        url=agent.url,
        api_key=_mask_value(agent.api_key),
        headers=masked_headers,
        stream=agent.stream,
        background=agent.background,
        format=agent.format,
    )


@router.get(
    "",
    response_model=List[ExternalAgentInfo],
    summary="List all external agents",
)
async def list_external_agents(
    request: Request,
) -> List[ExternalAgentInfo]:
    """Get list of all configured external agents."""
    from ..agent_context import get_agent_for_request

    agent = await get_agent_for_request(request)
    ext_config = agent.config.external
    if ext_config is None or not ext_config.agents:
        return []

    return [
        _build_agent_info(key, ext_agent)
        for key, ext_agent in ext_config.agents.items()
    ]


@router.get(
    "/{agent_key}",
    response_model=ExternalAgentInfo,
    summary="Get external agent details",
)
async def get_external_agent(
    request: Request,
    agent_key: str = Path(...),
) -> ExternalAgentInfo:
    """Get details of a specific external agent."""
    from ..agent_context import get_agent_for_request

    agent = await get_agent_for_request(request)
    ext_config = agent.config.external
    if ext_config is None:
        raise HTTPException(
            404, detail=f"External agent '{agent_key}' not found"
        )

    ext_agent = ext_config.agents.get(agent_key)
    if ext_agent is None:
        raise HTTPException(
            404, detail=f"External agent '{agent_key}' not found"
        )
    return _build_agent_info(agent_key, ext_agent)


@router.post(
    "",
    response_model=ExternalAgentInfo,
    summary="Create a new external agent",
    status_code=201,
)
async def create_external_agent(
    request: Request,
    agent_key: str = Body(..., embed=True),
    ext_agent: ExternalAgentCreateRequest = Body(
        ..., embed=True, alias="agent"
    ),
) -> ExternalAgentInfo:
    """Create a new external agent configuration."""
    from ..agent_context import get_agent_for_request
    from ...config.config import save_agent_config, ExternalConfig

    agent = await get_agent_for_request(request)

    if agent.config.external is None:
        agent.config.external = ExternalConfig(agents={})

    if agent_key in agent.config.external.agents:
        raise HTTPException(
            400,
            detail=f"External agent '{agent_key}' already exists. "
            f"Use PUT to update.",
        )

    new_agent = ExternalAgentConfig(
        name=ext_agent.name,
        description=ext_agent.description,
        enabled=ext_agent.enabled,
        url=ext_agent.url,
        api_key=ext_agent.api_key,
        headers=ext_agent.headers,
        stream=ext_agent.stream,
        background=ext_agent.background,
        format=ext_agent.format,
    )

    agent.config.external.agents[agent_key] = new_agent
    save_agent_config(agent.agent_id, agent.config)
    schedule_agent_reload(request, agent.agent_id)

    return _build_agent_info(agent_key, new_agent)


@router.put(
    "/{agent_key}",
    response_model=ExternalAgentInfo,
    summary="Update an external agent",
)
async def update_external_agent(
    request: Request,
    agent_key: str = Path(...),
    updates: ExternalAgentUpdateRequest = Body(...),
) -> ExternalAgentInfo:
    """Update an existing external agent configuration."""
    from ..agent_context import get_agent_for_request
    from ...config.config import save_agent_config

    agent = await get_agent_for_request(request)

    if (
        agent.config.external is None
        or agent_key not in agent.config.external.agents
    ):
        raise HTTPException(
            404, detail=f"External agent '{agent_key}' not found"
        )

    existing = agent.config.external.agents[agent_key]
    update_data = updates.model_dump(exclude_unset=True)

    # For api_key: skip if it looks like a masked value
    if "api_key" in update_data and update_data["api_key"]:
        if "*" * 4 in update_data["api_key"]:
            del update_data["api_key"]

    # For headers: merge with existing, don't replace
    if "headers" in update_data and update_data["headers"] is not None:
        updated_headers = existing.headers.copy() if existing.headers else {}
        for k, v in update_data["headers"].items():
            if "*" * 4 not in v:
                updated_headers[k] = v
        update_data["headers"] = updated_headers

    merged_data = existing.model_dump(mode="json")
    merged_data.update(update_data)
    updated_agent = ExternalAgentConfig.model_validate(merged_data)
    agent.config.external.agents[agent_key] = updated_agent

    save_agent_config(agent.agent_id, agent.config)
    schedule_agent_reload(request, agent.agent_id)

    return _build_agent_info(agent_key, updated_agent)


@router.patch(
    "/{agent_key}/toggle",
    response_model=ExternalAgentInfo,
    summary="Toggle external agent enabled status",
)
async def toggle_external_agent(
    request: Request,
    agent_key: str = Path(...),
) -> ExternalAgentInfo:
    """Toggle the enabled status of an external agent."""
    from ..agent_context import get_agent_for_request
    from ...config.config import save_agent_config

    agent = await get_agent_for_request(request)

    if (
        agent.config.external is None
        or agent_key not in agent.config.external.agents
    ):
        raise HTTPException(
            404, detail=f"External agent '{agent_key}' not found"
        )

    ext_agent = agent.config.external.agents[agent_key]
    ext_agent.enabled = not ext_agent.enabled
    save_agent_config(agent.agent_id, agent.config)
    schedule_agent_reload(request, agent.agent_id)

    return _build_agent_info(agent_key, ext_agent)


@router.delete(
    "/{agent_key}",
    response_model=Dict[str, str],
    summary="Delete an external agent",
)
async def delete_external_agent(
    request: Request,
    agent_key: str = Path(...),
) -> Dict[str, str]:
    """Delete an external agent configuration."""
    from ..agent_context import get_agent_for_request
    from ...config.config import save_agent_config

    agent = await get_agent_for_request(request)

    if (
        agent.config.external is None
        or agent_key not in agent.config.external.agents
    ):
        raise HTTPException(
            404, detail=f"External agent '{agent_key}' not found"
        )

    del agent.config.external.agents[agent_key]
    save_agent_config(agent.agent_id, agent.config)
    schedule_agent_reload(request, agent.agent_id)

    return {
        "message": f"External agent '{agent_key}' deleted successfully"
    }


class ExternalAgentCallRequest(BaseModel):
    """Request body for calling an external agent."""

    text: str = Field(..., description="User input text")
    stream: Optional[bool] = Field(
        None,
        description="Override streaming setting",
    )


async def _call_external_agent_stream(
    ext_agent: ExternalAgentConfig,
    text: str,
    stream: Optional[bool] = None,
) -> AsyncGenerator[str, None]:
    """Call an external agent and yield SSE data lines."""
    from ...external.caller import (
        build_request_headers,
        build_request_payload,
        detect_api_format,
        extract_response_text,
        extract_sse_text,
    )

    use_stream = stream if stream is not None else ext_agent.stream
    fmt = detect_api_format(ext_agent)
    headers = build_request_headers(ext_agent, use_stream)
    payload = build_request_payload(ext_agent, text, use_stream)

    try:
        async with httpx.AsyncClient(timeout=300.0) as client:
            if use_stream:
                async with client.stream(
                    "POST",
                    ext_agent.url,
                    headers=headers,
                    json=payload,
                ) as resp:
                    if resp.status_code != 200:
                        body = await resp.aread()
                        err = {
                            "error": f"HTTP {resp.status_code}: "
                            f"{body.decode('utf-8', errors='replace')}"
                        }
                        yield f"data: {json.dumps(err)}\n\n"
                        return
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
                                    yield (
                                        f"data: {json.dumps({'text': chunk})}"
                                        f"\n\n"
                                    )
                            except json.JSONDecodeError:
                                yield f"data: {line}\n\n"
                        else:
                            yield (
                                f"data: {json.dumps({'text': line})}\n\n"
                            )
            else:
                resp = await client.post(
                    ext_agent.url,
                    headers=headers,
                    json=payload,
                )
                if resp.status_code != 200:
                    err = {
                        "error": f"HTTP {resp.status_code}: "
                        f"{resp.text}"
                    }
                    yield f"data: {json.dumps(err)}\n\n"
                    return
                try:
                    data = resp.json()
                    result = extract_response_text(data, fmt)
                    yield (
                        f"data: {json.dumps({'text': result or resp.text})}"
                        f"\n\n"
                    )
                except (json.JSONDecodeError, ValueError):
                    yield (
                        f"data: {json.dumps({'text': resp.text})}\n\n"
                    )

        yield f"data: {json.dumps({'done': True})}\n\n"
    except httpx.TimeoutException:
        yield f"data: {json.dumps({'error': 'Request timed out'})}\n\n"
    except Exception as e:
        logger.exception("External agent call failed: %s", e)
        yield (
            f"data: {json.dumps({'error': str(e)})}\n\n"
        )


@router.post(
    "/{agent_key}/call",
    summary="Call an external agent",
)
async def call_external_agent(
    request: Request,
    agent_key: str = Path(...),
    body: ExternalAgentCallRequest = Body(...),
) -> StreamingResponse:
    """Call an external agent and stream the response."""
    from ..agent_context import get_agent_for_request

    agent = await get_agent_for_request(request)

    if (
        agent.config.external is None
        or agent_key not in agent.config.external.agents
    ):
        raise HTTPException(
            404, detail=f"External agent '{agent_key}' not found"
        )

    ext_agent = agent.config.external.agents[agent_key]
    if not ext_agent.enabled:
        raise HTTPException(
            400,
            detail=f"External agent '{agent_key}' is disabled",
        )

    return StreamingResponse(
        _call_external_agent_stream(ext_agent, body.text, body.stream),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
