from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class AllowedIPResponse(BaseModel):
    id: int
    ip_address: str
    label: Optional[str] = None
    status: str
    is_admin_ip: bool
    approved_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class UpdateIPStatusRequest(BaseModel):
    status: str = Field(..., description="Trang thai: pending, approved, rejected")
    is_admin_ip: Optional[bool] = None
