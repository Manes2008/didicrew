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

def extract_scenes_from_script(script_text: str) -> list[tuple[int, str]]:
    import re
    scenes_data = {}
    
    # 1. Parse theo bảng Markdown có Scene 1, **Scene 1**, Phân cảnh 1 hoặc số thứ tự
    table_rows = re.findall(r"\|\s*(?:\*\*)?(?:Scene|Phân cảnh|Cảnh)?\s*(\d+)(?:\*\*)?\s*\|(?:[^|]*\|)?\s*`?([^`|\n]+)`?\s*\|", script_text, re.IGNORECASE)
    if table_rows:
        for s_num_str, prompt_str in table_rows:
            try:
                s_num = int(s_num_str)
                cleaned = prompt_str.strip().strip("`")
                if cleaned and len(cleaned) > 10 and "thời lượng" not in cleaned.lower() and "ghi chú" not in cleaned.lower():
                    scenes_data[s_num] = cleaned
            except Exception:
                pass

    # 2. Parse theo khối block Cảnh của Phần 3 để tìm Combined / Visual Prompt
    if not scenes_data:
        scene_blocks = re.split(r"-?\s*\*?\*?\s*(?:Phân\s*cảnh\s*Veo3|Cảnh\s*Veo3|Phân\s*cảnh|Cảnh|Scene)\s*(\d+)\s*(?:\([^)]*\))?\s*\*?\*?\s*[:\-–\.\s\n]+", script_text, flags=re.IGNORECASE)
        if len(scene_blocks) > 1:
            for i in range(1, len(scene_blocks), 2):
                try:
                    s_num = int(scene_blocks[i])
                    block_content = scene_blocks[i+1]
                    
                    visual_match = re.search(r"(?:Combined\s+)?Visual(?:\s*\(EN\))?\s*[:\-–\.]+\s*(.*?)(?=\n\s*\*|\Z)", block_content, re.IGNORECASE | re.DOTALL)
                    voice_match = re.search(r"Voiceover(?:\s*/\s*Dialogue)?(?:\s*\(VI\))?\s*[:\-–\.]+\s*(.*?)(?=\n\s*\*|\Z)", block_content, re.IGNORECASE | re.DOTALL)
                    detail_match = re.search(r"Veo3\s*Detail\s*[:\-–\.]+\s*(.*?)(?=\n\s*\*|\Z)", block_content, re.IGNORECASE | re.DOTALL)
                    combined_match = re.search(r"Combined\s+(?:Prompt|Visual)(?:\s*\(EN\))?\s*[:\-–\.]+\s*(.*?)(?=\n\s*\*|\Z)", block_content, re.IGNORECASE | re.DOTALL)
                    
                    visual_en = visual_match.group(1).strip() if visual_match else ""
                    voice_vi = voice_match.group(1).strip() if voice_match else ""
                    detail = detail_match.group(1).strip() if detail_match else ""
                    combined = combined_match.group(1).strip() if combined_match else ""
                    
                    prompt = combined or visual_en or detail or voice_vi
                    if prompt.strip():
                        scenes_data[s_num] = prompt.strip()
                except Exception as ex_block:
                    print(f"[WARN] Loi parse block canh {scene_blocks[i]}: {ex_block}")
                    
    # 3. Fallback 2: Parse các gạch đầu dòng hoặc định dạng danh sách
    if not scenes_data:
        list_matches = re.findall(r"(?:^|\n)\s*(?:[-*]|\d+\.)?\s*(?:Cảnh|Phân cảnh|Scene)\s*(\d+)[\s*:\-\u2013\.]+(.*?)(?=(?:\n\s*(?:[-*]|\d+\.)?\s*(?:Cảnh|Phân cảnh|Scene)\s*\d+)|\Z)", script_text, re.DOTALL | re.IGNORECASE)
        for s_num_str, prompt_str in list_matches:
            try:
                s_num = int(s_num_str)
                cleaned = re.sub(r"\n+", " ", prompt_str).strip()
                if cleaned and len(cleaned) > 10:
                    scenes_data[s_num] = cleaned
            except Exception:
                pass

    # 4. Fallback 3: Tìm các code blocks (Master Character Reference Sheet, Prompt (EN))
    if not scenes_data:
        code_blocks = re.findall(r"```(?:text|prompt)?\s*\n(.*?)```", script_text, re.DOTALL)
        for idx, block in enumerate(code_blocks, start=1):
            cleaned = block.strip()
            if cleaned and len(cleaned) > 20:
                scenes_data[idx] = cleaned
                
    return sorted(scenes_data.items(), key=lambda x: x[0])

