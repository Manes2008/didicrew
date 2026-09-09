from fastapi import APIRouter
from src.api.v1.endpoints.auth import router as auth_router
from src.api.v1.endpoints.channels import router as channels_router
from src.api.v1.endpoints.production import router as production_router
from src.api.v1.endpoints.config import router as config_router
from src.api.v1.endpoints.analytics import router as analytics_router
from src.api.v1.endpoints.ip_manager import router as ip_manager_router
from src.api.v1.endpoints.rustdesk import router as rustdesk_router
from src.api.v1.endpoints.ws import router as ws_router

api_v1_router = APIRouter(prefix="/api/v1")

# Dang ky toan bo sub-routers
api_v1_router.include_router(auth_router)
api_v1_router.include_router(channels_router)
api_v1_router.include_router(production_router)
api_v1_router.include_router(config_router)
api_v1_router.include_router(analytics_router)
api_v1_router.include_router(ip_manager_router)
api_v1_router.include_router(rustdesk_router)
# WebSocket duoc gop vao api_v1_router de co versioning prefix /api/v1/ws/tasks/{task_id}
api_v1_router.include_router(ws_router)
