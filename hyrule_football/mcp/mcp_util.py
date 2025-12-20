from hyrule_football.config import settings
from enum import Enum


MCP_SERVER_PORT = settings.MCP_SERVER_PORT
MCP_SERVER_URL = settings.MCP_SERVER_URL


class MCPEndpoint(Enum):
    """MCP服务端点枚举"""

    COMPANY = "/mcp/company"
    MATCH = "/mcp/match"
    ODDS = "/mcp/odds"

    @property
    def server_config(self) -> dict:
        """生成 MCP 客户端的配置"""
        return {
            "url": f"{MCP_SERVER_URL}{self.value}",
            "transport": "streamable_http",
        }
