# src/core/video_generator.py
import os
import time
import requests
import base64
from urllib.parse import urlparse
from PIL import Image
import io
import config

def generate_video_func(prompt: str, image_path: str = None) -> str:
    """
    Tạo video bằng Pollo AI (Minimax Hailuo 02) và tải về máy local.
    Ảnh đầu vào sẽ được resize và nén để đảm bảo kích thước base64 < 1MB.
    """
    try:
        api_key = config.POLLO_API_KEY
        if not api_key:
            return "ERROR: Thieu POLLO_API_KEY trong moi truong. Vui long cau hinh API Key de tao video."

        url = "https://pollo.ai/api/platform/generation/minimax/minimax-hailuo-02"
        headers = {
            "Content-Type": "application/json",
            "x-api-key": api_key
        }

        # Payload cơ bản
        data = {
            "input": {
                "prompt": prompt[:2000]  # giới hạn độ dài prompt
            }
        }

        # Xử lý ảnh nếu có
        if image_path and os.path.exists(image_path):
            try:
                # Mở ảnh
                img = Image.open(image_path)
                
                # Chuyển sang RGB nếu có kênh alpha (RGBA, P, LA)
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                
                # Resize về tối đa 1024px (giữ tỉ lệ)
                max_size = 1024
                if max(img.size) > max_size:
                    img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
                
                # Nén lần 1: chất lượng 85%, định dạng JPEG
                buffer = io.BytesIO()
                img.save(buffer, format='JPEG', quality=85, optimize=True)
                img_bytes = buffer.getvalue()
                
                # Nếu vẫn > 700KB (để base64 ~ 930KB), giảm chất lượng xuống 60
                if len(img_bytes) > 700 * 1024:
                    buffer = io.BytesIO()
                    img.save(buffer, format='JPEG', quality=60, optimize=True)
                    img_bytes = buffer.getvalue()
                
                # Mã hóa base64
                b64_string = base64.b64encode(img_bytes).decode('utf-8')
                data["input"]["image_url"] = f"data:image/jpeg;base64,{b64_string}"
                
            except Exception as ex:
                # Nếu lỗi xử lý ảnh, vẫn tiếp tục với prompt (bỏ qua ảnh)
                print(f"[WARN] Không thể xử lý ảnh {image_path}: {ex}")
                # Không gửi ảnh
                pass

        # Gửi request tạo task
        response = requests.post(url, headers=headers, json=data)

        # Xử lý lỗi 403 (hết tiền)
        if response.status_code == 403:
            try:
                resp_json = response.json()
                if "insufficient" in resp_json.get("message", "").lower():
                    return "ERROR: Tài khoản Pollo AI của bạn đã hết tiền (Insufficient balance). Vui lòng nạp thêm tiền để tiếp tục tạo video."
            except:
                pass

        if response.status_code != 200:
            return f"ERROR: Không thể khởi tạo task tạo video. HTTP {response.status_code} - {response.text}"

        resp_json = response.json()
        if "data" not in resp_json or "id" not in resp_json["data"]:
            return f"ERROR: Phản hồi API không có Task ID. Phản hồi: {response.text}"

        task_id = resp_json["data"]["id"]
        poll_url = f"https://pollo.ai/api/platform/generation/tasks/{task_id}"

        # Polling cho đến khi hoàn thành
        max_attempts = 60  # 60 * 5s = 300s (5 phút)
        for i in range(max_attempts):
            time.sleep(5)
            poll_resp = requests.get(poll_url, headers=headers)
            if poll_resp.status_code == 200:
                poll_data = poll_resp.json()
                status = poll_data.get("data", {}).get("status")
                
                if status == "success":
                    video_url = poll_data["data"]["output"]["video_url"]
                    if not video_url:
                        return "ERROR: Tạo video thành công nhưng không tìm thấy video_url."
                    
                    # Tải video về local
                    vid_response = requests.get(video_url, stream=True)
                    if vid_response.status_code == 200:
                        os.makedirs("generated_videos", exist_ok=True)
                        file_name = f"video_{int(time.time())}.mp4"
                        file_path = os.path.join("generated_videos", file_name)
                        
                        with open(file_path, "wb") as f:
                            for chunk in vid_response.iter_content(chunk_size=8192):
                                f.write(chunk)
                        return f"📁 Đường dẫn video: {file_path}"
                    else:
                        return f"ERROR: Không thể tải video từ URL: {video_url}"
                
                elif status == "failed":
                    error_msg = poll_data.get("data", {}).get("error", "Unknown error")
                    return f"ERROR: Tạo video thất bại trên Pollo AI. Lỗi: {error_msg}"
            
        return "ERROR: Quá thời gian chờ (Timeout) khi tạo video. Vui lòng thử lại sau."
            
    except Exception as e:
        return f"ERROR: Lỗi hệ thống: {str(e)}"