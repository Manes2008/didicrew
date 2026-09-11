# VideoCrew Studio — AI Creative Director & Media Automation Engine

[![Python Version](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-15.0-000000?style=for-the-badge&logo=nextdotjs&logoColor=white)](https://nextjs.org)
[![OpenSpace Ecosystem](https://img.shields.io/badge/OpenSpace-Cloud_v2-8A2BE2?style=for-the-badge)](https://github.com/HKUDS/OpenSpace)
[![Playwright](https://img.shields.io/badge/Playwright-Automation-2EAD33?style=for-the-badge&logo=playwright&logoColor=white)](https://playwright.dev)
[![Docker Ready](https://img.shields.io/badge/Docker-Container_Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)

> **Tổ hợp Biên kịch, Đạo diễn & Tự động hóa Sản xuất Video Điện ảnh ứng dụng Trí tuệ Nhân tạo thế hệ mới.**

VideoCrew Studio không đơn thuần là một công cụ sinh video tự động; hệ thống đóng vai trò như một **Tổng đạo diễn AI (The AI Showrunner)**. Dự án giải quyết triệt để bài toán lớn nhất của việc sáng tạo video AI: **Thổi linh hồn nghệ thuật kể chuyện (Storytelling), ứng dụng tâm lý học giữ chân người xem (Retention Hooks) và tự động hóa kết nối 1-click vào Google Flow (Veo & Voiceover Studio)**.

---

## 1. Dinh Vi & Su Menh Chuyen Doi

Hầu hết các công cụ AI hiện nay chỉ tập trung vào việc render hình ảnh hoặc video thô, dẫn đến các kịch bản vô hồn, sáo rỗng và tỷ lệ thoát video cao sau 3 giây đầu. VideoCrew Studio định vị là **Bộ não Sáng tạo Cốt lõi**:

* **Đạo diễn Điện ảnh & Tâm lý Khán giả**: Áp dụng các cấu trúc kịch bản đỉnh cao (Mô thức Hook nghịch lý, tương phản số liệu, vòng lặp tò mò), đo lường chính xác nhịp thở (~3.0 - 3.3 từ/giây) tương thích với âm thanh đọc TTS.
* **Tích hợp Tri thức OpenSpace Cloud**: Nạp động 16 kỹ năng chuyên gia từ nền tảng OpenSpace của HKUDS, loại bỏ 100% văn phong sáo ngữ máy móc.
* **Cộng sinh với Big Tech**: Không cố gắng tự render video nặng nề trên máy cá nhân; VideoCrew tạo ra bản thiết kế phân cảnh (Director Blueprint) chuẩn xác và dùng Playwright tự động đẩy trực tiếp vào các cỗ máy GPU của Google Flow (Veo & Imagen 3).

---

## 2. Bang So Sanh Nang Luc He Thong

| Tieu Chi Danh Gia | Cong Cu AI Tong Quat / Flow Thuan Tuy | VideoCrew Studio Pipeline |
| :--- | :--- | :--- |
| **Tam ly hoc Hook 3 giay** | Khong co; mo dau cham rai, chung chung | Tu dong ap dung Mo thuc A/B chong drop-off |
| **Nhip do loi thoai** | Thoai tho cung, de tran chu khi long tieng | Tinh toan chinh xac ~3.0 tu/giay chuan video ngan |
| **Visual Prompt cho Video** | Mo ta so sai, de bi loi do tren Veo/Flow | Chuan hoa thuoc tinh camera 35mm, anh sang, goc quay |
| **Kiem dinh chat luong** | Phai tu doc va danh gia bang tay | Agent Content Quality Auditor tu cham diem rubric |
| **Thao tac voi Google Flow** | Copy-paste tung cau, chon giong thu cong | Playwright Automation Bridge tu dong hoa 1-click |
| **Giao dien Van hanh** | Phuc tap, mang tinh chat lap trinh vien | Next.js 15 Media Studio hien dai, truc quan |

---

## 3. Kien Truc Pipeline 8 Cong Doan

Hệ thống điều phối luồng sản xuất tuần tự qua 8 công đoạn chuyên môn hóa:

```
[ Ý TƯỞNG SƠ KHỞI ]
        │
        ▼
[ Stage 1: Phân Tích & Chiến Lược ] ──► (OpenSpace: content-strategy & gap-analysis)
        │
        ▼
[ Stage 2: Kịch Bản & Hook 3s ] ─────► (OpenSpace: cinematic-script-writer & viral-video)
        │
        ▼
[ Stage 3: Thẩm Định Chất Lượng ] ───► (OpenSpace: content-quality-auditor)
        │
        ▼
[ Stage 4: Storyboard 6 Cột ] ───────► (OpenSpace: storyboard & visual-vocabulary)
        │
        ▼
[ Stage 5: Chỉ Đạo Nghệ Thuật ] ─────► (OpenSpace: visual-prompt-engine & style-cards)
        │
        ▼
[ Stage 6: Lọc Sạch Dữ Liệu ] ───────► (Data Sanitizer: cat gon <120 ky tu, loc sach --ar)
        │
        ▼
[ Stage 7: Automation Bridge ] ──────► (Playwright Engine: ket noi Google Flow)
        │
        ▼
[ BẢN THIẾT KẾ HOÀN CHỈNH / VIDEO CLIP VEO ]
```

---

## 4. Danh Muc 16 Ky Nang Chuyen Sau Tu OpenSpace

Hệ thống nạp trực tiếp tri thức từ thư mục `skills/` đã được đồng bộ hóa từ OpenSpace Cloud:

### Nhom 1: Bien Kich & Chien Luoc Noi Dung
- `cinematic-script-writer`: Viết kịch bản chuẩn điện ảnh, tối ưu nhịp thở và cấu trúc Hook 3s.
- `storyboard`: Phân chia bảng phân cảnh 6 cột chi tiết (Visual, Voiceover, Text, SFX/BGM).
- `content-quality-auditor`: Đánh giá, chấm điểm và tự động chỉnh sửa kịch bản theo rubric khắt khe.
- `viral-video-analysis`: Phân tích xu hướng và tích hợp các yếu tố kích hoạt tương tác (CTA Trigger).
- `content-strategy`: Định hình thông điệp cốt lõi và chân dung khán giả mục tiêu.
- `content-gap-analysis`: Phát hiện khoảng trống thông tin để tạo sự khác biệt cạnh tranh.
- `content-refresher`: Tái cấu trúc và nâng cấp các chủ đề cũ thành góc nhìn mới.

### Nhom 2: Thi Giac & Chi Dao Nghe Thuat
- `visual-prompt-engine`: Chuyển hóa kịch bản thành câu lệnh prompt điện ảnh chuyên nghiệp.
- `visual-concept`: Xây dựng bảng moodboard và phong cách thị giác đồng nhất.
- `best-image-generation`: Tối ưu hóa chất lượng hình ảnh qua các tham số ánh sáng và chất liệu.
- `blip-2-vision-language`: Phân tích và kiểm soát tính nhất quán của nhân vật qua các khung hình.

### Nhom 3: Am Thanh & Long Tieng
- `elevenlabs-tts`: Tối ưu hóa tham số biểu cảm giọng đọc và ngắt nghỉ tự nhiên.
- `audio-conductor`: Điều phối âm lượng, nhạc nền (BGM) và hiệu ứng âm thanh (SFX).
- `audiocraft-audio-generation`: Tạo âm thanh nền tùy biến theo nhịp điệu video.
- `audio-processing`: Hậu kỳ, lọc tạp âm và cân bằng tần số âm thanh.

### Nhom 4: Video & Chuyen Dong
- `eachlabs-video-generation`: Tối ưu câu lệnh chuyển động camera cho AI Video Generators.
- `hyperframes`: Kiểm soát chuyển cảnh mượt mà giữa các phân đoạn video.

---

## 5. Co Che Tu Dong Hoa Google Flow (Playwright Bridge)

VideoCrew Studio cung cấp cầu nối tự động hóa độc quyền với Google Flow:

1. **Bộ lọc Dữ liệu Thông minh (Data Sanitizer)**:
   - Tự động bóc tách các nhãn vai đọc `[NARRATOR]:`, `[DIALOGUE]:` và số lượng từ `*(11 từ)*` để tránh việc AI đọc nhầm thành tiếng.
   - Tự động kiểm tra và chia nhỏ câu thoại không vượt quá 120 ký tự (giới hạn của Voiceover Studio).
   - Tự động loại bỏ các cờ lệnh không tương thích như `--ar 9:16` trong Prompt Veo.
   - Tự động ánh xạ giọng đọc thích hợp: **Alnilam** (trầm hùng lịch sử), **Charon** (công nghệ, đĩnh đạc), **Achird** (thân thiện, đời sống).

2. **Dedicated Profile Trình duyệt (`.chrome_profile`)**:
   - Sử dụng một profile Chrome riêng biệt, tránh hoàn toàn lỗi chiếm dụng file khi bạn đang mở Chrome cá nhân.
   - Đăng nhập tài khoản Google Flow một lần duy nhất; bot tự động duy trì phiên làm việc cho các lần sản xuất tiếp theo.

3. **Thao tác 1-Click trên Giao diện**:
   - Nhấp nút **"Đẩy Sang Google Flow"** ngay trên trang Sản Xuất để mở modal kiểm tra phân cảnh.
   - Bấm **"Bắt Đầu Đẩy Vào Flow"**, hệ thống sẽ tự mở dự án, nạp toàn bộ Veo prompts và tạo voiceover song song.

---

## 6. Huong Dan Cai Dat & Van Hanh

### Yeu Cau He Thong
- **Hệ điều hành**: Windows 10/11, macOS, hoặc Linux
- **Python**: Phiên bản 3.12 trở lên (Bắt buộc cho OpenSpace và Playwright)
- **Node.js**: Phiên bản 18+ (Dành cho giao diện Next.js 15)
- **Cơ sở dữ liệu**: PostgreSQL 16+

### Cach 1: Cai Dat & Chay Cuc Bo (Local Development)

1. **Clone repository và thiết lập môi trường ảo**:
```bash
git clone https://github.com/Manes2008/didicrew.git
cd didicrew
python -m venv venv
venv\Scripts\activate  # Tren Linux/macOS: source venv/bin/activate
```

2. **Cài đặt các gói phụ thuộc Backend**:
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m playwright install --with-deps chromium
```

3. **Cấu hình tệp môi trường (`.env`)**:
```env
OPENAI_API_KEY=your_openai_key
GEMINI_API_KEY=your_gemini_key
DATABASE_URL=postgresql+psycopg2://postgres:123456@localhost:5432/didicrew
OPENSPACE_API_KEY=your_openspace_key
GOOGLE_FLOW_PROJECT_URL=https://flow.google.com/project/your-project-id/tools
```

4. **Khởi chạy Backend (FastAPI)**:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

5. **Khởi chạy Giao diện Frontend (videocrew-ui)**:
```bash
cd videocrew-ui
npm install
npm run dev
```
Truy cập giao diện tại: `http://localhost:3000`

---

### Cach 2: Trien Khai Tron Goi Bang Docker (Docker Deployment)

Hệ thống đã được đóng gói sẵn sàng cho Docker với môi trường chuẩn Python 3.12:

```bash
# Khởi động toàn bộ Database và Backend qua Docker Compose
docker compose up -d --build

# Hoặc sử dụng script Redeploy an toàn (tự động giữ nguyên Database)
scripts\redeploy.bat
```

> [!TIP]
> Để mở trình duyệt Chrome độc lập cho Google Flow và đăng nhập sẵn tài khoản, bạn chỉ cần chạy tệp:
> `scripts\start_flow_chrome.bat`

---

## 7. Cau Truc Thu Muc Du An

```
videocrew/
├── config/
│   ├── agents.yaml             # Thiết lập vai trò & mục tiêu của các AI Agent
│   └── tasks.yaml              # Định nghĩa quy chuẩn nhiệm vụ và kết quả đầu ra
├── skills/                     # Kho 16 kỹ năng Studio gốc từ OpenSpace Cloud
│   ├── mass-media/             # Chiến lược kịch bản, SEO, phân tích viral
│   └── technology/             # Đạo diễn thị giác, prompt Veo, TTS, xử lý âm thanh
├── src/
│   ├── api/v1/endpoints/       # Các API endpoints FastAPI (Production, Config, Channels)
│   ├── core/
│   │   ├── engine.py           # WorkflowEngine điều phối tiêm kỹ năng OpenSpace động
│   │   ├── llm_provider.py     # Hỗ trợ Gemini 3.8 Flash, OpenAI o3-mini
│   │   └── skill_loader.py     # Bộ nạp kỹ năng đệ quy kèm in-memory cache
│   └── tools/
│       ├── google_flow_sanitizer.py # Bộ lọc làm sạch dữ liệu thoại và Veo prompt
│       ├── google_flow_bridge.py    # Trình điều khiển tự động hóa Playwright
│       └── image_tool.py            # Công cụ sinh ảnh dự phòng (Flux Realism, Gemini)
├── videocrew-ui/               # Giao diện Studio hiện đại (Next.js 15, TailwindCSS)
├── scripts/
│   ├── redeploy.bat            # Script build lại Docker an toàn dữ liệu
│   ├── start_flow_chrome.bat   # Mở Chrome Dedicated Profile cho Google Flow
│   └── sync_openspace.py       # Script đồng bộ kỹ năng từ OpenSpace Cloud
├── Dockerfile                  # Cấu hình container Python 3.12 + Playwright
├── docker-compose.yml          # Điều phối dịch vụ App và PostgreSQL
└── requirements.txt            # Danh sách gói phụ thuộc chuẩn Python 3.12+
```

---

## 8. Ban Quyen & Giay Phep

Dự án được phát triển và phát hành dưới giấy phép **MIT License**.
Bản quyền thuộc về **(c) 2026 Manes2008/didicrew**.
