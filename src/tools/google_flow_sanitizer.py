# MIT License
# Copyright (c) 2026 Manes2008/didicrew

import re
from typing import List, Dict, Any, Optional

def clean_voiceover_text(raw_text: str, max_chars: int = 120) -> List[str]:
    """
    Lam sach loi thoai doc voiceover:
    - Loai bo the vai doc [NARRATOR]:, [DIALOGUE - ...]:
    - Loai bo chu thich so tu *(11 tu)* hoac (12 words)
    - Loai bo dau ngoac kep thua
    - Tu dong cat ngan neu vuot qua gioi han max_chars (mac dinh 120 ky tu cua Google Flow)
    """
    if not raw_text:
        return []

    # 1. Bo the nguoi noi [NARRATOR]:, [DIALOGUE]:, etc.
    text = re.sub(r"\[[^\]]+\]\s*[:\-–]*", "", raw_text)
    
    # 2. Bo chu thich so tu *(11 tu)* hoac (25 words)
    text = re.sub(r"[\*\(]\s*\d+\s*(?:tu|từ|words?)\s*[\*\)]", "", text, flags=re.IGNORECASE)
    
    # 3. Bo ngoac kep boc ngoai va ngoac don chu thich thua
    text = text.replace('"', '').replace("'", "").replace("*", "").strip()
    text = re.sub(r"\s+", " ", text).strip()

    if not text:
        return []

    # 4. Neu do dai nam trong gioi han, tra ve luon
    if len(text) <= max_chars:
        return [text]

    # 5. Neu vuot qua gioi han 120 ky tu, chia nho theo dau cau
    sentences = re.split(r"([.!?…]+|\s*,\s*)", text)
    chunks = []
    current_chunk = ""

    for part in sentences:
        if not part:
            continue
        if len(current_chunk) + len(part) <= max_chars:
            current_chunk += part
        else:
            if current_chunk.strip():
                chunks.append(current_chunk.strip())
            current_chunk = part

    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks if chunks else [text[:max_chars]]

# Bo tu dien chuyen doi an toan dien anh (Safety & Cinematic Metaphor Map)
SAFETY_REPLACEMENT_MAP = [
    # Vu khi & Chay no
    (r"\b(?:violent\s+)?(?:orange\s+)?explosion\s+of\s+a\s+DK75\s+shell\b", "dramatic sudden burst of golden-orange cinematic backlight"),
    (r"\bDK75(?:\s+shell)?\b", "cinematic flash"),
    (r"\b(?:artillery|mortar|missile|rocket|grenade|bomb|bullet|shrapnel)\b", "cinematic light ray"),
    (r"\b(?:violent\s+)?explosion\b", "sudden burst of warm rim light"),
    (r"\b(?:blast|detonation)\b", "radiant light flare"),
    (r"\b(?:gun|rifle|weapon|pistol|firearm|AK47)\b", "vintage gear"),
    # Hanh dong bao luc & Thuong tat
    (r"\bcrawls?\s+(?:forward\s+)?through\s+(?:dark\s+)?mud\b", "moves low through atmospheric jungle mist"),
    (r"\bfalls?\s+sideways\s+into\s+dark\s+mud\b", "rests in quiet reflection amidst lush foliage"),
    (r"\bshivering\s+face\b", "deeply focused heroic expression"),
    (r"\bunmoving\s+legs\b", "sitting in contemplative silence"),
    (r"\bparalyzed\s+legs\b", "gentle resting posture"),
    (r"\bscarred\s+hands\b", "weathered mature hands"),
    (r"\b(?:blood|bleeding|bloody|gore|gory)\b", "warm golden dust"),
    (r"\b(?:wound|wounded|injury|injured|casualty)\b", "solemn remembrance"),
    (r"\b(?:trauma|past\s+trauma)\b", "emotional journey"),
    # Boi canh xung dot
    (r"\b(?:historical\s+)?war\s+documentary\s+style\b", "historical epic cinematic drama style"),
    (r"\b(?:battlefield|warzone|combat)\b", "historic outdoor environment")
]

