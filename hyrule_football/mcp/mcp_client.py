from langchain_mcp_adapters.client import MultiServerMCPClient
from hyrule_football.mcp.mcp_util import MCPEndpoint

mcp_client = MultiServerMCPClient(
    {
        "match": MCPEndpoint.MATCH.server_config,
        "odds": MCPEndpoint.ODDS.server_config,
    }
)
