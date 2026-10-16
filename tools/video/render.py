"""Render the video text layers (and the link-preview image) to PNG.

Usage (from tools/video, with a server on the REPO ROOT:  python3 -m http.server 8766):
  python3 render.py 1      # text layers at 720x1280  (WhatsApp video)
  python3 render.py 1.5    # text layers at 1080x1920 (full-quality video)
  python3 render.py og     # docs/img/og-cover.jpg, the 1200x630 link preview
Output goes to data/video-build (git-ignored)."""
import asyncio, os, sys
from playwright.async_api import async_playwright

URL = "http://localhost:8766/tools/video"
BUILD = "../../data/video-build"
SCENES = ["cover", "sanctuary", "dome", "ark", "kollel", "donors", "contact"]

async def main(arg):
    os.makedirs(BUILD, exist_ok=True)
    async with async_playwright() as p:
        b = await p.chromium.launch()
        if arg == "og":
            pg = await b.new_page(viewport={"width": 1200, "height": 630})
            await pg.goto(f"{URL}/og.html")
            await pg.wait_for_selector('body[data-ready="1"]')
            await pg.wait_for_timeout(300)
            await pg.screenshot(path=f"{BUILD}/og-cover.png")
            from PIL import Image
            Image.open(f"{BUILD}/og-cover.png").convert("RGB").save(
                "../../docs/img/og-cover.jpg", quality=84, optimize=True, progressive=True)
        else:
            scale = float(arg)
            pg = await b.new_page(viewport={"width": 720, "height": 1280}, device_scale_factor=scale)
            for s in SCENES:
                await pg.goto("about:blank")
                await pg.goto(f"{URL}/overlay.html#{s}")
                await pg.wait_for_selector('body[data-ready="1"]')
                await pg.wait_for_timeout(300)
                await pg.screenshot(path=f"{BUILD}/ov{int(720 * scale)}_{s}.png", omit_background=(s != "contact"))
        await b.close()

asyncio.run(main(sys.argv[1] if len(sys.argv) > 1 else "1"))
