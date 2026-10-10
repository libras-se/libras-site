#!/usr/bin/env python3
"""Estrutura de links internos da LIBRAS.SE (SEO): matérias correlatas, ícones e banners.

Em cada post do blog:
  - um banner interno (house ad) no meio do texto, escolhido pelo assunto do post
    (Aprenda Libras, alfabeto, jogos, materiais, cultura surda, serviço, Seja TILS);
  - no fim, "Continue lendo" com 4 matérias correlatas (mesma editoria, palavras em comum,
    posts pilares e equilíbrio de links para nenhum post ficar sem link de entrada),
    a solução comercial relacionada (quando houver) e os ícones de Aprenda e jogue.
    Substitui os blocos antigos "Leia mais no blog" e os cartões Jogo/Vocabulário/Glossário.
Nas páginas comerciais e institucionais: "Conteúdo relacionado no blog".
Nos verbetes do glossário: "Este termo no blog", com os posts que citam o verbete (link de volta).

Tudo fica entre marcadores <!-- LSE:... --> e é regerado a cada execução (idempotente).
Configuração em tools/seo/links.json; editorias e cards vêm de tools/blog/home.json e da home do blog.

Uso:  python3 tools/seo/links.py
"""
import hashlib
import html
import importlib.util
import json
import re
import unicodedata
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
_spec = importlib.util.spec_from_file_location("home", ROOT / "tools/blog/home.py")
home = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(home)
L = json.loads((HERE / "links.json").read_text())
TEMAS = home.CFG["temas"]
ANTIGOS = ("pa-actions", "pa-related", "pa-acts-alt", "blog-more", "post-actions")
PARADAS = set("para com como sobre entre mais pela pelo pelas pelos uma umas uns que dos das nos nas aos por sua seu suas seus ele ela eles elas isso esta este essa esse libras".split())


def esc(s):
    return html.escape(s, quote=True)


def palavras(txt):
    t = unicodedata.normalize("NFD", txt.lower())
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return {w for w in re.findall(r"[a-z0-9]{4,}", t) if w not in PARADAS}


def h(s):
    return int(hashlib.md5(s.encode()).hexdigest(), 16)


# ------------------------------------------------------------------ dados

def carregar():
    arts = home.artigos()
    src = (ROOT / "blog/index.html").read_text()
    cards = {home.slug_do(c): c for c in home.CARD.findall(src)}
    posts = {}
    for s in arts:
        if s not in cards:
            continue
        p = home.dados(s, cards[s], arts[s], home.CFG["classificacao"].get(s, "inclusao"))
        busca = re.search(r'data-search="([^"]*)"', cards[s])
        p["palavras"] = palavras(p["titulo"] + " " + (busca.group(1) if busca else ""))
        posts[s] = p
    return posts


def pontuar(a, b, posts):
    pa, pb = posts[a], posts[b]
    sc = 3.0 if pa["tema"] == pb["tema"] else 0.0
    inter = len(pa["palavras"] & pb["palavras"])
    sc += 8.0 * inter / max(1, len(pa["palavras"] | pb["palavras"]))
    if b in L["pilares"].get(pa["tema"], []):
        sc += 2.0
    if pb["data"].year >= 2025:
        sc += 0.4
    return sc


def relacionados(posts, n=4):
    """Escolha gulosa com equilíbrio de entrada: cada post recebe ao menos 2 links de outros posts."""
    entrada = defaultdict(int)
    rel = {}
    pilares = {s for v in L["pilares"].values() for s in v}
    for a in sorted(posts, key=h):
        cand = sorted((b for b in posts if b != a), key=lambda b: pontuar(a, b, posts) - 0.7 * entrada[b], reverse=True)
        esc_ = []
        for b in cand:
            if len(esc_) == n:
                break
            mesma = sum(1 for x in esc_ if posts[x]["tema"] == posts[a]["tema"])
            if posts[b]["tema"] == posts[a]["tema"] and mesma >= n - 1:
                continue
            esc_.append(b)
        rel[a] = esc_
        for b in esc_:
            entrada[b] += 1
    for _ in range(3):
        for q in sorted(posts, key=lambda s: entrada[s]):
            while entrada[q] < 2:
                melhor = None
                for a in posts:
                    if a == q or q in rel[a]:
                        continue
                    trocaveis = [r for r in rel[a] if entrada[r] > 2 and r not in pilares]
                    if not trocaveis:
                        continue
                    r = min(trocaveis, key=lambda x: pontuar(a, x, posts))
                    ganho = pontuar(a, q, posts) - pontuar(a, r, posts)
                    if melhor is None or ganho > melhor[0]:
                        melhor = (ganho, a, r)
                if not melhor:
                    break
                _, a, r = melhor
                rel[a][rel[a].index(r)] = q
                entrada[r] -= 1
                entrada[q] += 1
    return rel, entrada


