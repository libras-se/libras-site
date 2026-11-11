"""Elementos divertidos das páginas de sinal: a arte do cabeçalho e a ficha de cada categoria.

Usado pelo build_pages.py. Os dados ficam em elementos.json e os contornos das letras em letras.json (letras.py).
- Times de futebol: camisa tradicional desenhada em SVG, apelido, mascote, cores, estádio e quem torce.
- Estados: o estado destacado no mapa do Brasil, sigla, capital, região, gentílico e quatro símbolos do lugar.
- Alfabeto: a letra de oito jeitos (de forma, cursiva, pontilhada para traçar, com serifa, em pixels, de bolhas)
  e as palavras do vocabulário que começam com ela.
- Cores: a mancha de tinta da cor.
Quando o sinal tem figurinha (figurinhas.py), ela ocupa o cabeçalho; sem figurinha, entra o desenho da ficha.
"""
import html
import json
import re
import unicodedata
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parents[1]
EL = json.loads((HERE / "elementos.json").read_text())
LETRAS = json.loads((HERE / "letras.json").read_text())
FIG_DIR = "/assets/img/sinais/figurinhas"
esc = html.escape
TRACO = "#0e3538"
_MAPA = re.findall(r' d="([^"]+)"', (ROOT / "assets/img/home/brazil-map.svg").read_text())
assert len(_MAPA) == 27, "o mapa do Brasil deve ter um <path> por unidade federativa, na ordem do IBGE"


def fold(s):
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()


def lista_pt(itens):
    return ", ".join(itens[:-1]) + " e " + itens[-1] if len(itens) > 1 else itens[0]


# ---------- times: camisa ----------
CORPO = ("M78 18 44 30 12 66 40 92 58 76V200Q58 206 64 206H176Q182 206 182 200V76L200 92 228 66 196 30 162 18"
         "Q150 40 120 40 90 40 78 18Z")


def _listras(listras, vertical):
    u, total = 6.8, sum(w for _, w in listras)
    pos = 120 - listras[0][1] * u / 2 if vertical else 60  # vertical: a primeira cor passa no meio do peito
    while pos > 0:
        pos -= total * u
    out = ""
    while pos < 240:
        for cor, w in listras:
            a, b = round(pos, 1), round(w * u + 0.4, 1)
            out += f'<rect x="{a}" y="0" width="{b}" height="220" fill="{cor}"/>' if vertical else \
                   f'<rect x="0" y="{a}" width="240" height="{b}" fill="{cor}"/>'
            pos += w * u
    return out


def camisa(c, uid):
    t = c["tipo"]
    base = c.get("base", "#ffffff")
    miolo = f'<rect width="240" height="220" fill="{base}"/>'
    if t in ("listras-v", "listras-h"):
        miolo = _listras(c["listras"], t == "listras-v")
    elif t == "faixa-diagonal":
        miolo += f'<path d="M188 24 50 204" stroke="{c["faixa"]}" stroke-width="34"/>'
    elif t == "faixas-peito":
        miolo += "".join(f'<rect x="0" y="{84 + i * 13}" width="240" height="13.4" fill="{cor}"/>' for i, cor in enumerate(c["faixas"]))
    gola, punho = c.get("gola", TRACO), c.get("punho", c.get("gola", TRACO))
    return (f'<svg viewBox="0 0 240 220" class="camisa" role="img" aria-label="Desenho da camisa tradicional do time">'
            f'<defs><clipPath id="cm{uid}"><path d="{CORPO}"/></clipPath></defs>'
            f'<g clip-path="url(#cm{uid})">{miolo}'
            f'<path d="M12 66 40 92M228 66 200 92" stroke="{punho}" stroke-width="15" fill="none"/>'
            f'<path d="M150 0H240V220H150Z" fill="{TRACO}" opacity=".07"/></g>'
            f'<path d="M78 18Q90 40 120 40 150 40 162 18" stroke="{gola}" stroke-width="9" fill="none" stroke-linecap="round"/>'
            f'<path d="{CORPO}" fill="none" stroke="{TRACO}" stroke-width="4" stroke-linejoin="round"/>'
            f'<path d="M71 16Q86 47 120 47 154 47 169 16" stroke="{TRACO}" stroke-width="3" fill="none" stroke-linecap="round"/></svg>')


