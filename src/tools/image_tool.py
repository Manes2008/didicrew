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

from concurrent.futures import ThreadPoolExecutor

def generate_gpt_image_func(prompt: str) -> str:
    """Hàm Python thuần túy để tạo hình ảnh bằng gpt-image-2 và tải về máy local (tạo song song 4 ảnh, loại bỏ chữ)."""
    try:
        # Sử dụng API Key của OpenAI được thiết lập trong môi trường
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            return "ERROR: Thieu OPENAI_API_KEY trong moi truong. Vui long cau hinh API Key de tao anh."

        # Thêm chỉ thị loại bỏ chữ/text
        no_text_suffix = ", absolutely NO text, NO words, NO letters, NO signs, NO watermark, NO logo, NO labels, pure visual scene"
        refined_prompt = f"{prompt[:30000]}{no_text_suffix}"

        # Chỉ định cứng base_url của OpenAI để tránh bị ghi đè bởi biến môi trường proxy
        client = OpenAI(api_key=api_key, base_url="https://api.openai.com/v1")
        
        def generate_single_image(idx: int) -> str:
            try:
                try:
                    # Thử tạo ảnh bằng gpt-image-2
                    response = client.images.generate(
                        model="gpt-image-2",
                        prompt=refined_prompt,
                        size="1024x1024",
                        quality="medium",
                        n=1
                    )
                except Exception as e2:
                    # Nếu gpt-image-2 lỗi, tự động hạ cấp xuống gpt-image-1-mini
                    try:
                        response = client.images.generate(
                            model="gpt-image-1-mini",
                            prompt=refined_prompt,
                            size="1024x1024",
                            quality="medium",
                            n=1
                        )
                    except Exception as e1:
                        return f"ERROR_IDX_{idx}: gpt-image-2: {str(e2)} | gpt-image-1-mini: {str(e1)}"
                
                # gpt-image-1/2 trả về b64_json mặc định
                b64_data = response.data[0].b64_json
                if not b64_data:
                    return f"ERROR_IDX_{idx}: OpenAI khong tra ve du lieu anh."
                
                # Giải mã base64 thành bytes hình ảnh
                img_bytes = base64.b64decode(b64_data)
                img = Image.open(BytesIO(img_bytes))
                
                # Đảm bảo thư mục lưu trữ tồn tại
                os.makedirs("generated_images", exist_ok=True)
                file_path = f"generated_images/image_{int(time.time())}_{idx}.png"
                img.save(file_path)
                
                return file_path
            except Exception as e:
                return f"ERROR_IDX_{idx}: {str(e)}"

        # Tạo song song 4 ảnh bằng ThreadPoolExecutor
        num_images = 4
        with ThreadPoolExecutor(max_workers=num_images) as executor:
            results = list(executor.map(generate_single_image, range(num_images)))

        file_paths = []
        errors = []
        for r in results:
            if r.startswith("ERROR_IDX_"):
                errors.append(r)
            else:
                file_paths.append(r)

        if not file_paths:
            return f"ERROR: Khong the tao bat ky anh nao. Chi tiet:\n" + "\n".join(errors)

        output_lines = [f"📁 Đường dẫn ảnh: {fp}" for fp in file_paths]
        if errors:
            output_lines.append(f"[WARN] Mot so anh bi loi khi tao:\n" + "\n".join(errors))
        return "\n".join(output_lines)

    except Exception as e:
        return f"ERROR: {str(e)}"

@tool("genimage")
def generate_gpt_image(prompt: str) -> str:
    """Tạo hình ảnh bằng dall-e-3, tự động tải về máy local và trả về đường dẫn file."""
    return generate_gpt_image_func(prompt)
