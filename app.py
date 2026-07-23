# MIT License
# Copyright (c) 2026 Manes2008/didicrew

import streamlit as st
import os
import re
import datetime
import hashlib
import binascii
import config
from src.core.llm_provider import get_llm
from src.core.models import init_db, get_db_session, Channel, Project, ProjectStage, MediaFile, AllowedIP, User

st.set_page_config(page_title="VideoCrew Studio - AI Video Production Platform", layout="wide")
st.title("VideoCrew Studio - AI Video Production Platform")

# Khoi tao database
try:
    init_db()
except Exception as e:
    st.error(f"Khong the ket noi hoac khoi tao Database: {e}")
    st.stop()

# ==================== PASSWORD HASHING ====================
def hash_password(password: str) -> str:
    """Bam mat khau bang PBKDF2-SHA256 voi salt ngau nhien."""
    salt = os.urandom(16)
    db_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return binascii.hexlify(salt).decode('utf-8') + ":" + binascii.hexlify(db_hash).decode('utf-8')


def verify_password(password: str, stored_hash: str) -> bool:
    """Xac thuc mat khau voi salt da luu."""
    try:
        salt_hex, hash_hex = stored_hash.split(":")
        salt = binascii.unhexlify(salt_hex)
        stored_db_hash = binascii.unhexlify(hash_hex)
        test_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
        return test_hash == stored_db_hash
    except Exception:
        return False


# ==================== IP AUTHENTICATION GATE ====================
def get_client_ip() -> str:
    """Lay IP that cua client tu headers proxy hoac fallback."""
    headers = st.context.headers
    for header in ["X-Forwarded-For", "X-Real-Ip", "CF-Connecting-IP", "True-Client-Ip"]:
        ip_val = headers.get(header)
        if ip_val:
            return ip_val.split(",")[0].strip()
    return "127.0.0.1"


def show_login_register_gate(client_ip: str):
    """Hiển thị form đăng nhập / đăng ký."""
    st.set_page_config(page_title="Xác thực | VideoCrew Studio", layout="centered")
    st.markdown("<h2 style='text-align: center;'>🛡️ Cổng Xác Thực VideoCrew Studio</h2>", unsafe_allow_html=True)
    st.info(f"Thiết bị hiện tại (IP: {client_ip}) chưa được phê duyệt. Vui lòng đăng nhập để tiếp tục.")

    auth_mode = st.radio("Chọn hành động", ["Đăng nhập", "Đăng ký tài khoản"], horizontal=True)

    db = get_db_session()
    try:
        if auth_mode == "Đăng nhập":
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
                                # Auto approve IP thiet bi cho user
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
                                st.success("Đăng nhập thành công! Vui lòng đợi...")
                                st.rerun()
                        else:
                            st.error("Tên đăng nhập hoặc mật khẩu không chính xác.")

        else: # Dang ky
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

                            # Auto approve IP luon
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


# Kiem tra IP truoc khi render bat ky noi dung nao
_client_ip = get_client_ip()

_db_check = get_db_session()
try:
    _ip_record = _db_check.query(AllowedIP).filter_by(ip_address=_client_ip).first()
    if _ip_record and _ip_record.status == "approved":
        if _ip_record.user_id:
            _user = _db_check.query(User).filter_by(id=_ip_record.user_id).first()
            if _user:
                if not _user.is_active:
                    st.set_page_config(page_title="Tài khoản bị khóa", layout="centered")
                    st.error("Tài khoản của bạn đã bị khóa! Vui lòng liên hệ quản trị viên.")
                    st.stop()

                st.session_state["current_user"] = {
                    "id": _user.id,
                    "username": _user.username,
                    "role": _user.role
                }
            else:
                st.session_state["current_user"] = {
                    "id": None,
                    "username": f"Guest ({_client_ip})",
                    "role": "user"
                }
        else:
            st.session_state["current_user"] = {
                "id": None,
                "username": f"Guest ({_client_ip})",
                "role": "user"
            }
finally:
    _db_check.close()

if _ip_record is None or _ip_record.status != "approved":
    show_login_register_gate(_client_ip)



