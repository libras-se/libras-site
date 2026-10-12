#!/usr/bin/env python3
"""Etapa 5 da auditoria do blog: mídia leve e nomes de arquivo sem espaço. Idempotente.

    python3 tools/auditoria/etapa5_midia.py

1. Renomeia os vídeos com espaço no nome (sinais de pessoas) e troca as referências.
2. Os 4 GIFs de "Libras tem sotaque" (1,6 a 2,2 MB cada) viram MP4 em loop com pôster,
   carregados só quando aparecem na tela (video.lse-loop[data-src], JS do tools/seo/links.py).
3. O vídeo do Summit em "garantir" (WebM 1080p60 de 26 MB) vira MP4 H.264 720p (6,6 MB), que todo
   navegador toca; um WebM 720p ficou do mesmo tamanho e não entraria em uso, então não há.
   O fundo do hero deixa de ter o PNG de 6,7 MB como fallback (passa ao JPG da OG).
4. Toda <picture> dos posts com WebP e sem AVIF ganha o AVIF, gerado a partir do JPG/PNG.
Rode depois os geradores (links.py reinjeta o JS; videos.py refaz o VideoObject).
"""
import re
import subprocess
from pathlib import Path
from urllib.parse import quote, unquote

from PIL import Image

RAIZ = Path(__file__).resolve().parents[2]
BLOG = RAIZ / "assets/img/blog"
PESSOAS = BLOG / "como-sao-criados-sinais-de-pessoas-na-libras"
SOTAQUE = BLOG / "libras-tem-sotaque-e-giria"
GARANTIR = BLOG / "garantir-libras-sem-improviso"

RENOMEAR = {PESSOAS / f"{a} - LIBRAS-SE_GIFS.{e}": PESSOAS / f"{b}-libras-se-gifs.{e}"
            for a, b in (("beyonce", "beyonce"), ("HUCK", "huck"), ("JOAB", "joab")) for e in ("mp4", "webm")}
GIFS = ("VERDE", "CERVEJA", "TRISTE", "MAS")


def git(*a):
    subprocess.run(["git", *a], cwd=RAIZ, check=True, capture_output=True)


def ffmpeg(*a):
    subprocess.run(["ffmpeg", "-v", "error", "-y", *a], check=True)


def publicadas():
    return [p for p in (RAIZ / "blog").glob("*/index.html")]


def renomeia():
    for velho, novo in RENOMEAR.items():
        if velho.exists() and not novo.exists():
            git("mv", str(velho.relative_to(RAIZ)), str(novo.relative_to(RAIZ)))
            print(f"  ~ {velho.name} -> {novo.name}")
    for f in publicadas():
        t = original = f.read_text()
        for velho, novo in RENOMEAR.items():
            for forma in (velho.name, quote(velho.name)):
                t = t.replace(f"{velho.parent.name}/{forma}", f"{novo.parent.name}/{novo.name}")
        if t != original:
            f.write_text(t)


def sotaque():
    f = RAIZ / "blog/libras-tem-sotaque-e-giria/index.html"
    t = original = f.read_text()
    for nome in GIFS:
        gif = SOTAQUE / f"{nome} EM LIBRAS.gif"
        base = f"{nome.lower()}-em-libras"
        mp4, poster = SOTAQUE / f"{base}.mp4", SOTAQUE / f"{base}.webp"
        if gif.exists() and not mp4.exists():
            ffmpeg("-i", str(gif), "-movflags", "+faststart", "-pix_fmt", "yuv420p", "-c:v", "libx264",
                   "-crf", "23", "-preset", "slow", "-an", "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2", str(mp4))
        if gif.exists() and not poster.exists():
            with Image.open(gif) as im:
                im.seek(0)
                im.convert("RGB").save(poster, "WEBP", quality=80, method=6)
        m = re.search(rf'<img src="[^"]*/{quote(nome + " EM LIBRAS")}\.gif" alt="([^"]*)"[^>]*>', t)
        if m:
            rotulo = re.sub(r"^GIF ", "Vídeo ", m[1])
            url = "/assets/img/blog/libras-tem-sotaque-e-giria/"
            t = t.replace(m[0], f'<video class="lse-loop" muted loop playsinline preload="none" poster="{url}{base}.webp" '
                                f'data-src="{url}{base}.mp4" width="600" height="338" aria-label="{rotulo}"></video>')
        for velho in (gif, SOTAQUE / f"{nome} EM LIBRAS.webp"):
            if velho.exists() and mp4.exists():
                git("rm", "-q", str(velho.relative_to(RAIZ)))
    t = t.replace(".sign-figure img {", ".sign-figure img, .sign-figure video {")
    t = t.replace("Os GIFs a seguir comparam", "Os vídeos curtos a seguir comparam")
    t = t.replace(">GIFs com exemplos reais de variação regional", ">vídeos com exemplos reais de variação regional")
    if t != original:
        f.write_text(t)
        print("  ~ sotaque: GIFs trocados por vídeo")


