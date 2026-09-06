from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Any, Dict
from datetime import datetime

class VideoGenerateRequest(BaseModel):
    channel_id: int = Field(..., description="ID cua kenh duoc chon de san xuat")
    idea: str = Field(..., min_length=3, max_length=5000, description="Y tuong noi dung video")
    provider: str = Field(default="OpenAI", description="Nha cung cap AI: OpenAI hoac Gemini")
    model_name: str = Field(default="gpt-4o-mini", description="Ten model AI")
    video_engine: str = Field(default="hunyuan", description="Engine sinh video: hunyuan, luma, pika, polling...")
    image_engine: str = Field(default="gemini", description="Engine sinh anh: gemini, sdxl, flux, dalle...")
    aspect_ratio: str = Field(default="9:16", description="Ty le khung hinh: 9:16, 16:9, 1:1")

    @field_validator("provider")
    @classmethod
    def validate_provider(cls, v: str) -> str:
        v_lower = v.lower()
        if "gemini" in v_lower:
            return "Gemini"
        if "openai" in v_lower or "gpt" in v_lower:
            return "OpenAI"
        return "OpenAI"

    @field_validator("aspect_ratio")
    @classmethod
    def validate_aspect_ratio(cls, v: str) -> str:
        allowed = {"9:16", "16:9", "1:1"}
        if v not in allowed:
            return "9:16"
        return v

class SingleStageRunRequest(BaseModel):
    project_id: Optional[int] = Field(default=None, description="ID project nếu đã tạo")
    channel_id: int = Field(..., description="ID kênh")
    stage_name: str = Field(..., description="Tên stage cần chạy: brief, script, image, voice, video")
    idea: str = Field(..., description="Ý tưởng hoặc nội dung đã tối ưu")
    custom_content: Optional[str] = Field(default=None, description="Nội dung tùy chỉnh của stage trước đó nếu người dùng đã sửa")
    provider: str = Field(default="Gemini")
    model_name: str = Field(default="gemini-3.6-flash")
    video_engine: str = Field(default="hunyuan")
    image_engine: str = Field(default="gemini")
    aspect_ratio: str = Field(default="9:16")

class ProjectStageResponse(BaseModel):
    id: int
    project_id: int
    stage_name: str
    result_content: Optional[str] = None
    media_path: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ProjectResponse(BaseModel):
    id: int
    channel_id: int
    idea: str
    provider: str
    model_name: str
    current_stage: str
    status: str
    created_at: datetime
    updated_at: datetime
    stages: List[ProjectStageResponse] = []

    class Config:
        from_attributes = True

class TaskTriggerResponse(BaseModel):
    task_id: str = Field(..., description="ID tac vu bat dong bo de lang nghe qua WebSocket")
    project_id: int = Field(..., description="ID ban ghi Project trong database")
    status: str = Field(default="queued")
    message: str = Field(default="Tac vu da duoc dua vao hang doi xu ly")

class WSMessageSchema(BaseModel):
    event: str = Field(..., description="Loai su kien: progress, log, complete, error")
    task_id: str
    stage: Optional[str] = None
    progress_percent: Optional[int] = None
    data: Optional[Dict[str, Any]] = None
    message: Optional[str] = None
