#!/usr/bin/env python3
"""Gera o Glossário de Libras: o índice /glossario/ e cada verbete /glossario/<slug>/.

Fontes em tools/glossario/verbetes/<slug>.html (bloco <!--META {json} META--> + seções do texto).
Header, footer, fontes, variáveis e JS de navegação vêm dos partials canônicos (tools/sinais/partials/).
Cada verbete é assinado por Luis Debiasi, Equipe LIBRAS.SE, com as datas de publicação e de
atualização no bloco de autor, no fim do texto.

Também gera glossario/termos.csv (lista usada pelo blog) e mantém o bloco GLOSSARIO:SITEMAP do sitemap.xml.
Preserva o bloco LSE:DOBLOG ("Este termo no blog"), que o tools/seo/links.py injeta depois.

Uso:  python3 tools/glossario/build.py
"""
import csv
import html
import importlib.util
import io
import json
import re
import sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
SITE = "https://libras.se"
_spec = importlib.util.spec_from_file_location("aprender", ROOT / "tools/aprender/build.py")
ap = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ap)
PARTIALS = ap.PARTIALS
CSS = (HERE / "glossario.css").read_text()
SUGESTAO_JS = (HERE / "sugestao.js").read_text()
OG = "/assets/img/og/glossario.webp"
ORG_ID = f"{SITE}/#organization"
AUTOR = {
    "nome": "Luis Debiasi", "equipe": "Equipe LIBRAS.SE", "url": "/autor/luis-debiasi/", "iniciais": "LD",
    "cargo": "Fundador e CEO da LIBRAS.SE",
    "bio": "Fundador e CEO da LIBRAS.SE, plataforma de tradução de vídeos para Libras com intérpretes humanos. "
           "Escreve e revisa os verbetes do glossário com a equipe de intérpretes.",
}
PESSOA = {"@type": "Person", "@id": f"{SITE}{AUTOR['url']}#person", "name": AUTOR["nome"], "url": SITE + AUTOR["url"],
          "jobTitle": AUTOR["cargo"], "worksFor": {"@id": ORG_ID}}
CATEGORIAS = {  # ordem dos filtros do índice
    "linguística": ("Linguística", "#1a9ca4"),
    "legislação": ("Legislação", "#7c5cd6"),
    "interpretação": ("Interpretação", "#16a34a"),
    "tecnologia": ("Tecnologia", "#2f6fde"),
    "cultura": ("Cultura surda", "#d9468f"),
}
MESES = ["jan.", "fev.", "mar.", "abr.", "maio", "jun.", "jul.", "ago.", "set.", "out.", "nov.", "dez."]
NOVO_DIAS = 45
SKIP = ap.SKIP
ICO = {
    "relogio": '<svg viewBox="0 0 24 24" fill="none" stroke-width="2" aria-hidden="true"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>',
    "livro": '<svg viewBox="0 0 24 24" fill="none" stroke-width="2" aria-hidden="true"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20V3H6.5A2.5 2.5 0 0 0 4 5.5z"/><path d="M4 19.5A2.5 2.5 0 0 0 6.5 22H20v-5"/></svg>',
    "pessoa": '<svg viewBox="0 0 24 24" fill="none" stroke-width="2" aria-hidden="true"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>',
}


def esc(s):
    return html.escape(s, quote=True)


def texto(s):
    return html.unescape(re.sub(r"<[^>]+>", "", s))


def data_pt(iso):
    d = date.fromisoformat(iso)
    return f"{d.day} de {MESES[d.month - 1]} de {d.year}"


def ordem(t):
    import unicodedata
    return "".join(c for c in unicodedata.normalize("NFD", t.lower()) if unicodedata.category(c) != "Mn")


# ------------------------------------------------------------------ fontes

