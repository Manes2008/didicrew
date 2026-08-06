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
        import os
        # Chống phân mảnh bộ nhớ trên Windows bằng cách kích hoạt expandable_segments
        os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"
        
        import torch
        import gc
        
        # Giải phóng cache CUDA chủ động trước khi tải mô hình
        gc.collect()
        torch.cuda.empty_cache()
        
        if not torch.cuda.is_available():
            return "ERROR: WAN 2.1 Local yeu cau GPU NVIDIA voi CUDA. Khong tim thay GPU phu hop tren may hien tai."
            
        device_props = torch.cuda.get_device_properties(0)
        total_vram_gb = device_props.total_memory / (1024 ** 3)
        
        # Tăng giới hạn sử dụng VRAM của PyTorch lên 95% để tránh OOM ảo trên Windows
        try:
            torch.cuda.set_per_process_memory_fraction(0.95, 0)
        except Exception as e:
            print(f"[WARN] Khong the set memory fraction: {e}")
            
        alloc_vram = torch.cuda.memory_allocated(0) / (1024 ** 3)
        res_vram = torch.cuda.memory_reserved(0) / (1024 ** 3)
        print(f"[LOG] GPU: {device_props.name} | Tong VRAM: {total_vram_gb:.2f} GB | Dang dung: {alloc_vram:.2f} GB (Allocated) / {res_vram:.2f} GB (Reserved)")
            
        os.makedirs("generated_videos", exist_ok=True)
        file_name = f"wan21_video_{int(time.time())}.mp4"
        file_path = os.path.join("generated_videos", file_name)
        
        try:
            from diffusers import WanPipeline, AutoencoderKLWan
            model_id = "Wan-AI/Wan2.1-T2V-1.3B-Diffusers"
            dtype = torch.float16
            # Sử dụng torch.float16 cho VAE thay vì float32 để giảm thiểu tối đa tiêu thụ VRAM lúc decode video
            vae = AutoencoderKLWan.from_pretrained(model_id, subfolder="vae", torch_dtype=torch.float16, low_cpu_mem_usage=True)
            pipe = WanPipeline.from_pretrained(model_id, vae=vae, torch_dtype=dtype, low_cpu_mem_usage=True)
            
            # Kich hoat VAE tiling va slicing de giam VRAM luc decode video
            if hasattr(pipe, "vae") and pipe.vae is not None:
                try:
                    pipe.vae.enable_tiling()
                    print("[LOG] Da bat VAE Tiling de tiet kiem VRAM.")
                except Exception as e:
                    print(f"[WARN] Khong the bat VAE Tiling: {e}")
                try:
                    pipe.vae.enable_slicing()
                    print("[LOG] Da bat VAE Slicing de tiet kiem VRAM.")
                except Exception as e:
                    print(f"[WARN] Khong the bat VAE Slicing: {e}")
            
            # Toi uu hoa tai model dua tren dung luong VRAM
            if total_vram_gb >= 16.0:
                print("[LOG] GPU co VRAM >= 16GB. Tai truc tiep model len GPU de tang toc do sinh video.")
                pipe.to("cuda")
            elif hasattr(pipe, "enable_model_cpu_offload"):
                print("[LOG] GPU co VRAM < 16GB. Bat CPU offload de tiet kiem VRAM.")
                pipe.enable_model_cpu_offload()
            else:
                pipe.to("cuda")
                
            if hasattr(pipe, "enable_attention_slicing"):
                pipe.enable_attention_slicing()
            
            # Log VRAM truoc khi chay inference
            post_alloc = torch.cuda.memory_allocated(0) / (1024 ** 3)
            print(f"[LOG] VRAM sau khi nap pipeline: {post_alloc:.2f} GB / {total_vram_gb:.2f} GB")

            # Reset thong ke VRAM va do thoi gian sinh
            torch.cuda.reset_peak_memory_stats(0)
            gen_start_time = time.time()
            
            num_frames = 81
            height = 480
            width = 832
            guidance_scale = 5.0

            output = pipe(
                prompt=prompt[:1000],
                height=height,
                width=width,
                num_frames=num_frames,
                guidance_scale=guidance_scale
            ).frames[0]
            
            gen_elapsed = time.time() - gen_start_time
            sec_per_frame = gen_elapsed / num_frames if num_frames > 0 else 0
            peak_vram = torch.cuda.max_memory_allocated(0) / (1024 ** 3)
            
            print(f"[LOG METRICS] Thoi gian sinh: {gen_elapsed:.2f}s | Toc do: {sec_per_frame:.2f}s/frame | VRAM Dinh: {peak_vram:.2f} GB | Do phan giai: {width}x{height} | Frames: {num_frames} | CFG: {guidance_scale}")
            
            # Luu file video
            output.save(file_path)
            
            # Don dep pipeline va cache de giai phong VRAM triet de
            del pipe
            del vae
            gc.collect()
            torch.cuda.empty_cache()
            return file_path
            
        except torch.cuda.OutOfMemoryError as oom_err:
            if "pipe" in locals():
                del pipe
            if "vae" in locals():
                del vae
            gc.collect()
            torch.cuda.empty_cache()
            print(f"[WARNING] Tràn VRAM GPU: {oom_err}")
            return f"ERROR: Tràn VRAM GPU (CUDA Out of Memory)! VRAM đã cấp phát quá mức cho phép. Vui lòng đóng các ứng dụng khác hoặc dùng engine Cloud."
        except ImportError as imp_err:
            return f"ERROR: Thiếu thư viện diffusers hoặc phụ thuộc: {str(imp_err)}. Vui lòng chạy: pip install -r requirements.txt"
        except Exception as model_err:
            err_str = str(model_err)
            if "File reconstruction error" in err_str or "Background writer channel closed" in err_str:
                return "ERROR: File cache weights bị hỏng do ngắt tải giữa chừng. Vui lòng chạy: Remove-Item -Recurse -Force \"$env:USERPROFILE\\.cache\\huggingface\\hub\\models--Wan-AI--Wan2.1-T2V-1.3B-Diffusers\""
            return f"ERROR: Không thể khởi tạo pipeline Wan 2.1 Local: {err_str}. Vui lòng kiểm tra lại thư viện diffusers và VRAM."

    except ImportError:
        return "ERROR: Chưa cài đặt thư viện torch / diffusers cho Wan 2.1 Local. Vui lòng chạy: pip install torch diffusers transformers"
    except Exception as e:
        return f"ERROR: Lỗi khi chạy Wan 2.1 Local: {str(e)}"

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

