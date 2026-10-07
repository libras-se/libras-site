"""Mede a área ocupada pela intérprete (alpha do chroma) em cada tomada do manifest.

Uso: uv run --python 3.12 --with numpy tools/sinais/extent.py <WORKDIR> <RAWDIR>
Grava <WORKDIR>/extent.json: {"<slug>#<tomada>": [x0, y0, x1, y1]} em pixels do quadro 1920x1080.
Serve para escolher o recorte e para marcar sinais que encostam na borda.
"""
import csv
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np

KEY = "0x57B56C"
W, H, SC = 480, 270, 4  # análise em 1/4 da resolução
work, raw = Path(sys.argv[1]), Path(sys.argv[2])
rows = [r for r in csv.DictReader((work / "manifest.csv").open()) if r["arquivo"]]


def bbox(r):
    cmd = ["ffmpeg", "-v", "error", "-ss", r["ini"], "-to", r["fim"], "-i", str(raw / f"{r['arquivo']}.MOV"), "-an",
           "-vf", f"scale={W}:{H},format=yuva444p,chromakey={KEY}:0.05:0.05,alphaextract,format=gray",
           "-f", "rawvideo", "-"]
    a = np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, np.uint8).reshape(-1, H, W)
    m = (a > 128).sum(0) >= 2  # pixel de primeiro plano em pelo menos 2 quadros (ignora ruído)
    ys, xs = np.nonzero(m)
    return f"{r['slug']}#{r['tomada']}", [int(xs.min()) * SC, int(ys.min()) * SC, int(xs.max() + 1) * SC, int(ys.max() + 1) * SC]


with ThreadPoolExecutor(8) as ex:
    out = dict(ex.map(bbox, rows))
(work / "extent.json").write_text(json.dumps(out, indent=0))
arr = np.array(list(out.values()))
print(f"{len(out)} tomadas; x0 min={arr[:,0].min()} p1={np.percentile(arr[:,0],1):.0f} | x1 max={arr[:,2].max()} p99={np.percentile(arr[:,2],99):.0f} | y0 min={arr[:,1].min()}")
