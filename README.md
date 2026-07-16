# VideoCrew - AI Video Factory

> **Hệ thống tự động sản xuất nội dung video ngắn (TikTok/Reel) cho nhân vật Bé Tiểu Thư bằng AI.**

Được xây dựng trên nền tảng **CrewAI** + **OpenAI** + **Streamlit**, hệ thống điều phối 5 Agent AI chuyên biệt để thực hiện toàn bộ quy trình từ ý tưởng đến nguyên liệu sản xuất video hoàn chỉnh.

---

## Kiến trúc hệ thống

```text
videocrew/
├── config/
│   ├── agents.yaml          # Định nghĩa role, goal, backstory cho từng Agent
│   └── tasks.yaml           # Mô tả nhiệm vụ và đầu ra kỳ vọng cho từng stage
├── generated_images/        # Thư mục lưu ảnh được tạo ra (auto-created)
├── src/
│   ├── agents/
│   │   └── factory.py       # AgentFactory: Khởi tạo CrewAI Agent động từ config YAML
│   ├── tools/
│   │   └── image_tool.py    # Tool sinh ảnh: gpt-image-2 (fallback: gpt-image-1-mini)
│   └── core/
│       ├── engine.py        # WorkflowEngine: Điều phối 5 stage chạy tuần tự
│       └── llm_provider.py  # Khởi tạo LLM linh hoạt (OpenAI / Google Gemini)
├── .env                     # API Keys bảo mật (không commit lên git)
├── app.py                   # Giao diện Streamlit (UI mỏng, gọi engine, hiển thị kết quả)
├── config.py                # Load biến môi trường từ .env
├── Dockerfile               # Đóng gói Docker
├── docker-compose.yml       # Cấu hình Docker Compose
├── run.bat                  # Script khởi chạy nhanh trên Windows
├── run.sh                   # Script khởi chạy nhanh trên Linux/macOS
└── requirements.txt
```

---

## Quy trình 5 Stage (Pipeline)

Hệ thống thực thi tuần tự 5 stage, kết quả của stage trước là đầu vào của stage tiếp theo:

| Stage | Agent | Mô tả |
| :---: | :--- | :--- |
| **1** | Senior Script Writer | Nhận ý tưởng → Viết kịch bản TikTok 25-30s hoàn chỉnh (hook, lời thoại, timing) |
| **2** | Visual Prompt Engineer | Nhận kịch bản → Tạo prompt hình ảnh chi tiết (phong cách, nhân vật, bối cảnh) |
| **3** | Image Generation | Nhận prompt → **Gọi trực tiếp API** gpt-image-2 → Lưu ảnh local → Hiển thị |
| **4** | Voiceover Specialist | Nhận kịch bản → Soạn text voiceover + cấu hình giọng đọc ElevenLabs |
| **5** | Video Editor | Nhận tất cả nguyên liệu → Hướng dẫn ghép video chi tiết trong CapCut |

---

## Thiết kế tối ưu hóa chi phí

### Stage 3 (Tạo Hình Ảnh) - Gọi trực tiếp không qua Agent

Stage sinh ảnh được thiết kế để **bỏ qua CrewAI Agent** và gọi trực tiếp hàm Python:

```python
# src/core/engine.py
if stage_name == "image":
    from src.tools.image_tool import generate_gpt_image_func
    prompt = previous_result if previous_result else idea
    return generate_gpt_image_func(prompt)
```

**Lý do**: Sinh ảnh là tác vụ xác định (deterministic), không cần LLM suy luận. Việc gọi trực tiếp giúp:
- Tiết kiệm **3,000 - 8,000 tokens/lần** (loại bỏ vòng suy luận Agent)
- Đảm bảo thành công **100%** (tránh lỗi LLM từ chối gọi tool)
- Tốc độ phản hồi nhanh hơn **5-10 lần**

### Cơ chế Fallback tự động cho model sinh ảnh

```python
# src/tools/image_tool.py
# Uu tien gpt-image-2 (chat luong cao nhat)
# Neu loi → tu dong ha cap gpt-image-1-mini
# Neu ca hai loi → tra ve thong bao huong dan khac phuc chi tiet
```

---

## Cài đặt và Chạy

