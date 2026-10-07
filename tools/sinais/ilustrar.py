"""Gera a ilustração de dicionário de cada sinal com o Codex (geração de imagem da conta ChatGPT).

Uso: uv run --python 3.12 --with numpy tools/sinais/ilustrar.py [slug ...] [--aprovados] [--nota "texto"] [--jobs 3]
     --aprovados  gera para todos os sinais com vídeo aprovado que ainda não têm ilustração

Para cada sinal, a partir da tomada aprovada (revisao/<slug>/t<n>.mp4):
1. Acha o trecho ativo do sinal pela curva de movimento (motion/<arquivo>.npz) e extrai o quadro-chave (meio)
   e uma tira com 3 quadros (começo, meio e fim do movimento). A marca d'água é coberta.
2. Chama `codex exec` com o prompt (ilustracao-prompt.txt), os dois quadros e a referência de estilo
   (ilustracao-estilo.jpg) e salva em <WORKDIR>/ilustracoes/<slug>/v<k>.png + v<k>.json.
A nota (opcional) vira uma instrução extra para o Codex, usada no "gerar de novo" do app de aprovação.
"""
import argparse
import datetime
import json
import shutil
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
WORK = Path("/Volumes/Extreme Pro/LIBRAS.SE/TRABALHOS/VIDEOS GLOSSARIO/_processamento")
ESTILO = HERE / "ilustracao-estilo.jpg"
PROMPT = HERE / "ilustracao-prompt.txt"
FPS = 30000 / 1001
COBRE_MARCA = "drawbox=x=1020:y=15:w=250:h=70:color=0xF0FAFA:t=fill,crop=960:720:160:0"


def trecho_ativo(meta):
    """Começo e fim (s, relativos ao clipe) do movimento do sinal, pela distância ao repouso."""
    npz = WORK / "motion" / f"{meta['arquivo']}.npz"
    pad = 0.1
    dur = meta["fim"] - meta["ini"] + 2 * pad
    if not npz.exists():
        return dur * 0.2, dur * 0.7
    d = np.load(npz)["dist"]
    a, b = int((meta["ini"] - pad) * FPS), int((meta["fim"] + pad) * FPS)
    seg = d[a:b]
    on = np.flatnonzero(seg > seg.min() + 0.5 * (seg.max() - seg.min()))
    if len(on) < 3:
        return dur * 0.2, dur * 0.7
    return on[0] / FPS, on[-1] / FPS


def quadros(video, meta, pasta):
    t0, t1 = trecho_ativo(meta)
    chave = pasta / "chave.png"
    seq = pasta / "seq.png"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{(t0 + t1) / 2:.2f}", "-i", str(video), "-frames:v", "1",
                    "-vf", COBRE_MARCA, str(chave)], check=True)
    ts = [t0 + (t1 - t0) * f for f in (0.1, 0.5, 0.9)]
    ins = sum([["-ss", f"{t:.2f}", "-i", str(video)] for t in ts], [])
    fc = "".join(f"[{i}:v]{COBRE_MARCA},scale=480:360,trim=end_frame=1[v{i}];" for i in range(3)) + "[v0][v1][v2]hstack=3"
    subprocess.run(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex", fc, "-frames:v", "1", str(seq)], check=True)
    return chave, seq


def gerar(slug, nota="", tentativas=2):
    ap = json.loads((HERE / "aprovacoes.json").read_text())
    d = ap["itens"][slug]
    n = d.get("aprovado", {}).get("tomada") or d.get("tomada", 1)
    meta = json.loads((WORK / "revisao" / slug / f"t{n}.json").read_text())
    destino = WORK / "ilustracoes" / slug
    destino.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        chave, seq = quadros(WORK / "revisao" / slug / f"t{n}.mp4", meta, td)
        shutil.copy(ESTILO, td / "estilo.jpg")
        extra = f"- Corrections requested by the reviewer (follow them strictly): {nota}\n" if nota else ""
        prompt = PROMPT.read_text().replace("{{NOTA}}", extra).replace("{{SAIDA}}", "ilustracao.png")
        for _ in range(tentativas):
            subprocess.run(["codex", "exec", "--skip-git-repo-check", "-C", str(td), "-s", "workspace-write",
                            "-i", str(chave), "-i", str(seq), "-i", str(td / "estilo.jpg"), "-"],
                           input=prompt, text=True, capture_output=True, timeout=900)
            if (td / "ilustracao.png").exists():
                break
        else:
            raise RuntimeError(f"{slug}: o Codex não gerou a imagem")
        k = 1 + max([int(p.stem[1:]) for p in destino.glob("v*.png") if p.stem[1:].isdigit()] or [0])
        shutil.copy(td / "ilustracao.png", destino / f"v{k}.png")
        shutil.copy(chave, destino / f"v{k}-referencia.png")
    (destino / f"v{k}.json").write_text(json.dumps({
        "versao": k, "tomada": n, "assinatura_video": meta["assinatura"], "nota": nota,
        "gerado_em": datetime.datetime.now().astimezone().isoformat(timespec="seconds")}, ensure_ascii=False))
    return slug, k


def main():
    p = argparse.ArgumentParser()
    p.add_argument("slugs", nargs="*")
    p.add_argument("--aprovados", action="store_true")
    p.add_argument("--nota", default="")
    p.add_argument("--jobs", type=int, default=3)
    args = p.parse_args()
    slugs = list(args.slugs)
    if args.aprovados:
        ap = json.loads((HERE / "aprovacoes.json").read_text())
        slugs += [s for s, d in ap["itens"].items() if d.get("status") == "aprovado"
                  and not any((WORK / "ilustracoes" / s).glob("v[0-9]*.png"))]
    with ThreadPoolExecutor(args.jobs) as ex:
        futs = [ex.submit(gerar, s, args.nota) for s in dict.fromkeys(slugs)]
        for f in futs:
            try:
                slug, k = f.result()
                print(f"{slug}: v{k}", flush=True)
            except Exception as e:  # segue com os outros
                print(f"ERRO {e}", flush=True)


if __name__ == "__main__":
    main()