def generate_gpt_image_func(script_text: str) -> str:
    """Ham sinh anh gpt-image-2 cho tung phan canh (Co fallback va retry)."""
    import config
    client = OpenAI(api_key=config.OPENAI_API_KEY)
    
    scene_prompts = extract_scenes_from_script(script_text)
    
    no_text_suffix = ", cinematic composition, highly detailed, realistic textures, no text, no watermark, no typography, clean image"
    
    scene_results = {}
    
    if scene_prompts:
        max_attempts = 3
        
        def generate_single_scene_image(scene_info, gen_id_ref=None) -> tuple[int, str, str | None]:
            s_num, s_prompt = scene_info
            
            if gen_id_ref and s_num > 1:
                refined_prompt = f"Using gen_id {gen_id_ref} as reference to maintain identical character, clothing, face features, and art style. {s_prompt[:25000]}{no_text_suffix}"
            else:
                refined_prompt = f"{s_prompt[:30000]}{no_text_suffix}"
                
            try:
                try:
                    response = client.images.generate(
                        model="gpt-image-2",
                        prompt=refined_prompt,
                        size="1024x1024",
                        quality="medium",
                        n=1
                    )
                except Exception as e2:
                    try:
                        response = client.images.generate(
                            model="gpt-image-1-mini",
                            prompt=refined_prompt,
                            size="1024x1024",
                            quality="medium",
                            n=1
                        )
                    except Exception as e1:
                        return s_num, f"ERROR_IDX_{s_num}: gpt-image-2: {str(e2)} | gpt-image-1-mini: {str(e1)}", None
                
                b64_data = response.data[0].b64_json
                if not b64_data:
                    return s_num, f"ERROR_IDX_{s_num}: OpenAI khong tra ve du lieu anh.", None
                
                gen_id = getattr(response.data[0], "gen_id", None)
                
                img_bytes = base64.b64decode(b64_data)
                img = Image.open(BytesIO(img_bytes))
                
                os.makedirs("generated_images", exist_ok=True)
                file_path = f"generated_images/scene_{s_num}_image_{int(time.time())}.png"
                img.save(file_path)
                
                return s_num, file_path, gen_id
            except Exception as e:
                return s_num, f"ERROR_IDX_{s_num}: {str(e)}", None

        sorted_scenes = sorted(scene_prompts, key=lambda x: x[0])
        gen_id_ref = None
        
        if sorted_scenes:
            first_scene = sorted_scenes[0]
            first_scene_success = False
            first_attempt = 0
            
            while first_attempt < max_attempts and not first_scene_success:
                first_attempt += 1
                s_num, res_path, gen_id = generate_single_scene_image(first_scene, None)
                if "ERROR_IDX_" in res_path:
                    err_lower = res_path.lower()
                    is_api_limit = "429" in err_lower or "quota" in err_lower or "limit" in err_lower or "exhausted" in err_lower
                    scene_results[s_num] = res_path
                    if not is_api_limit:
                        break
                    if first_attempt < max_attempts:
                        time.sleep(2)
                else:
                    scene_results[s_num] = res_path
                    gen_id_ref = gen_id
                    first_scene_success = True
            
            other_scenes = sorted_scenes[1:]
            if other_scenes:
                pending_scenes = list(other_scenes)
                attempt = 0
                
                while pending_scenes and attempt < max_attempts:
                    attempt += 1
                    
                    def run_batch_task(scene_info):
                        return generate_single_scene_image(scene_info, gen_id_ref)
                        
                    with ThreadPoolExecutor(max_workers=min(len(pending_scenes), 4)) as executor:
                         batch_results = list(executor.map(run_batch_task, pending_scenes))
                    
                    next_pending = []
                    for s_num, res_path, gen_id in batch_results:
                        if "ERROR_IDX_" in res_path:
                            err_lower = res_path.lower()
                            is_api_limit = "429" in err_lower or "quota" in err_lower or "limit" in err_lower or "exhausted" in err_lower
                            scene_results[s_num] = res_path
                            if is_api_limit and attempt < max_attempts:
                                s_prompt = next(p[1] for p in pending_scenes if p[0] == s_num)
                                next_pending.append((s_num, s_prompt))
                        else:
                            scene_results[s_num] = res_path
                            
                    pending_scenes = next_pending
                    if pending_scenes and attempt < max_attempts:
                        time.sleep(2)
                        
        output_lines = [f"[ANH CẢNH {s}]: {p}" for s, p in sorted(scene_results.items())]
        return "\n".join(output_lines)
    else:
        try:
            clean_prompt = f"{script_text[:30000]}{no_text_suffix}"
            response = client.images.generate(
                model="gpt-image-2",
                prompt=clean_prompt,
                size="1024x1024",
                quality="medium",
                n=1
            )
            b64_data = response.data[0].b64_json
            if not b64_data:
                return "ERROR: OpenAI khong tra ve du lieu anh."
            
            img_bytes = base64.b64decode(b64_data)
            img = Image.open(BytesIO(img_bytes))
            
            os.makedirs("generated_images", exist_ok=True)
            file_path = f"generated_images/single_image_{int(time.time())}.png"
            img.save(file_path)
            
            return f"[ANH]: {file_path}"
        except Exception as e:
            return f"ERROR: Loi khi sinh anh tong the bang gpt-image: {str(e)}"

