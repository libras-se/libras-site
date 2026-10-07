"""Publica no site SOMENTE os sinais aprovados no app de aprovação.

Uso: python3 tools/sinais/publicar.py [--work <WORKDIR>] [--simular]

1. Para cada sinal com status "aprovado", confere se o corte renderizado ainda tem a assinatura aprovada
   (se alguém ajustou depois, o sinal fica de fora até ser aprovado de novo).
2. Copia <WORKDIR>/revisao/<slug>/t<n>.mp4|.webp para assets/videos/sinais/<slug>.mp4|.webp.
3. Remove de assets/videos/sinais o que não está mais aprovado (a pasta é só do pipeline).
4. Ilustrações (assets/img/sinais/<slug>.webp): só a versão aprovada no app, e só se foi gerada a partir do
   corte de vídeo aprovado. Com --preview-ilustracoes, usa a última versão gerada mesmo sem aprovação
   (para avaliar no site local; não commitar nesse estado).
5. Atualiza o campo `video` dos desafios em jogo/index.html (só sinais publicados).
6. Regenera /sinal/ e sitemap.xml (build_pages.py).
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
import unicodedata
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parents[1]
DEST = ROOT / "assets" / "videos" / "sinais"
DEST_ILU = ROOT / "assets" / "img" / "sinais"
JOGO = ROOT / "jogo" / "index.html"

p = argparse.ArgumentParser()
p.add_argument("--work", default="/Volumes/Extreme Pro/LIBRAS.SE/TRABALHOS/VIDEOS GLOSSARIO/_processamento")
p.add_argument("--simular", action="store_true", help="só mostra o que mudaria")
p.add_argument("--aprovacoes", default=str(HERE / "aprovacoes.json"))
p.add_argument("--preview-ilustracoes", action="store_true")
args = p.parse_args()
work = Path(args.work)
APROV = Path(args.aprovacoes)
ap = json.loads(APROV.read_text()) if APROV.exists() else {"itens": {}}


def fold(s):
    return re.sub(r"[^a-z0-9]+", "-", unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()).strip("-")


publicar, barrados = {}, []
for slug, d in sorted(ap["itens"].items()):
    if d.get("status") != "aprovado":
        continue
    a = d.get("aprovado", {})
    base = work / "revisao" / slug / f"t{a.get('tomada')}"
    side = base.with_suffix(".json")
    meta = json.loads(side.read_text()) if side.exists() else None
    if not meta or meta["assinatura"] != a.get("assinatura"):
        barrados.append(slug)
        continue
    publicar[slug] = base

mudou = []
DEST.mkdir(parents=True, exist_ok=True)
for slug, base in publicar.items():
    for ext in ("mp4", "webp"):
        src, dst = base.with_suffix("." + ext), DEST / f"{slug}.{ext}"
        if not dst.exists() or dst.read_bytes() != src.read_bytes():
            mudou.append(f"+ {dst.relative_to(ROOT)}")
            if not args.simular:
                shutil.copyfile(src, dst)
for f in sorted(DEST.glob("*")):
    if f.stem not in publicar and f.suffix in (".mp4", ".webp"):
        mudou.append(f"- {f.relative_to(ROOT)} (não aprovado)")
        if not args.simular:
            f.unlink()

# ilustrações
ilus, ilu_barradas = {}, []
for slug, base in publicar.items():
    pasta = work / "ilustracoes" / slug
    versoes = sorted((int(f.stem[1:]) for f in pasta.glob("v*.json") if f.stem[1:].isdigit()), reverse=True)
    if not versoes:
        continue
    d = ap["itens"][slug].get("ilustracao", {})
    if d.get("status") == "aprovado":
        k = d["versao"]
    elif args.preview_ilustracoes:
        k = versoes[0]
    else:
        continue
    meta = json.loads((pasta / f"v{k}.json").read_text())
    if meta["assinatura_video"] != ap["itens"][slug]["aprovado"]["assinatura"]:
        ilu_barradas.append(slug)
        continue
    ilus[slug] = pasta / f"v{k}.png"
DEST_ILU.mkdir(parents=True, exist_ok=True)
for slug, png in ilus.items():
    dst = DEST_ILU / f"{slug}.webp"
    stamp = dst.with_suffix(".origem")
    origem = f"{png}:{png.stat().st_mtime_ns}"
    if not dst.exists() or not stamp.exists() or stamp.read_text() != origem:
        mudou.append(f"+ {dst.relative_to(ROOT)}")
        if not args.simular:
            subprocess.run(["cwebp", "-quiet", "-q", "80", "-m", "6", "-resize", "960", "720", str(png), "-o", str(dst)],
                           check=True)
            stamp.write_text(origem)
for f in sorted(DEST_ILU.glob("*.webp")):
    if f.stem not in ilus:
        mudou.append(f"- {f.relative_to(ROOT)} (ilustração não aprovada)")
        if not args.simular:
            f.unlink()
            f.with_suffix(".origem").unlink(missing_ok=True)

# jogo: só referencia vídeo de sinal publicado
texto = JOGO.read_text()
novo = texto
for m in re.finditer(r"    word: '([A-Z]+)',\n(    video: '[^']*',\n)?", texto):
    slug = fold(m.group(1))
    linha = f"    video: '{slug}',\n" if slug in publicar else ""
    novo = novo.replace(m.group(0), f"    word: '{m.group(1)}',\n{linha}", 1)
if novo != texto:
    mudou.append("~ jogo/index.html (vídeos dos desafios)")
    if not args.simular:
        JOGO.write_text(novo)

print(f"Aprovados e publicáveis: {len(publicar)}")
if barrados:
    print(f"Barrados (corte mudou depois da aprovação, aprove de novo): {', '.join(barrados)}")
print(f"Ilustrações publicáveis: {len(ilus)}" + (" (prévia: inclui não aprovadas)" if args.preview_ilustracoes else ""))
if ilu_barradas:
    print(f"Ilustrações desatualizadas (o corte do vídeo mudou, gere de novo): {', '.join(ilu_barradas)}")
print("\n".join(mudou) if mudou else "Nada mudou nos vídeos.")
if args.simular:
    sys.exit(0)
subprocess.run([sys.executable, str(HERE / "build_pages.py")], check=True, cwd=ROOT)
