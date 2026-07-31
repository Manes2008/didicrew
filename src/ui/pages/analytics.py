import streamlit as st
import os
import json

def render_analytics_page(db, selected_channel):
    if st.session_state.get("user_role") != "ADMIN":
        st.error("Không có quyền truy cập. Chỉ dành cho ADMIN.")
        return

    st.markdown('<div class="vc-eyebrow"><i class="bi bi-graph-up"></i> Phân tích hiệu quả AI và Video Viral</div>', unsafe_allow_html=True)
    st.subheader("Tổng quan hiệu suất Hệ thống", anchor=False)

    from src.core.models import Project, PromptOptimizationLog, VideoAnalysisLog

    projects = db.query(Project).filter_by(channel_id=selected_channel.id).order_by(Project.id.desc()).all()
    if not projects:
        st.info("Kênh này chưa có dự án nào để phân tích.")
        return

    project_options = [f"#{p.id} - {p.idea[:40]}..." for p in projects]
    selected_opt = st.selectbox("Chọn dự án để phân tích", project_options, key="analytics_project_select")
    project_id = int(selected_opt.split(" - ")[0].replace("#", ""))
    selected_project = next((p for p in projects if p.id == project_id), None)
    if not selected_project:
        return

    st.markdown("---")
    prompt_logs = db.query(PromptOptimizationLog).filter_by(project_id=selected_project.id).all()
    video_logs = db.query(VideoAnalysisLog).filter_by(project_id=selected_project.id).order_by(VideoAnalysisLog.id.desc()).all()
    total_scripts = len([l for l in prompt_logs if l.step_name == "step_2_scripting"])
    passed_scripts = len([l for l in prompt_logs if l.step_name == "step_2_scripting" and l.is_standardized])
    scores = []
    for log in prompt_logs:
        if log.step_name == "step_2_scripting" and log.analysis_metrics:
            try:
                m = json.loads(log.analysis_metrics)
                s = m.get("transition_score", 0)
                if s:
                    scores.append(float(s))
            except Exception:
                pass
    avg_score = sum(scores) / len(scores) if scores else 0.0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Tổng kịch bản", total_scripts)
    col2.metric("Đạt chuẩn (>=8)", passed_scripts)
    col3.metric("Điểm chuyển cảnh TB", f"{avg_score:.1f}/10")
    col4.metric("Video mẫu phân tích", len(video_logs))

    if scores:
        st.markdown("---")
        st.markdown('<div class="vc-eyebrow"><i class="bi bi-bar-chart-line"></i> Xu hướng Transition Score</div>', unsafe_allow_html=True)
        import pandas as pd
        df = pd.DataFrame({"Lượt": list(range(1, len(scores) + 1)), "Điểm": scores})
        st.area_chart(df.set_index("Lượt"))

    st.markdown("---")
    st.markdown('<div class="vc-eyebrow"><i class="bi bi-journal-text"></i> Lịch sử Log Phân tích Prompt</div>', unsafe_allow_html=True)
    with st.container(border=True):
        if not prompt_logs:
            st.info("Chưa có log phân tích nào.")
        else:
            for log in reversed(prompt_logs):
                if log.step_name == "step_1_analysis":
                    step_label = "Bước 1: Phân tích Ý tưởng"
                elif log.step_name == "step_2_scripting":
                    step_label = "Bước 2: Kiểm tra Kịch bản"
                elif log.step_name == "step_3_visual":
                    step_label = "Bước 3: Mô tả hình ảnh (Visual)"
                else:
                    step_label = f"Giai đoạn: {log.step_name}"
                status = "Đạt chuẩn" if log.is_standardized else "Cần tối ưu"
                ts_str = log.created_at.strftime("%Y-%m-%d %H:%M")
                with st.expander(f"{step_label} -- {status} -- {ts_str}"):
                    c1, c2 = st.columns(2)
                    c1.text_area("Đầu vào gốc", log.user_input_content, height=100, key=f"li_{log.id}", disabled=True)
                    c2.text_area("Sau tối ưu", log.adjusted_prompt, height=100, key=f"la_{log.id}", disabled=True)
                    if log.analysis_metrics:
                        try:
                            m = json.loads(log.analysis_metrics)
                            nested = m.get("metrics", {})
                            mc1, mc2, mc3, mc4 = st.columns(4)
                            mc1.metric("Tone", m.get("tone", nested.get("tone", "N/A")))
                            mc2.metric("Keyword", m.get("keyword_density", nested.get("keyword_density", "N/A")))
                            mc3.metric("Duration", m.get("estimated_duration", nested.get("estimated_duration", "N/A")))
                            ts_val = m.get("transition_score")
                            if ts_val:
                                mc4.metric("Transition Score", f"{ts_val}/10")
                            fb = m.get("feedback")
                            if fb:
                                st.info(f"Phản hồi: {fb}")
                        except Exception:
                            st.text(log.analysis_metrics)

    st.markdown("---")
    st.markdown('<div class="vc-eyebrow"><i class="bi bi-film"></i> Video Mẫu Viral - Phân tích 5 bước</div>', unsafe_allow_html=True)
    tab_list, tab_new = st.tabs(["Video đã phân tích", "Phân tích URL mới"])

    with tab_list:
        if not video_logs:
            st.info("Chưa có video mẫu nào cho dự án này.")
        else:
            for vlog in video_logs:
                ts_str = vlog.created_at.strftime("%Y-%m-%d")
                sc = vlog.overall_viral_score
                with st.expander(f"{vlog.platform.upper()} - Score: {sc:.1f}/10 - {ts_str}"):
                    st.markdown(f"**URL:** {vlog.video_url}")
                    stage_attrs = [
                        ("step_1_idea_metrics", "Bước 1: Ý tưởng và Chủ đề"),
                        ("step_2_script_metrics", "Bước 2: Kịch bản và Hook"),
                        ("step_3_visual_metrics", "Bước 3: Hình ảnh và Art Style"),
                        ("step_4_audio_metrics", "Bước 4: Âm thanh và Giọng đọc"),
                        ("step_5_render_metrics", "Bước 5: Dựng phim và Pacing"),
                    ]
                    for attr, label in stage_attrs:
                        val = getattr(vlog, attr)
                        if val:
                            try:
                                st.markdown(f"**{label}:**")
                                st.json(json.loads(val))
                            except Exception:
                                st.markdown(f"**{label}:** {val}")
                        else:
                            st.markdown(f"**{label}:** *Chưa có dữ liệu*")
                    if vlog.analysis_report:
                        tv, tc = st.tabs(["Xem báo cáo", "Sao chép"])
                        with tv:
                            st.markdown(vlog.analysis_report)
                        with tc:
                            st.code(vlog.analysis_report, language="markdown")

    with tab_new:
        with st.container(border=True):
            url_input = st.text_input("URL video (YouTube / TikTok / Instagram...)", placeholder="https://", key="analytics_url")
            if st.button("Phân tích video", type="primary", use_container_width=True):
                if not url_input.strip():
                    st.warning("Vui lòng nhập URL video.")
                else:
                    _run_video_analysis(db, selected_project, url_input.strip())


