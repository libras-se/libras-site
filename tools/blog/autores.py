#!/usr/bin/env python3
"""Gera as páginas de autor do blog a partir da autoria declarada nos posts.

    python3 tools/blog/autores.py

Lê tools/blog/autores.json (quem são os autores) e o JSON-LD BlogPosting de cada post
(quem escreveu o quê), e escreve /<pasta>/<slug>/index.html a partir de tools/blog/autor.html:
schema ProfilePage + Person, lista de artigos (ItemList), contagem e cards com miniatura.
Também mantém as páginas de autor no sitemap.xml. Idempotente.

Rode depois de publicar um post e antes do tools/seo/links.py (que injeta o bloco
"Aprenda e jogue" nestas páginas, listadas em so_icones do links.json).
"""
import html
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import home  # noqa: E402

ROOT = home.ROOT
SITE = home.SITE
CFG = json.loads((HERE / "autores.json").read_text())
MOLDE = (HERE / "autor.html").read_text()
ORG = {"@id": f"{SITE}/#organization", "@type": "Organization", "name": "LIBRAS.SE", "url": f"{SITE}/"}


def esc(s):
    return html.escape(s, quote=True)


def autores_do_post(a):
    au = a.get("author") or []
    return [x.get("name") for x in (au if isinstance(au, list) else [au]) if isinstance(x, dict)]


def titulo(src):
    m = re.search(r'<meta property="og:title" content="([^"]*)"', src)
    t = html.unescape(m.group(1)) if m else re.search(r"<title>([^<]*)", src).group(1)
    return re.sub(r"\s*\|\s*(Blog )?LIBRAS\.SE\s*$", "", t, flags=re.I)


def capa(src):
    m = re.search(r'<meta property="og:image" content="([^"]*)"', src)
    return m.group(1).replace(SITE, "") if m else "/assets/img/og/blog.webp"


def pagina(autor, posts):
    url = f"{SITE}/{autor['pasta']}/{autor['slug']}/"
    n = len(posts)
    ano = min(p["a"]["datePublished"][:4] for _, p in posts) if posts else ""
    pessoa = {
        "@type": "Person", "@id": url + "#person", "name": autor["nome"], "url": url,
        "description": autor["bio"], "jobTitle": autor["cargo"], "worksFor": ORG,
    }
    if autor.get("sameAs"):
        pessoa["sameAs"] = autor["sameAs"]
    ld = [
        {"@context": "https://schema.org", "@type": "ProfilePage", "url": url, "mainEntity": pessoa},
        {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Início", "item": f"{SITE}/"},
            {"@type": "ListItem", "position": 2, "name": "Blog", "item": f"{SITE}/blog/"},
            {"@type": "ListItem", "position": 3, "name": autor["nome"], "item": url}]},
        {"@context": "https://schema.org", "@type": "ItemList", "name": f"Artigos de {autor['nome']} no Blog LIBRAS.SE",
         "itemListElement": [{"@type": "ListItem", "position": i, "url": f"{SITE}/blog/{s}/"} for i, (s, _) in enumerate(posts, 1)]},
    ]
    ld_html = "\n".join(f'<script type="application/ld+json">\n{json.dumps(x, ensure_ascii=False, indent=1)}\n</script>' for x in ld)
    cards = []
    for i, (s, p) in enumerate(posts):
        t = titulo(p["src"])
        thumb = home.img({"slug": s, "img": capa(p["src"]), "titulo": t}, (480, 960), "(max-width:580px) 92vw, 360px", alt="")
        atraso = f" d{i + 1}" if i < 3 else ""
        cards.append(f'        <a class="au-card rv{atraso}" href="/blog/{s}/">\n'
                     f'          <span class="au-card__thumb">{thumb}</span>\n'
                     f'          <div class="au-card__body"><span class="au-card__title">{esc(t)}</span><span class="au-card__read">Ler artigo →</span></div>\n'
                     f'        </a>')
    stats = (f'<div class="au-stat"><strong>{n}</strong><span>{"artigo" if n == 1 else "artigos"}</span></div>'
             + (f'<div class="au-stat"><strong>{ano}</strong><span>primeiro artigo</span></div>' if ano else ""))
    curta = f"Artigos de {autor['nome']} sobre Libras, acessibilidade audiovisual e cultura surda."
    longa = f"{autor['nome']} ({autor['cargo']}) escreve no Blog LIBRAS.SE. " + curta
    trocas = {
        "{{NOME}}": esc(autor["nome"]), "{{ROTULO}}": esc(autor["rotulo"]), "{{ROTULO_CURTO}}": esc(autor["rotulo_curto"]),
        "{{PERFIL}}": esc(autor["perfil"]), "{{DESCRICAO}}": esc(longa[:300]), "{{DESCRICAO_CURTA}}": esc(curta), "{{URL}}": url,
        "{{LD}}": ld_html, "{{INICIAIS}}": esc(autor["iniciais"]), "{{BIO}}": esc(autor["bio"]), "{{STATS}}": stats,
        "{{CARDS}}": "\n".join(cards),
    }
    t = MOLDE
    for k, v in trocas.items():
        t = t.replace(k, v)
    assert "{{" not in t, re.findall(r"\{\{\w+\}\}", t)
    return t