# ==================== SIDEBAR CONFIGURATION ====================
with st.sidebar:
    if "current_user" in st.session_state:
        u_info = st.session_state["current_user"]
        with st.container(border=True):
            st.markdown(f"👤 **Tài khoản**: `{u_info['username']}`")
            st.markdown(f"🔑 **Vai trò**: `{u_info['role'].upper()}`")
            st.markdown(f"🌐 **IP**: `{_client_ip}`")
        st.divider()


    st.header("Cấu hình AI Model")

    
    # 1. Chọn Nhà cung cấp LLM
    provider = st.selectbox(
        "Nhà cung cấp LLM",
        ["OpenAI", "Google Gemini"],
        index=0
    )
    
    # 2. Chọn Model (API Key được ẩn và tự động tải từ môi trường)
    if provider == "OpenAI":
        model_options = ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"]
        model_name = st.selectbox("Chọn Model", model_options, index=0)
        api_key = config.OPENAI_API_KEY
    else:
        model_options = ["gemini-1.5-flash", "gemini-1.5-pro"]
        model_name = st.selectbox("Chọn Model", model_options, index=0)
        api_key = config.GEMINI_API_KEY

    st.divider()
    st.header("Cấu hình Video Engine")
    video_engine_option = st.selectbox(
        "Engine sinh Video",
        ["Wan 2.1 Local", "Pollo AI (Cloud API)"],
        index=0
    )
    st.session_state["video_engine"] = "wan2.1_local" if video_engine_option == "Wan 2.1 Local" else "pollo_api"

    st.divider()
    st.header("Quản lý Kênh & Dự án")
    
    db = get_db_session()
    
    # Đảm bảo có ít nhất 1 kênh mặc định
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
    channel_options = channel_names + ["-- Tạo kênh mới --"]
    
    # Quản lý kênh hiện tại bằng session_state
    if "selected_channel_name" not in st.session_state or st.session_state["selected_channel_name"] not in channel_options:
        st.session_state["selected_channel_name"] = channel_names[0]
        
    # Lấy index của kênh hiện tại trong danh sách options
    try:
        current_index = channel_options.index(st.session_state["selected_channel_name"])
    except ValueError:
        current_index = 0
        
    selected_channel_opt = st.selectbox("Chọn Kênh", channel_options, index=current_index)
    st.session_state["selected_channel_name"] = selected_channel_opt
    
    if selected_channel_opt == "-- Tạo kênh mới --":
        st.markdown("### 🆕 Tạo Kênh Mới")
        with st.form("create_channel_form"):
            new_name = st.text_input("Tên kênh", placeholder="Vd: Kênh Công Nghệ")
            new_desc = st.text_input("Mô tả kênh (tùy chọn)", placeholder="Mô tả ngắn về kênh...")
            new_goal = st.text_area("Mục tiêu của kênh", value="Tạo video Reels/TikTok thu hút người xem")
            
            btn_create_channel = st.form_submit_button("Lưu Kênh Mới", use_container_width=True, type="primary")
            
            if btn_create_channel:
                if not new_name.strip():
                    st.error("Tên kênh không được để trống")
                elif not new_goal.strip():
                    st.error("Mục tiêu của kênh không được để trống")
                else:
                    # Kiểm tra trùng tên
                    dup = db.query(Channel).filter_by(name=new_name.strip()).first()
                    if dup:
                        st.error("Tên kênh này đã tồn tại! Vui lòng chọn tên khác.")
                    else:
                        try:
                            new_chan = Channel(
                                name=new_name.strip(),
                                description=new_desc.strip() if new_desc else None,
                                goal=new_goal.strip()
                            )
                            db.add(new_chan)
                            db.commit()
                            st.success(f"Đã tạo kênh '{new_name.strip()}' thành công!")
                            st.session_state["selected_channel_name"] = new_name.strip()
                            st.rerun()
                        except Exception as ex:
                            db.rollback()
                            st.error(f"Lỗi: {ex}")
        st.stop()
        
    selected_channel = next(c for c in channels if c.name == selected_channel_opt)

    
    # Lấy danh sách dự án trong kênh
    projects = db.query(Project).filter_by(channel_id=selected_channel.id).order_by(Project.id.desc()).all()
    project_options = ["-- Tạo dự án mới --"] + [f"#{p.id} - {p.idea[:30]}..." for p in projects]
    selected_project_opt = st.selectbox("Chọn dự án", project_options)
    
    selected_project = None
    if selected_project_opt != "-- Tạo dự án mới --":
        project_id = int(selected_project_opt.split(" - ")[0].replace("#", ""))
        selected_project = db.query(Project).filter_by(id=project_id).first()
        
        # Đồng bộ trạng thái từ DB sang session_state
        # Chi sync khi project thay doi (project_id moi != project_id cu)
        # Tranh ghi de stage khi user dang navigate qua thanh tien trinh
        if selected_project:
            prev_project_id = st.session_state.get("project_id")
            project_changed = prev_project_id != selected_project.id

            st.session_state["project_id"] = selected_project.id
            st.session_state["idea"] = selected_project.idea

            if project_changed:
                # Chi reset stage va results khi doi sang du an khac
                st.session_state["stage"] = selected_project.current_stage
                st.session_state["results"] = {}
                for stage_rec in selected_project.stages:
                    if stage_rec.result_content:
                        st.session_state["results"][stage_rec.stage_name] = stage_rec.result_content
            else:
                # Cung du an: dam bao results luon day du (khong reset stage)
                if "results" not in st.session_state:
                    st.session_state["results"] = {}
                for stage_rec in selected_project.stages:
                    if stage_rec.result_content and stage_rec.stage_name not in st.session_state["results"]:
                        st.session_state["results"][stage_rec.stage_name] = stage_rec.result_content