@tool("generate_gpt_image")
def generate_gpt_image(script_text: str) -> str:
    """Cong cu CrewAI sinh anh cho tung phan canh kich ban."""
    return generate_gpt_image_func(script_text)

def generate_gemini_imagen_func(script_text: str, aspect_ratio: str = "9:16", model_name: str = "gemini-2.5-flash-image") -> str:
    """Sinh anh bang Google Gemini Image Native (gemini-2.5-flash-image, gemini-3-pro-image, gemini-3.1-flash-image) hoac Flux Realism Ultra HD."""
    import config
    import urllib.parse
    import re
    api_key = config.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY")

    scene_prompts = extract_scenes_from_script(script_text)
    if not scene_prompts:
        scene_prompts = [(1, script_text[:1000])]

    scene_results = {}
    os.makedirs("generated_images", exist_ok=True)

    # Tinh toan do phan giai cao (Ultra HD) theo ti le
    if aspect_ratio == "16:9":
        w, h = 1536, 896
    elif aspect_ratio == "1:1":
        w, h = 1024, 1024
    else: # 9:16 Shorts
        w, h = 896, 1536

    def generate_single_scene(s_num: int, prompt: str) -> tuple[int, str]:
        clean_p = prompt.replace("\n", " ").strip()
        clean_p = re.sub(r"(?:Phân cảnh|Cảnh|Lời thoại|Voiceover|SFX|BGM|Veo3 Detail)\s*[:\-–\.]+", "", clean_p, flags=re.IGNORECASE)
        clean_p = re.sub(r"[^\x00-\x7F]+", " ", clean_p)
        clean_p = re.sub(r"\s+", " ", clean_p).strip()

        if len(clean_p) < 15:
            clean_p = "cinematic photorealistic scene, highly detailed, beautiful lighting, masterpiece 8k"

        file_path = f"generated_images/scene_{s_num}_{int(time.time())}.png"

        # 1. Thu goi Google Gemini GenAI SDK voi model da chon neu khong phai Flux truc tiep
        if api_key and not model_name.startswith("flux"):
            try:
                from google import genai
                from google.genai import types
                client = genai.Client(api_key=api_key)
                response = client.models.generate_content(
                    model=target_gemini_model,
                    contents=f"Generate a high quality, photorealistic, cinematic image of: {clean_p}",
                    config=types.GenerateContentConfig(response_modalities=["IMAGE"])
                )
                if response.candidates and response.candidates[0].content.parts:
                    for part in response.candidates[0].content.parts:
                        if hasattr(part, "inline_data") and part.inline_data:
                            img_bytes = part.inline_data.data
                            with open(file_path, "wb") as f:
                                f.write(img_bytes)
                            return s_num, file_path
            except Exception:
                pass

        # 2. Fallback sang Flux Realism / Flux / Turbo voi co che Retry 3 lan chong Timeout
        enhanced_prompt = f"{clean_p[:450]}, masterpiece, 8k resolution, highly detailed realistic textures, cinematic soft rim lighting, photorealistic portrait, sharp focus, 35mm photography"
        encoded_p = urllib.parse.quote(enhanced_prompt)
        
        fallback_models = ["flux-realism", "flux", "turbo"]
        for attempt, f_model in enumerate(fallback_models):
            try:
                seed_val = int(time.time() + s_num * 100 + attempt * 17) % 99999
                flux_url = f"https://image.pollinations.ai/prompt/{encoded_p}?width={w}&height={h}&model={f_model}&nologo=true&seed={seed_val}&enhance=true"
                
                r = requests.get(flux_url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}, timeout=60)
                if r.status_code == 200 and len(r.content) > 5000:
                    with open(file_path, "wb") as f:
                        f.write(r.content)
                    return s_num, file_path
            except Exception as ex_attempt:
                time.sleep(1.5)
                
        return s_num, f"ERROR_IDX_{s_num}: Khong the sinh anh cho canh {s_num}"

    # Chay song song toi da 3 luong de toi uu toc do va khong bi nghen mang
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(generate_single_scene, s_num, prompt) for s_num, prompt in scene_prompts]
        for f in futures:
            try:
                s_idx, res_path = f.result()
                scene_results[s_idx] = res_path
            except Exception as ex_f:
                pass

    output_lines = [f"[ANH CẢNH {s}]: {p}" for s, p in sorted(scene_results.items())]
    return "\n".join(output_lines)

