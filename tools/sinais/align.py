"""Alinha fala (Whisper) + movimento com a lista ordenada do briefing e gera o manifest.csv.

Uso: uv run --python 3.12 --with numpy tools/sinais/align.py <WORKDIR>

Ideia: a intérprete fala a palavra (~1-2s) e em seguida sinaliza, sempre na ordem do briefing.
1. Segmentos de sinal = trechos fora do repouso (curva de motion/*.npz), divididos nos vales.
2. Menções = n-gramas da transcrição que casam com um item do briefing ("ou X" = variante).
3. DP monotônica menções -> itens (permite repetir item = nova tomada, e pular menções lixo).
4. DP monotônica menções -> segmentos (o sinal começa entre -1s e +5s depois da fala).
5. Segmentos sem fala entre dois itens com lacuna recebem os itens faltantes (flag "inferido").
6. Por item, a tomada oficial é a ÚLTIMA (decisão do projeto); as demais ficam como alternativas.
Correções manuais: <WORKDIR>/overrides.csv (arquivo,ini,fim,slug) substitui a detecção para aquele slug.
"""
import csv
import difflib
import json
import re
import sys
import unicodedata
from pathlib import Path

import numpy as np

FPS = 30000 / 1001
HERE = Path(__file__).parent
work = Path(sys.argv[1])

FILES = {
    "1-003": ["jogo", "desafios"],
    "2-002": ["desafios", "saudacoes", "alfabeto"],
    "3": ["alfabeto", "numeros"],
    "estados": ["estados"],
    "presidentes + times": ["presidentes", "times"],
}
EXACT_BLOCKS = {"alfabeto", "numeros"}
ALIASES = {
    "ola": ["oi"], "eu-te-amo": ["te amo"], "ele-ela": ["ele", "ela"], "jk": ["juscelino", "juscelino kubitschek"],
    "fernando-henrique-cardoso": ["fhc", "fernando henrique"], "internacional": ["inter"],
    "sao-paulo-futebol-clube": ["sao paulo fc", "sao paulo"], "athletico-paranaense": ["athletico", "atletico paranaense"],
    "esporte-clube-bahia": ["bahia"], "ceara-sporting-club": ["ceara"], "sport-recife": ["sport"],
    "lula": ["lula"], "dilma-rousseff": ["dilma"], "getulio-vargas": ["getulio"], "jair-bolsonaro": ["bolsonaro"],
    "michel-temer": ["temer"], "joao-goulart": ["jango"], "jose-sarney": ["sarney"], "itamar-franco": ["itamar"],
    "deodoro-da-fonseca": ["deodoro"], "fernando-collor": ["collor"], "atletico-mineiro": ["atletico", "galo"],
}
NUM_WORDS = "zero um dois tres quatro cinco seis sete oito nove dez onze doze treze quatorze quinze dezesseis dezessete dezoito dezenove vinte".split()
VARIANT_MARK = {"ou", "o", "ô", "oh", "e"}


def norm(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9 ]+", " ", s).split()


