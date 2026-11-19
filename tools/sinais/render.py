"""Renderiza as tomadas para revisão: chroma key, fundo da marca, marca d'água, MP4 16:9 + poster WebP.

Uso: python3 tools/sinais/render.py <WORKDIR> <RAWDIR> [--slugs a,b,c] [--force] [--jobs 4]

Renderiza TODAS as tomadas do manifest (inclusive variantes "ou X") e os sinais extras criados na aprovação,
em <WORKDIR>/revisao/<slug>/t<n>.mp4|.webp|.json. O .json guarda a assinatura do corte (arquivo, início, fim e
parâmetros de render): a aprovação registra essa assinatura e o publicar.py só publica se ela não mudou.
Ajustes de corte feitos na aprovação (aprovacoes.json -> "ajustes") têm prioridade sobre o manifest.
Perfis de chave por sinal ficam em <WORKDIR>/chaves.json ({"itens": {"<slug>": "<perfil>"}}, perfis em CHAVES).
Sinal sem perfil usa o chromakey padrão e mantém a assinatura de antes; com perfil, o perfil entra na assinatura.
Requer ffmpeg (chromakey/geq/despill/libx264) e cwebp no PATH.
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

# Chave por diferença de cor: D = G - max(R, B). O chromakey compara só o croma e apaga o cabelo escuro com
# reflexo verde (D ≈ 30-50); o fundo fica em D ≈ 71-77, pele < 0, camiseta ≈ 0. Alfa = 1 abaixo de "lo", 0 acima
# de "hi", rampa no meio. Nos pixels de borda a cor do verde (k) é descontada: C' = (C - (1 - α)·k) / α, e depois
# G' = min(G', max(R', B')). O alfa perde 1 px (erosão) e é suavizado ("blur"): o H.264 4:2:0 do celular vaza o
# croma verde ~2 px para dentro da pele e deixaria um contorno oliva nos dedos. Fora de x0..x1 o alfa é zero:
# a tela tem duas marcas fixas em x ≈ 80-180 (o espaço de sinalização vai de x ≈ 270 a 1550).
CHAVES = {
    # v2: recorta já em 1280x720 (o blur e a erosão de 1 px valem nessa escala)
    "dif": {"v": 2, "hi": 64, "lo": 12, "k": [87, 181, 108], "amin": 0.06, "blur": 0.6, "x0": 220, "x1": 1700},
}


def chave_de(base: Path):
    """Perfil de chave do sinal (pasta revisao/<slug>/), lido de <WORKDIR>/chaves.json. None = chromakey padrão."""
    f = Path(base).parent.parent.parent / "chaves.json"
    if not f.exists():
        return None
    nome = json.loads(f.read_text()).get("itens", {}).get(Path(base).parent.name)
    if nome and nome not in CHAVES:
        raise ValueError(f"perfil de chave desconhecido: {nome}")
    return nome


def keyer(chave=None, esc=1.0):
    """Filtro de chave. esc = escala do quadro em relação ao bruto 1920x1080 (as faixas x0/x1 acompanham)."""
    if not chave:
        return f"format=yuva444p,chromakey={KEY}:0.05:0.05,format=rgba,despill=type=green:mix=0.6:expand=0"
    c = CHAVES[chave]
    hi, faixa, (kr, kg, kb) = c["hi"], c["hi"] - c["lo"], c["k"]
    x0, x1 = round(c["x0"] * esc), round(c["x1"] * esc)
    d = "(g(X,Y)-max(r(X,Y),b(X,Y)))"
    st = f"st(0,clip(({hi}-{d})/{faixa},0,1))"  # α em 0..1, guardado na variável 0 da expressão

    def limpa(p, k):  # desconta a parte de fundo verde do pixel
        return f"clip(({p}(X,Y)-(1-ld(0))*{k})/max(ld(0),{c['amin']}),0,255)"

    r, b = f"{st};{limpa('r', kr)}", f"{st};{limpa('b', kb)}"
    g = f"{st};st(1,{limpa('r', kr)});st(2,{limpa('b', kb)});min({limpa('g', kg)},max(ld(1),ld(2)))"
    a = f"if(between(X,{x0},{x1}),clip(({hi}-{d})*255/{faixa},0,255),0)"
    return (f"format=gbrap,geq=r='{r}':g='{g}':b='{b}':a='{a}',"
            f"erosion=threshold0=0:threshold1=0:threshold2=0,gblur=sigma={c['blur']}:planes=8,format=rgba")


def graph(rgb=False, chave=None):
    w, h = SETTINGS["w"], SETTINGS["h"]
    tail = (f"scale={w}:{h}:flags=lanczos,format=rgb24[v]" if rgb else
            f"scale={w}:{h}:flags=lanczos:out_color_matrix=bt709:out_range=tv,format=yuv420p[v]")
    # quadro inteiro 16:9 (sem recorte lateral: o espaço de sinalização vai de x≈270 a x≈1550 nos brutos)
    if chave:
        # a chave por diferença (geq) é cara: reduz para a saída antes de recortar (2,25x menos pixels que 1080p);
        # fundo e marca d'água acompanham a escala, então o quadro final fica igual ao do caminho padrão
        e = w / 1920
        return (
            f"[0:v]setpts=PTS-STARTPTS,scale={w}:{h}:flags=lanczos,{keyer(chave, e)}[fg];"
            f"[2:v]scale={w}:{h},format=rgba[bg];[bg][fg]overlay=format=rgb:shortest=1[comp];"
            f"[1:v]scale={round(SETTINGS['wm'] * e)}:-1,format=rgba,colorchannelmixer=aa=0.85[wm];"
            f"[comp][wm]overlay=W-w-{round(56 * e)}:{round(48 * e)}:format=rgb," + tail
        )
    return (
        f"[0:v]setpts=PTS-STARTPTS,{keyer(chave)}[fg];"
        f"[2:v]format=rgba[bg];[bg][fg]overlay=format=rgb:shortest=1[comp];"
        f"[1:v]scale={SETTINGS['wm']}:-1,format=rgba,colorchannelmixer=aa=0.85[wm];"
        f"[comp][wm]overlay=W-w-56:48:format=rgb," + tail
    )


def inputs(mov, ss, dur=None):
    t = ["-t", f"{dur:.3f}"] if dur else []
    return ["-ss", f"{ss:.3f}", *t, "-i", str(mov), "-i", str(WATERMARK),
            "-f", "lavfi", "-i", f"color=c={BG}:s=1920x1080:r=30000/1001"]


def assinatura(arquivo, ini, fim, chave=None):
    partes = [arquivo, round(float(ini), 3), round(float(fim), 3), SETTINGS]
    if chave:  # sem perfil, a assinatura fica igual à de antes dos perfis (aprovações antigas continuam valendo)
        partes.append({"chave": chave, **CHAVES[chave]})
    raw = json.dumps(partes, sort_keys=True)
    return hashlib.sha1(raw.encode()).hexdigest()[:12]


def render_take(rawdir, arquivo, ini, fim, pico, base: Path, force=False):
    """Renderiza um corte em base.mp4/.webp/.json. Devolve o conteúdo do .json."""
    ini, fim = float(ini), float(fim)
    chave = chave_de(base)
    sig = assinatura(arquivo, ini, fim, chave)
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
    subprocess.run(["ffmpeg", "-v", "error", "-y", *inputs(mov, ss, dur), "-filter_complex", graph(chave=chave), "-map", "[v]",
                    "-an", "-c:v", "libx264", "-preset", "slow", "-crf", str(SETTINGS["crf"]), "-profile:v", "high",
                    "-pix_fmt", "yuv420p", *COLOR, "-g", "300", "-movflags", "+faststart", str(mp4)], check=True)
    pico = float(pico) if pico not in (None, "") and ini <= float(pico) <= fim else (ini + fim) / 2
    with tempfile.TemporaryDirectory() as td:
        png = Path(td) / "p.png"
        subprocess.run(["ffmpeg", "-v", "error", "-y", *inputs(mov, pico), "-filter_complex", graph(rgb=True, chave=chave),
                        "-map", "[v]", "-frames:v", "1", str(png)], check=True)
        subprocess.run(["cwebp", "-quiet", "-q", "80", "-m", "6", str(png), "-o", str(base.with_suffix(".webp"))],
                       check=True)
    meta = {"arquivo": arquivo, "ini": round(ini, 3), "fim": round(fim, 3), "pico": round(pico, 3),
            "dur": round(dur, 2), "bytes": mp4.stat().st_size, "assinatura": sig}
    if chave:
        meta["chave"] = chave
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
