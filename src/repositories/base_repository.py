from typing import Generic, TypeVar, Type, Optional, List, Any, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from src.core.models import Base

ModelType = TypeVar("ModelType", bound=Base)

class BaseRepository(Generic[ModelType]):
    """
    Lop Base Repository bat dong bo cung cap cac thao tac CRUD co ban cho SQLAlchemy.
    """
    def __init__(self, model: Type[ModelType], db: AsyncSession):
        self.model = model
        self.db = db

    async def get_by_id(self, id: Any) -> Optional[ModelType]:
        stmt = select(self.model).where(self.model.id == id)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        stmt = select(self.model).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def create(self, obj_in: Dict[str, Any] | ModelType) -> ModelType:
        if isinstance(obj_in, dict):
            db_obj = self.model(**obj_in)
        else:
            db_obj = obj_in
        self.db.add(db_obj)
        await self.db.flush()
        await self.db.refresh(db_obj)
        return db_obj

    async def update(self, db_obj: ModelType, obj_in: Dict[str, Any]) -> ModelType:
        for field, value in obj_in.items():
            if value is not None and hasattr(db_obj, field):
                setattr(db_obj, field, value)
        self.db.add(db_obj)
        await self.db.flush()
        await self.db.refresh(db_obj)
        return db_obj

    async def delete(self, id: Any) -> bool:
        stmt = delete(self.model).where(self.model.id == id)
        result = await self.db.execute(stmt)
        return result.rowcount > 0
