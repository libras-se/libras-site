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
  gtm-iframe   title no <iframe> do Google Tag Manager dentro do <noscript>
  faq-region   resposta de FAQ com role="region" e sem nome vira div comum (eram dezenas de "regiões" sem nome)
  aria-papel   aria-label em elemento sem papel: contêiner ganha role="group"; vídeo sem controles e
               abreviação ("7d" = 7 dias) ganham role="img"; rótulo igual ao texto sai
  oculto-foco  link ou botão com aria-hidden="true" sai da ordem do Tab (tabindex="-1")
  conteudo     <div> dentro de <button> vira <span>; "&" solto vira &amp;
  contraste    cores de texto abaixo de 4,5:1 nos posts (data, links), em /todos/ e na home do blog
  logo         nome do link do logo inclui o texto visível ("LIBRAS.SE Blog") e a grafia da marca
  jsonld       entidades HTML decodificadas no JSON-LD; Article do glossário com headline, autor e imagem
  titulo-nivel título que pula nível nos posts (ex.: <h4> logo depois de <h2>) ganha aria-level com o
               nível certo, sem mudar tag nem visual
"""
import html
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
    yield from sorted((RAIZ / "tools/aprender/paginas").glob("*.html"))


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


def op_gtm_iframe(t, f):
    novo = re.sub(r'(<noscript><iframe )(src="https://www\.googletagmanager\.com/ns\.html[^"]*")(?![^>]*\btitle=)',
                  r'\1title="Google Tag Manager" \2', t)
    return novo, novo.count('title="Google Tag Manager"') - t.count('title="Google Tag Manager"')


def op_faq_region(t, f):
    novo = re.sub(r'<div (class="faq-a[^"]*"[^>]*?) role="region"((?![^>]*aria-label)[^>]*)>', r'<div \1\2>', t)
    return novo, t.count('role="region"') - novo.count('role="region"')


def op_aria_papel(t, f):
    n = 0

    def troca(m):
        nonlocal n
        tag, attrs, depois = m[1], m[2], t[m.end():m.end() + 400]
        if "role=" in attrs:
            return m[0]
        rotulo = re.search(r'aria-label="([^"]*)"', attrs)[1]
        if tag == "video":
            return m[0]
        folha = re.match(rf"([^<]*)</{tag}>", depois)
        if folha and folha[1].strip():
            n += 1
            if " ".join(folha[1].split()).lower() == rotulo.strip().lower():
                return "<" + tag + re.sub(r' aria-label="[^"]*"', "", attrs) + ">"
            return f"<{tag} role=\"img\"{attrs}>"
        n += 1
        return f"<{tag} role=\"group\"{attrs}>"
    novo = re.sub(r'<(div|span)((?:\s[^>]*)?\saria-label="[^"]*"[^>]*)>', troca, t)
    sem = re.sub(r'(<video\b[^>]*?) role="img"', r"\1", novo)
    return sem, n + (novo != sem)


def op_oculto_foco(t, f):
    novo = re.sub(r'<(a|button)\b((?=[^>]*\baria-hidden="true")(?![^>]*\btabindex=)[^>]*)>', r'<\1\2 tabindex="-1">', t)
    return novo, novo.count('tabindex="-1"') - t.count('tabindex="-1"')


def fora_de_script(t, fn):
    """Aplica fn só ao HTML fora de <script> (JSON-LD e JS não usam entidades HTML)."""
    partes = re.split(r"(<script\b[\s\S]*?</script>)", t)
    return "".join(p if i % 2 else fn(p) for i, p in enumerate(partes))


def op_conteudo(t, f):
    novo = re.sub(r'<div class="faq-arr" aria-hidden="true">([^<]*)</div>', r'<span class="faq-arr" aria-hidden="true">\1</span>', t)
    novo = fora_de_script(novo, lambda s: s.replace("D&I ", "D&amp;I ").replace("D&I.", "D&amp;I.").replace("Q&As", "Q&amp;As"))
    novo = novo.replace('<nav class="alpha-nav" id="alpha-nav">', '<nav class="alpha-nav" id="alpha-nav" aria-label="Termos por letra">')
    return novo, int(novo != t)


CONTRASTE = {
    # template dos posts de baixa complexidade: data (2,37:1) e links do texto (3,11:1)
    ".pa-meta{display:flex;align-items:center;gap:12px;flex-wrap:wrap;font-size:.82rem;color:var(--txm)}":
        ".pa-meta{display:flex;align-items:center;gap:12px;flex-wrap:wrap;font-size:.82rem;color:#487577}",
    ".pa-body a{color:var(--teal-dd);": ".pa-body a{color:#12737a;",
    # /todos/ e /temas/: data dos cards (3,51:1) e contador (2,37:1)
    "color:var(--bk-s);opacity:.65;margin-bottom:10px}": "color:#587373;margin-bottom:10px}",
    'id="bl-post-count" style="text-align:center;color:var(--txm);': 'id="bl-post-count" style="text-align:center;color:var(--txs);',
    ".bl-no-results{text-align:center;padding:48px 24px;color:var(--txm);": ".bl-no-results{text-align:center;padding:48px 24px;color:var(--txs);",
}


def op_contraste(t, f):
    novo = t
    for a, b in CONTRASTE.items():
        novo = novo.replace(a, b)
    if f.relative_to(RAIZ).as_posix() in ("tools/blog/home.html", "blog/index.html"):
        # home do blog: cinza de apoio (4,1:1) e textos em --teal-dd (3,3:1); o token do design system fica
        novo = novo.replace("--muted:#5d8487", "--muted:#4d7477")
        if "--teal-txt" not in novo:
            novo = novo.replace("--muted:#4d7477", "--muted:#4d7477;--teal-txt:#12737a", 1)
        novo = re.sub(r"(?<![-\w])color:var\(--teal-dd\)", "color:var(--teal-txt)", novo)
    return novo, int(novo != t)


def op_logo(t, f):
    novo = re.sub(r'(<a href="/" class="nlogo" aria-label=")[^"]*("[^>]*>\s*<span class="nlogo-txt" aria-hidden="true">LIBRAS\.SE</span>\s*<span class="nsub" aria-hidden="true">([^<]+)</span>)',
                  lambda m: f"{m[1]}LIBRAS.SE {m[3]}, página inicial do site{m[2]}", t)
    novo = novo.replace('aria-label="Libras.se, Página inicial"', 'aria-label="LIBRAS.SE, Página inicial"')
    return novo, int(novo != t)


def op_titulo_nivel(t, f):
    """Nos posts, componentes do template (caixas, passos, cards) usam <h4> logo abaixo de um <h2> (ou do <h1>):
    o nível certo (anterior + 1) vai no aria-level, sem mudar tag nem CSS."""
    if not e_post(f) and f.relative_to(RAIZ).as_posix() != "blog/CLAUDE.md":
        return t, 0
    corpo_ini = t.find("<body")
    if corpo_ini < 0:
        return t, 0
    partes, ult, n, pos = [t[:corpo_ini]], 1, 0, corpo_ini
    for m in re.finditer(r"<h([1-6])\b([^>]*)>", t[corpo_ini:]):
        ini = corpo_ini + m.start()
        nivel = int(m[1])
        attrs = re.sub(r'\s*aria-level="\d"', "", m[2])
        certo = min(nivel, ult + 1)
        tag = f'<h{nivel} aria-level="{certo}"{attrs}>' if certo != nivel else f"<h{nivel}{attrs}>"
        if tag != m[0]:
            partes.append(t[pos:ini] + tag)
            pos, n = ini + len(m[0]), n + 1
        ult = certo
    partes.append(t[pos:])
    return "".join(partes), n


ORG_AUTOR = {"@type": "Organization", "@id": "https://libras.se/#organization", "name": "LIBRAS.SE", "url": "https://libras.se/"}


def op_jsonld(t, f):
    """JSON-LD é lido como JSON puro: entidades HTML (&ccedil;) chegavam literais ao Google. Decodifica os textos.
    No glossário, o Article tinha só name: ganha headline, autor (a organização) e a imagem da OG."""
    n = 0
    og = re.search(r'<meta property="og:image" content="([^"]+)"', t)

    def limpa(x):
        if isinstance(x, str):
            return html.unescape(x) if "&" in x else x
        if isinstance(x, list):
            return [limpa(i) for i in x]
        if isinstance(x, dict):
            return {k: limpa(v) for k, v in x.items()}
        return x

    def nos(o):
        if isinstance(o, list):
            for i in o:
                yield from nos(i)
        elif isinstance(o, dict):
            yield o
            if "@graph" in o:
                yield from nos(o["@graph"])

    def troca(m):
        nonlocal n
        bruto = m[2]
        try:
            o = json.loads(bruto)
        except ValueError:
            return m[0]
        novo = limpa(o)
        for nd in nos(novo):
            if nd.get("@type") == "Article" and nd.get("name") and not nd.get("headline"):
                nd["headline"] = nd["name"]
                nd.setdefault("author", ORG_AUTOR)
                if og:
                    nd.setdefault("image", html.unescape(og[1]))
        if novo == o:
            return m[0]
        n += 1
        multi = "\n" in bruto.strip()
        s = json.dumps(novo, ensure_ascii=False, indent=2 if multi else None, separators=None if multi else (",", ":"))
        return m[1] + ("\n" + s + "\n" if multi else s) + m[3]
    return re.sub(r'(<script type="application/ld\+json"[^>]*>)([\s\S]*?)(</script>)', troca, t), n


OPS = [
    ("favicon", op_favicon), ("touch-icon", op_toque_corrige), ("barra", op_barra), ("rodape-css", op_rodape_css),
    ("rodape-h4", op_rodape_h4), ("aria", op_aria), ("body", op_body), ("emoji-lbl", op_emoji_lbl),
    ("https", op_https), ("publisher", op_publisher), ("youtube", op_youtube), ("speculation", op_speculation),
    ("busca", op_busca), ("feed", op_feed), ("gtm-iframe", op_gtm_iframe), ("faq-region", op_faq_region),
    ("aria-papel", op_aria_papel), ("oculto-foco", op_oculto_foco), ("conteudo", op_conteudo),
    ("contraste", op_contraste), ("logo", op_logo), ("titulo-nivel", op_titulo_nivel), ("jsonld", op_jsonld),
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
