#!/usr/bin/env python3
"""
Generate a compact inline SVG of Brazil's states from IBGE GeoJSON API.
"""

import gzip
import json
import math
import urllib.request
import os
import sys

# ── Config ──────────────────────────────────────────────────────────────────
SVG_W = 500
SVG_H = 560
PAD   = 10          # pixels of padding on each side

# Bounding box for Brazil
LON_MIN, LON_MAX = -73.99, -28.84
LAT_MIN, LAT_MAX = -33.75,   5.27

# Inner canvas (after padding)
INNER_W = SVG_W - 2 * PAD
INNER_H = SVG_H - 2 * PAD

# Coordinate decimal precision (2 decimals = ~1km accuracy, good for display)
COORD_PRECISION = 1  # 1 decimal = ~10km, much smaller file

# Output
OUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "brazil-map.svg")

# API endpoints (try in order)
APIS = [
    # v3: BR country mesh with state subdivisions, resolution 2 (low), geojson
    "https://servicodados.ibge.gov.br/api/v3/malhas/paises/BR?formato=application/vnd.geo%2Bjson&resolucao=2&intrarregiao=UF",
    # v3: fallback — all states (may return 404 depending on API version)
    "https://servicodados.ibge.gov.br/api/v3/malhas/paises/BR?formato=application/vnd.geo%2Bjson&resolucao=2",
]

# Cities to report positions for
CITIES = {
    "Boa Vista":    [-60.67,  2.82],
    "Manaus":       [-60.02, -3.10],
    "Belém":        [-48.49, -1.45],
    "Fortaleza":    [-38.54, -3.72],
    "João Pessoa":  [-34.87, -7.12],
    "Salvador":     [-38.52,-12.97],
    "Porto Velho":  [-63.90, -8.76],
    "Brasília":     [-47.93,-15.78],
    "Goiânia":      [-49.26,-16.67],
    "BH":           [-43.94,-19.92],
    "Rio":          [-43.17,-22.91],
    "SP":           [-46.63,-23.55],
    "Curitiba":     [-49.27,-25.43],
    "Floripa":      [-48.55,-27.60],
    "POA":          [-51.23,-30.03],
}


# ── Projection ───────────────────────────────────────────────────────────────
def project(lon, lat):
    x = (lon - LON_MIN) / (LON_MAX - LON_MIN) * INNER_W + PAD
    y = (LAT_MAX - lat) / (LAT_MAX - LAT_MIN) * INNER_H + PAD
    return x, y


# ── Douglas-Peucker simplification ──────────────────────────────────────────
def point_line_dist(p, a, b):
    """Perpendicular distance from point p to line a-b (in pixel space)."""
    ax, ay = a
    bx, by = b
    px, py = p
    dx, dy = bx - ax, by - ay
    if dx == 0 and dy == 0:
        return math.hypot(px - ax, py - ay)
    t = ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)
    t = max(0.0, min(1.0, t))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))


def rdp(points, epsilon=0.5):
    """Ramer–Douglas–Peucker simplification (pixel coordinates)."""
    if len(points) < 3:
        return points
    # Find the point with the maximum distance
    dmax = 0.0
    idx = 0
    end = len(points) - 1
    for i in range(1, end):
        d = point_line_dist(points[i], points[0], points[end])
        if d > dmax:
            dmax = d
            idx = i
    if dmax > epsilon:
        left  = rdp(points[:idx + 1], epsilon)
        right = rdp(points[idx:], epsilon)
        return left[:-1] + right
    return [points[0], points[end]]


# ── GeoJSON → SVG path ───────────────────────────────────────────────────────
def ring_to_path(coords, epsilon=0.5):
    """Convert a ring of [lon, lat] pairs into an SVG path fragment."""
    # Project all points
    projected = [project(lon, lat) for lon, lat in coords]
    # Simplify
    simplified = rdp(projected, epsilon)
    if len(simplified) < 3:
        return ""
    parts = []
    for i, (x, y) in enumerate(simplified):
        fmt = f"{x:.{COORD_PRECISION}f},{y:.{COORD_PRECISION}f}"
        parts.append(("M" if i == 0 else "L") + fmt)
    parts.append("Z")
    return "".join(parts)


def geometry_to_d(geometry, epsilon=0.5):
    """Return combined 'd' string for a Polygon or MultiPolygon geometry."""
    gtype = geometry["type"]
    parts = []

    if gtype == "Polygon":
        for ring in geometry["coordinates"]:
            d = ring_to_path(ring, epsilon)
            if d:
                parts.append(d)

    elif gtype == "MultiPolygon":
        for polygon in geometry["coordinates"]:
            for ring in polygon:
                d = ring_to_path(ring, epsilon)
                if d:
                    parts.append(d)

    return "".join(parts)


