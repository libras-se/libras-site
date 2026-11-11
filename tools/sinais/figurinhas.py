"""Figurinhas dos sinais: o elemento divertido de cada página (mascote do time, símbolos do estado, letra desenhada...).

Uso: uv run --python 3.12 --with numpy --with pillow tools/sinais/figurinhas.py <comando>
     gerar [slug ...] [--pendentes] [--categoria "Times de futebol"] [--jobs 3] [--refazer]
            pede a figurinha ao Codex (geração de imagem da conta ChatGPT), recorta o fundo e publica
     recortar [slug ...]   refaz o recorte a partir do original já gerado (depois de mexer no recorte)
     compor [slug ...]     monta o cartão: a ilustração do sinal com a figurinha no canto mais vazio
     folha <saida.jpg>     folha de contato com todas as figurinhas, para aprovar de uma vez

O que cada etapa grava:
- <WORK>/figurinhas/<slug>/v<k>.png   original do Codex, em fundo chapado (magenta ou verde), fora do repositório
- assets/img/sinais/figurinhas/<slug>.webp   a figurinha recortada, com transparência (600 px)
- assets/img/sinais/cartoes/<slug>.webp      ilustração + figurinha (960x720), usada nas páginas /sinal/ e no og:image
A ilustração limpa (assets/img/sinais/<slug>.webp) não muda: os jogos e as atividades continuam com ela, senão a
figurinha entregaria a resposta.

O texto pedido ao Codex vem de elementos.json ("figurinhas" -> "arte"; as letras e os números são montados a partir de "letras" e "numeros").
O limite de imagens do Codex vale aqui também: quando ele para, rode `gerar --pendentes` de novo mais tarde.
"""
import argparse
import json
import os
import shutil
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

HERE = Path(__file__).parent
ROOT = HERE.parents[1]
WORK = Path(os.environ.get("SINAIS_WORK", "/Volumes/Extreme Pro/LIBRAS.SE/TRABALHOS/VIDEOS GLOSSARIO/_processamento"))
ORIG = WORK / "figurinhas"
ILU = ROOT / "assets" / "img" / "sinais"
FIG = ILU / "figurinhas"
CART = ILU / "cartoes"
ESTILO = HERE / "ilustracao-estilo.jpg"
EL = json.loads((HERE / "elementos.json").read_text())
SINAIS = {s["slug"]: s for s in json.loads((ROOT / "sinal" / "sinais.json").read_text())["sinais"]}
FUNDOS = {"magenta": ("#FF00FF", "magenta or hot pink"), "verde": ("#00FF00", "green")}

PROMPT = """Use your image generation tool to create ONE square (1:1) image: a fun die-cut STICKER illustration for a children-friendly Brazilian Sign Language dictionary.

The attached image is the STYLE REFERENCE for line work and coloring only: clean vector-like illustration, confident dark teal (#0e3538) outlines of even weight, flat colors with a single soft shadow tone, friendly and slightly cute. Do NOT draw the woman from the reference and do not copy its composition.

Subject: {arte}

Rules:
- One compact composition, centered, filling about 80% of the canvas, with a thick white die-cut sticker border of even width all around its silhouette.
- Background: perfectly flat solid {cor} {hex} from edge to edge. No gradient, no shadow, no texture, nothing else on the background.
- Never use {evitar} inside the subject.
- {texto}
- No human hands making signs or gestures. No official club crest, no brand logo, no watermark, no real person.

Save the final image as figurinha.png in the current directory. Do not change anything else.
"""


def lista_pt(itens):
    return ", ".join(itens[:-1]) + " e " + itens[-1] if len(itens) > 1 else itens[0]


def pedido(slug):
    """(arte, texto alternativo, fundo) de um sinal; as letras saem da tabela 'letras'."""
    if slug in EL["letras"]:
        L, d = SINAIS[slug]["palavra"][-1], EL["letras"][slug]
        coisas = ", ".join(f"a {en}" for _, en in d["com"])
        arte = (f"a giant chunky capital letter {L}, drawn as a playful 3D block letter in {d['cor']} with a lighter highlight, "
                f"with small cute things whose Portuguese names start with {L} hugging it and peeking around it: {coisas}. "
                f"Each little thing has a happy face and its own bright color.")
        return arte, f"letra {L} gigante com {lista_pt([pt for pt, _ in d['com']])}", "magenta"
    if slug in EL["numeros"]:
        d = EL["numeros"][slug]
        n = d["n"]
        quem = f"the single digit {n}" if n < 10 else f"the two digits {' and '.join(str(n))} side by side, forming {n}"
        arte = (f"the number {n} ({quem}) drawn as a giant chunky playful 3D block numeral in {d['cor']} with a lighter highlight, "
                f"as a cheerful character with a happy face and little arms and legs, jumping and celebrating, with colorful "
                f"confetti and a few small stars around it.")
        return arte, f"o número {n} como personagem sorridente", "magenta"
    f = EL["figurinhas"].get(slug)
    return (f["arte"], f["alt"], f.get("fundo", "magenta")) if f else None