def do_glossario(posts, n=3):
    """Para cada verbete, os posts que o citam no próprio texto (link de volta), com rodízio para não repetir sempre os mesmos."""
    cita = defaultdict(set)
    for s in posts:
        t = (ROOT / "blog" / s / "index.html").read_text()
        for nome in ("MAIS", "BANNER", "CSS"):
            t = tira(t, nome)
        for termo in re.findall(r'href="(?:https://libras\.se)?/glossario/([a-z0-9-]+)/"', t):
            cita[termo].add(s)
    pilares = {s for v in L["pilares"].values() for s in v}
    uso = defaultdict(int)
    out = {}
    termos = sorted(f.parent.name for f in (ROOT / "glossario").glob("*/index.html"))
    for termo in sorted(termos, key=lambda x: (len(cita[x]), x)):
        src = (ROOT / "glossario" / termo / "index.html").read_text()
        tit = re.search(r"<title>([^<]*)</title>", src)
        pal = palavras(html.unescape(tit.group(1)) if tit else termo.replace("-", " "))

        def nota(s):
            return (10.0 * (s in cita[termo]) + 2.0 * len(pal & posts[s]["palavras"]) + 1.5 * (s in pilares)
                    + 0.4 * (posts[s]["data"].year >= 2025) - 1.0 * uso[s])
        esc_ = sorted(posts, key=lambda s: (nota(s), s), reverse=True)[:n]
        for s in esc_:
            uso[s] += 1
        out[f"/glossario/{termo}/"] = (esc_, len(cita[termo]))
    return out


# ------------------------------------------------------------------ html