def sitemap(urls_datas):
    p = ROOT / "sitemap.xml"
    t = original = p.read_text()
    validas = set(urls_datas)

    def poda(m):
        loc = m.group(1)
        if re.match(rf"{re.escape(SITE)}/autora?/[^/]+/$", loc) and loc not in validas:
            print(f"  - sitemap: {loc}")
            return ""
        return m.group(0)
    t = re.sub(r"  <url>\s*<loc>([^<]*)</loc>[\s\S]*?</url>\n", poda, t)
    novos = ""
    for u, d in urls_datas.items():
        if f"<loc>{u}</loc>" in t:
            t = re.sub(rf"(<loc>{re.escape(u)}</loc>\s*<lastmod>)[^<]*(</lastmod>)", lambda m, d=d: m[1] + d + m[2], t)
        else:
            novos += f"  <url>\n    <loc>{u}</loc>\n    <lastmod>{d}</lastmod>\n  </url>\n"
            print(f"  + sitemap: {u}")
    t = t.replace("</urlset>", novos + "</urlset>")
    if t != original:
        p.write_text(t)


def main():
    arts = home.artigos()
    datas = {}
    for autor in CFG["autores"]:
        posts = sorted(((s, a) for s, a in arts.items() if autor["nome"] in autores_do_post(a["a"])),
                       key=lambda x: x[1]["a"]["datePublished"], reverse=True)
        destino = ROOT / autor["pasta"] / autor["slug"] / "index.html"
        destino.parent.mkdir(parents=True, exist_ok=True)
        novo = pagina(autor, posts)
        if not destino.exists() or destino.read_text() != novo:
            # preserva o bloco gerado pelo links.py (LSE:APRENDA), que é reinjetado por ele
            if destino.exists():
                velho = destino.read_text()
                m = re.search(r"\n<!-- LSE:APRENDA [\s\S]*?<!-- /LSE:APRENDA -->\n", velho)
                if m and "<!-- LSE:APRENDA" not in novo:
                    i = novo.find('<footer id="foot"')
                    novo = novo[:i] + m.group(0).lstrip("\n") + novo[i:]
            if not destino.exists() or destino.read_text() != novo:
                destino.write_text(novo)
        mod = max((a["a"].get("dateModified") or a["a"]["datePublished"] for _, a in posts), default=None)
        datas[f"{SITE}/{autor['pasta']}/{autor['slug']}/"] = home.dia(mod).isoformat() if mod else home.dia("2026-10-12T00:00:00Z").isoformat()
        print(f"ok  /{autor['pasta']}/{autor['slug']}/ ({len(posts)} artigos)")
    sitemap(datas)


if __name__ == "__main__":
    main()
