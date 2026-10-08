#!/usr/bin/env python3
"""Gera as páginas das áreas educativas (Aprender Libras, Cultura Surda, Atividades,
Materiais e Jogos) a partir de tools/aprender/paginas/*.html.

Cada fonte começa com um bloco <!--META {json} META--> e traz o <style>, o <main> e o
<script> próprios da página. Header, footer, fontes, variáveis e JS de navegação vêm dos
mesmos partials canônicos usados pelas páginas de sinal (tools/sinais/partials/).

Uso:  python3 tools/aprender/build.py          (gera tudo)
      python3 tools/aprender/build.py jogos     (só as fontes cujo nome começa com "jogos")
"""
import html
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
SITE = "https://libras.se"
PARTIALS = {p.stem + "_" + p.suffix[1:]: p.read_text() for p in (ROOT / "tools/sinais/partials").iterdir() if p.is_file()}
BASE_CSS = (HERE / "base.css").read_text()
SKIP = '<a href="#main-content" class="skip-link">Pular para o conteúdo principal</a>'

GTM = """<!-- Google Tag Manager -->
<script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
})(window,document,'script','dataLayer','GTM-WZ7MN3KX');</script>
<!-- End Google Tag Manager -->"""

GTM_NOSCRIPT = ('<noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-WZ7MN3KX" '
                'height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>')


def esc(s):
    return html.escape(s, quote=True)


def sinais_jogos():
    """Sinais com vídeo publicado, no formato enxuto que os jogos usam."""
    data = json.loads((ROOT / "sinal/sinais.json").read_text())
    out = []
    for s in data["sinais"]:
        if not (ROOT / f"assets/videos/sinais/{s['slug']}.mp4").exists():
            continue
        out.append({"s": s["slug"], "p": s["palavra"], "c": s["categoria"],
                    "i": (ROOT / f"assets/img/sinais/{s['slug']}.webp").exists()})
    return out


AREAS = [("Aprender Libras", "/aprender-libras/"), ("Vocabulário em vídeo", "/sinal/"), ("Sinais básicos", "/aprender-libras/sinais-basicos/"),
         ("Alfabeto", "/aprender-libras/alfabeto-em-libras/"),
         ("Jogos", "/jogos/"), ("Atividades", "/atividades/"), ("Materiais", "/materiais/"),
         ("Cultura surda", "/cultura-surda/"), ("Glossário", "/glossario/")]


def areas_nav(url):
    """Faixa de navegação entre as áreas educativas, logo abaixo do hero."""
    links = []
    for n, u in AREAS:
        atual = url == u or (u != "/aprender-libras/" and url.startswith(u))
        links.append(f'<a href="{u}"' + (' aria-current="page"' if atual else "") + f">{esc(n)}</a>")
    return ('<nav class="areas-strip no-print" aria-label="Áreas para aprender Libras"><div class="w"><div class="areas-nav">'
            + "".join(links) + "</div></div></nav>")


def cards_sinais(slugs):
    """Cartões estáticos (indexáveis) de sinais com vídeo: {{SINAIS:agua,casa,...}} na fonte."""
    por_slug = {s["slug"]: s for s in json.loads((ROOT / "sinal/sinais.json").read_text())["sinais"]}
    out = []
    for slug in slugs.split(","):
        s = por_slug[slug]
        assert (ROOT / f"assets/videos/sinais/{slug}.mp4").exists(), f"sinal sem vídeo: {slug}"
        out.append(f"""<a class="sb-card" href="/sinal/{slug}/" data-video="/assets/videos/sinais/{slug}.mp4">
  <span class="sb-vis"><img src="/assets/videos/sinais/{slug}.webp" alt="Intérprete fazendo o sinal de {esc(s['palavra'])} em Libras" width="1280" height="720" loading="lazy" decoding="async"></span>
  <span class="sb-txt"><b>{esc(s['palavra'])}</b><small>{esc(s['resumo'].split('.')[0])}.</small></span>
</a>""")
    return "\n".join(out)


def post_blog(slug):
    """Título, resumo e capa de um post do catálogo, lidos do próprio HTML do post."""
    f = ROOT / "blog" / slug / "index.html"
    assert f.exists(), f"post inexistente no blog: {slug}"
    t = f.read_text()
    def meta(attr, nome):
        m = re.search(rf'<meta {attr}="{nome}" content="([^"]*)"', t)
        return html.unescape(m.group(1)) if m else ""
    titulo = re.sub(r"\s*\|\s*(Blog )?LIBRAS\.SE\s*$", "", meta("property", "og:title") or re.search(r"<title>([^<]*)", t).group(1), flags=re.I)
    img = meta("property", "og:image").replace(SITE, "")
    return {"titulo": titulo, "desc": meta("name", "description"), "img": img if (ROOT / img.lstrip("/")).exists() else ""}


