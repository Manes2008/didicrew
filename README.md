# VideoCrew Studio — AI Video Production Platform

> **Nền tảng tự động hóa sản xuất nội dung video ngắn (TikTok/Reels) bằng trí tuệ nhân tạo (AI) — từ ý tưởng sơ khởi đến sản phẩm video hoàn chỉnh.**

Được xây dựng trên sự kết hợp mạnh mẽ giữa **CrewAI** + **OpenAI/Gemini** + **Streamlit**, hệ thống điều phối 5 AI Agent chuyên biệt chạy tuần tự theo mô hình Pipeline (kết quả của bước trước làm đầu vào cho bước sau). Toàn bộ dự án và dữ liệu media (ảnh, video dưới dạng nhị phân) được lưu trữ trực tiếp vào cơ sở dữ liệu **PostgreSQL**, đảm bảo an toàn dữ liệu và khả năng khôi phục/tiếp tục làm việc linh hoạt trên mọi môi trường.

---

## 🚀 Các Tính Năng Vượt Trội Mới Cập Nhật

### 1. ⚙️ Tự Động Hóa Nạp Veo3 (Qua Mark-L Engine)
* **Xuất dữ liệu một click**: Hệ thống tự động đóng gói toàn bộ kịch bản, âm thanh lồng tiếng, hình ảnh phân cảnh từ dự án và nạp trực tiếp vào phần mềm Veo3.
* **Tự trị hoàn toàn (Self-contained)**: Module tự động hóa `computer_control` đã được tích hợp trực tiếp vào nhân dự án (không phụ thuộc repo ngoài).
* **Quét cửa sổ thực tế (PowerShell)**: Trước khi kích hoạt phím tắt giả lập, hệ thống quét tiến trình Windows bằng PowerShell để định vị chính xác cửa sổ phần mềm `Veo3` đang mở, ngăn chặn tình trạng phím tắt "ảo" khi phần mềm đích chưa chạy.

### 2. 🛡️ Cổng Xác Thực Auth Gate & Single-page App
* **Bảo mật tuyệt đối**: Loại bỏ chế độ khách tự điền API Key tùy tiện, thay thế bằng luồng **Đăng nhập & Đăng ký** đồng bộ hóa qua DB Postgres. Mật khẩu người dùng được mã hóa bằng thuật toán PBKDF2 sha256.
* **Đăng nhập Admin thông minh**: Quản trị viên chỉ cần nhập mã cấu hình `ADMIN_SECRET_KEY` (từ file `.env`) vào ô mật khẩu của form đăng nhập chuẩn.
* **Che dấu mã khoá Admin**: Tự động gán nhãn bảo mật dạng `Didicrew01`, `Didicrew02`... cho các thiết bị Admin và che dấu hoàn toàn chuỗi key thô trong DB và trên giao diện.
* **Giao diện không sidebar trống**: Hệ thống chuyển đổi hoàn chỉnh sang mô hình Single-page App (SPA), ẩn hoàn toàn thanh sidebar màu xám bên trái khi chưa đăng nhập, đem lại trải nghiệm sang trọng và tập trung.

### 3. 💾 Lưu Trữ Nhị Phân DB (Postgres LargeBinary)
* **Không mất dữ liệu vật lý**: Lưu trữ trực tiếp bytes dữ liệu của ảnh và video vào trường `file_data` trong bảng `MediaFile`.
* **Sẵn sàng cho Docker/Cloud**: Hỗ trợ deploy Docker mượt mà, client từ xa xem được ảnh/video stream trực tiếp từ database mà không gặp lỗi thiếu file vật lý local trên máy chủ.
* **Tự động Fallback**: Giao diện Streamlit ưu tiên stream binary từ DB, tự động fallback về file local nếu phát hiện dữ liệu cũ chưa migrate.

### 4. 🧠 Đa Dạng Hóa Engine Vẽ Ảnh & Sinh Video Local
* **Stable Diffusion v1.5 Local**: Hỗ trợ sinh ảnh trực tiếp trên thiết bị (CPU/GPU) của người dùng thay vì phụ thuộc hoàn toàn vào OpenAI DALL-E Cloud API.
* **Tránh tràn VRAM (CUDA OOM)**: Tối ưu hóa bộ nhớ khi dùng GPU (VAE float16, bật chế độ `expandable_segments` trong PyTorch).

---

## 🛠️ Pipeline 5 Stage Tự Động

| Bước | Tên Bước | AI Agent | Vai Trò & Hành Động |
| :---: | :--- | :--- | :--- |
| **1** | **Viết Kịch Bản** | Senior Script Writer | Nhận ý tưởng gốc → Tạo kịch bản TikTok/Reels 25-30s đầy đủ (tiêu đề, lời thoại, timing). |
| **2** | **Mô Tả Hình Ảnh** | Visual Prompt Engineer | Phân tích kịch bản → Biên soạn mô tả visual chi tiết từng phân cảnh cho AI vẽ. |
| **3** | **Tạo Hình Ảnh** | Image Generation | Bypass Agent chạy trực tiếp: Gọi API DALL-E 3 hoặc chạy Stable Diffusion v1.5 Local (CPU/GPU) → Lưu DB binary. |
| **4** | **Tạo Giọng Đọc** | Voiceover Specialist | Trích xuất lời thoại → Chuyển văn bản thành giọng đọc truyền cảm (TTS). |
| **5** | **Xuất Video** | Video Editor | Ghép nhạc nền, âm thanh lồng tiếng và chuỗi phân cảnh ảnh → Gọi Pollo AI (Minimax Hailuo 02) / Wan 2.1 Local để dựng video hoàn chỉnh. |

