# """
# 异步 HTTP 客户端封装

# 基于 httpx 实现异步请求
# """

# import logging
# from typing import Optional, Dict, Any, Union
# from urllib.parse import urljoin

# try:
#     import httpx
# except ImportError:
#     httpx = None

# from .exceptions import (
#     HTTPRequestError,
#     HTTPResponseError,
#     HTTPTimeoutError,
#     HTTPConnectionError,
#     HTTPAuthenticationError,
#     HTTPRateLimitError,
# )

# logger = logging.getLogger(__name__)


# class AsyncHTTPClient:
#     """
#     异步 HTTP 客户端
    
#     特性：
#     - 异步请求
#     - 自动重试
#     - 超时控制
#     - 请求/响应日志
#     - 异常处理
    
#     需要安装: pip install httpx
#     """
    
#     def __init__(
#         self,
#         base_url: str = "",
#         timeout: int = 30,
#         max_retries: int = 3,
#         headers: Optional[Dict[str, str]] = None,
#         verify_ssl: bool = True,
#     ):
#         """
#         初始化异步 HTTP 客户端
        
#         参数:
#             base_url: 基础 URL
#             timeout: 请求超时时间（秒）
#             max_retries: 最大重试次数
#             headers: 默认请求头
#             verify_ssl: 是否验证 SSL 证书
#         """
#         if httpx is None:
#             raise ImportError("请安装 httpx: pip install httpx")
        
#         self.base_url = base_url.rstrip("/") if base_url else ""
#         self.timeout = timeout
#         self.verify_ssl = verify_ssl
#         self.max_retries = max_retries
        
#         # 默认请求头
#         self.default_headers = {
#             "User-Agent": "HyruleFootball/0.1.0",
#             "Accept": "application/json",
#             "Content-Type": "application/json",
#         }
        
#         if headers:
#             self.default_headers.update(headers)
        
#         # 创建客户端（延迟初始化）
#         self._client: Optional[httpx.AsyncClient] = None
    
#     async def _get_client(self) -> httpx.AsyncClient:
#         """获取或创建客户端"""
#         if self._client is None:
#             self._client = httpx.AsyncClient(
#                 base_url=self.base_url,
#                 timeout=self.timeout,
#                 headers=self.default_headers,
#                 verify=self.verify_ssl,
#             )
#         return self._client
    
#     def _build_url(self, endpoint: str) -> str:
#         """构建完整 URL"""
#         if endpoint.startswith("http://") or endpoint.startswith("https://"):
#             return endpoint
        
#         if self.base_url:
#             return urljoin(self.base_url + "/", endpoint.lstrip("/"))
#         return endpoint
    
#     async def _handle_response(self, response: httpx.Response) -> Dict[str, Any]:
#         """处理响应"""
#         try:
#             # 检查状态码
#             if response.status_code == 401:
#                 raise HTTPAuthenticationError(
#                     "认证失败",
#                     status_code=response.status_code,
#                     response_data=response.json() if response.content else None,
#                 )
            
#             if response.status_code == 429:
#                 raise HTTPRateLimitError(
#                     "请求频率超限",
#                     status_code=response.status_code,
#                     response_data=response.json() if response.content else None,
#                 )
            
#             response.raise_for_status()
            
#             # 解析 JSON
#             if response.content:
#                 return response.json()
#             return {}
            
#         except Exception as e:
#             logger.error(f"响应处理失败: {e}")
#             raise HTTPResponseError(
#                 f"响应处理失败: {str(e)}",
#                 status_code=response.status_code,
#             )
    
#     async def get(
#         self,
#         endpoint: str,
#         params: Optional[Dict[str, Any]] = None,
#         headers: Optional[Dict[str, str]] = None,
#         timeout: Optional[int] = None,
#     ) -> Dict[str, Any]:
#         """
#         发送异步 GET 请求
        
#         参数:
#             endpoint: API 端点
#             params: 查询参数
#             headers: 额外的请求头
#             timeout: 超时时间（覆盖默认值）
        
#         返回:
#             响应数据（JSON）
#         """
#         url = self._build_url(endpoint)
#         client = await self._get_client()
        
