from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.async_db import get_async_db
from src.schemas.ip_manager_schema import AllowedIPResponse, UpdateIPStatusRequest
from src.services.ip_manager_service import IPManagerService

router = APIRouter(prefix="/ip-manager", tags=["IP Manager"])


@router.get("", response_model=List[AllowedIPResponse], summary="Lay danh sach IP")
async def list_ips(db: AsyncSession = Depends(get_async_db)):
    service = IPManagerService(db)
    return await service.list_ips()


@router.put("/{ip_id}", response_model=AllowedIPResponse, summary="Duyet hoac cap nhat quyen IP")
async def update_ip_status(
    ip_id: int,
    req: UpdateIPStatusRequest,
    db: AsyncSession = Depends(get_async_db),
):
    service = IPManagerService(db)
    return await service.update_ip_status(ip_id, req)


@router.delete("/{ip_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Xoa IP khoi danh sach")
async def delete_ip(ip_id: int, db: AsyncSession = Depends(get_async_db)):
    service = IPManagerService(db)
    await service.delete_ip(ip_id)
    return None
