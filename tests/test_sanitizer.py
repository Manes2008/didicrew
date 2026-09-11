import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.tools.google_flow_sanitizer import clean_voiceover_text, clean_veo_prompt, suggest_flow_voice


def test_sanitizer():
    voice = suggest_flow_voice("Ký ức trinh sát - Nụ cười bất tử")
    assert voice == "Alnilam", f"Expected Alnilam, got {voice}"

    sample_vo = '[NARRATOR]: "24 tuổi, người trinh sát xông pha qua 15 trận tử chiến." *(11 từ)*'
    clean_vo = clean_voiceover_text(sample_vo)
    assert clean_vo == ["24 tuổi, người trinh sát xông pha qua 15 trận tử chiến."], f"Unexpected clean_vo: {clean_vo}"

    sample_prompt = "Cinematic documentary style, shot on Arri Alexa 35mm lens. --ar 9:16"
    clean_p = clean_veo_prompt(sample_prompt)
    assert "--ar" not in clean_p, f"Unexpected clean_p: {clean_p}"
    print("[SUCCESS] All sanitizer tests passed!")

if __name__ == "__main__":
    test_sanitizer()
