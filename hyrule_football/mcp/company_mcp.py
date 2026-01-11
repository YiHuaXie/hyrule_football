from typing import List, Optional
from mcp.server.fastmcp import FastMCP
from hyrule_football.utils import get_logger
import hyrule_football.service.company_service as company_service

logger = get_logger(__name__)

company_mcp = FastMCP("Company")
# 设置 MCP 端点路径为根路径（实际路径由 Starlette Mount 控制）
company_mcp.settings.streamable_http_path = "/"


@company_mcp.tool(description="根据名称查询博彩公司")
async def get_company_by_name(name: str) -> Optional[dict]:
    company = await company_service.get_company_by_name(name)
    return company.model_dump() if company else None


@company_mcp.tool(description="根据多个名称批量查询博彩公司")
async def get_company_list_by_names(names: List[str]) -> List[dict]:
    default_namnes = ["Bet365", "威廉希尔"]
    result = []
    for name in names:
        company = await get_company_by_name(name)
        if company:
            result.append(company)

    # 如果没有找到任何公司，则返回默认公司
    if not result:
        for name in default_namnes:
            company = await get_company_by_name(name)
            if company:
                result.append(company)

    return result


if __name__ == "__main__":
    company_mcp.run(transport="streamable-http")