#         logger.info(f"GET {url}")
#         logger.debug(f"Params: {params}")
        
#         try:
#             response = await client.get(
#                 url,
#                 params=params,
#                 headers=headers,
#                 timeout=timeout or self.timeout,
#             )
#             return await self._handle_response(response)
            
#         except httpx.TimeoutException as e:
#             logger.error(f"请求超时: {e}")
#             raise HTTPTimeoutError(f"请求超时: {str(e)}")
#         except httpx.ConnectError as e:
#             logger.error(f"连接错误: {e}")
#             raise HTTPConnectionError(f"连接错误: {str(e)}")
#         except httpx.RequestError as e:
#             logger.error(f"请求失败: {e}")
#             raise HTTPRequestError(f"请求失败: {str(e)}")

#     async def post(
#         self,
#         endpoint: str,
#         data: Optional[Union[Dict[str, Any], list]] = None,
#         json: Optional[Union[Dict[str, Any], list]] = None,
#         headers: Optional[Dict[str, str]] = None,
#         timeout: Optional[int] = None,
#     ) -> Dict[str, Any]:
#         """发送异步 POST 请求"""
#         url = self._build_url(endpoint)
#         client = await self._get_client()

#         logger.info(f"POST {url}")

#         try:
#             response = await client.post(
#                 url,
#                 data=data,
#                 json=json,
#                 headers=headers,
#                 timeout=timeout or self.timeout,
#             )
#             return await self._handle_response(response)

#         except httpx.TimeoutException as e:
#             raise HTTPTimeoutError(f"请求超时: {str(e)}")
#         except httpx.ConnectError as e:
#             raise HTTPConnectionError(f"连接错误: {str(e)}")
#         except httpx.RequestError as e:
#             raise HTTPRequestError(f"请求失败: {str(e)}")

#     async def put(
#         self,
#         endpoint: str,
#         data: Optional[Union[Dict[str, Any], list]] = None,
#         json: Optional[Union[Dict[str, Any], list]] = None,
#         headers: Optional[Dict[str, str]] = None,
#         timeout: Optional[int] = None,
#     ) -> Dict[str, Any]:
#         """发送异步 PUT 请求"""
#         url = self._build_url(endpoint)
#         client = await self._get_client()

#         logger.info(f"PUT {url}")

#         try:
#             response = await client.put(
#                 url,
#                 data=data,
#                 json=json,
#                 headers=headers,
#                 timeout=timeout or self.timeout,
#             )
#             return await self._handle_response(response)

#         except httpx.TimeoutException as e:
#             raise HTTPTimeoutError(f"请求超时: {str(e)}")
#         except httpx.ConnectError as e:
#             raise HTTPConnectionError(f"连接错误: {str(e)}")
#         except httpx.RequestError as e:
#             raise HTTPRequestError(f"请求失败: {str(e)}")

#     async def delete(
#         self,
#         endpoint: str,
#         params: Optional[Dict[str, Any]] = None,
#         headers: Optional[Dict[str, str]] = None,
#         timeout: Optional[int] = None,
#     ) -> Dict[str, Any]:
#         """发送异步 DELETE 请求"""
#         url = self._build_url(endpoint)
#         client = await self._get_client()

#         logger.info(f"DELETE {url}")

#         try:
#             response = await client.delete(
#                 url,
#                 params=params,
#                 headers=headers,
#                 timeout=timeout or self.timeout,
#             )
#             return await self._handle_response(response)

#         except httpx.TimeoutException as e:
#             raise HTTPTimeoutError(f"请求超时: {str(e)}")
#         except httpx.ConnectError as e:
#             raise HTTPConnectionError(f"连接错误: {str(e)}")
#         except httpx.RequestError as e:
#             raise HTTPRequestError(f"请求失败: {str(e)}")

#     async def close(self):
#         """关闭客户端"""
#         if self._client:
#             await self._client.aclose()
#             self._client = None

#     async def __aenter__(self):
#         """异步上下文管理器入口"""
#         return self

#     async def __aexit__(self, exc_type, exc_val, exc_tb):
#         """异步上下文管理器退出"""
#         await self.close()

