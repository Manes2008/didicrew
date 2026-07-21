# src/core/video_generator.py
import os
import time
import requests
import base64
from urllib.parse import urlparse
from PIL import Image
import io
import config
import subprocess

def merge_video_audio_func(video_path: str, voice_path: str) -> str:
    """
    Ghep file am thanh voiceover tu Buc 4 vao file video mp4 bang FFmpeg.
    """
    if not voice_path or not os.path.exists(voice_path):
        return video_path

    try:
        output_path = video_path.replace(".mp4", "_with_voice.mp4")
        cmd = [
            "ffmpeg", "-y",
            "-i", video_path,
            "-i", voice_path,
            "-c:v", "copy",
            "-c:a", "aac",
            "-shortest",
            output_path
        ]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0 and os.path.exists(output_path):
            return output_path
        else:
            return video_path
    except Exception as ex:
        print(f"[WARN] Khong the ghep audio bang FFmpeg: {ex}")
        return video_path

def generate_wan21_local_video(prompt: str, image_path: str = None) -> str:
    """
    Tao video local su dung Wan 2.1 qua PyTorch / Hugging Face diffusers.
    """
    try:
        import torch
        if not torch.cuda.is_available():
            return "ERROR: WAN 2.1 Local yeu cau GPU NVIDIA voi CUDA. Khong tim thấy GPU phu hop tren may hien tai."
            
        device_props = torch.cuda.get_device_properties(0)
        total_vram_gb = device_props.total_memory / (1024 ** 3)
        print(f"[LOG] Nhan dien GPU: {device_props.name} | VRAM: {total_vram_gb:.2f} GB")
            
        os.makedirs("generated_videos", exist_ok=True)
        file_name = f"wan21_video_{int(time.time())}.mp4"
        file_path = os.path.join("generated_videos", file_name)
        
        try:
            from diffusers import WanPipeline, AutoencoderKLWan
            model_id = "Wan-AI/Wan2.1-T2V-1.3B-Diffusers"
            dtype = torch.float16
            vae = AutoencoderKLWan.from_pretrained(model_id, subfolder="vae", torch_dtype=torch.float32)
            pipe = WanPipeline.from_pretrained(model_id, vae=vae, torch_dtype=dtype)
            
            # Toi uu hoa Low VRAM cho GPU < 6GB VRAM (nhu RTX 3050 4GB)
            if hasattr(pipe, "enable_model_cpu_offload"):
                pipe.enable_model_cpu_offload()
            else:
                pipe.to("cuda")
                
            if hasattr(pipe, "enable_attention_slicing"):
                pipe.enable_attention_slicing()
            
            output = pipe(
                prompt=prompt[:1000],
                height=480,
                width=832,
                num_frames=81,
                guidance_scale=5.0
            ).frames[0]
            
            # Luu file video
            output.save(file_path)
            return file_path
        except ImportError as imp_err:
            return f"ERROR: Thieu thu vien diffusers hoac phu thuoc: {str(imp_err)}. Vui long chay: pip install -r requirements.txt"
        except Exception as model_err:
            # Fallback thong bao cho nguoi dung neu weights chua duoc tai
            return f"ERROR: Khong the khoi tao pipeline Wan 2.1 Local: {str(model_err)}. Vui long kiem tra lai thu vien diffusers va VRAM."

    except ImportError:
        return "ERROR: Chưa cai dat thu vien torch / diffusers cho Wan 2.1 Local. Vui long chay: pip install torch diffusers transformers"
    except Exception as e:
        return f"ERROR: Loi khi chay Wan 2.1 Local: {str(e)}"

import math

def get_audio_duration_func(voice_path: str) -> float:
    """
    Do thoi luong file am thanh voiceover tu Buc 4.
    """
    if not voice_path or not os.path.exists(voice_path):
        return 5.0
    try:
        cmd = [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            voice_path
        ]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0 and result.stdout.strip():
            return float(result.stdout.strip())
    except Exception as ex:
        print(f"[WARN] Khong the do duration audio bang ffprobe: {ex}")
    return 5.0

