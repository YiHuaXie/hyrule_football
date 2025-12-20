from hyrule_football.database import db_async_session
from hyrule_football.repositories.company_repo import CompanyRepo
from hyrule_football.schemas import CompanyBase
from hyrule_football.utils import get_logger
import json
from pathlib import Path
from typing import Optional

logger = get_logger(__name__)


async def load_company_data():
    logger.info("🚀 同步博彩公司列表...")

    try:
        data_file = Path(__file__).parent.parent / "data" / "company.json"
        with open(data_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        async with db_async_session() as db:
            result = await CompanyRepo.batch_create_or_update(db, data)
            logger.info(f"✅ 已同步 {len(result)} 家博彩公司")
    except Exception as e:
        logger.error(f"❌ 同步博彩公司列表失败: {e}")


async def get_company_by_name(name: str) -> Optional[CompanyBase]:
    name_map = {
        "bet365": "Bet365",
        "365": "Bet365",
        "williamhill": "威廉希尔",
        "威廉希尔": "威廉希尔",
        "威廉": "威廉希尔",
    }

    name = name_map.get(name.lower(), name)

    async with db_async_session() as db:
        db_company = await CompanyRepo.get_by_name(db, name)
        if db_company:
            company = CompanyBase.model_validate(db_company)
            return company
        return None