def cores_camisa(c):
    cores = [x for x, _ in c.get("listras", [])] + [c.get("base")] + c.get("faixas", []) + [c.get("faixa"), c.get("gola"), c.get("punho")]
    return list(dict.fromkeys(x for x in cores if x))


# ---------- estados: mapa ----------
def mapa(idx, uid):
    pts = [(float(a), float(b)) for a, b in re.findall(r"(-?[\d.]+),(-?[\d.]+)", _MAPA[idx])]
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    raio = max(30, max(max(xs) - min(xs), max(ys) - min(ys)) * 0.62)
    return (f'<div class="mapa"><img src="/assets/img/home/brazil-map.svg" alt="" width="500" height="560" loading="lazy" decoding="async">'
            f'<svg viewBox="0 0 500 560" preserveAspectRatio="none" aria-hidden="true" focusable="false">'
            f'<path class="mapa-uf" d="{_MAPA[idx]}"/>'
            f'<circle class="mapa-anel" cx="{cx:.0f}" cy="{cy:.0f}" r="{raio:.0f}"/></svg></div>')


# ---------- alfabeto: a letra de vários jeitos ----------
JEITOS = [("forma-mai", "De forma, maiúscula", "j1"), ("forma-min", "De forma, minúscula", "j2"),
          ("cursiva-mai", "Cursiva, maiúscula", "j3"), ("cursiva-min", "Cursiva, minúscula", "j3"),
          ("forma-mai", "Pontilhada, para traçar", "j4"), ("serifa", "Com serifa", "j5"),
          ("pixel", "Em pixels", "j6"), ("divertida", "De bolhas", "j7")]


def glifo(estilo, L, cls=""):
    g = LETRAS[estilo][L]
    return f'<svg viewBox="{g["vb"]}" class="{cls}" aria-hidden="true" focusable="false"><path d="{g["d"]}"/></svg>'


# ---------- arte do cabeçalho ----------
def arte(s):
    """HTML da arte do cabeçalho (decorativa) ou '' quando o sinal ainda não tem elemento."""
    slug = s["slug"]
    if (ROOT / FIG_DIR.lstrip("/") / f"{slug}.webp").exists():
        return f'<div class="entry-art figu" aria-hidden="true"><img src="{FIG_DIR}/{slug}.webp" alt="" width="600" height="600" decoding="async"></div>'
    if slug in EL["times"]:
        return f'<div class="entry-art figu" aria-hidden="true">{camisa(EL["times"][slug]["camisa"], "h")}</div>'
    if slug in EL["estados"]:
        return f'<div class="entry-art art-mapa" aria-hidden="true">{mapa(EL["estados"][slug]["mapa"], "h")}</div>'
    if slug in EL["letras"]:
        return f'<div class="entry-art figu art-letra" aria-hidden="true">{glifo("divertida", s["palavra"][-1])}</div>'
    if slug in EL["cores"]:
        return (f'<div class="entry-art figu" aria-hidden="true"><svg viewBox="0 0 200 200" class="tinta">'
                f'<path fill="{EL["cores"][slug]}" stroke="#fff" stroke-width="7" stroke-linejoin="round" d="M98 14c30-8 62 8 74 36 9 21 22 33 18 60-5 34-34 44-48 62-13 17-45 20-64 6-17-13-45-14-56-40-12-28 2-48 6-68 6-30 38-48 70-56Z"/>'
                f'<circle cx="160" cy="176" r="12" fill="{EL["cores"][slug]}" stroke="#fff" stroke-width="5"/>'
                f'<path d="M66 62c12-14 30-20 46-18" stroke="#fff" stroke-width="9" stroke-linecap="round" fill="none" opacity=".45"/></svg></div>')
    return ""


def alt_figurinha(slug):
    """Descrição da figurinha, para o texto alternativo do cartão (ilustração + figurinha)."""
    if slug in EL["letras"]:
        return f"a letra desenhada com {lista_pt([pt for pt, _ in EL['letras'][slug]['com']])}"
    return EL["figurinhas"].get(slug, {}).get("alt", "")


# ---------- fichas ----------
def _dl(pares):
    return '<dl class="ficha-dados">' + "".join(f"<div><dt>{esc(k)}</dt><dd>{v}</dd></div>" for k, v in pares if v) + "</dl>"


