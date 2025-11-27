"""
HTTP 客户端使用示例
"""

import asyncio
from hyrule_football.clients import HTTPClient, AsyncHTTPClient


# ============================================
# 示例 1: 同步 HTTP 客户端基本使用
# ============================================

def example_sync_basic():
    """同步客户端基本使用"""
    print("=" * 50)
    print("示例 1: 同步 HTTP 客户端基本使用")
    print("=" * 50)
    
    # 创建客户端
    client = HTTPClient(
        base_url="https://api.example.com",
        timeout=30,
        max_retries=3,
    )
    
    try:
        # GET 请求
        response = client.get("/users", params={"page": 1, "limit": 10})
        print(f"GET 响应: {response}")
        
        # POST 请求
        response = client.post("/users", json={"name": "张三", "age": 25})
        print(f"POST 响应: {response}")
        
        # PUT 请求
        response = client.put("/users/1", json={"name": "李四"})
        print(f"PUT 响应: {response}")
        
        # DELETE 请求
        response = client.delete("/users/1")
        print(f"DELETE 响应: {response}")
        
    finally:
        client.close()


# ============================================
# 示例 2: 使用上下文管理器
# ============================================

def example_sync_context_manager():
    """使用上下文管理器"""
    print("\n" + "=" * 50)
    print("示例 2: 使用上下文管理器")
    print("=" * 50)
    
    with HTTPClient(base_url="https://api.example.com") as client:
        response = client.get("/users")
        print(f"响应: {response}")


# ============================================
# 示例 3: 自定义请求头和认证
# ============================================

def example_sync_with_auth():
    """自定义请求头和认证"""
    print("\n" + "=" * 50)
    print("示例 3: 自定义请求头和认证")
    print("=" * 50)
    
    client = HTTPClient(
        base_url="https://api.example.com",
        headers={
            "Authorization": "Bearer YOUR_TOKEN",
            "X-Custom-Header": "custom-value",
        }
    )
    
    try:
        response = client.get("/protected-resource")
        print(f"响应: {response}")
    finally:
        client.close()


# ============================================
# 示例 4: 异常处理
# ============================================

def example_sync_error_handling():
    """异常处理"""
    print("\n" + "=" * 50)
    print("示例 4: 异常处理")
    print("=" * 50)
    
    from hyrule_football.clients import (
        HTTPTimeoutError,
        HTTPConnectionError,
        HTTPResponseError,
    )
    
    client = HTTPClient(base_url="https://api.example.com", timeout=5)
    
    try:
        response = client.get("/slow-endpoint")
        print(f"响应: {response}")
    except HTTPTimeoutError as e:
        print(f"请求超时: {e}")
    except HTTPConnectionError as e:
        print(f"连接失败: {e}")
    except HTTPResponseError as e:
        print(f"响应错误: {e}, 状态码: {e.status_code}")
    finally:
        client.close()


# ============================================
# 示例 5: 异步 HTTP 客户端
# ============================================

async def example_async_basic():
    """异步客户端基本使用"""
    print("\n" + "=" * 50)
    print("示例 5: 异步 HTTP 客户端")
    print("=" * 50)
    
    async with AsyncHTTPClient(base_url="https://api.example.com") as client:
        # 并发请求
        tasks = [
            client.get("/users/1"),
            client.get("/users/2"),
            client.get("/users/3"),
        ]
        
        results = await asyncio.gather(*tasks)
        
        for i, result in enumerate(results, 1):
            print(f"用户 {i}: {result}")


# ============================================
# 示例 6: 足球 API 客户端封装
# ============================================

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
    
    def get_team_info(self, team_id: int):
        """获取球队信息"""
        return self.get(f"/teams/{team_id}")


def example_football_api():
    """足球 API 使用示例"""
    print("\n" + "=" * 50)
    print("示例 6: 足球 API 客户端")
    print("=" * 50)
    
    with FootballAPIClient(api_key="YOUR_API_KEY") as client:
        # 获取英超比赛
        matches = client.get_matches("PL")
        print(f"英超比赛: {matches}")
        
        # 获取比赛赔率
        odds = client.get_match_odds(12345)
        print(f"比赛赔率: {odds}")


# ============================================
# 运行所有示例
# ============================================

if __name__ == "__main__":
    # 同步示例
    # example_sync_basic()
    # example_sync_context_manager()
    # example_sync_with_auth()
    # example_sync_error_handling()
    # example_football_api()
    
    # 异步示例
    # asyncio.run(example_async_basic())
    
    print("\n✅ 所有示例完成")

