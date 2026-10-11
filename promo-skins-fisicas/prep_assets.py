#!/usr/bin/env python3
"""Prepara las capturas originales (sin alterar su contenido): recorta tarjetas de skins, amplía con Lanczos.
BLUR_OTHER_PLAYERS=True difumina el nombre del otro jugador en los trades (privacidad, opcional)."""
import os, numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage as ndi
ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = "/tmp/claude-0/-home-user-Claude-Code-Videos/d7eef31e-54e1-596e-a9cb-13062292304f/images/"
OUT = os.path.join(ROOT, "assets/captures/")
BLUR_OTHER_PLAYERS = False
os.makedirs(OUT, exist_ok=True)

def up(im, k, sharp=True):
    im = im.resize((im.width * k, im.height * k), Image.LANCZOS)
    return im.filter(ImageFilter.UnsharpMask(1.6, 45, 2)) if sharp else im

# --- tarjetas de skins (captura 8): cada tarjeta original con nombre y precio
img = Image.open(SRC + "8.png").convert("RGB")
panels = [(22, 17, 227, 387), (302, 17, 111, 387)]
idx = 0
for (y0, x0, h, w) in panels:
    rows = round((h + 5) / 116); gap = 5
    cw = (w - 3 * gap) / 4; ch = (h - (rows - 1) * gap) / rows
    for r in range(rows):
        for c in range(4):
            x = int(x0 + c * (cw + gap)); y = int(y0 + r * (ch + gap))
            up(img.crop((x, y, int(x + cw), int(y + ch))), 4).save(OUT + f"skin_{idx:02d}.png"); idx += 1
print("skins", idx)

# --- permanentes (captura 5, tal cual, ampliada)
up(Image.open(SRC + "5.png").convert("RGB"), 3).save(OUT + "perm_full.png")

# --- trades (9 Kitsune, 10 Portal+Yeti, 11 Dragon, 13 Dark Blade); la 12 es duplicado de la 11
TRADES = {"trade_kitsune": ("9", (408, 92, 786, 124)), "trade_portal_yeti": ("10", (397, 85, 775, 112)),
          "trade_dragon": ("11", (381, 82, 750, 110)), "trade_darkblade": ("13", (392, 74, 772, 100))}
for name, (n, box) in TRADES.items():
    im = Image.open(SRC + n + ".png").convert("RGB")
    if BLUR_OTHER_PLAYERS:
        reg = im.crop(box).filter(ImageFilter.GaussianBlur(9)); im.paste(reg, box[:2])
    up(im, 2).save(OUT + name + ".png")

# --- iconos para el gancho (de la captura de permanentes y skins)
def cards(n, panels, ncol=4):
    im = Image.open(SRC + n + ".png").convert("RGB"); res = []
    for (y0, x0, h, w) in panels:
        rows = round((h + 5) / 116); gap = 5; cw = (w - 3 * gap) / 4; ch = (h - (rows - 1) * gap) / rows
        for r in range(rows):
            for c in range(4):
                x = int(x0 + c * (cw + gap)); y = int(y0 + r * (ch + gap))
                res.append(im.crop((x + 5, y + 5, int(x + cw - 5), y + int(ch * .60))))
    return res
perm = cards("5", [(18, 17, 227, 387), (298, 17, 227, 387), (577, 17, 227, 387)])
sk = cards("8", [(22, 17, 227, 387), (302, 17, 111, 387)])
for name, im in {"ico_dragon": perm[0], "ico_control": perm[1], "ico_kitsune": perm[2], "ico_magnet": perm[3], "ico_galaxy": sk[0], "ico_ember": sk[1]}.items():
    up(im, 4).save(OUT + name + ".png")
print("ok")
