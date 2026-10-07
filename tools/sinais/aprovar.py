"""App local de aprovação dos sinais (revisar recorte, escolher tomada/variante, ajustar corte, aprovar).

Uso: python3 tools/sinais/aprovar.py [--work <WORKDIR>] [--raw <RAWDIR>] [--porta 8790]
Abre http://localhost:8790. Decisões ficam em tools/sinais/aprovacoes.json (versionado).
Nada vai para o site daqui: depois de aprovar, rode tools/sinais/publicar.py.
"""
import argparse
import csv
import datetime
import json
import re
import shutil
import subprocess
import sys
import threading
import unicodedata
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import render

HERE = Path(__file__).parent
DEFAULT_RAW = Path("/Volumes/Extreme Pro/LIBRAS.SE/TRABALHOS/VIDEOS GLOSSARIO")
STATUS = ("pendente", "aprovado", "ajustar", "regravar")
LOCK = threading.Lock()
JOBS = {}  # slug -> subprocess da geração de ilustração em andamento
UV = shutil.which("uv") or str(Path.home() / ".local/bin/uv")

p = argparse.ArgumentParser()
p.add_argument("--raw", default=str(DEFAULT_RAW))
p.add_argument("--work", default="")
p.add_argument("--porta", type=int, default=8790)
p.add_argument("--aprovacoes", default=str(render.APROVACOES), help="arquivo de decisões (para testes)")
p.add_argument("--sem-navegador", action="store_true")
args = p.parse_args()
RAW = Path(args.raw)
WORK = Path(args.work) if args.work else RAW / "_processamento"
APROV = Path(args.aprovacoes)


