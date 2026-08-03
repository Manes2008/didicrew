import streamlit as st
import datetime
from src.core.models import get_db_session, AllowedIP, User

def render_ip_manager_page(db):
    # Header cẩn chỉnh giống các tab khác trong app.py
    st.markdown('<div class="vc-eyebrow"><i class="bi bi-shield-lock-fill"></i> Quản lý thiết bị</div>', unsafe_allow_html=True)
    st.subheader("Quản lý IP & Thiết bị Truy cập", anchor=False)
    st.markdown('<div class="sub-title">Giám sát, phê duyệt hoặc từ chối thiết bị truy cập vào VideoCrew Studio</div>', unsafe_allow_html=True)

    # Đọc danh sách IP
    all_ips = db.query(AllowedIP).order_by(AllowedIP.created_at.desc()).all()

    pending  = [x for x in all_ips if x.status == "pending"]
    approved = [x for x in all_ips if x.status == "approved"]
    rejected = [x for x in all_ips if x.status == "rejected"]

    # --- METRICS ---
    st.markdown('<div class="vc-eyebrow"><i class="bi bi-bar-chart"></i> Tổng quan thiết bị</div>', unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-number">{len(all_ips)}</div>
                <div class="metric-label">Tổng IP</div>
            </div>
        """, unsafe_allow_html=True)
    with m2:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-number" style="color:#e67e22;">{len(pending)}</div>
                <div class="metric-label">Chờ duyệt</div>
            </div>
        """, unsafe_allow_html=True)
    with m3:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-number" style="color:#27ae60;">{len(approved)}</div>
                <div class="metric-label">Đã duyệt</div>
            </div>
        """, unsafe_allow_html=True)
    with m4:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-number" style="color:#e74c3c;">{len(rejected)}</div>
                <div class="metric-label">Từ chối</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Điều hướng phụ bằng st.radio hoặc tabs
    admin_sub_nav = st.radio("Chọn bảng quản lý", ["Quản lý IP thiết bị", "Quản lý Người dùng hệ thống"], horizontal=True)

    if admin_sub_nav == "Quản lý IP thiết bị":
        tab_pending, tab_approved, tab_rejected, tab_add = st.tabs([
            f"Chờ duyệt ({len(pending)})",
            f"Đã duyệt ({len(approved)})",
            f"Từ chối ({len(rejected)})",
            "Thêm IP thủ công",
        ])

        with tab_pending:
            if not pending:
                st.info("Không có IP nào đang chờ duyệt.")
            for rec in pending:
                with st.container(border=True):
                    c1, c2, c3 = st.columns([5, 1.2, 1.2])
                    admin_badge = ' <span style="background:#e67e22;color:#fff;padding:2px 8px;border-radius:12px;font-size:0.72rem;font-weight:700;">ADMIN IP</span>' if rec.is_admin_ip else ''
                    c1.markdown(
                        f'<span style="font-weight:700;font-size:1rem;">{rec.ip_address}</span>{admin_badge}'  
                        f'<br><span style="color:#aaa;font-size:0.8rem;">⏱️ Đăng ký: {rec.created_at.strftime("%d/%m/%Y %H:%M") if rec.created_at else "N/A"}</span>'  
                        + (f'<br><span style="color:#bbb;font-size:0.78rem;">📝 {rec.label}</span>' if rec.label else ''),
                        unsafe_allow_html=True
                    )
                    if c2.button("Duyệt", key=f"ap_{rec.id}", type="primary", use_container_width=True):
                        try:
                            rec.status = "approved"
                            rec.approved_at = datetime.datetime.utcnow()
                            db.commit()
                            st.success(f"Đã duyệt {rec.ip_address}")
                            st.rerun()
                        except Exception as ex:
                            db.rollback()
                            st.error(str(ex))
                    if c3.button("Từ chối", key=f"rj_{rec.id}", use_container_width=True):
                        try:
                            rec.status = "rejected"
                            db.commit()
                            st.warning(f"Đã từ chối {rec.ip_address}")
                            st.rerun()
                        except Exception as ex:
                            db.rollback()
                            st.error(str(ex))

        with tab_approved:
            if not approved:
                st.info("Chưa có IP nào được duyệt.")
            for rec in approved:
                with st.container(border=True):
                    c1, c2, c3 = st.columns([5, 1.2, 1.2])
                    admin_badge = ' <span style="background:#27ae60;color:#fff;padding:2px 8px;border-radius:12px;font-size:0.72rem;font-weight:700;">ADMIN IP</span>' if rec.is_admin_ip else ''
                    c1.markdown(
                        f'<span style="font-weight:700;font-size:1rem;">{rec.ip_address}</span>{admin_badge}'  
                        + (f' — <span style="color:#bbb;font-size:0.82rem;">{rec.label}</span>' if rec.label else '')  
                        + f'<br><span style="color:#aaa;font-size:0.8rem;">✅ Duyệt: {rec.approved_at.strftime("%d/%m/%Y %H:%M") if rec.approved_at else "N/A"}  |  ⏱️ Đăng ký: {rec.created_at.strftime("%d/%m/%Y %H:%M") if rec.created_at else "N/A"}</span>',
                        unsafe_allow_html=True
                    )
                    if c2.button("Thu hồi", key=f"rv_{rec.id}", use_container_width=True):
                        try:
                            rec.status = "rejected"
                            rec.approved_at = None
                            db.commit()
                            st.warning(f"Đã thu hồi quyền {rec.ip_address}")
                            st.rerun()
                        except Exception as ex:
                            db.rollback()
                            st.error(str(ex))
                    if c3.button("Xóa", key=f"dl_{rec.id}", use_container_width=True):
                        try:
                            db.delete(rec)
                            db.commit()
                            st.rerun()
                        except Exception as ex:
                            db.rollback()
                            st.error(str(ex))

        with tab_rejected:
            if not rejected:
                st.info("Chưa có IP nào bị từ chối.")
            for rec in rejected:
                with st.container(border=True):
                    c1, c2, c3 = st.columns([5, 1.4, 1.2])
                    admin_badge = ' <span style="background:#7f8c8d;color:#fff;padding:2px 8px;border-radius:12px;font-size:0.72rem;">ADMIN IP</span>' if rec.is_admin_ip else ''
                    c1.markdown(
                        f'<span style="font-weight:700;font-size:1rem;text-decoration:line-through;color:#aaa;">{rec.ip_address}</span>{admin_badge}'  
                        + f'<br><span style="color:#aaa;font-size:0.8rem;">⏱️ Đăng ký: {rec.created_at.strftime("%d/%m/%Y %H:%M") if rec.created_at else "N/A"}</span>',
                        unsafe_allow_html=True
                    )
                    if c2.button("Phê duyệt lại", key=f"rea_{rec.id}", type="primary", use_container_width=True):
                        try:
                            rec.status = "approved"
                            rec.approved_at = datetime.datetime.utcnow()
                            db.commit()
                            st.success(f"Đã phê duyệt lại {rec.ip_address}")
                            st.rerun()
                        except Exception as ex:
                            db.rollback()
                            st.error(str(ex))
                    if c3.button("Xóa", key=f"dlr_{rec.id}", use_container_width=True):
                        try:
                            db.delete(rec)
                            db.commit()
                            st.rerun()
                        except Exception as ex:
                            db.rollback()
                            st.error(str(ex))

        with tab_add:
            st.markdown("Thêm IP thủ công và duyệt ngay lập tức (hoặc để chờ).")
            with st.container(border=True):
                with st.form("add_ip_form_internal"):
                    new_ip    = st.text_input("Địa chỉ IP", placeholder="Vd: 192.168.1.100")
                    new_label = st.text_input("Ghi chú thiết bị", placeholder="Vd: PC cá nhân...")
                    auto_approve = st.checkbox("Phê duyệt ngay sau khi thêm", value=True)
                    add_submitted = st.form_submit_button("Thêm IP", use_container_width=True, type="primary")

                if add_submitted:
                    if not new_ip or not new_ip.strip():
                        st.error("Vui lòng nhập địa chỉ IP.")
                    else:
                        try:
                            existing = db.query(AllowedIP).filter_by(ip_address=new_ip.strip()).first()
                            if existing:
                                st.warning(f"IP `{new_ip.strip()}` đã tồn tại (trạng thái: {existing.status}).")
                            else:
                                status_val = "approved" if auto_approve else "pending"
                                entry = AllowedIP(
                                    ip_address=new_ip.strip(),
                                    label=new_label.strip() if new_label else None,
                                    status=status_val,
                                    approved_at=datetime.datetime.utcnow() if auto_approve else None,
                                )
                                db.add(entry)
                                db.commit()
                                st.success("Thêm IP thành công!")
                                st.rerun()
                        except Exception as ex:
                            db.rollback()
                            st.error(f"Lỗi: {ex}")

    else:
        # --- TAB QUẢN LÝ NGƯỜI DÙNG ---
        users = db.query(User).order_by(User.created_at.desc()).all()
        if not users:
            st.info("Chưa có người dùng nào đăng ký.")
        for u in users:
            with st.container(border=True):
                col1, col2, col3, col4 = st.columns([3, 1.5, 1.5, 1])
                status_text = "Hoạt động" if u.is_active else "Đã khóa"
                status_icon = "bi-check-circle-fill" if u.is_active else "bi-x-circle-fill"
                col1.markdown(f'<i class="bi {status_icon}" style="color:{"#27ae60" if u.is_active else "#e74c3c"};"></i> <strong>{u.username}</strong> — <span class="user-badge">{u.role.upper()}</span> ({status_text})', unsafe_allow_html=True)
                col1.caption(f"Ngày tạo: {u.created_at.strftime('%Y-%m-%d %H:%M') if u.created_at else 'N/A'}")

                if col2.button("Đổi vai trò", key=f"role_user_{u.id}", use_container_width=True):
                    try:
                        u.role = "user" if u.role == "admin" else "admin"
                        db.commit()
                        st.rerun()
                    except Exception as ex:
                        db.rollback()
                        st.error(str(ex))

                btn_lock_label = "Khóa" if u.is_active else "Mở khóa"
                if col3.button(btn_lock_label, key=f"lock_user_{u.id}", use_container_width=True):
                    try:
                        u.is_active = not u.is_active
                        db.commit()
                        st.rerun()
                    except Exception as ex:
                        db.rollback()
                        st.error(str(ex))

                if col4.button("Xóa", key=f"del_user_{u.id}", use_container_width=True):
                    try:
                        db.delete(u)
                        db.commit()
                        st.rerun()
                    except Exception as ex:
                        db.rollback()
                        st.error(str(ex))
