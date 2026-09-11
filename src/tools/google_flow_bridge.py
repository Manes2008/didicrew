# MIT License
# Copyright (c) 2026 Manes2008/didicrew

import os
import time
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any, List

class GoogleFlowBridge:
    """
    Bridge tu dong hoa Playwright ket noi giua VideoCrew va Google Flow.
    Ho tro hai che do:
    1. CDP Port: Ket noi truc tiep vao cua so Chrome dang chay voi --remote-debugging-port=9222
    2. Persistent Context: Khoi chay Chromium voi Profile rieng (.chrome_profile)
    """

    def __init__(self, project_url: Optional[str] = None, debug_port: int = 9222):
        self.project_url = project_url or os.getenv("GOOGLE_FLOW_PROJECT_URL", "")
        self.debug_port = int(os.getenv("GOOGLE_CHROME_DEBUG_PORT", str(debug_port)))
        self.profile_dir = Path(".chrome_profile").resolve()
        self.browser = None
        self.context = None
        self.page = None

    async def connect(self, headless: Optional[bool] = None):
        """Khoi tao ket noi toi trinh duyet."""
        from playwright.async_api import async_playwright
        self.pw = await async_playwright().start()

        # Tu dong phat hien headless neu dang chay trong Docker Linux khong co $DISPLAY
        if headless is None:
            headless = bool(os.name != "nt" and "DISPLAY" not in os.environ)

        # 1. Thu ket noi qua CDP port (localhost hoac host.docker.internal)
        cdp_hosts = ["127.0.0.1", "localhost", "host.docker.internal"]
        for h in cdp_hosts:
            try:
                cdp_url = f"http://{h}:{self.debug_port}"
                self.browser = await self.pw.chromium.connect_over_cdp(cdp_url, timeout=1500)
                if self.browser.contexts:
                    self.context = self.browser.contexts[0]
                    if self.context.pages:
                        self.page = self.context.pages[0]
                    else:
                        self.page = await self.context.new_page()
                else:
                    self.context = await self.browser.new_context()
                    self.page = await self.context.new_page()
                print(f"[INFO] Da ket noi thanh cong vao Chrome Host tai {cdp_url}")
                return True
            except Exception:
                continue

        # 2. Neu khong co CDP port, mo Chromium voi profile rieng
        print(f"[INFO] Khong tim thay Chrome CDP port {self.debug_port}. Khoi chay Dedicated Profile (headless={headless}) tai {self.profile_dir}")
        self.profile_dir.mkdir(parents=True, exist_ok=True)
        self.context = await self.pw.chromium.launch_persistent_context(
            user_data_dir=str(self.profile_dir),
            headless=headless,
            viewport={"width": 1440, "height": 900},
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage"
            ]
        )
        if self.context.pages:
            self.page = self.context.pages[0]
        else:
            self.page = await self.context.new_page()
        return True


    async def open_project(self, target_url: Optional[str] = None):
        """Mo du an Google Flow tren trinh duyet."""
        url = target_url or self.project_url
        if not url:
            raise ValueError("Chua cau hinh URL du an Google Flow (GOOGLE_FLOW_PROJECT_URL)")

        if not self.page:
            await self.connect()

        current_url = self.page.url
        if url not in current_url:
            print(f"[INFO] Dang dieu huong toi du an: {url}")
            await self.page.goto(url, wait_until="domcontentloaded", timeout=60000)
            await asyncio.sleep(3)

    async def push_video_prompt(self, visual_prompt: str) -> bool:
        """Dien prompt vao o tao video cua Google Flow va gui lenh."""
        if not self.page:
            return False

        try:
            # Tim o input 'Ban muon tao gi?' hoac textarea tuong duong
            input_box = await self.page.wait_for_selector(
                "textarea, input[type='text'], div[contenteditable='true']",
                timeout=10000
            )
            if input_box:
                await input_box.click()
                await input_box.fill(visual_prompt)
                await asyncio.sleep(0.5)
                # Nhan Enter hoac click nut Submit
                await self.page.keyboard.press("Enter")
                print(f"[OK] Da gui Prompt Veo thanh cong: {visual_prompt[:60]}...")
                await asyncio.sleep(2)
                return True
        except Exception as e:
            print(f"[WARN] Khong the gui Prompt Video: {e}")
            return False

    async def push_voiceover_clip(self, voice_text: str, voice_name: str = "Charon") -> bool:
        """Mo Voiceover Studio, chon giong doc va dien text thoai."""
        if not self.page:
            return False

        try:
            # 1. Click vao cong cu Voiceover / Giong noi neu chua mo
            voice_btn = await self.page.query_selector("text='Giọng nói', text='Voiceover Studio', button:has-text('Giọng nói')")
            if voice_btn:
                await voice_btn.click()
                await asyncio.sleep(1)

            # 2. Chon giong doc neu co
            if voice_name:
                v_target = await self.page.query_selector(f"text='{voice_name}'")
                if v_target:
                    await v_target.click()
                    await asyncio.sleep(0.5)

            # 3. Dien loi thoai vao hop thoai mau
            input_area = await self.page.query_selector("textarea, div[contenteditable='true']")
            if input_area:
                await input_area.click()
                await input_area.fill(voice_text[:120])
                await asyncio.sleep(0.5)

                # Click nut 'Them vao cau lenh'
                submit_btn = await self.page.query_selector("button:has-text('Thêm vào câu lệnh'), button:has-text('Tạo')")
                if submit_btn:
                    await submit_btn.click()
                    print(f"[OK] Da them Voiceover ({voice_name}): {voice_text[:50]}...")
                    await asyncio.sleep(1.5)
                    return True
        except Exception as e:
            print(f"[WARN] Khong the tao Voiceover tren Flow: {e}")
            return False

    async def batch_sync(self, payload: Dict[str, Any], auto_voice: bool = True) -> Dict[str, Any]:
        """Dong bo toan bo phan canh tu VideoCrew sang Google Flow."""
        await self.open_project()

        results = {
            "success_prompts": 0,
            "success_voiceovers": 0,
            "errors": []
        }

        # Uu tien day cac veo_blocks (gom cum 8s)
        items = payload.get("veo_blocks") or payload.get("scenes") or []
        default_voice = payload.get("suggested_voice", "Charon")

        for item in items:
            p_text = item.get("visual_prompt", "")
            vo_text = item.get("voiceover_clean", "")
            v_name = item.get("suggested_voice", default_voice)

            if p_text:
                ok = await self.push_video_prompt(p_text)
                if ok:
                    results["success_prompts"] += 1
                await asyncio.sleep(2)

            if auto_voice and vo_text:
                # Xu ly cac chunk nho hon 120 ky tu
                chunks = item.get("voiceover_chunks") or [vo_text[:120]]
                for c in chunks:
                    ok_vo = await self.push_voiceover_clip(c, v_name)
                    if ok_vo:
                        results["success_voiceovers"] += 1
                    await asyncio.sleep(1.5)

        return results

    async def close(self):
        """Dong ket noi."""
        if self.context:
            await self.context.close()
        if hasattr(self, "pw") and self.pw:
            await self.pw.stop()
