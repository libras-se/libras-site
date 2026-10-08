#!/usr/bin/env python3
"""Auditoria de SEO e de links internos do libras.se.

Lê todas as páginas index.html publicadas e mede, por página:
título, descrição, canonical, H1, JSON-LD, OG, links internos de saída e de entrada,
links para as áreas de engajamento (Aprender, jogos, sinais, glossário, materiais,
cultura surda), links quebrados, imagens sem alt e tamanho do texto.

Uso:  python3 tools/seo/auditoria.py            (resumo no terminal + tools/seo/auditoria.json)
      python3 tools/seo/auditoria.py --csv      (também grava tools/seo/auditoria.csv)
"""
import csv
import html
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SITE = "https://libras.se"
IGNORAR = ("tools/", "node_modules/", ".git/", "og/", "emails/", "audit/", "scripts/", "crm/", "CLIENTES/", "cogna 2026/")
ENGAJAMENTO = {
    "aprender": ("/aprender-libras/",),
    "jogos": ("/jogos/", "/jogo/"),
    "sinais": ("/sinal/",),
    "glossario": ("/glossario/",),
    "materiais": ("/materiais/", "/assets/materiais/", "/atividades/"),
    "cultura": ("/cultura-surda/",),
}


def tipo(url):
    if url == "/blog/":
        return "blog-home"
    if url.startswith("/blog/"):
        return "blog-hub" if url in ("/blog/todos/", "/blog/temas/") else "post"
    for pre, t in (("/glossario/", "glossario"), ("/sinal/", "sinal"), ("/jogos/", "jogo"), ("/jogo/", "jogo"),
                   ("/aprender-libras/", "aprender"), ("/atividades/", "aprender"), ("/materiais/", "aprender"),
                   ("/cultura-surda/", "aprender"), ("/libras-para-", "comercial"), ("/acessibilidade-para-", "comercial"),
                   ("/solucoes/", "comercial"), ("/produtos/", "comercial"), ("/orcamento/", "comercial"),
                   ("/eventos-ao-vivo/", "comercial"), ("/libras-ao-vivo/", "comercial"), ("/autora/", "autor")):
        if url.startswith(pre):
            return t
    return "institucional" if url != "/" else "home"


def texto(src):
    corpo = re.sub(r"<(script|style|nav|footer|noscript)[^>]*>.*?</\1>", " ", src, flags=re.S | re.I)
    m = re.search(r"<main\b.*?</main>", corpo, re.S | re.I)
    corpo = m.group(0) if m else corpo
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", corpo)).split())


def links_corpo(src):
    """Links internos fora de header, menu mobile e footer canônicos (o que conta para SEO de contexto)."""
    s = re.sub(r'<nav id="nav".*?</nav>', " ", src, flags=re.S)
    s = re.sub(r'<div class="mob".*?</div>', " ", s, flags=re.S)
    s = re.sub(r'<footer id="foot".*?</footer>', " ", s, flags=re.S)
    s = re.sub(r"<script\b.*?</script>", " ", s, flags=re.S)
    out = set()
    for h in re.findall(r'href="([^"]+)"', s):
        h = h.replace(SITE, "")
        if h.startswith("/") and not h.startswith("//"):
            out.add(h.split("#")[0].split("?")[0] or "/")
    return out


def normal(u):
    if u.endswith((".pdf", ".webp", ".png", ".jpg", ".mp4", ".xml", ".txt", ".css", ".js", ".json", ".ico")):
        return u
    return u if u.endswith("/") else u + "/"


def existe(u):
    p = ROOT / u.lstrip("/")
    return p.exists() or (p / "index.html").exists()


