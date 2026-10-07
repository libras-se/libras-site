"""Renderiza as tomadas para revisão: chroma key, fundo da marca, marca d'água, MP4 16:9 + poster WebP.

Uso: python3 tools/sinais/render.py <WORKDIR> <RAWDIR> [--slugs a,b,c] [--force] [--jobs 4]

Renderiza TODAS as tomadas do manifest (inclusive variantes "ou X") e os sinais extras criados na aprovação,
em <WORKDIR>/revisao/<slug>/t<n>.mp4|.webp|.json. O .json guarda a assinatura do corte (arquivo, início, fim e
parâmetros de render): a aprovação registra essa assinatura e o publicar.py só publica se ela não mudou.
Ajustes de corte feitos na aprovação (aprovacoes.json -> "ajustes") têm prioridade sobre o manifest.
Requer ffmpeg (chromakey/despill/libx264) e cwebp no PATH.
"""
import argparse
import csv
import hashlib
import json
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).parent
WATERMARK = HERE / "marca-dagua.png"
APROVACOES = HERE / "aprovacoes.json"
BG = "0xF0FAFA"        # --bg do site
KEY = "0x57B56C"       # verde medido nas bordas dos brutos
SETTINGS = {"v": 2, "w": 1280, "h": 720, "crf": 26, "key": KEY, "bg": BG, "wm": 300, "pad": 0.1}
COLOR = ["-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-color_range", "tv"]


def graph(rgb=False):
    w, h = SETTINGS["w"], SETTINGS["h"]
    tail = (f"scale={w}:{h}:flags=lanczos,format=rgb24[v]" if rgb else
            f"scale={w}:{h}:flags=lanczos:out_color_matrix=bt709:out_range=tv,format=yuv420p[v]")
    # quadro inteiro 16:9 (sem recorte lateral: o espaço de sinalização vai de x≈270 a x≈1550 nos brutos)
    return (
        f"[0:v]setpts=PTS-STARTPTS,format=yuva444p,chromakey={KEY}:0.05:0.05,"
        f"format=rgba,despill=type=green:mix=0.6:expand=0[fg];"
        f"[2:v]format=rgba[bg];[bg][fg]overlay=format=rgb:shortest=1[comp];"
        f"[1:v]scale={SETTINGS['wm']}:-1,format=rgba,colorchannelmixer=aa=0.85[wm];"
        f"[comp][wm]overlay=W-w-56:48:format=rgb," + tail
    )


def inputs(mov, ss, dur=None):
    t = ["-t", f"{dur:.3f}"] if dur else []
    return ["-ss", f"{ss:.3f}", *t, "-i", str(mov), "-i", str(WATERMARK),
            "-f", "lavfi", "-i", f"color=c={BG}:s=1920x1080:r=30000/1001"]


def assinatura(arquivo, ini, fim):
    raw = json.dumps([arquivo, round(float(ini), 3), round(float(fim), 3), SETTINGS], sort_keys=True)
    return hashlib.sha1(raw.encode()).hexdigest()[:12]


def render_take(rawdir, arquivo, ini, fim, pico, base: Path, force=False):
    """Renderiza um corte em base.mp4/.webp/.json. Devolve o conteúdo do .json."""
    ini, fim = float(ini), float(fim)
    sig = assinatura(arquivo, ini, fim)
    side = base.with_suffix(".json")
    if not force and side.exists() and base.with_suffix(".mp4").exists():
        meta = json.loads(side.read_text())
        if meta.get("assinatura") == sig:
            return meta
    base.parent.mkdir(parents=True, exist_ok=True)
    mov = Path(rawdir) / f"{arquivo}.MOV"
    ss = max(0.0, ini - SETTINGS["pad"])
    dur = fim - ini + 2 * SETTINGS["pad"]
    mp4 = base.with_suffix(".mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", *inputs(mov, ss, dur), "-filter_complex", graph(), "-map", "[v]",
                    "-an", "-c:v", "libx264", "-preset", "slow", "-crf", str(SETTINGS["crf"]), "-profile:v", "high",
                    "-pix_fmt", "yuv420p", *COLOR, "-g", "300", "-movflags", "+faststart", str(mp4)], check=True)
    pico = float(pico) if pico not in (None, "") and ini <= float(pico) <= fim else (ini + fim) / 2
    with tempfile.TemporaryDirectory() as td:
        png = Path(td) / "p.png"
        subprocess.run(["ffmpeg", "-v", "error", "-y", *inputs(mov, pico), "-filter_complex", graph(rgb=True),
                        "-map", "[v]", "-frames:v", "1", str(png)], check=True)
        subprocess.run(["cwebp", "-quiet", "-q", "80", "-m", "6", str(png), "-o", str(base.with_suffix(".webp"))],
                       check=True)
    meta = {"arquivo": arquivo, "ini": round(ini, 3), "fim": round(fim, 3), "pico": round(pico, 3),
            "dur": round(dur, 2), "bytes": mp4.stat().st_size, "assinatura": sig}
    side.write_text(json.dumps(meta, ensure_ascii=False))
    return meta


def load_aprovacoes():
    if APROVACOES.exists():
        return json.loads(APROVACOES.read_text())
    return {"itens": {}, "ajustes": {}, "extras": {}}


def candidatos(work, ap=None):
    """Todas as tomadas a revisar: [(slug, n, arquivo, ini, fim, pico)], com ajustes e extras aplicados."""
    ap = ap or load_aprovacoes()
    out = []
    for r in csv.DictReader((Path(work) / "manifest.csv").open()):
        if not r["arquivo"]:
            continue
        a = ap["ajustes"].get(f"{r['slug']}#{r['tomada']}", {})
        out.append((r["slug"], int(r["tomada"]), a.get("arquivo", r["arquivo"]), a.get("ini", r["ini"]),
                    a.get("fim", r["fim"]), r["pico"]))
    for slug, ex in ap.get("extras", {}).items():
        a = ap["ajustes"].get(f"{slug}#1", {})
        out.append((slug, 1, a.get("arquivo", ex["arquivo"]), a.get("ini", ex["ini"]), a.get("fim", ex["fim"]), ""))
    # itens sem tomada no manifest, mas com corte manual definido na aprovação
    for key, a in ap["ajustes"].items():
        slug, n = key.split("#")
        if "arquivo" in a and not any(c[0] == slug and c[1] == int(n) for c in out):
            out.append((slug, int(n), a["arquivo"], a["ini"], a["fim"], ""))
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument("work")
    p.add_argument("raw")
    p.add_argument("--slugs", default="")
    p.add_argument("--force", action="store_true")
    p.add_argument("--jobs", type=int, default=4)
    args = p.parse_args()
    cands = candidatos(args.work)
    if args.slugs:
        want = set(args.slugs.split(","))
        cands = [c for c in cands if c[0] in want]
    rev = Path(args.work) / "revisao"

    def job(c):
        slug, n, arquivo, ini, fim, pico = c
        return render_take(args.raw, arquivo, ini, fim, pico, rev / slug / f"t{n}", args.force)["bytes"]

    with ThreadPoolExecutor(args.jobs) as ex:
        sizes = list(ex.map(job, cands))
    print(f"{len(cands)} tomadas prontas para revisão em {rev} (média {sum(sizes) / max(1, len(sizes)) / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
