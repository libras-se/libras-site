#!/usr/bin/env python3
"""Checagem do blog: dados, SEO, mídia, banners e lint.

Só lê o site. Escreve o relatório em tools/seo/checagem_blog.json.

    python3 tools/seo/checagem_blog.py             # resumo por categoria
    python3 tools/seo/checagem_blog.py --detalhe   # lista cada ocorrência
    python3 tools/seo/checagem_blog.py --base tools/seo/checagem_blog.base.json
        # compara com uma linha de base e falha se alguma categoria piorou

Categorias de erro (devem chegar a zero ao fim das correções da auditoria) e de aviso.
"""
import argparse
import json
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from urllib.parse import unquote, urlparse
from zoneinfo import ZoneInfo

from bs4 import BeautifulSoup
from PIL import Image

RAIZ = Path(__file__).resolve().parents[2]
BASE = "https://libras.se"
SP = ZoneInfo("America/Sao_Paulo")
SAIDA = RAIZ / "tools/seo/checagem_blog.json"
FORA = {"todos", "temas", "feed.xml"}
NAO_PUBLICADO = ("tools/", "scripts/", "og/", "emails/", "audit/", "crm/", "CLIENTES/", "cogna 2026/", "node_modules/", ".")
EMOJI = re.compile(r"[\U0001F300-\U0001FAFF\U0001F000-\U0001F2FF☀-⛿✅✨❌❗❤⭐]")
CREDITOS = re.compile(r"Créditos e referências", re.I)


def dia(iso):
    return datetime.fromisoformat(iso.replace("Z", "+00:00")).astimezone(SP).date().isoformat()


def caminho_local(url, pasta=None):
    """Arquivo local de uma URL do site, ou None se for externa."""
    if not url or url.startswith(("#", "mailto:", "tel:", "javascript:", "data:")):
        return None
    u = urlparse(url)
    if u.scheme in ("http", "https") and u.netloc not in ("libras.se", "www.libras.se"):
        return None
    p = unquote(u.path)
    if not p:
        return None
    if p.startswith("/"):
        alvo = RAIZ / p.lstrip("/")
    elif pasta is not None:
        alvo = (pasta / p).resolve()
    else:
        return None
    if p.endswith("/") or alvo.is_dir():
        alvo = alvo / "index.html"
    return alvo


def existe(url, pasta=None):
    alvo = caminho_local(url, pasta)
    return None if alvo is None else alvo.exists()


_img = {}


def info_img(arq):
    if arq not in _img:
        d = {"bytes": arq.stat().st_size}
        try:
            with Image.open(arq) as im:
                d["w"], d["h"] = im.size
        except Exception:
            pass
        _img[arq] = d
    return _img[arq]


def ld_blocos(soup):
    out = []
    for s in soup.find_all("script", type="application/ld+json"):
        try:
            j = json.loads(s.string or s.get_text())
        except Exception as e:
            out.append({"_erro": str(e)[:80]})
            continue
        for x in j if isinstance(j, list) else (j.get("@graph") or [j]):
            out.append(x)
    return out


def sitemap():
    t = (RAIZ / "sitemap.xml").read_text()
    return dict(re.findall(r"<loc>(.*?)</loc>\s*<lastmod>(.*?)</lastmod>", t))


def posts():
    for d in sorted((RAIZ / "blog").iterdir()):
        f = d / "index.html"
        if d.is_dir() and f.exists() and d.name not in FORA:
            t = f.read_text()
            if 'http-equiv="refresh"' in t:
                continue
            yield d.name, f, t


