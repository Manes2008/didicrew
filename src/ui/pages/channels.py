import streamlit as st
import json
import os
from src.core.models import Channel, Project, ChannelStageConfig, VideoDurationConfig, PromptOptimizationLog

# Các hằng số workflow
STAGE_DISPLAY_NAMES = {
    "script": "1. Viết kịch bản",
    "visual": "2. Mô tả hình ảnh",
    "image": "3. Tạo hình ảnh",
    "voice": "4. Tạo giọng đọc",
    "video": "5. Xuất Video"
}
STAGES_ORDER = ["script", "visual", "image", "voice", "video"]
TECH_TO_DISPLAY = STAGE_DISPLAY_NAMES

def _render_text_dual(text: str, key_prefix: str):
    """Hiển thị 2 tab: Trực quan (Markdown được render) và Raw (copy)."""
    def _clean(t):
        t = t.strip()
        if t.startswith("```markdown"):
            t = t[11:]
        elif t.startswith("```"):
            t = t[3:]
        if t.endswith("```"):
            t = t[:-3]
        return t.strip()
    tab_v, tab_r = st.tabs([":material/edit: Trực quan", ":material/content_copy: Raw Markdown"])
    with tab_v:
        st.markdown(_clean(text))
    with tab_r:
        st.code(text, language="markdown")

