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
    with st.container(border=True):
        from src.core.models import Channel, VideoDurationConfig
        import json
        
        channels = db.query(Channel).all()
        channel_names = [c.name for c in channels]
        
        # Chia layout hàng ngang cực kỳ gọn gàng (thêm cột xóa dự án)
        col_chan, col_proj, col_del_proj, col_dur_mode, col_dur_val, col_dur_save = st.columns([2.5, 3.0, 0.7, 2.3, 2.5, 1.2])
        
        with col_chan:
            try:
                chan_index = channel_names.index(selected_channel.name)
            except ValueError:
                chan_index = 0
            selected_chan_name = st.selectbox(
                "Chọn Kênh", 
                channel_names, 
                index=chan_index, 
                key="prod_channel_select"
            )
            if selected_chan_name != selected_channel.name:
                st.session_state["selected_channel_name"] = selected_chan_name
                if "project_id" in st.session_state:
                    st.session_state["project_id"] = None
                st.rerun()
                
        projects = db.query(Project).filter_by(channel_id=selected_channel.id).order_by(Project.id.desc()).all()
        project_options = ["+ Tạo dự án mới..."] + [f"#{p.id} - {p.idea[:30]}..." for p in projects]
        
        default_index = 0
        current_project_id = st.session_state.get("project_id")
        if current_project_id:
            for idx, opt in enumerate(project_options):
                if opt.startswith(f"#{current_project_id} -"):
                    default_index = idx
                    break
                    
        with col_proj:
            selected_project_opt = st.selectbox(
                "Chọn Dự án",
                project_options,
                index=default_index,
                key="project_select_main"
            )

        # Nút xóa dự án nhanh
        with col_del_proj:
            st.markdown('<div style="height: 28px;"></div>', unsafe_allow_html=True)
            is_existing_proj = selected_project_opt != "+ Tạo dự án mới..."
            if is_existing_proj:
                if st.button("Xóa", icon=":material/delete:", key="btn_del_proj_quick", help="Xóa dự án này", use_container_width=True):
                    st.session_state["confirm_delete_project"] = True
                    st.rerun()
            else:
                st.button("Xóa", icon=":material/delete:", key="btn_del_proj_disabled", disabled=True, use_container_width=True)

        # Dialog xác nhận xóa dự án
        if st.session_state.get("confirm_delete_project") and selected_project_opt != "+ Tạo dự án mới...":
            _del_pid = int(selected_project_opt.split(" - ")[0].replace("#", ""))
            _del_proj = db.query(Project).filter_by(id=_del_pid).first()
            if _del_proj:
                with st.container(border=True):
                    st.warning(f"Xóa dự án **#{_del_pid}** — `{_del_proj.idea[:50]}...` ?  \nThao tác này không thể hoàn tác.")
                    c_confirm_del, c_cancel_del = st.columns(2)
                    if c_confirm_del.button("Xác nhận xóa", type="primary", use_container_width=True, key="confirm_del_proj_btn"):
                        try:
                            db.delete(_del_proj)
                            db.commit()
                            st.session_state["confirm_delete_project"] = False
                            if st.session_state.get("project_id") == _del_pid:
                                st.session_state["project_id"] = None
                                st.session_state["idea"] = ""
                                for _k in ["stage", "results", "llm"]:
                                    st.session_state.pop(_k, None)
                            st.toast("Đã xóa dự án thành công!", icon=":material/delete:")
                            st.rerun()
                        except Exception as ex:
                            db.rollback()
                            st.error(f"Lỗi xóa dự án: {ex}")
                    if c_cancel_del.button("Hủy", use_container_width=True, key="cancel_del_proj_btn"):
                        st.session_state["confirm_delete_project"] = False
                        st.rerun()

        selected_project = None
        duration_cfg = None
        
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
        else:
            if st.session_state.get("project_id") is not None:
                st.session_state["project_id"] = None
                st.session_state["idea"] = ""
                if "stage" in st.session_state:
                    del st.session_state["stage"]
                if "results" in st.session_state:
                    del st.session_state["results"]
                st.rerun()
                
        # Hiển thị cấu hình thời lượng nhanh trên các cột
        DUR_TYPE_LABELS = {
            "system_generated": "Hệ thống",
            "uploaded_video": "Theo video nguồn ngoài"
        }
        DUR_TYPE_REVERSE = {v: k for k, v in DUR_TYPE_LABELS.items()}
        dur_label_options = list(DUR_TYPE_LABELS.values())

        with col_dur_mode:
            if selected_project and duration_cfg:
                cur_label = DUR_TYPE_LABELS.get(duration_cfg.duration_type, "Hệ thống")
                dur_label = st.selectbox(
                    "Thời lượng",
                    dur_label_options,
                    index=dur_label_options.index(cur_label) if cur_label in dur_label_options else 0,
                    key=f"prod_dur_type_{selected_project.id}"
                )
                dur_type = DUR_TYPE_REVERSE[dur_label]
            else:
                st.selectbox("Thời lượng", ["-"], disabled=True, key="prod_dur_type_disabled")
                dur_type = "system_generated"

        with col_dur_val:
            if selected_project and duration_cfg:
                if dur_type == "system_generated":
                    tgt_dur = st.number_input(
                        "Số giây",
                        min_value=0,
                        value=int(duration_cfg.target_duration or 0),
                        key=f"prod_tgt_dur_{selected_project.id}"
                    )
                    src_path = None
                else:
                    src_path = st.text_input(
                        "Video nguồn",
                        value=duration_cfg.video_source_path or "",
                        key=f"prod_src_path_{selected_project.id}",
                        placeholder="Đường dẫn file..."
                    )
                    tgt_dur = 0
            else:
                st.text_input("Giá trị", value="-", disabled=True, key="prod_dur_val_disabled")

        with col_dur_save:
            st.markdown('<div style="height: 28px;"></div>', unsafe_allow_html=True)
            if selected_project and duration_cfg:
                if st.button("Lưu", key=f"prod_save_dur_{selected_project.id}", type="primary", use_container_width=True):
                    duration_cfg.duration_type = dur_type
                    if dur_type == "system_generated":
                        duration_cfg.target_duration = tgt_dur
                    else:
                        duration_cfg.video_source_path = src_path.strip() if src_path and src_path.strip() else None
                    db.commit()
                    st.toast("Đã lưu cấu hình thời lượng!", icon=":material/check_circle:")
            else:
                st.button("Lưu", disabled=True, key="prod_save_dur_disabled", use_container_width=True)

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
                    db.flush()  # Để sinh ra new_proj.id tạm thời
                    
                    # Tự động nạp cấu hình thời lượng mặc định của Kênh
                    from src.core.models import ChannelStageConfig, VideoDurationConfig
                    import json
                    
                    channel_video_cfg = db.query(ChannelStageConfig).filter_by(
                        channel_id=selected_channel.id,
                        stage_name="video"
                    ).first()
                    
                    # Các thông số thời lượng mặc định
                    dur_type = "system_generated"
                    tgt_dur = 0
                    min_dur = 0
                    max_dur = 0
                    src_path = None
                    ratio_mult = 1.0
                    
                    if channel_video_cfg and channel_video_cfg.markdown_template:
                        try:
                            cfg_data = json.loads(channel_video_cfg.markdown_template)
                            dur_type = cfg_data.get("duration_type", "system_generated")
                            tgt_dur = int(cfg_data.get("target_duration", 0))
                            min_dur = int(cfg_data.get("min_duration", 0))
                            max_dur = int(cfg_data.get("max_duration", 0))
                            src_path = cfg_data.get("video_source_path")
                            ratio_mult = float(cfg_data.get("system_ratio_multiplier", 1.0))
                        except Exception:
                            pass
                            
                    # Tạo VideoDurationConfig cho Project mới
                    new_duration_cfg = VideoDurationConfig(
                        project_id=new_proj.id,
                        duration_type=dur_type,
                        target_duration=tgt_dur,
                        min_duration=min_dur,
                        max_duration=max_dur,
                        video_source_path=src_path,
                        system_ratio_multiplier=ratio_mult
                    )
                    db.add(new_duration_cfg)
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
    if "stage" in st.session_state and selected_project is not None:
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

                    from src.core.models import ChannelStageConfig, VideoDurationConfig
                    prev_stage = STAGES_ORDER[current_idx - 1] if current_idx > 0 else None
                    prev = st.session_state["results"].get(prev_stage, "") if prev_stage else ""

                    stage_config = db.query(ChannelStageConfig).filter_by(
                        channel_id=selected_channel.id, stage_name=current
                    ).first()

                    # Nạp cấu hình thời lượng từ DB để truyền động vào prompt viết kịch bản
                    duration_cfg = db.query(VideoDurationConfig).filter_by(project_id=st.session_state.get("project_id")).first()
                    target_duration_str = "25-30"
                    if duration_cfg:
                        if duration_cfg.target_duration and duration_cfg.target_duration > 0:
                            target_duration_str = f"{duration_cfg.target_duration}"
                        elif duration_cfg.max_duration and duration_cfg.max_duration > 0:
                            target_duration_str = f"dưới {duration_cfg.max_duration}"

                    context = {
                        "channel_name": selected_channel.name,
                        "channel_description": selected_channel.description,
                        "channel_goal": selected_channel.goal,
                        "video_engine": st.session_state.get("video_engine", "wan2.1_local"),
                        "image_engine": st.session_state.get("image_engine", "openai"),
                        "project_id": st.session_state.get("project_id"),
                        "target_duration": target_duration_str
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
                                for line in result.split("\n"):
                                    if "generated_images" in line:
                                        clean = line.replace("[ANH] Duong dan anh:", "").replace("Duong dan anh:", "").strip()
                                        if clean and os.path.exists(clean):
                                            image_paths.append(clean)
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
                            else:
                                stage_rec.result_content = result
                                stage_rec.media_path = media_path
                                stage_rec.status = "completed"
                            
                            # Lưu file ảnh vào DB (MediaFile)
                            if current == "image" and image_paths:
                                for img_path in image_paths:
                                    if os.path.exists(img_path):
                                        with open(img_path, "rb") as img_f:
                                            img_data = img_f.read()
                                        media_rec = MediaFile(
                                            project_stage_id=stage_rec.id,
                                            file_name=os.path.basename(img_path),
                                            file_data=img_data,
                                            media_type="image/png"
                                        )
                                        db.add(media_rec)

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

                    # Lấy visual prompt từ kết quả bước "visual" để khớp mô tả cảnh với ảnh
                    import re as _re_img
                    visual_result = st.session_state.get("results", {}).get("visual", "")
                    scene_descriptions = {}
                    if visual_result:
                        for m in _re_img.finditer(
                            r"(?:Scene|Cảnh)\s*(\d+)[\s*:\-–\.]+(.+?)(?=(?:Scene|Cảnh)\s*\d+[\s*:\-–\.]|\Z)",
                            visual_result,
                            _re_img.DOTALL | _re_img.IGNORECASE
                        ):
                            scene_descriptions[int(m.group(1))] = m.group(2).strip()[:300]

                    def _extract_img_paths_with_scene(text):
                        paths = []  # list of (scene_num, path)
                        for line in text.split("\n"):
                            if "generated_images" not in line:
                                continue
                            clean = line
                            for prefix in ["[ANH] Duong dan anh:", "Duong dan anh:"]:
                                clean = clean.replace(prefix, "")
                            clean = clean.strip()
                            if not clean:
                                continue
                            sm = _re_img.search(r"scene_?(\d+)", clean)
                            s_num = int(sm.group(1)) if sm else len(paths) + 1
                            paths.append((s_num, clean))
                        return paths

                    db_images = [m for m in media_files if m.file_data]
                    if db_images:
                        for idx, media in enumerate(db_images):
                            s_num = idx + 1
                            sm = _re_img.search(r"scene_?(\d+)", media.file_name or "")
                            if sm:
                                s_num = int(sm.group(1))
                            desc = scene_descriptions.get(s_num, "")
                            with st.container():
                                st.markdown(f"**Cảnh {s_num}**")
                                if desc:
                                    st.caption(desc)
                                st.image(media.file_data, use_container_width=True)
                    else:
                        img_scene_paths = _extract_img_paths_with_scene(result_text)
                        if img_scene_paths:
                            cols = st.columns(min(len(img_scene_paths), 3))
                            for col_idx, (s_num, img_path) in enumerate(img_scene_paths):
                                desc = scene_descriptions.get(s_num, "")
                                with cols[col_idx % len(cols)]:
                                    st.markdown(f"**Cảnh {s_num}**")
                                    if desc:
                                        st.caption(desc)
                                    if os.path.exists(img_path):
                                        st.image(img_path, use_container_width=True)
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
                                                img_paths = [l.replace("[ANH] Duong dan anh:", "").replace("Duong dan anh:", "").strip() for l in img_rec.result_content.split("\n") if "generated_images" in l]
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
                                    st.toast("Đang quét các cửa sổ ứng dụng trên Windows...", icon=":material/search:")
                                    import subprocess
                                    # Quét tất cả visible windows bằng Win32 API (đáng tin cậy hơn Get-Process)
                                    win32_scan_script = """
Add-Type @"
using System;
using System.Runtime.InteropServices;
using System.Text;
public class WinEnum {
    [DllImport("user32.dll")] public static extern bool EnumWindows(EnumWindowsProc lpEnumFunc, IntPtr lParam);
    [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern int GetWindowText(IntPtr hWnd, StringBuilder lpString, int nMaxCount);
    [DllImport("user32.dll")] public static extern int GetWindowTextLength(IntPtr hWnd);
    public delegate bool EnumWindowsProc(IntPtr hWnd, IntPtr lParam);
    public static System.Collections.Generic.List<string> GetVisibleWindowTitles() {
        var list = new System.Collections.Generic.List<string>();
        EnumWindows(delegate(IntPtr hwnd, IntPtr lParam) {
            if (IsWindowVisible(hwnd)) {
                int len = GetWindowTextLength(hwnd);
                if (len > 0) {
                    var sb = new StringBuilder(len + 1);
                    GetWindowText(hwnd, sb, sb.Capacity);
                    list.Add(sb.ToString());
                }
            }
            return true;
        }, IntPtr.Zero);
        return list;
    }
}
"@
[WinEnum]::GetVisibleWindowTitles()
"""
                                    check_res = subprocess.run(
                                        ["powershell", "-NoProfile", "-NonInteractive", "-Command", win32_scan_script],
                                        capture_output=True, text=True, timeout=10
                                    )
                                    window_titles = [line.strip() for line in check_res.stdout.split("\n") if line.strip()]

                                    # Tìm Veo3 bằng nhiều pattern khác nhau
                                    VEO_KEYWORDS = ["veo3", "veo 3", "google veo", "veo"]
                                    target_title = None
                                    for kw in VEO_KEYWORDS:
                                        target_title = next((t for t in window_titles if kw in t.lower()), None)
                                        if target_title:
                                            break

                                    if not target_title:
                                        # Hiển thị danh sách cửa sổ để user chọn thủ công
                                        st.warning("Không tự động tìm thấy cửa sổ Veo3. Vui lòng chọn thủ công từ danh sách bên dưới hoặc khởi động Veo3 trước.")
                                        if window_titles:
                                            manual_title = st.selectbox(
                                                "Chọn cửa sổ ứng dụng Veo3 thủ công:",
                                                ["-- Chọn --"] + window_titles,
                                                key="veo3_manual_window_select"
                                            )
                                            if manual_title and manual_title != "-- Chọn --":
                                                target_title = manual_title
                                        else:
                                            st.error("Không có cửa sổ nào đang mở. Vui lòng khởi động phần mềm Veo3 trước!")

                                    if target_title:
                                        st.toast(f"Đang kích hoạt cửa sổ: {target_title}...", icon=":material/rocket_launch:")
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

                                    with st.expander("Xem du lieu phan tich tho (Raw JSON)", expanded=False):
                                        st.json(metrics)
                            except Exception:
                                st.warning("Khong the phan tich dinh dang JSON cua metrics. Dang hien thi du lieu tho:")
                                st.code(log.analysis_metrics, language="json")

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
