import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Dam bao root directory nam trong sys.path
root_dir = os.path.abspath(os.path.dirname(__file__))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from src.api.v1.router import api_v1_router
from src.core.concurrency import shutdown_executor
from src.core.async_db import async_engine
from src.core.models import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Quan ly vong doi ung dung FastAPI (Startup & Shutdown)."""
    # Startup: Khoi tao cac bang database neu chua co
    try:
        init_db()
    except Exception as e:
        print(f"[WARN] Khoi tao DB: {e}")
    yield
    # Shutdown
    shutdown_executor()
    await async_engine.dispose()

app = FastAPI(
    title="VideoCrew Studio API",
    description="Backend API Server cho he thong tu dong hoa san xuat Video AI (Ho tro Async I/O, WebSockets, Next.js & Rust Client)",
    version="1.0.0",
    lifespan=lifespan
)

# Cau hinh CORS Middleware ho tro Frontend Next.js / React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.staticfiles import StaticFiles

# Dam bao cac thu muc media ton tai truoc khi mount
os.makedirs("generated_images", exist_ok=True)
os.makedirs("generated_audio", exist_ok=True)
os.makedirs("generated_videos", exist_ok=True)
os.makedirs("exports", exist_ok=True)

app.mount("/generated_images", StaticFiles(directory="generated_images"), name="generated_images")
app.mount("/generated_audio", StaticFiles(directory="generated_audio"), name="generated_audio")
app.mount("/generated_videos", StaticFiles(directory="generated_videos"), name="generated_videos")
app.mount("/exports", StaticFiles(directory="exports"), name="exports")

# Dang ky cac Routes
app.include_router(api_v1_router)

@app.get("/health", tags=["System Health"])
async def health_check():
    """Endpoint kiem tra trang thai song cua Backend Server."""
    return {"status": "healthy", "service": "VideoCrew FastAPI Backend"}

@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "Chao mung toi VideoCrew Studio API Server",
        "docs_url": "/docs",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
