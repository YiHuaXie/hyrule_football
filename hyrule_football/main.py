from hyrule_football.utils import configure_root_logger
from hyrule_football.config import settings
from hyrule_football.mcp.mcp_server import mcp_server, MCP_SERVER_PORT
from hyrule_football.task import start_all_tasks
from hyrule_football.lark_client import start_lark_client
from pathlib import Path
import threading
import uvicorn


def main():
    # 配置日志
    configure_root_logger(Path("logs") / settings.LOG_FILE)

    # 定时器任务
    start_all_tasks()

    # 开一个线程 处理飞书消息
    threading.Thread(target=start_lark_client, daemon=True).start()

    # 启动 MCP Server（会阻塞在这里）
    uvicorn.run(mcp_server, host="0.0.0.0", port=MCP_SERVER_PORT)


if __name__ == "__main__":
    main()