def carregar():
    vs = []
    for f in sorted((HERE / "verbetes").glob("*.html")):
        t = f.read_text()
        m = re.match(r"\s*<!--META\s*(\{.*?\})\s*META-->\s*", t, re.S)
        assert m, f"{f.name}: bloco META ausente"
        v = json.loads(m.group(1))
        v["slug"] = f.stem
        v["corpo"] = t[m.end():].strip()
        v["secoes"] = [(s.group(1), html.unescape(s.group(2)), s.group(3)) for s in
                       re.finditer(r'<section id="(s\d+)" data-toc="([^"]*)">\s*(.*?)\s*</section>', v["corpo"], re.S)]
        problemas = [k for k in ("termo", "categoria", "title", "desc", "sub", "definicao", "resumo", "publicado", "atualizado", "faq", "fontes")
                     if not v.get(k)]
        assert not problemas, f"{f.name}: faltam {problemas}"
        assert v["categoria"] in CATEGORIAS, f"{f.name}: categoria {v['categoria']!r}"
        assert v["secoes"], f"{f.name}: nenhuma <section id=\"sN\" data-toc>"
        traco = re.search(r"[—–]", t)
        if traco:
            print(f"  aviso {f.name}: travessão em '{t[max(0, traco.start() - 30):traco.start() + 30]}'")
        vs.append(v)
    slugs = {v["slug"] for v in vs}
    for v in vs:
        for r in v.get("relacionados", []):
            if r not in slugs:
                print(f"  aviso {v['slug']}: relacionado inexistente {r}")
        for alvo in re.findall(r'href="/(glossario|blog)/([a-z0-9-]+)/"', v["corpo"] + v["definicao"]):
            if not (ROOT / alvo[0] / alvo[1] / "index.html").exists() and not (alvo[0] == "glossario" and alvo[1] in slugs):
                print(f"  aviso {v['slug']}: link para /{alvo[0]}/{alvo[1]}/ que não existe")
    return sorted(vs, key=lambda v: ordem(v["termo"]))


def leitura(v):
    palavras = len(texto(v["definicao"] + " " + v["corpo"] + " ".join(q["q"] + " " + q["a"] for q in v["faq"])).split())
    return max(2, round(palavras / 200))


# ------------------------------------------------------------------ partes comuns

def cabecalho():
    h = PARTIALS["header_html"].replace(SKIP, SKIP + "\n\n" + PARTIALS["promo-body_html"], 1)
    h = h.replace('<span class="nlogo-txt" aria-hidden="true">LIBRAS.SE</span>',
                  '<span class="nlogo-txt" aria-hidden="true">LIBRAS.SE</span>\n        <span class="nsub" aria-hidden="true">Glossário</span>')
    h = h.replace('<a href="/glossario/" onclick="cm()">Glossário</a>', '<a href="/glossario/" onclick="cm()" aria-current="page">Glossário</a>')
    return h


def pagina(url, title, desc, keywords, og_title, og_desc, ld, main, extra_head="", extra_js="", og_type="article"):
    """Monta a página com os partials canônicos e preserva o LSE:DOBLOG que já estiver no arquivo."""
    dest = ROOT / url.strip("/") / "index.html"
    doblog = ""
    if dest.exists():
        m = re.search(r"\n<!-- LSE:DOBLOG [\s\S]*?<!-- /LSE:DOBLOG -->\n", dest.read_text())
        doblog = m.group(0) if m else ""
    lse_css = ""
    if doblog and dest.exists():
        m = re.search(r"\n<!-- LSE:CSS [\s\S]*?<!-- /LSE:CSS -->\n", dest.read_text())
        lse_css = m.group(0) if m else ""
    ld_html = json.dumps({"@context": "https://schema.org", "@graph": ap.com_redes(ld)}, ensure_ascii=False, indent=1)
    out = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
{ap.GTM}