# ---------- 1. segmentos de sinal ----------
def find_segments(name):
    npz = np.load(work / "motion" / f"{name}.npz")
    meta = json.loads((work / "motion" / f"{name}.json").read_text())
    d = np.convolve(npz["dist"], np.ones(7) / 7, mode="same")
    lo, thr = meta["repouso"], meta["limiar"]
    act = d > thr
    segs, start = [], None
    for i, a in enumerate(np.append(act, False)):
        if a and start is None:
            start = i
        elif not a and start is not None:
            segs.append([start, i])
            start = None
    # junta lacunas curtas
    merged = []
    for s in segs:
        if merged and s[0] - merged[-1][1] < int(0.25 * FPS):
            merged[-1][1] = s[1]
        else:
            merged.append(s)

    # divide nos vales: mínimo local bem abaixo dos picos vizinhos (variantes/tomadas sem repouso completo)
    def split(a, b):
        if b - a < int(2.2 * FPS):
            return [[a, b]]
        sub = d[a:b]
        best, best_i = 0, None
        margin = int(0.7 * FPS)
        for i in range(margin, len(sub) - margin):
            if sub[i] != sub[max(0, i - 6):i + 7].min():
                continue
            left, right = sub[:i].max(), sub[i:].max()
            depth = min(left, right) - sub[i]
            rel = depth / max(1e-6, min(left, right) - lo)
            if rel > 0.45 and depth > best:
                best, best_i = depth, i
        if best_i is None:
            return [[a, b]]
        return split(a, a + best_i) + split(a + best_i, b)

    out = []
    for a, b in merged:
        for x, y in split(a, b):
            if y - x >= int(0.5 * FPS):
                out.append([x, y])
    # refina bordas com histerese: estende enquanto ainda está acima de um limiar baixo
    res = []
    for k, (a, b) in enumerate(out):
        peak = d[a:b].max()
        low = lo + 0.12 * (peak - lo)
        prev_end = res[-1]["b"] if res else 0
        nxt = out[k + 1][0] if k + 1 < len(out) else len(d)
        while a > prev_end + 1 and d[a - 1] > low and d[a - 1] < d[a] + 0.5:
            a -= 1
        while b < nxt - 1 and d[b] > low and d[b] < d[b - 1] + 0.5:
            b += 1
        res.append({"a": a, "b": b, "peak": a + int(np.argmax(d[a:b])), "amp": float(peak)})
    return res, d, npz["energy_s"]


# ---------- 2. menções na transcrição ----------
def build_items(blocks):
    allitems = json.loads((HERE / "briefing.json").read_text())
    items = [x for x in allitems if x["bloco"] in blocks]
    for it in items:
        names = [" ".join(norm(it["palavra"]))] + ALIASES.get(it["slug"], [])
        if it["bloco"] == "numeros":
            n = int(it["palavra"])
            names = [str(n), NUM_WORDS[n]]
        if it["bloco"] == "alfabeto":
            names = [it["palavra"].lower()]
        it["_names"] = [n.split() for n in names]
    return items


def mentions(name, items):
    asr = json.loads((work / "asr" / f"{name}.json").read_text())
    toks = []
    for w in asr["words"]:
        for t in norm(w["w"]):
            toks.append({"t": t, "s": w["s"], "e": w["e"]})
    out, i = [], 0
    while i < len(toks):
        best = None
        for n in (4, 3, 2, 1):
            if i + n > len(toks):
                continue
            gram = [x["t"] for x in toks[i:i + n]]
            for j, it in enumerate(items):
                for nm in it["_names"]:
                    if len(nm) != n:
                        continue
                    if it["bloco"] in EXACT_BLOCKS:
                        sc = 1.0 if gram == nm else 0.0
                    else:
                        sc = difflib.SequenceMatcher(None, " ".join(gram), " ".join(nm)).ratio()
                    if sc >= 0.72 and (best is None or sc > best[0] + 1e-9 or (abs(sc - best[0]) < 1e-9 and n > best[2])):
                        best = (sc, j, n)
        if best:
            sc, j, n = best
            # candidatos: todos os itens com score alto para o n-grama vencedor
            gram = " ".join(x["t"] for x in toks[i:i + n])
            cands = {}
            for jj, it in enumerate(items):
                for nm in it["_names"]:
                    if len(nm) != n:
                        continue
                    s2 = (1.0 if gram.split() == nm else 0.0) if it["bloco"] in EXACT_BLOCKS else \
                        difflib.SequenceMatcher(None, gram, " ".join(nm)).ratio()
                    if s2 >= 0.72:
                        cands[jj] = max(cands.get(jj, 0), s2)
            variant = i > 0 and toks[i - 1]["t"] in VARIANT_MARK and toks[i]["s"] - toks[i - 1]["e"] < 1.5
            t0 = toks[i - 1]["s"] if variant else toks[i]["s"]
            out.append({"t": t0, "texto": gram, "cands": cands, "variante": variant})
            i += n
        else:
            i += 1
    return out