def leia_no_blog(slugs):
    """{{LEIA_NO_BLOG:slug1,slug2,slug3}}: cartões de posts que já existem no catálogo do blog."""
    cards = []
    for slug in slugs.split(","):
        p = post_blog(slug)
        img = (f'<span class="lb-img"><img src="{p["img"]}" alt="" loading="lazy" decoding="async"></span>' if p["img"] else "")
        cards.append(f'<a class="lb-card" href="/blog/{slug}/">{img}<span class="lb-txt"><b>{esc(p["titulo"])}</b>'
                     f'<small>{esc(p["desc"][:120].rsplit(" ", 1)[0] + "…" if len(p["desc"]) > 120 else p["desc"])}</small></span></a>')
    return ('<section class="sec lb no-print" aria-labelledby="lb-t"><div class="w"><div class="sec-head"><span class="lbl">No blog</span>'
            '<h2 id="lb-t">Leia também no blog da LIBRAS.SE</h2></div><div class="lb-grid">' + "".join(cards) +
            '</div><p class="lb-more"><a href="/blog/">Ver todos os posts do blog</a></p></div></section>')


def breadcrumb(items):
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i, "name": n, "item": SITE + u} for i, (n, u) in enumerate(items, 1)]}


def breadcrumb_html(items):
    seta = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" aria-hidden="true"><polyline points="9 18 15 12 9 6"/></svg>'
    partes = []
    for i, (n, u) in enumerate(items):
        if i == len(items) - 1:
            partes.append(f'<span aria-current="page">{esc(n)}</span>')
        else:
            partes.append(f'<a href="{u}">{esc(n)}</a>')
    return f'<nav class="bc" aria-label="Você está em">{seta.join(partes)}</nav>'


def build(src):
    text = src.read_text()
    m = re.match(r"\s*<!--META\s*(\{.*?\})\s*META-->\s*", text, re.S)
    assert m, f"{src.name}: bloco META ausente"
    meta = json.loads(m.group(1))
    body = text[m.end():]
    url = SITE + meta["url"]
    graph = [breadcrumb(meta["breadcrumb"])] + meta.get("jsonld", [])
    ld = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, indent=1)
    og_image = SITE + meta.get("og_image", "/assets/img/og/blog.webp")

    body = body.replace("{{BREADCRUMB}}", breadcrumb_html(meta["breadcrumb"]))
    body = re.sub(r"\{\{SINAIS:([a-z0-9,\-]+)\}\}", lambda m: cards_sinais(m.group(1)), body)
    body = re.sub(r"\{\{LEIA_NO_BLOG:([a-z0-9,\-]+)\}\}", lambda m: leia_no_blog(m.group(1)), body)
    if "{{PALAVRAS_JSON}}" in body:
        pal = json.loads((HERE / "palavras.json").read_text())
        pal.pop("_leia", None)
        body = body.replace("{{PALAVRAS_JSON}}", json.dumps(pal, ensure_ascii=False, separators=(",", ":")))
    if "{{SINAIS_JSON}}" in body:
        body = body.replace("{{SINAIS_JSON}}", json.dumps(sinais_jogos(), ensure_ascii=False, separators=(",", ":")))

    style = re.search(r"<style>(.*?)</style>", body, re.S)
    page_css = style.group(1) if style else ""
    body = body[:style.start()] + body[style.end():] if style else body
    scripts = re.findall(r"<script>.*?</script>", body, re.S)
    for s in scripts:
        body = body.replace(s, "")
    main = body.strip()
    if meta.get("areas_nav", True):
        main = main.replace('<main id="main-content">', '<main id="main-content">\n' + areas_nav(meta["url"]), 1)

    header = PARTIALS["header_html"].replace(SKIP, SKIP + "\n\n" + PARTIALS["promo-body_html"], 1)
    out = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
{GTM}

