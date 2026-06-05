#!/usr/bin/env python3
"""
gen_brazil_map.py, Gera brazil-map.svg para o site Libras.se.

Sistema de coordenadas garantido:
  • O bounding box é calculado dos dados reais do IBGE (não fixo).
  • A MESMA função project() é usada para desenhar os paths E calcular os pins.
  • Resultado: zero desalinhamento entre mapa e pins.

CSS obrigatório no site:
  .map-stage  { position:relative; width:100%; aspect-ratio:500/560; }
  .map-img-el { position:absolute; inset:0; width:100%; height:100%;
                object-fit:contain; object-position:center; }
  .pins       { position:absolute; inset:0; pointer-events:none; }
  .pin        { position:absolute; left:var(--x); top:var(--y);
                transform:translate(-50%,-50%); pointer-events:auto; }

NUNCA use object-fit:fill, distorce o mapa e quebra o alinhamento dos pins.
"""

import gzip
import json
import math
import os
import sys
import urllib.request

# ── Dimensões do canvas ───────────────────────────────────────────────────────
SVG_W = 500
SVG_H = 560
PAD   = 12   # margem em pixels em cada lado

COORD_PRECISION = 1  # casas decimais nas coordenadas SVG (~10 km de resolução)

OUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "brazil-map.svg")

# ── Endpoints IBGE ────────────────────────────────────────────────────────────
APIS = [
    "https://servicodados.ibge.gov.br/api/v3/malhas/paises/BR"
    "?formato=application/vnd.geo%2Bjson&resolucao=2&intrarregiao=UF",
    "https://servicodados.ibge.gov.br/api/v3/malhas/paises/BR"
    "?formato=application/vnd.geo%2Bjson&resolucao=2",
]

# ── Cidades (lon, lat) ────────────────────────────────────────────────────────
CITIES = {
    "Boa Vista":   (-60.67,   2.82),
    "Manaus":      (-60.02,  -3.10),
    "Belém":       (-48.49,  -1.45),
    "Fortaleza":   (-38.54,  -3.72),
    "João Pessoa": (-34.87,  -7.12),
    "Salvador":    (-38.52, -12.97),
    "Porto Velho": (-63.90,  -8.76),
    "Brasília":    (-47.93, -15.78),
    "Goiânia":     (-49.26, -16.67),
    "BH":          (-43.94, -19.92),
    "Rio":         (-43.17, -22.91),
    "SP":          (-46.63, -23.55),
    "Curitiba":    (-49.27, -25.43),
    "Floripa":     (-48.55, -27.60),
    "POA":         (-51.23, -30.03),
}


# ── Bounding box dinâmico ─────────────────────────────────────────────────────
def compute_bounds(geojson):
    """
    Calcula min/max de lon/lat dos dados reais do GeoJSON.
    Garante que a projeção cubra exatamente o extent dos paths.
    """
    mn_lon = mn_lat =  float("inf")
    mx_lon = mx_lat = -float("inf")

    def walk(obj):
        nonlocal mn_lon, mx_lon, mn_lat, mx_lat
        if isinstance(obj, list) and obj and isinstance(obj[0], (int, float)):
            mn_lon = min(mn_lon, obj[0]); mx_lon = max(mx_lon, obj[0])
            mn_lat = min(mn_lat, obj[1]); mx_lat = max(mx_lat, obj[1])
        elif isinstance(obj, list):
            for item in obj:
                walk(item)

    features = geojson.get("features") or [{"geometry": geojson}]
    for feat in features:
        geom = feat.get("geometry") or feat
        if geom and "coordinates" in geom:
            walk(geom["coordinates"])

    return mn_lon, mx_lon, mn_lat, mx_lat


