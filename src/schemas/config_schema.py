from pydantic import BaseModel, Field
from typing import Optional, Dict
from datetime import datetime

class SystemConfigUpdate(BaseModel):
    openai_api_key: Optional[str] = Field(None, description="Khoa API OpenAI")
    gemini_api_key: Optional[str] = Field(None, description="Khoa API Gemini")
    provider: Optional[str] = Field(None, description="AI Provider mac dinh: OpenAI hoac Gemini")
    model_name: Optional[str] = Field(None, description="Ten model mac dinh")
    video_engine: Optional[str] = Field(None, description="Engine video mac dinh")
    image_engine: Optional[str] = Field(None, description="Engine anh mac dinh")

class SystemConfigResponse(BaseModel):
    provider: str
    model_name: str
    video_engine: str
    image_engine: str
    has_openai_key: bool
    has_gemini_key: bool
    masked_openai_key: Optional[str] = None
    masked_gemini_key: Optional[str] = None

class TestKeyRequest(BaseModel):
    provider: str = Field(..., description="OpenAI hoặc Gemini")
    api_key: Optional[str] = Field(None, description="Khóa API muốn test (nếu để trống sẽ test key đã lưu)")

class TestKeyResponse(BaseModel):
    provider: str
    is_valid: bool
    status: str
    message: str
