import streamlit as st
import os
import datetime

# ===== Fernet Encryption Helpers =====
def _get_fernet():
    """Trả về Fernet instance từ ENCRYPTION_SECRET_KEY trong .env hoặc tự generate."""
    try:
        from cryptography.fernet import Fernet
    except ImportError:
        return None

    secret = os.getenv("ENCRYPTION_SECRET_KEY", "")
    if not secret:
        key = Fernet.generate_key().decode()
        env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '.env'))
        try:
            with open(env_path, "a", encoding="utf-8") as f:
                f.write(f"\nENCRYPTION_SECRET_KEY={key}\n")
            os.environ["ENCRYPTION_SECRET_KEY"] = key
            secret = key
        except Exception:
            return None
    try:
        return Fernet(secret.encode() if isinstance(secret, str) else secret)
    except Exception:
        return None

def encrypt_value(plaintext: str) -> str:
    f = _get_fernet()
    if not f or not plaintext:
        return plaintext
    return f.encrypt(plaintext.encode()).decode()

def decrypt_value(ciphertext: str) -> str:
    f = _get_fernet()
    if not f or not ciphertext:
        return ciphertext
    try:
        return f.decrypt(ciphertext.encode()).decode()
    except Exception:
        return ""

def load_config_from_db(db, key: str) -> str:
    """Đọc và decrypt giá trị từ bảng system_configs."""
    try:
        from src.core.models import SystemConfig
        rec = db.query(SystemConfig).filter_by(key=key).first()
        if rec and rec.value:
            return decrypt_value(rec.value) if rec.is_encrypted else rec.value
    except Exception:
        pass
    return ""

def save_config_to_db(db, key: str, value: str, encrypt: bool = True):
    """Encrypt và lưu giá trị vào bảng system_configs."""
    from src.core.models import SystemConfig
    rec = db.query(SystemConfig).filter_by(key=key).first()
    stored = encrypt_value(value) if encrypt else value
    if rec:
        rec.value = stored
        rec.is_encrypted = encrypt
        rec.updated_at = datetime.datetime.utcnow()
    else:
        rec = SystemConfig(key=key, value=stored, is_encrypted=encrypt)
        db.add(rec)
    db.commit()