<!-- Página gerada por tools/glossario/build.py a partir de tools/glossario/. Edite a fonte, não este arquivo. -->
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="keywords" content="{esc(keywords)}">
<link rel="canonical" href="{SITE}{url}">
<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1">
<meta name="author" content="{AUTOR['nome']}, {AUTOR['equipe']}">
<meta property="og:type" content="{og_type}">
<meta property="og:url" content="{SITE}{url}">
<meta property="og:title" content="{esc(og_title)}">
<meta property="og:description" content="{esc(og_desc)}">
<meta property="og:image" content="{SITE}{OG}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:locale" content="pt_BR">
<meta property="og:site_name" content="LIBRAS.SE">
{extra_head}<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:site" content="@librasse">
<meta name="twitter:title" content="{esc(og_title)}">
<meta name="twitter:description" content="{esc(og_desc)}">
<meta name="twitter:image" content="{SITE}{OG}">
<link rel="icon" href="/assets/img/favicon/cropped-FAVICONpng-1-32x32.png">
<link rel="apple-touch-icon" href="/assets/img/favicon/cropped-FAVICONpng-1-180x180.png">
<link rel="manifest" href="/manifest.json">
<meta name="theme-color" content="#4fd1c5">
<link rel="preload" href="/assets/fonts/museo-sans-rounded-300.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/assets/fonts/museo-sans-rounded-900.woff2" as="font" type="font/woff2" crossorigin>
<script type="application/ld+json">
{ld_html}
</script>
<style>
{PARTIALS["fonts_css"]}
{PARTIALS["vars_css"]}
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
html{{scroll-behavior:smooth}}
body{{font-family:'M',system-ui,sans-serif;background:var(--bg);color:var(--txt);line-height:1.65;-webkit-font-smoothing:antialiased}}
a{{text-decoration:none;color:inherit}}
{PARTIALS["header_css"]}
{PARTIALS["utils_css"]}
{CSS}
{PARTIALS["footer_css"]}
</style>
{PARTIALS["promo-css_html"]}<script src="/assets/js/libras-lead.js" defer></script>
<script src="/assets/js/grifo.js" defer></script>
{lse_css}</head>
<body>
{ap.GTM_NOSCRIPT}
{cabecalho()}
<div id="g-prog" aria-hidden="true"></div>

{main}

{doblog}{PARTIALS["footer_html"]}

<script>
{PARTIALS["base_js"]}
(function(){{var b=document.getElementById('g-prog');if(!b)return;var r=false;function u(){{var h=document.documentElement,m=h.scrollHeight-h.clientHeight;b.style.width=(m>0?Math.min(100,h.scrollTop/m*100):0)+'%';r=false}}addEventListener('scroll',function(){{if(!r){{r=true;requestAnimationFrame(u)}}}},{{passive:true}});u()}})();
{extra_js}</script>
{PARTIALS["promo-js_html"]}</body>
</html>
"""
    sobra = re.findall(r"\{\{[A-Z_]+\}\}", out)
    assert not sobra, f"{url}: marcadores sem substituição {sobra}"
    dest.parent.mkdir(parents=True, exist_ok=True)
    mudou = not dest.exists() or dest.read_text() != out
    if mudou:
        dest.write_text(out)
    return mudou


def trilha(itens):
    lis = []
    for i, (nome, url) in enumerate(itens):
        if i == len(itens) - 1:
            lis.append(f'<li><span aria-current="page">{esc(nome)}</span></li>')
        else:
            lis.append(f'<li><a href="{url}">{esc(nome)}</a></li>')
    return f'<ol class="g-trail" aria-label="Caminho de navegação">{"".join(lis)}</ol>'


def breadcrumb_ld(itens, url):
    return {"@type": "BreadcrumbList", "@id": f"{SITE}{url}#breadcrumb", "itemListElement": [
        {"@type": "ListItem", "position": i, "name": n, "item": SITE + u} for i, (n, u) in enumerate(itens, 1)]}


def fim():
    return """<section class="g-fim" aria-labelledby="g-fim-t">
  <div class="w">
    <div class="g-fim-in rv">
      <h2 id="g-fim-t">Precisa de Libras no seu conteúdo?</h2>
      <p>Intérpretes humanos, entrega em até 1 hora e a qualidade que a lei exige e o seu público merece.</p>
      <div class="g-fim-acts">
        <a href="https://huet.libras.se/" class="btn bgl">Enviar seu vídeo</a>
        <a href="https://wa.me/5548996367511?text=Ol%C3%A1%2C+estava+no+gloss%C3%A1rio+do+Libras.se+e+quero+saber+mais!" class="btn bo-dark" target="_blank" rel="noopener noreferrer">Falar no WhatsApp</a>
      </div>
    </div>
  </div>