# ==================== INPUT FIELD & VALIDATION ====================
# Nếu đang chọn dự án cũ, hiển thị ý tưởng của dự án cũ (disable sửa đổi)
is_new = selected_project is None
idea_val = st.session_state.get("idea", "") if not is_new else ""

idea = st.text_area(
    "Nhập ý tưởng video:",
    height=140, 
    value=idea_val if not is_new else "",
    disabled=not is_new,
    placeholder="Ví dụ: Bé gái mặc váy hồng mới, cảm ơn mẹ mua đồ cho con"
)

if is_new:
    if st.button("Bắt Đầu Quy Trình", type="primary"):
        errors = []
        
        # Kiểm tra API Key có tồn tại trong cấu hình không
        if provider == "OpenAI" and not api_key:
            errors.append("Không tìm thấy OpenAI API Key trong cấu hình môi trường (.env)!")
        elif provider == "Google Gemini" and not api_key:
            errors.append("Không tìm thấy Gemini API Key trong cấu hình môi trường (.env)!")
            
        # Kiểm tra ý tưởng video
        if not idea.strip():
            errors.append("Vui lòng nhập ý tưởng video!")
        elif len(idea.strip()) < 5:
            errors.append("Ý tưởng video quá ngắn (tối thiểu 5 ký tự) để có kịch bản tốt.")
            
        if errors:
            for err in errors:
                st.error(err)
        else:
            db = get_db_session()
            try:
                new_proj = Project(
                    channel_id=selected_channel.id,
                    idea=idea,
                    provider=provider,
                    model_name=model_name,
                    current_stage="script",
                    status="pending"
                )
                db.add(new_proj)
                db.commit()
                st.session_state["project_id"] = new_proj.id
            except Exception as ex:
                st.error(f"Lỗi khi lưu Project vào DB: {ex}")
                db.rollback()
                st.stop()
                
            st.session_state["idea"] = idea
            st.session_state["llm"] = get_llm(
                provider=provider,
                model_name=model_name,
                api_key=api_key,
                temperature=0.75
            )
                
            st.session_state["stage"] = "script"
            st.session_state["results"] = {}
            st.success(f"Đã khởi tạo quy trình thành công với model {model_name}!")
            st.rerun()
else:
    # Nếu chọn dự án cũ và chưa khởi tạo LLM trong session_state
    if "llm" not in st.session_state:
        st.session_state["llm"] = get_llm(
            provider=selected_project.provider,
            model_name=selected_project.model_name,
            api_key=config.OPENAI_API_KEY if selected_project.provider == "OpenAI" else config.GEMINI_API_KEY,
            temperature=0.75
        )

# ==================== STAGES RUNNER ====================
stages = ["script", "visual", "image", "voice", "video"]
stage_names = {
    "script": "1. Viết Kịch Bản",
    "visual": "2. Tạo Prompt Hình Ảnh",
    "image": "3. Tạo Hình Ảnh",
    "voice": "4. Tạo Voiceover",
    "video": "5. Tạo Video AI"
}

