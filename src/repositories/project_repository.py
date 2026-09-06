from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from src.core.models import Project, ProjectStage
from src.repositories.base_repository import BaseRepository

class ProjectRepository(BaseRepository[Project]):
    def __init__(self, db: AsyncSession):
        super().__init__(Project, db)

    async def get_project_with_stages(self, project_id: int) -> Optional[Project]:
        stmt = (
            select(Project)
            .options(selectinload(Project.stages))
            .where(Project.id == project_id)
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def get_projects_by_channel(self, channel_id: int, skip: int = 0, limit: int = 50) -> List[Project]:
        stmt = (
            select(Project)
            .options(selectinload(Project.stages))
            .where(Project.channel_id == channel_id)
            .order_by(Project.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_stage(self, project_id: int, stage_name: str) -> Optional[ProjectStage]:
        stmt = select(ProjectStage).where(
            ProjectStage.project_id == project_id,
            ProjectStage.stage_name == stage_name
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def upsert_stage(self, project_id: int, stage_name: str, result_content: Optional[str] = None, media_path: Optional[str] = None, status: str = "completed") -> ProjectStage:
        stage = await self.get_stage(project_id, stage_name)
        if stage:
            stage.result_content = result_content or stage.result_content
            stage.media_path = media_path or stage.media_path
            stage.status = status
        else:
            stage = ProjectStage(
                project_id=project_id,
                stage_name=stage_name,
                result_content=result_content,
                media_path=media_path,
                status=status
            )
            self.db.add(stage)
        await self.db.flush()
        await self.db.refresh(stage)
        return stage