def ficha(s, sinais):
    """Seção própria da categoria (HTML completo, com <section>) ou ''."""
    slug, por_slug = s["slug"], {x["slug"]: x for x in sinais}
    if slug in EL["times"]:
        t = EL["times"][slug]
        bolinhas = "".join(f'<i style="background:{c}"></i>' for c in cores_camisa(t["camisa"]))
        uf = por_slug.get(t.get("uf", ""))
        pares = [("Apelido", esc(t["apelido"])), ("Mascote", esc(t["mascote"])),
                 ("Cores", f'<span class="cores">{bolinhas}</span>{esc(t["cores"])}'),
                 ("Estádio", esc(t["estadio"])), ("Quem torce é", esc(t["torcedor"])),
                 ("Estado em Libras", f'<a href="/sinal/{uf["slug"]}/">Sinal de {esc(uf["palavra"])}</a>' if uf else "")]
        return f'''  <section aria-labelledby="ficha-h">
    <h2 class="sec-label" id="ficha-h">Ficha do time</h2>
    <div class="ficha">
      <figure class="ficha-art">{camisa(t["camisa"], "f")}<figcaption>Camisa tradicional</figcaption></figure>
      {_dl(pares)}
    </div>
    <p class="ficha-nota">Desenhos feitos pela LIBRAS.SE para ajudar a lembrar do sinal, sem vínculo com o clube.</p>
  </section>

'''
    if slug in EL["estados"]:
        e = EL["estados"][slug]
        times = [x for x in sinais if EL["times"].get(x["slug"], {}).get("uf") == slug]
        pares = [("Sigla", e["uf"]), ("Capital", esc(s.get("dados", {}).get("Capital", ""))),
                 ("Região", esc(s.get("dados", {}).get("Região", ""))), ("Quem nasce lá é", esc(e["gentilico"])),
                 ("Times em Libras", ", ".join(f'<a href="/sinal/{x["slug"]}/">{esc(x["palavra"])}</a>' for x in times))]
        simbolos = "".join(f'\n      <li><strong>{esc(n)}</strong><span>{esc(t)}</span></li>' for n, t in e["simbolos"])
        return f'''  <section aria-labelledby="ficha-h">
    <h2 class="sec-label" id="ficha-h">{"Conheça o Distrito Federal" if slug == "distrito-federal" else "Conheça o estado"}</h2>
    <div class="ficha">
      <figure class="ficha-art">{mapa(e["mapa"], "f")}<figcaption>Onde fica no mapa do Brasil</figcaption></figure>
      {_dl(pares)}
    </div>
    <ul class="simbolos">{simbolos}
    </ul>
  </section>

'''
    if slug in EL["letras"]:
        L, d = s["palavra"][-1], EL["letras"][slug]
        tiles = "".join(f'\n      <li class="jeito {cls}">{glifo(est, L)}<span>{esc(rot)}</span></li>' for est, rot, cls in JEITOS)
        nome = {fold(x["palavra"]): x for x in sinais}
        com = lista_pt([f'<a href="/sinal/{nome[fold(pt)]["slug"]}/">{esc(pt)}</a>' if fold(pt) in nome else esc(pt) for pt, _ in d["com"]])
        palavras = [x for x in sinais if x["video"] and x["categoria"] != "Alfabeto" and fold(x["palavra"])[0] == L.lower()][:8]
        vocab = ""
        if palavras:
            cards = "\n".join(
                f'      <a href="/sinal/{x["slug"]}/" class="rel-card"><img src="/assets/img/sinais/{x["slug"]}.webp" alt="" width="960" '
                f'height="720" loading="lazy" decoding="async"><span>{esc(x["palavra"])}</span></a>' if x["ilustracao"] else
                f'      <a href="/sinal/{x["slug"]}/" class="rel-card"><img src="/assets/videos/sinais/{x["slug"]}.webp" alt="" width="1280" '
                f'height="720" loading="lazy" decoding="async"><span>{esc(x["palavra"])}</span></a>' for x in palavras)
            vocab = f'''
    <h3 class="ficha-sub">Sinais que começam com {L}</h3>
    <nav class="rel-grid" aria-label="Sinais que começam com a letra {L}">
{cards}
    </nav>'''
        return f'''  <section aria-labelledby="ficha-h">
    <h2 class="sec-label" id="ficha-h">A letra {L} de vários jeitos</h2>
    <ul class="jeitos" aria-label="A letra {L} escrita de oito jeitos">{tiles}
    </ul>
    <p class="letra-com"><strong>{L}</strong> de {com}.</p>{vocab}
  </section>

'''
    return ""
