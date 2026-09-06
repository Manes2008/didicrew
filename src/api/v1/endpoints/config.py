from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.async_db import get_async_db
from src.schemas.config_schema import SystemConfigUpdate, SystemConfigResponse, TestKeyRequest, TestKeyResponse
from src.services.config_service import ConfigService

router = APIRouter(prefix="/config", tags=["System Config"])

@router.get("", response_model=SystemConfigResponse, summary="Lay cau hinh he thong va AI keys")
async def get_config(db: AsyncSession = Depends(get_async_db)):
    service = ConfigService(db)
    return await service.get_system_config()

@router.post("", response_model=SystemConfigResponse, summary="Cap nhat cau hinh he thong")
async def update_config(
    cfg_in: SystemConfigUpdate,
    db: AsyncSession = Depends(get_async_db)
):
    service = ConfigService(db)
    return await service.update_system_config(cfg_in)

@router.post("/test-key", response_model=TestKeyResponse, summary="Kiem tra truc tiep ket noi va quota cua API Key")
async def test_api_key(
    req: TestKeyRequest,
    db: AsyncSession = Depends(get_async_db)
):
    service = ConfigService(db)
    return await service.test_api_key(provider=req.provider, raw_key=req.api_key)
