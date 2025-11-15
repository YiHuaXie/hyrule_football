"""
HTTP 客户端异常定义
"""


class HTTPClientError(Exception):
    """HTTP 客户端基础异常"""
    
    def __init__(self, message: str, status_code: int = None, response_data: dict = None):
        self.message = message
        self.status_code = status_code
        self.response_data = response_data
        super().__init__(self.message)
    
    def __str__(self):
        if self.status_code:
            return f"[{self.status_code}] {self.message}"
        return self.message


class HTTPRequestError(HTTPClientError):
    """HTTP 请求错误"""
    pass


class HTTPResponseError(HTTPClientError):
    """HTTP 响应错误"""
    pass


class HTTPTimeoutError(HTTPClientError):
    """HTTP 超时错误"""
    pass


class HTTPConnectionError(HTTPClientError):
    """HTTP 连接错误"""
    pass


class HTTPAuthenticationError(HTTPClientError):
    """HTTP 认证错误"""
    pass


class HTTPRateLimitError(HTTPClientError):
    """HTTP 限流错误"""
    pass

