#!/usr/bin/env python3
"""Liga ao glossário a primeira ocorrência de cada termo nos posts do blog que ainda não linkam o termo.

Usa a mesma lista de variações do publicador (APELIDOS e glossario/termos.csv, via tools/blog/novo_post.py),
então "pessoas com deficiência" vira link para /glossario/pcd/, "intérprete de Libras" para /glossario/til-tils/ etc.

Regras (as do §6 do blog/CLAUDE.md):
  - só no corpo do artigo, fora de títulos, links, legendas, botões, blocos gerados e créditos;
  - uma vez por termo em cada post (se o post já linka o termo em qualquer lugar, não mexe);
  - no máximo LIMITE termos distintos linkados por post (contando os que já existiam), na ordem do texto.
Idempotente: rodar de novo não muda nada.

Uso:  python3 tools/seo/glossario_links.py                 (termos de --termos ou, sem ele, todos os publicados)
      python3 tools/seo/glossario_links.py --termos pcd,ouvinte --simular
"""
import argparse
import importlib.util
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
_spec = importlib.util.spec_from_file_location("novo_post", ROOT / "tools/blog/novo_post.py")
np_ = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(np_)

LIMITE = 8  # no máximo 8 termos distintos do glossário linkados por post (contando os que já existiam)
PROIBIDAS = {"a", "h1", "h2", "h3", "h4", "h5", "h6", "figcaption", "script", "style", "button", "summary", "label",
             "code", "pre", "title", "svg", "select", "option", "textarea", "time", "cite"}
CLASSES_FORA = re.compile(r"lse-|pa-refs|pa-tags|pa-cta|post-cta|hero|meta|caption|cap\b|credit|tags|faq-q|btn|stat|label|number|kicker|badge")
# termo com outro sentido no post (ex.: "assistir às aulas como ouvintes" = como ouvinte de curso, não pessoa ouvinte)
EXCECOES = {("tocantins-tem-libras-na-rede-estadual-de-ensino", "ouvinte")}
VOID = {"br", "img", "source", "input", "meta", "link", "hr", "wbr", "path", "circle", "line", "rect", "polyline", "polygon", "ellipse", "use"}
TERMO_RE = re.compile(r'href="(?:https://libras\.se)?/glossario/([a-z0-9-]+)/"')


def regiao(t):
    """(início, fim) do corpo do artigo."""
    m = re.search(r'<div class="pa-body">', t) or re.search(r'<main\b[^>]*class="article-wrapper[^"]*"[^>]*>', t) \
        or re.search(r"<article\b", t)
    if not m:
        return None
    fim = len(t)
    for marca in ('class="pa-refs', "<!-- LSE:MAIS", 'class="pa-tags', '<footer id="foot"'):
        i = t.find(marca, m.end())
        if 0 <= i < fim:
            fim = i
    return m.end(), fim


def processa(t, glossario, alvos, slug_post=""):
    reg = regiao(t)
    if not reg:
        return t, []
    ini, fim = reg
    ja = set(TERMO_RE.findall(t))
    # blocos gerados (banner, Leia também) ficam de fora
    mascaras = [(m.start(), m.end()) for m in re.finditer(r"<!-- LSE:(\w+) [^>]*-->[\s\S]*?<!-- /LSE:\1 -->", t)]
    pilha = []
    trocas, novos = [], []
    for m in re.finditer(r"(<[^>]+>)|([^<]+)", t[ini:fim]):
        pos = ini + m.start()
        if any(a <= pos < b for a, b in mascaras):
            continue
        if m.group(1):
            tag = m.group(1)
            nome = re.match(r"</?\s*([a-zA-Z0-9]+)", tag)
            if not nome or tag.startswith("<!"):
                continue
            nome = nome.group(1).lower()
            if nome in VOID or tag.endswith("/>"):
                continue
            if tag.startswith("</"):
                while pilha:
                    if pilha.pop()[0] == nome:
                        break
            else:
                cls = re.search(r'class="([^"]*)"', tag)
                pilha.append((nome, cls.group(1) if cls else ""))
            continue
        if len(ja) >= LIMITE or any(n in PROIBIDAS or CLASSES_FORA.search(c) for n, c in pilha):
            continue
        texto = m.group(2)
        for achado in glossario.re.finditer(texto):
            slug = glossario.slug(achado.group(0))
            if not slug or slug not in alvos or slug in ja or (slug_post, slug) in EXCECOES:
                continue
            a, b = pos + achado.start(), pos + achado.end()
            trocas.append((a, b, slug))
            ja.add(slug)
            novos.append(slug)
            if len(ja) >= LIMITE:
                break
    for a, b, slug in sorted(trocas, reverse=True):
        t = t[:a] + f'<a href="/glossario/{slug}/">{t[a:b]}</a>' + t[b:]
    return t, novos


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--termos", help="slugs separados por vírgula (padrão: todos os publicados)")
    ap.add_argument("--simular", action="store_true")
    a = ap.parse_args()
    g = np_.Glossario()
    publicados = {s for s, _ in g.termos}
    alvos = set(a.termos.split(",")) & publicados if a.termos else publicados
    total, por_termo = 0, {}
    for f in sorted((ROOT / "blog").glob("*/index.html")):
        t = f.read_text()
        if '"BlogPosting"' not in t:
            continue
        novo, novos = processa(t, g, alvos, f.parent.name)
        if novos:
            total += len(novos)
            for s in novos:
                por_termo[s] = por_termo.get(s, 0) + 1
            print(f"  {f.parent.name}: {', '.join(novos)}")
            if not a.simular:
                f.write_text(novo)
    print(f"{'(simulação) ' if a.simular else ''}ok  {total} links novos para o glossário: {por_termo}")


if __name__ == "__main__":
    main()