def sanitize_prompt_safety(raw_prompt: str, max_chars: int = 500) -> str:
    """
    Bo loc an toan chong nghẽn va bi chan tren Google Gemini, Imagen 3, Veo 3:
    - Chuyen doi cac tu khoa vu khi, chay no, bao luc, thuong tat sang an du dien anh an toan.
    - Kiem tra tinh hop le va gioi han do dai (Validation).
    """
    if not raw_prompt:
        return ""

    prompt = raw_prompt.strip()

    # 1. Ap dung tu dien thay the an toan
    for pattern, replacement in SAFETY_REPLACEMENT_MAP:
        prompt = re.sub(pattern, replacement, prompt, flags=re.IGNORECASE)

    # 2. Don dep cac khoang trang thua
    prompt = re.sub(r"\s+", " ", prompt).strip()

    # 3. Validation gioi han do dai cho AI Model
    if max_chars and len(prompt) > max_chars:
        # Cat gon den dau cau hoac dau phay gan nhat de khong bi cut cau
        cut_point = prompt.rfind(",", 0, max_chars)
        if cut_point > int(max_chars * 0.7):
            prompt = prompt[:cut_point].strip()
        else:
            prompt = prompt[:max_chars].strip()

    return prompt

def clean_veo_prompt(raw_prompt: str, max_chars: int = 500) -> str:
    """
    Lam sach va thanh loc an toan cho prompt video:
    - Loai bo cac tham so Midjourney nhu --ar 9:16, --v 6
    - Chay qua bo loc an toan sanitize_prompt_safety
    - Validation do dai toi da
    """
    if not raw_prompt:
        return ""

    # Loai bo cac flag tham so
    prompt = re.sub(r"--[a-zA-Z0-9_\-:]+(?:\s+[^\s]+)?", "", raw_prompt)
    prompt = prompt.replace("`", "").strip()

    # Ap dung bo loc an toan dien anh
    prompt = sanitize_prompt_safety(prompt, max_chars=max_chars)
    return prompt

def suggest_flow_voice(content_context: str = "") -> str:
    """
    Goi y giong doc thich hop tren Google Flow:
    - Alnilam: Male, firm, mid-low pitch (Lich su, chien tranh, hao hung, trang trong)
    - Charon: Male, informative, lower pitch (Cong nghe, phan tich, huong dan)
    - Achird: Male, friendly, mid pitch (Kham pha, doi thuong, truyen cam hung)
    - Aoede: Female, breezy, mid pitch (Thu gian, cuoc song, tam su)
    - Autonoe: Female, bright, mid pitch (Nang dong, marketing, xu huong)
    """
    ctx = content_context.lower()
    if any(k in ctx for k in ["lịch sử", "chiến", "trinh sát", "liệt sĩ", "hùng", "tự hào", "quân đội", "tổ quốc"]):
        return "Alnilam"
    elif any(k in ctx for k in ["công nghệ", "ai", "chatgpt", "phần mềm", "lập trình", "hướng dẫn", "mẹo"]):
        return "Charon"
    elif any(k in ctx for k in ["nữ", "làm đẹp", "thời trang", "ẩm thực", "du lịch"]):
        return "Autonoe"
    elif any(k in ctx for k in ["tâm sự", "chữa lành", "thơ", "sách", "cảm xúc"]):
        return "Aoede"
    return "Achird"

