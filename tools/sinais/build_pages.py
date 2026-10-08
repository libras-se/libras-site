"""Gera as páginas do Vocabulário (/sinal/) a partir de sinal/sinais.json.

Uso (na raiz do repo): python3 tools/sinais/build_pages.py

- /sinal/<slug>/index.html  (template-sinal.html + header/footer canônicos em partials/)
- /sinal/index.html         (cards, filtros, contagem e ItemList entre marcadores SINAIS:*)
- sitemap.xml               (bloco SINAIS com extensão de vídeo do Google)
O vídeo de cada sinal (assets/videos/sinais/<slug>.mp4/.webp) só existe depois de aprovado e publicado por
publicar.py. Sem vídeo publicado, a página sai em modo "vídeo em preparação" (sem VideoObject e fora do sitemap de vídeo).
"""
import html
import json
import re
import subprocess
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).parent
SITE = "https://libras.se"
VID_DIR = "/assets/videos/sinais"
ILU_DIR = "/assets/img/sinais"

data = json.loads((ROOT / "sinal" / "sinais.json").read_text())
partials = {p.stem + "_" + p.suffix[1:]: p.read_text() for p in (HERE / "partials").iterdir() if p.is_file()}
template = (HERE / "template-sinal.html").read_text()
esc = html.escape


def fold(s):
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()


def duration(slug):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                          str(ROOT / VID_DIR.lstrip("/") / f"{slug}.mp4")], capture_output=True, text=True)
    return float(out.stdout.strip())


def seg_txt(d):
    return f"{d:.1f}".replace(".", ",") + " s" if d else "em preparação"


sinais = []
for s in data["sinais"]:
    s["video"] = (ROOT / VID_DIR.lstrip("/") / f"{s['slug']}.mp4").exists()
    s["dur"] = duration(s["slug"]) if s["video"] else None
    s["ilustracao"] = s["video"] and (ROOT / ILU_DIR.lstrip("/") / f"{s['slug']}.webp").exists()
    if not s["video"]:
        print(f"sem vídeo publicado (página em modo 'em preparação'): {s['slug']}")
    sinais.append(s)
# listagem: primeiro os que têm vídeo publicado, depois em ordem alfabética
sinais.sort(key=lambda s: (not s["video"], fold(s["palavra"])))
OG_PADRAO = f"{SITE}/assets/img/og/sinal.webp"


SKIP = '<a href="#main-content" class="skip-link">Pular para o conteúdo principal</a>'


def com_banner(header):
    """Banner promocional (partials/promo-*.html, copiado da main) logo após o skip-link, como nas demais páginas."""
    assert SKIP in header
    return header.replace(SKIP, SKIP + "\n\n" + partials["promo-body_html"], 1)


def related(s, n=4):
    same = [x for x in sinais if x is not s and x["categoria"] == s["categoria"] and x["video"]]
    rest = [x for x in sinais if x is not s and x not in same and x["video"]]
    rest += [x for x in sinais if x is not s and not x["video"]]
    return (same + rest)[:n]


