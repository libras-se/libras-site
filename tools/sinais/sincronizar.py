"""Sincroniza o Mac com o app de aprovação online (aprovacao.libras.se).

Uso (no Mac, com o SSD conectado):
  python3 tools/sinais/sincronizar.py semear [--forcar]   1ª vez: sobe as decisões locais para o servidor
  python3 tools/sinais/sincronizar.py enviar [--brutos]   sobe manifest, cortes, proxies e ilustrações (e os brutos)
  python3 tools/sinais/sincronizar.py baixar              baixa decisões e cortes refeitos online

Regras: o servidor é a fonte das DECISÕES (aprovacoes.json) depois de semeado; para os demais arquivos, vale o
mais novo (mtime) de cada lado. Uploads grandes vão em partes de 16 MB e retomam de onde pararam.
Credencial de admin: variável SINAIS_ADMIN="nome:senha" ou arquivo ~/.config/libras-sinais/admin (uma linha).
"""
import argparse
import base64
import hashlib
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent
WORK = Path(os.environ.get("SINAIS_WORK", "/Volumes/Extreme Pro/LIBRAS.SE/TRABALHOS/VIDEOS GLOSSARIO/_processamento"))
RAW = Path(os.environ.get("SINAIS_RAW", str(WORK.parent)))
URL = os.environ.get("SINAIS_URL", "https://aprovacao.libras.se").rstrip("/")
PARTE = 16 << 20
ENVIAR = ["manifest.csv", "extent.json", "revisao", "proxy", "ilustracoes"]


def credencial():
    c = os.environ.get("SINAIS_ADMIN") or (Path.home() / ".config/libras-sinais/admin").read_text().strip()
    return "Basic " + base64.b64encode(c.encode()).decode()


AUTH = None


def req(metodo, caminho, dados=None, ok=(200, 206)):
    r = urllib.request.Request(URL + caminho, data=dados, method=metodo, headers={"Authorization": AUTH})
    try:
        with urllib.request.urlopen(r, timeout=300) as resp:
            return resp.status, resp.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()


def jget(caminho):
    st, body = req("GET", caminho)
    if st != 200:
        sys.exit(f"erro {st} em {caminho}: {body[:200]!r}")
    return json.loads(body)


def q(**kw):
    return "?" + urllib.parse.urlencode(kw)


def locais(raiz, base, itens):
    out = {}
    for it in itens:
        alvo = base / it
        arquivos = [alvo] if alvo.is_file() else sorted(alvo.rglob("*")) if alvo.exists() else []
        for f in arquivos:
            if f.is_file() and not f.name.startswith(".") and f.suffix not in (".parte", ".tmp"):
                out[f"{raiz}/{f.relative_to(base).as_posix()}"] = f
    return out


def igual(f, info):
    if f.stat().st_size != info["tamanho"]:
        return False
    if "sha1" in info:
        return hashlib.sha1(f.read_bytes()).hexdigest() == info["sha1"]
    return True


def subir(rel, f):
    tam = f.stat().st_size
    feito = jget("/admin/tamanho" + q(caminho=rel))["parte"]
    if feito > tam:
        feito = 0
    with f.open("rb") as fh:
        fh.seek(feito)
        while True:
            bloco = fh.read(PARTE)
            final = feito + len(bloco) >= tam
            extra = {"final": 1, "mtime": int(f.stat().st_mtime)} if final else {}
            st, body = req("PUT", "/admin/arquivo" + q(caminho=rel, offset=feito, **extra), bloco)
            if st == 409:  # o servidor tem outro tamanho de parte: retoma dali
                feito = json.loads(body)["parte"]
                fh.seek(feito)
                continue
            if st != 200:
                sys.exit(f"erro {st} ao enviar {rel}: {body[:200]!r}")
            feito += len(bloco)
            if tam > PARTE:
                print(f"\r  {rel}: {feito / tam:6.1%}", end="", flush=True)
            if final:
                break
    if tam > PARTE:
        print()


def baixar_arquivo(rel, destino, mtime):
    st, body = req("GET", "/admin/arquivo" + q(caminho=rel))
    if st != 200:
        sys.exit(f"erro {st} ao baixar {rel}")
    destino.parent.mkdir(parents=True, exist_ok=True)
    tmp = destino.with_name(destino.name + ".tmp")
    tmp.write_bytes(body)
    tmp.replace(destino)
    os.utime(destino, (mtime, mtime))


def cmd_enviar(args):
    alvos = [("processamento", WORK, ENVIAR)]
    if args.brutos:
        alvos.append(("brutos", RAW, [f.name for f in sorted(RAW.glob("[!.]*.MOV"))]))
    for raiz, base, itens in alvos:
        remoto = {i["caminho"]: i for i in jget("/admin/listar" + q(raiz=raiz))["arquivos"]}
        loc = locais(raiz, base, itens)
        fila = [(rel, f) for rel, f in loc.items()
                if rel not in remoto or (not igual(f, remoto[rel]) and f.stat().st_mtime > remoto[rel]["mtime"])]
        print(f"{raiz}: {len(fila)} de {len(loc)} arquivos para enviar")
        for i, (rel, f) in enumerate(fila, 1):
            subir(rel, f)
            if i % 50 == 0:
                print(f"  {i}/{len(fila)}", flush=True)


def cmd_baixar(args):
    ap = jget("/admin/aprovacoes")
    (HERE / "aprovacoes.json").write_text(json.dumps(ap, ensure_ascii=False, indent=1, sort_keys=True))
    print(f"decisões baixadas: {sum(1 for d in ap['itens'].values() if d.get('status') == 'aprovado')} sinais aprovados")
    remoto = {i["caminho"]: i for i in jget("/admin/listar" + q(raiz="processamento"))["arquivos"]}
    n = 0
    for rel, info in remoto.items():
        f = WORK / rel.partition("/")[2]
        if f.exists() and (igual(f, info) or f.stat().st_mtime >= info["mtime"]):
            continue
        baixar_arquivo(rel, f, info["mtime"])
        n += 1
    print(f"arquivos baixados (cortes refeitos online etc.): {n}")


def cmd_semear(args):
    st, body = req("GET", "/admin/aprovacoes")
    remoto = json.loads(body) if st == 200 else {}
    if remoto.get("itens") and not args.forcar:
        sys.exit("o servidor já tem decisões; use --forcar para substituir (cuidado: perde o que foi decidido online)")
    dados = (HERE / "aprovacoes.json").read_bytes()
    st, body = req("PUT", "/admin/aprovacoes", dados)
    print("decisões enviadas" if st == 200 else f"erro {st}: {body[:200]!r}")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    e = sub.add_parser("enviar")
    e.add_argument("--brutos", action="store_true")
    sub.add_parser("baixar")
    s = sub.add_parser("semear")
    s.add_argument("--forcar", action="store_true")
    a = p.parse_args()
    AUTH = credencial()
    {"enviar": cmd_enviar, "baixar": cmd_baixar, "semear": cmd_semear}[a.cmd](a)
