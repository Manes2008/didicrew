# Admin IP Manager - Trang quản lý IP thiết bị
# Yêu cầu Admin Secret Key (trừ khi đã đăng nhập với role admin)

import streamlit as st
import datetime
import sys
import os
from streamlit_option_menu import option_menu

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import config
from src.core.models import init_db, get_db_session, AllowedIP, User

st.set_page_config(
    page_title="Admin - Quản lý IP Thiết bị | VideoCrew",
    page_icon=":material/shield_person:",
    layout="wide",
)

# ==================== CSS + BOOTSTRAP ICONS ====================
st.markdown(
    '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.css">',
    unsafe_allow_html=True
)

st.markdown("""
<style>
    :root {
        --vc-radius-sm: 8px;
        --vc-radius-md: 12px;
        --vc-border: rgba(128, 128, 128, 0.18);
        --vc-border-strong: rgba(128, 128, 128, 0.32);
        --vc-muted: #808495;
        --vc-accent-1: #C2542D;
        --vc-accent-2: #C99A45;
        --vc-accent-soft: rgba(194, 84, 45, 0.10);
        --vc-accent-soft-strong: rgba(194, 84, 45, 0.16);
    }

    .main .block-container {
        padding-top: 1.4rem !important;
        padding-bottom: 3rem !important;
        max-width: 1360px;
    }

    .vc-header {
        display: flex;
        align-items: center;
        gap: 0.65rem;
        margin-bottom: 0.1rem;
    }
    .vc-logo-mark {
        width: 40px;
        height: 40px;
        border-radius: 11px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 19px;
        color: #fff;
        background: linear-gradient(135deg, var(--vc-accent-1), var(--vc-accent-2));
        box-shadow: 0 3px 10px rgba(194, 84, 45, 0.20);
        flex-shrink: 0;
    }
    .main-title {
        font-size: 1.85rem;
        font-weight: 800;
        line-height: 1.1;
        background: linear-gradient(90deg, #C2542D, #C99A45);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    .sub-title {
        color: var(--vc-muted);
        font-size: 0.9rem;
        margin: 0.15rem 0 1.6rem 3.05rem;
    }
    .vc-eyebrow {
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: var(--vc-muted);
        margin: 0 0 0.5rem 0;
        display: flex;
        align-items: center;
        gap: 0.4rem;
    }
    .vc-card {
        border: 1px solid var(--vc-border);
        border-radius: var(--vc-radius-md);
        padding: 0.8rem 1rem;
        margin-bottom: 0.8rem;
        background: white;
    }
    .vc-account-card {
        border: 1px solid var(--vc-border);
        border-radius: var(--vc-radius-md);
        padding: 0.85rem 0.95rem;
        background: var(--vc-accent-soft);
    }
    .vc-account-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 0.82rem;
        padding: 0.18rem 0;
    }
    .vc-account-row + .vc-account-row {
        border-top: 1px dashed var(--vc-border);
    }
    .vc-account-label {
        color: var(--vc-muted);
    }
    .vc-account-value {
        font-weight: 600;
    }
    .user-badge {
        display: inline-block;
        padding: 0.14rem 0.55rem;
        border-radius: 999px;
        font-size: 0.68rem;
        font-weight: 700;
        letter-spacing: 0.03em;
        background-color: var(--vc-accent-soft-strong);
        color: var(--vc-accent-1);
    }
    .stButton > button {
        border-radius: var(--vc-radius-sm) !important;
        font-weight: 600 !important;
        transition: all 0.15s ease-in-out !important;
    }
    .stButton > button:hover {
        transform: translateY(-1px);
    }
    button[kind="primary"],
    button[data-testid="stBaseButton-primary"],
    button[kind="primaryFormSubmit"],
    button[data-testid="stBaseButton-primaryFormSubmit"] {
        background-color: var(--vc-accent-1) !important;
        border-color: var(--vc-accent-1) !important;
        color: #fff !important;
    }
    button[kind="primary"]:hover,
    button[data-testid="stBaseButton-primary"]:hover,
    button[kind="primaryFormSubmit"]:hover,
    button[data-testid="stBaseButton-primaryFormSubmit"]:hover {
        background-color: #A6482A !important;
        border-color: #A6482A !important;
        color: #fff !important;
    }
    div[data-testid="stExpander"] {
        border: 1px solid var(--vc-border) !important;
        border-radius: var(--vc-radius-md) !important;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.05);
        overflow: hidden;
    }
    nav[data-testid="stSidebarNav"] { display: none; }
    section[data-testid="stSidebar"] .block-container {
        padding-top: 1.1rem;
    }
    .vc-sidebar-brand {
        display: flex;
        align-items: center;
        gap: 0.55rem;
        margin-bottom: 1.1rem;
        padding-bottom: 0.9rem;
        border-bottom: 1px solid var(--vc-border);
    }
    .vc-sidebar-brand .vc-logo-mark {
        width: 34px;
        height: 34px;
        border-radius: 9px;
        font-size: 16px;
    }
    .vc-sidebar-brand-text {
        font-weight: 800;
        font-size: 1.02rem;
        line-height: 1.15;
    }
    .vc-sidebar-brand-sub {
        font-size: 0.7rem;
        color: var(--vc-muted);
        letter-spacing: 0.03em;
    }
    .vc-sidebar-section {
        margin-bottom: 1.3rem;
    }
    .metric-card {
        background: white;
        border-radius: var(--vc-radius-md);
        padding: 0.8rem 1rem;
        border: 1px solid var(--vc-border);
        text-align: center;
    }
    .metric-number {
        font-size: 2rem;
        font-weight: 700;
        line-height: 1.2;
        color: var(--vc-accent-1);
    }
    .metric-label {
        font-size: 0.78rem;
        color: var(--vc-muted);
        margin-top: 0.2rem;
    }
    .ip-row {
        border: 1px solid var(--vc-border);
        border-radius: var(--vc-radius-sm);
        padding: 0.65rem 0.9rem;
        margin-bottom: 0.5rem;
        background: white;
        transition: border-color 0.15s ease;
    }
    .ip-row:hover {
        border-color: var(--vc-border-strong);
    }
    .ip-address {
        font-family: monospace;
        font-weight: 700;
        font-size: 0.95rem;
    }
    .ip-label {
        color: var(--vc-muted);
        font-size: 0.78rem;
    }
    .ip-timestamp {
        font-size: 0.72rem;
        color: var(--vc-muted);
    }
    .status-badge {
        display: inline-block;
        padding: 0.1rem 0.55rem;
        border-radius: 999px;
        font-size: 0.68rem;
        font-weight: 600;
        background: var(--vc-accent-soft);
        color: var(--vc-accent-1);
    }
    hr { margin: 1rem 0 !important; }
</style>
""", unsafe_allow_html=True)