# ---------- 3. DP menções -> itens ----------
def assign_items(ms, n_items):
    K = len(ms)
    NEG = -1e9
    # best[k][j]: melhor score usando menções até k, com a menção k atribuída ao item j (ou lixo)
    score = np.full((K + 1, n_items + 1), NEG)  # coluna 0 = antes de qualquer item
    back = {}
    score[0][0] = 0
    for k in range(1, K + 1):
        m = ms[k - 1]
        for j in range(n_items + 1):
            # menção k é lixo: mantém estado j
            if score[k - 1][j] > NEG:
                v = score[k - 1][j] - 0.35
                if v > score[k][j]:
                    score[k][j] = v
                    back[(k, j)] = (j, None)
        for jj, sc in m["cands"].items():
            j = jj + 1
            for i in range(0, j + 1):
                if score[k - 1][i] <= NEG:
                    continue
                gap = max(0, j - i - 1)
                v = score[k - 1][i] + sc - 0.04 * gap - (0.0 if i == j else 0.0)
                if v > score[k][j]:
                    score[k][j] = v
                    back[(k, j)] = (i, jj)
    j = int(np.argmax(score[K]))
    res = [None] * K
    for k in range(K, 0, -1):
        i, jj = back[(k, j)]
        res[k - 1] = jj
        j = i
    return res


# ---------- 4. DP menções -> segmentos ----------
def assign_segments(times, segs, delay=1.5, lo_w=-1.0, hi_w=5.0):
    K, S = len(times), len(segs)
    NEG = -1e9
    sc = np.full((K + 1, S + 1), NEG)
    back = {}
    sc[0][:] = 0
    for k in range(1, K + 1):
        for s in range(0, S + 1):
            # menção sem segmento
            best, arg = sc[k - 1][s] - 1.0, (k - 1, s, None)
            if s > 0:
                # segmento s sem menção
                if sc[k][s - 1] > best:
                    best, arg = sc[k][s - 1], (k, s - 1, None)
                dt = segs[s - 1]["a"] / FPS - times[k - 1]
                if lo_w <= dt <= hi_w:
                    v = sc[k - 1][s - 1] + 1.0 - ((dt - delay) / 2.5) ** 2
                    if v > best:
                        best, arg = v, (k - 1, s - 1, s - 1)
            sc[k][s] = best
            back[(k, s)] = arg
    res = [None] * K
    k, s = K, S
    while k > 0:
        pk, ps, seg = back[(k, s)]
        if pk == k - 1:
            res[k - 1] = seg
        k, s = pk, ps
    return res


