# MIT License
# Copyright (c) 2026 Manes2008/didicrew

import streamlit as st
import os
import sys

# Đảm bảo đường dẫn import hoạt động đúng
root_dir = os.path.abspath(os.path.dirname(__file__))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

import config
from src.core.models import init_db, get_db_session, Channel

# 1. Cấu hình trang Streamlit
st.set_page_config(
    page_title="VideoCrew Studio - Sản xuất video tự động", 
    layout="wide", 
    page_icon=":material/movie:"
)

# 2. Khởi tạo database
try:
    init_db()
except Exception as e:
    st.error(f"Không thể kết nối hoặc khởi tạo Database: {e}")
    st.stop()

# 3. Lấy IP khách truy cập
def get_client_ip() -> str:
    headers = st.context.headers
    for header in ["X-Forwarded-For", "X-Real-Ip", "CF-Connecting-IP", "True-Client-Ip"]:
        ip_val = headers.get(header)
        if ip_val:
            return ip_val.split(",")[0].strip()
    return "127.0.0.1"

_client_ip = get_client_ip()

# 4. Inject styles CSS tùy biến
from src.ui.styles import inject_custom_css
inject_custom_css(logged_in=st.session_state.get("logged_in", False))

# 5. Xác thực bắt buộc (Auth Gate)
from src.ui.auth import render_login_page
render_login_page()

# 6. Render Sidebar và lấy tuỳ chọn menu điều hướng
from src.ui.sidebar import render_sidebar
selected_nav = render_sidebar(_client_ip)

# 7. Khởi tạo database session và các kênh
db = get_db_session()
try:
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

    # Thiết lập kênh mặc định đang chọn
    channel_names = [c.name for c in channels]
    if "selected_channel_name" not in st.session_state or st.session_state["selected_channel_name"] not in channel_names:
        st.session_state["selected_channel_name"] = channel_names[0]

    selected_channel = next((c for c in channels if c.name == st.session_state["selected_channel_name"]), channels[0])

    # 8. Lấy cấu hình AI Key & Model
    provider = st.session_state.get("provider", "OpenAI")
    if provider == "OpenAI":
        api_key = st.session_state.get("custom_openai_key") or config.OPENAI_API_KEY
        model_name = st.session_state.get("model_name", "gpt-4o-mini")
    else:
        api_key = st.session_state.get("custom_gemini_key") or config.GEMINI_API_KEY
        model_name = st.session_state.get("model_name", "gemini-1.5-flash")

    # Header trang chính
    st.markdown("""
    <div class="vc-header">
        <div class="vc-logo-mark"><i class="bi bi-camera-reels-fill"></i></div>
        <div class="main-title">VideoCrew Studio</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Hệ thống tự động hóa sản xuất Video ngắn đa nền tảng bằng AI</div>', unsafe_allow_html=True)

    # 9. Điều hướng render các trang chức năng
    if selected_nav == "Sản xuất Video":
        from src.ui.pages.production import render_production_page
        render_production_page(db, api_key, provider, model_name, selected_channel)

    elif selected_nav == "Quản lý Kênh":
        from src.ui.pages.channels import render_channels_page
        render_channels_page(db)

    elif selected_nav == "Cấu hình AI":
        from src.ui.pages.config import render_config_page
        render_config_page(db, selected_channel)

    elif selected_nav == "Phân tích hiệu quả":
        from src.ui.pages.analytics import render_analytics_page
        render_analytics_page(db, selected_channel)

    elif selected_nav == "Quản lý IP Admin":
        from src.ui.pages.ip_manager import render_ip_manager_page
        render_ip_manager_page(db)

    elif selected_nav == "Cấu hình RustDesk":
        from src.ui.pages.rustdesk_page import render_rustdesk_page
        render_rustdesk_page()

finally:
    db.close()