# ==================== KHỞI TẠO DB ====================
try:
    init_db()
except Exception as e:
    st.error(f"Lỗi kết nối DB: {e}")
    st.stop()

# ==================== HEADER ====================
st.markdown("""
<div class="vc-header">
    <div class="vc-logo-mark"><i class="bi bi-shield-lock-fill"></i></div>
    <div class="main-title">Quản lý IP Thiết bị</div>
</div>
""", unsafe_allow_html=True)
st.markdown('<div class="sub-title">Phê duyệt hoặc từ chối thiết bị truy cập vào VideoCrew Studio</div>', unsafe_allow_html=True)

# ==================== ADMIN AUTH ====================
if "admin_authenticated" not in st.session_state:
    st.session_state["admin_authenticated"] = False

if "current_user" in st.session_state and st.session_state["current_user"]["role"] == "admin":
    st.session_state["admin_authenticated"] = True

if not st.session_state["admin_authenticated"]:
    st.markdown('<div class="vc-eyebrow"><i class="bi bi-lock-fill"></i> Xác thực Admin</div>', unsafe_allow_html=True)
    with st.container(border=True):
        with st.form("admin_login_form"):
            key_input = st.text_input(
                "Nhập Admin Secret Key",
                type="password",
                placeholder="Nhập secret key...",
                label_visibility="collapsed"
            )
            submitted = st.form_submit_button("Đăng nhập", type="primary", use_container_width=True)
            if submitted:
                if key_input == config.ADMIN_SECRET_KEY:
                    st.session_state["admin_authenticated"] = True
                    st.rerun()
                else:
                    st.error("Secret key không chính xác. Thử lại.")
    st.stop()