def main():
    rows = []
    overrides = {}
    ov = work / "overrides.csv"
    if ov.exists():
        for r in csv.DictReader(ov.open()):
            overrides[r["slug"]] = r
    for name, blocks in FILES.items():
        if not (work / "asr" / f"{name}.json").exists():
            continue
        items = build_items(blocks)
        segs, d, en = find_segments(name)
        ms = mentions(name, items)
        it_idx = assign_items(ms, len(items))
        ms_ok = [dict(m, item=j) for m, j in zip(ms, it_idx) if j is not None]
        seg_idx = assign_segments([m["t"] for m in ms_ok], segs)
        for m, s_i in zip(ms_ok, seg_idx):
            if s_i is not None:
                segs[s_i]["m"] = m
        # menções sem segmento que caem dentro de um sinal já rotulado (variante emendada): divide no vale
        for m, s_i in zip(ms_ok, seg_idx):
            if s_i is not None:
                continue
            t = m["t"] * FPS
            host = next((sg for sg in segs if sg.get("m") and sg["a"] + 0.8 * FPS <= t <= sg["b"] - 1.0 * FPS), None)
            # repetir a mesma palavra sem "ou" dentro do mesmo sinal não é nova tomada
            if not host or (host["m"]["item"] == m["item"] and not m["variante"]):
                continue
            lo_i = int(max(t - 0.5 * FPS, host["a"] + 0.8 * FPS))
            hi_i = int(min(t + 1.5 * FPS, host["b"] - 0.8 * FPS))
            if hi_i <= lo_i:
                continue
            # entre variantes ela segura a pose (energia baixa) e então parte para o novo sinal:
            # o corte é o fim desse "segurar", logo antes da energia subir
            k = lo_i + int(np.argmin(en[lo_i:hi_i]))
            base = en[k]
            while k < hi_i and en[k] < base + 0.6:
                k += 1
            cut = max(lo_i, k - int(0.1 * FPS))
            new_sg = {"a": cut, "b": host["b"], "peak": cut + int(np.argmax(d[cut:host["b"]])), "amp": host["amp"], "m": m}
            host["b"] = cut
            host["peak"] = host["a"] + int(np.argmax(d[host["a"]:cut]))
            segs.append(new_sg)
            segs.sort(key=lambda x: x["a"])
        takes = {}  # item -> lista de tomadas
        for sg in segs:
            if sg.get("m"):
                m = sg["m"]
                takes.setdefault(m["item"], []).append({"seg": sg, "m": m, "flag": "variante" if m["variante"] else ""})
        # segmentos sem fala: (a) emendados logo após uma tomada -> nova tomada do mesmo item;
        # (b) entre dois itens com lacuna -> item faltante (inferido)
        last_item = None
        prev_end = -1e9
        for s_i, sg in enumerate(segs):
            if sg.get("m"):
                last_item, prev_end = sg["m"]["item"], sg["b"]
                continue
            dur = (sg["b"] - sg["a"]) / FPS
            nxt = next((x for x in segs[s_i + 1:] if x.get("m") or x.get("inf") is not None), None)
            if last_item is None or nxt is None or dur < 0.8:
                prev_end = sg["b"]
                continue
            n_item = nxt["m"]["item"] if nxt.get("m") else nxt["inf"]
            missing = [j for j in range(last_item + 1, n_item) if j not in takes]
            if missing:
                j = missing[0]
                flag = "inferido"
            elif (sg["a"] - prev_end) / FPS < 1.0 and 1.0 <= dur <= 7.0:
                j = last_item
                flag = "tomada_sem_fala"
            else:
                prev_end = sg["b"]
                continue
            sg["inf"] = j
            takes.setdefault(j, []).append({"seg": sg, "m": None, "flag": flag})
            last_item, prev_end = j, sg["b"]
        for j, it in enumerate(items):
            ts = [t for t in takes.get(j, []) if t["seg"]]
            ts.sort(key=lambda t: t["seg"]["a"])
            for n_t, t in enumerate(ts):
                sg = t["seg"]
                dur = (sg["b"] - sg["a"]) / FPS
                flags = [f for f in [t["flag"], "longo" if dur > 4.5 else ""] if f]
                rows.append({
                    "slug": it["slug"], "palavra": it["palavra"], "categoria": it["categoria"], "bloco": it["bloco"],
                    "arquivo": name, "ini": round(sg["a"] / FPS, 3), "fim": round(sg["b"] / FPS, 3),
                    "pico": round(sg["peak"] / FPS, 3), "dur": round(dur, 2),
                    "ouvido": t["m"]["texto"] if t["m"] else "", "fala_t": round(t["m"]["t"], 2) if t["m"] else "",
                    "tomada": n_t + 1, "tomadas": len(ts), "oficial": int(n_t == len(ts) - 1),
                    "flags": " ".join(flags),
                })
    # itens sem nenhuma tomada
    found = {r["slug"] for r in rows}
    for it in json.loads((HERE / "briefing.json").read_text()):
        if it["slug"] not in found:
            rows.append({"slug": it["slug"], "palavra": it["palavra"], "categoria": it["categoria"], "bloco": it["bloco"],
                         "arquivo": "", "ini": "", "fim": "", "pico": "", "dur": "", "ouvido": "", "fala_t": "",
                         "tomada": 0, "tomadas": 0, "oficial": 0, "flags": "nao_encontrado"})
    # overrides manuais substituem a tomada oficial
    for r in rows:
        o = overrides.get(r["slug"])
        if o and r["oficial"] == 1:
            r.update(arquivo=o["arquivo"], ini=float(o["ini"]), fim=float(o["fim"]),
                     pico=round((float(o["ini"]) + float(o["fim"])) / 2, 3),
                     dur=round(float(o["fim"]) - float(o["ini"]), 2), flags="manual")
    order = {it["slug"]: i for i, it in enumerate(json.loads((HERE / "briefing.json").read_text()))}
    rows.sort(key=lambda r: (order[r["slug"]], r["tomada"]))
    with (work / "manifest.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    of = [r for r in rows if r["oficial"] == 1]
    print(f"{len(of)} itens com tomada oficial; {sum(1 for r in rows if r['flags'] == 'nao_encontrado')} não encontrados")


if __name__ == "__main__":
    main()