def checa_post(slug, arq, bruto, sm, achados):
    soup = BeautifulSoup(bruto, "lxml")
    pasta = arq.parent
    ach = lambda cat, msg: achados[cat].append(f"{slug}: {msg}")
    meta = lambda **kw: (soup.find("meta", attrs=kw) or {}).get("content")
    canon = f"{BASE}/blog/{slug}/"

    # --- HTML estrutural
    if bruto.count("<body") != 1:
        ach("erro:body-duplicado", f"{bruto.count('<body')} tags <body>")
    if (soup.find("link", rel="canonical") or {}).get("href") != canon:
        ach("erro:canonical", "canonical diferente da URL")

    # --- JSON-LD
    lds = ld_blocos(soup)
    for x in lds:
        if "_erro" in x:
            ach("erro:jsonld-invalido", x["_erro"])
    bp = next((x for x in lds if x.get("@type") in ("BlogPosting", "NewsArticle", "Article")), None)
    if not bp:
        ach("erro:sem-blogposting", "sem BlogPosting")
        return
    pub, mod = bp.get("datePublished"), bp.get("dateModified") or bp.get("datePublished")

    # --- datas: schema, meta, visível, sitemap
    if mod and pub and mod < pub:
        ach("erro:data-modificada-antes", f"dateModified {mod} < datePublished {pub}")
    if meta(property="article:published_time") not in (None, pub):
        ach("erro:data-meta", "article:published_time ≠ datePublished")
    if meta(property="article:modified_time") not in (None, mod):
        ach("erro:data-meta", "article:modified_time ≠ dateModified")
    vis = re.findall(r'(Publicado|Atualizado)[^<]{0,12}<time datetime="([^"]+)"', bruto)
    for tipo, d in vis:
        ref = pub if tipo == "Publicado" else mod
        if ref and d[:10] != dia(ref):
            ach("erro:data-visivel", f"{tipo} visível {d[:10]} ≠ schema {dia(ref)}")
    if mod and pub and dia(mod) != dia(pub) and not any(t == "Atualizado" for t, _ in vis):
        ach("aviso:atualizado-oculto", f"dateModified {dia(mod)} sem 'Atualizado em' visível")
    if canon not in sm:
        ach("erro:fora-do-sitemap", "fora do sitemap.xml")
    elif mod and sm[canon] != dia(mod):
        ach("erro:sitemap-lastmod", f"lastmod {sm[canon]} ≠ dateModified {dia(mod)}")

    # --- autoria e publisher
    autor = bp.get("author")
    autores = autor if isinstance(autor, list) else [autor]
    for a in autores:
        if isinstance(a, dict) and a.get("@type") == "Person" and ("LIBRAS.SE" in (a.get("name") or "") or " e " in (a.get("name") or "")):
            ach("erro:autor-schema", f"Person com nome '{a.get('name')}'")
        if isinstance(a, dict) and a.get("@type") == "Organization" and a.get("name") not in ("LIBRAS.SE",) and "@id" not in a:
            ach("aviso:autor-organizacao", f"organização '{a.get('name')}'")
    pubr = bp.get("publisher") or {}
    if "@id" not in pubr:
        ach("aviso:publisher-sem-id", "publisher sem @id da organização")

    # --- OG
    og = meta(property="og:image")
    if not og:
        ach("erro:og", "sem og:image")
    else:
        alvo = caminho_local(og)
        if alvo is not None and not alvo.exists():
            ach("erro:og", f"og:image não existe: {og}")
        elif alvo is not None:
            i = info_img(alvo)
            w, h = meta(property="og:image:width"), meta(property="og:image:height")
            if w and i.get("w") and (str(i["w"]), str(i["h"])) != (w, h):
                ach("erro:og-dimensao", f"declarado {w}x{h}, arquivo {i.get('w')}x{i.get('h')}")
            if i["bytes"] > 300_000:
                ach("erro:og-peso", f"{i['bytes'] // 1024} KB")
            if i.get("w", 1200) < 1200:
                ach("aviso:og-pequena", f"{i.get('w')}x{i.get('h')}")
        img = bp.get("image")
        img = img.get("url") if isinstance(img, dict) else img
        if img and img != og:
            ach("aviso:og-jsonld", "imagem do JSON-LD ≠ og:image")

    # --- FAQ visível
    faq = next((x for x in lds if x.get("@type") == "FAQPage"), None)
    if faq:
        texto = soup.get_text(" ")
        for q in faq.get("mainEntity", []):
            if (q.get("name") or "")[:40] not in texto:
                ach("erro:faq-invisivel", q.get("name", "")[:60])

    # --- imagens, vídeos, iframes
    imgs = [i for i in soup.body.find_all("img") if not i.find_parent(class_=re.compile("lse-"))]
    if imgs and imgs[0].get("loading") == "lazy":
        ach("erro:lcp-lazy", "primeira imagem com loading=lazy")
    for i in soup.body.find_all("img"):
        src = i.get("src") or ""
        if existe(src, pasta) is False:
            ach("erro:imagem-quebrada", src)
        if (i.get("alt") or "").startswith("Imagem ilustrativa do post"):
            ach("aviso:alt-generico", src.rsplit("/", 1)[-1])
    for el in soup.body.find_all(["source", "video", "img"]):
        for attr in ("src", "srcset", "poster", "data-src"):
            v = el.get(attr)
            if not v:
                continue
            itens = [v] if attr != "srcset" else [x.strip().rsplit(" ", 1)[0] if re.search(r"\s\d+[wx]$", x.strip()) else x.strip() for x in v.split(",")]
            for it in itens:
                if " " in unquote(it) or "%20" in it:
                    ach("erro:arquivo-com-espaco", it)
                if existe(it, pasta) is False:
                    ach("erro:midia-quebrada", f"{attr}={it}")
    if soup.find("iframe", src=re.compile("youtube")):
        ach("aviso:youtube-iframe", f"{len(soup.find_all('iframe', src=re.compile('youtube')))} iframe(s) sem fachada")

    # --- links
    for a in soup.find_all("a", href=True):
        h = a["href"].strip()
        u = urlparse(h)
        if u.scheme == "http":
            ach("erro:link-http", h)
        if u.netloc in ("", "libras.se", "www.libras.se") and h.startswith(("/", "https://libras.se", "../")):
            e = existe(h, pasta)
            if e is False:
                ach("erro:link-quebrado", h)
            ult = u.path.rsplit("/", 1)[-1]
            if u.path and not u.path.endswith("/") and "." not in ult and e:
                ach("aviso:link-sem-barra", h)

    # --- editorial
    corpo = soup.body.get_text(" ")
    if EMOJI.search(corpo):
        ach("erro:emoji", "".join(sorted(set(EMOJI.findall(corpo)))))
    if "—" in corpo:
        ach("erro:travessao", f"{corpo.count('—')}x")
    if "LIBRAS-SE" in corpo:
        ach("erro:grafia-marca", "LIBRAS-SE")
    if not CREDITOS.search(corpo):
        ach("aviso:sem-creditos", "sem bloco 'Créditos e referências'")
    if re.search(r"<cite>\s*,", bruto):
        ach("erro:virgula-solta", "citação começando com vírgula")
    if "FAVICONpng.png" in bruto:
        ach("erro:favicon-pesado", "FAVICONpng.png")

    # --- banners
    ads = soup.select("aside.lse-ad")
    if not ads:
        ach("erro:sem-banner", "sem LSE:BANNER")
    for ad in ads:
        if re.search(r"R\$\s*\d", ad.get_text()):
            ach("erro:banner-preco", "banner com preço")
        for a in ad.find_all("a", href=True):
            if existe(a["href"], pasta) is False:
                ach("erro:banner-link", a["href"])


