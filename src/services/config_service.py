import os
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories.config_repository import ConfigRepository
from src.schemas.config_schema import SystemConfigUpdate, SystemConfigResponse
import config

class ConfigService:
    def __init__(self, db: AsyncSession):
        self.repo = ConfigRepository(db)

    async def get_system_config(self) -> SystemConfigResponse:
        openai_rec = await self.repo.get_by_key("openai_api_key")
        gemini_rec = await self.repo.get_by_key("gemini_api_key")
        provider_rec = await self.repo.get_by_key("provider")
        model_rec = await self.repo.get_by_key("model_name")
        video_rec = await self.repo.get_by_key("video_engine")
        image_rec = await self.repo.get_by_key("image_engine")

        openai_key = (openai_rec.value if openai_rec else None) or config.OPENAI_API_KEY or ""
        gemini_key = (gemini_rec.value if gemini_rec else None) or config.GEMINI_API_KEY or ""

        masked_openai = f"sk-...{openai_key[-4:]}" if len(openai_key) > 8 else None
        masked_gemini = f"AI...{gemini_key[-4:]}" if len(gemini_key) > 8 else None

        return SystemConfigResponse(
            provider=provider_rec.value if provider_rec else "OpenAI",
            model_name=model_rec.value if model_rec else "gpt-4o-mini",
            video_engine=video_rec.value if video_rec else "hunyuan",
            image_engine=image_rec.value if image_rec else "sdxl",
            has_openai_key=bool(openai_key),
            has_gemini_key=bool(gemini_key),
            masked_openai_key=masked_openai,
            masked_gemini_key=masked_gemini
        )

    async def update_system_config(self, cfg_in: SystemConfigUpdate) -> SystemConfigResponse:
        if cfg_in.openai_api_key:
            await self.repo.set_config("openai_api_key", cfg_in.openai_api_key.strip())
            os.environ["OPENAI_API_KEY"] = cfg_in.openai_api_key.strip()
        if cfg_in.gemini_api_key:
            await self.repo.set_config("gemini_api_key", cfg_in.gemini_api_key.strip())
            os.environ["GEMINI_API_KEY"] = cfg_in.gemini_api_key.strip()
        if cfg_in.provider:
            await self.repo.set_config("provider", cfg_in.provider)
        if cfg_in.model_name:
            await self.repo.set_config("model_name", cfg_in.model_name)
        if cfg_in.video_engine:
            await self.repo.set_config("video_engine", cfg_in.video_engine)
        if cfg_in.image_engine:
            await self.repo.set_config("image_engine", cfg_in.image_engine)

        return await self.get_system_config()

    async def test_api_key(self, provider: str, raw_key: Optional[str] = None) -> Dict[str, Any]:
        key_to_test = raw_key
        if not key_to_test:
            if provider.lower() == "gemini":
                rec = await self.repo.get_by_key("gemini_api_key")
                key_to_test = (rec.value if rec else None) or config.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY")
            else:
                rec = await self.repo.get_by_key("openai_api_key")
                key_to_test = (rec.value if rec else None) or config.OPENAI_API_KEY or os.getenv("OPENAI_API_KEY")

        if not key_to_test or not key_to_test.strip():
            return {
                "provider": provider,
                "is_valid": False,
                "status": "missing",
                "message": f"Chưa cấu hình API Key cho {provider}."
            }

        key_to_test = key_to_test.strip()

        if provider.lower() == "gemini":
            try:
                from google import genai
                client = genai.Client(api_key=key_to_test)
                # Test goi model nhe gemini-3.6-flash
                res = client.models.generate_content(
                    model="gemini-3.6-flash",
                    contents="ping"
                )
                return {
                    "provider": "Gemini",
                    "is_valid": True,
                    "status": "active",
                    "message": "Kết nối thành công! Gemini API Key hợp lệ và hoạt động tốt."
                }
            except Exception as e:
                err_str = str(e)
                if "RESOURCE_EXHAUSTED" in err_str:
                    return {
                        "provider": "Gemini",
                        "is_valid": True,
                        "status": "rate_limited",
                        "message": "API Key đúng nhưng đang bị giới hạn tốc độ (Rate limit/Quota)."
                    }
                return {
                    "provider": "Gemini",
                    "is_valid": False,
                    "status": "error",
                    "message": f"Lỗi xác thực Gemini API Key: {err_str[:120]}"
                }
        else: # OpenAI
            try:
                from openai import OpenAI
                client = OpenAI(api_key=key_to_test)
                client.models.list()
                return {
                    "provider": "OpenAI",
                    "is_valid": True,
                    "status": "active",
                    "message": "Kết nối thành công! OpenAI API Key hợp lệ."
                }
            except Exception as e:
                return {
                    "provider": "OpenAI",
                    "is_valid": False,
                    "status": "error",
                    "message": f"Lỗi xác thực OpenAI API Key: {str(e)[:120]}"
                }
