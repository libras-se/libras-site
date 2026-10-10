#!/usr/bin/env python3
"""Gera a home do blog (blog/index.html) como portal de notícias e Libras.

Fonte da verdade dos posts: os cartões <article data-post> da própria home (um por post
publicado), como o audit/sync_blog.py espera. O gerador:
  1. lê os cartões existentes (verbatim) e cria cartões para posts novos que ainda não têm;
  2. monta o portal (manchetes, mais lidas, editorias, Aprender Libras, arquivo filtrável)
     a partir desses cartões e de tools/blog/home.json (editorias, mais lidas, destaques);
  3. regenera /blog/todos/ e /blog/temas/ e acrescenta posts novos ao sitemap, com o mesmo
     algoritmo do sync_blog.py, para que o --check continue limpo;
  4. gera miniaturas leves em assets/img/blog/thumbs/ para as vistas do portal.

Uso:  python3 tools/blog/home.py
"""
import html
import json
import re
import sys
import unicodedata
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
SITE = "https://libras.se"
CFG = json.loads((HERE / "home.json").read_text())
PARTIALS = {p.stem + "_" + p.suffix[1:]: p.read_text() for p in (ROOT / "tools/sinais/partials").iterdir() if p.is_file()}
CARD = re.compile(r'<article\b[^>]*\bdata-post\b[^>]*>[\s\S]*?</article>')
JSONLD = re.compile(r'(<script type="application/ld\+json">)([\s\S]*?)(</script>)')
MESES = "jan fev mar abr mai jun jul ago set out nov dez".split()
TZ = ZoneInfo("America/Sao_Paulo")
THUMBS = ROOT / "assets/img/blog/thumbs"


def esc(s):
    return html.escape(s, quote=True)


def plano(s):
    return " ".join(html.unescape(re.sub(r"<[^>]+>", "", s)).split())


def slug_do(card):
    return re.search(r'href="/blog/([^"/]+)/"', card)[1]


def dia(iso):
    dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
    return dt.astimezone(TZ).date() if dt.tzinfo else dt.date()


def schemas(src):
    out = []
    for m in JSONLD.finditer(src):
        try:
            o = json.loads(m[2])
        except json.JSONDecodeError:
            continue
        for n in (o.get("@graph", [o]) if isinstance(o, dict) else o):
            out.append(n)
    return out


def artigos():
    """Posts publicados, com o mesmo critério do sync_blog.py."""
    out = {}
    for f in sorted((ROOT / "blog").glob("*/index.html")):
        src = f.read_text()
        if 'http-equiv="refresh"' in src or re.search(r'<meta name="robots" content="[^"]*noindex', src):
            continue
        a = next((n for n in schemas(src) if n.get("@type") == "BlogPosting"), None)
        if not a:
            continue
        leitura = re.search(r"(\d+)\s*min de leitura", src)
        out[f.parent.name] = {"a": a, "src": src, "leitura": int(leitura[1]) if leitura else None}
    return out


def busca(texto):
    t = unicodedata.normalize("NFD", texto.lower())
    return " ".join(sorted(set(re.findall(r"[a-z0-9]{3,}", "".join(c for c in t if unicodedata.category(c) != "Mn")))))


