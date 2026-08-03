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

        if st.button("Luu API Keys", type="primary"):
            saved = False
            if openai_key_input.strip():
                try:
                    save_config_to_db(db, "openai_api_key", openai_key_input.strip(), encrypt=True)
                    st.session_state["custom_openai_key"] = openai_key_input.strip()
                    os.environ["OPENAI_API_KEY"] = openai_key_input.strip()
                    saved = True
                except Exception as ex:
                    st.error(f"Loi luu OpenAI Key: {ex}")
            if gemini_key_input.strip():
                try:
                    save_config_to_db(db, "gemini_api_key", gemini_key_input.strip(), encrypt=True)
                    st.session_state["custom_gemini_key"] = gemini_key_input.strip()
                    os.environ["GEMINI_API_KEY"] = gemini_key_input.strip()
                    saved = True
                except Exception as ex:
                    st.error(f"Loi luu Gemini Key: {ex}")
            if saved:
                st.success("Da ma hoa va luu API Keys vao database thanh cong!")
                st.rerun()
            else:
                st.warning("Vui long nhap it nhat mot API Key de luu.")

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

        if st.button("Luu Cau Hinh Model", use_container_width=True):
            st.success("Da luu cau hinh AI Model thanh cong!")
            st.rerun()

