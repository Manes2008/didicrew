from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories.channel_repository import ChannelRepository
from src.schemas.channel_schema import ChannelCreate, ChannelUpdate
from src.core.models import Channel

class ChannelService:
    def __init__(self, db: AsyncSession):
        self.repo = ChannelRepository(db)

    async def get_all_channels(self, skip: int = 0, limit: int = 100) -> List[Channel]:
        return await self.repo.get_all(skip=skip, limit=limit)

    async def get_channel_by_id(self, channel_id: int) -> Channel:
        channel = await self.repo.get_by_id(channel_id)
        if not channel:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Khong tim thay kenh voi ID: {channel_id}"
            )
        return channel

    async def create_channel(self, channel_in: ChannelCreate) -> Channel:
        existing = await self.repo.get_by_name(channel_in.name)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ten kenh '{channel_in.name}' da ton tai"
            )
        return await self.repo.create(channel_in.model_dump())

    async def update_channel(self, channel_id: int, channel_in: ChannelUpdate) -> Channel:
        channel = await self.get_channel_by_id(channel_id)
        if channel_in.name and channel_in.name != channel.name:
            existing = await self.repo.get_by_name(channel_in.name)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Ten kenh '{channel_in.name}' da ton tai"
                )
        update_data = channel_in.model_dump(exclude_unset=True)
        return await self.repo.update(channel, update_data)

    async def delete_channel(self, channel_id: int) -> bool:
        channel = await self.get_channel_by_id(channel_id)
        return await self.repo.delete(channel.id)
