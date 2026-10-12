#!/usr/bin/env python3
"""Gera as páginas de redirecionamento do site e o mapa 301 do old.libras.se.

Fonte única: tools/seo/redirects.json ({"origem": "destino"}).

    python3 tools/seo/redirects.py          # escreve/atualiza os stubs e o mapa do nginx
    python3 tools/seo/redirects.py --check  # só confere; sai com erro se algo estiver desatualizado

Para cada origem, escreve <origem>/index.html (ou o próprio arquivo, se a origem terminar
em .html) com meta refresh 0, canonical e link visível. O GitHub Pages não faz 301, e o
Google trata o refresh imediato como redirecionamento permanente.

Regras:
- cadeias são resolvidas: se o destino também é origem, o stub aponta direto para o fim;
- o destino precisa existir e ser uma página de verdade (não um stub);
- nunca sobrescreve uma página de verdade;
- stubs gerados antes e que saíram do JSON são apagados;
- nomes com acento ficam em NFC, como o Wix publicava (o GitHub Pages só acha a forma NFC).
"""
import json
import sys
import unicodedata
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
FONTE = RAIZ / "tools/seo/redirects.json"
MAPA_NGINX = RAIZ / "tools/redirects/old-libras-se/redirects.map"
BASE = "https://libras.se"
MARCA = "<!-- gerado por tools/seo/redirects.py"
NAO_PUBLICADO = ("tools/", "scripts/", "og/", "emails/", "node_modules/")

STUB = """<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
{marca}: não edite, mude tools/seo/redirects.json -->
<title>Página movida | LIBRAS.SE</title>
<link rel="canonical" href="{url}">
<meta name="robots" content="noindex, follow">
<meta http-equiv="refresh" content="0; url={url}">
</head>
<body>
<p>Esta página mudou de endereço: <a href="{url}">{url}</a>.</p>
<script>location.replace("{url}")</script>
</body>
</html>
"""


def nfc(s):
    return unicodedata.normalize("NFC", s)


def arquivo(origem):
    rel = origem.lstrip("/")
    return RAIZ / (rel if rel.endswith(".html") else rel + "index.html")


def e_stub(f):
    return f.exists() and 'http-equiv="refresh"' in f.read_text(errors="ignore")


def resolve(mapa):
    final = {}
    for origem in mapa:
        destino, vistos = mapa[origem], {origem}
        while destino in mapa:
            if destino in vistos:
                sys.exit(f"ciclo de redirecionamento em {origem}")
            vistos.add(destino)
            destino = mapa[destino]
        final[origem] = destino
    return final


def valida(final):
    erros = []
    for origem, destino in final.items():
        if origem != nfc(origem):
            erros.append(f"origem fora de NFC: {origem}")
        if not origem.startswith("/") or not (origem.endswith("/") or origem.endswith(".html")):
            erros.append(f"origem precisa começar com / e terminar com / ou .html: {origem}")
        if destino.startswith("http"):
            continue
        alvo = arquivo(destino) if destino != "/" else RAIZ / "index.html"
        if not alvo.exists():
            erros.append(f"destino não existe: {origem} → {destino}")
        elif e_stub(alvo):
            erros.append(f"destino é um redirecionamento fora do JSON: {origem} → {destino}")
        f = arquivo(origem)
        if f.exists() and not e_stub(f):
            erros.append(f"origem é uma página de verdade, não sobrescrevo: {f.relative_to(RAIZ)}")
    return erros


def mapa_nginx(final):
    linhas = ["# gerado por tools/seo/redirects.py a partir de tools/seo/redirects.json", ""]
    for origem, destino in sorted(final.items()):
        url = destino if destino.startswith("http") else BASE + destino
        for chave in sorted({origem, origem.rstrip("/") or "/"}):
            linhas.append(f'"{chave}" "{url}";')
    return "\n".join(linhas) + "\n"


def stubs_gerados():
    for f in RAIZ.rglob("*.html"):
        rel = f.relative_to(RAIZ).as_posix()
        if rel.startswith(NAO_PUBLICADO) or "/." in "/" + rel:
            continue
        if MARCA in f.read_text(errors="ignore")[:400]:
            yield f


def main():
    check = "--check" in sys.argv
    mapa = {nfc(k): v for k, v in json.loads(FONTE.read_text())["redirects"].items()}
    final = resolve(mapa)
    erros = valida(final)
    if erros:
        print("\n".join(erros))
        sys.exit(1)
    mudou = []
    esperados = set()
    for origem, destino in final.items():
        url = destino if destino.startswith("http") else BASE + destino
        f = arquivo(origem)
        esperados.add(f)
        texto = STUB.format(marca=MARCA, url=url)
        if not f.exists() or f.read_text() != texto:
            mudou.append(f"escreve {f.relative_to(RAIZ)}")
            if not check:
                f.parent.mkdir(parents=True, exist_ok=True)
                f.write_text(texto)
    for f in stubs_gerados():
        if f not in esperados:
            mudou.append(f"apaga {f.relative_to(RAIZ)}")
            if not check:
                f.unlink()
                p = f.parent
                while p != RAIZ and not any(p.iterdir()):
                    p.rmdir()
                    p = p.parent
    texto = mapa_nginx(final)
    if not MAPA_NGINX.exists() or MAPA_NGINX.read_text() != texto:
        mudou.append(f"escreve {MAPA_NGINX.relative_to(RAIZ)}")
        if not check:
            MAPA_NGINX.parent.mkdir(parents=True, exist_ok=True)
            MAPA_NGINX.write_text(texto)
    if check:
        if mudou:
            print("desatualizado:\n  " + "\n  ".join(mudou))
            sys.exit(1)
        print(f"ok  {len(final)} redirecionamentos em dia")
    else:
        print(f"ok  {len(final)} redirecionamentos; {len(mudou)} arquivo(s) alterado(s)")


if __name__ == "__main__":
    main()
