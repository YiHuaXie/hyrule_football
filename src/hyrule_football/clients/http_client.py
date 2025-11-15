"""
HTTP 客户端封装

支持同步和异步请求，包含重试、超时、日志等功能
"""

import logging
from typing import Optional, Dict, Any, Union
from urllib.parse import urljoin

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .exceptions import (
    HTTPRequestError,
    HTTPResponseError,
    HTTPTimeoutError,
    HTTPConnectionError,
    HTTPAuthenticationError,
    HTTPRateLimitError,
)

logger = logging.getLogger(__name__)

class HTTPClient:
    """
    同步 HTTP 客户端
    
    特性：
    - 自动重试
    - 超时控制
    - 请求/响应日志
    - 异常处理
    - Session 复用
    """
    
    def __init__(
        self,
        base_url: str = "",
        timeout: int = 10,
        max_retries: int = 0,
        headers: Optional[Dict[str, str]] = None,
        verify_ssl: bool = True,
    ):
        """
        初始化 HTTP 客户端
        
        参数:
            base_url: 基础 URL
            timeout: 请求超时时间（秒）
            max_retries: 最大重试次数
            headers: 默认请求头
            verify_ssl: 是否验证 SSL 证书
        """
        self.base_url = base_url.rstrip("/") if base_url else ""
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        
        # 创建 Session
        self.session = requests.Session()
        
        # 设置默认请求头
        self.session.headers.update({
            "User-Agent": "HyruleFootball/0.1.0",
            "Accept": "application/json",
            "Content-Type": "application/json",
        })
        
        if headers:
            self.session.headers.update(headers)
        
        # 配置重试策略
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=1,  # 重试间隔：1s, 2s, 4s...
            status_forcelist=[429, 500, 502, 503, 504],  # 需要重试的状态码
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST", "PUT", "DELETE"],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    def _build_url(self, endpoint: str) -> str:
        """构建完整 URL"""
        if endpoint.startswith("http://") or endpoint.startswith("https://"):
            return endpoint
        
        if self.base_url:
            return urljoin(self.base_url + "/", endpoint.lstrip("/"))
        return endpoint
    
    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """处理响应"""
        try:
            # 检查状态码
            if response.status_code == 401:
                raise HTTPAuthenticationError(
                    "认证失败",
                    status_code=response.status_code,
                    response_data=response.json() if response.content else None,
                )
            
            if response.status_code == 429:
                raise HTTPRateLimitError(
                    "请求频率超限",
                    status_code=response.status_code,
                    response_data=response.json() if response.content else None,
                )
            
            response.raise_for_status()
            
            # 解析 JSON
            if response.content:
                return response.json()
            return {}
            
        except requests.exceptions.JSONDecodeError as e:
            logger.error(f"JSON 解析失败: {e}")
            raise HTTPResponseError(
                f"响应解析失败: {str(e)}",
                status_code=response.status_code,
            )
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP 错误: {e}")
            raise HTTPResponseError(
                f"HTTP 错误: {str(e)}",
                status_code=response.status_code,
                response_data=response.json() if response.content else None,
            )
    
    def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        发送 GET 请求
        
        参数:
            endpoint: API 端点
            params: 查询参数
            headers: 额外的请求头
            timeout: 超时时间（覆盖默认值）
        
        返回:
            响应数据（JSON）
        """
        url = self._build_url(endpoint)
        timeout = timeout or self.timeout
        
        logger.info(f"GET {url}")
        logger.debug(f"Params: {params}")
        
        try:
            response = self.session.get(
                url,
                params=params,
                headers=headers,
                timeout=timeout,
                verify=self.verify_ssl,
            )
            return self._handle_response(response)
            
        except requests.exceptions.Timeout as e:
            logger.error(f"请求超时: {e}")
            raise HTTPTimeoutError(f"请求超时: {str(e)}")
        except requests.exceptions.ConnectionError as e:
            logger.error(f"连接错误: {e}")
            raise HTTPConnectionError(f"连接错误: {str(e)}")
        except requests.exceptions.RequestException as e:
            logger.error(f"请求失败: {e}")
            raise HTTPRequestError(f"请求失败: {str(e)}")

    def post(
        self,
        endpoint: str,
        data: Optional[Union[Dict[str, Any], list]] = None,
        json: Optional[Union[Dict[str, Any], list]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        发送 POST 请求

        参数:
            endpoint: API 端点
            data: 表单数据
            json: JSON 数据
            headers: 额外的请求头
            timeout: 超时时间（覆盖默认值）

        返回:
            响应数据（JSON）
        """
        url = self._build_url(endpoint)
        timeout = timeout or self.timeout

        logger.info(f"POST {url}")
        logger.debug(f"Data: {data or json}")

        try:
            response = self.session.post(
                url,
                data=data,
                json=json,
                headers=headers,
                timeout=timeout,
                verify=self.verify_ssl,
            )
            return self._handle_response(response)

        except requests.exceptions.Timeout as e:
            logger.error(f"请求超时: {e}")
            raise HTTPTimeoutError(f"请求超时: {str(e)}")
        except requests.exceptions.ConnectionError as e:
            logger.error(f"连接错误: {e}")
            raise HTTPConnectionError(f"连接错误: {str(e)}")
        except requests.exceptions.RequestException as e:
            logger.error(f"请求失败: {e}")
            raise HTTPRequestError(f"请求失败: {str(e)}")

    def put(
        self,
        endpoint: str,
        data: Optional[Union[Dict[str, Any], list]] = None,
        json: Optional[Union[Dict[str, Any], list]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        发送 PUT 请求

        参数:
            endpoint: API 端点
            data: 表单数据
            json: JSON 数据
            headers: 额外的请求头
            timeout: 超时时间（覆盖默认值）

        返回:
            响应数据（JSON）
        """
        url = self._build_url(endpoint)
        timeout = timeout or self.timeout

        logger.info(f"PUT {url}")
        logger.debug(f"Data: {data or json}")

        try:
            response = self.session.put(
                url,
                data=data,
                json=json,
                headers=headers,
                timeout=timeout,
                verify=self.verify_ssl,
            )
            return self._handle_response(response)

        except requests.exceptions.Timeout as e:
            logger.error(f"请求超时: {e}")
            raise HTTPTimeoutError(f"请求超时: {str(e)}")
        except requests.exceptions.ConnectionError as e:
            logger.error(f"连接错误: {e}")
            raise HTTPConnectionError(f"连接错误: {str(e)}")
        except requests.exceptions.RequestException as e:
            logger.error(f"请求失败: {e}")
            raise HTTPRequestError(f"请求失败: {str(e)}")

    def delete(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        发送 DELETE 请求

        参数:
            endpoint: API 端点
            params: 查询参数
            headers: 额外的请求头
            timeout: 超时时间（覆盖默认值）

        返回:
            响应数据（JSON）
        """
        url = self._build_url(endpoint)
        timeout = timeout or self.timeout

        logger.info(f"DELETE {url}")
        logger.debug(f"Params: {params}")

        try:
            response = self.session.delete(
                url,
                params=params,
                headers=headers,
                timeout=timeout,
                verify=self.verify_ssl,
            )
            return self._handle_response(response)

        except requests.exceptions.Timeout as e:
            logger.error(f"请求超时: {e}")
            raise HTTPTimeoutError(f"请求超时: {str(e)}")
        except requests.exceptions.ConnectionError as e:
            logger.error(f"连接错误: {e}")
            raise HTTPConnectionError(f"连接错误: {str(e)}")
        except requests.exceptions.RequestException as e:
            logger.error(f"请求失败: {e}")
            raise HTTPRequestError(f"请求失败: {str(e)}")

    def patch(
        self,
        endpoint: str,
        data: Optional[Union[Dict[str, Any], list]] = None,
        json: Optional[Union[Dict[str, Any], list]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        发送 PATCH 请求

        参数:
            endpoint: API 端点
            data: 表单数据
            json: JSON 数据
            headers: 额外的请求头
            timeout: 超时时间（覆盖默认值）

        返回:
            响应数据（JSON）
        """
        url = self._build_url(endpoint)
        timeout = timeout or self.timeout

        logger.info(f"PATCH {url}")
        logger.debug(f"Data: {data or json}")

        try:
            response = self.session.patch(
                url,
                data=data,
                json=json,
                headers=headers,
                timeout=timeout,
                verify=self.verify_ssl,
            )
            return self._handle_response(response)

        except requests.exceptions.Timeout as e:
            logger.error(f"请求超时: {e}")
            raise HTTPTimeoutError(f"请求超时: {str(e)}")
        except requests.exceptions.ConnectionError as e:
            logger.error(f"连接错误: {e}")
            raise HTTPConnectionError(f"连接错误: {str(e)}")
        except requests.exceptions.RequestException as e:
            logger.error(f"请求失败: {e}")
            raise HTTPRequestError(f"请求失败: {str(e)}")

    def close(self):
        """关闭 Session"""
        self.session.close()

    def __enter__(self):
        """上下文管理器入口"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出"""
        self.close()