CSS = """<!-- LSE:CSS (gerado por tools/seo/links.py) -->
<style id="lse-css">
@font-face{font-family:'LseM';src:url('/assets/fonts/museo-sans-rounded-300.woff2') format('woff2');font-weight:300;font-display:swap}
@font-face{font-family:'LseM';src:url('/assets/fonts/museo-sans-rounded-700.woff2') format('woff2');font-weight:700;font-display:swap}
@font-face{font-family:'LseM';src:url('/assets/fonts/museo-sans-rounded-900.woff2') format('woff2');font-weight:900;font-display:swap}
@font-face{font-family:'LseDat';src:url('/assets/fonts/Libras2020-Regular.woff2') format('woff2');font-display:block}
.lse-ad,.lse-mais{font-family:'LseM',system-ui,sans-serif;-webkit-font-smoothing:antialiased}
.lse-ad{position:relative;display:grid;grid-template-columns:118px minmax(0,1fr) auto;gap:18px;align-items:center;margin:34px 0;padding:16px 20px 16px 16px;border-radius:20px;background:#e8f6f5;border:1px solid rgba(46,184,192,.25);color:#0e3538;text-align:left}
.lse-ad--escuro{background:radial-gradient(ellipse 45% 110% at 88% 50%,rgba(79,209,197,.22),transparent 70%),linear-gradient(135deg,#0e3538,#2a6069);border-color:transparent;color:#fff;box-shadow:0 8px 32px rgba(10,34,37,.16)}
.lse-ad-l{display:block;margin-bottom:6px;font-size:9.5px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;line-height:1.2;color:#1a9ca4}
.lse-ad--escuro .lse-ad-l{color:#4fd1c5}
.lse-ad-v{display:flex;align-items:center;justify-content:center;width:118px;aspect-ratio:4/3;border-radius:14px;overflow:hidden;background:#fff;text-decoration:none}
.lse-ad-v video,.lse-ad-v img{width:100%;height:100%;object-fit:cover;object-position:50% 20%;display:block}
.lse-ad-v video{object-position:20% 50%}
.lse-ad--escuro .lse-ad-v{box-shadow:0 0 0 2px rgba(255,255,255,.85)}
.lse-ad-v img.lse-capa{object-fit:contain;padding:6px;background:#f0fafa}
.lse-ad-v .lse-dat{font-family:'LseDat',monospace;font-size:30px;line-height:1;color:#0e3538;letter-spacing:1px}
.lse-ad-t b{display:block;font-size:19px;font-weight:900;letter-spacing:-.02em;line-height:1.15}
.lse-ad-t p{margin:6px 0 0!important;font-size:14px!important;font-weight:300;line-height:1.5!important;opacity:.82;color:inherit!important}
.lse-ad-b{display:flex;flex-direction:column;gap:6px;align-items:stretch}
.lse-btn,.lse-btn2{display:inline-flex;align-items:center;justify-content:center;white-space:nowrap;font-size:13px;font-weight:700;border-radius:999px;padding:10px 18px;text-decoration:none!important;transition:transform .2s}
.lse-btn{background:#0e3538;color:#fff!important}
.lse-ad--escuro .lse-btn{background:#2eb8c0}
.lse-btn2{border:1.5px solid rgba(255,255,255,.35);color:#fff!important}
.lse-btn:hover,.lse-btn2:hover{transform:translateY(-2px)}
.lse-mais{background:#f0fafa;border-top:1px solid rgba(10,34,37,.08);padding:48px 0 54px;color:#12393d}
.lse-w{max-width:1140px;margin:0 auto;padding:0 40px}
.lse-hd{display:flex;align-items:flex-end;justify-content:space-between;gap:14px;flex-wrap:wrap;margin-bottom:18px}
.lse-hd h2{font-family:'LseM',system-ui,sans-serif!important;font-size:24px!important;font-weight:900!important;letter-spacing:-.03em;color:#0e3538!important;margin:0!important;display:flex;align-items:center;gap:10px;line-height:1.1}
.lse-hd h2::before{content:'';width:6px;height:22px;border-radius:3px;background:linear-gradient(130deg,#1aa8b0,#81e6d9)}
.lse-hd a{font-size:13px;font-weight:700;color:#1a9ca4;text-decoration:none}
.lse-hd2{margin-top:34px}
.lse-rel{display:grid;grid-template-columns:repeat(4,1fr);gap:18px}
.lse-rel3{grid-template-columns:repeat(3,1fr)}
.lse-c{display:flex;flex-direction:column;gap:7px;background:#fff;border:1px solid rgba(10,34,37,.08);border-radius:18px;padding:10px 10px 14px;text-decoration:none;color:#0e3538;box-shadow:0 2px 16px rgba(10,34,37,.05);transition:transform .25s,box-shadow .25s}
.lse-c:hover{transform:translateY(-3px);box-shadow:0 8px 30px rgba(10,34,37,.1)}
.lse-ci{display:block;aspect-ratio:16/9;border-radius:12px;overflow:hidden;background:#dff2f0}
.lse-ci img{width:100%;height:100%;object-fit:cover;display:block}
.lse-ck{font-size:10.5px;font-weight:900;letter-spacing:.08em;text-transform:uppercase;padding:0 4px}
.lse-c b{font-size:15px;font-weight:900;line-height:1.28;letter-spacing:-.01em;padding:0 4px}
.lse-sol{margin-top:22px;display:flex;flex-wrap:wrap;align-items:center;gap:8px 14px;background:#fff;border:1px solid rgba(46,184,192,.25);border-left:4px solid #2eb8c0;border-radius:14px;padding:14px 18px;font-size:14px}
.lse-sol strong{color:#0e3538;font-weight:900}
.lse-sol a{color:#1a9ca4;font-weight:700;text-decoration:none}
.lse-sol a:hover{text-decoration:underline}
.lse-ic{display:grid;grid-template-columns:repeat(6,1fr);gap:12px}
.lse-i{display:flex;flex-direction:column;gap:5px;background:#fff;border:1px solid rgba(10,34,37,.08);border-radius:16px;padding:14px 12px;text-decoration:none;color:#0e3538;transition:transform .25s,box-shadow .25s}
.lse-i:hover{transform:translateY(-3px);box-shadow:0 8px 30px rgba(10,34,37,.1)}
.lse-i:first-child{background:linear-gradient(135deg,#0e3538,#2a6069);color:#fff;border-color:transparent}
.lse-ii{width:36px;height:36px;border-radius:11px;background:rgba(79,209,197,.15);color:#1a9ca4;display:flex;align-items:center;justify-content:center}
.lse-i:first-child .lse-ii{color:#4fd1c5}
.lse-ii svg{width:19px;height:19px}
.lse-ii .lse-dat{font-family:'LseDat',monospace;font-size:22px;line-height:1}
.lse-i b{font-size:14px;font-weight:900;line-height:1.2}
.lse-i small{font-size:11.5px;opacity:.65}
.lse-sobre{margin:26px 0 0!important;font-size:13px!important;color:#5d8487!important;text-align:center}
.lse-sobre a{color:#1a9ca4;font-weight:700;text-decoration:none}
.lse-chips{margin-top:18px;display:flex;flex-wrap:wrap;gap:8px;align-items:center;font-size:13px;color:#5d8487}
.lse-chips a{background:#fff;border:1px solid rgba(46,184,192,.3);border-radius:999px;padding:7px 13px;color:#0e3538;font-weight:700;text-decoration:none}
.lse-chips a:hover{border-color:#2eb8c0}
.lse-ad a:focus-visible,.lse-mais a:focus-visible{outline:3px solid #4fd1c5;outline-offset:2px}
@media(max-width:960px){.lse-rel{grid-template-columns:repeat(2,1fr)}.lse-ic{grid-template-columns:repeat(3,1fr)}}
@media(max-width:640px){
  .lse-w{padding:0 18px}
  .lse-ad{grid-template-columns:84px minmax(0,1fr);gap:12px;padding:14px}
  .lse-ad-v{width:84px}
  .lse-ad-v .lse-dat{font-size:21px}
  .lse-ad-b{grid-column:1/-1;flex-direction:row;flex-wrap:wrap}
  .lse-rel,.lse-rel3{grid-template-columns:1fr}
  .lse-c{display:grid;grid-template-columns:minmax(0,1fr) 104px;grid-template-rows:auto 1fr;column-gap:12px;padding:10px}
  .lse-ci{grid-column:2;grid-row:1/3;aspect-ratio:1}
  .lse-ck{grid-column:1;grid-row:1}
  .lse-c b{grid-column:1;grid-row:2}
  .lse-ic{grid-template-columns:repeat(2,1fr)}
}
</style>
<!-- /LSE:CSS -->"""