---

## 📁 Cấu Trúc Mã Nguồn Dự Án

```
videocrew/
├── config/
│   ├── agents.yaml          # Định nghĩa vai trò, mục tiêu, lịch sử cho AI Agent
│   └── tasks.yaml           # Định nghĩa các task và đầu ra kỳ vọng cho từng bước
├── src/
│   ├── agents/
│   │   └── factory.py       # Khởi tạo CrewAI Agent động từ file YAML cấu hình
│   ├── tools/
│   │   ├── image_tool.py    # Sinh ảnh: OpenAI DALL-E hoặc Stable Diffusion v1.5 Local
│   │   ├── video_tool.py    # Sinh video: Pollo AI (Minimax), Wan 2.1 Local, ghép nhạc
│   │   └── computer_control.py # Tự động hóa Mark-L giả lập phím chuột xuất Veo3
│   ├── core/
│   │   ├── engine.py        # WorkflowEngine điều phối quy trình 5 bước chạy tuần tự
│   │   ├── llm_provider.py  # Khởi tạo mô hình LLM linh hoạt (OpenAI / Google Gemini)
│   │   └── models.py        # Định nghĩa các ORM model SQLAlchemy (Postgres)
│   └── ui/
│       ├── styles.py        # Inject CSS tùy biến làm đẹp và responsive giao diện
│       ├── auth.py          # Xử lý Cổng đăng nhập & đăng ký kết nối DB
│       ├── sidebar.py       # Sidebar điều hướng tinh giản, hiển thị tài khoản gọn gàng
│       └── pages/
│           ├── production.py # Giao diện quy trình sản xuất video 5 bước chính
│           ├── channels.py  # Quản lý kênh nội dung & chỉnh sửa vai trò AI
│           ├── config.py    # Quản lý cấu hình API Keys, AI Models, Render Engines
│           └── ip_manager.py # Quản lý phê duyệt IP thiết bị & tài khoản của Admin
├── exports/                 # Nơi xuất dữ liệu phân cảnh tạm thời để nạp vào Veo3
├── generated_images/        # Thư mục lưu ảnh phân cảnh local
├── generated_videos/        # Thư mục lưu video thành phẩm local
├── migrations/              # Lịch sử các file migration của Alembic
├── .env                     # File chứa API Keys bảo mật & DATABASE_URL
├── alembic.ini              # Cấu hình công cụ quản lý DB migration
├── app.py                   # Điểm khởi chạy chính của Streamlit App (Routing, SPA)
├── config.py                # Xử lý môi trường và cấu hình
├── requirements.txt         # Danh sách thư viện phụ thuộc của dự án
└── run.bat                  # Script khởi động nhanh một chạm cho Windows
```

---

## 💾 Sơ Đồ Cơ Sở Dữ Liệu (Postgres ERD)

```
channels (Kênh nội dung)
├── id (PK)
├── name (UNIQUE, NOT NULL)
├── description
├── goal (NOT NULL)
│
├──< channel_stage_configs (Cấu hình vai trò AI từng kênh)
│    ├── id (PK)
│    ├── channel_id (FK)
│    ├── stage_name            # script | visual | image | voice | video
│    ├── role / goal / backstory
│    └── markdown_template
│
└──< projects (Dự án sản xuất)
     ├── id (PK)
     ├── channel_id (FK)
     ├── idea (NOT NULL)
     ├── provider / model_name
     ├── current_stage
     ├── status                # pending | running | completed
     │
     └──< project_stages (Các bước thực thi)
          ├── id (PK)
          ├── project_id (FK)
          ├── stage_name
          ├── result_content (TEXT)
          ├── media_path        # Đường dẫn file local
          ├── status            # pending | completed | failed
          │
          └──< media_files (Dữ liệu đa phương tiện nhị phân)
               ├── id (PK)
               ├── project_stage_id (FK)
               ├── file_name / file_path
               ├── file_data (LargeBinary - Lưu trữ bytes nhị phân trực tiếp)
               ├── mime_type    # image/png | video/mp4
               ├── file_size (BIGINT)
               └── created_at
```

---

## ⚡ Hướng Dẫn Cài Đặt & Khởi Chạy

### Yêu Cầu Hệ Thống
* Python 3.10+
* PostgreSQL Database
* Cài đặt phần mềm FFmpeg (nếu chạy local để ghép nhạc và video)

### Cài Đặt Các Bước
1. **Clone dự án về máy:**
   ```bash
   git clone https://github.com/Manes2008/didicrew.git
   cd didicrew
   ```
2. **Khởi tạo môi trường ảo:**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. **Cấu hình môi trường (`.env`):**
   Tạo file `.env` tại thư mục gốc và điền các khóa cần thiết:
   ```env
   OPENAI_API_KEY=sk-proj-...
   GEMINI_API_KEY=AIzaSy...
   POLLO_API_KEY=pollo_...
   DATABASE_URL=postgresql+psycopg2://postgres:123456@localhost:5432/didicrew
   ADMIN_SECRET_KEY=xR4q90gPLDGvU-VHra08adaK1BIqroR9qQ7l8boDNGw
   ```

### Khởi Chạy
* **Windows (Chạy nhanh một chạm):**
  ```powershell
  .\run.bat
  ```
* **Chạy thủ công bằng Streamlit:**
  ```bash
  streamlit run app.py
  ```

---

## 🤝 Bản Quyền (License)
Dự án được phân phối dưới giấy phép **MIT License**. Bản quyền thuộc về © 2026 Manes2008/didicrew.