</section>"""


# ------------------------------------------------------------------ verbete

def html_verbete(v, por_slug, anterior, proximo):
    url = f"/glossario/{v['slug']}/"
    nome_cat, cor = CATEGORIAS[v["categoria"]]
    itens = [("Início", "/"), ("Glossário", "/glossario/"), (v["termo"], url)]
    minutos = leitura(v)
    toc = "".join(f'<li><a href="#{sid}">{esc(rot)}</a></li>' for sid, rot, _ in v["secoes"])
    toc += '<li><a href="#g-faq">Perguntas frequentes</a></li>'
    secoes = "\n\n".join(f'<section class="g-sec" id="{sid}">\n  {corpo}\n</section>' for sid, _, corpo in v["secoes"])
    rel = "".join(f'<li><a href="/glossario/{r}/"><b>{esc(por_slug[r]["termo"])}</b><small>{esc(CATEGORIAS[por_slug[r]["categoria"]][0])}</small></a></li>'
                  for r in v.get("relacionados", []) if r in por_slug)
    faq = "\n".join(f'      <details><summary>{esc(q["q"])}</summary><p>{q["a"]}</p></details>' for q in v["faq"])
    fontes = "\n".join(f"        <li>{f}</li>" for f in v["fontes"])
    datas = f'Publicado em <strong><time datetime="{v["publicado"]}">{data_pt(v["publicado"])}</time></strong>'
    if v["atualizado"] != v["publicado"]:
        datas += f'</span><span>Atualizado em <strong><time datetime="{v["atualizado"]}">{data_pt(v["atualizado"])}</time></strong>'
    pn = ""
    if anterior:
        pn += f'<a href="/glossario/{anterior["slug"]}/" rel="prev"><small>← Termo anterior</small><b>{esc(anterior["termo"])}</b></a>'
    if proximo:
        pn += f'<a class="nx" href="/glossario/{proximo["slug"]}/" rel="next"><small>Próximo termo →</small><b>{esc(proximo["termo"])}</b></a>'
    blog = ",".join(v.get("blog", []))
    fonte_def = f'<small>Fonte: {esc(v["fonte_definicao"])}</small>' if v.get("fonte_definicao") else ""

    main = f"""<main id="main-content">
<header class="g-hero">
  <div class="w">
    {trilha(itens)}
    <a class="g-kicker" href="/glossario/?cat={esc(v['categoria'])}" style="--c:{cor}"><i></i>Glossário · {esc(nome_cat)}</a>
    <h1 class="g-h1">{esc(v['termo'])}</h1>
    <p class="g-sub">{v['sub']}</p>
    <div class="g-meta">
      <span>{ICO['livro']}Verbete do Glossário de Libras</span>
      <span>{ICO['relogio']}{minutos} min de leitura</span>
      <span>{ICO['pessoa']}<span>Por <a href="{AUTOR['url']}">{AUTOR['nome']}</a>, {AUTOR['equipe']}</span></span>
    </div>
  </div>
</header>

<div class="g-grid">
  <article class="g-art" data-blog="{esc(blog)}">
    <div class="g-def">
      <p class="g-def-l">Definição</p>
      <p>{v['definicao']}</p>
      {fonte_def}
    </div>

{secoes}

    <section class="g-faq" id="g-faq" aria-labelledby="g-faq-t">
      <h2 id="g-faq-t">Perguntas frequentes sobre {esc(v['termo'])}</h2>
{faq}
    </section>

    <section class="g-refs" aria-labelledby="g-refs-t">
      <h2 id="g-refs-t">Fontes e referências</h2>
      <ol>
{fontes}
      </ol>
    </section>

    <aside class="g-autor" aria-label="Sobre o autor">
      <div class="g-autor-av" aria-hidden="true">{AUTOR['iniciais']}</div>
      <div>
        <p class="g-autor-l">Escrito por</p>
        <p class="g-autor-n"><a href="{AUTOR['url']}">{AUTOR['nome']}</a><span>, {AUTOR['equipe']}</span></p>
        <p class="g-autor-b">{esc(AUTOR['bio'])}</p>
        <p class="g-autor-d"><span>{datas}</span><a href="{AUTOR['url']}">Ver perfil e artigos →</a></p>
      </div>
    </aside>

    <nav class="g-pn" aria-label="Outros termos do glossário">{pn}</nav>
  </article>

  <aside class="g-side" aria-label="Neste verbete">
    <nav class="g-box" aria-labelledby="g-toc-t">
      <h2 id="g-toc-t">Neste verbete</h2>
      <ul class="g-toc">{toc}</ul>
    </nav>
    <div class="g-box">
      <h2>Termos relacionados</h2>
      <ul class="g-rel">{rel}</ul>
    </div>
    <div class="g-cta">
      <h2>Libras no seu vídeo</h2>
      <p>Intérpretes humanos, entrega em até 1 hora e qualidade que a lei exige.</p>
      <a href="https://huet.libras.se/" class="btn bgl">Enviar seu vídeo</a>
    </div>
  </aside>
