#!/usr/bin/env python3
import subprocess
import sys

# import time

# # 后台启动 MCP Server
# subprocess.Popen([sys.executable, "-m", "hyrule_football.mcp.mcp_server"])

# # 等待 3 秒
# time.sleep(3)

# 启动主应用
subprocess.run([sys.executable, "-m", "hyrule_football.agents.chains.match_combine"])
