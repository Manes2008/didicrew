# Kế hoạch thực hiện - Tái cấu trúc mã nguồn VideoCrew

Dưới đây là sơ đồ cấu trúc thư mục mới đề xuất để tối ưu hóa hiệu suất, tăng tính mô đun và độ linh hoạt cho hệ thống VideoCrew.

## Đề xuất Cấu trúc Thư mục Mới

Chúng ta sẽ chuyển mã nguồn chính vào thư mục `src/`, đồng thời tách biệt cấu hình prompts/agents ra file YAML ngoài:

```text
videocrew/
├── config/
│   ├── agents.yaml          # Định nghĩa role, goal, backstory, model cho từng Agent
│   └── pipeline.yaml        # Thứ tự chạy các stage và mô tả task
├── generated_images/        # Thư mục lưu ảnh đã tạo
├── src/
│   ├── __init__.py
│   ├── agents/
│   │   ├── __init__.py
│   │   └── factory.py       # Đọc config/agents.yaml để khởi tạo Agent động
│   ├── tools/
│   │   ├── __init__.py
│   │   └── image_tool.py    # Xử lý sinh ảnh, giải mã base64 và lưu local
│   ├── core/
│   │   ├── __init__.py
│   │   ├── engine.py        # Pipeline Runner điều phối các stage chạy tuần tự
│   │   └── llm_provider.py  # Khởi tạo đối tượng LLM (OpenAI, Gemini, Anthropic) từ UI
│   └── utils/
│       ├── __init__.py
│       └── helpers.py       # Các hàm tiện ích (lưu file, log, format dữ liệu)
├── .env                     # Lưu API Keys bảo mật
├── .gitignore
├── app.py                   # UI Streamlit mỏng (chỉ nhận input, gọi engine, hiển thị kết quả)
├── requirements.txt
└── README.md
```

---

## Chi tiết các thành phần chính trong kiến trúc mới

### 1. `config/agents.yaml` (Quản lý Prompt & Model tập trung)
Định nghĩa tất cả các agent trong một file cấu hình duy nhất:
```yaml
script_writer:
  role: "Senior Script Writer"
  goal: "Viết kịch bản TikTok/Reel 25-30s hấp dẫn"
  backstory: "Chuyên gia viết content TikTok về bé gái đáng yêu..."
  temperature: 0.75

image_generator:
  role: "Image Generation Specialist"
  goal: "Tạo prompt và sinh hình ảnh"
  backstory: "Chuyên gia thiết kế prompt hình ảnh bé gái..."
  temperature: 0.8
  tools: ["generate_gpt_image"]
```

### 2. `src/core/llm_provider.py` (Linh hoạt thay thế Model)
Khởi tạo LLM phù hợp dựa trên lựa chọn từ giao diện UI:
```python
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI

def get_llm(provider: str, model_name: str, api_key: str, temperature: float = 0.7):
    if provider == "OpenAI":
        return ChatOpenAI(model=model_name, api_key=api_key, temperature=temperature)
    elif provider == "Google (Gemini)":
        return ChatGoogleGenerativeAI(model=model_name, google_api_key=api_key, temperature=temperature)
    # Dễ dàng thêm Claude, Ollama... vào đây
    raise ValueError(f"Không hỗ trợ provider: {provider}")
```

### 3. `src/tools/image_tool.py` (Sửa lỗi lưu ảnh local)
Tool tự lưu ảnh thay vì trả base64 thô về cho LLM:
```python
import base64
import time
import os
from PIL import Image
from io import BytesIO
from crewai.tools import tool
from openai import OpenAI

@tool("genimage")
def generate_gpt_image(prompt: str) -> str:
    """Tạo hình ảnh bằng API và tự động lưu về máy local."""
    try:
        client = OpenAI()
        response = client.images.generate(
            model="gpt-image-1-mini",
            prompt=prompt[:4000],
            size="1024x1024",
            quality="medium",
            n=1,
        )
        b64_data = response.data[0].b64_json
        
        # Giải mã và lưu
        img_data = base64.b64decode(b64_data)
        img = Image.open(BytesIO(img_data))
        
        os.makedirs("generated_images", exist_ok=True)
        file_path = f"generated_images/image_{int(time.time())}.png"
        img.save(file_path)
        
        return f"📁 Đường dẫn ảnh: {file_path}"
    except Exception as e:
        return f"ERROR: {str(e)}"
```

---

## Ý kiến từ người dùng

> [!IMPORTANT]
> Phương pháp hiện tại trả dữ liệu base64 trực tiếp cho LLM Agent bị lỗi do chuỗi base64 quá dài vượt quá giới hạn token đầu ra của LLM. Thay đổi tool `generate_gpt_image` để tự giải mã và lưu ảnh tại máy local rồi trả về đường dẫn file sẽ giải quyết triệt để lỗi này.

## Câu hỏi thảo luận

