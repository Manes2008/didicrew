from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from src.core.models import Channel, ChannelStageConfig
from src.repositories.base_repository import BaseRepository

class ChannelRepository(BaseRepository[Channel]):
    def __init__(self, db: AsyncSession):
        super().__init__(Channel, db)

    async def get_by_name(self, name: str) -> Optional[Channel]:
        stmt = select(Channel).where(Channel.name == name)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def get_channel_with_configs(self, channel_id: int) -> Optional[Channel]:
        stmt = select(Channel).options(selectinload(Channel.configs)).where(Channel.id == channel_id)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def get_stage_configs(self, channel_id: int) -> List[ChannelStageConfig]:
        stmt = select(ChannelStageConfig).where(ChannelStageConfig.channel_id == channel_id)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
