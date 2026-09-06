from typing import Optional
from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str
    password: Optional[str] = ""


class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    device_label: Optional[str] = None


class AuthResponse(BaseModel):
    status: str
    username: str
    role: str
    is_admin_ip: bool
    client_ip: str
    message: str
