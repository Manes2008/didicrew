# MIT License
# Copyright (c) 2026 Manes2008/didicrew

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Nap bien moi truong tu .env
load_dotenv()

from openspace.cloud.config import load_cloud_config
from openspace.cloud.client import OpenSpaceClient


# Danh sach cac skill Studio chuyen nghiep can dong bo
STUDIO_SKILLS = {
    # 1. Content & Script
    "cinematic-script-writer": "ed25db1b-00b1-4b64-9e4c-f8e4a4d91dab",
    "storyboard": "ce9754e6-7c77-462e-8fdf-dd4ee3f12788",
    "viral-video-analysis": "3113c8d0-6fac-45a3-99c5-9f77a8f6642a",
    "content-strategy": "b51c916f-6d99-4359-b09c-040346e5a950",
    "content-quality-auditor": "c7c384ce-36c9-4c37-9c0f-9d51a2a577b5",
    "content-gap-analysis": "4739694f-84f8-4dd3-b655-5033251352e1",
    "content-refresher": "10a2f0ef-43dc-4095-a3df-2c6746ee267c",
    
    # 2. Visual & Image
    "visual-prompt-engine": "69965fd8-bff5-437d-8a8c-576c85ddf04f",
    "visual-concept": "baef62a8-95fd-4d38-b8d3-a51a20a8250f",
    "best-image-generation": "eb5ae2ad-9525-46ed-a58d-3f0e18ec2423",
    "blip-2-vision-language": "06a24b49-d1ba-4958-9c5a-7b5a89a14644",
    
    # 3. Audio & Voice
    "elevenlabs-tts": "3d86d7d9-f2d6-4f3f-957c-ca911632440f",
    "audiocraft-audio-generation": "c0c22a81-1a14-4e02-abc9-fa31a0c814e8",
    "audio-conductor": "77382fbd-0f81-4268-ac6c-adbaef333bdb",
    "audio-processing": "7e5f2e58-025e-4627-9aae-f7980d5b128f",
    
    # 4. Video & Editing
    "eachlabs-video-generation": "799ac745-cef5-4d18-84ad-011c29c0ff8f",
    "hyperframes": "41051059-7bf4-4d51-865e-b95dedf41291"
}

def sync_studio_skills(target_dict=None):
    """
    Dong bo tat ca cac ky nang trong he thong Studio tu OpenSpace Cloud.
    """
    if target_dict is None:
        target_dict = STUDIO_SKILLS

    config = load_cloud_config()
    client = OpenSpaceClient(config)
    output_base = Path("skills").resolve()

    print(f"[INFO] Bat dau dong bo {len(target_dict)} ky nang Studio tu OpenSpace Cloud...")
    synced_count = 0

    for name, s_id in target_dict.items():
        print(f"[INFO] Dang tai xuong: {name} (ID: {s_id})...")
        try:
            res = client.import_skill(s_id, output_base, audience="public")
            print(f"[OK] {name} -> {res.get('local_path')}")
            synced_count += 1
        except Exception as e:
            # Neu da ton tai, co the coi nhu thanh cong
            if "already_exists" in str(e):
                print(f"[SKIP] {name} da ton tai trong thu muc skills.")
                synced_count += 1
            else:
                print(f"[WARN] Khong the tai {name}: {e}")

    print(f"[DONE] Hoan tat dong bo {synced_count}/{len(target_dict)} ky nang Studio.")

if __name__ == "__main__":
    sync_studio_skills()