def extract_scene_prompts(prompt_text: str, num_scenes: int) -> list:
    """
    Trích xuất prompt chi tiết cho từng phân cảnh dựa trên cấu trúc Scene từ Bước 2.
    """
    import re
    pattern = r"(?:Scene|Cảnh)\s*(\d+)[\s*:\-–\.]+(.*?)(?=(?:Scene|Cảnh)\s*\d+[\s*:\-–\.]+|\Z)"
    matches = re.findall(pattern, prompt_text, re.DOTALL | re.IGNORECASE)
    
    prompts = []
    if matches:
        sorted_matches = sorted(matches, key=lambda x: int(x[0]))
        for _, content in sorted_matches:
            clean_content = content.strip().replace("\n", " ")
            if clean_content:
                prompts.append(clean_content)
    
    if not prompts:
        lines = [line.strip() for line in prompt_text.split("\n") if line.strip() and not line.strip().startswith("#")]
        prompts = [l for l in lines if len(l) > 10]
        
    if not prompts:
        prompts = [s.strip() for s in prompt_text.split(".") if s.strip() and len(s.strip()) > 5]
        
    if not prompts:
        prompts = [prompt_text]
        
    while len(prompts) < num_scenes:
        prompts.append(prompts[-1])
        
    return prompts[:num_scenes]


def scale_video_speed_ffmpeg(video_path: str, target_duration: float, system_ratio_multiplier: float = 1.0) -> str:
    """
    Sử dụng FFmpeg để co giãn (tăng/giảm tốc độ) của video gốc cho khớp chính xác với target_duration.
    """
    if not video_path or not os.path.exists(video_path):
        return video_path
    
    # Đo thời lượng hiện tại của video bằng ffprobe
    current_duration = 5.0
    try:
        cmd_probe = [
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", video_path
        ]
        res = subprocess.run(cmd_probe, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if res.returncode == 0 and res.stdout.strip():
            current_duration = float(res.stdout.strip())
    except Exception as ex:
        print(f"[WARN] Khong the do thoi luong video bang ffprobe: {ex}")
        
    if current_duration <= 0 or target_duration <= 0:
        return video_path

    # Tính toán hệ số nhân tốc độ: setpts = target_duration / current_duration
    setpts_factor = target_duration / current_duration
    if system_ratio_multiplier and system_ratio_multiplier != 1.0:
        setpts_factor = setpts_factor / system_ratio_multiplier
    
    output_path = video_path.replace(".mp4", f"_scaled_{int(time.time())}.mp4")
    
    # Sử dụng bộ lọc video setpts để thay đổi tốc độ phát
    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-filter:v", f"setpts={setpts_factor}*PTS",
        "-an", # Bỏ âm thanh của video gốc để chuẩn bị ghép voiceover sau
        output_path
    ]
    
    try:
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if res.returncode == 0 and os.path.exists(output_path):
            return output_path
    except Exception as ex:
        print(f"[WARN] Loi khi co gian video bang FFmpeg: {ex}")
        
    return video_path