JS = """<script>(function(){var vs=document.querySelectorAll('.lse-ad video[data-src]');if(!vs.length||!('IntersectionObserver' in window))return;var o=new IntersectionObserver(function(es){es.forEach(function(e){var v=e.target;if(e.isIntersecting){if(!v.src)v.src=v.dataset.src;var p=v.play();if(p&&p.catch)p.catch(function(){})}else v.pause()})},{threshold:.3});vs.forEach(function(v){o.observe(v)})})();</script>"""

ICONES = [
    ("/aprender-libras/", "Aprenda Libras", "Comece por aqui", '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M22 10 12 5 2 10l10 5 10-5z"/><path d="M6 12v5c3 3 9 3 12 0v-5"/></svg>'),
    ("/sinal/", "Sinais em vídeo", "Vocabulário", '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><rect x="2" y="5" width="15" height="14" rx="2"/><path d="m17 10 5-3v10l-5-3"/></svg>'),
    ("/aprender-libras/alfabeto-em-libras/", "Alfabeto", "Seu nome em Libras", '<span class="lse-dat" aria-hidden="true">A</span>'),
    ("/jogos/", "Jogos", "Sinal do dia e quiz", '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><rect x="2" y="6" width="20" height="12" rx="4"/><path d="M6 12h4M8 10v4M15 11h.01M18 13h.01"/></svg>'),
    ("/materiais/", "Materiais", "PDFs grátis", '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6M12 18v-6M9 15l3 3 3-3"/></svg>'),
    ("/glossario/", "Glossário", "Termos da área", '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20V3H6.5A2.5 2.5 0 0 0 4 5.5z"/><path d="M4 19.5A2.5 2.5 0 0 0 6.5 22H20v-5"/></svg>'),
]


