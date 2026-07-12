import streamlit as st
from langchain_openai import ChatOpenAI
from crewai import Agent, Task, Crew, Process
import config
import os

st.set_page_config(page_title="AI Video Factory - Bé Tiểu Thư", layout="wide")
st.title("🎬 AI Video Factory - Bé Tiểu Thư (TikTok/Reel)")

with st.sidebar:
    st.header("Cài đặt")
    openai_key = st.text_input("OpenAI API Key", type="password", value=config.OPENAI_API_KEY)
    if openai_key:
        st.session_state["openai_key"] = openai_key

idea = st.text_area("Nhập ý tưởng video:", height=140, 
                    placeholder="Bé gái mặc váy hồng mới, cảm ơn mẹ mua đồ cho con")

if st.button("🚀 Bắt Đầu Quy Trình", type="primary"):
    if not idea or not openai_key:
        st.error("Nhập ý tưởng và API Key trước!")
    else:
        st.session_state["idea"] = idea
        st.session_state["llm"] = ChatOpenAI(model="gpt-5.4-mini", temperature=0.75, api_key=openai_key)
        st.session_state["stage"] = "script"
        st.session_state["results"] = {}
        st.rerun()

# ==================== STAGES ====================
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
            from core.workflow import run_stage
            prev = st.session_state["results"].get(list(st.session_state["results"].keys())[-1] if st.session_state["results"] else None, "")
            result = run_stage(current, st.session_state["idea"], prev, st.session_state["llm"])
            st.session_state["results"][current] = result
            st.rerun()

    # ==================== HIỂN THỊ KẾT QUẢ ====================
    if current in st.session_state.get("results", {}):
        result = st.session_state["results"][current]

        if current == "image":
            st.subheader("🖼️ Hình ảnh đã tạo")

            result_text = st.session_state["results"][current]

            image_path = None

            # Trường hợp 1: Đã có đường dẫn local trong text
            for line in result_text.split("\n"):
                if "generated_images" in line:
                    image_path = line.replace("📁 Đường dẫn ảnh: ", "").strip()
                    break

            # Trường hợp 2: Trả về base64 → tự giải mã và lưu
            if not image_path:
                import base64
                import re
                from PIL import Image
                from io import BytesIO

                # Tìm base64 trong result (thường dài)
                b64_match = re.search(r'([A-Za-z0-9+/=]{100,})', result_text)
                if b64_match:
                    b64_data = b64_match.group(1)
                    try:
                        img_data = base64.b64decode(b64_data)
                        img = Image.open(BytesIO(img_data))

                        os.makedirs("generated_images", exist_ok=True)
                        filename = f"generated_images/image_{len(os.listdir('generated_images')) + 1}.png"
                        img.save(filename)
                        image_path = filename
                        st.success("✅ Đã giải mã base64 và lưu ảnh local!")
                    except Exception as e:
                        st.error(f"Lỗi giải mã base64: {e}")

            # Hiển thị ảnh
            if image_path and os.path.exists(image_path):
                st.image(image_path, caption="Hình ảnh được tạo", use_container_width=True)
            else:
                st.warning("Không tìm thấy ảnh. Hiển thị kết quả gốc:")
                st.text(result_text)

        else:
            st.text_area("Kết quả:", value=result, height=350)

        # Nút điều khiển
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

# Tiến trình
if "results" in st.session_state and st.session_state["results"]:
    st.divider()
    st.subheader("Tiến trình")
    for s in stages:
        status = "✅" if s in st.session_state["results"] else "⏳"
        st.write(f"{status} {stage_names[s]}")