</div>

{fim()}
</main>"""

    titulo_art = re.sub(r"\s*\|\s*Gloss[aá]rio LIBRAS\.SE\s*$", "", v["title"])
    ld = [
        {"@type": "Article", "@id": f"{SITE}{url}#article", "url": SITE + url, "headline": titulo_art, "name": titulo_art,
         "description": v["desc"], "inLanguage": "pt-BR", "image": SITE + OG,
         "datePublished": v["publicado"], "dateModified": v["atualizado"], "author": PESSOA,
         "publisher": {"@id": ORG_ID}, "mainEntityOfPage": SITE + url, "about": {"@id": f"{SITE}{url}#term"},
         "isPartOf": {"@type": "CollectionPage", "@id": f"{SITE}/glossario/"}, "breadcrumb": {"@id": f"{SITE}{url}#breadcrumb"},
         "timeRequired": f"PT{minutos}M", "articleSection": "Glossário de Libras"},
        {"@type": "DefinedTerm", "@id": f"{SITE}{url}#term", "name": v["termo"], "description": v["resumo"], "url": SITE + url,
         **({"alternateName": v["en"]} if v.get("en") else {}),
         "inDefinedTermSet": {"@type": "DefinedTermSet", "@id": f"{SITE}/glossario/#set", "name": "Glossário de Libras", "url": f"{SITE}/glossario/"}},
        breadcrumb_ld(itens, url),
        {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q["q"], "acceptedAnswer": {"@type": "Answer", "text": texto(q["a"])}}
                                            for q in v["faq"]]},
        {"@type": "Organization", "@id": ORG_ID, "name": "LIBRAS.SE", "url": SITE + "/"},
    ]
    js = """(function(){var ls=[].slice.call(document.querySelectorAll('.g-toc a'));if(!ls.length||!('IntersectionObserver' in window))return;
var m={};ls.forEach(function(a){m[a.getAttribute('href').slice(1)]=a});
var o=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){ls.forEach(function(a){a.classList.remove('on')});var a=m[e.target.id];if(a)a.classList.add('on')}})},{rootMargin:'-20% 0px -70% 0px'});
Object.keys(m).forEach(function(id){var s=document.getElementById(id);if(s)o.observe(s)})})();"""
    extra = (f'<meta property="article:published_time" content="{v["publicado"]}T12:00:00-03:00">\n'
             f'<meta property="article:modified_time" content="{v["atualizado"]}T12:00:00-03:00">\n'
             f'<meta property="article:author" content="{SITE}{AUTOR["url"]}">\n'
             f'<meta property="article:section" content="Glossário de Libras">\n')
    return pagina(url, v["title"], v["desc"], v.get("keywords", ""), v.get("og_title") or v["title"], v.get("og_desc") or v["desc"],
                  ld, main, extra_head=extra, extra_js=js)


# ------------------------------------------------------------------ índice

def html_indice(vs):
    lista = [v for v in vs if v.get("listar", True)]
    hoje = date.today()
    atualizado = max(v["atualizado"] for v in vs)
    letras = {}
    for v in lista:
        letras.setdefault(ordem(v["termo"])[0].upper(), []).append(v)
    alpha = "".join(f'<a href="#letra-{l}">{l}</a>' if l in letras else f'<span aria-hidden="true">{l}</span>'
                    for l in "ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    grupos = []
    for l in sorted(letras):
        cards = []
        for v in letras[l]:
            nome_cat, cor = CATEGORIAS[v["categoria"]]
            novo = (hoje - date.fromisoformat(v["publicado"])).days <= NOVO_DIAS
            busca = ordem(" ".join([v["termo"], v.get("en", ""), v["resumo"], v.get("keywords", ""), nome_cat]))
            en = f'<small>{esc(v["en"])}</small>' if v.get("en") else ""
            ex = f'<p class="ex">{esc(v["exemplo"])}</p>' if v.get("exemplo") else ""
            cards.append(f"""      <a class="gi-card" id="{v['slug']}" href="/glossario/{v['slug']}/" data-cat="{esc(v['categoria'])}" data-busca="{esc(busca)}">
        <span class="gi-card-top"><span class="gi-cat" style="--c:{cor}">{esc(nome_cat)}</span>{'<span class="gi-novo">Novo</span>' if novo else ''}</span>
        <h3>{esc(v['termo'])}{en}</h3>
        <p>{esc(v['resumo'])}</p>
        {ex}
        <span class="go">Ler o verbete →</span>
      </a>""")
        grupos.append(f'  <section class="gi-letra" id="letra-{l}" aria-labelledby="h-letra-{l}">\n    <h2 id="h-letra-{l}">{l}</h2>\n    <div class="gi-grid">\n'
                      + "\n".join(cards) + "\n    </div>\n  </section>")
    pills = '<button type="button" data-f="" aria-pressed="true">Todos</button>' + "".join(
        f'<button type="button" data-f="{esc(k)}" aria-pressed="false">{esc(n)}</button>' for k, (n, _) in CATEGORIAS.items())
    n = len(lista)
    itens = [("Início", "/"), ("Glossário", "/glossario/")]
    main = f"""<main id="main-content">
