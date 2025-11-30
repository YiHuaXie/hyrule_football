from langchain_mcp_adapters.client import MultiServerMCPClient
from pathlib import Path

import os

MCP_DIR = Path(__file__).parent
MATCH_MCP_SERVER = (MCP_DIR / "match_mcp.py").resolve()
ODDS_MCP_SERVER = (MCP_DIR / "odds_mcp.py").resolve()

mcp_client = MultiServerMCPClient(
    {
        "match": {
            "command": "python",
            "args": [str(MATCH_MCP_SERVER)],
            "transport": "stdio",
            # 这里显式传入 os.environ，保证子进程环境和主进程一致
            "env": os.environ.copy(),
        },
        "odds": {
            "command": "python",
            "args": [str(ODDS_MCP_SERVER)],
            "transport": "stdio",
            "env": os.environ.copy(),
        },
    }
)
