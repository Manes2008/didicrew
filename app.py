# MIT License
# Copyright (c) 2026 Manes2008/didicrew

import streamlit as st
import os
import re
import datetime
import hashlib
import binascii
from streamlit_option_menu import option_menu
import config
from src.core.llm_provider import get_llm
from src.core.models import init_db, get_db_session, Channel, Project, ProjectStage, MediaFile, AllowedIP, User, ChannelStageConfig

st.set_page_config(page_title="VideoCrew Studio - Sản xuất video tự động", layout="wide", page_icon=":material/movie:")

# Nạp Bootstrap Icons cho trang chính
st.markdown(
    '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.css">',
    unsafe_allow_html=True
)

# ==================== DESIGN TOKENS & CSS ====================
st.markdown("""
<style>
    :root {
        --vc-radius-sm: 8px;
        --vc-radius-md: 12px;
        --vc-radius-lg: 16px;
        --vc-space-xs: 0.35rem;
        --vc-space-sm: 0.6rem;
        --vc-space-md: 1rem;
        --vc-space-lg: 1.5rem;
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
        padding: var(--vc-space-md);
        margin-bottom: var(--vc-space-md);
    }

    div[data-testid="stExpander"] {
        border: 1px solid var(--vc-border) !important;
        border-radius: var(--vc-radius-md) !important;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.05);
        overflow: hidden;
    }
    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: var(--vc-radius-md) !important;
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

    nav[data-testid="stSidebarNav"] { display: none; }

    .vc-stage-row {
        border: 1px solid var(--vc-border);
        border-radius: var(--vc-radius-sm);
        padding: 0.55rem 0.8rem;
        margin-bottom: 0.5rem;
        transition: border-color 0.15s ease;
    }
    .vc-stage-row:hover {
        border-color: var(--vc-border-strong);
    }
    .vc-stage-name {
        font-weight: 700;
        font-size: 0.85rem;
    }
    .vc-stage-role-pill {
        display: inline-block;
        font-size: 0.72rem;
        font-weight: 600;
        padding: 0.1rem 0.5rem;
        border-radius: 999px;
        background: var(--vc-accent-soft);
        color: var(--vc-accent-1);
    }
    .vc-stage-goal {
        color: var(--vc-muted);
        font-size: 0.78rem;
    }

    .vc-result-header {
        display: flex;
        align-items: center;
        gap: 0.4rem;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        color: var(--vc-muted);
        margin: 0.4rem 0 0.6rem 0;
    }
    hr { margin: 1rem 0 !important; }
</style>
""", unsafe_allow_html=True)

# Khởi tạo session_state flags
if "editing_channel" not in st.session_state:
    st.session_state["editing_channel"] = False
if "confirm_delete_channel" not in st.session_state:
    st.session_state["confirm_delete_channel"] = False
if "show_add_config" not in st.session_state:
    st.session_state["show_add_config"] = False
if "editing_config_id" not in st.session_state:
    st.session_state["editing_config_id"] = None
if "_last_channel_for_edit" not in st.session_state:
    st.session_state["_last_channel_for_edit"] = None

# Khởi tạo database
try:
    init_db()
except Exception as e:
    st.error(f"Không thể kết nối hoặc khởi tạo Database: {e}")
    st.stop()

# ==================== MÃ HÓA MẬT KHẨU ====================
def hash_password(password: str) -> str:
    salt = os.urandom(16)
    db_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return binascii.hexlify(salt).decode('utf-8') + ":" + binascii.hexlify(db_hash).decode('utf-8')

def verify_password(password: str, stored_hash: str) -> bool:
    try:
        salt_hex, hash_hex = stored_hash.split(":")
        salt = binascii.unhexlify(salt_hex)
        stored_db_hash = binascii.unhexlify(hash_hex)
        test_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
        return test_hash == stored_db_hash
    except Exception:
        return False

# ==================== CỔNG XÁC THỰC IP ====================
def get_client_ip() -> str:
    headers = st.context.headers
    for header in ["X-Forwarded-For", "X-Real-Ip", "CF-Connecting-IP", "True-Client-Ip"]:
        ip_val = headers.get(header)
        if ip_val:
            return ip_val.split(",")[0].strip()
    return "127.0.0.1"

