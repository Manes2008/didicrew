import streamlit as st
from streamlit_option_menu import option_menu

def render_sidebar(client_ip):
    # Trích xuất thông tin người dùng từ session
    user_role = st.session_state.get("user_role", "USER")
    user_name = st.session_state.get("user_name", "Khách")

    with st.sidebar:
        # 1. Logo thương hiệu
        st.markdown("""
            <div class="vc-sidebar-brand">
                <div class="vc-logo-mark" style="display: flex; align-items: center; justify-content: center;">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                        <path d="M6 3a3 3 0 1 1-6 0 3 3 0 0 1 6 0zM9 6a3 3 0 1 1 0-6 3 3 0 0 1 0 6zM9 1.15a2.238 2.238 0 1 0 0 4.475A2.238 2.238 0 0 0 9 1.15zM5 2.15a2.238 2.238 0 1 0 0 4.475A2.238 2.238 0 0 0 5 2.15z"/>
                        <path d="M14 3a1 1 0 0 1 1 1v8a1 1 0 0 1-1 1H2a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1h12zM2 2a2 2 0 0 0-2 2v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2H2z"/>
                    </svg>
                </div>
                <div>
                    <div class="vc-sidebar-brand-text">VideoCrew Studio</div>
                    <div class="vc-sidebar-brand-sub">AI VIDEO PRODUCTION</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # 2. Điều hướng chính dựa trên quyền truy cập
        nav_options = ["Sản xuất Video", "Quản lý Kênh", "Cấu hình AI"]
        nav_icons = ["camera-reels", "folder2-open", "sliders"]

        # Nếu là ADMIN thì bổ sung mục Quản lý IP Admin
        if user_role == "ADMIN":
            nav_options.append("Quản lý IP Admin")
            nav_icons.append("shield-lock")

        selected_nav = option_menu(
            menu_title=None,
            options=nav_options,
            icons=nav_icons,
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

        # 3. Thông tin tài khoản người dùng
        st.markdown('<div class="vc-eyebrow"><i class="bi bi-person-circle"></i> Tài khoản</div>', unsafe_allow_html=True)
        st.markdown(f"""
            <div class="vc-account-card vc-sidebar-section">
                <div class="vc-account-row">
                    <span class="vc-account-label">Tên hiển thị</span>
                    <span class="vc-account-value">{user_name}</span>
                </div>
                <div class="vc-account-row">
                    <span class="vc-account-label">Vai trò</span>
                    <span class="user-badge">{"ADMIN" if user_role == "ADMIN" else "USER"}</span>
                </div>
                <div class="vc-account-row">
                    <span class="vc-account-label">Địa chỉ IP</span>
                    <span class="vc-account-value" style="font-family:monospace; font-size:0.76rem;">{client_ip}</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown('<div style="height:1rem;"></div>', unsafe_allow_html=True)

        # 4. Nút Đăng xuất
        if st.button("Đăng xuất", icon=":material/logout:", type="secondary", use_container_width=True):
            # Reset session state
            st.session_state["logged_in"] = False
            if "user_role" in st.session_state:
                del st.session_state["user_role"]
            if "user_name" in st.session_state:
                del st.session_state["user_name"]
            st.success("Đã đăng xuất!")
            st.rerun()

    return selected_nav