def page(s):
    url = f"{SITE}/sinal/{s['slug']}/"
    video, poster = f"{VID_DIR}/{s['slug']}.mp4", f"{VID_DIR}/{s['slug']}.webp"
    desc = (f"Veja em vídeo o sinal de {s['palavra']} em Libras, com definição, exemplos de uso e dicas de contexto. {s['resumo']}"
            if s["video"] else f"{s['palavra']} em Libras: definição, exemplos de uso e contexto. {s['resumo']}")
    if len(desc) > 300:
        desc = desc[:297].rsplit(" ", 1)[0] + "…"
    upload = data["publicado_em"] + "T00:00:00-03:00"
    graph = [
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Início", "item": f"{SITE}/"},
            {"@type": "ListItem", "position": 2, "name": "Sinais em Libras", "item": f"{SITE}/sinal/"},
            {"@type": "ListItem", "position": 3, "name": s["palavra"], "item": url}]},
        {"@type": "DefinedTerm", "name": s["palavra"], "description": re.sub("<[^>]+>", "", s["resumo"]),
         "inDefinedTermSet": {"@type": "DefinedTermSet", "name": "Sinais em Libras", "url": f"{SITE}/sinal/"},
         "url": url, **({"image": f"{SITE}{ILU_DIR}/{s['slug']}.webp"} if s["ilustracao"] else {})},
        {"@type": "VideoObject", "name": f"Sinal de {s['palavra']} em Libras",
         "description": f"Vídeo curto com o sinal de {s['palavra']} em Libras (Língua Brasileira de Sinais), "
                        f"interpretado por intérprete profissional da LIBRAS.SE.",
         "thumbnailUrl": SITE + poster, "contentUrl": SITE + video, "uploadDate": upload,
         "duration": f"PT{round(s['dur'] or 0)}S", "inLanguage": "bzs", "isFamilyFriendly": True,
         "width": 1280, "height": 720,
         "publisher": {"@type": "Organization", "name": "LIBRAS.SE", "url": f"{SITE}/",
                       "logo": {"@type": "ImageObject", "url": f"{SITE}/assets/img/logo/LIBRAS-SE_marca-1536x862.png"}}},
    ]
    if not s["video"]:
        graph = graph[:2]
    ld = {"@context": "https://schema.org", "@graph": graph}
    defs = "\n".join(f'        <li><span class="def-num">{i}.</span><p class="def-text">{d}</p></li>'
                     for i, d in enumerate(s["definicoes"], 1))
    dados = {"Categoria": s["categoria"], "Classe gramatical": s["classe"].replace(" · ", ", ").capitalize(),
             **s.get("dados", {}), "Interpretação": data["interprete"].split(",")[0] if s["video"] else "Em preparação",
             "Variação regional": "Pode variar", "Registro": "Vídeo LIBRAS.SE"}
    dados_html = "\n".join(f'      <div class="dado-item"><p class="dado-label">{esc(k)}</p><p class="dado-value">{esc(v)}</p></div>'
                           for k, v in list(dados.items())[:6])
    ex = "\n".join(f'      <div class="exemplo-item"><span class="exemplo-n">{i}.</span><p class="exemplo-text">{esc(e)}</p></div>'
                   for i, e in enumerate(s["exemplos"], 1))
    ctx = "\n".join(f"      <p>{c}</p>" for c in s["contexto"])
    ilu = f"{ILU_DIR}/{s['slug']}.webp"
    figura = (f'''
        <figure class="ilustra">
          <img src="{ilu}" width="960" height="720" alt="Ilustração do sinal de {esc(s['palavra'])} em Libras: a intérprete no meio do sinal, com setas indicando o movimento das mãos" decoding="async">
          <figcaption>Ilustração: as setas mostram o movimento das mãos.</figcaption>
        </figure>''' if s["ilustracao"] else "")
    if s["video"]:
        player = f'''    <div class="player">
      <div class="player-grid{' com-ilustra' if s['ilustracao'] else ''}">
        <div class="player-media">
          <video id="sinalVid" src="{video}" poster="{poster}" width="1280" height="720" muted loop playsinline preload="auto" aria-label="Vídeo do sinal de {esc(s['palavra'])} em Libras"></video>
        </div>{figura}
      </div>
      <div class="player-info">
        <p class="player-kicker">Sinal em vídeo</p>
        <h3 class="player-title">Como é o sinal de {esc(s['palavra'])} em Libras</h3>
        <p class="player-desc">O vídeo repete o sinal em loop. Use a câmera lenta para observar a configuração das mãos, o movimento e a expressão facial, que faz parte do sinal.</p>
        <div class="player-ctrls">
          <button type="button" class="pbtn" id="vPlay"><svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><rect x="6" y="5" width="4" height="14" rx="1"/><rect x="14" y="5" width="4" height="14" rx="1"/></svg><span>Pausar</span></button>
          <button type="button" class="pbtn" id="vSlow" aria-pressed="false"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><polyline points="12 7 12 12 15 14"/></svg><span>Câmera lenta</span></button>
        </div>
        <p class="player-credit">Interpretação: {esc(data['interprete'])}</p>
      </div>
    </div>'''
        og_media = (f'<meta property="og:image" content="{SITE + poster}">\n<meta property="og:image:width" content="1280">\n'
                    f'<meta property="og:image:height" content="720">\n<meta property="og:video" content="{SITE + video}">\n'
                    f'<meta property="og:video:type" content="video/mp4">\n<meta property="og:video:width" content="1280">\n'
                    f'<meta property="og:video:height" content="720">')
        preload = f'<link rel="preload" as="image" href="{poster}">\n'
        og_image = SITE + poster
        if s["ilustracao"]:  # a ilustração é a melhor imagem para compartilhamento e Google Imagens
            og_media = og_media.replace(f'<meta property="og:image" content="{SITE + poster}">\n<meta property="og:image:width" content="1280">\n<meta property="og:image:height" content="720">',
                                        f'<meta property="og:image" content="{SITE + ilu}">\n<meta property="og:image:width" content="960">\n<meta property="og:image:height" content="720">')
            og_image = SITE + ilu
    else:
        player = f'''    <div class="player">
      <div class="player-media"><div class="player-vazio"><strong>Vídeo em preparação</strong>O sinal de {esc(s['palavra'])} está em validação com a nossa intérprete e será publicado em breve.</div></div>
    </div>'''
        og_media = f'<meta property="og:image" content="{OG_PADRAO}">'
        preload = ""
        og_image = OG_PADRAO
    rel = "\n".join(
        f'      <a href="/sinal/{r["slug"]}/" class="rel-card">'
        + (f'<img src="{ILU_DIR}/{r["slug"]}.webp" alt="" width="960" height="720" loading="lazy" decoding="async">'
           if r["ilustracao"] else
           f'<img src="{VID_DIR}/{r["slug"]}.webp" alt="" width="1280" height="720" loading="lazy" decoding="async">'
           if r["video"] else '<span class="rel-vazio" aria-hidden="true"></span>')
        + f'<span>{esc(r["palavra"])}</span></a>'
        for r in related(s))
    rep = {
        "TITLE": f"{s['palavra']} em Libras: veja o sinal em vídeo | LIBRAS.SE",
        "OG_TITLE": f"{s['palavra']} em Libras, sinal em vídeo | LIBRAS.SE",
        "DESC": esc(desc), "URL": url, "OG_MEDIA": og_media, "OG_IMAGE": og_image, "PRELOAD": preload,
        "PLAYER": player,
        "JSONLD": json.dumps(ld, ensure_ascii=False, indent=1),
        "FONTS_CSS": partials["fonts_css"], "VARS_CSS": partials["vars_css"], "HEADER_CSS": partials["header_css"],
        "FOOTER_CSS": partials["footer_css"], "UTILS_CSS": partials["utils_css"],
        "HEADER_HTML": com_banner(partials["header_html"]), "FOOTER_HTML": partials["footer_html"], "BASE_JS": partials["base_js"],
        "PROMO_CSS": partials["promo-css_html"], "PROMO_JS": partials["promo-js_html"],
        "PALAVRA": esc(s["palavra"]), "CATEGORIA": esc(s["categoria"]), "PRON": esc(s["pron"]),
        "CLASSE": esc(s["classe"]), "RESUMO": esc(s["resumo"]), "DEFS": defs, "DADOS": dados_html, "EXEMPLOS": ex,
        "CONTEXTO": ctx, "RELACIONADOS": rel,
    }
    out = template
    for k, v in rep.items():
        out = out.replace("{{" + k + "}}", v)
    assert "{{" not in out, re.findall(r"\{\{\w+\}\}", out)
    dest = ROOT / "sinal" / s["slug"] / "index.html"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(out)


