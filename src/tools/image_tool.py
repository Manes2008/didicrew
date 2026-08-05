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
    """Hàm Python thuần túy để tạo hình ảnh bằng gpt-image-2 và tải về máy local cho tất cả các cảnh, có cơ chế retry khi cạn quota."""
    try:
        # Sử dụng API Key của OpenAI được thiết lập trong môi trường
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            return "ERROR: Thieu OPENAI_API_KEY trong moi truong. Vui long cau hinh API Key de tao anh."

        # Thêm chỉ thị loại bỏ chữ/text
        no_text_suffix = ", absolutely NO text, NO words, NO letters, NO signs, NO watermark, NO logo, NO labels, pure visual scene"

        # Trích xuất profile, style và các scene từ prompt
        import re
        profile_match = re.search(r"(?:Character Profile|Hồ sơ nhân vật|Profile|Nhân vật)[\s*:\-–\.]+(.*?)(?=(?:Art Style|Phong cách|Scene|Cảnh)\s*|\Z)", prompt, re.DOTALL | re.IGNORECASE)
        style_match = re.search(r"(?:Art Style|Phong cách nghệ thuật|Style|Phong cách)[\s*:\-–\.]+(.*?)(?=(?:Scene|Cảnh|Nhân vật|Profile)\s*|\Z)", prompt, re.DOTALL | re.IGNORECASE)
        
        profile_text = profile_match.group(1).strip() if profile_match else ""
        style_text = style_match.group(1).strip() if style_match else ""
        
        scenes = re.findall(r"(?:Scene|Cảnh)\s*(\d+)[\s*:\-–\.]+(.*?)(?=(?:Scene|Cảnh)\s*\d+[\s*:\-–\.]+|\Z)", prompt, re.DOTALL | re.IGNORECASE)
        
        if not scenes:
            # Fallback nếu không trích xuất được scene nào thì coi cả prompt là 1 scene
            scenes = [("1", prompt)]

        scene_prompts = []
        for s_num, s_desc in scenes:
            scene_prompt = f"{style_text} {profile_text} {s_desc.strip()}".strip()
            scene_prompt = scene_prompt.replace("\n", " ").strip()
            scene_prompts.append((int(s_num), scene_prompt))

        # Chỉ định cứng base_url của OpenAI để tránh bị ghi đè bởi biến môi trường proxy
        client = OpenAI(api_key=api_key, base_url="https://api.openai.com/v1")
        
        scene_results = {}
        pending_scenes = list(scene_prompts)
        
        max_attempts = 3
        attempt = 0
        
        while pending_scenes and attempt < max_attempts:
            attempt += 1
            
            def generate_single_scene_image(scene_info) -> tuple[int, str]:
                s_num, s_prompt = scene_info
                refined_prompt = f"{s_prompt[:30000]}{no_text_suffix}"
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
                            return s_num, f"ERROR_IDX_{s_num}: gpt-image-2: {str(e2)} | gpt-image-1-mini: {str(e1)}"
                    
                    b64_data = response.data[0].b64_json
                    if not b64_data:
                        return s_num, f"ERROR_IDX_{s_num}: OpenAI khong tra ve du lieu anh."
                    
                    img_bytes = base64.b64decode(b64_data)
                    img = Image.open(BytesIO(img_bytes))
                    
                    os.makedirs("generated_images", exist_ok=True)
                    # Lưu tên file chứa scene_{s_num} để UI dễ đối chiếu
                    file_path = f"generated_images/scene_{s_num}_image_{int(time.time())}.png"
                    img.save(file_path)
                    
                    return s_num, file_path
                except Exception as e:
                    return s_num, f"ERROR_IDX_{s_num}: {str(e)}"

            # Tạo song song các ảnh bằng ThreadPoolExecutor
            with ThreadPoolExecutor(max_workers=min(len(pending_scenes), 4)) as executor:
                batch_results = list(executor.map(generate_single_scene_image, pending_scenes))
            
            next_pending = []
            for s_num, res in batch_results:
                if "ERROR_IDX_" in res:
                    err_lower = res.lower()
                    is_api_limit = "429" in err_lower or "quota" in err_lower or "limit" in err_lower or "exhausted" in err_lower
                    
                    # Nếu gặp lỗi rate limit / quota, ta sẽ đưa vào danh sách thử lại cho vòng sau
                    if is_api_limit and attempt < max_attempts:
                        s_prompt = next(p[1] for p in pending_scenes if p[0] == s_num)
                        next_pending.append((s_num, s_prompt))
                        scene_results[s_num] = res
                    else:
                        scene_results[s_num] = res
                else:
                    scene_results[s_num] = res
            
            pending_scenes = next_pending
            if pending_scenes:
                # Đợi 2 giây trước khi gửi lại request lần tiếp theo
                time.sleep(2)

        # Định dạng dòng trả về để tương thích ngược
        output_lines = []
        errors = []
        for s_num in sorted(scene_results.keys()):
            res = scene_results[s_num]
            if "ERROR_IDX_" in res:
                errors.append(res)
            else:
                output_lines.append(f"[ANH] Duong dan anh: {res}")
        
        if not output_lines:
            return "ERROR: Khong the tao bat ky anh nao. Chi tiet:\n" + "\n".join(errors)
            
        if errors:
            output_lines.append("[WARN] Mot so anh bi loi khi tao:\n" + "\n".join(errors))
            
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
            
        return f"[ANH] Duong dan anh: {file_path}"
        
    except ImportError:
        return "ERROR: Chưa cài đặt thư viện diffusers / transformers / torch. Vui lòng chạy: pip install diffusers transformers torch"
    except Exception as e:
        return f"ERROR: Lỗi khi sinh ảnh bằng Stable Diffusion local: {str(e)}"