def visual(v):
    tipo, val = v.split(":", 1)
    if tipo == "video":
        return (f'<video muted loop playsinline preload="none" aria-hidden="true" poster="/assets/videos/sinais/{val}.webp" '
                f'data-src="/assets/videos/sinais/{val}.mp4"></video>')
    if tipo == "capa":
        return f'<img class="lse-capa" src="/assets/materiais/capas/{val}.webp" alt="" loading="lazy" decoding="async">'
    return f'<span class="lse-dat" aria-hidden="true">{esc(val)}</span>'


def banner(bid):
    b = L["banners"][bid]
    extra = (f'<a class="lse-btn2" href="{b["href2"]}">{esc(b["cta2"])}</a>' if b.get("cta2") else "")
    return (f'<!-- LSE:BANNER (gerado por tools/seo/links.py) -->\n<aside class="lse-ad{" lse-ad--escuro" if b.get("escuro") else ""}" '
            f'aria-label="{esc(b["rotulo"])}">'
            f'<a class="lse-ad-v" href="{b["href"]}" tabindex="-1" aria-hidden="true">{visual(b["visual"])}</a>'
            f'<div class="lse-ad-t"><span class="lse-ad-l">{esc(b["rotulo"])}</span><b>{esc(b["titulo"])}</b><p>{esc(b["texto"])}</p></div>'
            f'<div class="lse-ad-b"><a class="lse-btn" href="{b["href"]}">{esc(b["cta"])}</a>{extra}</div></aside>\n<!-- /LSE:BANNER -->')


def card(p):
    t = TEMAS[p["tema"]]
    return (f'<a class="lse-c" href="/blog/{p["slug"]}/"><span class="lse-ci">{home.img(p, (480,), "(max-width:640px) 104px, 260px", alt="")}</span>'
            f'<span class="lse-ck" style="color:{t["cor"]}">{esc(t["curto"])}</span><b>{esc(p["titulo"])}</b></a>')


def icones():
    return "".join(f'<a class="lse-i" href="{u}"><span class="lse-ii">{svg}</span><b>{esc(n)}</b><small>{esc(s)}</small></a>' for u, n, s, svg in ICONES)


def solucao(slug):
    for g in L["solucoes"].values():
        if slug in g["posts"]:
            links = " · ".join(f'<a href="{u}">{esc(n)}</a>' for n, u in g["links"])
            return f'<div class="lse-sol"><strong>{esc(g["titulo"])}:</strong> {links}</div>'
    return ""


def modulo_post(slug, rel, posts):
    return f"""<!-- LSE:MAIS (gerado por tools/seo/links.py) -->
<section class="lse-mais" aria-labelledby="lse-mais-t">
  <div class="lse-w">
    <div class="lse-hd"><h2 id="lse-mais-t">Continue lendo</h2><a href="/blog/">Mais notícias no blog →</a></div>
    <div class="lse-rel">{"".join(card(posts[s]) for s in rel)}</div>
    {solucao(slug)}
    <div class="lse-hd lse-hd2"><h2 id="lse-ap-t">Aprenda e jogue com a LIBRAS.SE</h2><a href="/aprender-libras/">Aprenda Libras →</a></div>
    <nav class="lse-ic" aria-labelledby="lse-ap-t">{icones()}</nav>
    <p class="lse-sobre">A LIBRAS.SE traduz vídeos para Libras com intérpretes de verdade. <a href="/proposito/">Conheça o nosso propósito</a></p>
  </div>
</section>
{JS}
<!-- /LSE:MAIS -->"""


CHIPS_COMERCIAL = (("/assets/materiais/checklist-video-acessivel-em-libras.pdf", "Checklist de vídeo acessível (PDF)"),
                   ("/assets/materiais/guia-como-se-comunicar-com-pessoas-surdas.pdf", "Guia de comunicação com surdos (PDF)"),
                   ("/aprender-libras/", "Aprenda Libras"), ("/cultura-surda/", "Cultura surda"))
