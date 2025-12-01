"""
统一的 MCP 服务器入口
将 match_mcp 和 odds_mcp 挂载到同一个 Starlette 应用上
"""

import contextlib
from starlette.applications import Starlette
from starlette.routing import Mount

from hyrule_football.mcp.match_mcp import match_mcp
from hyrule_football.mcp.odds_mcp import odds_mcp
from hyrule_football.mcp.mcp_util import MCPEndpoint, MCP_SERVER_PORT

# https://github.com/modelcontextprotocol/python-sdk/tree/main?tab=readme-ov-file#server
# https://pypi.org/project/mcp/


# 创建组合的 lifespan 来管理两个 session manager
@contextlib.asynccontextmanager
async def lifespan(app: Starlette):
    async with contextlib.AsyncExitStack() as stack:
        await stack.enter_async_context(match_mcp.session_manager.run())
        await stack.enter_async_context(odds_mcp.session_manager.run())
        yield


# 创建 Starlette 应用并挂载两个 MCP 服务
mcp_server = Starlette(
    routes=[
        Mount(MCPEndpoint.MATCH.value, match_mcp.streamable_http_app()),
        Mount(MCPEndpoint.ODDS.value, odds_mcp.streamable_http_app()),
    ],
    lifespan=lifespan,
)

if __name__ == "__main__":
    import uvicorn

    # 监听 0.0.0.0 允许本地和 Docker 都能访问
    uvicorn.run(mcp_server, host="0.0.0.0", port=MCP_SERVER_PORT)
