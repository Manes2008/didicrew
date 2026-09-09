from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from src.core.models import RequestCostLog, Project
from src.schemas.analytics_schema import AnalyticsSummary, CostLogResponse


class AnalyticsService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_summary(self) -> AnalyticsSummary:
        # Tong so du an
        res_proj = await self.db.execute(select(func.count(Project.id)))
        total_proj = res_proj.scalar() or 0

        # So du an da hoan thanh
        res_comp = await self.db.execute(
            select(func.count(Project.id)).where(Project.status == "completed")
        )
        completed_proj = res_comp.scalar() or 0

        # Tong tokens va chi phi
        res_tokens = await self.db.execute(
            select(func.sum(RequestCostLog.total_tokens), func.sum(RequestCostLog.cost_usd))
        )
        sum_tokens, sum_cost = res_tokens.first() or (0, 0.0)

        # Nhat ky chi phi gan day
        res_logs = await self.db.execute(
            select(RequestCostLog).order_by(RequestCostLog.created_at.desc()).limit(50)
        )
        cost_logs = list(res_logs.scalars().all())

        return AnalyticsSummary(
            total_projects=total_proj,
            completed_projects=completed_proj,
            total_tokens_used=sum_tokens or 0,
            total_cost_usd=round(float(sum_cost or 0.0), 4),
            cost_logs=cost_logs,
        )
