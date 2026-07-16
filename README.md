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
├── migrations/              # Alembic migration scripts (tự động sinh)
│   ├── env.py               # Cấu hình Alembic (kết nối DB từ .env)
│   ├── script.py.mako       # Template sinh migration file
│   └── versions/            # Các phiên bản migration
├── src/
│   ├── agents/
│   │   └── factory.py       # AgentFactory: Khởi tạo CrewAI Agent động từ config YAML
│   ├── tools/
│   │   └── image_tool.py    # Tool sinh ảnh: gpt-image-2 (fallback: gpt-image-1-mini)
│   └── core/
│       ├── engine.py        # WorkflowEngine: Điều phối 5 stage chạy tuần tự
│       ├── llm_provider.py  # Khởi tạo LLM linh hoạt (OpenAI / Google Gemini)
│       └── models.py        # SQLAlchemy ORM Models + init_db() tự động tạo bảng
├── .env                     # API Keys & DATABASE_URL bảo mật (không commit lên git)
├── alembic.ini              # Cấu hình Alembic CLI
├── app.py                   # Giao diện Streamlit (UI mỏng, gọi engine, hiển thị kết quả)
├── config.py                # Load biến môi trường từ .env + tự động chuyển đổi DB URL
├── Dockerfile               # Đóng gói Docker
├── docker-compose.yml       # Cấu hình Docker Compose
├── run.bat                  # Script khởi chạy nhanh trên Windows
├── run.sh                   # Script khởi chạy nhanh trên Linux/macOS
└── requirements.txt
```

---

## Kiến trúc Cơ sở Dữ liệu (Database Architecture)

### Cấu hình kết nối

Hệ thống sử dụng **PostgreSQL** kết nối qua SQLAlchemy ORM và quản lý phiên bản cấu trúc bằng **Alembic**. Khai báo `DATABASE_URL` trong file `.env`:

```env
# Kết nối local PostgreSQL
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/videocrew

# Kết nối Render PostgreSQL (nội bộ - chỉ dùng trên môi trường Render)
DATABASE_URL=postgresql://user:password@dpg-xxxxxx-a/dbname

# Kết nối Render PostgreSQL (bên ngoài - dùng khi chạy local)
DATABASE_URL=postgresql://user:password@dpg-xxxxxx-a.singapore-postgres.render.com/dbname
```

> **Lưu ý**: Hệ thống **tự động phát hiện** môi trường và chuyển đổi Render Internal URL thành External URL khi bạn chạy ở máy local (không cần sửa thủ công).

Khi khởi chạy ứng dụng lần đầu, **các bảng được tạo tự động** thông qua `init_db()` mà không cần chạy lệnh migration thủ công.

---

### Sơ đồ quan hệ các bảng (ERD)

```text
channels
├── id (PK)
├── name (UNIQUE, NOT NULL)        # Tên kênh (ví dụ: Bé Tiểu Thư, Kênh Ẩm Thực...)
├── description
├── goal (NOT NULL)
├── created_at / updated_at
│
├──< channel_stage_configs          # Cấu hình Agent riêng cho từng stage của kênh
│    ├── id (PK)
│    ├── channel_id (FK → channels)
│    ├── stage_name                 # script | visual | image | voice | editor
│    ├── role / goal / backstory    # Nội dung Agent tùy biến theo kênh
│    └── markdown_template
│
└──< projects                       # Mỗi lần tạo video = 1 Project
     ├── id (PK)
     ├── channel_id (FK → channels)
     ├── idea (NOT NULL)            # Ý tưởng video ban đầu
     ├── provider / model_name      # LLM được chọn (OpenAI / Google Gemini)
     ├── current_stage              # Stage hiện tại đang chạy
     ├── status                     # pending | running | completed
     ├── created_at / updated_at
     │
     └──< project_stages            # Kết quả từng stage của project
          ├── id (PK)
          ├── project_id (FK → projects)
          ├── stage_name             # script | visual | image | voice | editor
          ├── result_content (TEXT)  # Nội dung kết quả đầu ra
          ├── media_path             # Đường dẫn file media chính (nếu có)
          ├── status                 # pending | completed | failed
          ├── created_at / updated_at
          │
          └──< media_files          # Thông tin chi tiết file media được tạo ra
               ├── id (PK)
               ├── project_stage_id (FK → project_stages)
               ├── file_name / file_path   # Tên và đường dẫn lưu trữ file
               ├── mime_type              # image/png | audio/mp3 ...
               ├── file_size (BIGINT)     # Kích thước file (bytes)
               ├── duration_seconds       # Thời lượng (dùng cho audio/video)
               ├── status                 # active | deleted
               └── created_at
```

### Mô tả chi tiết các bảng

| Bảng | Mô tả |
| :--- | :--- |
| `channels` | Quản lý nhiều kênh nội dung khác nhau. Mỗi kênh có mục tiêu và phong cách riêng. |
| `channel_stage_configs` | Cấu hình vai trò Agent tùy biến theo từng stage của từng kênh cụ thể. |
| `projects` | Mỗi lần bấm "Bắt Đầu Quy Trình" = tạo 1 project mới. Lưu lịch sử toàn bộ các lần tạo video. |
| `project_stages` | Kết quả đầu ra của từng stage (script, visual, image, voice, editor) thuộc một project. |
| `media_files` | Metadata của file ảnh/âm thanh được tạo ra, liên kết với stage tương ứng. |

### Quản lý Migration (Alembic)

Khi thêm hoặc sửa cột trong models, sinh migration tự động:

```bash
# Sinh file migration tự động
.\venv\Scripts\alembic revision --autogenerate -m "Mô tả thay đổi"

# Áp dụng migration lên DB
.\venv\Scripts\alembic upgrade head

# Xem lịch sử migration
.\venv\Scripts\alembic history
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