# ==================== SIDEBAR ====================
with st.sidebar:
    st.markdown("""
        <div class="vc-sidebar-brand">
            <div class="vc-logo-mark"><i class="bi bi-camera-reels-fill"></i></div>
            <div>
                <div class="vc-sidebar-brand-text">VideoCrew Studio</div>
                <div class="vc-sidebar-brand-sub">ADMIN PANEL</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Navigation
    selected_nav = option_menu(
        menu_title=None,
        options=["Quản lý IP", "Quản lý Người dùng"],
        icons=["shield-check", "people"],
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "transparent", "margin-bottom": "1.2rem"},
            "icon": {"color": "#C99A45", "font-size": "16px"},
            "nav-link": {
                "font-size": "13.5px",
                "text-align": "left",
                "margin": "3px 0px",
                "border-radius": "8px",
                "padding": "9px 12px",
                "--hover-color": "rgba(194, 84, 45, 0.08)"
            },
            "nav-link-selected": {"background-color": "#C2542D", "font-weight": "600"},
        }
    )

    # Account info
    st.markdown('<div class="vc-eyebrow"><i class="bi bi-person-circle"></i> Tài khoản</div>', unsafe_allow_html=True)
    st.markdown("""
        <div class="vc-account-card vc-sidebar-section">
            <div class="vc-account-row">
                <span class="vc-account-label">Trạng thái</span>
                <span class="user-badge">ADMIN</span>
            </div>
            <div class="vc-account-row">
                <span class="vc-account-label">IP hiện tại</span>
                <span class="vc-account-value" style="font-family:monospace; font-size:0.76rem;">{ip}</span>
            </div>
        </div>
    """.format(ip=st.session_state.get("current_user", {}).get("ip", "N/A")), unsafe_allow_html=True)

    if st.button("Đăng xuất Admin", icon=":material/logout:", type="secondary", use_container_width=True):
        st.session_state["admin_authenticated"] = False
        st.rerun()

# ==================== MAIN CONTENT ====================
db = get_db_session()
try:
    all_ips = db.query(AllowedIP).order_by(AllowedIP.created_at.desc()).all()
finally:
    db.close()

pending  = [x for x in all_ips if x.status == "pending"]
approved = [x for x in all_ips if x.status == "approved"]
rejected = [x for x in all_ips if x.status == "rejected"]

# --- METRICS ---
st.markdown('<div class="vc-eyebrow"><i class="bi bi-bar-chart"></i> Tổng quan</div>', unsafe_allow_html=True)
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

# --- NỘI DUNG THEO TAB ---
if selected_nav == "Quản lý IP":
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
            with st.container():
                st.markdown('<div class="ip-row">', unsafe_allow_html=True)
                c1, c2, c3 = st.columns([4, 1, 1])
                c1.markdown(f'<span class="ip-address">{rec.ip_address}</span>', unsafe_allow_html=True)
                c1.markdown(f'<span class="ip-timestamp">Đăng ký lúc: {rec.created_at.strftime("%Y-%m-%d %H:%M:%S") if rec.created_at else "N/A"}</span>', unsafe_allow_html=True)

                if c2.button("Duyệt", key=f"ap_{rec.id}", type="primary", use_container_width=True):
                    db_a = get_db_session()
                    try:
                        r = db_a.query(AllowedIP).filter_by(id=rec.id).first()
                        if r:
                            r.status = "approved"
                            r.approved_at = datetime.datetime.utcnow()
                            db_a.commit()
                        st.success(f"Đã duyệt {rec.ip_address}")
                        st.rerun()
                    except Exception as ex:
                        db_a.rollback()
                        st.error(str(ex))
                    finally:
                        db_a.close()

                if c3.button("Từ chối", key=f"rj_{rec.id}", use_container_width=True):
                    db_a = get_db_session()
                    try:
                        r = db_a.query(AllowedIP).filter_by(id=rec.id).first()
                        if r:
                            r.status = "rejected"
                            db_a.commit()
                        st.warning(f"Đã từ chối {rec.ip_address}")
                        st.rerun()
                    except Exception as ex:
                        db_a.rollback()
                        st.error(str(ex))
                    finally:
                        db_a.close()
                st.markdown('</div>', unsafe_allow_html=True)

    with tab_approved:
        if not approved:
            st.info("Chưa có IP nào được duyệt.")
        for rec in approved:
            with st.container():
                st.markdown('<div class="ip-row">', unsafe_allow_html=True)
                c1, c2, c3 = st.columns([4, 1, 1])
                c1.markdown(f'<span class="ip-address">{rec.ip_address}</span> — <span class="ip-label">{rec.label or "Không có nhãn"}</span>', unsafe_allow_html=True)
                c1.markdown(f'<span class="ip-timestamp">Duyệt lúc: {rec.approved_at.strftime("%Y-%m-%d %H:%M:%S") if rec.approved_at else "N/A"}  |  Đăng ký: {rec.created_at.strftime("%Y-%m-%d %H:%M:%S") if rec.created_at else "N/A"}</span>', unsafe_allow_html=True)

                if c2.button("Từ chối", key=f"rv_{rec.id}", use_container_width=True):
                    db_a = get_db_session()
                    try:
                        r = db_a.query(AllowedIP).filter_by(id=rec.id).first()
                        if r:
                            r.status = "rejected"
                            r.approved_at = None
                            db_a.commit()
                        st.warning(f"Đã thu hồi quyền {rec.ip_address}")
                        st.rerun()
                    except Exception as ex:
                        db_a.rollback()
                        st.error(str(ex))
                    finally:
                        db_a.close()

                if c3.button("Xóa", key=f"dl_{rec.id}", use_container_width=True):
                    db_a = get_db_session()
                    try:
                        r = db_a.query(AllowedIP).filter_by(id=rec.id).first()
                        if r:
                            db_a.delete(r)
                            db_a.commit()
                        st.rerun()
                    except Exception as ex:
                        db_a.rollback()
                        st.error(str(ex))
                    finally:
                        db_a.close()
                st.markdown('</div>', unsafe_allow_html=True)

    with tab_rejected:
        if not rejected:
            st.info("Chưa có IP nào bị từ chối.")
        for rec in rejected:
            with st.container():
                st.markdown('<div class="ip-row">', unsafe_allow_html=True)
                c1, c2, c3 = st.columns([4, 1, 1])
                c1.markdown(f'<span class="ip-address">{rec.ip_address}</span>', unsafe_allow_html=True)
                c1.markdown(f'<span class="ip-timestamp">Đăng ký lúc: {rec.created_at.strftime("%Y-%m-%d %H:%M:%S") if rec.created_at else "N/A"}</span>', unsafe_allow_html=True)

                if c2.button("Phê duyệt lại", key=f"rea_{rec.id}", type="primary", use_container_width=True):
                    db_a = get_db_session()
                    try:
                        r = db_a.query(AllowedIP).filter_by(id=rec.id).first()
                        if r:
                            r.status = "approved"
                            r.approved_at = datetime.datetime.utcnow()
                            db_a.commit()
                        st.success(f"Đã phê duyệt lại {rec.ip_address}")
                        st.rerun()
                    except Exception as ex:
                        db_a.rollback()
                        st.error(str(ex))
                    finally:
                        db_a.close()

                if c3.button("Xóa", key=f"dlr_{rec.id}", use_container_width=True):
                    db_a = get_db_session()
                    try:
                        r = db_a.query(AllowedIP).filter_by(id=rec.id).first()
                        if r:
                            db_a.delete(r)
                            db_a.commit()
                        st.rerun()
                    except Exception as ex:
                        db_a.rollback()
                        st.error(str(ex))
                    finally:
                        db_a.close()
                st.markdown('</div>', unsafe_allow_html=True)

    with tab_add:
        st.markdown("Thêm IP thủ công và duyệt ngay lập tức (hoặc để chờ).")
        with st.container(border=True):
            with st.form("add_ip_form"):
                new_ip    = st.text_input("Địa chỉ IP", placeholder="Vd: 192.168.1.100 hoặc 118.69.52.156")
                new_label = st.text_input("Tên thiết bị / Ghi chú (tùy chọn)", placeholder="Vd: Laptop văn phòng, PC nhà...")
                auto_approve = st.checkbox("Phê duyệt ngay sau khi thêm", value=True)
                add_submitted = st.form_submit_button("Thêm IP", use_container_width=True, type="primary")

            if add_submitted:
                if not new_ip or not new_ip.strip():
                    st.error("Vui lòng nhập địa chỉ IP.")
                else:
                    db_a = get_db_session()
                    try:
                        existing = db_a.query(AllowedIP).filter_by(ip_address=new_ip.strip()).first()
                        if existing:
                            st.warning(f"IP `{new_ip.strip()}` đã tồn tại trong hệ thống (trạng thái: {existing.status}).")
                        else:
                            status_val = "approved" if auto_approve else "pending"
                            entry = AllowedIP(
                                ip_address=new_ip.strip(),
                                label=new_label.strip() if new_label else None,
                                status=status_val,
                                approved_at=datetime.datetime.utcnow() if auto_approve else None,
                            )
                            db_a.add(entry)
                            db_a.commit()
                            if auto_approve:
                                st.success(f"Đã thêm và phê duyệt IP `{new_ip.strip()}` thành công!")
                            else:
                                st.success(f"Đã thêm IP `{new_ip.strip()}` vào hàng chờ duyệt.")
                            st.rerun()
                    except ValueError as ve:
                        st.error(f"Dữ liệu không hợp lệ: {ve}")
                    except Exception as ex:
                        db_a.rollback()
                        st.error(f"Lỗi: {ex}")
                    finally:
                        db_a.close()

        st.divider()
        st.caption("IP hiện tại của bạn (để tham khảo):")
        try:
            headers = st.context.headers
            current_ip = None
            for h in ["X-Forwarded-For", "X-Real-Ip", "CF-Connecting-IP"]:
                v = headers.get(h)
                if v:
                    current_ip = v.split(",")[0].strip()
                    break
            st.code(current_ip or "127.0.0.1 (local)")
        except Exception:
            st.code("Không xác định được")

# --- TAB QUẢN LÝ NGƯỜI DÙNG ---
else:
    st.markdown('<div class="vc-eyebrow"><i class="bi bi-people-fill"></i> Quản lý người dùng</div>', unsafe_allow_html=True)
    db_u = get_db_session()
    try:
        users = db_u.query(User).order_by(User.created_at.desc()).all()
    finally:
        db_u.close()

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
                db_a = get_db_session()
                try:
                    r = db_a.query(User).filter_by(id=u.id).first()
                    if r:
                        r.role = "user" if r.role == "admin" else "admin"
                        db_a.commit()
                    st.rerun()
                except Exception as ex:
                    db_a.rollback()
                    st.error(str(ex))
                finally:
                    db_a.close()

            btn_lock_label = "Khóa" if u.is_active else "Mở khóa"
            if col3.button(btn_lock_label, key=f"lock_user_{u.id}", use_container_width=True):
                db_a = get_db_session()
                try:
                    r = db_a.query(User).filter_by(id=u.id).first()
                    if r:
                        r.is_active = not r.is_active
                        db_a.commit()
                    st.rerun()
                except Exception as ex:
                    db_a.rollback()
                    st.error(str(ex))
                finally:
                    db_a.close()

            if col4.button("Xóa", key=f"del_user_{u.id}", use_container_width=True):
                db_a = get_db_session()
                try:
                    r = db_a.query(User).filter_by(id=u.id).first()
                    if r:
                        db_a.delete(r)
                        db_a.commit()
                    st.rerun()
                except Exception as ex:
                    db_a.rollback()
                    st.error(str(ex))
                finally:
                    db_a.close()