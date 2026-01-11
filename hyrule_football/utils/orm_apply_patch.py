from sqlalchemy import inspect
from sqlalchemy.orm import DeclarativeBase


def orm_apply_patch(
    instance: DeclarativeBase,
    data: dict,
    *,
    allowed_fields: set[str] | None = None,
    protected_fields: set[str] | None = None,
):
    """
    对 SQLAlchemy ORM 实例进行安全的 partial update

    - 支持 nullable=True 的字段更新为 None
    - 自动忽略不存在 / 非列字段
    """

    try:
        mapper = inspect(instance).mapper

        for key, value in data.items():
            if protected_fields and key in protected_fields:
                continue

            if allowed_fields and key not in allowed_fields:
                continue

            column = mapper.columns.get(key)
            if column is None:
                continue

            if value is None and not column.nullable:
                continue

            setattr(instance, key, value)

    except Exception as e:
        print(f"❌ orm_apply_patch failed: {e}")
        raise
