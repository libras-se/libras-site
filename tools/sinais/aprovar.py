"""App de aprovação dos sinais (revisar recorte, escolher tomada/variante, ajustar corte, aprovar).

Local:    python3 tools/sinais/aprovar.py            -> http://localhost:8790 (sem login)
Servidor: imagem Docker (tools/sinais/Dockerfile), configurada por variáveis de ambiente:
  SINAIS_WORK        pasta de trabalho (manifest.csv, revisao/, proxy/, ilustracoes/)
  SINAIS_RAW         pasta dos brutos .MOV (para refazer cortes)
  SINAIS_APROVACOES  arquivo de decisões
  SINAIS_USUARIOS    "nome:senha:admin,nome:senha" -> login por pessoa (HTTP Basic); cada decisão registra quem
  PORT / SINAIS_HOST porta e endereço (no servidor: 8790 e 0.0.0.0)
Nada vai para o site daqui: depois de aprovar, sincronize (sincronizar.py) e rode publicar.py no Mac.
"""
import argparse
import base64
import csv
import datetime
import hashlib
import hmac
import json
import os
import re
import shutil
import subprocess
import threading
import unicodedata
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

import render

HERE = Path(__file__).parent
DEFAULT_RAW = Path("/Volumes/Extreme Pro/LIBRAS.SE/TRABALHOS/VIDEOS GLOSSARIO")
STATUS = ("pendente", "aprovado", "ajustar", "regravar")
LOCK = threading.Lock()                 # protege ler-alterar-gravar do arquivo de decisões
RENDER_LOCKS = {}                       # um render por tomada de cada vez
JOBS = {}                               # slug -> subprocess da geração de ilustração (só no Mac)
UV = shutil.which("uv") or str(Path.home() / ".local/bin/uv")
env = os.environ.get

p = argparse.ArgumentParser()
p.add_argument("--raw", default=env("SINAIS_RAW", str(DEFAULT_RAW)))
p.add_argument("--work", default=env("SINAIS_WORK", ""))
p.add_argument("--porta", type=int, default=int(env("PORT", env("SINAIS_PORTA", "8790"))))
p.add_argument("--host", default=env("SINAIS_HOST", "127.0.0.1"))
p.add_argument("--aprovacoes", default=env("SINAIS_APROVACOES", str(render.APROVACOES)))
p.add_argument("--sem-navegador", action="store_true")
args = p.parse_args()
RAW = Path(args.raw)
WORK = Path(args.work) if args.work else RAW / "_processamento"
APROV = Path(args.aprovacoes)
USUARIOS = {}  # nome -> (senha, papel)
for item in filter(None, (x.strip() for x in env("SINAIS_USUARIOS", "").split(","))):
    nome, senha, *papel = item.split(":")
    USUARIOS[nome] = (senha, papel[0] if papel else "revisor")
# geração de ilustração: no Mac roda o Codex; no servidor vira pedido na fila (processado no Mac)
GERA_LOCAL = env("SINAIS_ILUSTRACAO", "local" if shutil.which("codex") else "fila") == "local"