CHIPS_GLOSSARIO = (("/aprender-libras/", "Aprenda Libras"), ("/sinal/", "Sinais em vídeo"),
                   ("/aprender-libras/alfabeto-em-libras/", "Alfabeto em Libras"), ("/jogos/", "Jogos"),
                   ("/materiais/", "Materiais grátis"))


def modulo_pagina(slugs, posts, titulo="Conteúdo relacionado no blog", chips=CHIPS_COMERCIAL, rotulo="Grátis da LIBRAS.SE:"):
    links = "\n      ".join(f'<a href="{u}">{esc(n)}</a>' for u, n in chips)
    return f"""<!-- LSE:DOBLOG (gerado por tools/seo/links.py) -->
<section class="lse-mais" aria-labelledby="lse-db-t">
  <div class="lse-w">
    <div class="lse-hd"><h2 id="lse-db-t">{esc(titulo)}</h2><a href="/blog/">Ver o blog →</a></div>
    <div class="lse-rel lse-rel3">{"".join(card(posts[s]) for s in slugs if s in posts)}</div>
    <div class="lse-chips">{esc(rotulo)}
      {links}
    </div>
  </div>
</section>
<!-- /LSE:DOBLOG -->"""


def modulo_icones():
    return f"""<!-- LSE:APRENDA (gerado por tools/seo/links.py) -->
<section class="lse-mais" aria-labelledby="lse-ap-t">
  <div class="lse-w">
    <div class="lse-hd"><h2 id="lse-ap-t">Aprenda e jogue com a LIBRAS.SE</h2><a href="/aprender-libras/">Aprenda Libras →</a></div>
    <nav class="lse-ic" aria-labelledby="lse-ap-t">{icones()}</nav>
    <p class="lse-sobre">A LIBRAS.SE traduz vídeos para Libras com intérpretes de verdade. <a href="/proposito/">Conheça o nosso propósito</a></p>
  </div>
</section>
<!-- /LSE:APRENDA -->"""


# ------------------------------------------------------------------ edição dos arquivos

def tira(t, nome):
    """Remove o bloco gerado junto com as quebras de linha que a inserção acrescentou."""
    t = re.sub(rf"\n<!-- LSE:{nome} [^>]*-->[\s\S]*?<!-- /LSE:{nome} -->\n", "", t)
    return re.sub(rf"<!-- LSE:{nome} [^>]*-->[\s\S]*?<!-- /LSE:{nome} -->\n?", "", t)


def remove_por_classe(t, classe):
    """Remove o elemento (com filhos) cuja classe contém o token dado, contando a profundidade da tag."""
    while True:
        m = re.search(rf'<([a-z]+)\b[^>]*\bclass="(?:[^"]*\s)?{re.escape(classe)}(?:\s[^"]*)?"[^>]*>', t)
        if not m:
            return t
        tag, pos, prof = m.group(1), m.end(), 1
        for mm in re.finditer(rf"<(/?){tag}\b[^>]*>", t[pos:]):
            prof += -1 if mm.group(1) else 1
            if prof == 0:
                fim = pos + mm.end()
                ini = t.rfind("\n", 0, m.start()) + 1
                t = t[:ini] + t[fim:].lstrip(" ")
                break
        else:
            return t


def filhos(t, ini):
    """Posições (início, fim, tag, classe) dos filhos diretos do elemento que abre em t[ini]."""
    abre = re.match(r"<([a-z]+)\b[^>]*>", t[ini:])
    pos, prof, atual, out = ini + abre.end(), 0, None, []
    VOID = {"br", "img", "source", "input", "meta", "link", "hr", "path", "circle", "line", "rect", "polyline", "polygon", "ellipse", "use"}
    for mm in re.finditer(r"<(/?)([a-z0-9]+)\b[^>]*?(/?)>", t[pos:]):
        nome, fecha = mm.group(2), mm.group(1) == "/"
        if nome in VOID or mm.group(3) == "/":
            continue
        a = pos + mm.start()
        if not fecha:
            if prof == 0:
                cls = re.search(r'class="([^"]*)"', mm.group(0))
                atual = [a, None, nome, cls.group(1) if cls else ""]
            prof += 1
        else:
            if prof == 0:
                return out
            prof -= 1
            if prof == 0 and atual:
                atual[1] = pos + mm.end()
                out.append(tuple(atual))
                atual = None
    return out