def card_novo(slug, art, tema):
    """Cartão no mesmo formato dos existentes, para um post que ainda não está na home."""
    a = art["a"]
    titulo = a["headline"]
    desc = a.get("description", "")
    img = a["image"] if isinstance(a["image"], str) else (a["image"].get("url") or a["image"][0])
    img = img.replace(SITE, "")
    base = Path(img).with_suffix("")
    fontes = "".join(f'\n              <source srcset="{base}.{ext}" type="image/{ext}">'
                     for ext in ("avif", "webp") if (ROOT / f"{str(base).lstrip('/')}.{ext}").exists() and not img.endswith("." + ext))
    rot = CFG["temas"][tema]["curto"]
    leitura = art["leitura"] or 3
    d = dia(a["datePublished"])
    print(f"  + cartão criado para o post novo: {slug} (editoria {tema})")
    return f'''<article class="bl-card"
          data-post
          data-search="{busca(titulo + ' ' + desc)}"
          data-cat="acessibilidade"
          itemscope itemtype="https://schema.org/BlogPosting">
          <a href="/blog/{slug}/" class="bl-card__link-cover" aria-label="Ler artigo: {esc(titulo)}"></a>
          <a href="/blog/{slug}/" class="bl-card__thumb" aria-label="{esc(titulo)}">
            <picture>{fontes}
              <img src="{img}" alt="{esc(titulo)}" loading="lazy" decoding="async" itemprop="image" width="1200" height="675">
            </picture>
            <span class="bl-card__badge">{esc(rot)}</span>
          </a>
          <div class="bl-card__body">
            <div class="bl-card__meta">
              <time datetime="{d.isoformat()}" itemprop="datePublished">{d.day} {MESES[d.month - 1]} {d.year}</time>
              <span class="bl-card__dot" aria-hidden="true"></span>
              <span>{leitura} min de leitura</span>
            </div>
            <h3 class="bl-card__title" itemprop="headline">
              <a href="/blog/{slug}/">{esc(titulo)}</a>
            </h3>
            <p class="bl-card__excerpt" itemprop="description">
              {esc(desc)}
            </p>
            <a href="/blog/{slug}/" class="bl-card__read" aria-label="Ler artigo: {esc(titulo)}">Ler artigo →</a>
          </div>
        </article>'''


def normaliza(card, art, tema):
    """Mesmo cartão, com data normalizada (como o sync_blog.py), atributos de filtro e imagem lazy."""
    d = dia(art["a"]["datePublished"])
    card = re.sub(r'(<time\b[^>]*datetime=")[^"]*("[^>]*>)[^<]*(</time>)',
                  lambda m: m[1] + d.isoformat() + m[2] + f"{d.day} {MESES[d.month - 1]} {d.year}" + m[3], card, count=1)
    abre = re.match(r"<article\b[^>]*>", card)[0]
    attrs = {k: v for k, v in re.findall(r'(data-search|data-cat)="([^"]*)"', abre)}
    nova = (f'<article class="bl-card"\n          data-post\n          data-search="{attrs.get("data-search", "")}"\n'
            f'          data-cat="{attrs.get("data-cat", "")}"\n          data-tema="{tema}" data-ano="{d.year}"\n'
            f'          itemscope itemtype="https://schema.org/BlogPosting">')
    card = nova + card[len(abre):]
    return card.replace('loading="eager"', 'loading="lazy"').replace(' fetchpriority="high"', "")


def dados(slug, card, art, tema):
    titulo = plano(re.search(r'class="bl-card__title"[^>]*>\s*<a[^>]*>([\s\S]*?)</a>', card)[1])
    exc = re.search(r'class="bl-card__excerpt"[^>]*>([\s\S]*?)</p>', card)
    img = re.search(r'<img\b[^>]*\bsrc="([^"]+)"', card)[1]
    leitura = re.search(r"(\d+)\s*min de leitura", card)
    d = dia(art["a"]["datePublished"])
    return {"slug": slug, "titulo": titulo, "resumo": plano(exc[1]) if exc else art["a"].get("description", ""),
            "img": img, "data": d, "dataTxt": f"{d.day} {MESES[d.month - 1]} {d.year}", "tema": tema,
            "leitura": int(leitura[1]) if leitura else None, "iso": art["a"]["datePublished"]}


def miniatura(p, largura):
    """assets/img/blog/thumbs/<slug>-<largura>.webp, gerada uma vez a partir da imagem do cartão.
    Capas próprias do carrossel (capas_destaque) usam o nome do arquivo de origem no lugar do slug."""
    from PIL import Image
    THUMBS.mkdir(parents=True, exist_ok=True)
    dest = THUMBS / f"{p.get('thumb', p['slug'])}-{largura}.webp"
    if not dest.exists():
        src = ROOT / p["img"].lstrip("/")
        if not src.exists():
            for ext in ("webp", "jpg", "png", "avif"):
                alt = src.with_suffix("." + ext)
                if alt.exists():
                    src = alt
                    break
        if not src.exists():
            print(f"  ! imagem não encontrada para {p['slug']} ({p['img']}): usando a imagem padrão do blog")
            src = ROOT / "assets/img/og/blog.webp"
        im = Image.open(src).convert("RGB")
        alvo = (largura, round(largura * 9 / 16))
        r = max(alvo[0] / im.width, alvo[1] / im.height)
        im = im.resize((max(alvo[0], round(im.width * r)), max(alvo[1], round(im.height * r))), Image.LANCZOS)
        fx, fy = p.get("foco", (.5, .5))
        x, y = round((im.width - alvo[0]) * fx), round((im.height - alvo[1]) * fy)
        im.crop((x, y, x + alvo[0], y + alvo[1])).save(dest, "WEBP", quality=78, method=6)
    return f"/assets/img/blog/thumbs/{dest.name}"