> [!IMPORTANT]
> 1. **Cấu trúc mới**: Bạn có muốn chuyển đổi toàn bộ cấu trúc hiện tại sang cấu trúc thư mục mới (`src/`, `config/`) như đề xuất ở trên không?
> 2. **Xác thực dữ liệu đầu vào**: Bạn có muốn thêm kiểm tra hợp lệ cho các ô nhập liệu không? Ví dụ:
>    - Kiểm tra `openai_key` phải đúng định dạng key OpenAI (bắt đầu bằng `sk-` hoặc không để trống).
>    - Kiểm tra ý tưởng video `idea` phải dài ít nhất 10 ký tự để đảm bảo đủ ngữ cảnh viết kịch bản.
> 3. **Tích hợp Gemini/Claude**: Dự án hiện tại đang dùng thư viện `langchain_openai`. Nếu bạn muốn dùng thêm Gemini hoặc Claude, chúng ta cần cài đặt thêm các gói thư viện tương ứng (`langchain-google-genai`, `langchain-anthropic`). Bạn có đồng ý cài đặt thêm không?

---

## Kế hoạch kiểm thử

### Kiểm thử tự động
- Chạy file `app1.py` hoặc script test riêng để kiểm tra tool `generate_gpt_image` có lưu ảnh và trả về đúng đường dẫn.

### Kiểm thử thủ công
- Chạy Streamlit app: `streamlit run app.py`.
- Thực hiện qua các bước từ 1 đến 5 để đảm bảo mọi stage hoạt động và ảnh hiển thị đúng tại stage 3.

---

## Phân tích Vai trò & Chức năng của 5 file Agents

Các file agent trong thư mục `agents/` đóng vai trò là các tác nhân chuyên biệt được điều phối bởi CrewAI để thực hiện các nhiệm vụ riêng lẻ trong quy trình sản xuất video:

1. **`script.py` (Senior Script Writer)**:
   - **Nhiệm vụ**: Nhận ý tưởng thô từ người dùng và biên soạn thành một kịch bản ngắn (25-30 giây) phù hợp cho nền tảng video ngắn (TikTok/Reel).
   - **Đặc trưng**: Kịch bản được định hình có cấu trúc rõ ràng bao gồm lời thoại dễ thương phong cách bé gái tiểu thư, phần hook lôi cuốn ở đầu và thời gian timing cụ thể.
2. **`visual.py` (Visual Prompt Engineer)**:
   - **Nhiệm vụ**: Chuyển đổi kịch bản bằng chữ thành các mô tả hình ảnh/video chi tiết (Prompts) để làm đầu vào cho các mô hình sinh ảnh/video (Kling AI, Leonardo AI, v.v.).
   - **Đặc trưng**: Tạo ra các câu lệnh tối ưu, có tham chiếu phong cách nhân vật nhất quán (Character Reference) để đảm bảo hình ảnh đầu ra đồng bộ.
3. **`image.py` (Image Generation Specialist)**:
   - **Nhiệm vụ**: Sử dụng API OpenAI (`gpt-image-1-mini` hoặc phiên bản cao hơn) để trực tiếp tạo ảnh từ prompts hình ảnh đã phân tích.
   - **Đặc trưng**: Sử dụng tool tích hợp (`genimage`) để giao tiếp với API sinh ảnh. (Cần được sửa đổi để tự động lưu ảnh tại local thay vì trả về chuỗi base64 thô).
4. **`voice.py` (Voiceover Specialist)**:
   - **Nhiệm vụ**: Soạn thảo kịch bản lồng tiếng chính xác cho giọng đọc của bé gái và đưa ra cấu hình thông số giọng đọc tối ưu trên ElevenLabs (hoặc các nền tảng TTS tương tự).
5. **`editor.py` (Video Editor)**:
   - **Nhiệm vụ**: Lập kế hoạch và hướng dẫn dựng phim chi tiết trong CapCut, bao gồm cách ghép các cảnh, chèn giọng đọc, nhạc nền, hiệu ứng chuyển cảnh và phụ đề tự động.

---

## Kế hoạch triển khai Script Run, Deploy, CI/CD và Bản quyền (MIT License)

Để hoàn thiện dự án và chuyển giao thuận tiện, chúng ta sẽ xây dựng các tài nguyên hỗ trợ sau:

### 1. Scripts Khởi chạy và Triển khai (Run & Deploy Scripts)
- **Khởi chạy cục bộ (`run.bat` / `run.sh`)**:
  - Tự động kiểm tra và kích hoạt môi trường ảo Python (`venv`).
  - Cài đặt/cập nhật thư viện từ `requirements.txt`.
  - Khởi chạy ứng dụng Streamlit (`streamlit run app.py`).
- **Triển khai bằng Docker (`Dockerfile` / `docker-compose.yml`)**:
  - Đóng gói mã nguồn cùng các thư viện cần thiết vào một container nhẹ chạy Python 3.11-slim.
  - Cấu hình port Streamlit mặc định `8501`.
  - Tạo mount volume cho thư mục `generated_images/` để đảm bảo ảnh không bị mất khi container khởi động lại.

### 2. Tự động hóa CI/CD (GitHub Actions)
- Tạo file `.github/workflows/deploy.yml` để thực hiện:
  - Kiểm tra cú pháp mã nguồn (Linting) bằng Flake8.
  - Tự động chạy các bài kiểm thử cơ bản (nếu có).
  - Tự động đóng gói và đẩy Docker image lên Docker Hub hoặc GitHub Container Registry khi có bản cập nhật trên nhánh `main`.

### 3. MIT License & Tiêu đề bản quyền (MIT License Header)
- Tạo file `LICENSE` trong thư mục gốc của dự án với nội dung Giấy phép MIT thương mại tự do.
- Bổ sung tiêu đề chú thích bản quyền MIT ở đầu mỗi file mã nguồn chính.