if "stage" in st.session_state:
    current = st.session_state["stage"]
    completed = set(st.session_state.get("results", {}).keys())

    # ==================== STEP NAVIGATOR ====================
    st.markdown("""
    <style>
    div[data-testid="column"] > div > div > div > button {
        width: 100%;
        border-radius: 8px;
        font-weight: 600;
        font-size: 0.82rem;
        padding: 0.4rem 0.2rem;
        border: none;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    </style>
    """, unsafe_allow_html=True)

    nav_cols = st.columns(5)
    step_labels = {
        "script": "1\nViết Kịch Bản",
        "visual": "2\nPrompt Hình Ảnh",
        "image":  "3\nTạo Hình Ảnh",
        "voice":  "4\nVoiceover",
        "video":  "5\nVideo AI",
    }

    for col, stage_key in zip(nav_cols, stages):
        with col:
            is_done    = stage_key in completed
            is_current = stage_key == current
            label      = step_labels[stage_key]

            if is_current:
                icon = "▶"
                btn_type = "primary"
                disabled = False
                help_text = "Đang ở bước này"
            elif is_done:
                icon = "✅"
                btn_type = "secondary"
                disabled = False
                help_text = "Đã hoàn thành — Click để xem lại / chỉnh sửa"
            else:
                icon = "⏳"
                btn_type = "secondary"
                disabled = True
                prev_idx = stages.index(stage_key) - 1
                prev_name = stage_names[stages[prev_idx]].split(". ", 1)[-1] if prev_idx >= 0 else ""
                help_text = f"Chưa mở khóa — Cần hoàn thành '{prev_name}' trước"

            display = f"{icon} {label}"
            if st.button(display, key=f"nav_{stage_key}", type=btn_type, disabled=disabled,
                         help=help_text, use_container_width=True):
                st.session_state["stage"] = stage_key
                st.rerun()

    st.divider()
    # =========================================================

    st.subheader(stage_names[current])

    if st.button(f"▶️ Chạy {stage_names[current]}"):
        with st.spinner(f"Đang chạy {current}..."):
            if "llm" not in st.session_state:
                st.error("Phiên làm việc đã hết hạn. Vui lòng chọn lại dự án ở sidebar để khởi tạo lại LLM.")
                st.stop()
            from src.core.engine import run_stage
            
            # Lấy kết quả của stage trước đó làm ngữ cảnh
            current_idx = stages.index(current)
            prev_stage = stages[current_idx - 1] if current_idx > 0 else None
            prev = st.session_state["results"].get(prev_stage, "") if prev_stage else ""
            
            # Tạo context động từ thông tin kênh và video engine
            context = {
                "channel_name": selected_channel.name,
                "channel_description": selected_channel.description,
                "channel_goal": selected_channel.goal,
                "video_engine": st.session_state.get("video_engine", "wan2.1_local")
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
            
            # DB: Cập nhật hoặc lưu kết quả stage vào database
            db = get_db_session()
            project_id = st.session_state.get("project_id")
            if project_id:
                try:
                    stage_rec = db.query(ProjectStage).filter_by(project_id=project_id, stage_name=current).first()
                    if not stage_rec:
                        stage_rec = ProjectStage(
                            project_id=project_id,
                            stage_name=current,
                            result_content=result,
                            status="completed"
                        )
                        db.add(stage_rec)
                        db.flush() # Để có stage_rec.id cho liên kết khóa ngoại của MediaFile
                    else:
                        stage_rec.result_content = result
                        stage_rec.status = "completed"
                        db.flush()
                    
                    # Nếu là stage 'image', lưu file media vào media_files
                    if current == "image":
                        image_path = None
                        for line in result.split("\n"):
                            if "generated_images" in line:
                                clean_line = line.replace("📁 Đường dẫn ảnh:", "").replace("📁 Đường dẫn ảnh: ", "").strip()
                                image_path = clean_line
                                break
                        if image_path:
                            stage_rec.media_path = image_path
                            media_file = MediaFile(
                                project_stage_id=stage_rec.id,
                                file_name=os.path.basename(image_path),
                                file_path=image_path,
                                mime_type="image/png",
                                status="active"
                            )
                            db.add(media_file)
                            
                    # Nếu là stage 'video', lưu file media vào media_files
                    if current == "video":
                        video_path = None
                        for line in result.split("\n"):
                            if "generated_videos" in line or ".mp4" in line:
                                clean_line = line.replace("📁 Đường dẫn video:", "").replace("📁 Đường dẫn video: ", "").replace("Duong dan video:", "").replace("Duong dan video: ", "").strip()
                                video_path = clean_line
                                break
                        if video_path:
                            stage_rec.media_path = video_path
                            media_file = MediaFile(
                                project_stage_id=stage_rec.id,
                                file_name=os.path.basename(video_path),
                                file_path=video_path,
                                mime_type="video/mp4",
                                status="active"
                            )
                            db.add(media_file)
                    
                    # Cập nhật thông tin dự án
                    proj_rec = db.query(Project).filter_by(id=project_id).first()
                    if proj_rec:
                        proj_rec.current_stage = current
                        proj_rec.status = "running"
                        
                    db.commit()
                except Exception as ex:
                    st.error(f"Lỗi DB khi lưu kết quả stage: {ex}")
                    db.rollback()
            st.rerun()

    # ==================== HIỂN THỊ KẾT QUẢ ====================
    if current in st.session_state.get("results", {}):
        result_text = st.session_state["results"][current]

        if current == "image":
            st.subheader("🖼️ Hình ảnh đã tạo")
            image_path = None

            for line in result_text.split("\n"):
                if "generated_images" in line:
                    clean_line = line.replace("📁 Đường dẫn ảnh:", "").replace("📁 Đường dẫn ảnh: ", "").strip()
                    image_path = clean_line
                    break

            if image_path and os.path.exists(image_path):
                st.image(image_path, caption=f"Ảnh lưu tại: {image_path}")
                st.success(f"✅ Đã tải ảnh cục bộ thành công: {image_path}")
            else:
                st.warning("Không tìm thấy đường dẫn ảnh cục bộ hợp lệ trong phản hồi. Nội dung gốc:")
                st.text(result_text)
                
        elif current == "video":
            st.subheader("🎬 Video AI đã tạo")
            video_path = None

            for line in result_text.split("\n"):
                if "generated_videos" in line or ".mp4" in line:
                    clean_line = line.replace("📁 Đường dẫn video:", "").replace("📁 Đường dẫn video: ", "").replace("Duong dan video:", "").replace("Duong dan video: ", "").strip()
                    video_path = clean_line
                    break

            if video_path and os.path.exists(video_path):
                st.video(video_path)
                st.success(f"✅ Đã tải video cục bộ thành công: {video_path}")
            else:
                if "ERROR" in result_text:
                    st.error(result_text)
                else:
                    st.warning("Không tìm thấy đường dẫn video cục bộ hợp lệ trong phản hồi. Nội dung gốc:")
                    st.text(result_text)
        else:
            with st.container(border=True):
                st.markdown(result_text)
            with st.expander("Xem raw text / Copy"):
                st.code(result_text, language="markdown")

        # Nút điều khiển chuyển tiếp / quay lại
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("✅ Approve & Tiếp tục"):
                idx = stages.index(current)
                if idx < len(stages) - 1:
                    next_stage = stages[idx + 1]
                    st.session_state["stage"] = next_stage
                    db = get_db_session()
                    project_id = st.session_state.get("project_id")
                    if project_id:
                        proj_rec = db.query(Project).filter_by(id=project_id).first()
                        if proj_rec:
                            proj_rec.current_stage = next_stage
                            db.commit()
                else:
                    db = get_db_session()
                    project_id = st.session_state.get("project_id")
                    if project_id:
                        proj_rec = db.query(Project).filter_by(id=project_id).first()
                        if proj_rec:
                            proj_rec.status = "completed"
                            db.commit()
                    st.balloons()
                st.rerun()
        with col2:
            if st.button("🔄 Regenerate"):
                if current in st.session_state["results"]:
                    del st.session_state["results"][current]
                st.rerun()
        with col3:
            if st.button("⏮️ Quay lại"):
                idx = stages.index(current)
                if idx > 0:
                    prev_stage = stages[idx - 1]
                    st.session_state["stage"] = prev_stage
                    db = get_db_session()
                    project_id = st.session_state.get("project_id")
                    if project_id:
                        proj_rec = db.query(Project).filter_by(id=project_id).first()
                        if proj_rec:
                            proj_rec.current_stage = prev_stage
                            db.commit()
                st.rerun()

# ==================== TIEN TRINH SIDEBAR/FOOTER ====================
if "results" in st.session_state and st.session_state["results"]:
    st.divider()
    st.subheader("Tien trinh thuc hien")
    for s in stages:
        status = "OK" if s in st.session_state["results"] else "..."
        st.write(f"{status} {stage_names[s]}")

# ==================== ADMIN PANEL LINK & LOGOUT (SIDEBAR) ====================
with st.sidebar:
    st.divider()
    if "current_user" in st.session_state and st.session_state["current_user"]["role"] == "admin":
        st.page_link("pages/Admin_IP_Manager.py", label="Quan ly IP Thiet bi (Admin)", icon=":material/shield:")
        st.divider()
    
    if st.button("Đăng xuất 🔓", type="secondary", use_container_width=True):
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


