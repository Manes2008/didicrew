# MIT License
# Copyright (c) 2026 Manes2008/didicrew

import asyncio
import os
import re
import time

def extract_voiceover_text(script_text: str) -> str:
    """
    Trich xuat toan bo loi thoai / loi doc voiceover tu kich ban Markdown.
    """
    if not script_text:
        return ""

    lines = []
    # Tim cac dong [LỜI DẪN / VOICEOVER / NARRATOR / THOẠI / DIALOGUE]
    voice_patterns = [
        r"(?:Lời dẫn|Voiceover|Narrator|Thoại|Dialogue|Lời đọc|MC|Host)[\s*:\-\u2013\.]+(.*?)$",
        r'"([^"]{10,})"',
        r'“([^”]{10,})”'
    ]

    for line in script_text.split("\n"):
        line_clean = line.strip()
        if not line_clean or line_clean.startswith("#") or line_clean.startswith("![") or "http" in line_clean:
            continue
        
        matched = False
        for pat in voice_patterns:
            m = re.search(pat, line_clean, re.IGNORECASE)
            if m:
                text_content = m.group(1).strip()
                if len(text_content) > 5 and not text_content.startswith("http"):
                    lines.append(text_content)
                    matched = True
                    break
        
        # Neu dong co noi dung chu thuong dai va khong phai tieu de ky thuat
        if not matched and len(line_clean) > 20 and not line_clean.startswith("|") and not line_clean.startswith("* **"):
            # Loc cac tu khoa ky thuat
            if not any(k in line_clean.lower() for k in ["prompt", "camera", "lighting", "bối cảnh", "cảnh ", "scene"]):
                lines.append(line_clean)

    if lines:
        return " ".join(lines)
    
    # Fallback: loai bo cac ky tu markdown
    cleaned = re.sub(r"[#*_`|\[\]\(\)]", " ", script_text)
    return " ".join(cleaned.split()[:300])

async def _synthesize_edge_tts(text: str, voice: str, output_path: str):
    import edge_tts
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)

def generate_voiceover_func(script_text: str, voice_name: str = "vi-VN-NamMinhNeural") -> str:
    """
    Tao file am thanh voiceover tu kich ban su dung Microsoft Neural Edge-TTS (100% Mien phi, khong ton Quota API).
    """
    try:
        os.makedirs("generated_audio", exist_ok=True)
        spoken_text = extract_voiceover_text(script_text)
        if not spoken_text:
            spoken_text = "Chào mừng bạn đến với video mới nhất của kênh."

        timestamp = int(time.time())
        output_file = f"generated_audio/voice_{timestamp}.mp3"

        # Chay async edge-tts trong event loop moi hoac loop hien tai
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Chay trong thread rieng neu loop dang chay
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    pool.submit(asyncio.run, _synthesize_edge_tts(spoken_text, voice_name, output_file)).result()
            else:
                loop.run_until_complete(_synthesize_edge_tts(spoken_text, voice_name, output_file))
        except Exception:
            asyncio.run(_synthesize_edge_tts(spoken_text, voice_name, output_file))

        return f"[GIỌNG ĐỌC VOICEOVER]:\n📁 Đường dẫn file âm thanh: {output_file}\n🎙️ Giọng đọc: {voice_name}\n📝 Nội dung thuyết minh: {spoken_text}"

    except Exception as e:
        return f"[LỖI VOICEOVER]: Khong the tao giong doc: {str(e)}"
