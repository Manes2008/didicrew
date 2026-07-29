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


def generate_local_image_sd_func(prompt: str, use_gpu: bool = None) -> str:
    """
    Sinh anh local su dung Stable Diffusion v1.5 qua diffusers.
    Neu use_gpu la None, tu dong phat hien GPU qua torch.cuda.is_available().
    """
    try:
        import os
        import time
        import torch
        from diffusers import StableDiffusionPipeline
        import gc
        
        # Phat hien GPU neu khong chi dinh
        if use_gpu is None:
            use_gpu = torch.cuda.is_available()
            
        device = "cuda" if use_gpu else "cpu"
        # GPU thi dung float16 de tiet kiem VRAM, CPU thi bat buoc dung float32
        dtype = torch.float16 if use_gpu else torch.float32
        
        print(f"[LOG] Khoi tao Stable Diffusion v1.5 tren thiet bi: {device} | dtype: {dtype}")
        
        # Giai phong cache CUDA truoc khi chay
        if use_gpu:
            gc.collect()
            torch.cuda.empty_cache()
            
        model_id = "runwayml/stable-diffusion-v1-5"
        
        # Tải pipeline SD v1.5
        pipe = StableDiffusionPipeline.from_pretrained(
            model_id, 
            torch_dtype=dtype,
            low_cpu_mem_usage=True
        )
        
        # Cau hinh thiet bi va cac buoc toi uu hoa
        if use_gpu:
            pipe.to("cuda")
            if hasattr(pipe, "enable_attention_slicing"):
                pipe.enable_attention_slicing()
        else:
            pipe.to("cpu")
            
        # Tao thu muc luu tru
        os.makedirs("generated_images", exist_ok=True)
        
        # So buoc lay mau (steps): CPU chay 15 steps cho nhanh, GPU chay 30 steps chat luong tot hon
        num_inference_steps = 30 if use_gpu else 15
        
        # Sinh 1 anh chat luong cao de tranh tran bo nho
        image = pipe(prompt=prompt[:1024], num_inference_steps=num_inference_steps).images[0]
        
        file_path = f"generated_images/sd_image_{int(time.time())}.png"
        image.save(file_path)
        
        # Giai phong bo nho
        del pipe
        if use_gpu:
            gc.collect()
            torch.cuda.empty_cache()
            
        return f"📁 Đường dẫn ảnh: {file_path}"
        
    except ImportError:
        return "ERROR: Chưa cài đặt thư viện diffusers / transformers / torch. Vui lòng chạy: pip install diffusers transformers torch"
    except Exception as e:
        return f"ERROR: Lỗi khi sinh ảnh bằng Stable Diffusion local: {str(e)}"