def replace_block(text, name, content):
    pat = re.compile(rf"(<!-- SINAIS:{name} -->)(.*?)(<!-- /SINAIS:{name} -->)", re.S)
    assert pat.search(text), f"marcador SINAIS:{name} não encontrado"
    return pat.sub(lambda m: m.group(1) + content + m.group(3), text)


def index():
    p = ROOT / "sinal" / "index.html"
    text = p.read_text()
    cats = []
    for s in sinais:
        if s["categoria"] not in cats:
            cats.append(s["categoria"])
    chips = '\n      <button type="button" class="chip on" data-cat="" aria-pressed="true">Todos</button>' + "".join(
        f'\n      <button type="button" class="chip" data-cat="{esc(c)}" aria-pressed="false">{esc(c)}</button>' for c in cats) + "\n      "
    cards = ""
    for s in sinais:
        nome = esc(fold(s["palavra"] + " " + s.get("busca", "")))
        v, img = f"{VID_DIR}/{s['slug']}.mp4", f"{VID_DIR}/{s['slug']}.webp"
        if s["video"]:
            visual = f'''<div class="card-visual" data-video="{v}">
          {f'<img src="{ILU_DIR}/{s["slug"]}.webp" alt="Ilustração do sinal de {esc(s["palavra"])} em Libras" width="960" height="720" loading="lazy" decoding="async">' if s["ilustracao"] else f'<img src="{img}" alt="Intérprete fazendo o sinal de {esc(s["palavra"])} em Libras" width="1280" height="720" loading="lazy" decoding="async">'}
          <span class="card-badge"><svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><polygon points="7 4 20 12 7 20 7 4"/></svg>Vídeo</span>
        </div>'''
        else:
            visual = '''<div class="card-visual card-vazio">
          <span class="card-badge">Vídeo em breve</span>
        </div>'''
        cards += f'''
      <article class="sinal-card" data-nome="{nome}" data-cat="{esc(s['categoria'])}">
        {visual}
        <div class="card-body">
          <span class="card-cat">{esc(s['categoria'])}</span>
          <h2 class="card-nome"><a href="/sinal/{s['slug']}/" class="card-a">{esc(s['palavra'])}</a></h2>
          <p class="card-desc">{esc(s['resumo'])}</p>
          <span class="card-link" aria-hidden="true">Ver sinal em Libras <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" aria-hidden="true"><polyline points="9 18 15 12 9 6"/></svg></span>
        </div>
      </article>'''
    cards += "\n      "
    n = len(sinais)
    nv = sum(1 for s in sinais if s["video"])
    count = (f"{nv} {'sinal' if nv == 1 else 'sinais'} em vídeo, com página própria. Mais sinais em breve." if nv
             else f"{n} {'sinal' if n == 1 else 'sinais'} com página própria. Vídeos em breve.")
    itemlist = json.dumps({"@context": "https://schema.org", "@type": "ItemList", "name": "Sinais em Libras",
                           "numberOfItems": n, "itemListElement": [
                               {"@type": "ListItem", "position": i, "name": f"{s['palavra']} em Libras",
                                "url": f"{SITE}/sinal/{s['slug']}/"} for i, s in enumerate(sinais, 1)]},
                          ensure_ascii=False, indent=1)
    text = replace_block(text, "FILTROS", chips)
    text = replace_block(text, "CARDS", cards)
    text = replace_block(text, "CONTAGEM", count)
    text = replace_block(text, "ITEMLIST", f'\n<script type="application/ld+json">\n{itemlist}\n</script>\n')
    p.write_text(text)