def garantir():
    velho = GARANTIR / "garantir-libras-sem-improviso-1080p.webm"
    mp4 = GARANTIR / "garantir-libras-sem-improviso-720p.mp4"
    if velho.exists() and not mp4.exists():
        ffmpeg("-i", str(velho), "-vf", "scale=-2:720,fps=30", "-c:v", "libx264", "-profile:v", "high", "-crf", "24",
               "-preset", "slow", "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-an", str(mp4))
    f = RAIZ / "blog/garantir-libras-sem-improviso/index.html"
    t = original = f.read_text()
    base = "../../assets/img/blog/garantir-libras-sem-improviso/garantir-libras-sem-improviso"
    t = t.replace(f'<source src="{base}-1080p.webm" type="video/webm">',
                  f'<source src="{base}-720p.mp4" type="video/mp4">')
    t = t.replace('<video controls playsinline preload="metadata" poster="../../assets/img/blog/garantir-libras-sem-improviso/garantir-libras-sem-improviso.webp">',
                  '<video controls playsinline preload="metadata" width="1280" height="720" poster="../../assets/img/blog/garantir-libras-sem-improviso/garantir-libras-sem-improviso.webp">')
    # fundo do hero: o fallback (navegador sem AVIF/WebP) era o PNG de 6,7 MB; passa a ser o JPG da OG (113 KB)
    t = t.replace(f'<img src="{base}.png" alt="" aria-hidden="true" fetchpriority="high" width="2732" height="1536">',
                  f'<img src="{base}-og.jpg" alt="" aria-hidden="true" fetchpriority="high" width="1280" height="720">')
    if t != original:
        f.write_text(t)
        print("  ~ garantir: vídeo em 720p e fundo do hero leve")
    if velho.exists() and mp4.exists() and "-1080p.webm" not in t:
        git("rm", "-q", str(velho.relative_to(RAIZ)))


def avif():
    n = 0
    for f in publicadas():
        t = original = f.read_text()
        if 'http-equiv="refresh"' in t:
            continue

        def troca(m):
            nonlocal n
            pic = m[0]
            if 'type="image/avif"' in pic or 'type="image/webp"' not in pic:
                return pic
            src = re.search(r'<img\b[^>]*\bsrc="([^"]+)"', pic)[1]
            arq = (f.parent / unquote(src)).resolve() if not src.startswith("/") else RAIZ / unquote(src).lstrip("/")
            if arq.suffix.lower() not in (".jpg", ".jpeg", ".png") or not arq.exists():
                return pic
            dest = arq.with_suffix(".avif")
            if not dest.exists():
                with Image.open(arq) as im:
                    im.convert("RGB").save(dest, "AVIF", quality=55, speed=4)
                n += 1
            url = src[: -len(Path(src).suffix)] + ".avif"
            return pic.replace('<source srcset=', f'<source srcset="{url}" type="image/avif"><source srcset=', 1)
        t = re.sub(r"<picture>[\s\S]*?</picture>", troca, t)
        if t != original:
            f.write_text(t)
    print(f"  + {n} AVIF gerados")


def main():
    renomeia()
    sotaque()
    garantir()
    avif()
    print("ok  etapa 5 (mídia)")


if __name__ == "__main__":
    main()