def slugify(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def agora():
    return datetime.datetime.now().astimezone().isoformat(timespec="seconds")


def load_ap():
    if APROV.exists():
        ap = json.loads(APROV.read_text())
    else:
        ap = {}
    ap.setdefault("_leia", "Decisões do app tools/sinais/aprovar.py. Não edite à mão com o app aberto.")
    for k in ("itens", "ajustes", "extras"):
        ap.setdefault(k, {})
    return ap


def save_ap(ap):
    tmp = APROV.with_suffix(".tmp")
    tmp.write_text(json.dumps(ap, ensure_ascii=False, indent=1, sort_keys=True))
    tmp.replace(APROV)


def sidecar(slug, n):
    f = WORK / "revisao" / slug / f"t{n}.json"
    return json.loads(f.read_text()) if f.exists() else None


def estado():
    ap = load_ap()
    briefing = json.loads((HERE / "briefing.json").read_text())
    rows = list(csv.DictReader((WORK / "manifest.csv").open()))
    extent = json.loads((WORK / "extent.json").read_text()) if (WORK / "extent.json").exists() else {}
    by = {}
    for r in rows:
        if r["arquivo"]:
            by.setdefault(r["slug"], []).append(r)
    itens = [dict(it) for it in briefing]
    for slug, ex in ap["extras"].items():
        itens.append({"slug": slug, "palavra": ex["palavra"], "categoria": ex["categoria"], "bloco": ex["bloco"],
                      "extra": ex["origem"]})
    out = []
    for i, it in enumerate(itens):
        slug = it["slug"]
        takes = []
        src = by.get(slug, [])
        if it.get("extra"):
            src = [{"tomada": "1", "arquivo": "", "ini": "", "fim": "", "ouvido": f"criado de {it['extra']}",
                    "flags": "extra", "fala_t": "", "oficial": "1"}]
        for r in src:
            n = int(r["tomada"])
            meta = sidecar(slug, n)
            alerts = [f for f in r["flags"].split() if f]
            bb = extent.get(f"{slug}#{n}")
            if bb and bb[1] <= 8:
                alerts.append("borda_topo")
            if bb and (bb[0] <= 8 or bb[2] >= 1912):
                alerts.append("chroma_suspeito")
            takes.append({"n": n, "ouvido": r["ouvido"], "fala_t": r["fala_t"], "alertas": alerts,
                          "ajustado": f"{slug}#{n}" in ap["ajustes"], "meta": meta,
                          "auto": r["oficial"] == "1"})
        for key, a in ap["ajustes"].items():  # cortes manuais de itens não encontrados
            s, n = key.split("#")
            if s == slug and not any(t["n"] == int(n) for t in takes):
                takes.append({"n": int(n), "ouvido": "corte manual", "fala_t": "", "alertas": ["manual"],
                              "ajustado": True, "meta": sidecar(slug, int(n)), "auto": True})
        d = dict(ap["itens"].get(slug, {}))
        auto = next((t["n"] for t in takes if t["auto"]), takes[-1]["n"] if takes else None)
        d.setdefault("status", "pendente")
        d.setdefault("tomada", auto)
        if d["status"] == "aprovado":
            m = sidecar(slug, d.get("aprovado", {}).get("tomada"))
            if not m or m["assinatura"] != d.get("aprovado", {}).get("assinatura"):
                d["desatualizado"] = True
        out.append({**{k: it[k] for k in ("slug", "palavra", "categoria", "bloco")}, "ordem": i, "takes": takes,
                    "variantes": sum(1 for t in takes if "variante" in t["alertas"]), "decisao": d,
                    "ilustracao": ilustracao(slug, d, ap["itens"].get(slug, {}).get("ilustracao", {}))})
    # dicas de tempo para itens sem tomada: vizinhos no mesmo arquivo
    for i, o in enumerate(out):
        if o["takes"]:
            continue
        prev = next((x for x in reversed(out[:i]) if x["takes"] and x["takes"][-1]["meta"]), None)
        nxt = next((x for x in out[i + 1:] if x["takes"] and x["takes"][0]["meta"]), None)
        o["dica"] = {"antes": prev and {"palavra": prev["palavra"], **prev["takes"][-1]["meta"]},
                     "depois": nxt and {"palavra": nxt["palavra"], **nxt["takes"][0]["meta"]}}
    arquivos = sorted(p.stem for p in (WORK / "proxy").glob("[!.]*.mp4"))
    return {"itens": out, "arquivos": arquivos}


def ilustracao(slug, d, dec):
    pasta = WORK / "ilustracoes" / slug
    vid = d.get("aprovado", {}).get("assinatura")
    versoes = []
    for f in sorted(pasta.glob("v*.json"), key=lambda f: int(f.stem[1:]) if f.stem[1:].isdigit() else 0):
        if not f.stem[1:].isdigit():
            continue
        m = json.loads(f.read_text())
        versoes.append({"k": m["versao"], "nota": m.get("nota", ""), "em": m.get("gerado_em", ""),
                        "desatualizada": bool(vid) and m["assinatura_video"] != vid, "v": int(f.stat().st_mtime)})
    job = JOBS.get(slug)
    gerando = bool(job and job.poll() is None)
    dec = dict(dec)
    dec.setdefault("status", "pendente")
    if versoes:
        dec.setdefault("versao", versoes[-1]["k"])
    return {"versoes": versoes, "decisao": dec, "gerando": gerando}


def ilu_decidir(body):
    slug, ap = body["slug"], load_ap()
    d = ap["itens"].setdefault(slug, {}).setdefault("ilustracao", {})
    for k in ("versao", "nota", "status"):
        if k in body:
            d[k] = body[k]
    if d.get("status") == "aprovado":
        d["aprovado_em"] = agora()
    save_ap(ap)


def ilu_gerar(body):
    slug = body["slug"]
    if slug not in load_ap()["itens"] or load_ap()["itens"][slug].get("status") != "aprovado":
        raise ValueError("aprove o vídeo antes de gerar a ilustração")
    if JOBS.get(slug) and JOBS[slug].poll() is None:
        raise ValueError("já está gerando")
    log = (WORK / "tmp" / f"ilustrar-{slug}.log").open("w")
    JOBS[slug] = subprocess.Popen([UV, "run", "--quiet", "--python", "3.12", "--with", "numpy",
                                   str(HERE / "ilustrar.py"), slug, "--nota", body.get("nota", "")],
                                  stdout=log, stderr=subprocess.STDOUT, cwd=str(HERE.parents[1]))
    ap = load_ap()
    d = ap["itens"][slug].setdefault("ilustracao", {})
    d["status"] = "pendente"
    d.pop("versao", None)
    save_ap(ap)


def decidir(body):
    slug, ap = body["slug"], load_ap()
    d = ap["itens"].setdefault(slug, {})
    for k in ("tomada", "nota"):
        if k in body:
            d[k] = body[k]
    if "status" in body:
        st = body["status"]
        assert st in STATUS, st
        d["status"] = st
        d.pop("aprovado", None)
        if st == "aprovado":
            n = d.get("tomada") or body.get("tomada")
            meta = sidecar(slug, n)
            if not meta:
                raise ValueError("essa tomada ainda não foi renderizada")
            d["tomada"] = n
            d["aprovado"] = {"tomada": n, "assinatura": meta["assinatura"], "em": agora()}
    d["atualizado_em"] = agora()
    save_ap(ap)


def ajustar(body):
    slug, n = body["slug"], int(body["tomada"])
    ini, fim = round(float(body["ini"]), 3), round(float(body["fim"]), 3)
    if not 0.4 <= fim - ini <= 12:
        raise ValueError("o corte precisa ter entre 0,4 e 12 segundos")
    ap = load_ap()
    a = {"ini": ini, "fim": fim}
    if body.get("arquivo"):
        a["arquivo"] = body["arquivo"]
    base = sidecar(slug, n)
    if not a.get("arquivo"):
        if not base:
            raise ValueError("escolha o arquivo de origem")
        a["arquivo"] = base["arquivo"]
    meta = render.render_take(RAW, a["arquivo"], ini, fim, None, WORK / "revisao" / slug / f"t{n}")
    ap["ajustes"][f"{slug}#{n}"] = a
    d = ap["itens"].setdefault(slug, {})
    d["tomada"] = n
    # corte novo precisa de nova revisão
    if d.get("status") in ("aprovado", "ajustar"):
        d["status"] = "pendente"
        d.pop("aprovado", None)
    d["atualizado_em"] = agora()
    save_ap(ap)
    return meta


def desfazer(body):
    slug, n = body["slug"], int(body["tomada"])
    ap = load_ap()
    ap["ajustes"].pop(f"{slug}#{n}", None)
    save_ap(ap)
    for c in render.candidatos(WORK, ap):
        if c[0] == slug and c[1] == n:
            render.render_take(RAW, c[2], c[3], c[4], c[5], WORK / "revisao" / slug / f"t{n}")


def extra(body):
    origem_slug, n = body["origem"].split("#")
    palavra = body["palavra"].strip()
    slug = slugify(palavra)
    if not slug:
        raise ValueError("nome inválido")
    briefing = {it["slug"]: it for it in json.loads((HERE / "briefing.json").read_text())}
    ap = load_ap()
    if slug in briefing or slug in ap["extras"]:
        raise ValueError(f"já existe um sinal com o slug {slug}")
    meta = sidecar(origem_slug, int(n))
    orig = briefing.get(origem_slug) or ap["extras"].get(origem_slug)
    ap["extras"][slug] = {"palavra": palavra, "categoria": orig["categoria"], "bloco": orig["bloco"],
                          "origem": body["origem"], "arquivo": meta["arquivo"], "ini": meta["ini"], "fim": meta["fim"]}
    render.render_take(RAW, meta["arquivo"], meta["ini"], meta["fim"], meta["pico"], WORK / "revisao" / slug / "t1")
    ap["itens"][slug] = {"status": "pendente", "tomada": 1, "atualizado_em": agora()}
    save_ap(ap)
    return slug


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def send_json(self, obj, code=200):
        data = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def send_file(self, f: Path):
        if not f.is_file():
            self.send_error(404)
            return
        ctype = {".mp4": "video/mp4", ".webp": "image/webp", ".png": "image/png", ".html": "text/html; charset=utf-8"}.get(f.suffix, "application/octet-stream")
        size = f.stat().st_size
        start, end = 0, size - 1
        rng = self.headers.get("Range")
        if rng:
            m = re.match(r"bytes=(\d*)-(\d*)", rng)
            if m.group(1):
                start = int(m.group(1))
                end = int(m.group(2)) if m.group(2) else end
            else:
                start = size - int(m.group(2))
            self.send_response(206)
            self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        else:
            self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Length", str(end - start + 1))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        with f.open("rb") as fh:
            fh.seek(start)
            left = end - start + 1
            while left > 0:
                chunk = fh.read(min(1 << 20, left))
                if not chunk:
                    break
                try:
                    self.wfile.write(chunk)
                except (BrokenPipeError, ConnectionResetError):
                    return
                left -= len(chunk)

    def do_GET(self):
        path = self.path.split("?")[0]
        if path == "/":
            return self.send_file(HERE / "aprovar.html")
        if path == "/api/estado":
            with LOCK:
                return self.send_json(estado())
        m = re.match(r"^/media/rev/([a-z0-9-]+)/(t\d+\.(?:mp4|webp))$", path)
        if m:
            return self.send_file(WORK / "revisao" / m.group(1) / m.group(2))
        m = re.match(r"^/media/ilu/([a-z0-9-]+)/(v\d+(?:-referencia)?\.png)$", path)
        if m:
            return self.send_file(WORK / "ilustracoes" / m.group(1) / m.group(2))
        m = re.match(r"^/media/proxy/([^/]+\.mp4)$", path)
        if m:
            from urllib.parse import unquote
            return self.send_file(WORK / "proxy" / unquote(m.group(1)))
        self.send_error(404)

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
        acoes = {"/api/decidir": decidir, "/api/ajustar": ajustar, "/api/desfazer": desfazer, "/api/extra": extra,
                 "/api/ilu/decidir": ilu_decidir, "/api/ilu/gerar": ilu_gerar}
        fn = acoes.get(self.path)
        if not fn:
            return self.send_error(404)
        try:
            with LOCK:
                res = fn(body)
            self.send_json({"ok": True, "res": res})
        except Exception as e:  # erro de validação ou render: mostra na interface
            self.send_json({"ok": False, "erro": str(e)}, 400)


if __name__ == "__main__":
    for need in (WORK / "manifest.csv", RAW):
        if not need.exists():
            raise SystemExit(f"não encontrado: {need} (o SSD está conectado?)")
    srv = ThreadingHTTPServer(("127.0.0.1", args.porta), H)
    url = f"http://localhost:{args.porta}/"
    print(f"Aprovação de sinais em {url}  (Ctrl+C para sair)\nDecisões: {APROV}")
    if not args.sem_navegador:
        webbrowser.open(url)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
