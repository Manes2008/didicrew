from typing import Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.async_db import get_async_db
from src.repositories.config_repository import ConfigRepository

router = APIRouter(prefix="/rustdesk", tags=["RustDesk"])

class RustDeskConfig(BaseModel):
    id_server: str = Field(default="103.179.189.130", description="ID Server host / IP")
    relay_server: str = Field(default="103.179.189.130", description="Relay Server host / IP")
    api_server: Optional[str] = Field(default="", description="API Server URL")
    public_key: Optional[str] = Field(default="", description="Public Key xac thuc")
    is_connected: bool = True

@router.get("", response_model=RustDeskConfig, summary="Lay cau hinh RustDesk")
async def get_rustdesk_config(db: AsyncSession = Depends(get_async_db)):
    repo = ConfigRepository(db)
    id_srv = await repo.get_by_key("rustdesk_id_server")
    relay_srv = await repo.get_by_key("rustdesk_relay_server")
    api_srv = await repo.get_by_key("rustdesk_api_server")
    pub_key = await repo.get_by_key("rustdesk_public_key")

    return RustDeskConfig(
        id_server=id_srv.value if id_srv and id_srv.value else "103.179.189.130",
        relay_server=relay_srv.value if relay_srv and relay_srv.value else "103.179.189.130",
        api_server=api_srv.value if api_srv else "",
        public_key=pub_key.value if pub_key else "",
        is_connected=True
    )

@router.post("", response_model=RustDeskConfig, summary="Cap nhat cau hinh RustDesk")
async def update_rustdesk_config(cfg: RustDeskConfig, db: AsyncSession = Depends(get_async_db)):
    repo = ConfigRepository(db)
    await repo.set_config("rustdesk_id_server", cfg.id_server)
    await repo.set_config("rustdesk_relay_server", cfg.relay_server)
    await repo.set_config("rustdesk_api_server", cfg.api_server or "")
    await repo.set_config("rustdesk_public_key", cfg.public_key or "")
    return cfg
