# MIT License
# Copyright (c) 2026 Manes2008/didicrew

import streamlit as st
import os
import re
import config
from src.core.llm_provider import get_llm
from src.core.models import init_db, get_db_session, Channel, Project, ProjectStage, MediaFile

st.set_page_config(page_title="VideoCrew Studio - AI Video Production Platform", layout="wide")
st.title("VideoCrew Studio - AI Video Production Platform")

# Khởi tạo database
try:
    init_db()
except Exception as e:
    st.error(f"Không thể kết nối hoặc khởi tạo Database: {e}")

# ==================== SIDEBAR CONFIGURATION ====================
with st.sidebar:
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
    selected_channel_name = st.selectbox("Chọn Kênh", channel_names)
    selected_channel = next(c for c in channels if c.name == selected_channel_name)
    
    # Lấy danh sách dự án trong kênh
    projects = db.query(Project).filter_by(channel_id=selected_channel.id).order_by(Project.id.desc()).all()
    project_options = ["-- Tạo dự án mới --"] + [f"#{p.id} - {p.idea[:30]}..." for p in projects]
    selected_project_opt = st.selectbox("Chọn dự án", project_options)
    
    selected_project = None
    if selected_project_opt != "-- Tạo dự án mới --":
        project_id = int(selected_project_opt.split(" - ")[0].replace("#", ""))
        selected_project = db.query(Project).filter_by(id=project_id).first()
        
        # Đồng bộ trạng thái từ DB sang session_state
        if selected_project:
            st.session_state["project_id"] = selected_project.id
            st.session_state["idea"] = selected_project.idea
            st.session_state["stage"] = selected_project.current_stage
            
            # Load các kết quả stage đã chạy
            st.session_state["results"] = {}
            for stage_rec in selected_project.stages:
                if stage_rec.result_content:
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
    st.subheader(stage_names[current])

    if st.button(f"▶️ Chạy {stage_names[current]}"):
        with st.spinner(f"Đang chạy {current}..."):
            from src.core.engine import run_stage
            
            # Lấy kết quả của stage trước đó làm ngữ cảnh
            prev = st.session_state["results"].get(
                stages[stages.index(current) - 1] if stages.index(current) > 0 else None,
                ""
            )
            
            # Tạo context động từ thông tin kênh
            context = {
                "channel_name": selected_channel.name,
                "channel_description": selected_channel.description,
                "channel_goal": selected_channel.goal
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
                            if "generated_videos" in line:
                                clean_line = line.replace("📁 Đường dẫn video:", "").replace("📁 Đường dẫn video: ", "").strip()
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
                if "generated_videos" in line:
                    clean_line = line.replace("📁 Đường dẫn video:", "").replace("📁 Đường dẫn video: ", "").strip()
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
            st.text_area("Kết quả:", value=result_text, height=350)

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

# ==================== TIẾN TRÌNH SIDEBAR/FOOTER ====================
if "results" in st.session_state and st.session_state["results"]:
    st.divider()
    st.subheader("Tiến trình thực hiện")
    for s in stages:
        status = "✅" if s in st.session_state["results"] else "⏳"
        st.write(f"{status} {stage_names[s]}")