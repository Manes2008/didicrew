# MIT License
# Copyright (c) 2026 Manes2008/didicrew

import os
import base64
import time
import requests
from io import BytesIO
from PIL import Image
from openai import OpenAI
from crewai.tools import tool

def generate_gpt_image_func(prompt: str) -> str:
    """Hàm Python thuần túy để tạo hình ảnh bằng gpt-image-2 và tải về máy local."""
    try:
        # Sử dụng API Key của OpenAI được thiết lập trong môi trường
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            return "ERROR: Thieu OPENAI_API_KEY trong moi truong. Vui long cau hinh API Key de tao anh."

        # Chỉ định cứng base_url của OpenAI để tránh bị ghi đè bởi biến môi trường proxy
        client = OpenAI(api_key=api_key, base_url="https://api.openai.com/v1")
        
        try:
            # Thử tạo ảnh bằng gpt-image-2
            response = client.images.generate(
                model="gpt-image-2",
                prompt=prompt[:32000],
                size="1024x1024",
                quality="medium",
                n=1
            )
        except Exception as e2:
            # Nếu gpt-image-2 lỗi, tự động hạ cấp xuống gpt-image-1-mini
            try:
                response = client.images.generate(
                    model="gpt-image-1-mini",
                    prompt=prompt[:32000],
                    size="1024x1024",
                    quality="medium",
                    n=1
                )
            except Exception as e1:
                return (
                    f"ERROR: Khong the tao anh bang ca gpt-image-2 va gpt-image-1-mini.\n"
                    f"Loi gpt-image-2: {str(e2)}\n"
                    f"Loi gpt-image-1-mini: {str(e1)}\n"
                    f"Huong dan: Kiem tra lai tai khoan OpenAI va API Key cua ban."
                )

        # gpt-image-1/2 trả về b64_json mặc định
        b64_data = response.data[0].b64_json
        if not b64_data:
            return "ERROR: OpenAI khong tra ve du lieu anh."
        
        # Giải mã base64 thành bytes hình ảnh
        img_bytes = base64.b64decode(b64_data)
        img = Image.open(BytesIO(img_bytes))
        
        # Đảm bảo thư mục lưu trữ tồn tại
        os.makedirs("generated_images", exist_ok=True)
        file_path = f"generated_images/image_{int(time.time())}.png"
        img.save(file_path)
        
        return f"📁 Đường dẫn ảnh: {file_path}"
    except Exception as e:
        return f"ERROR: {str(e)}"

@tool("genimage")
def generate_gpt_image(prompt: str) -> str:
    """Tạo hình ảnh bằng dall-e-3, tự động tải về máy local và trả về đường dẫn file."""
    return generate_gpt_image_func(prompt)
