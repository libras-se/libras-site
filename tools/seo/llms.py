#!/usr/bin/env python3
"""Mantém o blog em dia no llms.txt e no llms-full.txt.

- llms-full.txt: refaz a lista "Artigos publicados" com todos os posts publicados (pilares primeiro,
  depois do mais novo para o mais antigo), usando a description do JSON-LD de cada post.
- llms.txt e llms-full.txt: atualizam a contagem de posts.

Os dois arquivos seguem em ASCII (sem acentos), como já eram. Idempotente.

Uso:  python3 tools/seo/llms.py
"""
import importlib.util
import json
import re
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
_spec = importlib.util.spec_from_file_location("home", ROOT / "tools/blog/home.py")
home = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(home)
PILARES = [s for v in json.loads((HERE / "links.json").read_text())["pilares"].values() for s in v]


def ascii_(t):
    for x, y in (("–", "-"), ("—", "-"), ("“", '"'), ("”", '"'), ("‘", "'"), ("’", "'"), ("º", "o"), ("ª", "a"), ("…", "..."), ("·", "-")):
        t = t.replace(x, y)
    t = "".join(c for c in unicodedata.normalize("NFD", t) if unicodedata.category(c) != "Mn")
    return " ".join(t.encode("ascii", "ignore").decode().split())


def main():
    arts = home.artigos()
    pil = [s for s in PILARES if s in arts]
    resto = sorted((s for s in arts if s not in PILARES), key=lambda s: arts[s]["a"]["datePublished"], reverse=True)
    linhas = [f"- https://libras.se/blog/{s}/ - {ascii_(arts[s]['a'].get('description', ''))}" for s in pil + resto]
    n = len(arts)

    f = ROOT / "llms-full.txt"
    t = f.read_text()
    bloco = f"Artigos publicados ({n} paginas indexaveis; os pilares de cada tema vem primeiro):\n\n" + "\n".join(linhas) + "\n"
    t, k = re.subn(r"Artigos publicados \([^)]*\):\n\n(?:- https://libras\.se/blog/[^\n]*\n)+", lambda m: bloco, t)
    assert k == 1, "lista de artigos não encontrada no llms-full.txt"
    f.write_text(t)

    f = ROOT / "llms.txt"
    t = f.read_text()
    t, k1 = re.subn(r"\): \d+ artigos sobre", f"): {n} artigos sobre", t)
    t, k2 = re.subn(r"O blog tem \d+ posts indexaveis", f"O blog tem {n} posts indexaveis", t)
    assert k1 == 1 and k2 == 1, "contagens não encontradas no llms.txt"
    f.write_text(t)
    print(f"ok  llms-full.txt com {n} artigos ({len(pil)} pilares); contagens do llms.txt atualizadas")


if __name__ == "__main__":
    main()
