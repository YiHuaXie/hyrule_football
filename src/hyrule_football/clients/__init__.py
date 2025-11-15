"""
HTTP 客户端模块
"""

from .http_client import HTTPClient
from .exceptions import (
    HTTPClientError,
    HTTPRequestError,
    HTTPResponseError,
    HTTPTimeoutError,
    HTTPConnectionError,
    HTTPAuthenticationError,
    HTTPRateLimitError,
)

# 异步客户端（可选，需要安装 httpx）
try:
    from .async_http_client import AsyncHTTPClient
    __all__ = [
        "HTTPClient",
        "AsyncHTTPClient",
        "HTTPClientError",
        "HTTPRequestError",
        "HTTPResponseError",
        "HTTPTimeoutError",
        "HTTPConnectionError",
        "HTTPAuthenticationError",
        "HTTPRateLimitError",
    ]
except ImportError:
    __all__ = [
        "HTTPClient",
        "HTTPClientError",
        "HTTPRequestError",
        "HTTPResponseError",
        "HTTPTimeoutError",
        "HTTPConnectionError",
        "HTTPAuthenticationError",
        "HTTPRateLimitError",
    ]

