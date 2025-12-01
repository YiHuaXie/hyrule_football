from hyrule_football.mcp.mcp_client import mcp_client
import asyncio


async def test():
    print("检查 MCP Server 是否可以连接...")
    await mcp_client.get_tools()
    print("MCP Server 正常响应")


if __name__ == "__main__":
    asyncio.run(test())
