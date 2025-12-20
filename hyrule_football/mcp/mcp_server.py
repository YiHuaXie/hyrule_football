# """
# 统一的 MCP 服务器入口
# 将 match_mcp 和 odds_mcp 挂载到 FastAPI 应用上
# """

# import contextlib
# from fastapi import FastAPI

# from hyrule_football.mcp.match_mcp import match_mcp
# from hyrule_football.mcp.odds_mcp import odds_mcp
# from hyrule_football.mcp.mcp_util import MCPEndpoint, MCP_SERVER_PORT
# from hyrule_football.database import init_database
# from hyrule_football.utils import get_logger
# from hyrule_football.task import start_all_tasks

# # 导入所有模型，确保它们注册到 Base
# from hyrule_football.models import Company  # noqa: F401

# # https://github.com/modelcontextprotocol/python-sdk/tree/main?tab=readme-ov-file#server
# # https://pypi.org/project/mcp/

# logger = get_logger(__name__)


# # 创建组合的 lifespan 来管理两个 session manager 和数据库初始化
# @contextlib.asynccontextmanager
# async def lifespan(app: FastAPI):
#     # 启动时：初始化数据库
#     logger.info("🚀 应用启动：开始初始化数据库...")
#     try:
#         await init_database()
#         logger.info("✅ 数据库初始化成功")
#     except Exception as e:
#         logger.error(f"❌ 数据库初始化失败: {e}", exc_info=True)
#         raise e

#     # 启动定时任务（在数据库初始化之后）
#     logger.info("🚀 启动定时任务...")
#     start_all_tasks()
#     logger.info("✅ 定时任务启动成功")

#     # 启动 MCP session managers
#     async with contextlib.AsyncExitStack() as stack:
#         await stack.enter_async_context(match_mcp.session_manager.run())
#         await stack.enter_async_context(odds_mcp.session_manager.run())
#         yield

#     # 关闭时的清理工作（如果需要）
#     logger.info("🛑 应用关闭")


# # 创建 FastAPI 应用并挂载两个 MCP 服务
# mcp_server = FastAPI(
#     title="Hyrule Football MCP Server",
#     description="足球数据分析 MCP 服务器",
#     version="1.0.0",
#     lifespan=lifespan,
# )

# # 挂载 MCP 服务
# mcp_server.mount(MCPEndpoint.MATCH.value, match_mcp.streamable_http_app())
# mcp_server.mount(MCPEndpoint.ODDS.value, odds_mcp.streamable_http_app())


# # 添加健康检查端点
# @mcp_server.get("/health")
# async def health_check():
#     """健康检查端点"""
#     return {"status": "ok", "service": "hyrule_football_mcp"}


# if __name__ == "__main__":
#     import uvicorn

#     # 监听 0.0.0.0 允许本地和 Docker 都能访问
#     uvicorn.run(mcp_server, host="0.0.0.0", port=MCP_SERVER_PORT)