def img(p, larguras=(480, 960), sizes="(max-width:700px) 100vw, 600px", eager=False, alt=None, pos=None):
    srcset = ", ".join(f"{miniatura(p, w)} {w}w" for w in larguras)
    return (f'<img src="{miniatura(p, larguras[0])}" srcset="{srcset}" sizes="{sizes}" alt="{esc(alt if alt is not None else p["titulo"])}" '
            f'width="{larguras[0]}" height="{round(larguras[0] * 9 / 16)}" decoding="async"'
            + (f' style="object-position:{pos}"' if pos else "")
            + (' fetchpriority="high"' if eager else ' loading="lazy"') + ">")


def capa_destaque(p):
    """Post do carrossel com a capa própria de capas_destaque (foto sem texto escrito), se houver.
    O ponto de foco (pos) vale para o recorte 16:9 da miniatura e para o object-position do 4:5
    do celular. Larguras limitadas à da imagem de origem, para não ampliar."""
    c = CFG.get("capas_destaque", {}).get(p["slug"])
    if not c:
        return p, (960, 1600), None
    from PIL import Image
    with Image.open(ROOT / c["img"].lstrip("/")) as im:
        w = im.width
    pos = c.get("pos", "50% 50%")
    foco = tuple(float(v.rstrip("%")) / 100 for v in pos.split())
    capa = {**p, "img": c["img"], "thumb": Path(c["img"]).stem, "foco": foco}
    return capa, tuple(sorted({min(960, w), min(1600, w)})), pos


def tema_tag(t, curto=True):
    info = CFG["temas"][t]
    return f'<span class="kick k-{t}">{esc(info["curto"] if curto else info["rotulo"])}</span>'


def sinais_video():
    data = json.loads((ROOT / "sinal/sinais.json").read_text())
    return [{"s": s["slug"], "p": s["palavra"], "c": s["categoria"]} for s in data["sinais"]
            if (ROOT / f"assets/videos/sinais/{s['slug']}.mp4").exists()]


def glossario():
    t = (ROOT / "glossario/index.html").read_text()
    bloco = re.search(r"const gd = \[([\s\S]*?)\n\];", t)[1]
    out = []
    for obj in re.split(r"\n  \},?\s*\n  \{", bloco):
        term, slug, d = (re.search(r'term:"([^"]+)"', obj), re.search(r'slug:"([^"]+)"', obj), re.search(r'def:"([^"]+)"', obj))
        if term and slug and d and (ROOT / "glossario" / slug[1] / "index.html").exists():
            out.append({"t": term[1], "s": slug[1], "d": d[1]})
    return out


def contagens():
    return {
        "sinais": len(sinais_video()),
        "glossario": sum(1 for l in (ROOT / "glossario/termos.csv").read_text().splitlines()[1:] if l.strip()),
        "pdfs": len(list((ROOT / "assets/materiais").glob("*.pdf"))),
    }


# ---------------------------------------------------------------- render

