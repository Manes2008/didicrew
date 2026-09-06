from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.async_db import get_async_db
from src.schemas.production_schema import VideoGenerateRequest, SingleStageRunRequest, TaskTriggerResponse, ProjectResponse
from src.services.production_service import ProductionService
from src.repositories.project_repository import ProjectRepository

router = APIRouter(prefix="/production", tags=["Production"])

@router.post("/generate", response_model=TaskTriggerResponse, status_code=status.HTTP_202_ACCEPTED, summary="Khoi tao quy trinh san xuat video tu dong")
async def generate_video(
    req: VideoGenerateRequest,
    db: AsyncSession = Depends(get_async_db)
):
    service = ProductionService(db)
    return await service.create_video_task(req)

@router.post("/stage/run", response_model=TaskTriggerResponse, status_code=status.HTTP_202_ACCEPTED, summary="Chay mot stage cu the trong quy trinh san xuat video")
async def run_single_stage(
    req: SingleStageRunRequest,
    db: AsyncSession = Depends(get_async_db)
):
    service = ProductionService(db)
    return await service.create_single_stage_task(req)

@router.get("/projects/{project_id}", response_model=ProjectResponse, summary="Lay chi tiet va tien trinh du an video")
async def get_project_detail(
    project_id: int,
    db: AsyncSession = Depends(get_async_db)
):
    repo = ProjectRepository(db)
    project = await repo.get_project_with_stages(project_id)
    if not project:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=f"Khong tim thay project voi ID: {project_id}")
    return project

@router.get("/channels/{channel_id}/projects", response_model=List[ProjectResponse], summary="Lay danh sach du an theo kenh")
async def list_channel_projects(
    channel_id: int,
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_async_db)
):
    repo = ProjectRepository(db)
    return await repo.get_projects_by_channel(channel_id, skip=skip, limit=limit)

@router.get("/projects/{project_id}/export-bundle", summary="Xuat toan bo goi du an thanh file ZIP")
async def export_project_bundle(
    project_id: int,
    db: AsyncSession = Depends(get_async_db)
):
    import os
    import io
    import json
    import zipfile
    from fastapi import HTTPException
    from fastapi.responses import Response

    repo = ProjectRepository(db)
    project = await repo.get_project_with_stages(project_id)
    if not project:
        raise HTTPException(status_code=404, detail=f"Khong tim thay du an #{project_id}")

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        # 1. Manifest
        manifest = {
            "project_id": project.id,
            "channel_id": project.channel_id,
            "idea": project.idea,
            "provider": project.provider,
            "model_name": project.model_name,
            "status": project.status,
            "created_at": str(project.created_at),
            "stages": [s.stage_name for s in (project.stages or [])]
        }
        zf.writestr("manifest.json", json.dumps(manifest, indent=2, ensure_ascii=False))

        # 2. Stage texts & media
        for stage in (project.stages or []):
            if stage.result_content:
                zf.writestr(f"{stage.stage_name}.txt", stage.result_content)
                # Tim anh / audio / video trong content de kem vao zip
                for line in stage.result_content.split("\n"):
                    line_clean = line.strip()
                    for ext in [".png", ".jpg", ".webp", ".mp3", ".wav", ".mp4"]:
                        if ext in line_clean:
                            # Trích xuất đường dẫn
                            words = line_clean.replace(":", " ").replace("[", " ").replace("]", " ").split()
                            for w in words:
                                if w.endswith(ext) and os.path.exists(w):
                                    try:
                                        with open(w, "rb") as f_media:
                                            zf.writestr(f"media/{os.path.basename(w)}", f_media.read())
                                    except Exception:
                                        pass

    zip_buffer.seek(0)
    zip_bytes = zip_buffer.getvalue()

    filename = f"Project_{project_id}_Bundle.zip"
    return Response(
        content=zip_bytes,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
