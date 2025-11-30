from hyrule_football.agents.hyrule_agent import HyruleAgent
from hyrule_football.mcp.mcp_client import mcp_client

import asyncio


async def test():
    # agent = HyruleAgent()
    print("检查 MCP Server 是否可以连接...")
    await mcp_client.get_tools()
    # await agent.run_agent("查询所有比赛", "nero_session1")

    print("MCP Server 正常响应")


if __name__ == "__main__":
    asyncio.run(test())
