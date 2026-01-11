# from hyrule_football.mcp.mcp_server import mcp_server, MCP_SERVER_PORT

from pathlib import Path
import threading
import uvicorn
import contextlib
from fastapi import FastAPI

from hyrule_football.lark_client import start_lark_client
from hyrule_football.utils import configure_root_logger
from hyrule_football.config import settings
import logging

logger = logging.getLogger(__name__)
# from hyrule_football.mcp.match_mcp import match_mcp
# from hyrule_football.mcp.odds_mcp import odds_mcp
from hyrule_football.mcp.company_mcp import company_mcp
from hyrule_football.mcp.mcp_util import MCPEndpoint, MCP_SERVER_PORT
from hyrule_football.database import init_database
from hyrule_football.task import start_all_tasks

import hyrule_football.jobs.sync_league as sync_league
import hyrule_football.service.company_service as company_service
import hyrule_football.service.standard_odds_service as standard_odds_service
from hyrule_football.service.match_sync_service import sync_daily_match_list

# 导入所有模型，确保它们注册到 Base
import hyrule_football.models

# https://github.com/modelcontextprotocol/python-sdk/tree/main?tab=readme-ov-file#server
# https://pypi.org/project/mcp/


# 创建组合的 lifespan 来管理两个 session manager 和数据库初始化
@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 初始化数据库...")
    try:
        await init_database()
        logger.info("✅ 数据库初始化成功")
    except Exception as e:
        logger.error(f"❌ 数据库初始化失败: {e}", exc_info=True)
        raise e

    # 加载静态数据
    await company_service.load_company_data()
    # await standard_odds_service.load_standard_odds_data()
    await sync_league.sync_all_leagues()
    await sync_league.sync_league_seasons()
    # await sync_daily_match_list()

    # 启动定时任务（在数据库初始化之后）
    # await start_all_tasks()

    # 启动 MCP session managers
    async with contextlib.AsyncExitStack() as stack:
        # await stack.enter_async_context(match_mcp.session_manager.run())
        # await stack.enter_async_context(odds_mcp.session_manager.run())
        await stack.enter_async_context(company_mcp.session_manager.run())
        yield

    # 关闭时的清理工作（如果需要）
    logger.info("🛑 应用关闭")


# 创建 FastAPI 应用并挂载两个 MCP 服务
mcp_server = FastAPI(
    title="Hyrule Football MCP Server",
    description="足球数据分析 MCP 服务器",
    version="1.0.0",
    lifespan=lifespan,
)

# 挂载 MCP 服务
# mcp_server.mount(MCPEndpoint.MATCH.value, match_mcp.streamable_http_app())
# mcp_server.mount(MCPEndpoint.ODDS.value, odds_mcp.streamable_http_app())
mcp_server.mount(MCPEndpoint.COMPANY.value, company_mcp.streamable_http_app())


# 添加健康检查端点
@mcp_server.get("/health")
async def health_check():
    """健康检查端点"""
    return {"status": "ok", "service": "hyrule_football_mcp"}


def main():
    # 配置日志
    configure_root_logger(Path("logs") / settings.LOG_FILE)

    # 开一个线程 处理飞书消息
    threading.Thread(target=start_lark_client, daemon=True).start()

    # 启动 MCP Server（会阻塞在这里）
    uvicorn.run(mcp_server, host="0.0.0.0", port=MCP_SERVER_PORT)


if __name__ == "__main__":
    main()