def orfaos(achados):
    """Arquivos de mídia do blog que nenhuma página, CSS, JS ou JSON publicado cita."""
    textos = []
    for f in RAIZ.rglob("*"):
        rel = f.relative_to(RAIZ).as_posix()
        if f.is_dir() or rel.startswith(NAO_PUBLICADO) or "/." in "/" + rel:
            continue
        if f.suffix in (".html", ".css", ".js", ".json", ".xml", ".txt", ".webmanifest"):
            try:
                textos.append(unquote(f.read_text(errors="ignore")))
            except Exception:
                pass
    tudo = unicodedata.normalize("NFC", "\n".join(textos))
    for pasta in ("assets/img/blog", "assets/videos/blog"):
        for f in (RAIZ / pasta).rglob("*"):
            if f.is_file() and not f.name.startswith("."):
                rel = unicodedata.normalize("NFC", f.relative_to(RAIZ).as_posix())
                if rel not in tudo and rel.split("assets/", 1)[1] not in tudo:
                    achados["aviso:orfao"].append(f"{rel} ({f.stat().st_size // 1024} KB)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--detalhe", action="store_true")
    ap.add_argument("--base")
    ap.add_argument("--sem-orfaos", action="store_true")
    args = ap.parse_args()
    sm = sitemap()
    achados = defaultdict(list)
    n = 0
    for slug, arq, bruto in posts():
        n += 1
        checa_post(slug, arq, bruto, sm, achados)
    if not args.sem_orfaos:
        orfaos(achados)
    resumo = {k: len(v) for k, v in sorted(achados.items())}
    SAIDA.write_text(json.dumps({"posts": n, "resumo": resumo, "achados": achados}, ensure_ascii=False, indent=1))
    print(f"{n} posts")
    for k, v in resumo.items():
        print(f"  {v:5}  {k}")
        if args.detalhe:
            for x in achados[k]:
                print(f"         {x}")
    if args.base:
        base = json.loads(Path(args.base).read_text())["resumo"]
        piorou = {k: (base.get(k, 0), v) for k, v in resumo.items() if v > base.get(k, 0)}
        if piorou:
            print("\nPIOROU em relação à base:", piorou)
            sys.exit(1)
        print("\nnenhuma categoria piorou em relação à base")


if __name__ == "__main__":
    main()
