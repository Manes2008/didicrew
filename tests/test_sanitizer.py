import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.tools.google_flow_sanitizer import (
    clean_voiceover_text,
    clean_veo_prompt,
    suggest_flow_voice,
    parse_script_to_flow_payload
)


def test_sanitizer():
    voice = suggest_flow_voice("Ký ức trinh sát - Nụ cười bất tử")
    assert voice == "Alnilam", f"Expected Alnilam, got {voice}"

    sample_vo = '[NARRATOR]: "24 tuổi, người trinh sát xông pha qua 15 trận tử chiến." *(11 từ)*'
    clean_vo = clean_voiceover_text(sample_vo)
    assert clean_vo == ["24 tuổi, người trinh sát xông pha qua 15 trận tử chiến."], f"Unexpected clean_vo: {clean_vo}"

    sample_prompt = "Cinematic documentary style, shot on Arri Alexa 35mm lens. --ar 9:16"
    clean_p = clean_veo_prompt(sample_prompt)
    assert "--ar" not in clean_p, f"Unexpected clean_p: {clean_p}"

    sample_script = """
    # Kịch bản sản xuất
    ### Nhân vật:
    - **Nguyễn Văn A**: Chiến sĩ trinh sát 24 tuổi, mặc áo lính bạc màu, ánh mắt kiên định.
    - **Lê Thị B**: Nữ giao liên gan dạ, đội nón tai bèo.

    ### Phân cảnh Veo 1:
    * Visual Prompt: Arri Alexa 35mm, portrait of a brave soldier in the jungle. --ar 9:16
    * Voiceover: Đồng đội ơi, ngày chiến thắng đã gần kề.
    """
    payload = parse_script_to_flow_payload(sample_script)
    assert len(payload["characters"]) >= 2, f"Expected at least 2 characters, got {len(payload['characters'])}"
    assert payload["characters"][0]["name"] == "Nguyễn Văn A"
    assert len(payload["veo_blocks"]) == 1

    print("[SUCCESS] All sanitizer tests passed!")

if __name__ == "__main__":
    test_sanitizer()
