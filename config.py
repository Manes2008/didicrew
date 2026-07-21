# config.py
import os
from dotenv import load_dotenv

load_dotenv(override=True)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
POLLO_API_KEY = os.getenv("POLLO_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/videocrew")

# Tự động chuyển đổi Render Internal URL thành External URL khi chạy ở local
if DATABASE_URL and "@dpg-" in DATABASE_URL and ".render.com" not in DATABASE_URL:
    if os.getenv("RENDER") != "true":
        from urllib.parse import urlparse, urlunparse
        try:
            parsed = urlparse(DATABASE_URL)
            if parsed.hostname and not parsed.hostname.endswith(".render.com"):
                # Render mặc định dùng phân vùng singapore-postgres cho máy chủ gần Việt Nam
                new_netloc = parsed.netloc.replace(parsed.hostname, f"{parsed.hostname}.singapore-postgres.render.com")
                DATABASE_URL = urlunparse(parsed._replace(netloc=new_netloc))
        except Exception:
            pass

if not OPENAI_API_KEY:
    print("⚠️ Cảnh báo: Chưa có OPENAI_API_KEY trong file .env")