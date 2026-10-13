# Confere se algum quadro tem conteúdo encostando nas bordas do palco. Na página o vídeo fica
# no meio da seção: qualquer coisa cortada na borda vira uma linha reta visível.
#   python3.12 -I bordas.py cache/quadros
import glob
import sys

from PIL import Image

LIMITE = 6  # alfa máximo tolerado na borda (0 a 255)
pior = {"topo": (0, 0), "base": (0, 0), "esquerda": (0, 0), "direita": (0, 0)}
for i, f in enumerate(sorted(glob.glob(f"{sys.argv[1]}/*.png"))):
    a = Image.open(f).getchannel("A")
    w, h = a.size
    for nome, caixa in {"topo": (0, 0, w, 1), "base": (0, h - 1, w, h), "esquerda": (0, 0, 1, h), "direita": (w - 1, 0, w, h)}.items():
        m = a.crop(caixa).getextrema()[1]
        if m > pior[nome][0]:
            pior[nome] = (m, i)
ruins = {k: v for k, v in pior.items() if v[0] > LIMITE}
for k, (m, i) in ruins.items():
    print(f"⚠ borda {k}: alfa {m} no quadro {i + 1} ({i / 30:.2f}s)")
if not ruins:
    print("✓ bordas limpas")
sys.exit(1 if ruins else 0)
