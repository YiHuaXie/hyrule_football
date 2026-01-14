from abc import ABC, abstractmethod
from typing import Set, Sequence, List, TypeVar, Generic
from sqlalchemy.ext.asyncio import AsyncSession
from hyrule_football.utils import Platform


class BaseSyncService(ABC):

    platforms: Set[Platform]

    @abstractmethod
    def __init__(self, platforms: Set[Platform]):
        self.platforms = platforms

    @classmethod
    def create(cls, platforms: Sequence[str] = None, **kwargs):
        if platforms is None:
            platforms = set(Platform)
        else:
            platforms = {Platform(p) for p in platforms if p in Platform.__members__}
            platforms = platforms or set(Platform)
        return cls(platforms, **kwargs)
