import streamlit as st
import os

def render_config_page(db, selected_channel):
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

    # 3. Cấu hình thời lượng video (Bước 5)
    st.markdown('<div class="vc-eyebrow" style="margin-top:1.5rem;"><i class="bi bi-clock-history"></i> Cấu hình thời lượng video (Bước 5)</div>', unsafe_allow_html=True)
    from src.core.models import Project, VideoDurationConfig
    
    projects = db.query(Project).filter_by(channel_id=selected_channel.id).order_by(Project.id.desc()).all()
    if not projects:
        st.info("Kênh này chưa có dự án nào để cấu hình thời lượng video.")
    else:
        project_options = [f"#{p.id} - {p.idea[:40]}..." for p in projects]
        selected_project_opt = st.selectbox("Chọn Dự án để cấu hình thời lượng", project_options, key="config_project_select")
        
        project_id = int(selected_project_opt.split(" - ")[0].replace("#", ""))
        selected_project = next((p for p in projects if p.id == project_id), None)
        
        if selected_project:
            duration_cfg = db.query(VideoDurationConfig).filter_by(project_id=selected_project.id).first()
            if not duration_cfg:
                duration_cfg = VideoDurationConfig(
                    project_id=selected_project.id,
                    duration_type="system_generated",
                    target_duration=0,
                    min_duration=0,
                    max_duration=0,
                    system_ratio_multiplier=1.0
                )
                db.add(duration_cfg)
                db.commit()
                
            with st.container(border=True):
                col_dur1, col_dur2 = st.columns(2)
                with col_dur1:
                    dur_type = st.selectbox(
                        "Chế độ thời lượng",
                        ["system_generated", "uploaded_video"],
                        index=0 if duration_cfg.duration_type == "system_generated" else 1,
                        key=f"config_dur_type_{selected_project.id}"
                    )
                    tgt_dur = st.number_input(
                        "Thời lượng mong muốn (giây, 0 = theo âm thanh)",
                        min_value=0,
                        value=int(duration_cfg.target_duration or 0),
                        key=f"config_tgt_dur_{selected_project.id}"
                    )
                    min_dur = st.number_input(
                        "Thời lượng tối thiểu (giây)",
                        min_value=0,
                        value=int(duration_cfg.min_duration or 0),
                        key=f"config_min_dur_{selected_project.id}"
                    )
                with col_dur2:
                    max_dur = st.number_input(
                        "Thời lượng tối đa (giây, 0 = không giới hạn)",
                        min_value=0,
                        value=int(duration_cfg.max_duration or 0),
                        key=f"config_max_dur_{selected_project.id}"
                    )
                    src_path = st.text_input(
                        "Đường dẫn video nguồn (chế độ uploaded_video)",
                        value=duration_cfg.video_source_path or "",
                        key=f"config_src_path_{selected_project.id}"
                    )
                    ratio_mult = st.slider(
                        "Hệ số co giãn (Speed multiplier)",
                        min_value=0.5,
                        max_value=3.0,
                        value=float(duration_cfg.system_ratio_multiplier or 1.0),
                        step=0.1,
                        key=f"config_ratio_mult_{selected_project.id}"
                    )
                
                if st.button("Lưu cấu hình thời lượng", key=f"config_save_dur_{selected_project.id}", type="primary", use_container_width=True):
                    duration_cfg.duration_type = dur_type
                    duration_cfg.target_duration = tgt_dur
                    duration_cfg.min_duration = min_dur
                    duration_cfg.max_duration = max_dur
                    duration_cfg.video_source_path = src_path.strip() if src_path.strip() else None
                    duration_cfg.system_ratio_multiplier = ratio_mult
                    db.commit()
                    st.success("Đã lưu cấu hình thời lượng video thành công!")

            # 4. Bộ phân tích hiệu suất & Tự tối ưu Prompt (Chỉ dành cho ADMIN)
            if st.session_state.get("user_role") == "ADMIN":
                st.markdown('<div class="vc-eyebrow" style="margin-top:1.5rem;"><i class="bi bi-cpu"></i> Bộ Phân Tích Hiệu Suất & Tối Ưu Prompt (ADMIN ONLY)</div>', unsafe_allow_html=True)
                with st.container(border=True):
                    st.markdown("### Lịch sử Tự tối ưu Prompt & Phân tích chất lượng kịch bản")
                    
                    from src.core.models import PromptOptimizationLog
                    import json
                    
                    logs = db.query(PromptOptimizationLog).filter_by(project_id=selected_project.id).order_by(PromptOptimizationLog.created_at.desc()).all()
                    
                    if not logs:
                        st.info("Chưa có dữ liệu phân tích hiệu suất cho dự án này.")
                    else:
                        for log in logs:
                            step_title = "Bước 1: Phân tích Ý tưởng" if log.step_name == "step_1_analysis" else "Bước 2: Viết Kịch bản chi tiết"
                            status_badge = "[Đạt chuẩn]" if log.is_standardized else "[Cần tối ưu]"
                            
                            with st.container(border=True):
                                st.markdown(f"**{step_title}** -- {status_badge} -- *{log.created_at.strftime('%Y-%m-%d %H:%M:%S')}*")
                                
                                st.markdown("**Đầu vào ban đầu (Original input):**")
                                st.code(log.user_input_content, language="text")
                                
                                st.markdown("**Kết quả đã tối ưu / sửa đổi (Adjusted prompt / result):**")
                                st.code(log.adjusted_prompt, language="text")
                                
                                if log.analysis_metrics:
                                    try:
                                        metrics = json.loads(log.analysis_metrics)
                                        st.markdown("**Chỉ số phân tích hiệu suất:**")
                                        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
                                        with col_m1:
                                            st.metric("Tone / Tông giọng", metrics.get("tone", "N/A"))
                                        with col_m2:
                                            st.metric("Mật độ từ khóa", metrics.get("keyword_density", "N/A"))
                                        with col_m3:
                                            st.metric("Thời lượng dự kiến", metrics.get("estimated_duration", "N/A"))
                                        with col_m4:
                                            if "transition_score" in metrics:
                                                st.metric("Điểm liền mạch", f"{metrics['transition_score']}/10")
                                            else:
                                                st.metric("Trạng thái", "Đã phân tích")
                                                
                                        if "feedback" in metrics and metrics["feedback"]:
                                            st.markdown(f"**Ý kiến phản hồi:** *{metrics['feedback']}*")
                                        if "attempts" in metrics:
                                            st.markdown(f"**Số lần viết lại tự động:** `{metrics['attempts']}`")
                                    except Exception:
                                        st.text(f"Raw Metrics: {log.analysis_metrics}")
