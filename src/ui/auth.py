import streamlit as st
import os
import hashlib
import binascii
import datetime
from src.core.models import get_db_session, User, AllowedIP

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

# ==================== LẤY IP TRUY CẬP ====================
def get_client_ip() -> str:
    headers = st.context.headers
    for header in ["X-Forwarded-For", "X-Real-Ip", "CF-Connecting-IP", "True-Client-Ip"]:
        ip_val = headers.get(header)
        if ip_val:
            return ip_val.split(",")[0].strip()
    return "127.0.0.1"

def render_login_page():
    # 1. Kiểm tra nếu đã đăng nhập thành công
    if st.session_state.get("logged_in", False):
        return True

    client_ip = get_client_ip()

    # 2. UI Banner Tiêu đề
    st.markdown("""
    <div class="vc-login-card">
        <div style="text-align: center; margin-bottom: 2rem;">
            <div class="vc-logo-mark" style="width: 50px; height: 50px; margin: 0 auto 0.75rem auto; display: flex; align-items: center; justify-content: center;">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" viewBox="0 0 16 16">
                    <path d="M6 3a3 3 0 1 1-6 0 3 3 0 0 1 6 0zM9 6a3 3 0 1 1 0-6 3 3 0 0 1 0 6zM9 1.15a2.238 2.238 0 1 0 0 4.475A2.238 2.238 0 0 0 9 1.15zM5 2.15a2.238 2.238 0 1 0 0 4.475A2.238 2.238 0 0 0 5 2.15z"/>
                    <path d="M14 3a1 1 0 0 1 1 1v8a1 1 0 0 1-1 1H2a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1h12zM2 2a2 2 0 0 0-2 2v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2H2z"/>
                </svg>
            </div>
            <h2 style="font-weight: 800; background: linear-gradient(90deg, #C2542D, #C99A45); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin:0;">
                VideoCrew Studio
            </h2>
            <p style="color: #808495; font-size: 0.85rem; margin-top: 0.25rem;">
                Hệ thống sản xuất video tự động đa kênh
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    admin_key_env = os.getenv("ADMIN_SECRET_KEY", "xR4q90gPLDGvU-VHra08adaK1BIqroR9qQ7l8boDNGw")
    db = get_db_session()

    try:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            tab_login, tab_register = st.tabs(["🔑 Đăng nhập", "📝 Đăng ký tài khoản"])
            
            # --- TAB ĐĂNG NHẬP ---
            with tab_login:
                with st.form("login_form_new"):
                    username = st.text_input("Tên đăng nhập")
                    password = st.text_input("Mật khẩu", type="password")
                    btn_login = st.form_submit_button("Đăng nhập", type="primary", use_container_width=True)
                    
                    if btn_login:
                        if not username.strip() or not password:
                            st.error("Vui lòng nhập đầy đủ tên đăng nhập và mật khẩu!")
                        else:
                            # TH1: Đăng nhập quyền Admin bằng cách điền ADMIN_SECRET_KEY vào ô Password
                            if password == admin_key_env:
                                # Tự động tạo nhãn dạng Didicrew01, Didicrew02... bảo mật
                                existing_ip = db.query(AllowedIP).filter_by(ip_address=client_ip).first()
                                if existing_ip and existing_ip.label and existing_ip.label.startswith("Didicrew"):
                                    admin_display_name = existing_ip.label.split(":")[0].strip()
                                else:
                                    admin_ip_count = db.query(AllowedIP).filter(AllowedIP.label.like("Didicrew%")).count()
                                    admin_display_name = f"Didicrew{admin_ip_count + 1:02d}"

                                st.session_state["logged_in"] = True
                                st.session_state["user_role"] = "ADMIN"
                                st.session_state["user_name"] = admin_display_name
                                
                                # Tự động duyệt IP cho Admin truy cập
                                if existing_ip:
                                    existing_ip.status = "approved"
                                    existing_ip.label = f"{admin_display_name}: Admin"
                                    existing_ip.approved_at = datetime.datetime.utcnow()
                                else:
                                    db.add(AllowedIP(
                                        ip_address=client_ip,
                                        label=f"{admin_display_name}: Admin",
                                        status="approved",
                                        approved_at=datetime.datetime.utcnow()
                                    ))
                                db.commit()
                                st.success("Đăng nhập vai trò Admin thành công!")
                                st.rerun()
                                
                            # TH2: Đăng nhập User thông thường qua DB
                            else:
                                user = db.query(User).filter_by(username=username.strip().lower()).first()
                                if user and verify_password(password, user.password_hash):
                                    if not user.is_active:
                                        st.error("Tài khoản của bạn đã bị khóa! Vui lòng liên hệ Admin.")
                                    else:
                                        st.session_state["logged_in"] = True
                                        st.session_state["user_role"] = user.role.upper()
                                        st.session_state["user_name"] = user.username
                                        
                                        # Tự động duyệt IP
                                        existing_ip = db.query(AllowedIP).filter_by(ip_address=client_ip).first()
                                        if existing_ip:
                                            existing_ip.status = "approved"
                                            existing_ip.user_id = user.id
                                            existing_ip.approved_at = datetime.datetime.utcnow()
                                        else:
                                            db.add(AllowedIP(
                                                ip_address=client_ip,
                                                label=f"User: {user.username}",
                                                status="approved",
                                                user_id=user.id,
                                                approved_at=datetime.datetime.utcnow()
                                            ))
                                        db.commit()
                                        st.success(f"Đăng nhập thành công! Chào mừng {user.username}")
                                        st.rerun()
                                else:
                                    st.error("Tên đăng nhập hoặc mật khẩu không chính xác.")
            
            # --- TAB ĐĂNG KÝ ---
            with tab_register:
                with st.form("register_form_new"):
                    new_username = st.text_input("Tên đăng nhập mới")
                    new_password = st.text_input("Mật khẩu mới", type="password")
                    confirm_password = st.text_input("Xác nhận mật khẩu", type="password")
                    btn_register = st.form_submit_button("Đăng ký tài khoản", type="primary", use_container_width=True)
                    
                    if btn_register:
                        if not new_username.strip() or not new_password or not confirm_password:
                            st.error("Vui lòng nhập đầy đủ thông tin đăng ký!")
                        elif len(new_username.strip()) < 3:
                            st.error("Tên đăng nhập tối thiểu 3 ký tự!")
                        elif len(new_password) < 6:
                            st.error("Mật khẩu tối thiểu 6 ký tự!")
                        elif new_password != confirm_password:
                            st.error("Mật khẩu xác nhận không khớp!")
                        else:
                            existing = db.query(User).filter_by(username=new_username.strip().lower()).first()
                            if existing:
                                st.error("Tên đăng nhập này đã được sử dụng!")
                            else:
                                try:
                                    # Tạo user mới với vai trò user mặc định
                                    hashed = hash_password(new_password)
                                    user_count = db.query(User).count()
                                    role_val = "admin" if user_count == 0 else "user"
                                    
                                    new_user = User(
                                        username=new_username.strip().lower(),
                                        password_hash=hashed,
                                        role=role_val,
                                        is_active=True
                                    )
                                    db.add(new_user)
                                    db.commit()
                                    
                                    st.success("Đăng ký tài khoản thành công! Vui lòng chuyển sang tab Đăng nhập.")
                                except Exception as ex:
                                    db.rollback()
                                    st.error(f"Lỗi hệ thống khi đăng ký: {ex}")
    finally:
        db.close()

    st.stop()