def render(posts, cards_feed, total, jsonld):
    por = {p["slug"]: p for p in posts}
    temas = list(CFG["temas"])
    mais = [por[s] for s in CFG["mais_lidas"] if s in por]
    com_texto = set(CFG.get("capas_com_texto", []))
    destaques = [por[s] for s in CFG["destaques"] if s in por] or [
        p for p in posts if p["slug"] not in CFG["mais_lidas"] and p["slug"] not in com_texto][:5]

    # Carrossel
    slides, thumbs = [], []
    for i, p in enumerate(destaques):
        capa, larguras, pos = capa_destaque(p)
        slides.append(f'''<article class="slide{' on' if i == 0 else ''}" data-i="{i}" aria-roledescription="slide" aria-label="{i + 1} de {len(destaques)}"{'' if i == 0 else ' aria-hidden="true"'}>
          <a href="/blog/{p['slug']}/" class="slide-a" tabindex="{0 if i == 0 else -1}">
            <span class="slide-img">{img(capa, larguras, "(max-width:1100px) 100vw, 860px", eager=i == 0, alt="", pos=pos)}</span>
            <span class="slide-txt">
              {tema_tag(p['tema'])}
              <span class="slide-t">{esc(p['titulo'])}</span>
              <span class="slide-r">{esc(p['resumo'])}</span>
              <span class="slide-m"><time datetime="{p['data'].isoformat()}">{p['dataTxt']}</time>{f" · {p['leitura']} min de leitura" if p['leitura'] else ''}</span>
            </span>
          </a>
        </article>''')
        thumbs.append(f'<button type="button" class="cth{" on" if i == 0 else ""}" data-i="{i}" aria-label="Ir para a notícia {i + 1}: {esc(p["titulo"])}"><span class="cth-bar"><i></i></span>{tema_tag(p["tema"])}<b>{esc(p["titulo"])}</b></button>')

    # Mais lidas
    mais_html = "".join(f'''<li{' class="extra"' if i >= 5 else ''}><a href="/blog/{p['slug']}/"><span class="n">{i + 1}</span><span class="mt">{tema_tag(p['tema'])}<b>{esc(p['titulo'])}</b></span></a></li>'''
                        for i, p in enumerate(mais))

    # Materiais grátis em destaque
    mats = []
    for m in CFG.get("materiais_destaque", []):
        pdf = ROOT / f"assets/materiais/{m['arquivo']}.pdf"
        if not pdf.exists():
            print(f"  ! material não encontrado: {pdf.name}")
            continue
        kb = pdf.stat().st_size // 1024
        tam = f"{kb / 1024:.1f} MB".replace(".", ",") if kb >= 1024 else f"{kb} KB"
        mats.append(f'''<a class="mat" href="/assets/materiais/{m['arquivo']}.pdf" download>
          <span class="mat-c"><img src="/assets/materiais/capas/{m['arquivo']}.webp" alt="" width="240" height="340" loading="lazy" decoding="async"></span>
          <span class="mat-t"><small>{esc(m['tipo'])} · PDF · {tam}</small><b>{esc(m['titulo'])}</b><span class="mat-b">Baixar grátis</span></span>
        </a>''')

    # Editorias
    eds = []
    for t in temas:
        ps = [p for p in posts if p["tema"] == t]
        if not ps:
            continue
        lead, resto = ps[0], ps[1:4]
        eds.append(f'''<section class="ed ed-{t}" aria-labelledby="ed-{t}">
          <header class="ed-h"><h3 id="ed-{t}"><i class="d-{t}"></i>{esc(CFG["temas"][t]["rotulo"])}</h3><span>{len(ps)}</span></header>
          <a class="ed-lead" href="/blog/{lead['slug']}/"><span class="ed-img">{img(lead, (480, 960), "(max-width:700px) 80vw, 380px")}</span><b>{esc(lead['titulo'])}</b><time datetime="{lead['data'].isoformat()}">{lead['dataTxt']}</time></a>
          <ul>{"".join(f'<li><a href="/blog/{p["slug"]}/">{esc(p["titulo"])}</a></li>' for p in resto)}</ul>
          <a class="ed-mais" href="/blog/temas/#{t}" data-tema-link="{t}">Mais de {esc(CFG["temas"][t]["curto"])} <span aria-hidden="true">→</span></a>
        </section>''')

    # Filtros do arquivo
    anos = sorted({p["data"].year for p in posts}, reverse=True)
    chips_tema = '<button type="button" class="chip on" data-f="tema" data-v="" aria-pressed="true">Todas <span>' + str(total) + '</span></button>' + "".join(
        f'<button type="button" class="chip" data-f="tema" data-v="{t}" aria-pressed="false"><i class="d-{t}"></i>{esc(CFG["temas"][t]["curto"])} <span>{sum(1 for p in posts if p["tema"] == t)}</span></button>'
        for t in temas)
    chips_ano = '<button type="button" class="chip on" data-f="ano" data-v="" aria-pressed="true">Todos os anos</button>' + "".join(
        f'<button type="button" class="chip" data-f="ano" data-v="{a}" aria-pressed="false">{a} <span>{sum(1 for p in posts if p["data"].year == a)}</span></button>' for a in anos)

    c = contagens()
    tema_css = "".join(f".k-{k}{{color:{i['cor']}}}.d-{k}{{background:{i['cor']}}}"
                       f".feed .bl-card[data-tema=\"{k}\"] .bl-card__meta::before{{content:\"{i['curto']}\";color:{i['cor']}}}"
                       for k, i in CFG["temas"].items())
    rep = {
        "TEMA_CSS": tema_css,
        "SLIDES": "\n        ".join(slides), "MATERIAIS": "\n        ".join(mats), "CTHUMBS": "".join(thumbs), "NSLIDES": str(len(destaques)),
        "MAIS": mais_html, "EDITORIAS": "\n        ".join(eds),
        "CHIPS_TEMA": chips_tema, "CHIPS_ANO": chips_ano, "TOTAL": str(total),
        "FEED": "\n\n".join(cards_feed),
        "SINAIS_JSON": json.dumps(sinais_video(), ensure_ascii=False, separators=(",", ":")),
        "GLOSSARIO_JSON": json.dumps(glossario(), ensure_ascii=False, separators=(",", ":")),
        "N_SINAIS": str(c["sinais"]), "N_GLOSSARIO": str(c["glossario"]), "N_PDFS": str(c["pdfs"]),
        "VARS_CSS": PARTIALS["vars_css"], "FONTS_CSS": PARTIALS["fonts_css"], "HEADER_CSS": PARTIALS["header_css"],
        "FOOTER_CSS": PARTIALS["footer_css"], "UTILS_CSS": PARTIALS["utils_css"], "BASE_JS": PARTIALS["base_js"],
        "HEADER_HTML": cabecalho(), "FOOTER_HTML": PARTIALS["footer_html"], "JSONLD": jsonld,
    }
    out = (HERE / "home.html").read_text()
    for k, v in rep.items():
        out = out.replace("{{" + k + "}}", v)
    sobra = re.findall(r"\{\{[A-Z_]+\}\}", out)
    assert not sobra, sobra
    return out