def show_login_register_gate(client_ip: str):
    st.markdown("""
        <div style="text-align:center; margin-top: 2rem; margin-bottom: 1.5rem;">
            <div class="vc-logo-mark" style="margin: 0 auto 0.8rem auto; width:52px; height:52px; border-radius:14px; font-size:24px;"><i class="bi bi-camera-reels-fill"></i></div>
            <h2 style="margin-bottom:0.2rem;">Cổng xác thực VideoCrew Studio</h2>
            <div style="color: var(--vc-muted); font-size:0.9rem;">Đăng nhập hoặc đăng ký để bắt đầu sản xuất video</div>
        </div>
    """, unsafe_allow_html=True)

    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        st.info(f"Thiết bị hiện tại (IP: `{client_ip}`) chưa được phê duyệt. Vui lòng đăng nhập để tiếp tục.")
        auth_mode = st.radio("Chọn hành động", ["Đăng nhập", "Đăng ký tài khoản"], horizontal=True, label_visibility="collapsed")

    db = get_db_session()

    try:
        if auth_mode == "Đăng nhập":
            with mid:
                with st.container(border=True):
                    with st.form("login_form"):
                        username = st.text_input("Tên đăng nhập")
                        password = st.text_input("Mật khẩu", type="password")
                        submitted = st.form_submit_button("Đăng nhập", use_container_width=True, type="primary")

                        if submitted:
                            if not username or not password:
                                st.error("Vui lòng nhập đầy đủ thông tin")
                            else:
                                user = db.query(User).filter_by(username=username.strip().lower()).first()
                                if user and verify_password(password, user.password_hash):
                                    if not user.is_active:
                                        st.error("Tài khoản này đã bị khóa.")
                                    else:
                                        existing = db.query(AllowedIP).filter_by(ip_address=client_ip).first()
                                        if existing:
                                            existing.status = "approved"
                                            existing.user_id = user.id
                                            existing.approved_at = datetime.datetime.utcnow()
                                        else:
                                            new_entry = AllowedIP(
                                                ip_address=client_ip,
                                                label=f"Tự động duyệt: {user.username}",
                                                status="approved",
                                                user_id=user.id,
                                                approved_at=datetime.datetime.utcnow()
                                            )
                                            db.add(new_entry)
                                        db.commit()
                                        st.success("Đăng nhập thành công!")
                                        st.rerun()
                                else:
                                    st.error("Tên đăng nhập hoặc mật khẩu không chính xác.")
        else:
            with mid:
                with st.container(border=True):
                    with st.form("register_form"):
                        new_username = st.text_input("Tên đăng nhập")
                        new_password = st.text_input("Mật khẩu", type="password")
                        confirm_password = st.text_input("Xác nhận mật khẩu", type="password")
                        reg_submitted = st.form_submit_button("Đăng ký", use_container_width=True, type="primary")

                        if reg_submitted:
                            if not new_username or not new_password or not confirm_password:
                                st.error("Vui lòng nhập đầy đủ thông tin")
                            elif len(new_username.strip()) < 3:
                                st.error("Tên đăng nhập phải có ít nhất 3 ký tự")
                            elif len(new_password) < 6:
                                st.error("Mật khẩu phải có ít nhất 6 ký tự")
                            elif new_password != confirm_password:
                                st.error("Mật khẩu xác nhận không khớp")
                            else:
                                existing = db.query(User).filter_by(username=new_username.strip().lower()).first()
                                if existing:
                                    st.error("Tên đăng nhập đã được sử dụng")
                                else:
                                    user_count = db.query(User).count()
                                    role_val = "admin" if user_count == 0 else "user"
                                    hashed = hash_password(new_password)
                                    user = User(
                                        username=new_username.strip().lower(),
                                        password_hash=hashed,
                                        role=role_val
                                    )
                                    db.add(user)
                                    db.flush()

                                    existing_ip = db.query(AllowedIP).filter_by(ip_address=client_ip).first()
                                    if existing_ip:
                                        existing_ip.status = "approved"
                                        existing_ip.user_id = user.id
                                        existing_ip.approved_at = datetime.datetime.utcnow()
                                    else:
                                        new_ip = AllowedIP(
                                            ip_address=client_ip,
                                            label=f"Tự động duyệt: {user.username}",
                                            status="approved",
                                            user_id=user.id,
                                            approved_at=datetime.datetime.utcnow()
                                        )
                                        db.add(new_ip)

                                    db.commit()
                                    st.success("Đăng ký thành công!")
                                    st.rerun()
    except Exception as e:
        db.rollback()
        st.error(f"Lỗi hệ thống: {e}")
    finally:
        db.close()
    st.stop()

