from typing import List
from datetime import datetime
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.core.models import AllowedIP
from src.schemas.ip_manager_schema import AllowedIPResponse, UpdateIPStatusRequest


class IPManagerService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_ips(self) -> List[AllowedIPResponse]:
        stmt = select(AllowedIP).order_by(AllowedIP.created_at.desc())
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def update_ip_status(self, ip_id: int, req: UpdateIPStatusRequest) -> AllowedIPResponse:
        stmt = select(AllowedIP).where(AllowedIP.id == ip_id)
        result = await self.db.execute(stmt)
        ip_obj = result.scalars().first()
        if not ip_obj:
            raise HTTPException(status_code=404, detail="Khong tim thay ban ghi IP")

        ip_obj.status = req.status
        if req.is_admin_ip is not None:
            ip_obj.is_admin_ip = req.is_admin_ip
        if req.status == "approved":
            ip_obj.approved_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(ip_obj)
        return ip_obj

    async def delete_ip(self, ip_id: int) -> None:
        stmt = select(AllowedIP).where(AllowedIP.id == ip_id)
        result = await self.db.execute(stmt)
        ip_obj = result.scalars().first()
        if ip_obj:
            await self.db.delete(ip_obj)
            await self.db.commit()
