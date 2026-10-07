"""Gera proxies leves dos brutos (640x360, com áudio) para o app de aprovação conferir e ajustar cortes.

Uso: python3 tools/sinais/proxies.py <WORKDIR> <RAWDIR>   -> <WORKDIR>/proxy/<arquivo>.mp4
Keyframe a cada 0,5 s para a busca no navegador ser precisa.
"""
import subprocess
import sys
from pathlib import Path

work, raw = Path(sys.argv[1]), Path(sys.argv[2])
(work / "proxy").mkdir(exist_ok=True)
for mov in sorted(raw.glob("[!.]*.MOV")):
    out = work / "proxy" / f"{mov.stem}.mp4"
    if out.exists():
        continue
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(mov), "-vf", "scale=640:360", "-c:v", "libx264",
                    "-preset", "veryfast", "-crf", "28", "-g", "15", "-pix_fmt", "yuv420p", "-c:a", "aac", "-ac", "1",
                    "-b:a", "64k", "-movflags", "+faststart", str(out)], check=True)
    print(out.name, f"{out.stat().st_size / 1e6:.0f} MB", flush=True)