_client_ip = get_client_ip()
_db_check = get_db_session()
try:
    _ip_record = _db_check.query(AllowedIP).filter_by(ip_address=_client_ip).first()
    if _ip_record and _ip_record.status == "approved":
        if _ip_record.user_id:
            _user = _db_check.query(User).filter_by(id=_ip_record.user_id).first()
            if _user:
                if not _user.is_active:
                    st.error("Tài khoản của bạn đã bị khóa! Vui lòng liên hệ quản trị viên.")
                    st.stop()
                st.session_state["current_user"] = {
                    "id": _user.id,
                    "username": _user.username,
                    "role": _user.role
                }
            else:
                st.session_state["current_user"] = {"id": None, "username": f"Guest ({_client_ip})", "role": "user"}
        else:
            st.session_state["current_user"] = {"id": None, "username": f"Guest ({_client_ip})", "role": "user"}
finally:
    _db_check.close()

if _ip_record is None or _ip_record.status != "approved":
    show_login_register_gate(_client_ip)

# ==================== CÁC HẰNG SỐ ====================
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

# ==================== HEADER TRANG ====================
st.markdown("""
<div class="vc-header">
    <div class="vc-logo-mark"><i class="bi bi-camera-reels-fill"></i></div>
    <div class="main-title">VideoCrew Studio</div>
</div>
""", unsafe_allow_html=True)
st.markdown('<div class="sub-title">Hệ thống tự động hóa sản xuất Video ngắn đa nền tảng bằng AI</div>', unsafe_allow_html=True)

