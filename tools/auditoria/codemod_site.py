#!/usr/bin/env python3
"""Correções mecânicas do site inteiro, da auditoria de outubro de 2026.

    python3 tools/auditoria/codemod_site.py           # aplica
    python3 tools/auditoria/codemod_site.py --check   # só conta o que mudaria (sai com erro se algo mudaria)

Idempotente: rodar de novo não muda nada. Alcança as páginas publicadas, os templates e partials
que geram páginas (tools/blog/home.html, tools/sinais/*, tools/aprender/*) e os blocos canônicos
do CLAUDE.md da raiz e do blog/CLAUDE.md, para que páginas novas já nasçam certas.

O que faz:
  favicon      ícone de 1080 px (170 KB) → 32 px; apple-touch-icon de 180 px
  barra        href interno sem barra final que aponta para pasta → com barra (evita um 301)
  rodape-css   contraste do rodapé (links .46 → .72, títulos .25 → .6, linha final → .6, apresentação → .66)
  rodape-h4    títulos do rodapé deixam de ser <h4> (pulavam a hierarquia) e viram <p class="ft-h">
  aria         div com aria-label e sem papel ganha role="group" (redes sociais, tags, kicker)
  body         <body> duplicado
  emoji-lbl    📰 do rótulo "Blog LIBRAS.SE"
  https        links externos em http:// que já respondem em https
  publisher    publisher do BlogPosting = Organization única, com @id, logo leve e redes
  youtube      iframe do YouTube → fachada leve (miniatura; o player só carrega no clique)
  speculation  prefetch moderado dos links do blog (navegação instantânea no Chrome)
  busca        botão de envio, visualmente oculto, nos formulários de busca da home do blog
  feed         <link rel="alternate"> do feed Atom (blog/feed.xml) no <head> das páginas do blog
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
NAO_PUBLICADO = ("tools/", "scripts/", "og/", "emails/", "audit/", "crm/", "CLIENTES/", "cogna 2026/", "node_modules/")
TEMPLATES = [
    "tools/blog/home.html",
    "tools/sinais/template-sinal.html",
    "tools/sinais/partials/header.html",
    "tools/sinais/partials/footer.html",
    "tools/sinais/partials/footer.css",
    "tools/sinais/partials/header.css",
    "tools/aprender/base.css",
    "tools/aprender/build.py",
    "CLAUDE.md",
    "blog/CLAUDE.md",
]
ICONE = '<link rel="icon" href="/assets/img/favicon/cropped-FAVICONpng-1-32x32.png">'
TOQUE = '<link rel="apple-touch-icon" href="/assets/img/favicon/cropped-FAVICONpng-1-180x180.png">'
ORG = {
    "@type": "Organization",
    "@id": "https://libras.se/#organization",
    "name": "LIBRAS.SE",
    "url": "https://libras.se/",
    "logo": {
        "@type": "ImageObject",
        "url": "https://libras.se/assets/img/favicon/cropped-FAVICONpng-1-512x512.png",
        "width": 512,
        "height": 512,
    },
    "sameAs": [
        "https://instagram.com/libras.se",
        "https://youtube.com/@librasse",
        "https://linkedin.com/company/librasse",
        "https://facebook.com/librasse",
        "https://tiktok.com/@libras.se",
    ],
}
HTTPS = {
    "http://www.planalto.gov.br/": "https://www.planalto.gov.br/",
    "http://www.mpf.mp.br/": "https://www.mpf.mp.br/",
    "http://www.angra.rj.gov.br/": "https://www.angra.rj.gov.br/",
    "http://www.osaogoncalo.com.br/": "https://www.osaogoncalo.com.br/",
}
SPECULATION = ('<script type="speculationrules">{"prefetch":[{"where":{"and":[{"href_matches":"/blog/*"},'
               '{"not":{"href_matches":"/blog/feed.xml"}}]},"eagerness":"moderate"}]}</script>')
YT_CSS = (
    '<style id="yt-lite-css">.yt-lite{position:relative;display:block;width:100%;aspect-ratio:16/9;'
    'background:#0e3538;overflow:hidden;cursor:pointer;border:0;padding:0}'
    '.yt-lite img{width:100%;height:100%;object-fit:cover;display:block}'
    '.yt-lite button{position:absolute;inset:0;margin:auto;width:72px;height:50px;border:0;border-radius:14px;'
    'background:rgba(14,53,56,.88);cursor:pointer;transition:background .2s}'
    '.yt-lite button::before{content:"";position:absolute;left:29px;top:15px;border-style:solid;'
    'border-width:10px 0 10px 18px;border-color:transparent transparent transparent #fff}'
    '.yt-lite:hover button,.yt-lite button:focus-visible{background:#1a9ca4}'
    '.yt-lite button:focus-visible{outline:3px solid #4fd1c5;outline-offset:3px}'
    '.yt-lite iframe{position:absolute;inset:0;width:100%;height:100%;border:0}'
    '.pa-video__frame .yt-lite{position:absolute;inset:0;aspect-ratio:auto;height:100%}</style>'
)
YT_JS = '<script src="/assets/js/yt-lite.js" defer></script>'
FEED = '<link rel="alternate" type="application/atom+xml" title="Blog LIBRAS.SE" href="https://libras.se/blog/feed.xml">'


def arquivos():
    for f in sorted(RAIZ.rglob("*.html")):
        rel = f.relative_to(RAIZ).as_posix()
        if rel.startswith(NAO_PUBLICADO) or "/." in "/" + rel:
            continue
        t = f.read_text(errors="ignore")
        if 'http-equiv="refresh"' in t:
            continue
        yield f
    for rel in TEMPLATES:
        f = RAIZ / rel
        if f.exists():
            yield f


def e_post(f):
    rel = f.relative_to(RAIZ).as_posix()
    return rel.startswith("blog/") and rel.count("/") == 2 and rel.endswith("/index.html") \
        and rel.split("/")[1] not in ("todos", "temas")


# --- operações: recebem (texto, arquivo) e devolvem (texto, n de trocas)

def op_favicon(t, f):
    t, n = re.subn(r'<link\b[^>]*\brel="icon"[^>]*FAVICONpng\.png[^>]*>', ICONE, t)
    if ICONE in t and "apple-touch-icon" not in t:
        t = t.replace(ICONE, ICONE + "\n" + TOQUE, 1)
        n += 1
    return t, n


def op_toque_corrige(t, f):
    novo = re.sub(r'<link\b[^>]*\brel="apple-touch-icon"[^>]*>', TOQUE, t)
    return novo, int(novo != t)


def op_barra(t, f):
    def troca(m):
        aspas, url = m.group(1), m.group(2)
        u = re.match(r"(https://libras\.se)?(/[^\"'#?]*?)([#?][^\"']*)?$", url)
        if not u or not u.group(2) or u.group(2).endswith("/") or "." in u.group(2).rsplit("/", 1)[-1]:
            return m.group(0)
        pasta = RAIZ / u.group(2).strip("/")
        if not (pasta / "index.html").exists():
            return m.group(0)
        return f'href={aspas}{u.group(1) or ""}{u.group(2)}/{u.group(3) or ""}{aspas}'
    novo = re.sub(r'href=(["\'])((?:https://libras\.se)?/[^"\'\s]*)\1', troca, t)
    return novo, sum(1 for a, b in zip(re.findall(r'href=["\'][^"\']*', t), re.findall(r'href=["\'][^"\']*', novo)) if a != b)


def op_rodape_css(t, f):
    n = 0

    def links(m):
        return m.group(0).replace("rgba(255,255,255,.46)", "rgba(255,255,255,.72)")

    def titulos(m):
        r = m.group(0).replace(".ft-col h4", ".ft-col .ft-h").replace("rgba(255,255,255,.25)", "rgba(255,255,255,.6)")
        return re.sub(r"margin-bottom:(\d+px)", r"margin:0 0 \1", r)

    def final(m):
        return re.sub(r"rgba\(255,255,255,\.(22|42)\)", "rgba(255,255,255,.6)", m.group(0))

    def apresentacao(m):
        return re.sub(r"rgba\(255,255,255,\.(3\d|4\d)\)", "rgba(255,255,255,.66)", m.group(0))

    for padrao, fn in ((r"\.ft-col ul a\s*\{[^}]*\}", links), (r"\.ft-col h4\s*\{[^}]*\}", titulos),
                       (r"\.ft-bot p\s*\{[^}]*\}", final), (r"\.ft-bp\s*\{[^}]*\}", apresentacao)):
        novo = re.sub(padrao, fn, t)
        n += int(novo != t)
        t = novo
    return t, n


def op_rodape_h4(t, f):
    def dentro(m):
        return m.group(0).replace("<h4>", '<p class="ft-h">').replace("</h4>", "</p>")
    novo = re.sub(r'<footer id="foot"[\s\S]*?</footer>', dentro, t)
    if f.name == "footer.html":
        novo = novo.replace("<h4>", '<p class="ft-h">').replace("</h4>", "</p>")
    return novo, novo.count('class="ft-h"') - t.count('class="ft-h"')


def op_aria(t, f):
    novo = re.sub(r'<div class="(ft-socs|pa-tags|pa-tags-alt reveal|hero-kicker)" aria-label=',
                  r'<div class="\1" role="group" aria-label=', t)
    return novo, len(re.findall(r'role="group" aria-label=', novo)) - len(re.findall(r'role="group" aria-label=', t))


def op_body(t, f):
    novo = re.sub(r"<body>(\s*)<body>", r"<body>\1", t)
    return novo, int(novo != t)


def op_emoji_lbl(t, f):
    novo = t.replace('<span aria-hidden="true">📰</span> ', "")
    return novo, int(novo != t)


def op_https(t, f):
    novo = t
    for a, b in HTTPS.items():
        novo = novo.replace(a, b)
    return novo, int(novo != t)


def op_publisher(t, f):
    if not e_post(f):
        return t, 0
    n = 0

    def troca(m):
        nonlocal n
        bruto = m.group(1)
        try:
            j = json.loads(bruto)
        except Exception:
            return m.group(0)
        if not (isinstance(j, dict) and j.get("@type") == "BlogPosting") or j.get("publisher") == ORG:
            return m.group(0)
        j["publisher"] = ORG
        n += 1
        multilinha = "\n" in bruto.strip()
        novo = json.dumps(j, ensure_ascii=False, indent=2 if multilinha else None,
                          separators=None if multilinha else (",", ":"))
        return m.group(0).replace(bruto, ("\n" + novo + "\n") if multilinha else novo)
    novo = re.sub(r'<script type="application/ld\+json">([\s\S]*?)</script>', troca, t)
    return novo, n


def op_youtube(t, f):
    n = 0

    def troca(m):
        nonlocal n
        tag = m.group(0)
        src = re.search(r'src="https://www\.youtube(?:-nocookie)?\.com/embed/([\w-]{11})([^"]*)"', tag)
        if not src:
            return tag
        vid, params = src.group(1), src.group(2).lstrip("?")
        titulo = (re.search(r'title="([^"]*)"', tag) or [None, "Vídeo do YouTube"])[1]
        n += 1
        extra = f' data-params="{params}"' if params else ""
        return (f'<div class="yt-lite" data-id="{vid}" data-title="{titulo}"{extra}>'
                f'<img src="https://i.ytimg.com/vi/{vid}/hqdefault.jpg" alt="" loading="lazy" decoding="async" width="480" height="360">'
                f'<button type="button" aria-label="Assistir ao vídeo: {titulo}"></button>'
                f'<noscript><a href="https://www.youtube.com/watch?v={vid}">Assistir no YouTube: {titulo}</a></noscript></div>')
    novo = re.sub(r"<iframe\b[^>]*youtube[^>]*>\s*</iframe>", troca, t, flags=re.S)
    if 'class="yt-lite"' in novo:
        if 'id="yt-lite-css"' not in novo:
            novo = novo.replace("</head>", YT_CSS + "\n</head>", 1)
        if YT_JS not in novo:
            novo = novo.replace("</body>", YT_JS + "\n</body>", 1)
    return novo, n


def op_speculation(t, f):
    rel = f.relative_to(RAIZ).as_posix()
    if not (e_post(f) or rel == "tools/blog/home.html") or '"speculationrules"' in t:
        return t, 0
    return t.replace("</head>", SPECULATION + "\n</head>", 1), 1


def op_busca(t, f):
    if f.relative_to(RAIZ).as_posix() != "tools/blog/home.html":
        return t, 0
    novo = re.sub(r'(<form class="busca"[\s\S]*?)(\s*</form>)',
                  lambda m: m.group(0) if 'type="submit"' in m.group(1) else m.group(1) + '\n              <button type="submit" class="sr">Buscar</button>' + m.group(2), t)
    return novo, novo.count('type="submit" class="sr"') - t.count('type="submit" class="sr"')


def op_feed(t, f):
    rel = f.relative_to(RAIZ).as_posix()
    if not ((rel.startswith("blog/") and rel.endswith("index.html")) or rel == "tools/blog/home.html") \
            or "application/atom+xml" in t or "</head>" not in t:
        return t, 0
    return t.replace("</head>", FEED + "\n</head>", 1), 1


OPS = [
    ("favicon", op_favicon), ("touch-icon", op_toque_corrige), ("barra", op_barra), ("rodape-css", op_rodape_css),
    ("rodape-h4", op_rodape_h4), ("aria", op_aria), ("body", op_body), ("emoji-lbl", op_emoji_lbl),
    ("https", op_https), ("publisher", op_publisher), ("youtube", op_youtube), ("speculation", op_speculation),
    ("busca", op_busca), ("feed", op_feed),
]


def main():
    check = "--check" in sys.argv
    total, por_arquivo = Counter(), Counter()
    vistos = set()
    for f in arquivos():
        if f in vistos:
            continue
        vistos.add(f)
        t = original = f.read_text()
        for nome, op in OPS:
            t, n = op(t, f)
            if n:
                total[nome] += n
        if t != original:
            por_arquivo[f.relative_to(RAIZ).as_posix()] += 1
            if not check:
                f.write_text(t)
    for nome, _ in OPS:
        print(f"  {total[nome]:5}  {nome}")
    print(f"{len(por_arquivo)} arquivo(s) {'mudariam' if check else 'alterados'}")
    if check and por_arquivo:
        sys.exit(1)


if __name__ == "__main__":
    main()
