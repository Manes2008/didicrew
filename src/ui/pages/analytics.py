import streamlit as st
import os
import json

def render_analytics_page(db, selected_channel):
    if st.session_state.get("user_role") != "ADMIN":
        st.error("Khong co quyen truy cap. Chi danh cho ADMIN.")
        return

    st.markdown('<div class="vc-eyebrow"><i class="bi bi-graph-up"></i> Phan tich hieu qua AI va Video Viral</div>', unsafe_allow_html=True)
    st.subheader("Tong quan hieu suat He thong", anchor=False)

    from src.core.models import Project, PromptOptimizationLog, VideoAnalysisLog

    projects = db.query(Project).filter_by(channel_id=selected_channel.id).order_by(Project.id.desc()).all()
    if not projects:
        st.info("Kenh nay chua co du an nao de phan tich.")
        return

    project_options = [f"#{p.id} - {p.idea[:40]}..." for p in projects]
    selected_opt = st.selectbox("Chon du an de phan tich", project_options, key="analytics_project_select")
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
    col1.metric("Tong kich ban", total_scripts)
    col2.metric("Dat chuan (>=8)", passed_scripts)
    col3.metric("Diem chuyen canh TB", f"{avg_score:.1f}/10")
    col4.metric("Video mau phan tich", len(video_logs))

    if scores:
        st.markdown("---")
        st.markdown('<div class="vc-eyebrow"><i class="bi bi-bar-chart-line"></i> Xu huong Transition Score</div>', unsafe_allow_html=True)
        import pandas as pd
        df = pd.DataFrame({"Luot": list(range(1, len(scores) + 1)), "Diem": scores})
        st.area_chart(df.set_index("Luot"))

    st.markdown("---")
    st.markdown('<div class="vc-eyebrow"><i class="bi bi-journal-text"></i> Lich su Log Phan tich Prompt</div>', unsafe_allow_html=True)
    with st.container(border=True):
        if not prompt_logs:
            st.info("Chua co log phan tich nao.")
        else:
            for log in reversed(prompt_logs):
                step_label = "Buoc 1: Phan tich Y tuong" if log.step_name == "step_1_analysis" else "Buoc 2: Kiem tra Kich ban"
                status = "Dat chuan" if log.is_standardized else "Can toi uu"
                ts_str = log.created_at.strftime("%Y-%m-%d %H:%M")
                with st.expander(f"{step_label} -- {status} -- {ts_str}"):
                    c1, c2 = st.columns(2)
                    c1.text_area("Dau vao goc", log.user_input_content, height=100, key=f"li_{log.id}", disabled=True)
                    c2.text_area("Sau toi uu", log.adjusted_prompt, height=100, key=f"la_{log.id}", disabled=True)
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
                                st.info(f"Phan hoi: {fb}")
                        except Exception:
                            st.text(log.analysis_metrics)

    st.markdown("---")
    st.markdown('<div class="vc-eyebrow"><i class="bi bi-film"></i> Video Mau Viral - Phan tich 5 buoc</div>', unsafe_allow_html=True)
    tab_list, tab_new = st.tabs(["Video da phan tich", "Phan tich URL moi"])

    with tab_list:
        if not video_logs:
            st.info("Chua co video mau nao cho du an nay.")
        else:
            for vlog in video_logs:
                ts_str = vlog.created_at.strftime("%Y-%m-%d")
                sc = vlog.overall_viral_score
                with st.expander(f"{vlog.platform.upper()} - Score: {sc:.1f}/10 - {ts_str}"):
                    st.markdown(f"**URL:** {vlog.video_url}")
                    stage_attrs = [
                        ("step_1_idea_metrics", "Buoc 1: Y tuong va Chu de"),
                        ("step_2_script_metrics", "Buoc 2: Kich ban va Hook"),
                        ("step_3_visual_metrics", "Buoc 3: Hinh anh va Art Style"),
                        ("step_4_audio_metrics", "Buoc 4: Am thanh va Giong doc"),
                        ("step_5_render_metrics", "Buoc 5: Dung phim va Pacing"),
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
                            st.markdown(f"**{label}:** *Chua co du lieu*")
                    if vlog.analysis_report:
                        tv, tc = st.tabs(["Xem bao cao", "Sao chep"])
                        with tv:
                            st.markdown(vlog.analysis_report)
                        with tc:
                            st.code(vlog.analysis_report, language="markdown")

    with tab_new:
        with st.container(border=True):
            url_input = st.text_input("URL video (YouTube / TikTok / Instagram...)", placeholder="https://", key="analytics_url")
            if st.button("Phan tich video", type="primary", use_container_width=True):
                if not url_input.strip():
                    st.warning("Vui long nhap URL video.")
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

    analysis_prompt = """Phan tich video theo 5 buoc san xuat video ngan. Tra ve JSON thuan tuy (khong markdown).
JSON phai co cac truong:
step_1_idea_metrics (dict: theme, core_message, target_audience, vibe),
step_2_script_metrics (dict: hook_efficiency, hook_text, storytelling_structure, transition_score, estimated_duration_sec),
step_3_visual_metrics (dict: art_style, color_palette, character_profile, lighting),
step_4_audio_metrics (dict: voice_tone, pacing_wpm, bgm_energy, bpm),
step_5_render_metrics (dict: avg_scene_duration_sec, cut_frequency, transition_effect, caption_style),
overall_viral_score (float 1-10),
analysis_report_markdown (string bao cao chi tiet)."""

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            out_tpl = os.path.join(tmpdir, "video.%(ext)s")
            holder.info("Dang tai video bang yt-dlp...")
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
                st.error("Can cau hinh Gemini API Key de phan tich.")
                return

            try:
                import google.generativeai as genai
                genai.configure(api_key=gemini_key)
                model = genai.GenerativeModel("gemini-1.5-flash")
                if vfiles:
                    holder.info("Da tai video. Dang gui Gemini phan tich 5 buoc...")
                    with open(os.path.join(tmpdir, vfiles[0]), "rb") as vf:
                        vbytes = vf.read()
                    resp = model.generate_content([analysis_prompt, {"mime_type": "video/mp4", "data": vbytes}])
                else:
                    holder.warning("Khong tai duoc file video. Dang phan tich qua URL text...")
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
                st.error(f"Gemini API loi: {eg}")
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
            holder.success(f"Phan tich xong! Viral Score: {viral_score:.1f}/10")
            st.rerun()

    except subprocess.TimeoutExpired:
        st.error("Qua thoi gian tai video (3 phut).")
    except Exception as ex:
        st.error(f"Loi khi phan tich video: {ex}")
