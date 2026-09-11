# MIT License
# Copyright (c) 2026 Manes2008/didicrew

import os
from typing import Dict, Optional

class SkillLoader:
    """
    Quan ly va nap dong cac ky nang (Skills) tu thu muc skills/.
    Ho tro cache trong bo nho de tiet kiem I/O va giam token bang cach
    chi nap ky nang khi Agent hoac Task can su dung.
    """
    _cache: Dict[str, str] = {}
    _base_dir: str = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "skills")

    @classmethod
    def set_skills_directory(cls, path: str):
        """Thiet lap duong dan thu muc chua skills neu can tuy bien."""
        cls._base_dir = path

    @classmethod
    def find_skill_file(cls, skill_name: str) -> Optional[str]:
        """Tim kiem duong dan file SKILL.md ke ca trong thu muc long nhau hoac co hau to cloud."""
        # 1. Kiem tra truc tiep
        direct_path = os.path.join(cls._base_dir, skill_name, "SKILL.md")
        if os.path.exists(direct_path):
            return direct_path

        # 2. Quet de quy trong thu muc skills/
        if os.path.exists(cls._base_dir):
            for root, dirs, files in os.walk(cls._base_dir):
                if "SKILL.md" in files:
                    dir_name = os.path.basename(root)
                    # Khop ten truc tiep hoac ten dang skill_name__cloud_...
                    if dir_name == skill_name or dir_name.startswith(f"{skill_name}__cloud_"):
                        return os.path.join(root, "SKILL.md")
        return None

    @classmethod
    def load_skill(cls, skill_name: str, force_reload: bool = False) -> str:
        """
        Doc va tra ve noi dung Markdown cua SKILL.md.
        """
        if not force_reload and skill_name in cls._cache:
            return cls._cache[skill_name]

        skill_path = cls.find_skill_file(skill_name)
        if not skill_path:
            raise FileNotFoundError(f"Ky nang '{skill_name}' khong ton tai trong thu muc: {cls._base_dir}")

        with open(skill_path, "r", encoding="utf-8") as f:
            content = f.read()

        cls._cache[skill_name] = content
        return content

    @classmethod
    def inject_skill_to_prompt(cls, prompt_template: str, skill_name: str, placeholder: str = "{skill_instructions}") -> str:
        """
        Tiem huong dan cua skill vao prompt_template tai vi tri placeholder.
        """
        skill_content = cls.load_skill(skill_name)
        return prompt_template.replace(placeholder, skill_content)

    @classmethod
    def list_available_skills(cls) -> list[str]:
        """Liet ke tat ca cac ky nang co san trong thu muc skills/ (ho tro quet de quy)."""
        if not os.path.exists(cls._base_dir):
            return []
        skills = set()
        for root, dirs, files in os.walk(cls._base_dir):
            if "SKILL.md" in files:
                dir_name = os.path.basename(root)
                clean_name = dir_name.split("__cloud_")[0]
                skills.add(clean_name)
        return sorted(list(skills))

