"""
简单的 HTTP/HTTPS 请求客户端

功能：
- 支持 GET、POST 请求
- 支持自定义 headers
- 自动检测 response status code
- 简单的异常处理
"""

import requests
from typing import Optional, Dict, Any
from hyrule_football.utils import get_logger
from urllib.parse import urljoin

logger = get_logger(__name__)


class HTTPClientError(Exception):
    """HTTP 客户端基础异常"""

    pass


class HTTPStatusError(HTTPClientError):
    """HTTP 状态码异常"""

    def __init__(self, status_code: int, message: str, response: requests.Response):
        self.status_code = status_code
        self.message = message
        self.response = response
        super().__init__(f"HTTP {status_code}: {message}")


class HTTPTimeoutError(HTTPClientError):
    """HTTP 请求超时异常"""

    pass


class HTTPConnectionError(HTTPClientError):
    """HTTP 连接异常"""

    pass


class HTTPClient:
    """简单的 HTTP/HTTPS 客户端

    使用示例：
        client = HTTPClient(base_url="https://api.example.com", timeout=10)

        # GET 请求
        data = client.get("/users", params={"page": 1})

        # POST 请求
        data = client.post("/users", json={"name": "张三"})

        # 自定义 headers
        client.headers["Authorization"] = "Bearer token123"
        data = client.get("/protected")
    """

    def __init__(
        self,
        base_url: str = "",
        timeout: int = 10,
        headers: Optional[Dict[str, str]] = None,
        verify_ssl: bool = True,
    ):
        """初始化 HTTP 客户端

        Args:
            base_url: 基础 URL，例如 "https://api.example.com"
            timeout: 请求超时时间（秒）
            headers: 默认请求头
            verify_ssl: 是否验证 SSL 证书
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self.headers = headers or {}

        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def _build_url(self, path: str) -> str:
        """构建完整 URL"""
        if path.startswith("http://") or path.startswith("https://"):
            return path

        if self.base_url:
            return urljoin(self.base_url + "/", path.lstrip("/"))
        return path

    def _handle_response(self, response: requests.Response) -> Any:
        """处理响应，检查状态码"""
        # 2xx 状态码认为是成功
        if 200 <= response.status_code < 300:
            # 尝试解析 JSON，如果失败返回文本
            try:
                return response.json()
            except ValueError:
                return response.text

        # 4xx 客户端错误
        if 400 <= response.status_code < 500:
            raise HTTPStatusError(
                status_code=response.status_code,
                message=f"Client error: {response.text[:200]}",
                response=response,
            )

        # 5xx 服务器错误
        if 500 <= response.status_code < 600:
            raise HTTPStatusError(
                status_code=response.status_code,
                message=f"Server error: {response.text[:200]}",
                response=response,
            )

        # 其他状态码
        raise HTTPStatusError(
            status_code=response.status_code,
            message=f"Unexpected status: {response.text[:200]}",
            response=response,
        )

    def get(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> Any:
        """发送 GET 请求

        Args:
            path: 请求路径，例如 "/users" 或完整 URL
            params: URL 查询参数
            headers: 本次请求的额外 headers（会与默认 headers 合并）
            **kwargs: 其他传递给 requests.get 的参数

        Returns:
            响应数据（JSON 或文本）

        Raises:
            HTTPStatusError: 状态码异常
            HTTPTimeoutError: 请求超时
            HTTPConnectionError: 连接失败
        """
        url = self._build_url(path)
        request_headers = {**self.headers, **(headers or {})}

        try:
            logger.debug(f"GET {url}, params={params}")
            response = self.session.get(
                url,
                params=params,
                headers=request_headers,
                timeout=self.timeout,
                verify=self.verify_ssl,
                **kwargs,
            )
            return self._handle_response(response)
        except requests.Timeout as e:
            raise HTTPTimeoutError(f"Request timeout: {url}") from e
        except requests.ConnectionError as e:
            raise HTTPConnectionError(f"Connection failed: {url}") from e

    def post(
        self,
        path: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> Any:
        """发送 POST 请求

        Args:
            path: 请求路径，例如 "/users" 或完整 URL
            data: 表单数据（application/x-www-form-urlencoded）
            json: JSON 数据（application/json）
            headers: 本次请求的额外 headers（会与默认 headers 合并）
            **kwargs: 其他传递给 requests.post 的参数

        Returns:
            响应数据（JSON 或文本）

        Raises:
            HTTPStatusError: 状态码异常
            HTTPTimeoutError: 请求超时
            HTTPConnectionError: 连接失败
        """
        url = self._build_url(path)
        request_headers = {**self.headers, **(headers or {})}

        try:
            logger.debug(f"POST {url}, data={data}, json={json}")
            response = self.session.post(
                url,
                data=data,
                json=json,
                headers=request_headers,
                timeout=self.timeout,
                verify=self.verify_ssl,
                **kwargs,
            )
            return self._handle_response(response)
        except requests.Timeout as e:
            raise HTTPTimeoutError(f"Request timeout: {url}") from e
        except requests.ConnectionError as e:
            raise HTTPConnectionError(f"Connection failed: {url}") from e

    def close(self):
        """关闭 session"""
        self.session.close()

    def __enter__(self):
        """支持上下文管理器"""
        return self

    def __exit__(self, _exc_type, _exc_val, _exc_tb):
        """退出上下文时关闭 session"""
        self.close()