def parse_script_to_flow_payload(script_markdown: str) -> Dict[str, Any]:
    """
    Phan tich toan bo van ban Markdown kich ban thanh danh sach phan canh doc lap (Scenes)
    va khoi prompt da duoc loc an toan san sang day vao Google Flow, ComfyUI, API Veo/Imagen.
    """
    scenes = []
    veo_blocks = []

    # 1. Trich xuat cac khoi Phân cảnh doc lap (Phan 3) - khong gop cum
    veo_sections = re.findall(
        r"###?\s*(?:Phân cảnh|Phân cảnh Veo3?|Cảnh)\s*(\d+)[^\n]*\n([\s\S]*?)(?=###?\s*(?:Phân cảnh|Phân cảnh Veo3?|Cảnh)\s*\d+|PHẦN \d+:|$)",
        script_markdown,
        re.IGNORECASE
    )

    for idx, (b_num, b_content) in enumerate(veo_sections, 1):
        num = b_num if b_num else str(idx)
        
        # Lay prompt tieng Anh da duoc thanh loc an toan
        v_match = re.search(r"\*?\s*(?:Combined Visual|Visual Description|Visual|Prompt)[^:]*:\s*[`\"]?(.*?)(?=(?:\n\s*\*|\Z))", b_content, re.IGNORECASE | re.DOTALL)
        visual_prompt = clean_veo_prompt(v_match.group(1).strip().strip("`\"")) if v_match else ""

        # Lay voiceover
        vo_match = re.search(r"\*?\s*(?:Voiceover|Dialogue)[^:]*:\s*([^\n]+)", b_content, re.IGNORECASE)
        raw_vo = vo_match.group(1) if vo_match else ""
        clean_vo_list = clean_voiceover_text(raw_vo)

        veo_blocks.append({
            "block_num": int(num),
            "visual_prompt": visual_prompt,
            "voiceover_raw": raw_vo,
            "voiceover_clean": " ".join(clean_vo_list),
            "voiceover_chunks": clean_vo_list,
            "suggested_voice": suggest_flow_voice(script_markdown[:500])
        })

    # 2. Trich xuat cac Scene le tu Storyboard table (Phan 2)
    scene_rows = re.findall(
        r"(?:Cảnh|Scene)\s*(\d+)\s*\|?\s*([0-9s\s\-\–\(\)]+)\s*\|?\s*([^\|]+)\s*\|?\s*([^\|]+)\s*\|?\s*([^\|]+)\s*\|?\s*([^\|\n]+)",
        script_markdown,
        re.IGNORECASE
    )

    for row in scene_rows:
        s_num, s_dur, s_vis, s_vo, s_txt, s_sfx = row
        clean_vo_list = clean_voiceover_text(s_vo)
        scenes.append({
            "scene_num": int(s_num),
            "duration": s_dur.strip(),
            "visual_prompt": clean_veo_prompt(s_vis),
            "voiceover_raw": s_vo.strip(),
            "voiceover_clean": " ".join(clean_vo_list),
            "voiceover_chunks": clean_vo_list,
            "flash_text": s_txt.strip(),
            "sfx_bgm": s_sfx.strip(),
            "suggested_voice": suggest_flow_voice(script_markdown[:500])
        })

    # 3. Trich xuat danh sach nhan vat (Characters & Consistency)
    characters = []
    char_matches = re.findall(
        r"(?:[-*•]|\d+\.)\s*(?:\*\*)?(?:Nhân vật|Character|Diễn viên)?\s*([A-Za-zÀ-ỹ0-9\s_-]+)(?:\*\*)?\s*:\s*([^\n]+)",
        script_markdown,
        re.IGNORECASE
    )
    for c_name, c_desc in char_matches:
        name_clean = c_name.strip().strip("*")
        if len(name_clean) > 2 and not name_clean.lower().startswith("visual") and not name_clean.lower().startswith("voiceover"):
            characters.append({
                "name": name_clean,
                "description": c_desc.strip(),
                "flow_prompt": f"Character consistency: {name_clean}. {c_desc.strip()}"
            })

    return {
        "title": "Google Flow Production Payload",
        "suggested_voice": suggest_flow_voice(script_markdown[:500]),
        "total_scenes": len(scenes),
        "total_veo_blocks": len(veo_blocks),
        "total_characters": len(characters),
        "characters": characters,
        "veo_blocks": veo_blocks,
        "scenes": scenes
    }
