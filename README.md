# VideoCrew Studio — AI Video Production Platform

> **Nền tảng tự động sản xuất nội dung video ngắn (TikTok/Reels) bằng AI — từ ý tưởng đến video hoàn chỉnh.**

Được xây dựng trên **CrewAI** + **OpenAI** + **Streamlit**, hệ thống điều phối 5 AI Agent chuyên biệt chạy tuần tự, kết quả của stage trước là đầu vào của stage tiếp theo. Mọi dự án được lưu trữ vào **PostgreSQL**, cho phép tiếp tục công việc bất kỳ lúc nào.

---

## Tính năng chính

### Pipeline 5 Stage tự động

| Stage | Tên | AI Agent | Mô tả |
| :---: | :--- | :--- | :--- |
| **1** | Viết Kịch Bản | Senior Script Writer | Nhận ý tưởng → Viết kịch bản TikTok 25-30s hoàn chỉnh (hook, lời thoại, timing) |
| **2** | Tạo Prompt Hình Ảnh | Visual Prompt Engineer | Nhận kịch bản → Tạo prompt hình ảnh chi tiết (phong cách, nhân vật, bối cảnh) |
| **3** | Tạo Hình Ảnh | Image Generation | Nhận prompt → Gọi API gpt-image-2 → Lưu ảnh local → Hiển thị trực tiếp |
| **4** | Tạo Voiceover | Voiceover Specialist | Nhận kịch bản → Soạn text voiceover + cấu hình giọng đọc ElevenLabs |
| **5** | Tạo Video AI | Video Editor | Nhận tất cả nguyên liệu → Gọi API Pollo AI (Minimax Hailuo 02) → Tải video về local |

### Quản lý Kênh & Dự án

- **Đa kênh**: Tạo và quản lý nhiều kênh nội dung (Bé Tiểu Thư, Ẩm thực, Du lịch...), mỗi kênh có mục tiêu, phong cách riêng
- **Lưu lịch sử**: Mỗi lần bấm "Bắt Đầu" tạo ra 1 Project, toàn bộ kết quả từng stage được lưu vào DB
- **Tiếp tục dang dở**: Chọn dự án cũ từ sidebar → hệ thống tự động khôi phục đúng stage đang làm
- **Regenerate**: Bấm lại để tạo kết quả mới cho bất kỳ stage nào

### Thanh tiến trình điều hướng (Step Navigator)

- Hiển thị 5 bước **1 → 2 → 3 → 4 → 5** dạng nút bấm ở đầu màn hình
- **Click vào stage đã hoàn thành** → nhảy về xem lại / chỉnh sửa ngay lập tức
- Stage chưa hoàn thành hiển thị tooltip lý do bị khóa
- Trạng thái trực quan: `▶` Đang chạy | `✅` Đã xong | `⏳` Chưa mở khóa

### Hiển thị kết quả thông minh

- **Script / Visual / Voice**: Render Markdown đầy đủ (bold, header, list) thay vì raw text
- Nút **"Xem raw text / Copy"** để lấy nội dung gốc khi cần
- **Image stage**: Hiển thị ảnh trực tiếp trong giao diện, kèm đường dẫn lưu local
- **Video stage**: Phát video trực tiếp trong giao diện, tải về từ Pollo AI

### Hỗ trợ đa LLM

Chọn nhà cung cấp LLM trực tiếp trên sidebar:

| Nhà cung cấp | Model hỗ trợ |
| :--- | :--- |
| **OpenAI** | `gpt-4o-mini`, `gpt-4o`, `gpt-3.5-turbo` |
| **Google Gemini** | `gemini-1.5-flash`, `gemini-1.5-pro` |

### Sinh ảnh với Fallback tự động

| Model | Ưu tiên | Ghi chú |
| :--- | :---: | :--- |
| `gpt-image-2` | Chinh | Chat luong cao nhat |
| `gpt-image-1-mini` | Fallback | Tu dong dung khi gpt-image-2 khong kha dung |

Nếu cả hai đều lỗi, hệ thống trả về thông báo hướng dẫn chi tiết thay vì crash.

---

## Kien truc he thong

```
videocrew/
├── config/
│   ├── agents.yaml          # Dinh nghia role, goal, backstory cho tung Agent
│   └── tasks.yaml           # Mo ta nhiem vu va dau ra ky vong cho tung stage
├── generated_images/        # Thu muc luu anh duoc tao (auto-created)
├── generated_videos/        # Thu muc luu video duoc tao (auto-created)
├── migrations/              # Alembic migration scripts
├── src/
│   ├── agents/
│   │   └── factory.py       # AgentFactory: khoi tao CrewAI Agent dong tu config YAML
│   ├── tools/
│   │   ├── image_tool.py    # Sinh anh: gpt-image-2 → fallback gpt-image-1-mini
│   │   └── video_tool.py    # Sinh video: Pollo AI (Minimax Hailuo 02), polling pattern
│   └── core/
│       ├── engine.py        # WorkflowEngine: dieu phoi 5 stage, Crew.kickoff()
│       ├── llm_provider.py  # Khoi tao LLM linh hoat (OpenAI / Google Gemini)
│       └── models.py        # SQLAlchemy ORM Models + init_db() tu dong tao bang
├── .env                     # API Keys & DATABASE_URL (khong commit len git)
├── alembic.ini
├── app.py                   # Giao dien Streamlit (UI, dieu phoi, hien thi ket qua)
├── config.py                # Load .env + tu dong chuyen doi Render DB URL
├── Dockerfile
├── docker-compose.yml
├── run.bat                  # Script khoi chay nhanh Windows
├── run.sh                   # Script khoi chay nhanh Linux/macOS
└── requirements.txt
```

