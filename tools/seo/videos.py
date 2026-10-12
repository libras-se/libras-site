#!/usr/bin/env python3
"""Schema VideoObject dos vídeos de cada post do blog (YouTube em fachada e vídeos próprios).

    python3 tools/seo/videos.py            # atualiza o cache e o JSON-LD dos posts
    python3 tools/seo/videos.py --offline  # não consulta o YouTube; usa só o cache

Para cada post, acha:
- fachadas do YouTube (<div class="yt-lite" data-id="...">);
- vídeos próprios (<video> que não é decorativo nem banner), com src/source e poster.
Metadados do YouTube (título, descrição, data de envio, duração) vêm do yt-dlp e ficam em
tools/seo/videos.json; a duração dos vídeos próprios vem do ffprobe. O JSON-LD é escrito
num bloco <script type="application/ld+json" data-lse="videos"> antes do </head>.
Idempotente.
"""
import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote

RAIZ = Path(__file__).resolve().parents[2]
SITE = "https://libras.se"
CACHE = RAIZ / "tools/seo/videos.json"
BLOCO = re.compile(r'\n?<script type="application/ld\+json" data-lse="videos">[\s\S]*?</script>')


def iso_duracao(seg):
    seg = int(round(float(seg)))
    h, r = divmod(seg, 3600)
    m, s = divmod(r, 60)
    return "PT" + (f"{h}H" if h else "") + (f"{m}M" if m else "") + f"{s}S"


def yt_meta(vid):
    r = subprocess.run(
        ["yt-dlp", "-j", "--skip-download", "--no-warnings", "--extractor-args", "youtube:player_client=web_embedded",
         f"https://www.youtube.com/watch?v={vid}"], capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        return None
    j = json.loads(r.stdout)
    up = j.get("upload_date") or ""
    return {
        "titulo": j.get("title"), "descricao": (j.get("description") or "").strip()[:300], "canal": j.get("channel") or j.get("uploader"),
        "data": f"{up[:4]}-{up[4:6]}-{up[6:8]}" if len(up) == 8 else None, "duracao": j.get("duration"),
    }


def local(caminho, pasta):
    p = (pasta / caminho).resolve() if not caminho.startswith("/") else RAIZ / caminho.lstrip("/")
    return p


def url_publica(arq):
    return SITE + "/" + quote(arq.relative_to(RAIZ).as_posix())


def ffprobe(arq):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=width,height", "-of", "json", str(arq)],
                       capture_output=True, text=True)
    j = json.loads(r.stdout or "{}")
    st = next((s for s in j.get("streams", []) if s.get("width")), {})
    return {"duracao": float(j.get("format", {}).get("duration", 0) or 0), "w": st.get("width"), "h": st.get("height")}


def sem_emoji(s):
    return re.sub(r"[\U0001F000-\U0001FAFF\u2600-\u27BF\uFE0F]", "", s).strip()


def texto(html):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", html)).strip()


def main():
    offline = "--offline" in sys.argv
    cache = json.loads(CACHE.read_text()) if CACHE.exists() else {"youtube": {}}
    total, sem_meta = 0, []
    for f in sorted((RAIZ / "blog").glob("*/index.html")):
        t = f.read_text()
        if 'http-equiv="refresh"' in t:
            continue
        ld = next((json.loads(b) for b in re.findall(r'<script type="application/ld\+json">([\s\S]*?)</script>', t)
                   if '"BlogPosting"' in b), None)
        if not ld:
            continue
        publicado = ld["datePublished"]
        corpo = t.split("<body", 1)[1]
        videos = []
        for vid, titulo in re.findall(r'class="yt-lite" data-id="([\w-]{11})" data-title="([^"]*)"', corpo):
            if vid not in cache["youtube"] and not offline:
                meta = yt_meta(vid)
                if meta:
                    cache["youtube"][vid] = meta
            m = cache["youtube"].get(vid)
            if not m or not m.get("data"):
                sem_meta.append(f"{f.parent.name}: {vid}")
                continue
            v = {"@type": "VideoObject", "name": m["titulo"] or titulo, "description": m["descricao"] or titulo,
                 "thumbnailUrl": f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg", "uploadDate": m["data"],
                 "embedUrl": f"https://www.youtube.com/embed/{vid}"}
            if m.get("duracao"):
                v["duration"] = iso_duracao(m["duracao"])
            videos.append(v)
        for m in re.finditer(r"<video\b([^>]*)>([\s\S]*?)</video>", corpo):
            attrs, inner = m.group(1), m.group(2)
            antes = corpo[:m.start()]
            aside = antes.rfind("<aside")
            if 'aria-hidden="true"' in attrs or (aside > antes.rfind("</aside>") and "lse-ad" in antes[aside:aside + 40]):
                continue
            srcs = re.findall(r'src="([^"]+)"', attrs + inner)
            mp4 = next((s for s in srcs if s.endswith(".mp4")), srcs[0] if srcs else None)
            poster = re.search(r'poster="([^"]+)"', attrs)
            if not mp4 or not poster:
                continue
            arq = local(mp4, f.parent)
            if not arq.exists():
                continue
            info = ffprobe(arq)
            depois = corpo[m.end():m.end() + 600]
            leg = re.search(r'<(?:figcaption|p class="video-caption")>([\s\S]*?)</(?:figcaption|p)>', depois)
            rotulo = re.findall(r'<span class="video-tag">([\s\S]*?)</span>', antes[-400:])
            nome = re.search(r'aria-label="([^"]+)"', attrs)
            legenda = sem_emoji(texto(leg.group(1)).split(" | ")[0]) if leg else None
            titulo_v = nome.group(1) if nome else (sem_emoji(texto(rotulo[-1])) if rotulo else legenda)
            v = {"@type": "VideoObject", "name": titulo_v or ld["headline"],
                 "description": legenda or ld.get("description", ld["headline"]),
                 "thumbnailUrl": url_publica(local(poster.group(1), f.parent)), "uploadDate": publicado,
                 "contentUrl": url_publica(arq)}
            if info["duracao"]:
                v["duration"] = iso_duracao(info["duracao"])
            if info["w"]:
                v["width"], v["height"] = info["w"], info["h"]
            videos.append(v)
        if videos:
            grafo = {"@context": "https://schema.org", "@graph": videos}
            bloco = f'<script type="application/ld+json" data-lse="videos">{json.dumps(grafo, ensure_ascii=False, separators=(",", ":"))}</script>'
            # atualiza no lugar (não muda a ordem do <head>); se não houver, entra antes do </head>
            novo = BLOCO.sub(lambda m: ("\n" if m[0].startswith("\n") else "") + bloco, t, count=1) if BLOCO.search(t) \
                else t.replace("</head>", bloco + "\n</head>", 1)
            total += len(videos)
        else:
            novo = BLOCO.sub("", t)
        if novo != t:
            f.write_text(novo)
    CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=1, sort_keys=True) + "\n")
    print(f"ok  {total} VideoObject nos posts")
    if sem_meta:
        print("  ! sem metadados do YouTube (rode sem --offline):", ", ".join(sem_meta))


if __name__ == "__main__":
    main()
