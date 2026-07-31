import streamlit as st
import os
import shutil
from src.core.models import Project, ProjectStage, MediaFile
from src.core.llm_provider import get_llm
from src.core.engine import run_stage

# Các hằng số workflow
STAGE_DISPLAY_NAMES = {
    "script": "1. Viết kịch bản",
    "visual": "2. Mô tả hình ảnh",
    "image": "3. Tạo hình ảnh",
    "voice": "4. Tạo giọng đọc",
    "video": "5. Xuất Video"
}
STAGES_ORDER = ["script", "visual", "image", "voice", "video"]
STAGE_ICONS = ["file-earmark-text", "eye", "image", "mic", "film"]
DISPLAY_TO_TECH = {v: k for k, v in STAGE_DISPLAY_NAMES.items()}
TECH_TO_DISPLAY = STAGE_DISPLAY_NAMES

def render_text_output(result_text: str):
    """
    Hiển thị giao diện 2 chế độ:
    1. Xem trực quan: Loại bỏ backticks thô và render Markdown đẹp.
    2. Sao chép (Raw Markdown): Dùng st.code để copy dễ dàng.
    """
    def clean_markdown_for_display(text: str) -> str:
        cleaned = text.strip()
        if cleaned.startswith("```markdown"):
            cleaned = cleaned[11:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        return cleaned.strip()

    tab_visual, tab_copy = st.tabs(["Xem trực quan", "Sao chép (Raw Markdown)"])
    with tab_visual:
        st.markdown(clean_markdown_for_display(result_text))
    with tab_copy:
        st.code(result_text, language="markdown")

def render_production_page(db, api_key, provider, model_name, selected_channel):
    # Workspace Dự Án hiện tại
    with st.expander("Workspace Dự Án hiện tại", icon=":material/folder_open:", expanded=True):
        st.markdown(f"**Kênh đang chọn:** `{selected_channel.name}`")
        projects = db.query(Project).filter_by(channel_id=selected_channel.id).order_by(Project.id.desc()).all()
        project_options = ["+ Tạo dự án mới..."] + [f"#{p.id} - {p.idea[:40]}..." for p in projects]
        selected_project_opt = st.selectbox("Chọn Dự án", project_options, key="project_select_main")

        selected_project = None
        if selected_project_opt != "+ Tạo dự án mới...":
            project_id = int(selected_project_opt.split(" - ")[0].replace("#", ""))
            selected_project = db.query(Project).filter_by(id=project_id).first()

            if selected_project:
                prev_project_id = st.session_state.get("project_id")
                project_changed = prev_project_id != selected_project.id

                st.session_state["project_id"] = selected_project.id
                st.session_state["idea"] = selected_project.idea

                if project_changed or "results" not in st.session_state:
                    st.session_state["stage"] = selected_project.current_stage
                    st.session_state["results"] = {}
                    for stage_rec in selected_project.stages:
                        if stage_rec.result_content:
                            st.session_state["results"][stage_rec.stage_name] = stage_rec.result_content

                # Cấu hình thời lượng video (Bước 5)
                st.markdown('<div class="vc-eyebrow" style="margin-top: 1rem;"><i class="bi bi-clock-history"></i> Cấu hình thời lượng video (Bước 5)</div>', unsafe_allow_html=True)
                from src.core.models import VideoDurationConfig
                duration_cfg = db.query(VideoDurationConfig).filter_by(project_id=selected_project.id).first()
                if not duration_cfg:
                    duration_cfg = VideoDurationConfig(
                        project_id=selected_project.id,
                        duration_type="system_generated",
                        target_duration=0,
                        min_duration=0,
                        max_duration=0,
                        system_ratio_multiplier=1.0
                    )
                    db.add(duration_cfg)
                    db.commit()
                    
                with st.container(border=True):
                    col_dur1, col_dur2 = st.columns(2)
                    with col_dur1:
                        dur_type = st.selectbox(
                            "Chế độ thời lượng",
                            ["system_generated", "uploaded_video"],
                            index=0 if duration_cfg.duration_type == "system_generated" else 1,
                            key=f"dur_type_{selected_project.id}"
                        )
                        tgt_dur = st.number_input(
                            "Thời lượng mong muốn (giây, 0 = theo âm thanh)",
                            min_value=0,
                            value=int(duration_cfg.target_duration or 0),
                            key=f"tgt_dur_{selected_project.id}"
                        )
                        min_dur = st.number_input(
                            "Thời lượng tối thiểu (giây)",
                            min_value=0,
                            value=int(duration_cfg.min_duration or 0),
                            key=f"min_dur_{selected_project.id}"
                        )
                    with col_dur2:
                        max_dur = st.number_input(
                            "Thời lượng tối đa (giây, 0 = không giới hạn)",
                            min_value=0,
                            value=int(duration_cfg.max_duration or 0),
                            key=f"max_dur_{selected_project.id}"
                        )
                        src_path = st.text_input(
                            "Đường dẫn video nguồn (chế độ uploaded_video)",
                            value=duration_cfg.video_source_path or "",
                            key=f"src_path_{selected_project.id}"
                        )
                        ratio_mult = st.slider(
                            "Hệ số co giãn (Speed multiplier)",
                            min_value=0.5,
                            max_value=3.0,
                            value=float(duration_cfg.system_ratio_multiplier or 1.0),
                            step=0.1,
                            key=f"ratio_mult_{selected_project.id}"
                        )
                    
                    if st.button("Lưu cấu hình thời lượng", key=f"save_dur_{selected_project.id}", type="secondary", use_container_width=True):
                        duration_cfg.duration_type = dur_type
                        duration_cfg.target_duration = tgt_dur
                        duration_cfg.min_duration = min_dur
                        duration_cfg.max_duration = max_dur
                        duration_cfg.video_source_path = src_path.strip() if src_path.strip() else None
                        duration_cfg.system_ratio_multiplier = ratio_mult
                        db.commit()
                        st.success("Đã lưu cấu hình thời lượng video thành công!")

    # Nhập Ý Tưởng
    is_new = selected_project is None
    idea_val = st.session_state.get("idea", "") if not is_new else ""

    st.markdown('<div class="vc-eyebrow"><i class="bi bi-lightbulb"></i> Ý tưởng Nội dung Video</div>', unsafe_allow_html=True)
    idea = st.text_area(
        "Nhập ý tưởng video:",
        height=90,
        value=idea_val if not is_new else "",
        disabled=not is_new,
        placeholder="Ví dụ: Bé gái nhận món quà bất ngờ từ mẹ nhân ngày sinh nhật",
        label_visibility="collapsed"
    )

    if is_new:
        if st.button("Bắt Đầu Dự Án Mới", icon=":material/rocket_launch:", type="primary", use_container_width=True):
            if not api_key:
                st.error(f"Thiếu API Key cho {provider}! Vui lòng cấu hình ở tab 'Cấu hình AI' hoặc Đăng nhập lại.")
            elif not idea.strip() or len(idea.strip()) < 5:
                st.error("Ý tưởng quá ngắn! Vui lòng viết rõ hơn (tối thiểu 5 ký tự).")
            else:
                try:
                    new_proj = Project(
                        channel_id=selected_channel.id,
                        idea=idea.strip(),
                        provider=provider,
                        model_name=model_name,
                        current_stage="script",
                        status="pending"
                    )
                    db.add(new_proj)
                    db.commit()
                    st.session_state["project_id"] = new_proj.id
                    st.session_state["idea"] = idea.strip()
                    st.session_state["llm"] = get_llm(provider=provider, model_name=model_name, api_key=api_key, temperature=0.75)
                    st.session_state["stage"] = "script"
                    st.session_state["results"] = {}
                    st.success("Khởi tạo dự án thành công!")
                    st.rerun()
                except Exception as ex:
                    db.rollback()
                    st.error(f"Lỗi khi lưu dự án: {ex}")
    else:
        if "llm" not in st.session_state and selected_project:
            st.session_state["llm"] = get_llm(
                provider=selected_project.provider,
                model_name=selected_project.model_name,
                api_key=api_key,
                temperature=0.75
            )

    # WORKFLOW STEPPER MENU
    if "stage" in st.session_state:
        current = st.session_state["stage"]
        current_idx = STAGES_ORDER.index(current)

        st.markdown("---")
        st.markdown('<div class="vc-eyebrow"><i class="bi bi-collection-play"></i> Quy trình Sản xuất Video</div>', unsafe_allow_html=True)

        from streamlit_option_menu import option_menu
        selected_stage_display = option_menu(
            menu_title=None,
            options=list(STAGE_DISPLAY_NAMES.values()),
            icons=STAGE_ICONS,
            default_index=current_idx,
            orientation="horizontal",
            styles={
                "container": {"padding": "0!important", "background-color": "transparent", "border": "1px solid rgba(128,128,128,0.18)", "border-radius": "12px"},
                "icon": {"font-size": "13px"},
                "nav-link": {
                    "font-size": "12.5px",
                    "text-align": "center",
                    "padding": "9px 10px",
                    "margin": "3px",
                    "border-radius": "8px",
                    "--hover-color": "rgba(194, 84, 45, 0.08)"
                },
                "nav-link-selected": {"background-color": "#C2542D", "font-weight": "600"},
            }
        )

        selected_tech_stage = DISPLAY_TO_TECH[selected_stage_display]
        if selected_tech_stage != current:
            st.session_state["stage"] = selected_tech_stage
            st.rerun()

        with st.container(border=True):
            st.markdown(f'<div class="vc-eyebrow" style="margin-bottom:0.2rem;">Bước hiện tại</div>', unsafe_allow_html=True)
            st.markdown(f"**{selected_stage_display}**")

            # Nút thực thi
            if st.button(f"Thực thi {selected_stage_display}", icon=":material/play_arrow:", type="primary"):
                with st.spinner(f"AI đang xử lý bước '{selected_stage_display}'..."):
                    if "llm" not in st.session_state:
                        st.error("Phiên làm việc hết hạn, vui lòng khởi động lại dự án.")
                        st.stop()

                    from src.core.models import ChannelStageConfig
                    prev_stage = STAGES_ORDER[current_idx - 1] if current_idx > 0 else None
                    prev = st.session_state["results"].get(prev_stage, "") if prev_stage else ""

                    stage_config = db.query(ChannelStageConfig).filter_by(
                        channel_id=selected_channel.id, stage_name=current
                    ).first()

                    context = {
                        "channel_name": selected_channel.name,
                        "channel_description": selected_channel.description,
                        "channel_goal": selected_channel.goal,
                        "video_engine": st.session_state.get("video_engine", "wan2.1_local"),
                        "image_engine": st.session_state.get("image_engine", "openai"),
                        "project_id": st.session_state.get("project_id")
                    }

                    if stage_config:
                        context["stage_config"] = {
                            "role": stage_config.role,
                            "goal": stage_config.goal,
                            "backstory": stage_config.backstory,
                            "markdown_template": stage_config.markdown_template
                        }
                    else:
                        context["stage_config"] = {
                            "role": "Trợ lý AI", "goal": "Thực hiện nhiệm vụ", "backstory": "Trợ lý AI", "markdown_template": None
                        }

                    result = run_stage(
                        current,
                        st.session_state["idea"],
                        prev,
                        st.session_state["llm"],
                        all_results=st.session_state.get("results", {}),
                        context=context
                    )
                    st.session_state["results"][current] = result

                    # Lưu DB
                    project_id = st.session_state.get("project_id")
                    if project_id:
                        try:
                            stage_rec = db.query(ProjectStage).filter_by(project_id=project_id, stage_name=current).first()
                            
                            # Trích xuất media path từ result
                            media_path = None
                            image_paths = []
                            if current == "image":
                                image_paths = [line.replace("📁 Đường dẫn ảnh:", "").replace("📁 Đường dẫn ảnh: ", "").strip() for line in result.split("\n") if "generated_images" in line]
                                if image_paths:
                                    media_path = ",".join(image_paths)
                            elif current == "video":
                                for line in result.split("\n"):
                                    if "generated_videos" in line or ".mp4" in line:
                                        media_path = line.replace("Đường dẫn video:", "").replace("Đường dẫn video: ", "").strip()
                                        break

                            if not stage_rec:
                                stage_rec = ProjectStage(
                                    project_id=project_id, 
                                    stage_name=current, 
                                    result_content=result, 
                                    media_path=media_path,
                                    status="completed"
                                )
                                db.add(stage_rec)
                                db.flush()
                            else:
                                stage_rec.result_content = result
                                stage_rec.media_path = media_path
                                stage_rec.status = "completed"
                                db.flush()

                            # Xoá MediaFile cũ liên quan đến stage này để ghi mới
                            db.query(MediaFile).filter_by(project_stage_id=stage_rec.id).delete()

                            # Lưu file nhị phân vào bảng MediaFile
                            if current == "image" and image_paths:
                                for ip in image_paths:
                                    if os.path.exists(ip):
                                        try:
                                            with open(ip, "rb") as f:
                                                f_data = f.read()
                                            db.add(MediaFile(
                                                project_stage_id=stage_rec.id,
                                                file_name=os.path.basename(ip),
                                                file_path=ip,
                                                file_data=f_data,
                                                mime_type="image/png",
                                                file_size=len(f_data)
                                            ))
                                        except Exception as e_img:
                                            st.warning(f"Không thể đọc file ảnh để lưu vào DB: {e_img}")
                            elif current == "video" and media_path:
                                if os.path.exists(media_path):
                                    try:
                                        with open(media_path, "rb") as f:
                                            f_data = f.read()
                                        db.add(MediaFile(
                                            project_stage_id=stage_rec.id,
                                            file_name=os.path.basename(media_path),
                                            file_path=media_path,
                                            file_data=f_data,
                                            mime_type="video/mp4",
                                            file_size=len(f_data)
                                        ))
                                    except Exception as e_vid:
                                        st.warning(f"Không thể đọc file video để lưu vào DB: {e_vid}")

                            proj_rec = db.query(Project).filter_by(id=project_id).first()
                            if proj_rec:
                                proj_rec.current_stage = current
                                proj_rec.status = "running"
                            db.commit()
                        except Exception as ex:
                            db.rollback()
                            st.error(f"Lỗi lưu DB: {ex}")
                    st.rerun()

            # Hiển thị Kết quả
            if current in st.session_state.get("results", {}):
                result_text = st.session_state["results"][current]
                st.markdown("---")
                st.markdown('<div class="vc-result-header"><i class="bi bi-check2-square"></i> Kết quả output</div>', unsafe_allow_html=True)

                if current == "image":
                    # Ưu tiên hiển thị từ dữ liệu nhị phân trong DB
                    project_id = st.session_state.get("project_id")
                    stage_rec = db.query(ProjectStage).filter_by(project_id=project_id, stage_name="image").first() if project_id else None
                    media_files = db.query(MediaFile).filter_by(project_stage_id=stage_rec.id).all() if stage_rec else []
                    
                    db_images = [m for m in media_files if m.file_data]
                    if db_images:
                        cols = st.columns(min(len(db_images), 3))
                        for idx, media in enumerate(db_images):
                            cols[idx % len(cols)].image(media.file_data, caption=media.file_name)
                    else:
                        # Fallback hiển thị từ đường dẫn file local
                        image_paths = [line.replace("Đường dẫn ảnh:", "").strip() for line in result_text.split("\n") if "generated_images" in line and os.path.exists(line.replace("Đường dẫn ảnh:", "").strip())]
                        if image_paths:
                            cols = st.columns(min(len(image_paths), 3))
                            for idx, img_path in enumerate(image_paths):
                                cols[idx % len(cols)].image(img_path, caption=f"Ảnh {idx+1}")
                        else:
                            render_text_output(result_text)

                elif current == "video":
                    project_id = st.session_state.get("project_id")
                    stage_rec = db.query(ProjectStage).filter_by(project_id=project_id, stage_name="video").first() if project_id else None
                    media_files = db.query(MediaFile).filter_by(project_stage_id=stage_rec.id).all() if stage_rec else []
                    
                    db_video = next((m for m in media_files if m.file_data), None)
                    video_shown = False
                    if db_video:
                        st.video(db_video.file_data)
                        video_shown = True
                    else:
                        # Fallback hiển thị từ đường dẫn file local
                        video_path = None
                        for line in result_text.split("\n"):
                            if "generated_videos" in line or ".mp4" in line:
                                video_path = line.replace("Đường dẫn video:", "").strip()
                                break
                        if video_path and os.path.exists(video_path):
                            st.video(video_path)
                            video_shown = True
                            
                    if not video_shown:
                        render_text_output(result_text)
                        
                    # Hiển thị tích hợp Veo3
                    st.markdown("---")
                    st.markdown('<div style="font-weight: bold; font-size: 1.1rem; margin-bottom: 8px;"><i class="bi bi-box-arrow-up"></i> Tích hợp xuất Veo3 (Windows)</div>', unsafe_allow_html=True)
                    
                    col_exp1, col_exp2 = st.columns(2)
                    with col_exp1:
                        if st.button("Tạo gói xuất dữ liệu (Veo3)", icon=":material/output:", type="secondary", use_container_width=True):
                            project_id = st.session_state.get("project_id")
                            if project_id:
                                try:
                                    import shutil
                                    export_dir = f"exports/project_{project_id}"
                                    os.makedirs(export_dir, exist_ok=True)
                                    
                                    # Copy/Write voiceover
                                    voice_rec = db.query(ProjectStage).filter_by(project_id=project_id, stage_name="voice").first()
                                    if voice_rec:
                                        voice_media = db.query(MediaFile).filter_by(project_stage_id=voice_rec.id).first()
                                        if voice_media and voice_media.file_data:
                                            with open(os.path.join(export_dir, voice_media.file_name), "wb") as f_out:
                                                f_out.write(voice_media.file_data)
                                        else:
                                            voice_path = None
                                            if voice_rec.result_content:
                                                for line in voice_rec.result_content.split("\n"):
                                                    if ".mp3" in line or ".wav" in line:
                                                        voice_path = line.strip()
                                                        break
                                            if voice_path and os.path.exists(voice_path):
                                                shutil.copy(voice_path, os.path.join(export_dir, os.path.basename(voice_path)))
                                    
                                    # Copy/Write image
                                    img_rec = db.query(ProjectStage).filter_by(project_id=project_id, stage_name="image").first()
                                    if img_rec:
                                        img_medias = db.query(MediaFile).filter_by(project_stage_id=img_rec.id).all()
                                        if img_medias:
                                            for idx, media in enumerate(img_medias):
                                                if media.file_data:
                                                    with open(os.path.join(export_dir, f"scene_{idx+1}_{media.file_name}"), "wb") as f_out:
                                                        f_out.write(media.file_data)
                                        else:
                                            if img_rec.result_content:
                                                img_paths = [l.replace("📁 Đường dẫn ảnh:", "").replace("📁 Đường dẫn ảnh: ", "").strip() for l in img_rec.result_content.split("\n") if "generated_images" in l]
                                                for idx, ip in enumerate(img_paths):
                                                    if os.path.exists(ip):
                                                        shutil.copy(ip, os.path.join(export_dir, f"scene_{idx+1}_{os.path.basename(ip)}"))
                                            
                                    # Ghi file kịch bản & phân cảnh
                                    script_rec = db.query(ProjectStage).filter_by(project_id=project_id, stage_name="script").first()
                                    if script_rec and script_rec.result_content:
                                        with open(os.path.join(export_dir, "script.txt"), "w", encoding="utf-8") as sf:
                                            sf.write(script_rec.result_content)
                                            
                                        visual_rec = db.query(ProjectStage).filter_by(project_id=project_id, stage_name="visual").first()
                                        if visual_rec and visual_rec.result_content:
                                            with open(os.path.join(export_dir, "visual_prompts.txt"), "w", encoding="utf-8") as vf:
                                                vf.write(visual_rec.result_content)
                                                
                                        st.success(f"Đã tạo gói xuất dữ liệu thành công tại: `{os.path.abspath(export_dir)}`.")
                                except Exception as ex:
                                    st.error(f"Lỗi khi tạo gói xuất dữ liệu: {ex}")
                    
                    with col_exp2:
                        if st.button("Đẩy tự động vào Veo3 (Qua Mark-L)", icon=":material/bolt:", type="primary", use_container_width=True):
                            project_id = st.session_state.get("project_id")
                            if project_id:
                                try:
                                    import sys
                                    # 1. Đảm bảo gói dữ liệu đã được xuất trước
                                    export_dir = f"exports/project_{project_id}"
                                    abs_export_dir = os.path.abspath(export_dir)
                                    if not os.path.exists(export_dir) or not os.listdir(export_dir):
                                        os.makedirs(export_dir, exist_ok=True)
                                        # Copy/Write voiceover
                                        voice_rec = db.query(ProjectStage).filter_by(project_id=project_id, stage_name="voice").first()
                                        if voice_rec:
                                            voice_media = db.query(MediaFile).filter_by(project_stage_id=voice_rec.id).first()
                                            if voice_media and voice_media.file_data:
                                                with open(os.path.join(export_dir, voice_media.file_name), "wb") as f_out:
                                                    f_out.write(voice_media.file_data)
                                        # Copy/Write image
                                        img_rec = db.query(ProjectStage).filter_by(project_id=project_id, stage_name="image").first()
                                        if img_rec:
                                            img_medias = db.query(MediaFile).filter_by(project_stage_id=img_rec.id).all()
                                            for idx, media in enumerate(img_medias):
                                                if media.file_data:
                                                    with open(os.path.join(export_dir, f"scene_{idx+1}_{media.file_name}"), "wb") as f_out:
                                                        f_out.write(media.file_data)
                                        # Ghi file kịch bản & phân cảnh
                                        script_rec = db.query(ProjectStage).filter_by(project_id=project_id, stage_name="script").first()
                                        if script_rec and script_rec.result_content:
                                            with open(os.path.join(export_dir, "script.txt"), "w", encoding="utf-8") as sf:
                                                sf.write(script_rec.result_content)
                                        visual_rec = db.query(ProjectStage).filter_by(project_id=project_id, stage_name="visual").first()
                                        if visual_rec and visual_rec.result_content:
                                            with open(os.path.join(export_dir, "visual_prompts.txt"), "w", encoding="utf-8") as vf:
                                                vf.write(visual_rec.result_content)

                                    # 2. Import computer_control
                                    from src.tools.computer_control import computer_control
                                    
                                    # 3. Kích hoạt cửa sổ Veo3 và tự động hoá nạp file
                                    st.toast("Đang quét các cửa sổ ứng dụng trên Windows...", icon="🔍")
                                    check_script = 'Get-Process | Where-Object {$_.MainWindowTitle -like "*Veo*"} | Select-Object -ExpandProperty MainWindowTitle'
                                    import subprocess
                                    check_res = subprocess.run(
                                        ["powershell", "-NoProfile", "-NonInteractive", "-Command", check_script], 
                                        capture_output=True, text=True, timeout=5
                                    )
                                    window_titles = [line.strip() for line in check_res.stdout.split("\n") if line.strip()]
                                    target_title = next((t for t in window_titles if "veo" in t.lower()), None)
                                    
                                    if not target_title:
                                        st.error("Không tìm thấy cửa sổ ứng dụng Veo3 nào đang mở trên Windows. Vui lòng khởi động phần mềm Veo3 trước khi thực hiện!")
                                    else:
                                        st.toast(f"Đang kích hoạt cửa sổ: {target_title}...", icon="🚀")
                                        computer_control({"action": "focus_window", "title": target_title})
                                        
                                        # Đợi 1 giây để focus ổn định
                                        computer_control({"action": "wait", "seconds": "1.0"})
                                        computer_control({"action": "hotkey", "keys": "ctrl+i"})
                                        computer_control({"action": "wait", "seconds": "1.0"})
                                        computer_control({"action": "hotkey", "keys": "alt+d"})
                                        computer_control({"action": "wait", "seconds": "0.5"})
                                        computer_control({"action": "smart_type", "text": abs_export_dir})
                                        computer_control({"action": "press", "key": "enter"})
                                        computer_control({"action": "wait", "seconds": "0.8"})
                                        computer_control({"action": "press", "key": "tab"})
                                        computer_control({"action": "wait", "seconds": "0.5"})
                                        computer_control({"action": "hotkey", "keys": "ctrl+a"})
                                        computer_control({"action": "wait", "seconds": "0.5"})
                                        computer_control({"action": "press", "key": "enter"})
                                        
                                        st.success(f"Đã tự động đẩy dữ liệu từ `{abs_export_dir}` vào {target_title} thành công!")
                                except Exception as ex:
                                    st.error(f"Không thể gọi module tự động hóa của Mark-L: {ex}")
                else:
                    render_text_output(result_text)

            # Nút điều hướng
            c_next, c_retry, c_back = st.columns([2, 1, 1])
            with c_next:
                if st.button("Duyệt & Sang Bước Tiếp Theo", icon=":material/check_circle:", type="primary", use_container_width=True):
                    idx = STAGES_ORDER.index(current)
                    if idx < len(STAGES_ORDER) - 1:
                        next_stage = STAGES_ORDER[idx + 1]
                        st.session_state["stage"] = next_stage
                        project_id = st.session_state.get("project_id")
                        if project_id:
                            proj_rec = db.query(Project).filter_by(id=project_id).first()
                            if proj_rec:
                                proj_rec.current_stage = next_stage
                                db.commit()
                    else:
                        st.balloons()
                        st.success("Đã hoàn thành toàn bộ quy trình sản xuất Video!")
                    st.rerun()

            with c_retry:
                if st.button("Làm lại", icon=":material/refresh:", use_container_width=True):
                    if current in st.session_state["results"]:
                        del st.session_state["results"][current]
                    st.rerun()

            with c_back:
                if st.button("Quay lại", icon=":material/arrow_back:", use_container_width=True):
                    idx = STAGES_ORDER.index(current)
                    if idx > 0:
                        st.session_state["stage"] = STAGES_ORDER[idx - 1]
                    st.rerun()

    # ---------------------------------------------
    # BO PHAN TICH HIEU SUAT & LOG TOI UU PROMPT (CHI ADMIN)
    # ---------------------------------------------
    if st.session_state.get("user_role") == "ADMIN" and selected_project:
        st.markdown("---")
        with st.expander("[DÀNH CHO ADMIN] Bộ Phân Tích Hiệu Suất & Tối Ưu Prompt", expanded=False):
            st.markdown("### Lịch sử Tự tối ưu Prompt & Phân tích chất lượng kịch bản")

            from src.core.models import PromptOptimizationLog
            import json
            import os as _os

            logs = db.query(PromptOptimizationLog).filter_by(project_id=selected_project.id).order_by(PromptOptimizationLog.created_at.desc()).all()

            if not logs:
                st.info("Chưa có dữ liệu phân tích hiệu suất cho dự án này.")
            else:
                for log in logs:
                    if log.step_name == "step_1_analysis":
                        step_title = "Bước 1: Phân tích Ý tưởng"
                    elif log.step_name == "step_2_scripting":
                        step_title = "Bước 2: Viết Kịch bản chi tiết"
                    elif log.step_name == "step_3_visual":
                        step_title = "Bước 3: Mô tả hình ảnh (Visual Prompt)"
                    else:
                        step_title = f"Giai đoạn: {log.step_name}"

                    status_badge = "[Đạt chuẩn]" if log.is_standardized else "[Cần tối ưu]"

                    with st.container(border=True):
                        st.markdown(f"**{step_title}** -- `{status_badge}` -- *{log.created_at.strftime('%Y-%m-%d %H:%M:%S')}*")

                        st.markdown("**Đầu vào ban đầu (Original input):**")
                        tab_input_view, tab_input_copy = st.tabs(["Xem trực quan", "Sao chép"])
                        with tab_input_view:
                            st.markdown(log.user_input_content)
                        with tab_input_copy:
                            st.code(log.user_input_content, language="text")

                        st.markdown("**Kết quả đã tối ưu / sửa đổi (Adjusted prompt / result):**")
                        tab_result_view, tab_result_copy = st.tabs(["Xem trực quan", "Sao chép"])
                        with tab_result_view:
                            st.markdown(log.adjusted_prompt)
                        with tab_result_copy:
                            st.code(log.adjusted_prompt, language="text")

                        if log.analysis_metrics:
                            try:
                                metrics = json.loads(log.analysis_metrics)
                                st.markdown("##### Chỉ số phân tích hiệu suất")
                                with st.container(border=True):
                                    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
                                    if "character_consistency" in metrics:
                                        with col_m1:
                                            st.caption("Đồng nhất nhân vật")
                                            st.write(f"**{metrics.get('character_consistency', 'N/A')}/10**")
                                        with col_m2:
                                            st.caption("Phong cách nghệ thuật")
                                            st.write(f"**{metrics.get('art_style_match', 'N/A')}/10**")
                                        with col_m3:
                                            st.caption("Chất lượng Visual Prompt")
                                            st.write(f"**{metrics.get('prompt_quality', 'N/A')}/10**")
                                        with col_m4:
                                            st.caption("Trạng thái")
                                            st.write("**Đã phân tích**")
                                    else:
                                        with col_m1:
                                            st.caption("Tông giọng")
                                            st.write(f"**{metrics.get('tone', 'N/A')}**")
                                        with col_m2:
                                            st.caption("Mật độ từ khóa")
                                            st.write(f"**{metrics.get('keyword_density', 'N/A')}**")
                                        with col_m3:
                                            st.caption("Thời lượng dự kiến")
                                            st.write(f"**{metrics.get('estimated_duration', 'N/A')}**")
                                        with col_m4:
                                            st.caption("Điểm liên mạch")
                                            score_val = metrics.get('transition_score', 'Đã phân tích')
                                            st.write(f"**{score_val}/10**" if isinstance(score_val, (int, float)) else f"**{score_val}**")

                                    if "feedback" in metrics and metrics["feedback"]:
                                        st.caption(f"Ý kiến phản hồi: {metrics['feedback']}")
                                    if "attempts" in metrics:
                                        st.caption(f"Số lần viết lại tự động: {metrics['attempts']}")
                            except Exception:
                                st.caption(f"Dữ liệu thô: {log.analysis_metrics}")

                        # Nút phân tích lại cho bước 3 chưa có chỉ số Visual
                        if log.step_name == "step_3_visual":
                            _needs_reanalyze = True
                            if log.analysis_metrics:
                                try:
                                    _existing = json.loads(log.analysis_metrics)
                                    if "character_consistency" in _existing:
                                        _needs_reanalyze = False
                                except Exception:
                                    pass

                            if _needs_reanalyze:
                                if st.button("Phân tích lại chỉ số Visual", key=f"reanalyze_visual_{log.id}"):
                                    _api_key = _os.getenv("OPENAI_API_KEY", "")
                                    if not _api_key:
                                        st.error("Chưa cấu hình OPENAI_API_KEY trong .env")
                                    else:
                                        try:
                                            from crewai import LLM
                                            from src.core.engine import WorkflowEngine
                                            from src.core.models import get_db_session
                                            import json as _json_inner
                                            _llm = LLM(model="gpt-4o-mini", api_key=_api_key)
                                            _engine = WorkflowEngine()
                                            _eval_prompt = (
                                                "You are a Visual Prompt Quality Evaluator for AI Image/Video generation.\n"
                                                "Evaluate the following Visual Prompt list:\n"
                                                f'"{log.adjusted_prompt}"\n\n'
                                                "Score each metric from 1 to 10:\n"
                                                "1) character_consistency: Consistency of character description across scenes.\n"
                                                "2) art_style_match: How well the art style is matched.\n"
                                                "3) prompt_quality: Detail and usability of English prompts.\n\n"
                                                "Return ONLY raw JSON (no markdown block):\n"
                                                '{"character_consistency": 9, "art_style_match": 9, "prompt_quality": 8, "feedback": "brief comment"}'
                                            )
                                            _resp = _llm.call(messages=[{"role": "user", "content": _eval_prompt}])
                                            _data = _json_inner.loads(_engine._clean_json_response(_resp))
                                            _db2 = get_db_session()
                                            try:
                                                _log2 = _db2.query(PromptOptimizationLog).filter_by(id=log.id).first()
                                                if _log2:
                                                    _log2.analysis_metrics = _json_inner.dumps({
                                                        "character_consistency": int(_data.get("character_consistency", 8)),
                                                        "art_style_match": int(_data.get("art_style_match", 8)),
                                                        "prompt_quality": int(_data.get("prompt_quality", 8)),
                                                        "feedback": _data.get("feedback", "")
                                                    }, ensure_ascii=False)
                                                    _log2.is_standardized = (
                                                        int(_data.get("character_consistency", 8)) >= 8 and
                                                        int(_data.get("art_style_match", 8)) >= 8
                                                    )
                                                    _db2.commit()
                                                st.success("Phân tích lại thành công! Đang tải lại...")
                                                st.rerun()
                                            except Exception as _ex2:
                                                _db2.rollback()
                                                st.error(f"Lỗi cập nhật DB: {_ex2}")
                                            finally:
                                                _db2.close()
                                        except Exception as _ex:
                                            st.error(f"Lỗi phân tích lại: {_ex}")