def ponto_banner(t):
    """Fronteira entre blocos do corpo do artigo, por volta de 40% do texto."""
    m = re.search(r'<div class="pa-body">', t) or re.search(r'<main\b[^>]*class="article-wrapper[^"]*"[^>]*>', t)
    if not m:
        return None
    ks = [k for k in filhos(t, m.start()) if not re.search(r"tags|cta|acts|actions|faq|references|post-", k[3])]
    cand = []
    for i in range(1, len(ks)):
        ant, prox = ks[i - 1], ks[i]
        if ant[2] in ("p", "div", "figure", "ul", "blockquote") and (prox[2] in ("h2", "p") or prox[3].strip() == "reveal"):
            if prox[2] == "p" and ant[2] != "p":
                continue
            cand.append((i, ant[1]))
    if not cand:
        return None
    alvo = max(2, round(len(ks) * 0.4))
    return min(cand, key=lambda c: abs(c[0] - alvo))[1]


def injeta_css(t):
    t = tira(t, "CSS")
    return t.replace("</head>", "\n" + CSS + "\n</head>", 1)


def processa_post(slug, rel, posts):
    f = ROOT / "blog" / slug / "index.html"
    t = f.read_text()
    original = t
    t = tira(tira(t, "BANNER"), "MAIS")
    for c in ANTIGOS:
        t = remove_por_classe(t, c)
    bid = L["banner_por_post"].get(slug) or (lambda op: op[h(slug) % len(op)])(L["banner_por_editoria"][posts[slug]["tema"]])
    pos = ponto_banner(t)
    if pos:
        t = t[:pos] + "\n" + banner(bid) + "\n" + t[pos:]
    alvo = t.find('<footer id="foot"')
    t = t[:alvo] + "\n" + modulo_post(slug, rel, posts) + "\n" + t[alvo:]
    t = injeta_css(t)
    if t != original:
        f.write_text(t)
    return bid if pos else None


def processa_pagina(url, slugs, posts, **kw):
    f = ROOT / url.strip("/") / "index.html"
    t = f.read_text()
    original = t
    t = tira(t, "DOBLOG")
    alvo = t.find('<footer id="foot"')
    t = t[:alvo] + "\n" + modulo_pagina(slugs, posts, **kw) + "\n" + t[alvo:]
    t = injeta_css(t)
    if t != original:
        f.write_text(t)


def processa_icones(url):
    f = ROOT / url.strip("/") / "index.html"
    t = f.read_text()
    original = t
    t = tira(t, "APRENDA")
    alvo = t.find('<footer id="foot"')
    t = t[:alvo] + "\n" + modulo_icones() + "\n" + t[alvo:]
    t = injeta_css(t)
    if t != original:
        f.write_text(t)


def main():
    posts = carregar()
    rel, entrada = relacionados(posts)
    banners = defaultdict(int)
    sem_banner = []
    for s in sorted(posts):
        b = processa_post(s, rel[s], posts)
        if b:
            banners[b] += 1
        else:
            sem_banner.append(s)
    for url, slugs in L["do_blog"].items():
        processa_pagina(url, slugs, posts)
    for url in L.get("so_icones", []):
        processa_icones(url)
    glos = do_glossario(posts)
    for url, (slugs, _) in glos.items():
        processa_pagina(url, slugs, posts, titulo="Este termo no blog", chips=CHIPS_GLOSSARIO, rotulo="Aprenda mais:")
    print(f"ok  {len(posts)} posts com 'Continue lendo' e ícones; {len(L['do_blog'])} páginas com 'Conteúdo relacionado no blog'")
    sem_cit = sorted(u for u, (_, c) in glos.items() if c == 0)
    print(f"    {len(glos)} verbetes do glossário com 'Este termo no blog'; sem post que cite o termo: {sem_cit}")
    print(f"    banners no texto: {dict(banners)}; sem lugar para banner: {sem_banner}")
    print(f"    links de entrada por post (só 'Continue lendo'): mínimo {min(entrada.values())}, máximo {max(entrada.values())}")


if __name__ == "__main__":
    main()
