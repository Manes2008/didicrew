import asyncio
import uuid
import time
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories.project_repository import ProjectRepository
from src.repositories.channel_repository import ChannelRepository
from src.repositories.config_repository import ConfigRepository
from src.schemas.production_schema import VideoGenerateRequest, SingleStageRunRequest, TaskTriggerResponse, WSMessageSchema
from src.core.ws_manager import ws_manager
from src.core.concurrency import run_in_thread
from src.core.models import Project, ProjectStage, Channel, ChannelStageConfig, MediaFile, get_db_session
from src.core.engine import run_stage, WorkflowEngine
from src.core.llm_provider import get_llm
import config

class ProductionService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.project_repo = ProjectRepository(db)
        self.channel_repo = ChannelRepository(db)
        self.config_repo = ConfigRepository(db)

    async def create_video_task(self, req: VideoGenerateRequest) -> TaskTriggerResponse:
        channel = await self.channel_repo.get_by_id(req.channel_id)
        if not channel:
            from fastapi import HTTPException, status
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Khong tim thay kenh voi ID: {req.channel_id}"
            )

        # Lấy API Key tương ứng từ DB hoặc config
        api_key = config.OPENAI_API_KEY if req.provider == "OpenAI" else config.GEMINI_API_KEY
        if req.provider == "OpenAI":
            db_key = await self.config_repo.get_by_key("openai_api_key")
            if db_key and db_key.value:
                api_key = db_key.value
        else:
            db_key = await self.config_repo.get_by_key("gemini_api_key")
            if db_key and db_key.value:
                api_key = db_key.value

        # Tao ban ghi Project trong database
        project = await self.project_repo.create({
            "channel_id": req.channel_id,
            "idea": req.idea,
            "provider": req.provider,
            "model_name": req.model_name,
            "current_stage": "brief",
            "status": "queued"
        })

        task_id = str(uuid.uuid4())
        loop = asyncio.get_running_loop()

        # Day tac vu sang ThreadPoolExecutor de WorkflowEngine khong lam nghen Event Loop
        asyncio.create_task(self._execute_pipeline_in_thread(task_id, project.id, req, api_key, loop))

        return TaskTriggerResponse(
            task_id=task_id,
            project_id=project.id,
            status="queued",
            message="Tac vu da duoc khoi tao va dang chay tren WorkflowEngine"
        )

    async def _execute_pipeline_in_thread(self, task_id: str, project_id: int, req: VideoGenerateRequest, api_key: str, loop: asyncio.AbstractEventLoop):
        """Wrapper goi ham worker trong ThreadPool."""
        await run_in_thread(self._worker_pipeline, task_id, project_id, req, api_key, loop)

    @staticmethod
    def _worker_pipeline(task_id: str, project_id: int, req: VideoGenerateRequest, api_key: str, loop: asyncio.AbstractEventLoop):
        """
        Worker chay tren ThreadPool, su dung WorkflowEngine thuc te de thuc thi cac agent CrewAI va stream tien do.
        """
        stages = [
            ("brief", "1. Dinh huong Sang tao (Brief)", 20),
            ("script", "2. Bien soan Kich ban (Script)", 45),
            ("image", "3. Tao Visual & Render Anh (Image)", 70),
            ("voice", "4. Tong hop Giong doc (Voice)", 85),
            ("video", "5. Render & Bien tap Video (Video)", 100)
        ]

        sync_db = get_db_session()
        try:
            db_project = sync_db.query(Project).filter(Project.id == project_id).first()
            if db_project:
                db_project.status = "processing"
                sync_db.commit()

            # Khoi tao LLM
            llm = get_llm(req.provider, req.model_name, api_key=api_key)

            ws_manager.send_to_task_threadsafe(
                task_id,
                {
                    "event": "start",
                    "task_id": task_id,
                    "project_id": project_id,
                    "progress_percent": 5,
                    "message": "Bat dau quy trinh san xuat tren WorkflowEngine"
                },
                loop
            )

            previous_result = None
            all_results = {}

            channel = sync_db.query(Channel).filter(Channel.id == req.channel_id).first()
            channel_name = channel.name if channel else "VideoCrew Studio"
            channel_goal = channel.goal if channel else "Tao video ngan hap dan thu hut nguoi xem"
            channel_description = channel.description if (channel and channel.description) else channel_goal

            for stage_name, stage_desc, progress in stages:
                # Gui thong bao bat dau stage qua WebSocket
                ws_manager.send_to_task_threadsafe(
                    task_id,
                    {
                        "event": "stage_start",
                        "task_id": task_id,
                        "stage": stage_name,
                        "progress_percent": progress - 10,
                        "message": f"Dang khoi chay WorkflowEngine cho: {stage_desc}"
                    },
                    loop
                )

                # Cap nhat Project current_stage
                if db_project:
                    db_project.current_stage = stage_name
                    sync_db.commit()

                # Doc cau hinh tuy bien cua stage tu database neu co
                stage_cfg_rec = sync_db.query(ChannelStageConfig).filter(
                    ChannelStageConfig.channel_id == req.channel_id,
                    ChannelStageConfig.stage_name == stage_name
                ).first()

                stage_config_dict = None
                if stage_cfg_rec:
                    stage_config_dict = {
                        "role": stage_cfg_rec.role,
                        "goal": stage_cfg_rec.goal,
                        "backstory": stage_cfg_rec.backstory,
                        "markdown_template": stage_cfg_rec.markdown_template
                    }

                # Goi WorkflowEngine thuc te (CrewAI & AI generators)
                context = {
                    "project_id": project_id,
                    "channel_id": req.channel_id,
                    "channel_name": channel_name,
                    "channel_goal": channel_goal,
                    "channel_description": channel_description,
                    "stage_config": stage_config_dict,
                    "model_name": req.model_name,
                    "provider": req.provider,
                    "video_engine": req.video_engine,
                    "image_engine": req.image_engine,
                    "aspect_ratio": req.aspect_ratio
                }

                stage_result = run_stage(
                    stage_name=stage_name,
                    idea=req.idea,
                    previous_result=previous_result,
                    llm=llm,
                    all_results=all_results,
                    context=context
                )

                all_results[stage_name] = stage_result
                previous_result = stage_result

                # Luu ket qua stage vao DB
                stage_rec = sync_db.query(ProjectStage).filter(
                    ProjectStage.project_id == project_id,
                    ProjectStage.stage_name == stage_name
                ).first()

                if not stage_rec:
                    stage_rec = ProjectStage(
                        project_id=project_id,
                        stage_name=stage_name,
                        result_content=stage_result if isinstance(stage_result, str) else str(stage_result),
                        status="completed"
                    )
                    sync_db.add(stage_rec)
                else:
                    stage_rec.result_content = stage_result if isinstance(stage_result, str) else str(stage_result)
                    stage_rec.status = "completed"
                sync_db.flush()

                # Luu cac media files (Anh, Voice, Video) vao bang MediaFile trong database
                if stage_name in ("image", "voice", "video"):
                    try:
                        import os
                        import re
                        result_str = str(stage_result) if stage_result else ""
                        
                        # Xoa cac ban ghi cu cua stage nay neu co de tranh trung lap
                        sync_db.query(MediaFile).filter_by(project_stage_id=stage_rec.id).delete()
                        
                        if stage_name == "image":
                            img_matches = re.findall(r"generated_images[/\\].*?\.(?:png|jpg|jpeg|webp)", result_str, re.IGNORECASE)
                            for match in set(img_matches):
                                norm_path = os.path.normpath(match)
                                if os.path.exists(norm_path):
                                    with open(norm_path, "rb") as f_img:
                                        img_bytes = f_img.read()
                                    media_rec = MediaFile(
                                        project_stage_id=stage_rec.id,
                                        file_name=os.path.basename(norm_path),
                                        file_path=norm_path,
                                        mime_type="image/png",
                                        file_size=len(img_bytes),
                                        file_data=img_bytes,
                                        status="active"
                                    )
                                    sync_db.add(media_rec)
                                    if not stage_rec.media_path:
                                        stage_rec.media_path = norm_path
                                        
                        elif stage_name == "voice":
                            voice_matches = re.findall(r"generated_audio[/\\].*?\.(?:mp3|wav|ogg)", result_str, re.IGNORECASE)
                            for match in set(voice_matches):
                                norm_path = os.path.normpath(match)
                                if os.path.exists(norm_path):
                                    with open(norm_path, "rb") as f_voice:
                                        voice_bytes = f_voice.read()
                                    media_rec = MediaFile(
                                        project_stage_id=stage_rec.id,
                                        file_name=os.path.basename(norm_path),
                                        file_path=norm_path,
                                        mime_type="audio/mpeg",
                                        file_size=len(voice_bytes),
                                        file_data=voice_bytes,
                                        status="active"
                                    )
                                    sync_db.add(media_rec)
                                    stage_rec.media_path = norm_path
                                    
                        elif stage_name == "video":
                            vid_matches = re.findall(r"(?:generated_videos|exports)[/\\].*?\.(?:mp4|mov|avi|mkv|webm)", result_str, re.IGNORECASE)
                            for match in set(vid_matches):
                                norm_path = os.path.normpath(match)
                                if os.path.exists(norm_path):
                                    with open(norm_path, "rb") as f_vid:
                                        vid_bytes = f_vid.read()
                                    media_rec = MediaFile(
                                        project_stage_id=stage_rec.id,
                                        file_name=os.path.basename(norm_path),
                                        file_path=norm_path,
                                        mime_type="video/mp4",
                                        file_size=len(vid_bytes),
                                        file_data=vid_bytes,
                                        status="active"
                                    )
                                    sync_db.add(media_rec)
                                    stage_rec.media_path = norm_path
                    except Exception as ex_media_db:
                        print(f"[WARN] Khong the luu MediaFile vao database: {ex_media_db}")

                sync_db.commit()

                # Gui ket qua stage qua WebSocket day du 100% noi dung
                full_stage_content = str(stage_result) if stage_result else ""
                ws_manager.send_to_task_threadsafe(
                    task_id,
                    {
                        "event": "stage_complete",
                        "task_id": task_id,
                        "stage": stage_name,
                        "progress_percent": progress,
                        "result_content": full_stage_content,
                        "result_preview": full_stage_content[:150] if full_stage_content else "",
                        "message": f"Hoan thanh giai doan: {stage_desc}"
                    },
                    loop
                )

            if db_project:
                db_project.status = "completed"
                sync_db.commit()

            # Thong bao hoan thanh toan bo pipeline
            ws_manager.send_to_task_threadsafe(
                task_id,
                {
                    "event": "complete",
                    "task_id": task_id,
                    "project_id": project_id,
                    "progress_percent": 100,
                    "message": "Toan bo quy trinh san xuat video tren WorkflowEngine da hoan thanh!"
                },
                loop
            )

        except Exception as e:
            if db_project:
                db_project.status = "failed"
                sync_db.commit()

            ws_manager.send_to_task_threadsafe(
                task_id,
                {
                    "event": "error",
                    "task_id": task_id,
                    "project_id": project_id,
                    "message": f"Loi thuc thi WorkflowEngine: {str(e)}"
                },
                loop
            )
        finally:
            sync_db.close()

    async def create_single_stage_task(self, req: SingleStageRunRequest) -> TaskTriggerResponse:
        channel = await self.channel_repo.get_by_id(req.channel_id)
        if not channel:
            from fastapi import HTTPException, status
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Khong tim thay kenh voi ID: {req.channel_id}"
            )

        api_key = config.OPENAI_API_KEY if req.provider == "OpenAI" else config.GEMINI_API_KEY
        if req.provider == "OpenAI":
            db_key = await self.config_repo.get_by_key("openai_api_key")
            if db_key and db_key.value:
                api_key = db_key.value
        else:
            db_key = await self.config_repo.get_by_key("gemini_api_key")
            if db_key and db_key.value:
                api_key = db_key.value

        project_id = req.project_id
        if not project_id:
            project = await self.project_repo.create({
                "channel_id": req.channel_id,
                "idea": req.idea,
                "provider": req.provider,
                "model_name": req.model_name,
                "current_stage": req.stage_name,
                "status": "processing"
            })
            project_id = project.id

        task_id = str(uuid.uuid4())
        loop = asyncio.get_running_loop()

        asyncio.create_task(self._execute_single_stage_in_thread(task_id, project_id, req, api_key, loop))

        return TaskTriggerResponse(
            task_id=task_id,
            project_id=project_id,
            status="queued",
            message=f"Tac vu chay stage {req.stage_name} da duoc khoi tao"
        )

    async def _execute_single_stage_in_thread(self, task_id: str, project_id: int, req: SingleStageRunRequest, api_key: str, loop: asyncio.AbstractEventLoop):
        await run_in_thread(self._worker_single_stage, task_id, project_id, req, api_key, loop)

    @staticmethod
    def _worker_single_stage(task_id: str, project_id: int, req: SingleStageRunRequest, api_key: str, loop: asyncio.AbstractEventLoop):
        sync_db = get_db_session()
        try:
            db_project = sync_db.query(Project).filter(Project.id == project_id).first()
            if db_project:
                db_project.status = "processing"
                db_project.current_stage = req.stage_name
                sync_db.commit()

            llm = get_llm(req.provider, req.model_name, api_key=api_key)

            ws_manager.send_to_task_threadsafe(
                task_id,
                {
                    "event": "stage_start",
                    "task_id": task_id,
                    "project_id": project_id,
                    "stage": req.stage_name,
                    "message": f"Dang khoi chay AI cho giai doan: {req.stage_name}"
                },
                loop
            )

            # Nạp tất cả kết quả stage trước đó từ database
            all_results = {}
            existing_stages = sync_db.query(ProjectStage).filter(ProjectStage.project_id == project_id).all()
            for st in existing_stages:
                if st.result_content:
                    all_results[st.stage_name] = st.result_content

            # Neu co custom_content tu client, ghi de len stage truoc hoac context
            if req.custom_content:
                stage_order = ["brief", "script", "image", "voice", "video"]
                if req.stage_name in stage_order:
                    cur_idx = stage_order.index(req.stage_name)
                    if cur_idx > 0:
                        prev_key = stage_order[cur_idx - 1]
                        all_results[prev_key] = req.custom_content

            stage_order = ["brief", "script", "image", "voice", "video"]
            previous_result = None
            if req.stage_name in stage_order:
                cur_idx = stage_order.index(req.stage_name)
                if cur_idx > 0:
                    prev_key = stage_order[cur_idx - 1]
                    previous_result = all_results.get(prev_key)

            channel = sync_db.query(Channel).filter(Channel.id == req.channel_id).first()
            channel_name = channel.name if channel else "VideoCrew Studio"
            channel_goal = channel.goal if channel else "Tao video ngan hap dan"
            channel_description = channel.description if (channel and channel.description) else channel_goal

            stage_cfg_rec = sync_db.query(ChannelStageConfig).filter(
                ChannelStageConfig.channel_id == req.channel_id,
                ChannelStageConfig.stage_name == req.stage_name
            ).first()

            stage_config_dict = None
            if stage_cfg_rec:
                stage_config_dict = {
                    "role": stage_cfg_rec.role,
                    "goal": stage_cfg_rec.goal,
                    "backstory": stage_cfg_rec.backstory,
                    "markdown_template": stage_cfg_rec.markdown_template
                }

            context = {
                "project_id": project_id,
                "channel_id": req.channel_id,
                "channel_name": channel_name,
                "channel_goal": channel_goal,
                "channel_description": channel_description,
                "stage_config": stage_config_dict,
                "model_name": req.model_name,
                "provider": req.provider,
                "video_engine": req.video_engine,
                "image_engine": req.image_engine,
                "aspect_ratio": req.aspect_ratio
            }

            stage_result = run_stage(
                stage_name=req.stage_name,
                idea=req.idea,
                previous_result=previous_result,
                llm=llm,
                all_results=all_results,
                context=context
            )

            # Luu ket qua stage vao DB
            stage_rec = sync_db.query(ProjectStage).filter(
                ProjectStage.project_id == project_id,
                ProjectStage.stage_name == req.stage_name
            ).first()

            if not stage_rec:
                stage_rec = ProjectStage(
                    project_id=project_id,
                    stage_name=req.stage_name,
                    result_content=stage_result if isinstance(stage_result, str) else str(stage_result),
                    status="completed"
                )
                sync_db.add(stage_rec)
            else:
                stage_rec.result_content = stage_result if isinstance(stage_result, str) else str(stage_result)
                stage_rec.status = "completed"
            sync_db.flush()

            # Luu media files neu co
            if req.stage_name in ("image", "voice", "video"):
                try:
                    import os
                    import re
                    result_str = str(stage_result) if stage_result else ""
                    sync_db.query(MediaFile).filter_by(project_stage_id=stage_rec.id).delete()
                    
                    if req.stage_name == "image":
                        img_matches = re.findall(r"generated_images[/\\].*?\.(?:png|jpg|jpeg|webp)", result_str, re.IGNORECASE)
                        for match in set(img_matches):
                            norm_path = os.path.normpath(match)
                            if os.path.exists(norm_path):
                                with open(norm_path, "rb") as f_img:
                                    img_bytes = f_img.read()
                                media_rec = MediaFile(
                                    project_stage_id=stage_rec.id,
                                    file_name=os.path.basename(norm_path),
                                    file_path=norm_path,
                                    mime_type="image/png",
                                    file_size=len(img_bytes),
                                    file_data=img_bytes,
                                    status="active"
                                )
                                sync_db.add(media_rec)
                                if not stage_rec.media_path:
                                    stage_rec.media_path = norm_path
                    elif req.stage_name == "voice":
                        voice_matches = re.findall(r"generated_audio[/\\].*?\.(?:mp3|wav|ogg)", result_str, re.IGNORECASE)
                        for match in set(voice_matches):
                            norm_path = os.path.normpath(match)
                            if os.path.exists(norm_path):
                                with open(norm_path, "rb") as f_voice:
                                    voice_bytes = f_voice.read()
                                media_rec = MediaFile(
                                    project_stage_id=stage_rec.id,
                                    file_name=os.path.basename(norm_path),
                                    file_path=norm_path,
                                    mime_type="audio/mpeg",
                                    file_size=len(voice_bytes),
                                    file_data=voice_bytes,
                                    status="active"
                                )
                                sync_db.add(media_rec)
                                stage_rec.media_path = norm_path
                    elif req.stage_name == "video":
                        vid_matches = re.findall(r"(?:generated_videos|exports)[/\\].*?\.(?:mp4|mov|avi|mkv|webm)", result_str, re.IGNORECASE)
                        for match in set(vid_matches):
                            norm_path = os.path.normpath(match)
                            if os.path.exists(norm_path):
                                with open(norm_path, "rb") as f_vid:
                                    vid_bytes = f_vid.read()
                                media_rec = MediaFile(
                                    project_stage_id=stage_rec.id,
                                    file_name=os.path.basename(norm_path),
                                    file_path=norm_path,
                                    mime_type="video/mp4",
                                    file_size=len(vid_bytes),
                                    file_data=vid_bytes,
                                    status="active"
                                )
                                sync_db.add(media_rec)
                                stage_rec.media_path = norm_path
                except Exception as ex_media:
                    print(f"[WARN] Loi luu MediaFile single stage: {ex_media}")

            sync_db.commit()

            full_stage_content = str(stage_result) if stage_result else ""
            ws_manager.send_to_task_threadsafe(
                task_id,
                {
                    "event": "stage_complete",
                    "task_id": task_id,
                    "project_id": project_id,
                    "stage": req.stage_name,
                    "result_content": full_stage_content,
                    "result_preview": full_stage_content[:150] if full_stage_content else "",
                    "message": f"Hoan thanh giai doan {req.stage_name}"
                },
                loop
            )

        except Exception as e:
            ws_manager.send_to_task_threadsafe(
                task_id,
                {
                    "event": "error",
                    "task_id": task_id,
                    "project_id": project_id,
                    "stage": req.stage_name,
                    "message": f"Loi thuc thi stage {req.stage_name}: {str(e)}"
                },
                loop
            )
        finally:
            sync_db.close()