def generate_local_image_sd_func(prompt: str, use_gpu: bool = False) -> str:
    """Sinh anh cuc bo bang model Stable Diffusion v1.5 (CPU hoac GPU)."""
    try:
        import torch
        import gc
        from diffusers import StableDiffusionPipeline
        
        if use_gpu and not torch.cuda.is_available():
            print("[WARN] Yeu cau chay GPU nhung he thong khong co CUDA! Tu dong chuyen sang CPU.")
            use_gpu = False
        elif not use_gpu:
            use_gpu = torch.cuda.is_available()
            
        device = "cuda" if use_gpu else "cpu"
        dtype = torch.float16 if use_gpu else torch.float32
        
        print(f"[LOG] Khoi tao Stable Diffusion tren: {device}")
        
        if use_gpu:
            gc.collect()
            torch.cuda.empty_cache()
            
        model_id = "runwayml/stable-diffusion-v1-5"
        pipe = StableDiffusionPipeline.from_pretrained(
            model_id, 
            torch_dtype=dtype,
            low_cpu_mem_usage=True
        )
        
        if use_gpu:
            pipe.to("cuda")
            if hasattr(pipe, "enable_attention_slicing"):
                pipe.enable_attention_slicing()
        else:
            pipe.to("cpu")
            
        os.makedirs("generated_images", exist_ok=True)
        num_inference_steps = 30 if use_gpu else 15
        image = pipe(prompt=prompt[:1024], num_inference_steps=num_inference_steps).images[0]
        file_path = f"generated_images/sd_image_{int(time.time())}.png"
        image.save(file_path)
        
        del pipe
        if use_gpu:
            gc.collect()
            torch.cuda.empty_cache()
            
        return f"[ANH]: {file_path}"
        
    except ImportError:
        return "ERROR: Chua cai dat thu vien diffusers / torch."
    except Exception as e:
        return f"ERROR: Loi khi sinh anh SD local: {str(e)}"
