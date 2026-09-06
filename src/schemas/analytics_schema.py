from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel


class CostLogResponse(BaseModel):
    id: int
    project_id: int
    stage_name: str
    sub_step_name: str
    model_name: Optional[str] = None
    provider: Optional[str] = None
    input_tokens: int
    output_tokens: int
    total_tokens: int
    cost_usd: float
    elapsed_seconds: float
    created_at: datetime

    class Config:
        from_attributes = True


class AnalyticsSummary(BaseModel):
    total_projects: int
    completed_projects: int
    total_tokens_used: int
    total_cost_usd: float
    cost_logs: List[CostLogResponse]
