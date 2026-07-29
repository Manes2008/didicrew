import streamlit as st
from src.core.models import Channel, Project, ChannelStageConfig

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
                    btn_create = st.form_submit_button("Tạo Kênh Mới", type="primary", use_container_width=True)

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
        st.caption(f"Mục tiêu Kênh: {selected_channel.goal}")

        # ===== SỬA / XÓA KÊNH =====
        col_edit, col_del = st.columns(2)
        with col_edit:
            if st.button("Sửa kênh", icon=":material/edit:", use_container_width=True):
                st.session_state["editing_channel"] = True
                st.session_state["confirm_delete_channel"] = False
                st.rerun()
        with col_del:
            if st.button("Xóa kênh", icon=":material/delete:", use_container_width=True):
                st.session_state["confirm_delete_channel"] = True
                st.session_state["editing_channel"] = False
                st.rerun()

        # Form sửa kênh
        if st.session_state.get("editing_channel"):
            with st.container(border=True):
                st.markdown('<div class="vc-eyebrow"><i class="bi bi-pencil-square"></i> Sửa thông tin kênh</div>', unsafe_allow_html=True)
                with st.form("edit_channel_form_main"):
                    edit_name = st.text_input("Tên kênh", value=selected_channel.name)
                    edit_desc = st.text_input("Mô tả (không bắt buộc)", value=selected_channel.description or "")
                    edit_goal = st.text_area("Mục tiêu", value=selected_channel.goal)
                    c_save, c_cancel = st.columns(2)
                    save_edit = c_save.form_submit_button("Lưu thay đổi", type="primary", use_container_width=True)
                    cancel_edit = c_cancel.form_submit_button("Hủy", use_container_width=True)

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
                    if st.button("Đóng", use_container_width=True):
                        st.session_state["confirm_delete_channel"] = False
                        st.rerun()
                elif len(channels) <= 1:
                    st.error("Không thể xóa kênh cuối cùng.")
                    if st.button("Đóng", use_container_width=True):
                        st.session_state["confirm_delete_channel"] = False
                        st.rerun()
                else:
                    c_confirm, c_cancel_del = st.columns(2)
                    if c_confirm.button("Xác nhận xóa", type="primary", use_container_width=True):
                        import datetime
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
                    if c_cancel_del.button("Hủy", use_container_width=True):
                        st.session_state["confirm_delete_channel"] = False
                        st.rerun()

    with col_proj:
        st.markdown("---")
        st.markdown('<div class="vc-eyebrow"><i class="bi bi-diagram-3"></i> Cấu hình Vai trò AI Các Bước</div>', unsafe_allow_html=True)

        # ===== CẤU HÌNH STAGE =====
        configs = db.query(ChannelStageConfig).filter_by(channel_id=selected_channel.id).all()
        if configs:
            for cfg in configs:
                display_name = TECH_TO_DISPLAY.get(cfg.stage_name, cfg.stage_name)
                with st.container():
                    st.markdown('<div class="vc-stage-row">', unsafe_allow_html=True)
                    c1, c2, c3, c4 = st.columns([2, 2, 5, 1.4])
                    c1.markdown(f'<span class="vc-stage-name">{display_name}</span>', unsafe_allow_html=True)
                    c2.markdown(f'<span class="vc-stage-role-pill">{cfg.role}</span>', unsafe_allow_html=True)
                    c3.markdown(f'<span class="vc-stage-goal">{cfg.goal}</span>', unsafe_allow_html=True)
                    
                    # Nút Sửa vai trò
                    if c4.button("Sửa", key=f"btn_edit_stage_{cfg.id}", size="small", use_container_width=True):
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
                        if col_save.form_submit_button("Lưu cấu hình", type="primary", use_container_width=True):
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
                        if col_cancel.form_submit_button("Hủy", use_container_width=True):
                            del st.session_state["editing_config_id"]
                            st.session_state["show_add_config"] = False
                            st.rerun()
