import streamlit as st
import os
import hashlib
import binascii
import datetime
import re
from src.core.models import get_db_session, User, AllowedIP

# ==================== PHẦN MÃ HÓA MẬT KHẨU ====================
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

# ==================== BẢO MẬT & VALIDATION DỮ LIỆU ====================
def validate_username(username: str) -> tuple[bool, str]:
    username = username.strip()
    if not username:
        return False, "Tên đăng nhập không được để trống!"
    if len(username) < 3 or len(username) > 20:
        return False, "Tên đăng nhập phải từ 3 đến 20 ký tự!"
    pattern = r'^[a-zA-Z0-9_]+$'
    if not re.match(pattern, username):
        return False, "Tên đăng nhập chỉ được chứa chữ cái, chữ số và dấu gạch dưới (_), không chứa khoảng trắng!"
    return True, ""

def validate_password(password: str) -> tuple[bool, str]:
    if not password:
        return False, "Mật khẩu không được để trống!"
    if len(password) < 8:
        return False, "Mật khẩu phải có tối thiểu 8 ký tự!"
    if len(password) > 64:
        return False, "Mật khẩu không được vượt quá 64 ký tự!"
    has_letter = any(c.isalpha() for c in password)
    has_digit = any(c.isdigit() for c in password)
    if not (has_letter and has_digit):
        return False, "Mật khẩu phải bao gồm cả chữ cái và chữ số!"
    return True, ""

# ==================== LẤY IP TRUY CẬP ====================
def get_client_ip() -> str:
    headers = st.context.headers
    for header in ["X-Forwarded-For", "X-Real-Ip", "CF-Connecting-IP", "True-Client-Ip"]:
        ip_val = headers.get(header)
        if ip_val:
            return ip_val.split(",")[0].strip()
    return "127.0.0.1"

# ==================== PHÂN TÍCH THIẾT BỊ ====================
def parse_user_agent(ua_string: str) -> str:
    if not ua_string:
        return "Thiết bị không xác định"
    os_name = "Unknown OS"
    browser = "Unknown Browser"
    
    if "Windows" in ua_string:
        os_name = "Windows"
    elif "Macintosh" in ua_string or "Mac OS" in ua_string:
        os_name = "macOS"
    elif "Android" in ua_string:
        os_name = "Android"
    elif "iPhone" in ua_string or "iPad" in ua_string:
        os_name = "iOS"
    elif "Linux" in ua_string:
        os_name = "Linux"
        
    if "Chrome" in ua_string and "Safari" in ua_string:
        browser = "Chrome"
    elif "Safari" in ua_string and "Chrome" not in ua_string:
        browser = "Safari"
    elif "Firefox" in ua_string:
        browser = "Firefox"
    elif "Edge" in ua_string:
        browser = "Edge"
        
    return f"{os_name} • {browser}"

# ==================== CUSTOM CSS INJECTION ====================
def inject_custom_css(logged_in=True):
    st.markdown(
        '''
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.css">
        ''',
        unsafe_allow_html=True
    )
    
    if not logged_in:
        st.markdown("""
        <style>
            section[data-testid="stSidebar"] {
                display: none !important;
            }
        </style>
        """, unsafe_allow_html=True)
    
    st.markdown("""
<style>
    :root {
        --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        --vc-radius-sm: 8px;
        --vc-radius-md: 12px;
        --vc-radius-lg: 18px;
        --vc-accent-1: #C2542D;
        --vc-accent-2: #C99A45;
        --vc-accent-gradient: linear-gradient(135deg, #C2542D 0%, #C99A45 100%);
    }

    html, body, [class*="css"] {
        font-family: var(--font-sans) !important;
    }

    .main .block-container {
        padding-top: 2rem !important;
        padding-bottom: 3.5rem !important;
        max-width: 1360px;
    }

    .stButton > button {
        border-radius: var(--vc-radius-sm) !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
    }
    .stButton > button:hover {
        transform: translateY(-1px);
    }

    button[kind="primary"],
    button[data-testid="stBaseButton-primary"],
    button[kind="primaryFormSubmit"],
    button[data-testid="stBaseButton-primaryFormSubmit"] {
        background: var(--vc-accent-gradient) !important;
        border: none !important;
        color: #ffffff !important;
    }

    div[data-baseweb="input"] {
        border-radius: var(--vc-radius-sm) !important;
    }

    nav[data-testid="stSidebarNav"] { display: none; }
</style>
""", unsafe_allow_html=True)

