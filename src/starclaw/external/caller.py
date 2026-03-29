# -*- coding: utf-8 -*-
"""Shared utilities for calling external agents."""

from __future__ import annotations

from typing import Dict

from ..config.config import ExternalAgentConfig


def detect_api_format(ext_agent: ExternalAgentConfig) -> str:
    """Detect API format from agent config and URL.

    Returns:
        "dashscope_v1" or "openai_responses"
    """
    if ext_agent.format and ext_agent.format != "auto":
        return ext_agent.format

    url = ext_agent.url
    # DashScope v1: /api/v1/apps/{id}/completion
    if "/api/v1/" in url and "/completion" in url:
        return "dashscope_v1"
    # DashScope v2 compatible-mode: /compatible-mode/v1/responses
    if "/compatible-mode/" in url or "/v2/" in url:
        return "openai_responses"
    # Default to openai_responses
    return "openai_responses"


def build_request_headers(
    ext_agent: ExternalAgentConfig,
    use_stream: bool = False,
) -> Dict[str, str]:
    """Build HTTP headers for external agent call."""
    headers = {"Content-Type": "application/json"}
    if ext_agent.api_key:
        headers["Authorization"] = f"Bearer {ext_agent.api_key}"

    fmt = detect_api_format(ext_agent)
    # DashScope v1 requires X-DashScope-SSE header for streaming
    if fmt == "dashscope_v1" and use_stream:
        headers["X-DashScope-SSE"] = "enable"

    if ext_agent.headers:
        headers.update(ext_agent.headers)
    return headers


def build_request_payload(
    ext_agent: ExternalAgentConfig,
    text: str,
    use_stream: bool,
) -> dict:
    """Build request payload based on detected API format."""
    fmt = detect_api_format(ext_agent)

    if fmt == "dashscope_v1":
        payload: dict = {
            "input": {"prompt": text},
            "parameters": {"incremental_output": use_stream},
        }
        return payload

    # openai_responses format (DashScope v2 compatible-mode)
    return {
        "input": [
            {
                "type": "message",
                "role": "user",
                "content": [{"type": "input_text", "text": text}],
            },
        ],
        "stream": use_stream,
        "background": ext_agent.background,
    }


def extract_sse_text(data: dict, fmt: str) -> str:
    """Extract text content from an SSE data object.

    Args:
        data: Parsed JSON from SSE data line
        fmt: API format ("dashscope_v1" or "openai_responses")
    """
    if fmt == "dashscope_v1":
        # DashScope v1 SSE: {"output": {"text": "..."}, ...}
        output = data.get("output", {})
        if isinstance(output, dict):
            return output.get("text", "")
        return ""

    # openai_responses / generic formats
    # OpenAI Responses API: {"type": "response.output_text.delta",
    #                        "delta": "..."}
    if data.get("type") == "response.output_text.delta":
        return data.get("delta", "")
    # Simple text field
    if "text" in data:
        return data["text"]
    # output list > content > text pattern
    output = data.get("output", [])
    if isinstance(output, list):
        for item in output:
            if isinstance(item, dict):
                content = item.get("content", [])
                if isinstance(content, list):
                    for block in content:
                        if (isinstance(block, dict)
                                and block.get("type") == "text"):
                            return block.get("text", "")
    return ""


def extract_response_text(data: dict, fmt: str) -> str:
    """Extract text content from a full (non-streaming) response.

    Args:
        data: Full response JSON
        fmt: API format
    """
    if fmt == "dashscope_v1":
        output = data.get("output", {})
        if isinstance(output, dict):
            return output.get("text", "")
        return ""

    # openai_responses / generic
    output = data.get("output", [])
    if isinstance(output, list):
        texts = []
        for item in output:
            if isinstance(item, dict):
                content = item.get("content", [])
                if isinstance(content, list):
                    for block in content:
                        if (isinstance(block, dict)
                                and block.get("type") == "text"):
                            texts.append(block.get("text", ""))
                elif isinstance(content, str):
                    texts.append(content)
        if texts:
            return "\n".join(texts)
    if "text" in data:
        return data["text"]
    choices = data.get("choices", [])
    if choices:
        msg = choices[0].get("message", {})
        return msg.get("content", "")
    return ""
