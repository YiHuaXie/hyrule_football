# HTTP 客户端使用文档

## 📦 安装依赖

```bash
# 基础依赖（同步客户端）
pip install requests

# 异步客户端（可选）
pip install httpx
```

## 🚀 快速开始

### 同步 HTTP 客户端

```python
from hyrule_football.clients import HTTPClient

# 创建客户端
client = HTTPClient(
    base_url="https://api.example.com",
    timeout=30,
    max_retries=3,
)

# 发送请求
response = client.get("/users", params={"page": 1})
print(response)

# 关闭客户端
client.close()
```

### 使用上下文管理器（推荐）

```python
from hyrule_football.clients import HTTPClient

with HTTPClient(base_url="https://api.example.com") as client:
    response = client.get("/users")
    print(response)
```

### 异步 HTTP 客户端

```python
import asyncio
from hyrule_football.clients import AsyncHTTPClient

async def main():
    async with AsyncHTTPClient(base_url="https://api.example.com") as client:
        response = await client.get("/users")
        print(response)

asyncio.run(main())
```

## 📖 API 文档

### HTTPClient

#### 初始化参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `base_url` | str | "" | 基础 URL |
| `timeout` | int | 30 | 请求超时时间（秒） |
| `max_retries` | int | 3 | 最大重试次数 |
| `headers` | dict | None | 默认请求头 |
| `verify_ssl` | bool | True | 是否验证 SSL 证书 |

#### 方法

##### `get(endpoint, params=None, headers=None, timeout=None)`
发送 GET 请求

**参数：**
- `endpoint`: API 端点
- `params`: 查询参数（字典）
- `headers`: 额外的请求头
- `timeout`: 超时时间（覆盖默认值）

**返回：** 响应数据（JSON 字典）

##### `post(endpoint, data=None, json=None, headers=None, timeout=None)`
发送 POST 请求

**参数：**
- `endpoint`: API 端点
- `data`: 表单数据
- `json`: JSON 数据
- `headers`: 额外的请求头
- `timeout`: 超时时间

**返回：** 响应数据（JSON 字典）

##### `put(endpoint, data=None, json=None, headers=None, timeout=None)`
发送 PUT 请求

##### `delete(endpoint, params=None, headers=None, timeout=None)`
发送 DELETE 请求

##### `patch(endpoint, data=None, json=None, headers=None, timeout=None)`
发送 PATCH 请求

## 🔧 高级用法

### 自定义请求头

```python
client = HTTPClient(
    base_url="https://api.example.com",
    headers={
        "Authorization": "Bearer YOUR_TOKEN",
        "X-Custom-Header": "custom-value",
    }
)
```

### 异常处理

```python
from hyrule_football.clients import (
    HTTPClient,
    HTTPTimeoutError,
    HTTPConnectionError,
    HTTPResponseError,
    HTTPAuthenticationError,
)

client = HTTPClient(base_url="https://api.example.com")

try:
    response = client.get("/users")
except HTTPTimeoutError as e:
    print(f"请求超时: {e}")
except HTTPConnectionError as e:
    print(f"连接失败: {e}")
except HTTPAuthenticationError as e:
    print(f"认证失败: {e}, 状态码: {e.status_code}")
except HTTPResponseError as e:
    print(f"响应错误: {e}, 状态码: {e.status_code}")
```

### 继承封装自定义 API 客户端

```python
from hyrule_football.clients import HTTPClient

class FootballAPIClient(HTTPClient):
    """足球数据 API 客户端"""
    
    def __init__(self, api_key: str):
        super().__init__(
            base_url="https://api.football-data.org/v4",
            headers={"X-Auth-Token": api_key},
        )
    
    def get_matches(self, league: str = "PL"):
        """获取比赛列表"""
        return self.get(f"/competitions/{league}/matches")
    
    def get_match_odds(self, match_id: int):
        """获取比赛赔率"""
        return self.get(f"/matches/{match_id}/odds")

# 使用
with FootballAPIClient(api_key="YOUR_KEY") as client:
    matches = client.get_matches("PL")
    print(matches)
```

## 🎯 特性

- ✅ **自动重试**：失败请求自动重试（可配置）
- ✅ **超时控制**：防止请求长时间挂起
- ✅ **日志记录**：自动记录请求和响应日志
- ✅ **异常处理**：统一的异常体系
- ✅ **Session 复用**：提高性能
- ✅ **上下文管理器**：自动资源清理
- ✅ **异步支持**：支持异步并发请求

## 📝 异常类型

| 异常 | 说明 |
|------|------|
| `HTTPClientError` | 基础异常类 |
| `HTTPRequestError` | 请求错误 |
| `HTTPResponseError` | 响应错误 |
| `HTTPTimeoutError` | 超时错误 |
| `HTTPConnectionError` | 连接错误 |
| `HTTPAuthenticationError` | 认证错误（401） |
| `HTTPRateLimitError` | 限流错误（429） |