<header class="g-hero">
  <div class="w">
    {trilha(itens)}
    <span class="g-kicker"><i></i>Referência editorial</span>
    <h1 class="g-h1">Glossário de <span class="gt">Libras</span></h1>
    <p class="g-sub">Os termos da Língua Brasileira de Sinais, da acessibilidade e da interpretação, com definição clara, exemplos e fontes conferidas. Cada verbete leva para os posts do blog que tratam do assunto.</p>
    <div class="gi-stats">
      <div class="gi-stat"><b>{n}</b><span>termos</span></div>
      <div class="gi-stat"><b>{len(CATEGORIAS)}</b><span>categorias</span></div>
      <div class="gi-stat"><b>{sum(len(v['fontes']) for v in lista)}</b><span>fontes citadas</span></div>
    </div>
  </div>
</header>

<div class="gi-bar" role="search" aria-label="Buscar no glossário">
  <div class="w">
    <input type="search" id="gi-q" placeholder="Buscar termo, sigla ou assunto: datilologia, TILS, LBI…" autocomplete="off" aria-label="Buscar termo">
    <div class="gi-pills" role="group" aria-label="Filtrar por categoria">{pills}</div>
    <span class="gi-count" id="gi-count" aria-live="polite">{n} termos</span>
  </div>
</div>

<div class="gi-lay">
  <nav class="gi-alpha" aria-label="Termos por letra">{alpha}</nav>
  <div>
{chr(10).join(grupos)}
    <p class="gi-vazio" id="gi-vazio" hidden>Nenhum termo encontrado. Tente outra palavra ou <a href="#sugira" style="color:var(--teal-dd);font-weight:700">sugira um termo novo</a>.</p>

    <aside class="g-autor" aria-label="Sobre o glossário">
      <div class="g-autor-av" aria-hidden="true">{AUTOR['iniciais']}</div>
      <div>
        <p class="g-autor-l">Escrito e revisado por</p>
        <p class="g-autor-n"><a href="{AUTOR['url']}">{AUTOR['nome']}</a><span>, {AUTOR['equipe']}</span></p>
        <p class="g-autor-b">Os verbetes são escritos pela LIBRAS.SE com a nossa rede de intérpretes e revisados com base em leis, pesquisas e fontes da comunidade surda.</p>
        <p class="g-autor-d"><span>Última atualização em <strong><time datetime="{atualizado}">{data_pt(atualizado)}</time></strong></span><a href="{AUTOR['url']}">Ver perfil e artigos →</a></p>
      </div>
    </aside>
  </div>