def slugify(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def agora():
    return datetime.datetime.now().astimezone().isoformat(timespec="seconds")


def instante(iso):
    """ISO 8601 -> datetime comparável (Mac em -03:00, servidor pode estar em UTC)."""
    try:
        return datetime.datetime.fromisoformat(iso)
    except (TypeError, ValueError):
        return datetime.datetime.min.replace(tzinfo=datetime.timezone.utc)


def load_ap():
    ap = json.loads(APROV.read_text()) if APROV.exists() else {}
    ap.setdefault("_leia", "Decisões do app tools/sinais/aprovar.py. Não edite à mão com o app aberto.")
    for k in ("itens", "ajustes", "extras"):
        ap.setdefault(k, {})
    return ap


def save_ap(ap):
    APROV.parent.mkdir(parents=True, exist_ok=True)
    tmp = APROV.with_suffix(".tmp")
    tmp.write_text(json.dumps(ap, ensure_ascii=False, indent=1, sort_keys=True))
    tmp.replace(APROV)


def alterar(fn):
    """Lê, altera e grava as decisões sob trava (duas pessoas podem decidir ao mesmo tempo)."""
    with LOCK:
        ap = load_ap()
        res = fn(ap)
        save_ap(ap)
        return res


def render_take(*a, **kw):
    base = str(a[5] if len(a) > 5 else kw["base"])  # render.render_take(rawdir, arquivo, ini, fim, pico, base)
    with RENDER_LOCKS.setdefault(base, threading.Lock()):
        return render.render_take(*a, **kw)


def sidecar(slug, n):
    f = WORK / "revisao" / slug / f"t{n}.json"
    return json.loads(f.read_text()) if f.exists() else None


def estado(usuario):
    ap = load_ap()
    briefing = json.loads((HERE / "briefing.json").read_text())
    man = WORK / "manifest.csv"
    rows = list(csv.DictReader(man.open())) if man.exists() else []
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
    return {"itens": out, "arquivos": arquivos, "usuario": usuario, "ilustracao_local": GERA_LOCAL}


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
    if dec["status"] == "refazer" and versoes and instante(versoes[-1]["em"]) > instante(dec.get("pedido_em")):
        dec.update(status="pendente", versao=versoes[-1]["k"])  # o pedido já foi atendido
    if versoes:
        dec.setdefault("versao", versoes[-1]["k"])
    return {"versoes": versoes, "decisao": dec, "gerando": gerando}


def ilu_decidir(body, usuario):
    def fn(ap):
        d = ap["itens"].setdefault(body["slug"], {}).setdefault("ilustracao", {})
        for k in ("versao", "nota", "status"):
            if k in body:
                d[k] = body[k]
        d["por"] = usuario
        if d.get("status") == "aprovado":
            d["aprovado_em"] = agora()
        if d.get("status") == "refazer":
            d.update(pedido_em=agora(), pedido_por=usuario)
    alterar(fn)


def ilu_gerar(body, usuario):
    slug = body["slug"]
    if load_ap()["itens"].get(slug, {}).get("status") != "aprovado":
        raise ValueError("aprove o vídeo antes de gerar a ilustração")
    if not GERA_LOCAL:  # servidor: registra o pedido; o Mac gera na próxima sincronização
        def fila(ap):
            d = ap["itens"][slug].setdefault("ilustracao", {})
            d.update(status="refazer", nota=body.get("nota", ""), pedido_por=usuario, pedido_em=agora())
        alterar(fila)
        return {"fila": True}
    if JOBS.get(slug) and JOBS[slug].poll() is None:
        raise ValueError("já está gerando")
    (WORK / "tmp").mkdir(exist_ok=True)
    log = (WORK / "tmp" / f"ilustrar-{slug}.log").open("w")
    JOBS[slug] = subprocess.Popen([UV, "run", "--quiet", "--python", "3.12", "--with", "numpy",
                                   str(HERE / "ilustrar.py"), slug, "--nota", body.get("nota", "")],
                                  stdout=log, stderr=subprocess.STDOUT, cwd=str(HERE.parents[1]))

    def pend(ap):
        d = ap["itens"][slug].setdefault("ilustracao", {})
        d["status"] = "pendente"
        d.pop("versao", None)
    alterar(pend)
    return {"fila": False}


def decidir(body, usuario):
    slug = body["slug"]

    def fn(ap):
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
                d["aprovado"] = {"tomada": n, "assinatura": meta["assinatura"], "em": agora(), "por": usuario}
        d["atualizado_em"] = agora()
        d["por"] = usuario
    alterar(fn)


def ajustar(body, usuario):
    slug, n = body["slug"], int(body["tomada"])
    ini, fim = round(float(body["ini"]), 3), round(float(body["fim"]), 3)
    if not 0.4 <= fim - ini <= 12:
        raise ValueError("o corte precisa ter entre 0,4 e 12 segundos")
    a = {"ini": ini, "fim": fim}
    if body.get("arquivo"):
        a["arquivo"] = body["arquivo"]
    base = sidecar(slug, n)
    if not a.get("arquivo"):
        if not base:
            raise ValueError("escolha o arquivo de origem")
        a["arquivo"] = base["arquivo"]
    if not (RAW / f"{a['arquivo']}.MOV").exists():
        raise ValueError(f"o bruto {a['arquivo']}.MOV ainda não está no servidor")
    meta = render_take(RAW, a["arquivo"], ini, fim, None, WORK / "revisao" / slug / f"t{n}")  # fora da trava

    def fn(ap):
        ap["ajustes"][f"{slug}#{n}"] = {**a, "por": usuario, "em": agora()}
        d = ap["itens"].setdefault(slug, {})
        d["tomada"] = n
        if d.get("status") in ("aprovado", "ajustar"):  # corte novo precisa de nova revisão
            d["status"] = "pendente"
            d.pop("aprovado", None)
        d["atualizado_em"] = agora()
        d["por"] = usuario
    alterar(fn)
    return meta


def desfazer(body, usuario):
    slug, n = body["slug"], int(body["tomada"])
    alterar(lambda ap: ap["ajustes"].pop(f"{slug}#{n}", None))
    for c in render.candidatos(WORK, load_ap()):
        if c[0] == slug and c[1] == n:
            render_take(RAW, c[2], c[3], c[4], c[5], WORK / "revisao" / slug / f"t{n}")


def extra(body, usuario):
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
    render_take(RAW, meta["arquivo"], meta["ini"], meta["fim"], meta["pico"], WORK / "revisao" / slug / "t1")

    def fn(ap):
        ap["extras"][slug] = {"palavra": palavra, "categoria": orig["categoria"], "bloco": orig["bloco"],
                              "origem": body["origem"], "arquivo": meta["arquivo"], "ini": meta["ini"],
                              "fim": meta["fim"], "por": usuario}
        ap["itens"][slug] = {"status": "pendente", "tomada": 1, "atualizado_em": agora(), "por": usuario}
    alterar(fn)
    return slug


# ---------- sincronização com o Mac (só admin) ----------
RAIZES = {"processamento": lambda: WORK, "brutos": lambda: RAW}


def caminho_seguro(rel):
    raiz, _, resto = rel.partition("/")
    if raiz not in RAIZES or not resto:
        raise ValueError("caminho inválido")
    base = RAIZES[raiz]().resolve()
    alvo = (base / resto).resolve()
    if base not in alvo.parents:
        raise ValueError("caminho fora da pasta")
    return alvo


def listar(raiz):
    base = RAIZES[raiz]()
    out = []
    for f in sorted(base.rglob("*")) if base.exists() else []:
        if not f.is_file() or f.name.startswith(".") or f.suffix in (".parte", ".tmp"):
            continue
        st = f.stat()
        item = {"caminho": f"{raiz}/{f.relative_to(base).as_posix()}", "tamanho": st.st_size, "mtime": int(st.st_mtime)}
        if st.st_size < 4 << 20:
            item["sha1"] = hashlib.sha1(f.read_bytes()).hexdigest()
        out.append(item)
    return out


class H(BaseHTTPRequestHandler):
    usuario = ""
    papel = "admin"

    def log_message(self, *a):
        pass

    def autenticar(self):
        if not USUARIOS:
            self.usuario, self.papel = "local", "admin"
            return True
        h = self.headers.get("Authorization", "")
        if h.startswith("Basic "):
            try:
                nome, _, senha = base64.b64decode(h[6:]).decode().partition(":")
            except Exception:
                nome, senha = "", ""
            ok = nome in USUARIOS and hmac.compare_digest(senha, USUARIOS[nome][0])
            if ok:
                self.usuario, self.papel = nome, USUARIOS[nome][1]
                return True
        self.send_response(401)
        self.send_header("WWW-Authenticate", 'Basic realm="Aprovacao de sinais LIBRAS.SE", charset="UTF-8"')
        self.send_header("Content-Length", "0")
        self.end_headers()
        return False

    def send_json(self, obj, code=200):
        data = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def send_file(self, f: Path):
        if not f.is_file():
            return self.send_json({"ok": False, "erro": "não encontrado"}, 404)
        ctype = {".mp4": "video/mp4", ".webp": "image/webp", ".png": "image/png", ".jpg": "image/jpeg",
                 ".json": "application/json", ".csv": "text/csv; charset=utf-8",
                 ".html": "text/html; charset=utf-8"}.get(f.suffix.lower(), "application/octet-stream")
        size = f.stat().st_size
        start, end = 0, size - 1
        rng = self.headers.get("Range")
        if rng and size:
            m = re.match(r"bytes=(\d*)-(\d*)", rng)
            if m.group(1):
                start = int(m.group(1))
                end = min(int(m.group(2)), size - 1) if m.group(2) else end
            else:
                start = max(0, size - int(m.group(2)))
            self.send_response(206)
            self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        else:
            self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Length", str(max(0, end - start + 1)))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        if self.command == "HEAD":
            return
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

    def do_HEAD(self):
        self.do_GET()

    def do_GET(self):
        u = urlparse(self.path)
        path, q = u.path, parse_qs(u.query)
        if path == "/saude":
            return self.send_json({"ok": True})
        if not self.autenticar():
            return
        if path == "/":
            return self.send_file(HERE / "aprovar.html")
        if path == "/api/estado":
            return self.send_json(estado(self.usuario))
        m = re.match(r"^/media/rev/([a-z0-9-]+)/(t\d+\.(?:mp4|webp))$", path)
        if m:
            return self.send_file(WORK / "revisao" / m.group(1) / m.group(2))
        m = re.match(r"^/media/ilu/([a-z0-9-]+)/(v\d+(?:-referencia)?\.png)$", path)
        if m:
            return self.send_file(WORK / "ilustracoes" / m.group(1) / m.group(2))
        m = re.match(r"^/media/proxy/([^/]+\.mp4)$", path)
        if m:
            return self.send_file(WORK / "proxy" / unquote(m.group(1)))
        if path.startswith("/admin/"):
            if self.papel != "admin":
                return self.send_json({"ok": False, "erro": "só admin"}, 403)
            try:
                if path == "/admin/listar":
                    return self.send_json({"ok": True, "arquivos": listar(q["raiz"][0])})
                if path == "/admin/arquivo":
                    return self.send_file(caminho_seguro(q["caminho"][0]))
                if path == "/admin/tamanho":
                    alvo = caminho_seguro(q["caminho"][0])
                    parte = alvo.with_name(alvo.name + ".parte")
                    return self.send_json({"ok": True, "tamanho": alvo.stat().st_size if alvo.exists() else None,
                                           "parte": parte.stat().st_size if parte.exists() else 0})
                if path == "/admin/aprovacoes":
                    return self.send_json(load_ap())
                if path == "/admin/espaco":  # espaço em disco do volume de dados (antes de subir os brutos)
                    tot, usado, livre = shutil.disk_usage(WORK)
                    return self.send_json({"ok": True, "total": tot, "usado": usado, "livre": livre})
            except (ValueError, KeyError) as e:
                return self.send_json({"ok": False, "erro": str(e)}, 400)
        self.send_json({"ok": False, "erro": "não encontrado"}, 404)

    def do_PUT(self):
        """Upload retomável em partes: PUT /admin/arquivo?caminho=..&offset=N[&final=1&mtime=T]."""
        if not self.autenticar():
            return
        if self.papel != "admin":
            return self.send_json({"ok": False, "erro": "só admin"}, 403)
        u = urlparse(self.path)
        q = parse_qs(u.query)
        n = int(self.headers.get("Content-Length", 0))
        try:
            if u.path == "/admin/aprovacoes":
                novo = json.loads(self.rfile.read(n))
                with LOCK:
                    save_ap(novo)
                return self.send_json({"ok": True})
            if u.path != "/admin/arquivo":
                return self.send_json({"ok": False, "erro": "não encontrado"}, 404)
            alvo = caminho_seguro(q["caminho"][0])
            parte = alvo.with_name(alvo.name + ".parte")
            offset = int(q.get("offset", ["0"])[0])
            alvo.parent.mkdir(parents=True, exist_ok=True)
            atual = parte.stat().st_size if parte.exists() else 0
            if offset != atual:
                self.rfile.read(n)
                return self.send_json({"ok": False, "erro": "offset", "parte": atual}, 409)
            with parte.open("ab") as fh:
                left = n
                while left > 0:
                    chunk = self.rfile.read(min(1 << 20, left))
                    if not chunk:
                        break
                    fh.write(chunk)
                    left -= len(chunk)
            if q.get("final", ["0"])[0] == "1":
                parte.replace(alvo)
                if "mtime" in q:
                    t = int(q["mtime"][0])
                    os.utime(alvo, (t, t))
            return self.send_json({"ok": True, "parte": parte.stat().st_size if parte.exists() else 0})
        except (ValueError, KeyError) as e:
            return self.send_json({"ok": False, "erro": str(e)}, 400)

    def do_POST(self):
        if not self.autenticar():
            return
        body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
        acoes = {"/api/decidir": decidir, "/api/ajustar": ajustar, "/api/desfazer": desfazer, "/api/extra": extra,
                 "/api/ilu/decidir": ilu_decidir, "/api/ilu/gerar": ilu_gerar}
        fn = acoes.get(self.path)
        if not fn:
            return self.send_json({"ok": False, "erro": "não encontrado"}, 404)
        try:
            self.send_json({"ok": True, "res": fn(body, self.usuario)})
        except Exception as e:  # erro de validação ou render: mostra na interface
            self.send_json({"ok": False, "erro": str(e)}, 400)


if __name__ == "__main__":
    WORK.mkdir(parents=True, exist_ok=True)
    if not (WORK / "manifest.csv").exists():
        print(f"aviso: {WORK / 'manifest.csv'} ainda não existe (servidor vazio? rode sincronizar.py enviar)")
    srv = ThreadingHTTPServer((args.host, args.porta), H)
    url = f"http://localhost:{args.porta}/"
    print(f"Aprovação de sinais em {url}  (Ctrl+C para sair)\nDecisões: {APROV}\n"
          f"Login: {'por pessoa (' + ', '.join(USUARIOS) + ')' if USUARIOS else 'desligado (uso local)'}", flush=True)
    if not args.sem_navegador:
        webbrowser.open(url)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
