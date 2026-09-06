from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.async_db import get_async_db
from src.schemas.analytics_schema import AnalyticsSummary
from src.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/summary", response_model=AnalyticsSummary, summary="Lay bao cao tong quan chi phi va token")
async def get_analytics_summary(db: AsyncSession = Depends(get_async_db)):
    service = AnalyticsService(db)
    return await service.get_summary()
