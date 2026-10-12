#!/usr/bin/env python3
"""Imagem de compartilhamento (OG) de cada post do blog: JPG 1200x675 com menos de 300 KB.

    python3 tools/seo/og.py

WebP e PNG não aparecem em todas as redes (LinkedIn e WhatsApp antigos mostram o link sem
imagem), e Facebook e Google Discover pedem 1200 px de largura. Para cada post:
- se a og:image já é um JPG 1200x675 abaixo de 300 KB, fica como está;
- se ao lado dela há um .jpg com o mesmo nome nesse padrão, passa a usar esse .jpg;
- senão, gera assets/img/blog/<slug>/<slug>-og.jpg a partir da maior versão da imagem
  (png, jpg ou webp com o mesmo nome, com ou sem o sufixo -og), recortada em 16:9.
  tools/seo/og.json troca a fonte ou o ponto de foco: {"<slug>": {"fonte": "...", "foco": [x, y]}}.
Depois alinha og:image (e secure_url), largura, altura e tipo, twitter:image e a image do
JSON-LD BlogPosting. Não mexe em datas. Idempotente: o JPG só é gerado se ainda não existir
(apague o arquivo para gerar de novo).
"""
import json
import re
from pathlib import Path
from urllib.parse import quote, unquote

from PIL import Image, ImageOps

RAIZ = Path(__file__).resolve().parents[2]
SITE = "https://libras.se"
W, H = 1200, 675
LIMITE = 300 * 1024
CFG = json.loads((RAIZ / "tools/seo/og.json").read_text()) if (RAIZ / "tools/seo/og.json").exists() else {}
LD = re.compile(r'<script type="application/ld\+json">([\s\S]*?)</script>')


def local(url):
    return RAIZ / unquote(url.replace(SITE + "/", "", 1)).lstrip("/")


def publica(p):
    return SITE + "/" + quote(p.relative_to(RAIZ).as_posix())


def no_padrao(p):
    if p.suffix.lower() not in (".jpg", ".jpeg") or not p.exists() or p.stat().st_size >= LIMITE:
        return False
    with Image.open(p) as im:
        return im.size == (W, H)


def fonte(slug, og):
    if slug in CFG and CFG[slug].get("fonte"):
        return RAIZ / CFG[slug]["fonte"].lstrip("/")
    stems = {og.stem, re.sub(r"-og$", "", og.stem)}
    cands = [og] + [og.with_name(s + e) for s in stems for e in (".png", ".jpg", ".jpeg", ".webp", ".PNG", ".JPG")]
    cands = [c for c in dict.fromkeys(cands) if c.exists() and c.suffix.lower() != ".avif"]

    def tam(c):  # a maior; no empate, png > jpg > webp
        with Image.open(c) as im:
            return (im.width, {".png": 2, ".jpg": 1, ".jpeg": 1}.get(c.suffix.lower(), 0))
    return max(cands, key=tam)


def gera(src, dest, foco):
    im = ImageOps.exif_transpose(Image.open(src))
    if im.mode in ("RGBA", "LA", "P"):
        im = im.convert("RGBA")
        fundo = Image.new("RGB", im.size, "white")
        fundo.paste(im, mask=im.split()[3])
        im = fundo
    im = im.convert("RGB")
    if im.width < W:
        print(f"  ! {src.relative_to(RAIZ)} tem {im.width}px: ampliada para {W}px")
    r = max(W / im.width, H / im.height)
    im = im.resize((max(W, round(im.width * r)), max(H, round(im.height * r))), Image.LANCZOS)
    x, y = round((im.width - W) * foco[0]), round((im.height - H) * foco[1])
    im = im.crop((x, y, x + W, y + H))
    dest.parent.mkdir(parents=True, exist_ok=True)
    for q in (86, 82, 78, 74, 70, 65, 60):
        im.save(dest, "JPEG", quality=q, optimize=True, progressive=True)
        if dest.stat().st_size < LIMITE:
            break
    print(f"  + {dest.relative_to(RAIZ)} ({dest.stat().st_size // 1024} KB, q{q}) de {src.relative_to(RAIZ)}")


def meta(t, prop, valor, depois_de):
    """Troca o content de <meta property=prop>; se não existir, cria logo depois de depois_de."""
    pad = re.compile(rf'(<meta property="{re.escape(prop)}" content=")[^"]*(">)')
    if pad.search(t):
        return pad.sub(lambda m: m[1] + valor + m[2], t, count=1)
    ancora = re.search(rf'<meta property="{re.escape(depois_de)}" content="[^"]*">\n?', t)
    return t[:ancora.end()] + f'<meta property="{prop}" content="{valor}">\n' + t[ancora.end():]


def main():
    mudou = 0
    for f in sorted((RAIZ / "blog").glob("*/index.html")):
        slug = f.parent.name
        t = f.read_text()
        if 'http-equiv="refresh"' in t or slug in ("todos", "temas"):
            continue
        m = re.search(r'<meta property="og:image" content="([^"]+)"', t)
        if not m:
            print(f"  ! {slug} sem og:image")
            continue
        og = local(m[1])
        if no_padrao(og):
            final = og
        elif no_padrao(og.with_suffix(".jpg")):
            final = og.with_suffix(".jpg")
        else:
            final = RAIZ / f"assets/img/blog/{slug}/{slug}-og.jpg"
            if not final.exists():
                gera(fonte(slug, og), final, CFG.get(slug, {}).get("foco", (.5, .5)))
        url = publica(final)
        novo = meta(t, "og:image", url, "og:image")
        if 'property="og:image:secure_url"' in novo:
            novo = meta(novo, "og:image:secure_url", url, "og:image")
        novo = meta(novo, "og:image:width", str(W), "og:image")
        novo = meta(novo, "og:image:height", str(H), "og:image:width")
        novo = meta(novo, "og:image:type", "image/jpeg", "og:image:height")
        novo = re.sub(r'(<meta name="twitter:image" content=")[^"]*(">)', lambda m: m[1] + url + m[2], novo, count=1)
        for bruto in LD.findall(novo):
            if '"BlogPosting"' not in bruto:
                continue
            bp = json.loads(bruto)
            img = {"@type": "ImageObject", "url": url, "width": W, "height": H}
            if bp.get("image") != img:
                bp["image"] = img
                multi = "\n" in bruto.strip()
                ld = json.dumps(bp, ensure_ascii=False, indent=2 if multi else None, separators=None if multi else (",", ":"))
                novo = novo.replace(bruto, ("\n" + ld + "\n") if multi else ld, 1)
            break
        if novo != t:
            f.write_text(novo)
            mudou += 1
    print(f"ok  OG em JPG {W}x{H}: {mudou} posts atualizados")


if __name__ == "__main__":
    main()
