#!/usr/bin/env python3
"""Extrae las tarjetas ORIGINALES (tile completo: fondo oscuro, borde, ícono, nombre y precio) de las capturas 14, 18, 20 y 21.
Solo se recorta por el borde exterior y se amplía con Lanczos + nitidez leve. No se recorta el ícono ni se redibuja nada."""
import os, json, numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage as ndi
ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = "/tmp/claude-0/-home-user-Claude-Code-Videos/d7eef31e-54e1-596e-a9cb-13062292304f/images/"
OUT = os.path.join(ROOT, "assets/tiles/"); os.makedirs(OUT, exist_ok=True)
PAGE = np.array([36, 36, 41]); CARD = np.array([23, 23, 25]); K = 4
SEL = {  # categoría: (captura, ítems en orden de la imagen = precio descendente)
 "perm": (14, [("Dragón Permanente", 625), ("Control Permanente", 500), ("Kitsune Permanente", 500), ("Magnet Permanente", 440), ("Yeti Permanente", 375), ("Tiger Permanente", 375)]),
 "fis": (18, [("Dragón West", 360), ("Dragón East", 320), ("Magnet", 140), ("Kitsune", 100), ("Control", 55), ("Yeti", 50)]),
 "gp": (20, [("Fruit Notifier", 340), ("Dark Blade", 150), ("2x Mastery", 60), ("2x Money", 60), ("+1 Fruit Storage", 50), ("Fast Boats", 45)]),
 "skin": (21, [("Galaxy Empyrean Kits...", 950), ("Ember Dragon", 650), ("Purple Lightbning", 550), ("Arcsteel Magnet", 350), ("Super Spirit Pain", 340), ("Red Lightning", 285)]),
}
def approx_grid(im):
    m = (abs(im - CARD).sum(2) < 14); m = ndi.binary_fill_holes(ndi.binary_closing(m, iterations=3))
    lab, _ = ndi.label(m)
    bx = [(s[1].start, s[0].start, s[1].stop, s[0].stop) for s in ndi.find_objects(lab) if s[1].stop - s[1].start > 80 and s[0].stop - s[0].start > 90]
    x0 = min(b[0] for b in bx); x3 = max(b[2] for b in bx) - 93; ys = sorted(set(b[1] for b in bx)); y0 = ys[0]; y1 = ys[-1]
    px = (x3 - x0) / 3
    return [(x0 + c * px, y0 + r * (y1 - y0)) for r in range(2) for c in range(4)]
def exact_bbox(im, ax, ay):
    x0, y0 = int(ax) - 5, int(ay) - 5; x1, y1 = int(ax) + 99, int(ay) + 116
    win = im[y0:y1, x0:x1]
    nonbg = (abs(win - PAGE).sum(2) > 10)
    nonbg = ndi.binary_closing(nonbg, iterations=1)
    lab, k = ndi.label(nonbg)
    sizes = ndi.sum(nonbg, lab, range(1, k + 1)); big = 1 + int(np.argmax(sizes))
    ys, xs = np.where(lab == big)
    return x0 + xs.min(), y0 + ys.min(), x0 + xs.max() + 1, y0 + ys.max() + 1
manifest = []; boxes = {}
for cat, (n, items) in SEL.items():
    img = Image.open(SRC + f"{n}.png").convert("RGB"); im = np.array(img).astype(int)
    for i, (ax, ay) in enumerate(approx_grid(im)[:len(items)]):
        boxes[(cat, i)] = exact_bbox(im, ax, ay)
ws = [b[2] - b[0] for b in boxes.values()]; hs = [b[3] - b[1] for b in boxes.values()]
W0, H0 = int(np.median(ws)), int(np.median(hs)); print("tile nativo", W0, "x", H0, "rangos", min(ws), max(ws), min(hs), max(hs))
for cat, (n, items) in SEL.items():
    img = Image.open(SRC + f"{n}.png").convert("RGB")
    for i, (name, price) in enumerate(items):
        x0, y0, x1, y1 = boxes[(cat, i)]
        cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
        c = img.crop((cx - W0 // 2, cy - H0 // 2, cx - W0 // 2 + W0, cy - H0 // 2 + H0))   # mismo tamaño para todas (sin estirar)
        a = np.array(c).astype(int)
        bgm = (abs(a - PAGE).sum(2) < 12)             # fondo de página fuera del tile (esquinas redondeadas)
        lab, _ = ndi.label(bgm); edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
        outside = np.isin(lab, list(edge))
        big = c.resize((W0 * K, H0 * K), Image.LANCZOS).filter(ImageFilter.UnsharpMask(1.2, 40, 2))
        al = Image.fromarray(((~outside) * 255).astype(np.uint8)).resize(big.size, Image.BICUBIC).filter(ImageFilter.GaussianBlur(1.4))
        al = al.point(lambda v: 0 if v < 70 else (255 if v > 185 else int((v - 70) * 255 / 115)))
        big.putalpha(al); fn = f"{cat}_{i}.png"; big.save(OUT + fn)
        manifest.append(dict(cat=cat, file=fn, name=name, price=price, src=n))
json.dump(dict(tile=[W0, H0], tiles=manifest), open(os.path.join(ROOT, "tiles.json"), "w"), ensure_ascii=False, indent=1)
print(len(manifest), "tiles")