# ── Projeção ──────────────────────────────────────────────────────────────────
def make_projector(lon_min, lon_max, lat_min, lat_max):
    """
    Retorna project(lon, lat) → (x, y) em coordenadas do SVG.
    PAD garante margem visual sem crop.
    A MESMA função é usada para paths e pins, coordenadas sempre alinhadas.
    """
    inner_w = SVG_W - 2 * PAD
    inner_h = SVG_H - 2 * PAD
    lon_span = lon_max - lon_min
    lat_span = lat_max - lat_min

    def project(lon, lat):
        x = (lon - lon_min) / lon_span * inner_w + PAD
        y = (lat_max - lat) / lat_span * inner_h + PAD
        return x, y

    return project


# ── Douglas-Peucker simplification ───────────────────────────────────────────
def _dist(p, a, b):
    ax, ay = a; bx, by = b; px, py = p
    dx, dy = bx - ax, by - ay
    if dx == 0 and dy == 0:
        return math.hypot(px - ax, py - ay)
    t = max(0.0, min(1.0, ((px-ax)*dx + (py-ay)*dy) / (dx*dx + dy*dy)))
    return math.hypot(px - ax - t*dx, py - ay - t*dy)


def rdp(pts, eps=0.5):
    if len(pts) < 3:
        return pts
    dmax, idx = 0.0, 0
    end = len(pts) - 1
    for i in range(1, end):
        d = _dist(pts[i], pts[0], pts[end])
        if d > dmax:
            dmax, idx = d, i
    if dmax > eps:
        return rdp(pts[:idx+1], eps)[:-1] + rdp(pts[idx:], eps)
    return [pts[0], pts[end]]


# ── GeoJSON → SVG paths ───────────────────────────────────────────────────────
def ring_to_path(coords, project, eps):
    pts = rdp([project(c[0], c[1]) for c in coords], eps)
    if len(pts) < 3:
        return ""
    p = COORD_PRECISION
    parts = [f"M{pts[0][0]:.{p}f},{pts[0][1]:.{p}f}"]
    for x, y in pts[1:]:
        parts.append(f"L{x:.{p}f},{y:.{p}f}")
    parts.append("Z")
    return "".join(parts)


def geom_to_d(geom, project, eps):
    rings = (geom["coordinates"] if geom["type"] == "Polygon"
             else [r for poly in geom["coordinates"] for r in poly])
    return "".join(d for r in rings if (d := ring_to_path(r, project, eps)))


# ── Fetch GeoJSON ─────────────────────────────────────────────────────────────
def fetch_geojson():
    for url in APIS:
        print(f"  Tentando: {url[:88]}…", file=sys.stderr)
        try:
            req = urllib.request.Request(url, headers={
                "Accept":          "application/vnd.geo+json, application/json, */*",
                "Accept-Encoding": "gzip, deflate",
                "User-Agent":      "Mozilla/5.0 (compatible; brazil-map-gen/2.0)",
            })
            with urllib.request.urlopen(req, timeout=60) as resp:
                raw = resp.read()
                if resp.headers.get("Content-Encoding") == "gzip" or raw[:2] == b"\x1f\x8b":
                    raw = gzip.decompress(raw)
                print(f"  OK, {len(raw):,} bytes", file=sys.stderr)
                return json.loads(raw.decode("utf-8"))
        except Exception as exc:
            print(f"  FALHOU: {exc}", file=sys.stderr)
    raise RuntimeError("Todos os endpoints IBGE falharam.")


# ── Build SVG ─────────────────────────────────────────────────────────────────
def build_svg(geojson, project, eps=0.5):
    # SVG decorativo, aria-hidden="true", sem role="img" (contradição de acessibilidade)
    defs = (
        '<defs>'
        '<linearGradient id="mapGrad" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0%" stop-color="#1f5a60"/>'
        '<stop offset="100%" stop-color="#0e3538"/>'
        '</linearGradient>'
        '</defs>'
    )
    attr = 'fill="url(#mapGrad)" stroke="#b2f5ea" stroke-opacity=".35" stroke-width="0.8"'

    features = geojson.get("features") or [{"geometry": geojson}]
    print(f"  Processando {len(features)} features…", file=sys.stderr)

    paths = []
    for feat in features:
        geom = feat.get("geometry") or feat
        if geom:
            d = geom_to_d(geom, project, eps)
            if d:
                paths.append(f'<path {attr} d="{d}"/>')

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {SVG_W} {SVG_H}" '
        f'aria-hidden="true" focusable="false">'
        f'{defs}{"".join(paths)}'
        f'</svg>'
    )