def _detect_platform(url):
    u = url.lower()
    if "youtube" in u or "youtu.be" in u:
        return "youtube"
    if "tiktok" in u:
        return "tiktok"
    if "instagram" in u:
        return "instagram"
    if "facebook" in u or "fb.watch" in u:
        return "facebook"
    return "other"


def _run_video_analysis(db, project, video_url):
    import tempfile
    import subprocess
    from src.core.models import VideoAnalysisLog

    platform = _detect_platform(video_url)
    gemini_key = st.session_state.get("custom_gemini_key") or os.getenv("GEMINI_API_KEY", "")
    holder = st.empty()

    analysis_prompt = (
        "Phân tích video theo 5 bước sản xuất video ngắn. Trả về JSON thuần túy (không markdown).\n"
        "JSON phải có các trường:\n"
        "step_1_idea_metrics (dict: theme, core_message, target_audience, vibe),\n"
        "step_2_script_metrics (dict: hook_efficiency, hook_text, storytelling_structure, transition_score, estimated_duration_sec),\n"
        "step_3_visual_metrics (dict: art_style, color_palette, character_profile, lighting),\n"
        "step_4_audio_metrics (dict: voice_tone, pacing_wpm, bgm_energy, bpm),\n"
        "step_5_render_metrics (dict: avg_scene_duration_sec, cut_frequency, transition_effect, caption_style),\n"
        "overall_viral_score (float 1-10),\n"
        "analysis_report_markdown (string báo cáo chi tiết)."
    )

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            out_tpl = os.path.join(tmpdir, "video.%(ext)s")
            holder.info("Đang tải video bằng yt-dlp...")
            cmd = [
                "yt-dlp", "--no-playlist",
                "-f", "bestvideo[height<=480]+bestaudio/best[height<=480]",
                "--merge-output-format", "mp4",
                "-o", out_tpl, video_url
            ]
            subprocess.run(cmd, capture_output=True, text=True, timeout=180)
            vfiles = [f for f in os.listdir(tmpdir) if f.endswith((".mp4", ".mkv", ".webm"))]

            step_data = {}
            report_md = ""

            if not gemini_key:
                st.error("Cần cấu hình Gemini API Key để phân tích.")
                return

            try:
                import google.generativeai as genai
                genai.configure(api_key=gemini_key)
                model = genai.GenerativeModel("gemini-1.5-flash")
                if vfiles:
                    holder.info("Đã tải video. Đang gửi Gemini phân tích 5 bước...")
                    with open(os.path.join(tmpdir, vfiles[0]), "rb") as vf:
                        vbytes = vf.read()
                    resp = model.generate_content([analysis_prompt, {"mime_type": "video/mp4", "data": vbytes}])
                else:
                    holder.warning("Không tải được file video. Đang phân tích qua URL text...")
                    resp = model.generate_content([f"{analysis_prompt}\nURL: {video_url}"])
                raw = resp.text.strip()
                for prefix in ("```json", "```"):
                    if raw.startswith(prefix):
                        raw = raw[len(prefix):]
                if raw.endswith("```"):
                    raw = raw[:-3]
                step_data = json.loads(raw.strip())
                report_md = step_data.pop("analysis_report_markdown", "")
            except Exception as eg:
                st.error(f"Gemini API lỗi: {eg}")
                return

            viral_score = float(step_data.get("overall_viral_score", 0.0))
            log = VideoAnalysisLog(
                project_id=int(project.id),
                video_url=video_url,
                platform=platform,
                step_1_idea_metrics=json.dumps(step_data.get("step_1_idea_metrics", {}), ensure_ascii=False),
                step_2_script_metrics=json.dumps(step_data.get("step_2_script_metrics", {}), ensure_ascii=False),
                step_3_visual_metrics=json.dumps(step_data.get("step_3_visual_metrics", {}), ensure_ascii=False),
                step_4_audio_metrics=json.dumps(step_data.get("step_4_audio_metrics", {}), ensure_ascii=False),
                step_5_render_metrics=json.dumps(step_data.get("step_5_render_metrics", {}), ensure_ascii=False),
                overall_viral_score=viral_score,
                analysis_report=report_md if report_md else json.dumps(step_data, ensure_ascii=False, indent=2)
            )
            db.add(log)
            db.commit()
            holder.success(f"Phân tích xong! Viral Score: {viral_score:.1f}/10")
            st.rerun()

    except subprocess.TimeoutExpired:
        st.error("Quá thời gian tải video (3 phút).")
    except Exception as ex:
        st.error(f"Lỗi khi phân tích video: {ex}")
