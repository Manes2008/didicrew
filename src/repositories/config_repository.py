from typing import Optional, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.core.models import SystemConfig
from src.repositories.base_repository import BaseRepository

class ConfigRepository(BaseRepository[SystemConfig]):
    def __init__(self, db: AsyncSession):
        super().__init__(SystemConfig, db)

    async def get_by_key(self, key: str) -> Optional[SystemConfig]:
        stmt = select(SystemConfig).where(SystemConfig.key == key)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def set_config(self, key: str, value: str, is_encrypted: bool = False) -> SystemConfig:
        config_obj = await self.get_by_key(key)
        if config_obj:
            config_obj.value = value
            config_obj.is_encrypted = is_encrypted
        else:
            config_obj = SystemConfig(key=key, value=value, is_encrypted=is_encrypted)
            self.db.add(config_obj)
        await self.db.flush()
        await self.db.refresh(config_obj)
        return config_obj