</div>

<section class="gi-sug" id="sugira" aria-labelledby="sug-title">
  <div class="w">
    <div class="gi-sug-in rv">
      <span class="lbl">Contribua</span>
      <h2 id="sug-title">Sugira uma correção ou um termo novo</h2>
      <p>Encontrou um erro, quer incluir um termo ou complementar uma definição? A nossa equipe editorial lê todas as sugestões.</p>
      <form class="sform" id="sform" novalidate>
        <div class="sform-row">
          <div class="sform-g">
            <label for="s-name">Seu nome</label>
            <input type="text" id="s-name" name="name" placeholder="Maria Silva" required autocomplete="name">
          </div>
          <div class="sform-g">
            <label for="s-email">E-mail <span style="font-weight:300;color:var(--txm)">(para retorno)</span></label>
            <input type="email" id="s-email" name="email" placeholder="maria@empresa.com.br" required autocomplete="email">
          </div>
        </div>
        <div class="sform-g">
          <label for="s-type">Tipo de sugestão</label>
          <select id="s-type" name="type" required>
            <option value="">Selecione…</option>
            <option value="correcao">Correção de definição existente</option>
            <option value="novo-termo">Adicionar novo termo</option>
            <option value="complemento">Complementar com exemplo ou referência</option>
            <option value="outro">Outro</option>
          </select>
        </div>
        <div class="sform-g">
          <label for="s-sug">Sugestão</label>
          <textarea id="s-sug" name="suggestion" placeholder="Descreva o termo, a correção ou o complemento que você propõe…" required></textarea>
        </div>
        <div aria-hidden="true" style="position:absolute;left:-9999px;top:auto;height:1px;width:1px;overflow:hidden">
          <label for="s-website">Não preencha este campo</label>
          <input type="text" id="s-website" name="website" tabindex="-1" autocomplete="off">
        </div>
        <div class="sform-acts">
          <button type="submit" class="btn bp" id="sbtn">Enviar sugestão →</button>
          <span class="sform-note">Respondemos em até 5 dias úteis. Ao enviar, você concorda com a <a href="/politica/" style="color:inherit;text-decoration:underline">Política de Privacidade</a>.</span>
        </div>
        <div id="sform-status" role="alert"></div>
      </form>
    </div>
  </div>
</section>

