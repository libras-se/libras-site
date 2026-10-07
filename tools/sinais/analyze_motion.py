"""Detecta os trechos de sinalização (fora da pose de repouso) em cada bruto.

Uso: uv run --python 3.12 --with numpy tools/sinais/analyze_motion.py <RAWDIR> <WORKDIR> [nome ...]
Grava <WORKDIR>/motion/<nome>.npz (curvas por quadro) e <nome>.json (segmentos).
"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

SIZE = 128  # análise em baixa resolução (recorte quadrado central 1080x1080)
FPS = 30000 / 1001

raw, work = Path(sys.argv[1]), Path(sys.argv[2])
names = sys.argv[3:] or sorted(p.stem for p in raw.glob("[!.]*.MOV"))


def frames(mov):
    cmd = ["ffmpeg", "-v", "error", "-i", str(mov), "-an",
           "-vf", f"crop=1080:1080:420:0,scale={SIZE}:{SIZE}:flags=area,format=gray",
           "-f", "rawvideo", "-"]
    data = subprocess.run(cmd, capture_output=True, check=True).stdout
    return np.frombuffer(data, np.uint8).reshape(-1, SIZE, SIZE)


def segments(active, min_gap, min_len):
    """Converte máscara booleana em [(ini, fim)], juntando lacunas curtas e descartando trechos curtos."""
    segs, start = [], None
    for i, a in enumerate(np.append(active, False)):
        if a and start is None:
            start = i
        elif not a and start is not None:
            segs.append([start, i])
            start = None
    merged = []
    for s in segs:
        if merged and s[0] - merged[-1][1] < min_gap:
            merged[-1][1] = s[1]
        else:
            merged.append(s)
    return [s for s in merged if s[1] - s[0] >= min_len]


for name in names:
    f = frames(raw / f"{name}.MOV").astype(np.float32)
    energy = np.r_[0, np.abs(np.diff(f, axis=0)).mean(axis=(1, 2))]
    energy_s = np.convolve(energy, np.ones(9) / 9, mode="same")
    # Referência de repouso local: a postura deriva ao longo da gravação, então a imagem de repouso é a mediana
    # dos quadros parados e próximos do repouso numa janela de ±20s (refinada em duas passadas).
    ref_all = np.median(f[:: max(1, len(f) // 600)], axis=0)
    dist = np.abs(f - ref_all).mean(axis=(1, 2))
    sec = int(round(FPS))
    for _ in range(2):
        calm = (dist < np.percentile(dist, 45)) & (energy_s < np.percentile(energy_s, 50))
        idx = np.flatnonzero(calm)
        new = np.empty_like(dist)
        for c in range(0, len(f), sec):
            win = idx[(idx >= c - 20 * sec) & (idx < c + 20 * sec)]
            ref = np.median(f[win[:: max(1, len(win) // 60)]], axis=0) if len(win) > 10 else ref_all
            new[c:c + sec] = np.abs(f[c:c + sec] - ref).mean(axis=(1, 2))
        dist = new
    k = 5
    dist_s = np.convolve(dist, np.ones(k) / k, mode="same")
    calm = (dist_s < np.percentile(dist_s, 40)) & (energy_s < np.percentile(energy_s, 50))
    lo = float(np.median(dist_s[calm]))
    mad = float(np.median(np.abs(dist_s[calm] - lo))) + 1e-6
    hi = np.percentile(dist_s, 95)
    thr = lo + max(6 * mad, 0.2 * (hi - lo))
    segs = segments(dist_s > thr, min_gap=int(0.3 * FPS), min_len=int(0.5 * FPS))
    out = []
    for a, b in segs:
        peak = a + int(np.argmax(dist_s[a:b]))
        out.append({"ini": round(a / FPS, 3), "fim": round(b / FPS, 3), "pico": round(peak / FPS, 3),
                    "dur": round((b - a) / FPS, 3), "amp": round(float(dist_s[a:b].max()), 2)})
    np.savez_compressed(work / "motion" / f"{name}.npz", dist=dist_s, energy=energy, energy_s=energy_s)
    (work / "motion" / f"{name}.json").write_text(json.dumps(
        {"fps": FPS, "frames": len(f), "limiar": round(float(thr), 2), "repouso": round(lo, 2),
         "segmentos": out}, ensure_ascii=False, indent=1))
    durs = [s["dur"] for s in out]
    print(f"{name}: {len(out)} segmentos, dur mediana {np.median(durs):.2f}s, max {max(durs):.2f}s", flush=True)
