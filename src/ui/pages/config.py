import streamlit as st
import os

def render_config_page():
    st.markdown('<div class="vc-eyebrow"><i class="bi bi-sliders"></i> Cấu hình hệ thống</div>', unsafe_allow_html=True)
    st.subheader("Cấu hình API Keys & AI Models", anchor=False)

    # 1. Quản lý API Keys
    st.markdown('<div class="vc-eyebrow" style="margin-top:1rem;"><i class="bi bi-key"></i> Quản lý API Keys</div>', unsafe_allow_html=True)
    with st.container(border=True):
        # Lấy keys hiện tại từ session state hoặc env
        current_openai = st.session_state.get("custom_openai_key") or os.getenv("OPENAI_API_KEY", "")
        current_gemini = st.session_state.get("custom_gemini_key") or os.getenv("GEMINI_API_KEY", "")
        
        # Mask keys
        def mask_key(k):
            if not k: return ""
            if len(k) > 12: return f"{k[:6]}...{k[-6:]}"
            return "******"

        st.info("API Key được nhập tại đây sẽ được lưu tạm thời cho phiên làm việc hiện tại và ghi đè cấu hình cũ.")
        
        openai_key_input = st.text_input(
            f"OpenAI API Key (Hiện tại: {mask_key(current_openai)})", 
            type="password", 
            placeholder="sk-proj-...",
            key="cfg_openai_key"
        )
        gemini_key_input = st.text_input(
            f"Gemini API Key (Hiện tại: {mask_key(current_gemini)})", 
            type="password", 
            placeholder="AIzaSy...",
            key="cfg_gemini_key"
        )

        if st.button("Lưu API Keys", type="primary"):
            if openai_key_input.strip():
                st.session_state["custom_openai_key"] = openai_key_input.strip()
                os.environ["OPENAI_API_KEY"] = openai_key_input.strip()
            if gemini_key_input.strip():
                st.session_state["custom_gemini_key"] = gemini_key_input.strip()
                os.environ["GEMINI_API_KEY"] = gemini_key_input.strip()
            st.success("Đã cập nhật API Keys thành công!")
            st.rerun()

    # 2. Cấu hình AI Model & Engines
    st.markdown('<div class="vc-eyebrow" style="margin-top:1.5rem;"><i class="bi bi-cpu"></i> Chọn AI Model & Render Engines</div>', unsafe_allow_html=True)
    with st.container(border=True):
        col1, col2 = st.columns(2)
        
        with col1:
            provider = st.selectbox(
                "LLM Provider", 
                ["OpenAI", "Google Gemini"], 
                index=0 if st.session_state.get("provider", "OpenAI") == "OpenAI" else 1,
                key="select_provider_page"
            )
            st.session_state["provider"] = provider

            if provider == "OpenAI":
                model_options = ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"]
                current_model = st.session_state.get("model_name", "gpt-4o-mini")
                model_index = model_options.index(current_model) if current_model in model_options else 0
                model_name = st.selectbox("Model", model_options, index=model_index, key="select_model_page")
            else:
                model_options = ["gemini-1.5-flash", "gemini-1.5-pro"]
                current_model = st.session_state.get("model_name", "gemini-1.5-flash")
                model_index = model_options.index(current_model) if current_model in model_options else 0
                model_name = st.selectbox("Model", model_options, index=model_index, key="select_model_page")
            
            st.session_state["model_name"] = model_name

        with col2:
            current_video_engine = st.session_state.get("video_engine", "wan2.1_local")
            video_options = ["Wan 2.1 Local", "Pollo AI (Cloud API)"]
            video_index = 0 if current_video_engine == "wan2.1_local" else 1
            video_engine_option = st.selectbox("Engine Sinh Video", video_options, index=video_index, key="select_video_page")
            st.session_state["video_engine"] = "wan2.1_local" if video_engine_option == "Wan 2.1 Local" else "pollo_api"

            current_image_engine = st.session_state.get("image_engine", "openai")
            image_options = ["OpenAI DALL-E", "Stable Diffusion v1.5 (CPU)", "Mark-L Local (GPU)"]
            engine_map = {
                "openai": 0,
                "sd1.5_local": 1,
                "markl_local": 2
            }
            image_index = engine_map.get(current_image_engine, 0)
            image_engine_option = st.selectbox("Engine Sinh Ảnh", image_options, index=image_index, key="select_image_page")
            
            reverse_map = {
                "OpenAI DALL-E": "openai",
                "Stable Diffusion v1.5 (CPU)": "sd1.5_local",
                "Mark-L Local (GPU)": "markl_local"
            }
            st.session_state["image_engine"] = reverse_map[image_engine_option]

        if st.button("Lưu Cấu Hình Model", use_container_width=True):
            st.success("Đã lưu cấu hình AI Model thành công!")
            st.rerun()