{fim()}
</main>"""
    js = """(function(){var q=document.getElementById('gi-q'),cs=[].slice.call(document.querySelectorAll('.gi-card')),gs=[].slice.call(document.querySelectorAll('.gi-letra')),
bs=[].slice.call(document.querySelectorAll('.gi-pills button')),n=document.getElementById('gi-count'),vz=document.getElementById('gi-vazio'),f='';
function norm(s){return s.toLowerCase().normalize('NFD').replace(/[\\u0300-\\u036f]/g,'')}
function aplica(){var t=norm(q.value.trim()),k=0;cs.forEach(function(c){var ok=(!f||c.dataset.cat===f)&&(!t||c.dataset.busca.indexOf(t)>-1);c.hidden=!ok;if(ok)k++});
gs.forEach(function(g){g.hidden=!g.querySelector('.gi-card:not([hidden])')});n.textContent=k+(k===1?' termo':' termos');vz.hidden=k>0}
function filtra(v){f=v;bs.forEach(function(b){b.setAttribute('aria-pressed',String(b.dataset.f===v))});aplica()}
q.addEventListener('input',aplica);bs.forEach(function(b){b.addEventListener('click',function(){filtra(b.dataset.f)})});
var p=new URLSearchParams(location.search),c=p.get('cat'),s=p.get('q');if(s){q.value=s}if(c&&bs.some(function(b){return b.dataset.f===c}))filtra(c);else if(s)aplica();})();
""" + SUGESTAO_JS
    ld = [
        {"@type": "CollectionPage", "@id": f"{SITE}/glossario/", "url": f"{SITE}/glossario/", "name": "Glossário de Libras",
         "description": "Termos da Libras, da acessibilidade e da interpretação, com definição, exemplos e fontes.",
         "inLanguage": "pt-BR", "dateModified": atualizado, "author": PESSOA, "publisher": {"@id": ORG_ID},
         "breadcrumb": {"@id": f"{SITE}/glossario/#breadcrumb"}, "mainEntity": {"@id": f"{SITE}/glossario/#set"}},
        {"@type": "DefinedTermSet", "@id": f"{SITE}/glossario/#set", "name": "Glossário de Libras", "url": f"{SITE}/glossario/",
         "hasDefinedTerm": [{"@type": "DefinedTerm", "@id": f"{SITE}/glossario/{v['slug']}/#term", "name": v["termo"],
                             "description": v["resumo"], "url": f"{SITE}/glossario/{v['slug']}/"} for v in lista]},
        breadcrumb_ld(itens, "/glossario/"),
        {"@type": "Organization", "@id": ORG_ID, "name": "LIBRAS.SE", "url": SITE + "/"},
    ]
    return pagina("/glossario/", "Glossário de Libras: termos e definições | LIBRAS.SE",
                  f"Glossário de Libras com {n} termos de língua de sinais, acessibilidade e interpretação: definições claras, exemplos práticos e fontes verificadas.",
                  "glossário de libras, termos de libras, dicionário de acessibilidade, datilologia, TILS, LBI, janela de libras",
                  "Glossário de Libras | LIBRAS.SE",
                  f"{n} termos de Libras, acessibilidade e interpretação com definição, exemplos e fontes.",
                  ld, main, extra_js=js, og_type="website")


# ------------------------------------------------------------------ csv e sitemap

def termos_csv(vs):
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(["termo", "slug", "categoria", "url", "status", "definicao"])
    for v in vs:
        if v.get("listar", True):
            w.writerow([v["termo"], v["slug"], v["categoria"], f"{SITE}/glossario/{v['slug']}/", "publicado", v["resumo"]])
    (ROOT / "glossario/termos.csv").write_text(buf.getvalue())


def sitemap(vs):
    """Bloco <!-- GLOSSARIO:SITEMAP --> com o índice e os verbetes; lastmod = data de atualização do verbete."""
    p = ROOT / "sitemap.xml"
    t = original = p.read_text()
    t = re.sub(r"  <url>\s*<loc>https://libras\.se/glossario/[^<]*</loc>[\s\S]*?</url>\n", "", t)
    t = re.sub(r"  <!-- GLOSSARIO:SITEMAP -->[\s\S]*?<!-- /GLOSSARIO:SITEMAP -->\n", "", t)
    urls = [("/glossario/", max(v["atualizado"] for v in vs), "weekly", "0.9")]
    urls += [(f"/glossario/{v['slug']}/", v["atualizado"], "monthly", "0.7") for v in vs]
    bloco = "  <!-- GLOSSARIO:SITEMAP -->\n" + "".join(
        f"  <url>\n    <loc>{SITE}{u}</loc>\n    <lastmod>{d}</lastmod>\n    <changefreq>{c}</changefreq>\n    <priority>{pr}</priority>\n  </url>\n"
        for u, d, c, pr in urls) + "  <!-- /GLOSSARIO:SITEMAP -->\n"
    ancora = "  <!-- SINAIS:SITEMAP -->"
    t = t.replace(ancora, bloco + ancora, 1) if ancora in t else t.replace("</urlset>", bloco + "</urlset>")
    if t != original:
        p.write_text(t)
    return len(urls)


def main():
    vs = carregar()
    por_slug = {v["slug"]: v for v in vs}
    listados = [v for v in vs if v.get("listar", True)]
    mudaram = []
    for v in vs:
        i = listados.index(v) if v in listados else None
        ant = listados[i - 1] if i else None
        prox = listados[i + 1] if i is not None and i + 1 < len(listados) else None
        if html_verbete(v, por_slug, ant, prox):
            mudaram.append(v["slug"])
    if html_indice(vs):
        mudaram.append("(índice)")
    termos_csv(vs)
    n = sitemap(vs)
    print(f"ok  {len(vs)} verbetes ({len(listados)} no índice); mudaram: {len(mudaram)}")
    print(f"ok  glossario/termos.csv e sitemap.xml ({n} URLs no bloco GLOSSARIO:SITEMAP)")


if __name__ == "__main__":
    sys.exit(main())
