"""Desenha cada letra do alfabeto em vários estilos e grava os contornos em tools/sinais/letras.json.

Uso: uv run --python 3.12 --with fonttools --with brotli tools/sinais/letras.py [pasta-de-cache-das-fontes]

As páginas /sinal/letra-x/ e /sinal/numero-n/ mostram a letra ou o número "de vários jeitos" (de forma, cursiva, pontilhada para traçar, com serifa,
pixel e divertida). Para não carregar seis fontes em cada página, o contorno de cada letra vira um <path> de SVG.
O build_pages.py só lê o letras.json; este script roda de novo apenas se a lista de estilos mudar.

Fontes: Museo Sans Rounded (a da marca, em assets/fonts) e fontes de licença aberta (OFL) do Google Fonts,
baixadas para a pasta de cache: Playwrite BR (a cursiva ensinada nas escolas do Brasil), Playfair Display,
Press Start 2P e Rubik Bubbles.
"""
import json
import string
import sys
import urllib.parse
import urllib.request
from pathlib import Path

from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

HERE = Path(__file__).parent
ROOT = HERE.parents[1]
CACHE = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.home() / ".cache" / "libras-sinais-fontes"
GF = "https://raw.githubusercontent.com/google/fonts/main/ofl/"

# estilo: (arquivo local ou caminho no Google Fonts, eixos da fonte variável, o que escrever: {M} maiúscula, {m} minúscula)
ESTILOS = {
    "forma-mai": (ROOT / "assets/fonts/museo-sans-rounded-900.woff2", None, "{M}"),
    "forma-min": (ROOT / "assets/fonts/museo-sans-rounded-900.woff2", None, "{m}"),
    "cursiva-mai": ("playwritebr/PlaywriteBR[wght].ttf", {"wght": 400}, "{M}"),
    "cursiva-min": ("playwritebr/PlaywriteBR[wght].ttf", {"wght": 400}, "{m}"),
    "serifa": ("playfairdisplay/PlayfairDisplay[wght].ttf", {"wght": 900}, "{M}{m}"),
    "pixel": ("pressstart2p/PressStart2P-Regular.ttf", None, "{M}"),
    "divertida": ("rubikbubbles/RubikBubbles-Regular.ttf", None, "{M}"),
}


def fonte(origem, eixos):
    if isinstance(origem, str):
        CACHE.mkdir(parents=True, exist_ok=True)
        arq = CACHE / Path(origem).name
        if not arq.exists():
            urllib.request.urlretrieve(GF + urllib.parse.quote(origem), arq)
        origem = arq
    f = TTFont(origem)
    if eixos and "fvar" in f:
        f = instancer.instantiateVariableFont(f, eixos)
    return f


def desenha(f, texto, escala):
    """Contorno do texto em coordenadas de SVG (y para baixo), em unidades de 1000 por eme."""
    gs, cmap = f.getGlyphSet(), f.getBestCmap()
    pen, caixa, x = SVGPathPen(gs, ntos=lambda v: str(round(v))), BoundsPen(gs), 0
    for ch in texto:
        g = gs[cmap[ord(ch)]]
        t = (escala, 0, 0, -escala, x * escala, 0)
        g.draw(TransformPen(pen, t))
        g.draw(TransformPen(caixa, t))
        x += g.width
    return pen.getCommands(), caixa.bounds


saida = {}
for nome, (origem, eixos, molde) in ESTILOS.items():
    f = fonte(origem, eixos)
    escala = 1000 / f["head"].unitsPerEm
    letras = {L: desenha(f, molde.format(M=L, m=L.lower()), escala) for L in string.ascii_uppercase}
    # a mesma faixa vertical para o alfabeto todo: assim a minúscula fica apoiada na linha, como no caderno
    y0 = min(b[1] for _, b in letras.values())
    y1 = max(b[3] for _, b in letras.values())
    lado = max(y1 - y0, max(b[2] - b[0] for _, b in letras.values())) * 1.12
    saida[nome] = {}
    for L, (d, b) in letras.items():
        cx = (b[0] + b[2]) / 2
        saida[nome][L] = {"d": d, "vb": f"{round(cx - lado / 2)} {round((y0 + y1) / 2 - lado / 2)} {round(lado)} {round(lado)}"}
    if nome.endswith("-min"):  # algarismo não tem minúscula
        continue
    for n in range(21):  # números de 0 a 20, para as páginas /sinal/numero-n/
        d, b = desenha(f, str(n), escala)
        cx, ln = (b[0] + b[2]) / 2, max(lado, (b[2] - b[0]) * 1.12)
        saida[nome][str(n)] = {"d": d, "vb": f"{round(cx - ln / 2)} {round((y0 + y1) / 2 - ln / 2)} {round(ln)} {round(ln)}"}
(HERE / "letras.json").write_text(json.dumps(saida, ensure_ascii=False, separators=(",", ":")))
print(f"letras.json: {len(saida)} estilos, {(HERE / 'letras.json').stat().st_size // 1024} KB")
