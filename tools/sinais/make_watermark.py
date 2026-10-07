"""Gera tools/sinais/marca-dagua.png: "LIBRAS.SE" em Museo Sans Rounded 1000 com o gradiente --gb, fundo transparente.

Uso: uv run --python 3.12 --with playwright,pillow tools/sinais/make_watermark.py
Renderiza no Chrome instalado (channel=chrome) para ficar idêntico ao logo do site.
"""
import asyncio
import base64
from pathlib import Path

from PIL import Image
from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).with_name("marca-dagua.png")
FONT = "data:font/woff2;base64," + base64.b64encode((ROOT / "assets/fonts/museo-sans-rounded-1000.woff2").read_bytes()).decode()
HTML = f"""<!doctype html><html><head><style>
@font-face{{font-family:'M';src:url('{FONT}') format('woff2');font-weight:1000}}
html,body{{margin:0;background:transparent}}
span{{display:inline-block;padding:20px 24px;font-family:'M';font-weight:1000;font-size:160px;line-height:1;letter-spacing:-.02em;
background:linear-gradient(130deg,#1aa8b0 0%,#4fd1c5 50%,#81e6d9 100%);-webkit-background-clip:text;background-clip:text;
-webkit-text-fill-color:transparent;color:transparent}}
</style></head><body><span id="t">LIBRAS.SE</span></body></html>"""


async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch(channel="chrome", headless=True)
        page = await br.new_page(device_scale_factor=1)
        await page.set_content(HTML)
        await page.evaluate("document.fonts.ready")
        assert await page.evaluate("document.fonts.check(\"1000 160px M\")"), "fonte não carregou"
        await page.wait_for_timeout(300)
        await page.locator("#t").screenshot(path=str(OUT), omit_background=True)
        await br.close()
    im = Image.open(OUT)
    im.crop(im.getbbox()).save(OUT, optimize=True)
    print(OUT, Image.open(OUT).size)


asyncio.run(main())