def cabecalho():
    h = PARTIALS["header_html"]
    h = h.replace("estava+no+site+do+Libras.se", "estava+no+blog+do+Libras.se")
    h = h.replace('<span class="nlogo-txt" aria-hidden="true">LIBRAS.SE</span>',
                  '<span class="nlogo-txt" aria-hidden="true">LIBRAS.SE</span>\n        <span class="nsub" aria-hidden="true">Blog</span>')
    h = h.replace('<li><a href="https://libras.se/blog">Blog</a></li>', '<li><a href="/blog/" aria-current="page">Blog</a></li>')
    h = h.replace('<a href="https://libras.se/blog" onclick="cm()">Blog</a>', '<a href="/blog/" onclick="cm()" aria-current="page">Blog</a>')
    h = h.replace('<a href="/jogo/" onclick="cm()">Jogo</a>', '<a href="/aprender-libras/" onclick="cm()">Aprender Libras</a>\n  <a href="/jogos/" onclick="cm()">Jogos</a>')
    return h


def itemlist_ld(cards_ordem, arts):
    """JSON-LD da home no formato exato que o sync_blog.py produz."""
    graph = json.loads((HERE / "home-ld.json").read_text())
    for n in graph["@graph"]:
        if n.get("@type") == "ItemList":
            n["numberOfItems"] = len(cards_ordem)
            n["itemListElement"] = [{"@type": "ListItem", "position": i, "item": {
                "@type": "BlogPosting", "headline": arts[s]["a"]["headline"], "description": arts[s]["a"]["description"],
                "url": f"{SITE}/blog/{s}/", "datePublished": arts[s]["a"]["datePublished"], "author": arts[s]["a"]["author"]}}
                for i, s in enumerate(cards_ordem, 1)]
    return '<script type="application/ld+json">\n' + json.dumps(graph, ensure_ascii=False, indent=2) + "\n</script>"


def compacto(card):
    return re.sub(r'class="bl-card[^"]*"', 'class="bl-card bl-card--sm rv"', card, count=1).replace('loading="eager"', 'loading="lazy"').replace(' fetchpriority="high"', "")


