from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime

class ChannelBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50, description="Ten kenh video")
    description: Optional[str] = Field(None, max_length=500, description="Mo ta chi tiet ve kenh")
    goal: str = Field(..., min_length=3, max_length=1000, description="Muc tieu noi dung kenh huong toi")

    @field_validator("name")
    @classmethod
    def validate_name_not_empty(cls, v: str) -> str:
        v_stripped = v.strip()
        if not v_stripped:
            raise ValueError("Ten kenh khong duoc chua toan bo khoang trang")
        return v_stripped

    @field_validator("goal")
    @classmethod
    def validate_goal_not_empty(cls, v: str) -> str:
        v_stripped = v.strip()
        if not v_stripped:
            raise ValueError("Muc tieu kenh khong duoc de trong")
        return v_stripped

class ChannelCreate(ChannelBase):
    pass

class ChannelUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=500)
    goal: Optional[str] = Field(None, min_length=3, max_length=1000)

class ChannelStageConfigResponse(BaseModel):
    id: int
    channel_id: int
    stage_name: str
    role: str
    goal: str
    backstory: str
    markdown_template: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ChannelResponse(ChannelBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
