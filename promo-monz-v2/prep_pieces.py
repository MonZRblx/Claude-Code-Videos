#!/usr/bin/env python3
"""Recorta cada objeto de las capturas 14–22: ícono limpio (sin fondo cuadrado) con contorno tipo sticker.
Nombre y precio se dibujan como texto exacto en el video (data.py)."""
import os, json, numpy as np, cv2
from PIL import Image, ImageFilter
from scipy import ndimage as ndi
from data import CATS
ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = "/tmp/claude-0/-home-user-Claude-Code-Videos/d7eef31e-54e1-596e-a9cb-13062292304f/images/"
OUT = os.path.join(ROOT, "assets/pieces/"); os.makedirs(OUT, exist_ok=True)
BG = np.array([23, 23, 25]); K = 4; PAD = 14; OUTLINE = 7

def grid(n, count):
    im = np.array(Image.open(SRC + f"{n}.png").convert("RGB")).astype(int)
    m = (abs(im - BG).sum(2) < 14); m = ndi.binary_fill_holes(ndi.binary_closing(m, iterations=3))
    lab, _ = ndi.label(m); bx = [(s[1].start, s[0].start, s[1].stop, s[0].stop) for s in ndi.find_objects(lab) if s[1].stop - s[1].start > 80 and s[0].stop - s[0].start > 90]
    x0 = min(b[0] for b in bx); x3 = max(b[2] for b in bx) - 93; ys = sorted(set(b[1] for b in bx))
    y0 = ys[0]; y1 = ys[-1]
    cols = 4; px = (x3 - x0) / 3
    rows = 1 if count <= 4 else 2
    return [(int(x0 + c * px), int(y0 + r * (y1 - y0))) for r in range(rows) for c in range(cols)][:count], 93, 110

def cutout(img, x, y, w, h):
    c = img.crop((x + 5, y + 5, x + w - 5, y + int(h * 0.60)))
    a = np.array(c).astype(int); d = np.abs(a - BG).max(2)
    bgm = d <= 15
    lab, _ = ndi.label(bgm)
    edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    bg = np.isin(lab, list(edge))
    fg = ~bg
    fg = ndi.binary_opening(fg, iterations=1) | (fg & ndi.binary_dilation(ndi.binary_opening(fg, iterations=1), iterations=1))
    lab2, k = ndi.label(fg)
    if k:
        sizes = ndi.sum(fg, lab2, range(1, k + 1)); keep = [i + 1 for i, s_ in enumerate(sizes) if s_ >= 14]
        fg = np.isin(lab2, keep)
    rgb = c.resize((c.width * K, c.height * K), Image.LANCZOS).filter(ImageFilter.UnsharpMask(1.5, 55, 2))
    m = Image.fromarray((fg * 255).astype(np.uint8)).resize(rgb.size, Image.BICUBIC).filter(ImageFilter.GaussianBlur(1.6))
    m = np.array(m).astype(np.float32) / 255
    m = np.clip((m - .5) * 4 + .5, 0, 1)
    m = cv2.erode(m, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)))
    return np.array(rgb), m

def sticker(rgb, m):
    h, w = m.shape
    P_ = PAD + OUTLINE
    R = np.zeros((h + 2 * P_, w + 2 * P_, 3), np.uint8); A = np.zeros((h + 2 * P_, w + 2 * P_), np.float32)
    R[P_:P_ + h, P_:P_ + w] = rgb; A[P_:P_ + h, P_:P_ + w] = m
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * OUTLINE + 1, 2 * OUTLINE + 1))
    base = (A > .5).astype(np.uint8)
    base = cv2.morphologyEx(base, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (13, 13)))
    dil = cv2.dilate(base, k).astype(np.float32)
    dil = cv2.GaussianBlur(dil, (0, 0), 2.6)
    dil = np.clip((dil - .5) * 6 + .5, 0, 1)
    gold = np.array([255, 226, 120], np.float32)
    out = np.zeros(R.shape[:2] + (4,), np.float32)
    out[..., :3] = gold; out[..., 3] = dil
    ic = np.concatenate([R.astype(np.float32), (A * 255)[..., None]], 2)
    a = ic[..., 3:4] / 255
    comp = ic[..., :3] * a + out[..., :3] * (1 - a)
    alpha = np.maximum(out[..., 3], ic[..., 3] / 255)
    res = np.dstack([comp, alpha * 255]).astype(np.uint8)
    ys, xs = np.where(res[..., 3] > 8)
    return Image.fromarray(res).crop((xs.min() - 4, ys.min() - 4, xs.max() + 5, ys.max() + 5))

manifest = []
for cat in CATS:
    idx = 0
    for n, items in cat["src"]:
        img = Image.open(SRC + f"{n}.png").convert("RGB")
        pos, w, h = grid(n, len(items))
        for (x, y), (name, price) in zip(pos, items):
            rgb, m = cutout(img, x, y, w, h); st = sticker(rgb, m)
            fn = f"{cat['key']}_{idx:02d}.png"; st.save(OUT + fn)
            manifest.append(dict(cat=cat["key"], file=fn, name=name, price=price, size=st.size, src=n, box=[x, y])); idx += 1
json.dump(manifest, open(os.path.join(ROOT, "pieces.json"), "w"), ensure_ascii=False, indent=1)
print(len(manifest), "piezas")