def derivadas(cards, ordem, temas_de):
    """/blog/todos/ e /blog/temas/ com o algoritmo do sync_blog.py."""
    comp = {s: compacto(c) for s, c in cards.items()}
    p = ROOT / "blog/todos/index.html"
    t = p.read_text()
    t = re.sub(r'(<div class="bl-grid" id="bl-all-grid">)[\s\S]*?(</div>\s*<p class="bl-no-results")',
               lambda m: m[1] + "\n" + "\n".join(comp[s] for s in ordem) + "\n    " + m[2], t, count=1)
    t = re.sub(r'(<p id="bl-post-count"[^>]*>)[^<]*(</p>)', lambda m: m[1] + f"{len(cards)} publicações" + m[2], t)
    p.write_text(t)

    p = ROOT / "blog/temas/index.html"
    t = p.read_text()
    grupos = []
    for k, info in CFG["temas"].items():
        sel = [s for s in ordem if temas_de[s] == k]
        grupos.append(f'''    <section class="bl-theme-group" id="{k}">
      <h2>{html.escape(info["rotulo"], quote=False)} <span style="color:var(--txm);font-weight:700;font-size:.9rem">· {len(sel)}</span></h2>
      <p style="color:var(--txs);font-size:.92rem;margin:-12px 0 22px">{esc(info["desc"])}</p>
      <div class="bl-grid">
''' + "\n".join(comp[s] for s in sel) + "\n      </div>\n    </section>")
    ini = t.index('    <section class="bl-theme-group"')
    fim = t.rindex("</section>", 0, t.index("</main>")) + len("</section>")
    while t[ini:fim].count('<section class="bl-theme-group"') < t[ini:fim].count("</section>"):
        fim = t.rindex("</section>", 0, fim - 1) + len("</section>")
    t = t[:ini] + "\n\n".join(grupos) + t[fim:]
    barra = "".join(f'<a class="bl-theme-pill" href="#{k}">{html.escape(i["curto"], quote=False)}</a>' for k, i in CFG["temas"].items())
    t = re.sub(r'(<div class="bl-theme-bar rv"[^>]*>)[\s\S]*?(</div>)', lambda m: m[1] + barra + m[2], t, count=1)
    p.write_text(t)


def sitemap(arts):
    p = ROOT / "sitemap.xml"
    t = p.read_text()
    tem = set(re.findall(r"<loc>(.*?)</loc>", t))
    novos = ""
    for s, a in arts.items():
        u = f"{SITE}/blog/{s}/"
        if u in tem:
            continue
        d = dia(a["a"].get("dateModified") or a["a"]["datePublished"]).isoformat()
        novos += f"  <url>\n    <loc>{html.escape(u)}</loc>\n    <lastmod>{d}</lastmod>\n  </url>\n"
        print(f"  + sitemap: {u}")
    if novos:
        p.write_text(t.replace("</urlset>", novos + "</urlset>"))


def main():
    arts = artigos()
    home = (ROOT / "blog/index.html").read_text()
    existentes = {slug_do(c): c for c in CARD.findall(home)}
    temas_de = {}
    for s in arts:
        t = CFG["classificacao"].get(s)
        if t not in CFG["temas"]:
            print(f"  ! {s} sem editoria em tools/blog/home.json: usando 'inclusao'")
            t = "inclusao"
        temas_de[s] = t
    for s in set(existentes) - set(arts):
        print(f"  - cartão removido (post não publicado): {s}")
    ordem = sorted(arts, key=lambda s: (arts[s]["a"]["datePublished"], f"{SITE}/blog/{s}/"), reverse=True)
    cards = {s: normaliza(existentes[s] if s in existentes else card_novo(s, arts[s], temas_de[s]), arts[s], temas_de[s]) for s in ordem}
    posts = [dados(s, cards[s], arts[s], temas_de[s]) for s in ordem]
    out = render(posts, [cards[s] for s in ordem], len(ordem), itemlist_ld(ordem, arts))
    (ROOT / "blog/index.html").write_text(out)
    derivadas(cards, ordem, temas_de)
    sitemap(arts)
    print(f"ok  blog/index.html ({len(ordem)} posts), blog/todos/, blog/temas/")


if __name__ == "__main__":
    sys.exit(main())