def original(slug):
    vs = sorted((p for p in (ORIG / slug).glob("v*.png") if p.stem[1:].isdigit()), key=lambda p: int(p.stem[1:]))
    return vs[-1] if vs else None


def recortar(slug):
    """Tira o fundo chapado (chroma), corrige a borda e grava a figurinha com transparência."""
    src = original(slug)
    fundo = json.loads(src.with_suffix(".json").read_text()).get("fundo", "magenta")
    a = np.asarray(Image.open(src).convert("RGB")).astype(np.float32)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    # quanto o pixel "é fundo": 255 no fundo puro, perto de 0 no branco da borda e nas cores do desenho
    chave = np.minimum(r, b) - g if fundo == "magenta" else g - np.maximum(r, b)
    alfa = 1 - np.clip((chave - 40) / 170, 0, 1)
    # na borda, o pixel é mistura de desenho com fundo: desfaz a mistura para não sobrar franja colorida
    cor_fundo = np.array([255, 0, 255] if fundo == "magenta" else [0, 255, 0], np.float32)
    seguro = np.maximum(alfa, 0.05)[..., None]
    limpo = np.clip((a - (1 - alfa[..., None]) * cor_fundo) / seguro, 0, 255)
    rgba = np.dstack([np.where(alfa[..., None] < 1, limpo, a), alfa * 255]).astype(np.uint8)
    im = Image.fromarray(rgba, "RGBA")
    im = im.crop(im.getchannel("A").point(lambda v: 255 if v > 24 else 0).getbbox())
    lado = max(im.size)
    quadro = Image.new("RGBA", (lado, lado), (0, 0, 0, 0))
    quadro.paste(im, ((lado - im.width) // 2, (lado - im.height) // 2))
    FIG.mkdir(parents=True, exist_ok=True)
    quadro.resize((600, 600), Image.LANCZOS).save(FIG / f"{slug}.webp", quality=88, method=6)


def gerar(slug, tentativas=2):
    arte, alt, fundo = pedido(slug)
    hexa, evitar = FUNDOS[fundo]
    if slug in EL["letras"]:
        texto = f"The capital letter {SINAIS[slug]['palavra'][-1]} is the ONLY letter in the image. No other text, letters or numbers."
    elif slug in EL["numeros"]:
        n = EL["numeros"][slug]["n"]
        texto = f"The number {n} is the ONLY number in the image, written exactly once. No letters, no words, no other digits."
    else:
        texto = "No text, no letters, no numbers anywhere."
    prompt = PROMPT.format(arte=arte, cor="green" if fundo == "verde" else "magenta", hex=hexa, evitar=evitar, texto=texto)
    destino = ORIG / slug
    destino.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        shutil.copy(ESTILO, td / "estilo.jpg")
        for _ in range(tentativas):
            out = subprocess.run(["codex", "exec", "--skip-git-repo-check", "-C", str(td), "-s", "workspace-write",
                                  "-i", str(td / "estilo.jpg"), "-"], input=prompt, text=True, capture_output=True, timeout=900)
            if (td / "figurinha.png").exists():
                break
            if "usage limit" in (out.stdout + out.stderr):
                raise RuntimeError(f"{slug}: limite de uso do Codex (tente de novo mais tarde)")
        else:
            raise RuntimeError(f"{slug}: o Codex não gerou a imagem")
        k = 1 + max([int(p.stem[1:]) for p in destino.glob("v*.png") if p.stem[1:].isdigit()] or [0])
        shutil.copy(td / "figurinha.png", destino / f"v{k}.png")
    (destino / f"v{k}.json").write_text(json.dumps({"versao": k, "fundo": fundo, "arte": arte, "alt": alt}, ensure_ascii=False))
    recortar(slug)
    return slug, k


def compor(slug):
    """Cola a figurinha no canto mais vazio da ilustração do sinal (de preferência em cima)."""
    base_p, fig_p = ILU / f"{slug}.webp", FIG / f"{slug}.webp"
    if not base_p.exists() or not fig_p.exists():
        return False
    base = Image.open(base_p).convert("RGB")
    W, H = base.size
    a = np.asarray(base).astype(np.int16)
    tinta = (abs(a - a[4:40, 4:40].reshape(-1, 3).mean(0)).max(-1) > 26)  # o que não é fundo
    fig0 = Image.open(fig_p).convert("RGBA")
    m = round(W * 0.02)
    melhor = None
    for frac in (0.40, 0.36, 0.32, 0.28, 0.24):
        t = round(H * frac)
        cantos = {"se": (m, m), "sd": (W - t - m, m), "ie": (m, H - t - m), "id": (W - t - m, H - t - m)}
        notas = {c: tinta[y:y + t, x:x + t].mean() + (0.004 if c[0] == "i" else 0) for c, (x, y) in cantos.items()}
        c = min(notas, key=notas.get)
        melhor = (t, cantos[c], c)
        if notas[c] < 0.012:
            break
    t, (x, y), c = melhor
    fig = fig0.resize((t, t), Image.LANCZOS).rotate(-6 if c[1] == "e" else 6, resample=Image.BICUBIC, expand=True)
    x, y = x - (fig.width - t) // 2, y - (fig.height - t) // 2
    sombra = Image.new("RGBA", base.size, (0, 0, 0, 0))
    sombra.paste((14, 53, 56, 70), (x + 3, y + 7), fig.getchannel("A"))
    out = Image.alpha_composite(base.convert("RGBA"), sombra.filter(ImageFilter.GaussianBlur(7)))
    out.alpha_composite(fig, (max(x, 0), max(y, 0)), (max(-x, 0), max(-y, 0)))
    CART.mkdir(parents=True, exist_ok=True)
    out.convert("RGB").save(CART / f"{slug}.webp", quality=82, method=6)
    return True


def folha(saida):
    figs = sorted(FIG.glob("*.webp"))
    n, t = 8, 240
    sheet = Image.new("RGB", (n * t, -(-len(figs) // n) * t), (14, 53, 56))
    for i, f in enumerate(figs):
        im = Image.open(f).convert("RGBA").resize((t - 16, t - 16), Image.LANCZOS)
        sheet.paste(im, ((i % n) * t + 8, (i // n) * t + 8), im)
    sheet.save(saida, quality=85)
    print(f"{len(figs)} figurinhas em {saida}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("cmd", choices=["gerar", "recortar", "compor", "folha"])
    p.add_argument("alvos", nargs="*")
    p.add_argument("--pendentes", action="store_true", help="todos os sinais com pedido em elementos.json e sem figurinha")
    p.add_argument("--categoria", action="append", default=[])
    p.add_argument("--refazer", action="store_true", help="gera versão nova mesmo se já existe")
    p.add_argument("--jobs", type=int, default=3)
    args = p.parse_args()
    if args.cmd == "folha":
        return folha(args.alvos[0])
    slugs = list(args.alvos)
    if args.cmd == "gerar":
        slugs += [s for c in args.categoria for s, d in SINAIS.items() if d["categoria"] == c]
        if args.pendentes:
            slugs += list(SINAIS)
        slugs = [s for s in dict.fromkeys(slugs) if pedido(s) and (args.refazer or not (FIG / f"{s}.webp").exists())]
        print(f"gerar {len(slugs)}: {', '.join(slugs) or 'nada'}", flush=True)
        with ThreadPoolExecutor(args.jobs) as ex:
            for f in [ex.submit(gerar, s) for s in slugs]:
                try:
                    slug, k = f.result()
                    compor(slug)
                    print(f"{slug}: v{k}", flush=True)
                except Exception as e:  # segue com os outros
                    print(f"ERRO {e}", flush=True)
        return
    slugs = slugs or sorted(d.name for d in ORIG.iterdir() if original(d.name)) if args.cmd == "recortar" else \
        slugs or sorted(f.stem for f in FIG.glob("*.webp"))
    for s in slugs:
        if args.cmd == "recortar":
            recortar(s)
        print(s, "ok" if args.cmd == "recortar" or compor(s) else "sem ilustração ou figurinha")


if __name__ == "__main__":
    main()