def render_channels_page(db):
    st.markdown('<div class="vc-eyebrow"><i class="bi bi-folder2-open"></i> Quản lý kênh</div>', unsafe_allow_html=True)
    st.subheader("Quản lý Kênh & Cấu hình Vai trò AI", anchor=False)
    col_chan, col_proj = st.columns([1, 1], gap="large")

    channels = db.query(Channel).all()
    channel_names = [c.name for c in channels]
    channel_options = channel_names + ["+ Tạo kênh mới..."]

    # Đảm bảo selected_channel_name hợp lệ
    if "selected_channel_name" not in st.session_state or st.session_state["selected_channel_name"] not in channel_options:
        st.session_state["selected_channel_name"] = channel_names[0] if channel_names else "+ Tạo kênh mới..."

    try:
        current_index = channel_options.index(st.session_state["selected_channel_name"])
    except ValueError:
        current_index = 0

    with col_chan:
        st.markdown('<div class="vc-eyebrow">Chọn Kênh Sản Xuất</div>', unsafe_allow_html=True)
        
        # Chia layout hàng ngang cho chọn kênh và sửa/xóa nhanh
        c_sel, c_edit, c_del = st.columns([5.5, 2.2, 2.3])
        
        with c_sel:
            selected_channel_opt = st.selectbox("Danh sách Kênh", channel_options, index=current_index, key="channel_select_main", label_visibility="collapsed")
            st.session_state["selected_channel_name"] = selected_channel_opt
            
        # Reset trạng thái sửa/xóa khi đổi kênh
        if st.session_state.get("_last_channel_for_edit") != selected_channel_opt:
            st.session_state["editing_channel"] = False
            st.session_state["confirm_delete_channel"] = False
            st.session_state["_last_channel_for_edit"] = selected_channel_opt

        if selected_channel_opt == "+ Tạo kênh mới...":
            with st.container(border=True):
                st.markdown('<div class="vc-eyebrow"><i class="bi bi-plus-circle"></i> Thêm Kênh Mới</div>', unsafe_allow_html=True)
                with st.form("create_channel_form_main"):
                    new_name = st.text_input("Tên kênh", placeholder="Ví dụ: Kênh Kể Chuyện AI")
                    new_desc = st.text_input("Mô tả kênh", placeholder="Mô tả ngắn...")
                    new_goal = st.text_area("Mục tiêu nội dung", value="Tạo video ngắn thu hút 100k view")
                    btn_create = st.form_submit_button("Tạo Kênh Mới", type="primary", width="stretch")

                    if btn_create:
                        if not new_name.strip() or not new_goal.strip():
                            st.error("Vui lòng điền đầy đủ tên và mục tiêu kênh")
                        else:
                            dup = db.query(Channel).filter_by(name=new_name.strip()).first()
                            if dup:
                                st.error("Tên kênh đã tồn tại!")
                            else:
                                try:
                                    new_chan = Channel(
                                        name=new_name.strip(),
                                        description=new_desc.strip() if new_desc else None,
                                        goal=new_goal.strip()
                                    )
                                    db.add(new_chan)
                                    db.flush()

                                    default_stages = [
                                        {"stage_name": "script", "role": "Biên kịch", "goal": "Viết kịch bản video hấp dẫn", "backstory": "Bạn là biên kịch chuyên nghiệp."},
                                        {"stage_name": "visual", "role": "Mô tả hình ảnh", "goal": "Tạo mô tả chi tiết cho AI vẽ", "backstory": "Bạn là chuyên gia concept visual."},
                                        {"stage_name": "image", "role": "Tạo hình ảnh", "goal": "Sinh ảnh minh họa sắc nét", "backstory": "Chuyên gia Prompt Engineer."},
                                        {"stage_name": "voice", "role": "Tạo giọng đọc", "goal": "Tạo file đọc truyền cảm", "backstory": "Chuyên gia lồng tiếng."},
                                        {"stage_name": "video", "role": "Dựng Video", "goal": "Ghép thành video hoàn chỉnh", "backstory": "Chuyên gia dựng phim."}
                                    ]
                                    for stage in default_stages:
                                        db.add(ChannelStageConfig(
                                            channel_id=new_chan.id,
                                            stage_name=stage["stage_name"],
                                            role=stage["role"],
                                            goal=stage["goal"],
                                            backstory=stage["backstory"]
                                        ))
                                    db.commit()
                                    st.success(f"Đã tạo kênh '{new_name.strip()}'!")
                                    st.session_state["selected_channel_name"] = new_name.strip()
                                    st.rerun()
                                except Exception as ex:
                                    db.rollback()
                                    st.error(f"Lỗi: {ex}")
            st.stop()

        selected_channel = next(c for c in channels if c.name == selected_channel_opt)
        
        with c_edit:
            if st.button("Sửa", icon=":material/edit:", key="btn_channel_edit_top", width="stretch"):
                st.session_state["editing_channel"] = True
                st.session_state["confirm_delete_channel"] = False
                st.rerun()
        with c_del:
            if st.button("Xóa", icon=":material/delete:", key="btn_channel_del_top", width="stretch"):
                st.session_state["confirm_delete_channel"] = True
                st.session_state["editing_channel"] = False
                st.rerun()

        st.markdown(f"**:material/target: Mục tiêu Kênh:** *{selected_channel.goal}*")

        # Form sửa kênh
        if st.session_state.get("editing_channel"):
            with st.container(border=True):
                st.markdown('<div class="vc-eyebrow"><i class="bi bi-pencil-square"></i> Sửa thông tin kênh</div>', unsafe_allow_html=True)
                with st.form("edit_channel_form_main"):
                    edit_name = st.text_input("Tên kênh", value=selected_channel.name)
                    edit_desc = st.text_input("Mô tả (không bắt buộc)", value=selected_channel.description or "")
                    edit_goal = st.text_area("Mục tiêu", value=selected_channel.goal)
                    c_save, c_cancel = st.columns(2)
                    save_edit = c_save.form_submit_button("Lưu thay đổi", type="primary", width="stretch")
                    cancel_edit = c_cancel.form_submit_button("Hủy", width="stretch")

                    if save_edit:
                        if not edit_name.strip() or not edit_goal.strip():
                            st.error("Vui lòng điền đầy đủ tên và mục tiêu")
                        else:
                            dup = db.query(Channel).filter(Channel.name == edit_name.strip(), Channel.id != selected_channel.id).first()
                            if dup:
                                st.error("Tên kênh đã tồn tại!")
                            else:
                                try:
                                    selected_channel.name = edit_name.strip()
                                    selected_channel.description = edit_desc.strip() or None
                                    selected_channel.goal = edit_goal.strip()
                                    db.commit()
                                    st.session_state["editing_channel"] = False
                                    st.session_state["selected_channel_name"] = selected_channel.name
                                    st.success("Cập nhật thành công!")
                                    st.rerun()
                                except Exception as ex:
                                    db.rollback()
                                    st.error(f"Lỗi: {ex}")
                    if cancel_edit:
                        st.session_state["editing_channel"] = False
                        st.rerun()

        # Xác nhận xóa kênh
        if st.session_state.get("confirm_delete_channel"):
            with st.container(border=True):
                st.warning(f"Bạn có chắc muốn xóa kênh **'{selected_channel.name}'**?")
                related_projects = db.query(Project).filter_by(channel_id=selected_channel.id).count()
                if related_projects > 0:
                    st.error(f"Kênh đang có {related_projects} dự án, không thể xóa.")
                    if st.button("Đóng", width="stretch"):
                        st.session_state["confirm_delete_channel"] = False
                        st.rerun()
                elif len(channels) <= 1:
                    st.error("Không thể xóa kênh cuối cùng.")
                    if st.button("Đóng", width="stretch"):
                        st.session_state["confirm_delete_channel"] = False
                        st.rerun()
                else:
                    c_confirm, c_cancel_del = st.columns(2)
                    if c_confirm.button("Xác nhận xóa", type="primary", width="stretch"):
                        try:
                            db.query(ChannelStageConfig).filter_by(channel_id=selected_channel.id).delete()
                            db.delete(selected_channel)
                            db.commit()
                            st.session_state["confirm_delete_channel"] = False
                            # Cập nhật lại danh sách kênh
                            remaining_channels = db.query(Channel).all()
                            if remaining_channels:
                                st.session_state["selected_channel_name"] = remaining_channels[0].name
                            st.success("Đã xóa kênh.")
                            st.rerun()
                        except Exception as ex:
                            db.rollback()
                            st.error(f"Lỗi: {ex}")
                    if c_cancel_del.button("Hủy", width="stretch"):
                        st.session_state["confirm_delete_channel"] = False
                        st.rerun()
        
        # ===== LƯỚI DANH SÁCH DỰ ÁN CỦA KÊNH =====
        st.markdown('<div class="vc-eyebrow" style="margin-top:2rem;"><i class="bi bi-grid-3x3-gap"></i> Lưới danh sách Dự án của Kênh</div>', unsafe_allow_html=True)
        projects = db.query(Project).filter_by(channel_id=selected_channel.id).order_by(Project.id.desc()).all()
        if not projects:
            st.info("Kênh này chưa có dự án nào.")
        else:
            import pandas as pd
            # Mapping trạng thái chính xác
            STATUS_BADGES = {
                "pending": "⏳ Chưa chạy",
                "running": ":material/sync: Đang chạy",
                "completed": ":material/check_circle: Hoàn thành",
                "failed": ":material/cancel: Thất bại"
            }
            project_data = []
            for p in projects:
                stage_name_display = STAGE_DISPLAY_NAMES.get(p.current_stage, p.current_stage)
                status_badge = STATUS_BADGES.get(p.status, p.status)
                project_data.append({
                    "Mã dự án": f"#{p.id}",
                    "Ý tưởng video": p.idea[:40] + "..." if len(p.idea) > 40 else p.idea,
                    "Bộ não AI": f"{p.provider} ({p.model_name})",
                    "Bước hiện tại": stage_name_display,
                    "Trạng thái": status_badge,
                    "Ngày tạo": p.created_at.strftime("%d/%m %H:%M")
                })
            df = pd.DataFrame(project_data)
            st.dataframe(
                df,
                width="stretch",
                hide_index=True,
                column_config={
                    "Mã dự án": st.column_config.TextColumn("Mã dự án", width="small"),
                    "Ý tưởng video": st.column_config.TextColumn("Ý tưởng video", width="medium"),
                    "Bộ não AI": st.column_config.TextColumn("Bộ não AI", width="small"),
                    "Bước hiện tại": st.column_config.TextColumn("Bước hiện tại", width="small"),
                    "Trạng thái": st.column_config.TextColumn("Trạng thái", width="small"),
                    "Ngày tạo": st.column_config.TextColumn("Ngày tạo", width="small")
                }
            )

    with col_proj:
        st.markdown('<div class="vc-eyebrow"><i class="bi bi-diagram-3"></i> Cấu hình Vai trò AI Các Bước</div>', unsafe_allow_html=True)

        # ===== CẤU HÌNH STAGE =====
        configs = db.query(ChannelStageConfig).filter_by(channel_id=selected_channel.id).all()
        if configs:
            # Sắp xếp cấu hình AI theo đúng thứ tự workflow chuẩn (1, 2, 3, 4, 5)
            configs = sorted(configs, key=lambda x: STAGES_ORDER.index(x.stage_name) if x.stage_name in STAGES_ORDER else 99)
            for cfg in configs:
                display_name = TECH_TO_DISPLAY.get(cfg.stage_name, cfg.stage_name)
                with st.container():
                    st.markdown('<div class="vc-stage-row">', unsafe_allow_html=True)
                    c1, c2, c3, c4 = st.columns([2.5, 2.2, 5, 1.4])
                    c1.markdown(f'<span class="vc-stage-name">{display_name}</span>', unsafe_allow_html=True)
                    c2.markdown(f'<span class="vc-stage-role-pill">{cfg.role}</span>', unsafe_allow_html=True)
                    c3.markdown(f'<span class="vc-stage-goal">{cfg.goal}</span>', unsafe_allow_html=True)
                    
                    # Nút Sửa vai trò
                    if c4.button("Sửa", key=f"btn_edit_stage_{cfg.id}", width="stretch"):
                        st.session_state["editing_config_id"] = cfg.id
                        st.session_state["show_add_config"] = True
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

        # Form sửa cấu hình stage
        if st.session_state.get("show_add_config") and st.session_state.get("editing_config_id"):
            cfg_id = st.session_state["editing_config_id"]
            cfg_rec = db.query(ChannelStageConfig).filter_by(id=cfg_id).first()
            if cfg_rec:
                with st.container(border=True):
                    st.subheader(f"Chỉnh sửa vai trò bước '{TECH_TO_DISPLAY.get(cfg_rec.stage_name, cfg_rec.stage_name)}'")
                    with st.form("edit_stage_form"):
                        role = st.text_input("Vai trò (Role)", value=cfg_rec.role)
                        goal = st.text_input("Mục tiêu (Goal)", value=cfg_rec.goal)
                        backstory = st.text_area("Lịch sử nền (Backstory)", value=cfg_rec.backstory)
                        markdown_template = st.text_area("Markdown Template (Chỉ dành cho viết kịch bản)", value=cfg_rec.markdown_template or "", placeholder="Nhập cấu trúc kịch bản...")
                        
                        col_save, col_cancel = st.columns(2)
                        if col_save.form_submit_button("Lưu cấu hình", type="primary", width="stretch"):
                            try:
                                cfg_rec.role = role.strip()
                                cfg_rec.goal = goal.strip()
                                cfg_rec.backstory = backstory.strip()
                                cfg_rec.markdown_template = markdown_template.strip() if markdown_template.strip() else None
                                db.commit()
                                st.success("Cập nhật vai trò AI thành công!")
                                del st.session_state["editing_config_id"]
                                st.session_state["show_add_config"] = False
                                st.rerun()
                            except Exception as ex:
                                db.rollback()
                                st.error(f"Lỗi lưu: {ex}")
                        if col_cancel.form_submit_button("Hủy", width="stretch"):
                            del st.session_state["editing_config_id"]
                            st.session_state["show_add_config"] = False
                            st.rerun()

    # ===== 3. Cấu hình thời lượng video (Cả Kênh & Dự án) =====
    st.markdown("---")
    st.markdown('<div class="vc-eyebrow" style="margin-top:1.5rem;"><i class="bi bi-clock-history"></i> Cấu hình thời lượng video (Bước 5)</div>', unsafe_allow_html=True)
    
    if 'selected_channel' in locals() and selected_channel:
        tab_channel, tab_project = st.tabs(["Cấu hình mặc định cho Kênh", "Cấu hình riêng cho từng Dự án"])
        
        with tab_channel:
            # Nạp cấu hình thời lượng của Kênh từ bảng ChannelStageConfig (stage_name="video", cột markdown_template)
            video_cfg = db.query(ChannelStageConfig).filter_by(
                channel_id=selected_channel.id, 
                stage_name="video"
            ).first()
            
            # Giá trị mặc định
            dur_type = "system_generated"
            tgt_dur = 0
            min_dur = 0
            max_dur = 0
            src_path = ""
            ratio_mult = 1.0
            
            if video_cfg and video_cfg.markdown_template:
                try:
                    cfg_data = json.loads(video_cfg.markdown_template)
                    dur_type = cfg_data.get("duration_type", "system_generated")
                    tgt_dur = int(cfg_data.get("target_duration", 0))
                    min_dur = int(cfg_data.get("min_duration", 0))
                    max_dur = int(cfg_data.get("max_duration", 0))
                    src_path = cfg_data.get("video_source_path", "")
                    ratio_mult = float(cfg_data.get("system_ratio_multiplier", 1.0))
                except Exception:
                    pass
                    
            with st.container(border=True):
                col_dur1, col_dur2 = st.columns(2)
                DUR_LABELS = {"system_generated": "Hệ thống", "uploaded_video": "Theo video nguồn ngoài"}
                DUR_REVERSE = {v: k for k, v in DUR_LABELS.items()}
                dur_label_opts = list(DUR_LABELS.values())
                with col_dur1:
                    cur_dur_label = DUR_LABELS.get(dur_type, "Hệ thống")
                    dur_type_input_label = st.selectbox(
                        "Chế độ thời lượng",
                        dur_label_opts,
                        index=dur_label_opts.index(cur_dur_label) if cur_dur_label in dur_label_opts else 0,
                        key=f"chan_dur_type_{selected_channel.id}"
                    )
                    dur_type_input = DUR_REVERSE[dur_type_input_label]
                    tgt_dur_input = st.number_input(
                        "Thời lượng mong muốn (giây, 0 = theo âm thanh)",
                        min_value=0,
                        value=tgt_dur,
                        key=f"chan_tgt_dur_{selected_channel.id}"
                    )
                    min_dur_input = st.number_input(
                        "Thời lượng tối thiểu (giây)",
                        min_value=0,
                        value=min_dur,
                        key=f"chan_min_dur_{selected_channel.id}"
                    )
                with col_dur2:
                    max_dur_input = st.number_input(
                        "Thời lượng tối đa (giây, 0 = không giới hạn)",
                        min_value=0,
                        value=max_dur,
                        key=f"chan_max_dur_{selected_channel.id}"
                    )
                    src_path_input = st.text_input(
                        "Đường dẫn video nguồn (chế độ uploaded_video)",
                        value=src_path,
                        key=f"chan_src_path_{selected_channel.id}"
                    )
                    ratio_mult_input = st.slider(
                        "Hệ số co giãn (Speed multiplier)",
                        min_value=0.5,
                        max_value=3.0,
                        value=ratio_mult,
                        step=0.1,
                        key=f"chan_ratio_mult_{selected_channel.id}"
                    )
                
                if st.button("Lưu cấu hình thời lượng Kênh", key=f"chan_save_dur_{selected_channel.id}", type="primary", width="stretch"):
                    # Tìm hoặc tạo bản ghi ChannelStageConfig cho stage "video"
                    if not video_cfg:
                        video_cfg = ChannelStageConfig(
                            channel_id=selected_channel.id,
                            stage_name="video",
                            role="Dựng Video",
                            goal="Ghép thành video hoàn chỉnh",
                            backstory="Chuyên gia dựng phim"
                        )
                        db.add(video_cfg)
                    
                    duration_data = {
                        "duration_type": dur_type_input,
                        "target_duration": tgt_dur_input,
                        "min_duration": min_dur_input,
                        "max_duration": max_dur_input,
                        "video_source_path": src_path_input.strip() if src_path_input.strip() else None,
                        "system_ratio_multiplier": ratio_mult_input
                    }
                    video_cfg.markdown_template = json.dumps(duration_data)
                    db.commit()
                    st.success("Đã lưu cấu hình thời lượng mặc định của Kênh thành công!")
        
        with tab_project:
            projects = db.query(Project).filter_by(channel_id=selected_channel.id).order_by(Project.id.desc()).all()
            if not projects:
                st.info("Kênh này chưa có dự án nào để cấu hình thời lượng video.")
            else:
                project_options = [f"#{p.id} - {p.idea[:40]}..." for p in projects]
                selected_project_opt = st.selectbox("Chọn Dự án để cấu hình thời lượng", project_options, key="channels_project_select")
                
                project_id = int(selected_project_opt.split(" - ")[0].replace("#", ""))
                selected_project = next((p for p in projects if p.id == project_id), None)
                
                if selected_project:
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
                            DUR_LABELS_P = {"system_generated": "Hệ thống", "uploaded_video": "Theo video nguồn ngoài"}
                            DUR_REVERSE_P = {v: k for k, v in DUR_LABELS_P.items()}
                            dur_label_opts_p = list(DUR_LABELS_P.values())
                            cur_p_label = DUR_LABELS_P.get(duration_cfg.duration_type, "Hệ thống")
                            dur_type_label_p = st.selectbox(
                                "Chế độ thời lượng",
                                dur_label_opts_p,
                                index=dur_label_opts_p.index(cur_p_label) if cur_p_label in dur_label_opts_p else 0,
                                key=f"channels_dur_type_{selected_project.id}"
                            )
                            dur_type = DUR_REVERSE_P[dur_type_label_p]
                            tgt_dur = st.number_input(
                                "Thời lượng mong muốn (giây, 0 = theo âm thanh)",
                                min_value=0,
                                value=int(duration_cfg.target_duration or 0),
                                key=f"channels_tgt_dur_{selected_project.id}"
                            )
                            min_dur = st.number_input(
                                "Thời lượng tối thiểu (giây)",
                                min_value=0,
                                value=int(duration_cfg.min_duration or 0),
                                key=f"channels_min_dur_{selected_project.id}"
                            )
                        with col_dur2:
                            max_dur = st.number_input(
                                "Thời lượng tối đa (giây, 0 = không giới hạn)",
                                min_value=0,
                                value=int(duration_cfg.max_duration or 0),
                                key=f"channels_max_dur_{selected_project.id}"
                            )
                            src_path = st.text_input(
                                "Đường dẫn video nguồn (chế độ uploaded_video)",
                                value=duration_cfg.video_source_path or "",
                                key=f"channels_src_path_{selected_project.id}"
                            )
                            ratio_mult = st.slider(
                                "Hệ số co giãn (Speed multiplier)",
                                min_value=0.5,
                                max_value=3.0,
                                value=float(duration_cfg.system_ratio_multiplier or 1.0),
                                step=0.1,
                                key=f"channels_ratio_mult_{selected_project.id}"
                            )
                        
                        if st.button("Lưu cấu hình thời lượng Dự án", key=f"channels_save_dur_{selected_project.id}", type="primary", width="stretch"):
                            duration_cfg.duration_type = dur_type
                            duration_cfg.target_duration = tgt_dur
                            duration_cfg.min_duration = min_dur
                            duration_cfg.max_duration = max_dur
                            duration_cfg.video_source_path = src_path.strip() if src_path.strip() else None
                            duration_cfg.system_ratio_multiplier = ratio_mult
                            db.commit()
                            st.success("Đã lưu cấu hình thời lượng dự án thành công!")

        # ===== 4. Bộ phân tích hiệu suất & Tự tối ưu Prompt (Chỉ dành cho ADMIN) =====
        if st.session_state.get("user_role") == "ADMIN":
            st.markdown('<div class="vc-eyebrow" style="margin-top:1.5rem;"><i class="bi bi-cpu"></i> Bộ Phân Tích Hiệu Suất & Tối Ưu Prompt (ADMIN ONLY)</div>', unsafe_allow_html=True)
            
            projects = db.query(Project).filter_by(channel_id=selected_channel.id).order_by(Project.id.desc()).all()
            if not projects:
                st.info("Kênh này chưa có dự án nào để xem phân tích hiệu suất.")
            else:
                project_options = [f"#{p.id} - {p.idea[:40]}..." for p in projects]
                selected_project_opt = st.selectbox("Chọn Dự án để xem phân tích hiệu suất", project_options, key="channels_log_project_select")
                
                project_id = int(selected_project_opt.split(" - ")[0].replace("#", ""))
                selected_project = next((p for p in projects if p.id == project_id), None)
                
                if selected_project:
                    with st.container(border=True):
                        st.markdown("### Lịch sử Tự tối ưu Prompt & Phân tích chất lượng kịch bản")
                        
                        logs = db.query(PromptOptimizationLog).filter_by(project_id=selected_project.id).order_by(PromptOptimizationLog.created_at.desc()).all()
                        
                        if not logs:
                            st.info("Chưa có dữ liệu phân tích hiệu suất cho dự án này.")
                        else:
                            for log in logs:
                                step_title = "Bước 1: Phân tích Ý tưởng" if log.step_name == "step_1_analysis" else "Bước 2: Viết Kịch bản chi tiết"
                                status_badge = "[Đạt chuẩn]" if log.is_standardized else "[Cần tối ưu]"
                                
                                with st.container(border=True):
                                    st.markdown(f"**{step_title}** -- {status_badge} -- *{log.created_at.strftime('%Y-%m-%d %H:%M:%S')}*")
                                    
                                    st.markdown("**Đầu vào ban đầu (Original input):**")
                                    _render_text_dual(log.user_input_content or "", f"input_{log.id}")
                                    
                                    st.markdown("**Kết quả đã tối ưu / sửa đổi (Adjusted prompt / result):**")
                                    _render_text_dual(log.adjusted_prompt or "", f"adj_{log.id}")
                                    
                                    if log.analysis_metrics:
                                        try:
                                            metrics = json.loads(log.analysis_metrics)
                                            st.markdown("**Chỉ số phân tích hiệu suất:**")
                                            col_m1, col_m2, col_m3, col_m4 = st.columns(4)
                                            with col_m1:
                                                st.metric("Tone / Tông giọng", metrics.get("tone", "N/A"))
                                            with col_m2:
                                                st.metric("Mật độ từ khóa", metrics.get("keyword_density", "N/A"))
                                            with col_m3:
                                                st.metric("Thời lượng dự kiến", metrics.get("estimated_duration", "N/A"))
                                            with col_m4:
                                                if "transition_score" in metrics:
                                                    st.metric("Điểm liền mạch", f"{metrics['transition_score']}/10")
                                                else:
                                                    st.metric("Trạng thái", "Đã phân tích")
                                                    
                                            if "feedback" in metrics and metrics["feedback"]:
                                                st.markdown(f"**Ý kiến phản hồi:** *{metrics['feedback']}*")
                                            if "attempts" in metrics:
                                                st.markdown(f"**Số lần viết lại tự động:** `{metrics['attempts']}`")

                                            with st.expander("Xem du lieu phan tich tho (Raw JSON)", expanded=False):
                                                st.json(metrics)
                                        except Exception:
                                            st.warning("Khong the phan tich dinh dang JSON cua metrics. Dang hien thi du lieu tho:")
                                            st.code(log.analysis_metrics, language="json")