def concat_video_clips_func(clip_paths: list) -> str:
    """
    Noi nhieu clip mp4 thanh 1 video dai bang FFmpeg concat.
    """
    if not clip_paths:
        return ""
    if len(clip_paths) == 1:
        return clip_paths[0]

    os.makedirs("generated_videos", exist_ok=True)
    list_file = os.path.join("generated_videos", f"concat_list_{int(time.time())}.txt")
    output_path = os.path.join("generated_videos", f"full_video_{int(time.time())}.mp4")

    with open(list_file, "w", encoding="utf-8") as f:
        for path in clip_paths:
            abs_p = os.path.abspath(path).replace("\\", "/")
            f.write(f"file '{abs_p}'\n")

    cmd = [
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", list_file,
        "-c", "copy",
        output_path
    ]
    try:
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if res.returncode == 0 and os.path.exists(output_path):
            return output_path
    except Exception as ex:
        print(f"[WARN] Loi khi concat video clips: {ex}")

    return clip_paths[0]

def generate_video_func(prompt: str, image_path: str = None, voice_path: str = None, engine: str = "wan2.1_local") -> str:
    """
    Ham tao video chinh ho tro sinh multi-scene dua tren do dai Voiceover.
    """
    start_time = time.time()
    # 1. Do thoi luong voiceover de tinh so luong phan canh (scenes)
    duration = get_audio_duration_func(voice_path) if voice_path else 5.0
    num_scenes = max(1, math.ceil(duration / 5.0))
    frames_per_scene = 81 if engine == "wan2.1_local" else 125
    total_frames = num_scenes * frames_per_scene

    # Tach prompt thanh cac cau tuong ung so canh
    prompt_sentences = [s.strip() for s in prompt.split(".") if s.strip()]
    if not prompt_sentences:
        prompt_sentences = [prompt]

    clip_paths = []
    
    for i in range(num_scenes):
        scene_prompt = prompt_sentences[i % len(prompt_sentences)]
        full_scene_prompt = f"Scene {i+1}/{num_scenes}: {scene_prompt}"
        print(f"[LOG] Dang tao phan canh {i+1}/{num_scenes} ({frames_per_scene} frames)...")
        
        if engine == "wan2.1_local":
            res = generate_wan21_local_video(full_scene_prompt, image_path)
        else:
            res = _generate_pollo_video(full_scene_prompt, image_path)

        if res.startswith("ERROR"):
            # Neu loi o canh dau tien thi tra ve loi
            if i == 0:
                return res
            break
        clip_paths.append(res)

    if not clip_paths:
        return "ERROR: Khong sinh duoc phan canh video nao."

    # 2. Noi tat ca clip lai thanh video dai
    merged_video_path = concat_video_clips_func(clip_paths)

    # 3. Ghep Voiceover audio tu Buc 4 neu co
    if voice_path and os.path.exists(voice_path):
        final_path = merge_video_audio_func(merged_video_path, voice_path)
        video_result_path = final_path
    else:
        video_result_path = merged_video_path

    elapsed_time = time.time() - start_time
    log_info = f"[LOG] Thoi gian thuc hien: {elapsed_time:.2f}s | Frame/canh: {frames_per_scene} | Tong so frames: {total_frames} | So phan canh: {num_scenes}"
    print(log_info)

    return f"Duong dan video: {video_result_path}\n{log_info}"

def _generate_pollo_video(prompt: str, image_path: str = None) -> str:
    """
    Tao video bang Pollo AI (Minimax Hailuo 02) qua API.
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
                        return file_path
                    else:
                        return f"ERROR: Không thể tải video từ URL: {video_url}"
                
                elif status == "failed":
                    error_msg = poll_data.get("data", {}).get("error", "Unknown error")
                    return f"ERROR: Tạo video thất bại trên Pollo AI. Lỗi: {error_msg}"
            
        return "ERROR: Quá thời gian chờ (Timeout) khi tạo video. Vui lòng thử lại sau."
            
    except Exception as e:
        return f"ERROR: Lỗi hệ thống: {str(e)}"