def sitemap():
    p = ROOT / "sitemap.xml"
    text = p.read_text()
    if "xmlns:video=" not in text:
        text = text.replace('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
                            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
                            'xmlns:video="http://www.google.com/schemas/sitemap-video/1.1">')
    # remove entradas avulsas antigas das páginas de sinal geradas (ficam só no bloco)
    for s in sinais:
        text = re.sub(rf"\s*<url>\s*<loc>{re.escape(SITE)}/sinal/{s['slug']}/</loc>.*?</url>", "", text, flags=re.S)
    block = ""
    for s in sinais:
        if not s["video"]:
            block += f"""
  <url>
    <loc>{SITE}/sinal/{s['slug']}/</loc>
    <lastmod>{data['publicado_em']}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.6</priority>
  </url>"""
            continue
        title = esc(f"Sinal de {s['palavra']} em Libras")
        d = esc(f"Vídeo curto com o sinal de {s['palavra']} em Libras, interpretado por intérprete profissional da LIBRAS.SE.")
        block += f"""
  <url>
    <loc>{SITE}/sinal/{s['slug']}/</loc>
    <lastmod>{data['publicado_em']}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.6</priority>
    <video:video>
      <video:thumbnail_loc>{SITE}{VID_DIR}/{s['slug']}.webp</video:thumbnail_loc>
      <video:title>{title}</video:title>
      <video:description>{d}</video:description>
      <video:content_loc>{SITE}{VID_DIR}/{s['slug']}.mp4</video:content_loc>
      <video:duration>{max(1, round(s['dur']))}</video:duration>
      <video:publication_date>{data['publicado_em']}T00:00:00-03:00</video:publication_date>
      <video:family_friendly>yes</video:family_friendly>
    </video:video>
  </url>"""
    if "<!-- SINAIS:SITEMAP -->" not in text:
        text = text.replace("</urlset>", "  <!-- SINAIS:SITEMAP --><!-- /SINAIS:SITEMAP -->\n</urlset>")
    text = replace_block(text, "SITEMAP", block + "\n  ")
    p.write_text(text)


for s in sinais:
    page(s)
index()
sitemap()
print(f"{len(sinais)} páginas de sinal geradas; /sinal/ e sitemap.xml atualizados")