### Yêu cầu
- Python 3.10+
- OpenAI API Key (có quyền truy cập `gpt-image-2` hoặc `gpt-image-1-mini`)
- Google Gemini API Key (tùy chọn nếu dùng Gemini làm LLM viết kịch bản)

### 1. Cài đặt thủ công

```bash
git clone https://github.com/Manes2008/didicrew.git
cd didicrew
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Tạo file `.env`:

```env
OPENAI_API_KEY=sk-proj-...
GEMINI_API_KEY=AIza...
```

Khởi chạy:

```bash
streamlit run app.py
```

### 2. Khởi chạy nhanh (Windows)

```bat
.\run.bat
```

Script tự động: kiểm tra Python → kích hoạt venv → cài đặt thư viện → chạy Streamlit.

### 3. Docker

```bash
docker-compose up --build
```

Truy cập tại: `http://localhost:8501`

---

## Hướng dẫn lập trình (Sử dụng trực tiếp trong Python)

Hệ thống được thiết kế dạng **mô-đun hóa (modular)**, cho phép bạn gọi riêng lẻ từng module chức năng (stage) dựa trên kết quả của module trước đó.

### Khởi tạo môi trường chung

```python
from src.core.llm_provider import get_llm
from src.core.engine import run_stage

# Khởi tạo LLM dùng chung cho các module
llm = get_llm(
    provider="OpenAI",
    model_name="gpt-4o-mini",
    api_key="YOUR_OPENAI_API_KEY"
)
idea = "Be gai mac vay hong cam on me"
```

### Chi tiết cách gọi các Module chức năng

#### 1. Module Viết Kịch Bản (`script`)
* **Input**: Ý tưởng gốc (`idea`).
* **Output**: Kịch bản chi tiết gồm phân cảnh và lời thoại nhân vật.
```python
script_result = run_stage("script", idea, llm=llm)
```

#### 2. Module Tạo Prompt Hình Ảnh (`visual`)
* **Input**: Kịch bản phân cảnh từ module trước (`previous_result`).
* **Output**: Mô tả hình ảnh (prompts) chi tiết cho từng phân cảnh.
```python
visual_result = run_stage("visual", idea, previous_result=script_result, llm=llm)
```

#### 3. Module Tạo Hình Ảnh (`image`)
* **Input**: Prompt hình ảnh chi tiết từ module tạo prompt (`previous_result`).
* **Output**: Đường dẫn tệp ảnh cục bộ đã lưu trên đĩa.
```python
image_result = run_stage("image", idea, previous_result=visual_result)
```

#### 4. Module Tạo Giọng Nói (`voice`)
* **Input**: Kịch bản lời thoại từ module viết kịch bản (`previous_result`).
* **Output**: Văn bản kịch bản lồng tiếng kèm tham số giọng đọc.
```python
voice_result = run_stage("voice", idea, previous_result=script_result, llm=llm)
```

#### 5. Module Hướng Dẫn Dựng Video (`editor`)
* **Input**: Toàn bộ kịch bản và thông tin nguyên liệu từ module tạo giọng nói (`previous_result`).
* **Output**: Hướng dẫn dựng video chi tiết từng bước trên CapCut.
```python
editor_result = run_stage("editor", idea, previous_result=voice_result, llm=llm)
```

---

## Hỗ trợ LLM

Chọn nhà cung cấp LLM trực tiếp trên giao diện Streamlit:

| Nhà cung cấp | Model hỗ trợ |
| :--- | :--- |
| **OpenAI** | `gpt-4o-mini`, `gpt-4o`, `gpt-3.5-turbo` |
| **Google Gemini** | `gemini-1.5-flash`, `gemini-1.5-pro` |

---

## Các model sinh ảnh được hỗ trợ

| Model | Ưu tiên | Ghi chú |
| :--- | :---: | :--- |
| `gpt-image-2` | Chính | Mới nhất, chất lượng cao nhất |
| `gpt-image-1-mini` | Fallback | Nhanh hơn, dùng khi gpt-image-2 không khả dụng |

Hệ thống tự động phát hiện model khả dụng trong tài khoản và chọn model phù hợp.

---

## License

MIT License - Copyright (c) 2026 Manes2008/didicrew