def render_config_page(db, selected_channel):
    st.markdown('<div class="vc-eyebrow"><i class="bi bi-sliders"></i> Cấu hình hệ thống</div>', unsafe_allow_html=True)
    st.subheader("Cấu hình API Keys & AI Models", anchor=False)

    # 1. Quản lý API Keys
    st.markdown('<div class="vc-eyebrow" style="margin-top:1rem;"><i class="bi bi-key"></i> Quản lý API Keys</div>', unsafe_allow_html=True)
    with st.container(border=True):
        # Nạp từ DB 1 lần duy nhất mỗi session
        if not st.session_state.get("_cfg_keys_loaded"):
            db_openai = load_config_from_db(db, "openai_api_key")
            db_gemini = load_config_from_db(db, "gemini_api_key")
            if db_openai and not st.session_state.get("custom_openai_key"):
                st.session_state["custom_openai_key"] = db_openai
                os.environ["OPENAI_API_KEY"] = db_openai
            if db_gemini and not st.session_state.get("custom_gemini_key"):
                st.session_state["custom_gemini_key"] = db_gemini
                os.environ["GEMINI_API_KEY"] = db_gemini
            st.session_state["_cfg_keys_loaded"] = True

        current_openai = st.session_state.get("custom_openai_key") or os.getenv("OPENAI_API_KEY", "")
        current_gemini = st.session_state.get("custom_gemini_key") or os.getenv("GEMINI_API_KEY", "")

        def mask_key(k):
            if not k: return ""
            if len(k) > 12: return f"{k[:6]}...{k[-6:]}"
            return "******"

        st.info("API Key nhập tại đây sẽ được **mã hóa Fernet và lưu vào database** — tự động nạp lại sau khi restart.")

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
            saved = False
            if openai_key_input.strip():
                try:
                    save_config_to_db(db, "openai_api_key", openai_key_input.strip(), encrypt=True)
                    st.session_state["custom_openai_key"] = openai_key_input.strip()
                    os.environ["OPENAI_API_KEY"] = openai_key_input.strip()
                    saved = True
                except Exception as ex:
                    st.error(f"Lỗi lưu OpenAI Key: {ex}")
            if gemini_key_input.strip():
                try:
                    save_config_to_db(db, "gemini_api_key", gemini_key_input.strip(), encrypt=True)
                    st.session_state["custom_gemini_key"] = gemini_key_input.strip()
                    os.environ["GEMINI_API_KEY"] = gemini_key_input.strip()
                    saved = True
                except Exception as ex:
                    st.error(f"Lỗi lưu Gemini Key: {ex}")
            if saved:
                st.success("Đã mã hóa và lưu API Keys vào database thành công!")
                st.rerun()
            else:
                st.warning("Vui lòng nhập ít nhất một API Key để lưu.")

    # 2. Cấu hình AI Model & Engines
    st.markdown('<div class="vc-eyebrow" style="margin-top:1.5rem;"><i class="bi bi-cpu"></i> Chon AI Model & Render Engines</div>', unsafe_allow_html=True)
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
            engine_map = {"openai": 0, "sd1.5_local": 1, "markl_local": 2}
            image_index = engine_map.get(current_image_engine, 0)
            image_engine_option = st.selectbox("Engine Sinh Anh", image_options, index=image_index, key="select_image_page")

            reverse_map = {
                "OpenAI DALL-E": "openai",
                "Stable Diffusion v1.5 (CPU)": "sd1.5_local",
                "Mark-L Local (GPU)": "markl_local"
            }
            st.session_state["image_engine"] = reverse_map[image_engine_option]

        if st.button("Lưu Cấu Hình Model", width="stretch"):
            st.success("Đã lưu cấu hình AI Model thành công!")
            st.rerun()

    # ─── 3. Backup & Restore ───────────────────────────────────────────────
    st.markdown('<div class="vc-eyebrow" style="margin-top:1.5rem;"><i class="bi bi-database"></i> Backup & Restore Du lieu</div>', unsafe_allow_html=True)
    with st.container(border=True):
        tab_bk, tab_rs = st.tabs([":material/cloud_download: Tao Backup", ":material/restore: Restore tu Backup"])

        # ── Tab Tao Backup ──
        with tab_bk:
            st.info("Backup toàn bộ dữ liệu DB (bao gồm ảnh, audio, video nhị phân) và file local vào 1 file ZIP.")
            col_bk1, col_bk2 = st.columns(2)
            with col_bk1:
                include_files = st.checkbox("Bao gồm file local (generated_images, videos, ...)", value=True, key="bk_include_files")
            with col_bk2:
                st.caption("File ZIP có thể đạt 100MB+ nếu có nhiều ảnh/video.")

            if st.button("Tạo Backup ngay", icon=":material/backup:", type="primary", width="stretch"):
                with st.spinner("Đang xuất dữ liệu, vui lòng chờ..."):
                    try:
                        from src.tools.backup_restore import create_backup
                        zip_bytes, stats = create_backup(db, include_local_files=include_files)
                        st.session_state["_backup_bytes"] = zip_bytes
                        st.session_state["_backup_stats"] = stats
                        st.success(f"Tạo backup thành công! Kích thước: {len(zip_bytes) / 1024:.1f} KB")
                    except Exception as ex:
                        st.error(f"Lỗi tạo backup: {ex}")

            if st.session_state.get("_backup_bytes"):
                zip_bytes = st.session_state["_backup_bytes"]
                stats = st.session_state.get("_backup_stats", {})
                ts = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
                st.download_button(
                    label=f"Tai ve file backup ({len(zip_bytes)/1024:.1f} KB)",
                    data=zip_bytes,
                    file_name=f"videocrew_backup_{ts}.zip",
                    mime="application/zip",
                    icon=":material/download:",
                    width="stretch"
                )
                # Hien thi thong ke
                if stats:
                    st.markdown("**Thống kê dữ liệu đã backup:**")
                    stat_rows = {k: v for k, v in stats.items() if k != "local_files" and not str(v).startswith("ERROR")}
                    if stat_rows:
                        col_s1, col_s2, col_s3 = st.columns(3)
                        items = list(stat_rows.items())
                        for idx, (tname, cnt) in enumerate(items):
                            with [col_s1, col_s2, col_s3][idx % 3]:
                                st.metric(tname, cnt)
                    local_stats = stats.get("local_files", {})
                    if local_stats:
                        st.caption("File local: " + ", ".join(f"{k}={v}" for k, v in local_stats.items()))

        # ── Tab Restore ──
        with tab_rs:
            st.warning("Restore sẽ THÊM các record chưa tồn tại. Record đã có (cùng PK) sẽ bị BỎ QUA (skip).")
            uploaded = st.file_uploader("Chọn file backup (.zip)", type=["zip"], key="rs_upload")

            if uploaded:
                zip_bytes_up = uploaded.read()
                # Hien thi preview
                try:
                    from src.tools.backup_restore import get_backup_preview, restore_backup
                    preview = get_backup_preview(zip_bytes_up)
                    if "error" in preview:
                        st.error(f"File backup không hợp lệ: {preview['error']}")
                    else:
                        with st.expander("Xem thông tin backup này", expanded=True):
                            st.markdown(f"- **Phiên bản:** `{preview.get('backup_version', 'N/A')}`")
                            st.markdown(f"- **Thời điểm tạo:** `{preview.get('created_at', 'N/A')}`")
                            bk_stats = preview.get("stats", {})
                            if bk_stats:
                                stat_items = {k: v for k, v in bk_stats.items() if k != "local_files"}
                                st.markdown("**Nội dung các bảng:**")
                                for tname, cnt in stat_items.items():
                                    st.caption(f"  {tname}: {cnt} records")
                                local_fs = bk_stats.get("local_files", {})
                                if local_fs:
                                    st.caption("File local: " + ", ".join(f"{k}={v}" for k, v in local_fs.items()))

                        if st.button("Bắt đầu Restore", icon=":material/restore:", type="primary", width="stretch"):
                            with st.spinner("Đang restore dữ liệu, vui lòng chờ..."):
                                try:
                                    result = restore_backup(db, zip_bytes_up, overwrite=False)
                                    st.success("Restore hoàn tất!")
                                    # Bao cao ket qua
                                    for tname, info in result.items():
                                        if tname == "local_files_restored":
                                            st.caption(f"File local đã phục hồi: {info}")
                                        elif isinstance(info, dict):
                                            if "error" in info:
                                                st.error(f"{tname}: {info['error']}")
                                            else:
                                                ins = info.get('inserted', 0)
                                                skp = info.get('skipped', 0)
                                                err = info.get('errors', 0)
                                                color = "normal" if err == 0 else "inverse"
                                                st.caption(f"{tname}: +{ins} thêm | {skp} bỏ qua | {err} lỗi")
                                except Exception as ex:
                                    st.error(f"Lỗi restore: {ex}")
                except ImportError:
                    st.error("Module backup_restore chua duoc cai dat.")
