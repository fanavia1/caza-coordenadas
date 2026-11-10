"""Download Natural Earth land (world-atlas TopoJSON), convert to an SVG path, inline into the game page."""
import json
import sys
import urllib.request
from pathlib import Path

URL = "https://cdn.jsdelivr.net/npm/world-atlas@2.0.2/land-110m.json"
data_file, template, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])

if not data_file.exists():
    data_file.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(URL, headers={"User-Agent": "map-build-script"})
    with urllib.request.urlopen(req, timeout=60) as r:
        data_file.write_bytes(r.read())

topo = json.loads(data_file.read_text(encoding="utf-8"))
sx, sy = topo["transform"]["scale"]
tx, ty = topo["transform"]["translate"]

arcs = []
for arc in topo["arcs"]:
    x = y = 0
    pts = []
    for dx, dy in arc:
        x += dx
        y += dy
        pts.append((x * sx + tx, y * sy + ty))
    arcs.append(pts)


def ring_points(ring):
    pts = []
    for i in ring:
        a = arcs[i] if i >= 0 else arcs[~i][::-1]
        pts.extend(a[1:] if pts else a)
    return pts


def polygons(geom):
    t = geom["type"]
    if t == "GeometryCollection":
        for g in geom["geometries"]:
            yield from polygons(g)
    elif t == "Polygon":
        yield geom["arcs"]
    elif t == "MultiPolygon":
        yield from geom["arcs"]


def num(v):
    s = f"{v:.1f}"
    return s[:-2] if s.endswith(".0") else s


parts = []
count = 0
for poly in polygons(topo["objects"]["land"]):
    for ring in poly:
        pts = ring_points(ring)
        # Unwrap rings that cross the antimeridian, then draw a shifted copy so both halves show.
        un, off = [], 0
        for i, (lon, lat) in enumerate(pts):
            if i:
                d = lon - pts[i - 1][0]
                if d > 180:
                    off -= 360
                elif d < -180:
                    off += 360
            un.append((lon + off, lat))
        lons = [p[0] for p in un]
        shifts = [0]
        if min(lons) < -180:
            shifts.append(360)
        if max(lons) > 180:
            shifts.append(-360)
        for shift in shifts:
            seq, last = [], None
            for lon, lat in un:
                p = (num(lon + shift + 180), num(90 - lat))
                if p != last:
                    seq.append(p)
                    last = p
            if len(seq) < 3:
                continue
            count += len(seq)
            parts.append("M" + "L".join(f"{x} {y}" for x, y in seq) + "Z")

path = "".join(parts)
html = template.read_text(encoding="utf-8")
assert "__LAND_PATH__" in html
out.write_text(html.replace("__LAND_PATH__", path), encoding="utf-8")
print(f"rings={len(parts)} points={count} path_bytes={len(path)} html_bytes={out.stat().st_size}")