# ==================== SIDEBAR ====================
with st.sidebar:
    st.markdown("""
        <div class="vc-sidebar-brand">
            <div class="vc-logo-mark"><i class="bi bi-camera-reels-fill"></i></div>
            <div>
                <div class="vc-sidebar-brand-text">VideoCrew Studio</div>
                <div class="vc-sidebar-brand-sub">AI VIDEO PRODUCTION</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # --- Điều hướng chính ---
    selected_nav = option_menu(
        menu_title=None,
        options=["Sản xuất Video", "Quản lý Kênh", "Cấu hình AI"],
        icons=["camera-reels", "folder2-open", "sliders"],
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

    # --- Tài khoản ---
    if "current_user" in st.session_state:
        u_info = st.session_state["current_user"]
        st.markdown('<div class="vc-eyebrow"><i class="bi bi-person-circle"></i> Tài khoản</div>', unsafe_allow_html=True)
        st.markdown(f"""
            <div class="vc-account-card vc-sidebar-section">
                <div class="vc-account-row">
                    <span class="vc-account-label">Tên đăng nhập</span>
                    <span class="vc-account-value">{u_info['username']}</span>
                </div>
                <div class="vc-account-row">
                    <span class="vc-account-label">Vai trò</span>
                    <span class="user-badge">{u_info['role'].upper()}</span>
                </div>
                <div class="vc-account-row">
                    <span class="vc-account-label">Địa chỉ IP</span>
                    <span class="vc-account-value" style="font-family:monospace; font-size:0.76rem;">{_client_ip}</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

    # --- Cấu hình AI Model ---
    st.markdown('<div class="vc-eyebrow"><i class="bi bi-sliders"></i> Cấu hình AI Model</div>', unsafe_allow_html=True)
    with st.container(border=True):
        provider = st.selectbox("LLM Provider", ["OpenAI", "Google Gemini"], index=0)

        if provider == "OpenAI":
            model_options = ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"]
            model_name = st.selectbox("Model", model_options, index=0)
            api_key = config.OPENAI_API_KEY
        else:
            model_options = ["gemini-1.5-flash", "gemini-1.5-pro"]
            model_name = st.selectbox("Model", model_options, index=0)
            api_key = config.GEMINI_API_KEY

        video_engine_option = st.selectbox("Engine Sinh Video", ["Wan 2.1 Local", "Pollo AI (Cloud API)"], index=0)
        st.session_state["video_engine"] = "wan2.1_local" if video_engine_option == "Wan 2.1 Local" else "pollo_api"

    st.markdown('<div style="height:1.2rem;"></div>', unsafe_allow_html=True)

    if "current_user" in st.session_state and st.session_state["current_user"]["role"] == "admin":
        st.page_link("pages/Admin_IP_Manager.py", label="Quản lý IP (Admin)", icon=":material/shield_person:")
        st.markdown('<div style="height:0.4rem;"></div>', unsafe_allow_html=True)

    if st.button("Đăng xuất", icon=":material/logout:", type="secondary", use_container_width=True):
        db = get_db_session()
        try:
            if _client_ip != "127.0.0.1":
                ip_rec = db.query(AllowedIP).filter_by(ip_address=_client_ip).first()
                if ip_rec and not ip_rec.is_admin_ip:
                    ip_rec.status = "pending"
                    ip_rec.approved_at = None
                    db.commit()
        except Exception:
            db.rollback()
        finally:
            db.close()

        if "current_user" in st.session_state:
            del st.session_state["current_user"]
        st.rerun()

# ==================== MAIN AREA ====================
db = get_db_session()

channels = db.query(Channel).all()
if not channels:
    default_channel = Channel(
        name="Kênh Mặc Định",
        description="Kênh mặc định cho VideoCrew",
        goal="Tạo video TikTok/Reels thu hút"
    )
    db.add(default_channel)
    db.commit()
    channels = [default_channel]

channel_names = [c.name for c in channels]
channel_options = channel_names + ["+ Tạo kênh mới..."]

if "selected_channel_name" not in st.session_state or st.session_state["selected_channel_name"] not in channel_options:
    st.session_state["selected_channel_name"] = channel_names[0]

try:
    current_index = channel_options.index(st.session_state["selected_channel_name"])
except ValueError:
    current_index = 0

# ==================== TAB QUẢN LÝ KÊNH ====================
if selected_nav == "Quản lý Kênh":
    st.markdown('<div class="vc-eyebrow"><i class="bi bi-folder2-open"></i> Quản lý kênh</div>', unsafe_allow_html=True)
    st.subheader("Quản lý Kênh & Cấu hình Vai trò AI", anchor=False)
    col_chan, col_proj = st.columns([1, 1], gap="large")

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
                goal_text = f"{cfg.goal[:60]}..." if len(cfg.goal) > 60 else cfg.goal
                c3.markdown(f'<span class="vc-stage-goal">{goal_text}</span>', unsafe_allow_html=True)

                b1, b2 = c4.columns(2)
                if b1.button("", icon=":material/edit:", key=f"edit_cfg_{cfg.id}", help="Sửa cấu hình"):
                    st.session_state["editing_config_id"] = cfg.id
                    st.session_state["show_add_config"] = False
                    st.rerun()
                if b2.button("", icon=":material/delete:", key=f"del_cfg_{cfg.id}", help="Xóa cấu hình"):
                    db.delete(cfg)
                    db.commit()
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("Kênh này chưa có cấu hình vai trò AI cho các bước.")

    # ===== NÚT THÊM MỚI CẤU HÌNH =====
    if st.button("Thêm cấu hình bước", icon=":material/add:", use_container_width=False):
        st.session_state["show_add_config"] = True
        st.session_state["editing_config_id"] = None
        st.rerun()

    # ===== FORM THÊM / SỬA CẤU HÌNH =====
    if st.session_state.get("show_add_config") or st.session_state.get("editing_config_id"):
        editing_id = st.session_state.get("editing_config_id")
        if editing_id:
            cfg_edit = db.query(ChannelStageConfig).filter_by(id=editing_id).first()
            if cfg_edit:
                current_display = TECH_TO_DISPLAY.get(cfg_edit.stage_name, cfg_edit.stage_name)
                role_val = cfg_edit.role
                goal_val = cfg_edit.goal
                backstory_val = cfg_edit.backstory
                markdown_val = cfg_edit.markdown_template or ""
            else:
                st.session_state["editing_config_id"] = None
                st.rerun()
        else:
            current_display = list(STAGE_DISPLAY_NAMES.values())[0]
            role_val = ""
            goal_val = ""
            backstory_val = ""
            markdown_val = ""

        with st.container(border=True):
            st.markdown('<div class="vc-eyebrow"><i class="bi bi-pencil-square"></i> ' + ("Sửa cấu hình" if editing_id else "Thêm cấu hình mới") + '</div>', unsafe_allow_html=True)
            with st.form(key="config_form_main"):
                selected_display = st.selectbox(
                    "Bước",
                    options=list(STAGE_DISPLAY_NAMES.values()),
                    index=list(STAGE_DISPLAY_NAMES.values()).index(current_display) if current_display in STAGE_DISPLAY_NAMES.values() else 0
                )
                tech_name = DISPLAY_TO_TECH[selected_display]

                role = st.text_input("Vai trò", value=role_val)
                goal = st.text_area("Mục tiêu", value=goal_val)
                backstory = st.text_area("Mô tả nhân vật", value=backstory_val)
                markdown_template = st.text_area("Mẫu Markdown (không bắt buộc)", value=markdown_val, height=80)

                col_submit, col_cancel = st.columns([1, 1])
                submitted = col_submit.form_submit_button("Lưu cấu hình", type="primary", use_container_width=True)
                if submitted:
                    errors = []
                    if not role.strip():
                        errors.append("Vai trò không được để trống")
                    if not goal.strip():
                        errors.append("Mục tiêu không được để trống")
                    if not backstory.strip():
                        errors.append("Mô tả nhân vật không được để trống")
                    if errors:
                        for err in errors:
                            st.error(err)
                    else:
                        try:
                            if editing_id:
                                cfg_edit.stage_name = tech_name
                                cfg_edit.role = role.strip()
                                cfg_edit.goal = goal.strip()
                                cfg_edit.backstory = backstory.strip()
                                cfg_edit.markdown_template = markdown_template.strip() or None
                                db.commit()
                                st.success("Cập nhật thành công!")
                                del st.session_state["editing_config_id"]
                            else:
                                existing = db.query(ChannelStageConfig).filter_by(
                                    channel_id=selected_channel.id, stage_name=tech_name
                                ).first()
                                if existing:
                                    st.error("Bước này đã tồn tại trong kênh, vui lòng chọn bước khác.")
                                else:
                                    new_cfg = ChannelStageConfig(
                                        channel_id=selected_channel.id,
                                        stage_name=tech_name,
                                        role=role.strip(),
                                        goal=goal.strip(),
                                        backstory=backstory.strip(),
                                        markdown_template=markdown_template.strip() or None
                                    )
                                    db.add(new_cfg)
                                    db.commit()
                                    st.success("Thêm cấu hình thành công!")
                                    st.session_state["show_add_config"] = False
                            st.rerun()
                        except Exception as e:
                            db.rollback()
                            st.error(f"Lỗi lưu cấu hình: {e}")

                if col_cancel.form_submit_button("Hủy", use_container_width=True):
                    if st.session_state.get("editing_config_id"):
                        del st.session_state["editing_config_id"]
                    else:
                        st.session_state["show_add_config"] = False
                    st.rerun()

# ==================== TAB SẢN XUẤT VIDEO ====================
else:
    selected_channel = next(c for c in channels if c.name == st.session_state["selected_channel_name"])

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
                st.error(f"Thiếu API Key cho {provider}! Vui lòng kiểm tra lại file `.env`.")
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
                api_key=config.OPENAI_API_KEY if selected_project.provider == "OpenAI" else config.GEMINI_API_KEY,
                temperature=0.75
            )

    # WORKFLOW STEPPER MENU
    if "stage" in st.session_state:
        current = st.session_state["stage"]
        current_idx = STAGES_ORDER.index(current)

        st.markdown("---")
        st.markdown('<div class="vc-eyebrow"><i class="bi bi-collection-play"></i> Quy trình Sản xuất Video</div>', unsafe_allow_html=True)

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

            if st.button(f"Thực thi {selected_stage_display}", icon=":material/play_arrow:", type="primary"):
                with st.spinner(f"AI đang xử lý bước '{selected_stage_display}'..."):
                    if "llm" not in st.session_state:
                        st.error("Phiên làm việc hết hạn, vui lòng chọn lại Dự án.")
                        st.stop()

                    from src.core.engine import run_stage
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
                            if not stage_rec:
                                stage_rec = ProjectStage(project_id=project_id, stage_name=current, result_content=result, status="completed")
                                db.add(stage_rec)
                            else:
                                stage_rec.result_content = result
                                stage_rec.status = "completed"

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
                    image_paths = [line.replace("Đường dẫn ảnh:", "").strip() for line in result_text.split("\n") if "generated_images" in line and os.path.exists(line.replace("Đường dẫn ảnh:", "").strip())]
                    if image_paths:
                        cols = st.columns(min(len(image_paths), 3))
                        for idx, img_path in enumerate(image_paths):
                            cols[idx % len(cols)].image(img_path, caption=f"Ảnh {idx+1}")
                    else:
                        st.info(result_text)

                elif current == "video":
                    video_path = None
                    for line in result_text.split("\n"):
                        if "generated_videos" in line or ".mp4" in line:
                            video_path = line.replace("Đường dẫn video:", "").strip()
                            break
                    if video_path and os.path.exists(video_path):
                        st.video(video_path)
                    else:
                        st.info(result_text)
                else:
                    st.markdown(result_text)

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