# ── Pin positions ─────────────────────────────────────────────────────────────
def compute_pins(project):
    """
    Usa a MESMA project() dos paths, alinhamento perfeito garantido.
    Percentuais relativos ao viewBox completo (inclui PAD).
    """
    pins = []
    for name, (lon, lat) in CITIES.items():
        x, y = project(lon, lat)
        pins.append({
            "name": name,
            "x":    round(x / SVG_W * 100, 2),
            "y":    round(y / SVG_H * 100, 2),
        })
    return pins


# ── Saída formatada ───────────────────────────────────────────────────────────
def print_html_pins(pins):
    print("\n=== HTML PINS (cole dentro de .pins) ===")
    for p in pins:
        print(
            f'              <div class="pin" style="--x:{p["x"]}%;--y:{p["y"]}%">'
            f'<div class="pin-body">'
            f'<div class="pdot"><div class="pring" aria-hidden="true"></div></div>'
            f'<span class="pname">{p["name"]}</span>'
            f'</div></div>'
        )


def print_js_pins(pins):
    print("\n=== JS / JSON PINS ===")
    print("const PINS = [")
    for p in pins:
        print(f'  {{ name: "{p["name"]}", x: "{p["x"]}%", y: "{p["y"]}%" }},')
    print("];")


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    print("Baixando GeoJSON do IBGE…", file=sys.stderr)
    geojson = fetch_geojson()

    print("Calculando bounding box real dos dados…", file=sys.stderr)
    lon_min, lon_max, lat_min, lat_max = compute_bounds(geojson)
    print(f"  lon: {lon_min:.4f} → {lon_max:.4f}", file=sys.stderr)
    print(f"  lat: {lat_min:.4f} → {lat_max:.4f}", file=sys.stderr)

    project = make_projector(lon_min, lon_max, lat_min, lat_max)

    print("Construindo SVG (RDP epsilon=0.5px)…", file=sys.stderr)
    svg = build_svg(geojson, project, eps=0.5)

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write(svg)

    size_b  = os.path.getsize(OUT_PATH)
    size_kb = size_b / 1024
    print(f"Tamanho: {size_kb:.1f} KB ({size_b:,} bytes)", file=sys.stderr)

    if size_kb > 200:
        print(f"AVISO: {size_kb:.0f} KB > 200 KB, reduzindo com epsilon maior…", file=sys.stderr)
        for eps in [1.0, 1.5, 2.0, 3.0]:
            svg = build_svg(geojson, project, eps)
            with open(OUT_PATH, "w", encoding="utf-8") as f:
                f.write(svg)
            size_b  = os.path.getsize(OUT_PATH)
            size_kb = size_b / 1024
            print(f"  epsilon={eps}: {size_kb:.1f} KB", file=sys.stderr)
            if size_kb <= 200:
                print(f"  OK, cabe com epsilon={eps}", file=sys.stderr)
                break
        else:
            print("ERRO: não conseguiu reduzir abaixo de 200 KB", file=sys.stderr)

    pins = compute_pins(project)
    print_html_pins(pins)
    print_js_pins(pins)

    print("\n=== RESUMO ===")
    print(f"  Arquivo      : {OUT_PATH}")
    print(f"  viewBox      : 0 0 {SVG_W} {SVG_H}")
    print(f"  aspect-ratio : {SVG_W} / {SVG_H}  ← use no CSS de .map-stage")
    print(f"  padding      : {PAD}px por lado")
    print(f"  pins         : {len(pins)} cidades calculadas")
    print(f"  tamanho      : {size_kb:.1f} KB")
    print()
    print("  ✓ Use object-fit:contain no .map-img-el")
    print("  ✗ NUNCA use object-fit:fill, distorce o mapa e quebra os pins")


if __name__ == "__main__":
    main()