<!-- Página gerada por tools/aprender/build.py a partir de tools/aprender/paginas/{src.name}. Edite a fonte, não este arquivo. -->
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(meta["title"])}</title>
<meta name="description" content="{esc(meta["desc"])}">
<link rel="canonical" href="{url}">
<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1">
<meta property="og:type" content="website">
<meta property="og:url" content="{url}">
<meta property="og:title" content="{esc(meta.get("og_title", meta["title"]))}">
<meta property="og:description" content="{esc(meta.get("og_desc", meta["desc"]))}">
<meta property="og:image" content="{og_image}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:locale" content="pt_BR">
<meta property="og:site_name" content="LIBRAS.SE">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:site" content="@librasse">
<meta name="twitter:image" content="{og_image}">
<link rel="icon" href="/assets/img/favicon/cropped-FAVICONpng-1-32x32.png">
<link rel="manifest" href="/manifest.json">
<meta name="theme-color" content="#4fd1c5">
<link rel="preload" href="/assets/fonts/museo-sans-rounded-300.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/assets/fonts/museo-sans-rounded-900.woff2" as="font" type="font/woff2" crossorigin>
<script type="application/ld+json">
{ld}
</script>
<style>
{PARTIALS["fonts_css"]}
{PARTIALS["vars_css"]}
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
html{{scroll-behavior:smooth}}
body{{font-family:'M',system-ui,sans-serif;background:var(--bg);color:var(--txt);line-height:1.65;-webkit-font-smoothing:antialiased}}
a{{text-decoration:none;color:inherit}}
{PARTIALS["header_css"]}
/* Nav sempre sólida: o hero destas páginas é escuro */
#nav{{background:rgba(240,250,250,.92);backdrop-filter:var(--blur);-webkit-backdrop-filter:var(--blur);box-shadow:0 1px 0 rgba(79,209,197,.12),0 2px 20px rgba(10,34,37,.05);padding:14px 0}}
{PARTIALS["utils_css"]}
{BASE_CSS}
{page_css.strip()}
{PARTIALS["footer_css"]}
</style>
{PARTIALS["promo-css_html"]}</head>
<body>
{GTM_NOSCRIPT}
{header}

{main}

{PARTIALS["footer_html"]}

<script>
{PARTIALS["base_js"]}
</script>
{"".join(scripts)}
{PARTIALS["promo-js_html"]}</body>
</html>
"""
    sobra = re.findall(r"\{\{[A-Z_]+\}\}", out)
    assert not sobra, f"{src.name}: marcadores sem substituição {sobra}"
    dest = ROOT / meta["url"].strip("/") / "index.html"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(out)
    return meta["url"]


def sitemap():
    """Mantém o bloco <!-- APRENDER:SITEMAP --> do sitemap.xml com todas as páginas e PDFs desta área."""
    from datetime import date
    hoje = date.today().isoformat()
    urls = []
    for src in sorted((HERE / "paginas").glob("*.html")):
        meta = json.loads(re.match(r"\s*<!--META\s*(\{.*?\})\s*META-->", src.read_text(), re.S).group(1))
        prio = "0.8" if meta["url"].count("/") == 2 else "0.7"
        urls.append((meta["url"], prio))
    urls += [("/assets/materiais/" + p.name, "0.5") for p in sorted((ROOT / "assets/materiais").glob("*.pdf"))]
    p = ROOT / "sitemap.xml"
    text = p.read_text()
    antigo = re.search(r"  <!-- APRENDER:SITEMAP -->.*?<!-- /APRENDER:SITEMAP -->\n", text, re.S)
    datas = dict(re.findall(r"<loc>(https://libras\.se[^<]+)</loc>\s*<lastmod>([^<]+)</lastmod>", antigo.group(0))) if antigo else {}
    bloco = "  <!-- APRENDER:SITEMAP -->\n" + "".join(
        f"  <url>\n    <loc>{SITE}{u}</loc>\n    <lastmod>{datas.get(SITE + u, hoje)}</lastmod>\n"
        f"    <changefreq>monthly</changefreq>\n    <priority>{pr}</priority>\n  </url>\n" for u, pr in urls) + "  <!-- /APRENDER:SITEMAP -->\n"
    text = text.replace(antigo.group(0), bloco) if antigo else text.replace("</urlset>", bloco + "</urlset>")
    p.write_text(text)
    return len(urls)


if __name__ == "__main__":
    filtro = sys.argv[1] if len(sys.argv) > 1 else ""
    feitas = [build(p) for p in sorted((HERE / "paginas").glob("*.html")) if p.stem.startswith(filtro)]
    print("\n".join(f"ok  {u}" for u in feitas) or "nenhuma página encontrada")
    print(f"ok  sitemap.xml ({sitemap()} URLs no bloco APRENDER:SITEMAP)")