def main():
    sitemap = set(re.findall(r"<loc>https://libras\.se([^<]*)</loc>", (ROOT / "sitemap.xml").read_text()))
    paginas = {}
    for f in sorted(ROOT.rglob("index.html")):
        rel = f.relative_to(ROOT).as_posix()
        if rel.startswith(IGNORAR):
            continue
        url = "/" + rel[: -len("index.html")]
        src = f.read_text(errors="ignore")
        refresh = 'http-equiv="refresh"' in src
        robots = re.search(r'<meta name="robots" content="([^"]*)"', src)
        noindex = bool(robots and "noindex" in robots.group(1))
        tit = re.search(r"<title>([^<]*)</title>", src)
        desc = re.search(r'<meta name="description" content="([^"]*)"', src)
        can = re.search(r'<link rel="canonical" href="([^"]*)"', src)
        tipos_ld = []
        for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', src, re.S):
            try:
                o = json.loads(m.group(1))
                for n in (o.get("@graph", [o]) if isinstance(o, dict) else o):
                    t = n.get("@type")
                    tipos_ld += t if isinstance(t, list) else [t]
            except Exception:
                tipos_ld.append("INVALIDO")
        lk = {normal(u) for u in links_corpo(src)}
        imgs = re.findall(r"<img\b[^>]*>", src)
        paginas[url] = {
            "url": url, "tipo": tipo(url), "sitemap": url in sitemap, "redireciona": refresh, "noindex": noindex,
            "titulo": html.unescape(tit.group(1)).strip() if tit else "", "descricao": html.unescape(desc.group(1)) if desc else "",
            "canonical": (can.group(1) if can else ""), "h1": len(re.findall(r"<h1\b", src)),
            "og_image": bool(re.search(r'property="og:image"', src)), "jsonld": sorted({str(t) for t in tipos_ld}),
            "palavras": len(texto(src).split()), "links": sorted(lk),
            "img_sem_alt": sum(1 for i in imgs if not re.search(r"""\balt=(["'])""", i)),
        }

    # páginas com canonical para outra URL (ex.: /produtos/ → /solucoes/) não concorrem na busca
    indexaveis = {u for u, p in paginas.items()
                  if not p["redireciona"] and not p["noindex"] and p["canonical"] in ("", SITE + u)}
    entrada = defaultdict(set)
    for u, p in paginas.items():
        if u not in indexaveis:
            continue
        for l in p["links"]:
            if l != u:
                entrada[l].add(u)
    posts = {u for u in indexaveis if paginas[u]["tipo"] == "post"}

    problemas = []
    for u in sorted(indexaveis):
        p = paginas[u]
        p["entrada"] = len(entrada[u])
        p["entrada_de_posts"] = len(entrada[u] & posts)
        p["engajamento"] = sorted(k for k, pres in ENGAJAMENTO.items() if any(l.startswith(pr) for l in p["links"] for pr in pres))
        p["links_posts"] = len([l for l in p["links"] if l in posts])
        p["quebrados"] = sorted(l for l in p["links"] if not existe(l))
        q = []
        if not p["sitemap"]:
            q.append("fora do sitemap")
        if not p["titulo"]:
            q.append("sem title")
        elif len(p["titulo"]) > 65:
            q.append(f"title longo ({len(p['titulo'])})")
        if not p["descricao"]:
            q.append("sem description")
        elif not 70 <= len(p["descricao"]) <= 165:
            q.append(f"description fora do tamanho ({len(p['descricao'])})")
        if p["canonical"] != SITE + u:
            q.append("canonical diferente da URL")
        if p["h1"] != 1:
            q.append(f"{p['h1']} H1")
        if not p["og_image"]:
            q.append("sem og:image")
        if not p["jsonld"]:
            q.append("sem JSON-LD")
        if p["entrada"] == 0 and u != "/":
            q.append("órfã (nenhum link interno de contexto aponta para ela)")
        if not p["engajamento"]:
            q.append("sem link para Aprender, jogos, sinais, glossário, materiais ou cultura surda")
        if p["tipo"] == "post" and p["links_posts"] < 3:
            q.append(f"só {p['links_posts']} links para outros posts")
        if p["quebrados"]:
            q.append(f"{len(p['quebrados'])} links internos quebrados")
        if p["img_sem_alt"]:
            q.append(f"{p['img_sem_alt']} imagens sem alt")
        p["problemas"] = q
        problemas += [(u, x) for x in q]

    fora_do_site = sorted(u for u in sitemap if u not in paginas and not existe(u))
    resumo = {
        "paginas": len(paginas), "indexaveis": len(indexaveis), "posts": len(posts),
        "por_tipo": dict(Counter(paginas[u]["tipo"] for u in indexaveis)),
        "problemas_por_tipo": dict(Counter(x.split(" (")[0] if "(" in x else re.sub(r"^\d+ ", "N ", x) for _, x in problemas)),
        "sitemap_sem_pagina": fora_do_site,
        "canonical_para_outra_url": sorted(u for u, p in paginas.items() if not p["redireciona"] and p["canonical"] not in ("", SITE + u)),
    }
    (ROOT / "tools/seo/auditoria.json").write_text(json.dumps({"resumo": resumo, "paginas": [paginas[u] for u in sorted(indexaveis)]},
                                                                ensure_ascii=False, indent=1, default=list))
    if "--csv" in sys.argv:
        with open(ROOT / "tools/seo/auditoria.csv", "w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["url", "tipo", "entrada", "entrada_de_posts", "links_posts", "engajamento", "palavras", "problemas"])
            for u in sorted(indexaveis):
                p = paginas[u]
                w.writerow([u, p["tipo"], p["entrada"], p["entrada_de_posts"], p["links_posts"], " ".join(p["engajamento"]), p["palavras"], " | ".join(p["problemas"])])
    print(json.dumps(resumo, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