# ==================== MANAGE LOGIN PAGE ====================
def render_login_page():
    if st.session_state.get("logged_in", False):
        return True

    client_ip = get_client_ip()
    user_agent = st.context.headers.get("User-Agent", "")
    device_info = parse_user_agent(user_agent)

    st.markdown("""
        <style>
        body {
            background-color: #0b0f19 !important;
            overflow-x: hidden;
        }

        /* Ambient Glow Orbs */
        .bg-orb {
            position: fixed;
            border-radius: 50%;
            filter: blur(90px);
            opacity: 0.45;
            z-index: 0;
            pointer-events: none;
            animation: orbFloat 14s infinite ease-in-out alternate;
        }
        .bg-orb-1 { width: 360px; height: 360px; background: #C2542D; top: 15%; left: 30%; }
        .bg-orb-2 { width: 300px; height: 300px; background: #C99A45; bottom: 15%; right: 30%; animation-delay: -5s; }

        @keyframes orbFloat {
            0% { transform: translate(0, 0) scale(1); }
            100% { transform: translate(-30px, 40px) scale(1.1); }
        }

        /* Khung Form Cố Định Độ Rộng Chuẩn 370px */
        div:has(#login-gate) div[data-testid="stVerticalBlockBorderWrapper"] {
            position: relative;
            z-index: 10;
            max-width: 370px !important;
            width: 100% !important;
            margin: 30px auto 0 auto !important;
            padding: 2rem 1.6rem !important;
            border-radius: 20px !important;
            border: 1px solid rgba(255, 255, 255, 0.12) !important;
            box-shadow: 0 30px 60px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.15) !important;
            background: rgba(18, 24, 38, 0.7) !important;
            backdrop-filter: blur(20px) !important;
            -webkit-backdrop-filter: blur(20px) !important;
        }

        /* Branding Header */
        .auth-header {
            text-align: center;
            margin-bottom: 1.4rem;
        }
        .auth-logo {
            width: 48px;
            height: 48px;
            margin: 0 auto 0.75rem auto;
            border-radius: 14px;
            background: linear-gradient(135deg, #C2542D 0%, #C99A45 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            color: #ffffff;
            box-shadow: 0 8px 20px rgba(194, 84, 45, 0.4);
        }
        .auth-title {
            font-size: 1.5rem;
            font-weight: 800;
            letter-spacing: -0.02em;
            background: linear-gradient(90deg, #FF7A50, #FFC86B);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin: 0 0 0.2rem 0;
        }
        .auth-subtitle {
            color: #94A3B8;
            font-size: 0.8rem;
            margin: 0;
        }

        /* Security Footer Badge */
        .auth-security-footer {
            margin-top: 1.2rem;
            padding-top: 0.85rem;
            border-top: 1px dashed rgba(255, 255, 255, 0.12);
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.7rem;
            color: #64748B;
        }
        .auth-badge {
            background-color: rgba(255, 255, 255, 0.06);
            border: 1px solid rgba(255, 255, 255, 0.08);
            padding: 0.15rem 0.45rem;
            border-radius: 6px;
            font-weight: 600;
            color: #CBD5E1;
        }

        /* 🌟 ĐIỀU CHỈNH TABS CÂN BẰNG 50% - 50% & FIX GOM CỤC 🌟 */
        div[data-baseweb="tab-highlight"] {
            display: none !important; /* Ẩn vạch gạch chân mặc định */
        }
        
        div[data-baseweb="tab-list"] {
            display: flex !important;
            width: 100% !important;
            min-width: 100% !important;
            box-sizing: border-box !important;
            gap: 6px !important;
            margin-bottom: 1.2rem !important;
            background: rgba(0, 0, 0, 0.3) !important;
            padding: 4px !important;
            border-radius: 10px !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
        }

        /* Ép wrapper cha của từng tab giãn đều 50% */
        div[data-baseweb="tab-list"] > div,
        div[data-baseweb="tab-list"] [role="tab"] {
            flex: 1 1 50% !important;
            width: 50% !important;
            max-width: 50% !important;
        }

        /* Định dạng nút tab */
        div[data-baseweb="tab-list"] button[role="tab"] {
            width: 100% !important;
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
            text-align: center !important;
            height: 38px !important;
            border-radius: 7px !important;
            font-weight: 600 !important;
            font-size: 0.85rem !important;
            border: none !important;
            margin: 0 !important;
            background: transparent !important;
            color: #94A3B8 !important;
            transition: all 0.2s ease !important;
        }

        /* Style nổi bật cho Tab được chọn */
        div[data-baseweb="tab-list"] button[role="tab"][aria-selected="true"] {
            background: rgba(255, 255, 255, 0.12) !important;
            color: #FFFFFF !important;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3) !important;
        }
        </style>

        <div class="bg-orb bg-orb-1"></div>
        <div class="bg-orb bg-orb-2"></div>
    """, unsafe_allow_html=True)

    st.markdown('<div id="login-gate"></div>', unsafe_allow_html=True)

    _, col_center, _ = st.columns([1, 1.1, 1])

    with col_center:
        with st.container(border=True):
            st.markdown("""
                <div class="auth-header">
                    <div class="auth-logo">
                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" viewBox="0 0 16 16">
                            <path d="M15 14s1 0 1-1-1-4-5-4-5 3-5 4 1 1 1 1zm-7.978-1L7 12.996c.001-.264.167-1.03.76-1.72C8.312 10.629 9.282 10 11 10c1.717 0 2.687.63 3.24 1.276.593.69.758 1.457.76 1.72l-.008.002zM11 7a2 2 0 1 0 0-4 2 2 0 0 0 0 4m3-2a3 3 0 1 1-6 0 3 3 0 0 1 6 0M6.936 9.28a6 6 0 0 0-1.23-.247A7 7 0 0 0 5 9c-4 0-5 3-5 4 0 .667.333 1 1 1h4.216A2.238 2.238 0 0 1 5 13c0-1.01.377-2.042 1.09-2.904.243-.294.526-.569.846-.816M4.92 10A5.5 5.5 0 0 0 4 13H1c0-.26.164-1.03.76-1.724.545-.636 1.492-1.256 3.16-1.275ZM1.5 5.5a3 3 0 1 1 6 0 3 3 0 0 1-6 0m3-2a2 2 0 1 0 0 4 2 2 0 0 0 0-4"/>
                        </svg>
                    </div>
                    <h2 class="auth-title">VideoCrew Studio</h2>
                    <p class="auth-subtitle">Hệ thống sản xuất video tự động đa kênh</p>
                </div>
            """, unsafe_allow_html=True)

            admin_key_env = os.getenv("ADMIN_SECRET_KEY", "xR4q90gPLDGvU-VHra08adaK1BIqroR9qQ7l8boDNGw")
            db = get_db_session()

            try:
                tab_login, tab_register = st.tabs([":material/login: Đăng nhập", ":material/person_add: Đăng ký"])
                
                # --- TAB ĐĂNG NHẬP ---
                with tab_login:
                    with st.form("login_form_new", border=False):
                        username = st.text_input("Tên đăng nhập", placeholder="Nhập username...").strip()
                        password = st.text_input("Mật khẩu", type="password", placeholder="••••••••")
                        btn_login = st.form_submit_button("Xác nhận đăng nhập", type="primary", use_container_width=True)
                        
                        if btn_login:
                            if not username or not password:
                                st.error("Vui lòng nhập đầy đủ Tên đăng nhập và Mật khẩu!")
                            else:
                                if password == admin_key_env:
                                    existing_ip = db.query(AllowedIP).filter_by(ip_address=client_ip).first()
                                    if existing_ip and existing_ip.label and existing_ip.label.startswith("Didicrew"):
                                        admin_display_name = existing_ip.label.split(":")[0].strip()
                                    else:
                                        admin_ip_count = db.query(AllowedIP).filter(AllowedIP.label.like("Didicrew%")).count()
                                        admin_display_name = f"Didicrew{admin_ip_count + 1:02d}"

                                    st.session_state["logged_in"] = True
                                    st.session_state["user_role"] = "ADMIN"
                                    st.session_state["user_name"] = admin_display_name
                                    
                                    if existing_ip:
                                        existing_ip.status = "approved"
                                        existing_ip.label = f"{admin_display_name}: Admin ({device_info})"
                                        existing_ip.approved_at = datetime.datetime.utcnow()
                                    else:
                                        db.add(AllowedIP(
                                            ip_address=client_ip,
                                            label=f"{admin_display_name}: Admin ({device_info})",
                                            status="approved",
                                            approved_at=datetime.datetime.utcnow()
                                        ))
                                    db.commit()
                                    st.toast("Đăng nhập Admin thành công!", icon="🚀")
                                    st.rerun()
                                else:
                                    user = db.query(User).filter_by(username=username.lower()).first()
                                    if user and verify_password(password, user.password_hash):
                                        if not user.is_active:
                                            st.error("Tài khoản của bạn đã bị khóa! Vui lòng liên hệ Admin.")
                                        else:
                                            st.session_state["logged_in"] = True
                                            st.session_state["user_role"] = user.role.upper()
                                            st.session_state["user_name"] = user.username
                                            
                                            existing_ip = db.query(AllowedIP).filter_by(ip_address=client_ip).first()
                                            if existing_ip:
                                                existing_ip.status = "approved"
                                                existing_ip.user_id = user.id
                                                existing_ip.label = f"{user.username}: User ({device_info})"
                                                existing_ip.approved_at = datetime.datetime.utcnow()
                                            else:
                                                db.add(AllowedIP(
                                                    ip_address=client_ip,
                                                    label=f"{user.username}: User ({device_info})",
                                                    status="approved",
                                                    user_id=user.id,
                                                    approved_at=datetime.datetime.utcnow()
                                                ))
                                            db.commit()
                                            st.toast(f"Chào mừng trở lại, {user.username}!", icon="👋")
                                            st.rerun()
                                    else:
                                        st.error("Tên đăng nhập hoặc mật khẩu không chính xác.")
                
                # --- TAB ĐĂNG KÝ ---
                with tab_register:
                    with st.form("register_form_new", border=False):
                        new_username = st.text_input("Tên đăng nhập mới", placeholder="3-20 ký tự (a-z, 0-9, _)").strip()
                        new_password = st.text_input("Mật khẩu mới", type="password", placeholder="Tối thiểu 8 ký tự (chữ + số)")
                        confirm_password = st.text_input("Xác nhận mật khẩu", type="password", placeholder="Nhập lại mật khẩu")
                        btn_register = st.form_submit_button("Tạo tài khoản mới", type="primary", use_container_width=True)
                        
                        if btn_register:
                            is_valid_user, msg_user = validate_username(new_username)
                            is_valid_pass, msg_pass = validate_password(new_password)
                            
                            if not is_valid_user:
                                st.error(msg_user)
                            elif not is_valid_pass:
                                st.error(msg_pass)
                            elif new_password != confirm_password:
                                st.error("Mật khẩu xác nhận không trùng khớp!")
                            else:
                                existing = db.query(User).filter_by(username=new_username.lower()).first()
                                if existing:
                                    st.error("Tên đăng nhập này đã được sử dụng! Vui lòng chọn tên khác.")
                                else:
                                    try:
                                        hashed = hash_password(new_password)
                                        user_count = db.query(User).count()
                                        role_val = "admin" if user_count == 0 else "user"
                                        
                                        new_user = User(
                                            username=new_username.lower(),
                                            password_hash=hashed,
                                            role=role_val,
                                            is_active=True
                                        )
                                        db.add(new_user)
                                        db.commit()
                                        st.success("Tạo tài khoản thành công! Vui lòng chuyển sang tab Đăng nhập.")
                                    except Exception as ex:
                                        db.rollback()
                                        st.error(f"Lỗi hệ thống khi đăng ký: {ex}")
            finally:
                db.close()

            # Footer
            st.markdown(f"""
                <div class="auth-security-footer">
                    <span>Thiết bị: <b class="auth-badge">{device_info}</b></span>
                    <span>IP: <b class="auth-badge">{client_ip}</b></span>
                </div>
            """, unsafe_allow_html=True)

    st.stop()