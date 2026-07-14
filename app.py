# MIT License
# Copyright (c) 2026 Manes2008/didicrew

import streamlit as st
import os
import re
import config
from src.core.llm_provider import get_llm

st.set_page_config(page_title="AI Video Factory - Bé Tiểu Thư", layout="wide")
st.title("🎬 AI Video Factory - Bé Tiểu Thư (TikTok/Reel)")

# ==================== SIDEBAR CONFIGURATION ====================
with st.sidebar:
    st.header("Cấu hình AI Model")
    
    # 1. Chọn Nhà cung cấp LLM
    provider = st.selectbox(
        "Nhà cung cấp LLM",
        ["OpenAI", "Google Gemini"],
        index=0
    )
    
    # 2. Nhập API Key tương ứng
    if provider == "OpenAI":
        openai_key = st.text_input(
            "OpenAI API Key",
            type="password",
            value=st.session_state.get("openai_key", config.OPENAI_API_KEY or "")
        )
        if openai_key:
            st.session_state["openai_key"] = openai_key
            os.environ["OPENAI_API_KEY"] = openai_key
            
        model_options = ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"]
        model_name = st.selectbox("Chọn Model", model_options, index=0)
        
    else:
        gemini_key = st.text_input(
            "Gemini API Key",
            type="password",
            value=st.session_state.get("gemini_key", os.getenv("GEMINI_API_KEY", ""))
        )
        if gemini_key:
            st.session_state["gemini_key"] = gemini_key
            os.environ["GEMINI_API_KEY"] = gemini_key
            
        model_options = ["gemini-1.5-flash", "gemini-1.5-pro"]
        model_name = st.selectbox("Chọn Model", model_options, index=0)

# ==================== INPUT FIELD & VALIDATION ====================
idea = st.text_area(
    "Nhập ý tưởng video:",
    height=140, 
    placeholder="Ví dụ: Bé gái mặc váy hồng mới, cảm ơn mẹ mua đồ cho con"
)

if st.button("🚀 Bắt Đầu Quy Trình", type="primary"):
    # Xác thực dữ liệu đầu vào (Input Validation)
    errors = []
    
    # Kiểm tra API Key
    if provider == "OpenAI" and not st.session_state.get("openai_key"):
        errors.append("Vui lòng nhập OpenAI API Key!")
    elif provider == "Google Gemini" and not st.session_state.get("gemini_key"):
        errors.append("Vui lòng nhập Gemini API Key!")
        
    # Kiểm tra ý tưởng video
    if not idea.strip():
        errors.append("Vui lòng nhập ý tưởng video!")
    elif len(idea.strip()) < 5:
        errors.append("Ý tưởng video quá ngắn (tối thiểu 5 ký tự) để có kịch bản tốt.")
        
    if errors:
        for err in errors:
            st.error(err)
    else:
        st.session_state["idea"] = idea
        
        # Khởi tạo đối tượng Chat LLM tương ứng thông qua llm_provider
        api_key = st.session_state["openai_key"] if provider == "OpenAI" else st.session_state["gemini_key"]
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

# ==================== STAGES RUNNER ====================
stages = ["script", "visual", "image", "voice", "editor"]
stage_names = {
    "script": "📝 1. Viết Kịch Bản",
    "visual": "🎨 2. Tạo Prompt Hình Ảnh",
    "image": "🖼️ 3. Tạo Hình Ảnh",
    "voice": "🎤 4. Tạo Voiceover",
    "editor": "✂️ 5. Hướng Dẫn Edit Video"
}

if "stage" in st.session_state:
    current = st.session_state["stage"]
    st.subheader(stage_names[current])

    if st.button(f"▶️ Chạy {stage_names[current]}"):
        with st.spinner(f"Đang chạy {current}..."):
            from src.core.engine import run_stage
            
            # Lấy kết quả của stage trước đó làm ngữ cảnh
            prev = st.session_state["results"].get(
                list(st.session_state["results"].keys())[-1] 
                if st.session_state["results"] else None, 
                ""
            )
            
            result = run_stage(
                current,
                st.session_state["idea"],
                prev,
                st.session_state["llm"]
            )
            st.session_state["results"][current] = result
            st.rerun()

    # ==================== HIỂN THỊ KẾT QUẢ ====================
    if current in st.session_state.get("results", {}):
        result_text = st.session_state["results"][current]

        if current == "image":
            st.subheader("🖼️ Hình ảnh đã tạo")
            image_path = None

            # Phân tách kết quả để tìm đường dẫn lưu ảnh cục bộ
            for line in result_text.split("\n"):
                if "generated_images" in line:
                    # Trích xuất đường dẫn ảnh sạch
                    clean_line = line.replace("📁 Đường dẫn ảnh:", "").replace("📁 Đường dẫn ảnh: ", "").strip()
                    image_path = clean_line
                    break

            # Hiển thị ảnh nếu đường dẫn tồn tại
            if image_path and os.path.exists(image_path):
                st.image(image_path, caption=f"Ảnh lưu tại: {image_path}", width="stretch")
                st.success(f"✅ Đã tải ảnh cục bộ thành công: {image_path}")
            else:
                st.warning("Không tìm thấy đường dẫn ảnh cục bộ hợp lệ trong phản hồi. Nội dung gốc:")
                st.text(result_text)
        else:
            st.text_area("Kết quả:", value=result_text, height=350)

        # Nút điều khiển chuyển tiếp / quay lại
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("✅ Approve & Tiếp tục"):
                idx = stages.index(current)
                if idx < len(stages) - 1:
                    st.session_state["stage"] = stages[idx + 1]
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
                    st.session_state["stage"] = stages[idx - 1]
                st.rerun()

# ==================== TIẾN TRÌNH SIDEBAR/FOOTER ====================
if "results" in st.session_state and st.session_state["results"]:
    st.divider()
    st.subheader("Tiến trình thực hiện")
    for s in stages:
        status = "✅" if s in st.session_state["results"] else "⏳"
        st.write(f"{status} {stage_names[s]}")