def generate_video_func(prompt: str, image_path: str = None, voice_path: str = None, engine: str = "wan2.1_local", project_id: str = None) -> str:
    """
    Ham tao video chinh ho tro sinh multi-scene dua tren do dai Voiceover va VideoDurationConfig.
    """
    start_time = time.time()
    
    # Cấu hình mặc định từ DB
    duration_type = "system_generated"
    target_duration = 0
    min_duration = 0
    max_duration = 0
    video_source_path = None
    system_ratio_multiplier = 1.0

    if project_id:
        from src.core.models import get_db_session, VideoDurationConfig
        db = get_db_session()
        try:
            cfg = db.query(VideoDurationConfig).filter_by(project_id=int(project_id)).first()
            if cfg:
                duration_type = cfg.duration_type
                target_duration = cfg.target_duration or 0
                min_duration = cfg.min_duration or 0
                max_duration = cfg.max_duration or 0
                video_source_path = cfg.video_source_path
                system_ratio_multiplier = float(cfg.system_ratio_multiplier or 1.0)
        except Exception as e_db:
            print(f"[WARN] Loi doc VideoDurationConfig tu DB: {e_db}")
        finally:
            db.close()

    # 1. Đo thời lượng voiceover để làm cơ sở căn chỉnh
    audio_duration = get_audio_duration_func(voice_path) if voice_path else 0.0
    
    # Tính toán thời lượng video mục tiêu
    duration = audio_duration if audio_duration > 0 else 5.0
    if target_duration > 0:
        duration = target_duration
        
    if min_duration > 0:
        duration = max(duration, min_duration)
    if max_duration > 0:
        duration = min(duration, max_duration)

    # XỬ LÝ CHẾ ĐỘ UPLOADED_VIDEO
    if duration_type == "uploaded_video" and video_source_path and os.path.exists(video_source_path):
        print(f"[LOG] Dang xu ly che do uploaded_video voi file nguon: {video_source_path}")
        scaled_video = scale_video_speed_ffmpeg(video_source_path, duration, system_ratio_multiplier)
        
        # Ghép âm thanh thuyết minh nếu có
        if voice_path and os.path.exists(voice_path):
            video_result_path = merge_video_audio_func(scaled_video, voice_path)
        else:
            video_result_path = scaled_video
            
        elapsed_time = time.time() - start_time
        log_info = f"[LOG] Hoan thanh co gian video nguon (uploaded_video) | Thoi gian: {elapsed_time:.2f}s | Target duration: {duration}s"
        return f"Duong dan video: {video_result_path}\n{log_info}"

    # XỬ LÝ CHẾ ĐỘ SYSTEM_GENERATED (Tự sinh clip)
    num_scenes = max(1, math.ceil(duration / 5.0))
    frames_per_scene = 81 if engine == "wan2.1_local" else 125
    total_frames = num_scenes * frames_per_scene

    # Phân tách danh sách ảnh nếu truyền dạng danh sách hoặc chuỗi phân tách
    image_paths_list = []
    if image_path:
        if isinstance(image_path, list):
            image_paths_list = image_path
        elif isinstance(image_path, str):
            image_paths_list = [img.strip() for img in image_path.replace("\n", ",").split(",") if img.strip()]

    # Trích xuất prompt tương ứng từng phân cảnh một cách nhất quán
    prompt_sentences = extract_scene_prompts(prompt, num_scenes)

    clip_paths = []
    
    for i in range(num_scenes):
        scene_prompt = prompt_sentences[i % len(prompt_sentences)]
        full_scene_prompt = scene_prompt
        print(f"[LOG] Dang tao phan canh {i+1}/{num_scenes} ({frames_per_scene} frames)...")
        
        # Chọn ảnh tương ứng cho phân cảnh hiện tại
        current_image = image_paths_list[i % len(image_paths_list)] if image_paths_list else None
        
        if engine == "wan2.1_local":
            res = generate_wan21_local_video(full_scene_prompt, current_image)
        else:
            res = _generate_pollo_video(full_scene_prompt, current_image)

        if res.startswith("ERROR"):
            # Neu loi o canh dau tien thi tra ve loi
            if i == 0:
                return res
            break
        clip_paths.append(res)

    if not clip_paths:
        return "ERROR: Khong sinh duoc phan canh video nao."

    # 2. Nối tất cả clip lại thành video dài
    merged_video_path = concat_video_clips_func(clip_paths)

    # Co giãn video đã nối cho khớp chính xác với thời lượng âm thanh
    print(f"[LOG] Dang co gian video da noi cho khop thoi luong target: {duration}s")
    scaled_merged_video = scale_video_speed_ffmpeg(merged_video_path, duration, system_ratio_multiplier)

    # 3. Ghép Voiceover audio từ Bước 4 nếu có
    if voice_path and os.path.exists(voice_path):
        final_path = merge_video_audio_func(scaled_merged_video, voice_path)
        video_result_path = final_path
    else:
        video_result_path = scaled_merged_video

    elapsed_time = time.time() - start_time
    log_info = f"[LOG] Thoi gian thuc hien: {elapsed_time:.2f}s | Frame/canh: {frames_per_scene} | Tong so frames: {total_frames} | So phan canh: {num_scenes} | Target duration: {duration}s"
    print(log_info)

    return f"Duong dan video: {video_result_path}\n{log_info}"

def _generate_pollo_video(prompt: str, image_path: str = None) -> str:
    """
    Tao video bang Pollo AI (Minimax Hailuo 02) qua API.
    """
    try:
        api_key = config.POLLO_API_KEY
        if not api_key:
            return "ERROR: Thiếu POLLO_API_KEY trong môi trường. Vui lòng cấu hình API Key để tạo video."

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