# ── Fetch GeoJSON ─────────────────────────────────────────────────────────────
def fetch_geojson():
    for url in APIS:
        print(f"  Trying: {url[:90]}...", file=sys.stderr)
        try:
            req = urllib.request.Request(
                url,
                headers={
                    "Accept": "application/vnd.geo+json, application/json, */*",
                    "Accept-Encoding": "gzip, deflate",
                    "User-Agent": "Mozilla/5.0 (compatible; brazil-map-gen/1.0)"
                }
            )
            with urllib.request.urlopen(req, timeout=60) as resp:
                ctype    = resp.headers.get("Content-Type", "")
                encoding = resp.headers.get("Content-Encoding", "")
                raw      = resp.read()
                # Decompress if gzip
                if encoding == "gzip" or raw[:2] == b'\x1f\x8b':
                    raw = gzip.decompress(raw)
                text = raw.decode("utf-8")
                print(f"  OK — {len(raw):,} bytes  Content-Type: {ctype}", file=sys.stderr)
                return json.loads(text)
        except Exception as e:
            print(f"  FAIL: {e}", file=sys.stderr)
    raise RuntimeError("All IBGE API endpoints failed.")


# ── Build SVG ─────────────────────────────────────────────────────────────────
def build_svg(geojson, epsilon=0.5):
    defs = (
        '<defs>'
        '<linearGradient id="mapGrad" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0%" stop-color="#22c55e"/>'
        '<stop offset="100%" stop-color="#16a34a"/>'
        '</linearGradient>'
        '</defs>'
    )

    path_attr = 'fill="url(#mapGrad)" stroke="rgba(255,255,255,0.35)" stroke-width="0.8"'

    features = geojson.get("features", [])
    if not features:
        # Some endpoints return a geometry directly (no FeatureCollection wrapper)
        features = [{"geometry": geojson}]

    print(f"  Processing {len(features)} features…", file=sys.stderr)

    all_d_parts = []
    for feature in features:
        geom = feature.get("geometry") or feature
        if geom is None:
            continue
        d = geometry_to_d(geom, epsilon)
        if d:
            all_d_parts.append(d)

    # Emit one <path> per feature so states have visible borders
    paths_str = "".join(
        f'<path {path_attr} d="{d}"/>' for d in all_d_parts
    )

    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {SVG_W} {SVG_H}" '
        f'role="img" aria-hidden="true">'
        f'{defs}'
        f'{paths_str}'
        f'</svg>'
    )
    return svg


# ── City positions ────────────────────────────────────────────────────────────
def city_positions():
    result = {}
    for name, (lon, lat) in CITIES.items():
        x, y = project(lon, lat)
        left_pct = round(x / SVG_W * 100, 2)
        top_pct  = round(y / SVG_H * 100, 2)
        result[name] = {
            "left": left_pct,
            "top":  top_pct,
            "x_px": round(x, 1),
            "y_px": round(y, 1)
        }
    return result


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    print("Fetching GeoJSON from IBGE…", file=sys.stderr)
    geojson = fetch_geojson()

    print("Building SVG (RDP simplification epsilon=0.5px)…", file=sys.stderr)
    svg = build_svg(geojson, epsilon=0.5)

    print(f"Writing to {OUT_PATH}…", file=sys.stderr)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write(svg)

    size_bytes = os.path.getsize(OUT_PATH)
    size_kb    = size_bytes / 1024

    print(f"File size: {size_kb:.1f} KB  ({size_bytes:,} bytes)", file=sys.stderr)

    if size_kb > 200:
        print(f"WARNING: {size_kb:.0f} KB exceeds 200 KB — re-running with higher epsilon…",
              file=sys.stderr)
        # Increase epsilon until we fit
        for eps in [1.0, 1.5, 2.0, 3.0]:
            svg = build_svg(geojson, epsilon=eps)
            with open(OUT_PATH, "w", encoding="utf-8") as f:
                f.write(svg)
            size_bytes = os.path.getsize(OUT_PATH)
            size_kb    = size_bytes / 1024
            print(f"  epsilon={eps}: {size_kb:.1f} KB", file=sys.stderr)
            if size_kb <= 200:
                print(f"  OK — fits with epsilon={eps}", file=sys.stderr)
                break
        else:
            print("ERROR: could not reduce below 200 KB", file=sys.stderr)
    else:
        print("OK — within 200 KB limit.", file=sys.stderr)

    positions = city_positions()

    print("\n=== FILE SIZE ===")
    print(f"{size_kb:.1f} KB  ({size_bytes:,} bytes)")

    print("\n=== CITY POSITIONS (left%, top% in 500x560 viewBox) ===")
    print(json.dumps(positions, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
