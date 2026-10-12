#!/usr/bin/env python3
"""Avisa o IndexNow (Bing, Yandex, Seznam e outros) das páginas que mudaram num push.

    python3 tools/seo/indexnow.py <sha-antes> <sha-depois>            # só lista as URLs
    python3 tools/seo/indexnow.py <sha-antes> <sha-depois> --enviar   # lista e envia

Usado pelo workflow .github/workflows/indexnow.yml depois do deploy do GitHub Pages.
A chave é o arquivo <32 hex>.txt na raiz do site, publicado em https://libras.se/<chave>.txt.
"""
import json
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
HOST = "libras.se"
FORA = ("tools/", "scripts/", "og/", "emails/", "audit/", "crm/", "CLIENTES/", "cogna 2026/", ".github/", "404.html")


def chave():
    achadas = [p.stem for p in RAIZ.glob("*.txt") if re.fullmatch(r"[0-9a-f]{32}", p.stem)]
    if len(achadas) != 1:
        sys.exit(f"esperava um arquivo de chave <32 hex>.txt na raiz, achei {len(achadas)}")
    return achadas[0]


def urls(antes, depois):
    if not antes or set(antes) == {"0"}:
        antes = f"{depois}~1"
    nomes = subprocess.run(
        ["git", "-C", str(RAIZ), "diff", "--name-only", "--diff-filter=AMR", "-z", antes, depois],
        capture_output=True, text=True, check=True,
    ).stdout.split("\0")
    out = []
    for n in nomes:
        if not n.endswith(".html") or n.startswith(FORA):
            continue
        caminho = n[: -len("index.html")] if n.endswith("index.html") else n
        out.append(f"https://{HOST}/{caminho}")
    return sorted(set(out))


def envia(lista, k):
    corpo = json.dumps({
        "host": HOST,
        "key": k,
        "keyLocation": f"https://{HOST}/{k}.txt",
        "urlList": lista[:10000],
    }).encode()
    req = urllib.request.Request(
        "https://api.indexnow.org/indexnow", data=corpo,
        headers={"Content-Type": "application/json; charset=utf-8"}, method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        print(f"IndexNow respondeu {r.status} para {len(lista)} URL(s)")


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) != 2:
        sys.exit(__doc__)
    k = chave()
    lista = urls(*args)
    print("\n".join(lista) or "nenhuma página publicada mudou")
    if "--enviar" in sys.argv and lista:
        envia(lista, k)


if __name__ == "__main__":
    main()
