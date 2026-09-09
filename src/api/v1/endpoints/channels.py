from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.async_db import get_async_db
from src.schemas.channel_schema import ChannelCreate, ChannelUpdate, ChannelResponse
from src.services.channel_service import ChannelService

router = APIRouter(prefix="/channels", tags=["Channels"])

@router.get("", response_model=List[ChannelResponse], summary="Lay danh sach kenh")
async def list_channels(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_async_db)
):
    service = ChannelService(db)
    return await service.get_all_channels(skip=skip, limit=limit)

@router.get("/{channel_id}", response_model=ChannelResponse, summary="Lay chi tiet mot kenh")
async def get_channel(
    channel_id: int,
    db: AsyncSession = Depends(get_async_db)
):
    service = ChannelService(db)
    return await service.get_channel_by_id(channel_id)

@router.post("", response_model=ChannelResponse, status_code=status.HTTP_201_CREATED, summary="Tao kenh moi")
async def create_channel(
    channel_in: ChannelCreate,
    db: AsyncSession = Depends(get_async_db)
):
    service = ChannelService(db)
    return await service.create_channel(channel_in)

@router.put("/{channel_id}", response_model=ChannelResponse, summary="Cap nhat thong tin kenh")
async def update_channel(
    channel_id: int,
    channel_in: ChannelUpdate,
    db: AsyncSession = Depends(get_async_db)
):
    service = ChannelService(db)
    return await service.update_channel(channel_id, channel_in)

@router.delete("/{channel_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Xoa kenh")
async def delete_channel(
    channel_id: int,
    db: AsyncSession = Depends(get_async_db)
):
    service = ChannelService(db)
    await service.delete_channel(channel_id)
    return None
