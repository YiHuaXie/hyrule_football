from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional, Dict
from hyrule_football.models import Company


class CompanyRepo:
    """博彩公司数据访问层"""

    @staticmethod
    async def get_by_id(db: AsyncSession, company_id: int) -> Optional[Company]:
        """根据 ID 获取博彩公司"""
        result = await db.execute(select(Company).filter_by(id=company_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_name(db: AsyncSession, name: str) -> Optional[Company]:
        """根据名称获取博彩公司"""
        result = await db.execute(select(Company).filter_by(name=name))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all(db: AsyncSession) -> List[Company]:
        """获取所有博彩公司"""
        result = await db.execute(select(Company))
        return list(result.scalars().all())

    @staticmethod
    async def batch_create_or_update(
        db: AsyncSession,
        company_list: List[Dict[str, any]],
    ) -> List[Company]:
        """批量创建或者更新博彩公司"""
        result = []

        for data in company_list:
            company_id = data.get("id")
            company_name = data.get("name")

            if not company_id or not company_name:
                continue

            # 异步查询现有记录
            existing = await CompanyRepo.get_by_id(db, company_id)

            if existing:
                # 更新现有记录
                if existing.name != company_name:
                    existing.name = company_name
                result.append(existing)
            else:
                # 创建新记录
                company = Company(id=company_id, name=company_name)
                db.add(company)
                result.append(company)

        await db.flush()
        return result