---

## Co so Du lieu (Database)

### So do quan he (ERD)

```
channels
├── id (PK)
├── name (UNIQUE, NOT NULL)
├── description
├── goal (NOT NULL)
├── created_at / updated_at
│
├──< channel_stage_configs
│    ├── id (PK)
│    ├── channel_id (FK)
│    ├── stage_name            # script | visual | image | voice | video
│    ├── role / goal / backstory
│    └── markdown_template
│
└──< projects
     ├── id (PK)
     ├── channel_id (FK)
     ├── idea (NOT NULL)
     ├── provider / model_name
     ├── current_stage
     ├── status                # pending | running | completed
     ├── created_at / updated_at
     │
     └──< project_stages
          ├── id (PK)
          ├── project_id (FK)
          ├── stage_name
          ├── result_content (TEXT)
          ├── media_path        # Duong dan file anh/video
          ├── status            # pending | completed | failed
          ├── created_at / updated_at
          │
          └──< media_files
               ├── id (PK)
               ├── project_stage_id (FK)
               ├── file_name / file_path
               ├── mime_type    # image/png | video/mp4
               ├── file_size (BIGINT)
               ├── duration_seconds
               ├── status       # active | deleted
               └── created_at
```

### Cau hinh ket noi

Khai bao trong file `.env`:

```env
# Local PostgreSQL
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/videocrew

# Render PostgreSQL (external)
DATABASE_URL=postgresql://user:password@dpg-xxxxxx-a.singapore-postgres.render.com/dbname
```

He thong **tu dong phat hien** va chuyen doi Render Internal URL thanh External URL khi chay local.
Cac bang duoc **tao tu dong** qua `init_db()` khi khoi chay lan dau.

### Quan ly Migration (Alembic)

```bash
# Sinh file migration
.\venv\Scripts\alembic revision --autogenerate -m "Mo ta thay doi"

# Ap dung migration
.\venv\Scripts\alembic upgrade head

# Xem lich su
.\venv\Scripts\alembic history
```

---

## Thiet ke toi uu hoa chi phi

### Stage 3 (Hinh Anh) — Bypass Agent

Stage sinh anh **bo qua CrewAI Agent**, goi truc tiep Python:

```python
if stage_name == "image":
    from src.tools.image_tool import generate_gpt_image_func
    return generate_gpt_image_func(prompt)
```

Tiet kiem 3,000-8,000 tokens/lan, toc do nhanh hon 5-10 lan, tranh loi LLM tu choi goi tool.

### Stage 5 (Video) — Polling pattern

1. Submit task → nhan `task_id`
2. Poll moi 5 giay toi da 60 lan (5 phut)
3. Khi `status == "success"` → tai file `.mp4` ve `generated_videos/`

Anh dau vao duoc resize + nen JPEG tu dong (base64 < 1MB) truoc khi gui API.

### Stage 1, 2, 4 — CrewAI Crew.kickoff()

Chay qua `Crew([agent], tasks=[task]).kickoff()`, tuong thich moi version CrewAI >= 0.1.

### Bao ve session timeout

Neu phien lam viec het han, he thong hien thong bao than thien thay vi crash:
> "Phien lam viec da het han. Vui long chon lai du an o sidebar."

---

## Cai dat va Chay

### Yeu cau

- Python 3.10+
- PostgreSQL
- **OpenAI API Key** — LLM va sinh anh (`gpt-image-2`)
- **Google Gemini API Key** — tuy chon
- **Pollo AI API Key** — tao video (Minimax Hailuo 02)

### 1. Cai dat thu cong

```bash
git clone https://github.com/Manes2008/didicrew.git
cd didicrew
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Tao file `.env`:

```env
OPENAI_API_KEY=sk-proj-...
GEMINI_API_KEY=AIza...
POLLO_API_KEY=...
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/videocrew
```

Khoi chay:

```bash
streamlit run app.py
```

### 2. Khoi chay nhanh (Windows)

```bat
.\run.bat
```

Script tu dong: kiem tra Python → kich hoat venv → cai thu vien → chay Streamlit.

### 3. Docker

```bash
docker-compose up --build
```

Truy cap tai: `http://localhost:8501`

---

## Huong dan su dung

### Tao du an moi

1. Sidebar → chon **Nha cung cap LLM** va **Model**
2. Sidebar → chon **Kenh**
3. Sidebar → chon **"-- Tao du an moi --"**
4. Nhap **y tuong video** vao o text area
5. Bam **"Bat Dau Quy Trinh"**
6. Lan luot bam **"Chay ..."** cho tung stage
7. Sau moi stage: **Approve & Tiep tuc** | **Regenerate** | **Quay lai**

### Tiep tuc du an cu

1. Sidebar → chon du an tu danh sach
2. He thong tu khoi phuc stage + ket qua da co
3. Thanh tien trinh **1→5** — **click de xem lai bat ky stage nao da xong**

---

## Huong dan lap trinh (Goi truc tiep tu Python)

```python
from src.core.llm_provider import get_llm
from src.core.engine import run_stage

llm = get_llm(provider="OpenAI", model_name="gpt-4o-mini", api_key="YOUR_KEY")
idea = "Be gai mac vay hong cam on me"

script_result  = run_stage("script", idea, llm=llm)
visual_result  = run_stage("visual", idea, previous_result=script_result, llm=llm)
image_result   = run_stage("image",  idea, previous_result=visual_result)
voice_result   = run_stage("voice",  idea, previous_result=script_result, llm=llm)

all_results = {"script": script_result, "visual": visual_result, "image": image_result}
video_result   = run_stage("video",  idea, all_results=all_results)
```

---

## License

MIT License — Copyright (c) 2026 Manes2008/didicrew
