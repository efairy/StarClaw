# -*- coding: utf-8 -*-
"""External agent calling utilities."""
from .caller import (
    build_request_payload,
    build_request_headers,
    detect_api_format,
    extract_sse_text,
    extract_response_text,
)

__all__ = [
    "build_request_payload",
    "build_request_headers",
    "detect_api_format",
    "extract_sse_text",
    "extract_response_text",
]
