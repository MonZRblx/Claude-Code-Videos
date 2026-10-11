#!/usr/bin/env python3
"""Trades (capturas 23–27): quita el número blanco de la cuenta regresiva y difumina los nombres de los otros jugadores (MonZ queda visible)."""
import os, numpy as np, cv2
from PIL import Image
ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = "/tmp/claude-0/-home-user-Claude-Code-Videos/d7eef31e-54e1-596e-a9cb-13062292304f/images/"
OUT = os.path.join(ROOT, "assets/trades/"); os.makedirs(OUT, exist_ok=True)
# imagen: (archivo, caja del número [x0,y0,x1,y1], caja del nombre del otro jugador [x0,y0,x1,y1])
T = [("kitsune", 23, (360, 190, 450, 405), (545, 94, 645, 124)),
     ("portal_yeti", 24, (355, 180, 440, 395), (560, 86, 612, 113)),
     ("portal_bran", 25, (335, 235, 405, 315), (515, 76, 590, 104)),
     ("dragon", 26, (362, 248, 400, 322), (528, 82, 600, 110)),
     ("darkblade", 27, (350, 170, 435, 385), (555, 76, 612, 100))]
for name, n, nb, pb in T:
    im = cv2.cvtColor(np.array(Image.open(SRC + f"{n}.png").convert("RGB")), cv2.COLOR_RGB2BGR)
    x0, y0, x1, y1 = nb
    reg = im[y0:y1, x0:x1].astype(int)
    sat = reg.max(2) - reg.min(2)
    white = ((reg.min(2) > 150) & (sat < 25)).astype(np.uint8)
    mask = np.zeros(im.shape[:2], np.uint8); mask[y0:y1, x0:x1] = white
    mask = cv2.dilate(mask, np.ones((3, 3), np.uint8), iterations=2)
    im = cv2.inpaint(im, mask, 7, cv2.INPAINT_TELEA)
    x0, y0, x1, y1 = pb
    r = im[y0:y1, x0:x1]
    small = cv2.resize(r, (max(2, (x1 - x0) // 10), max(2, (y1 - y0) // 8)), interpolation=cv2.INTER_AREA)
    r2 = cv2.resize(small, (x1 - x0, y1 - y0), interpolation=cv2.INTER_NEAREST)
    im[y0:y1, x0:x1] = cv2.GaussianBlur(r2, (0, 0), 3)
    if name == "portal_bran": im = im[:578]   # quita la fila de píxeles sueltos del borde inferior de la captura
    Image.fromarray(cv2.cvtColor(im, cv2.COLOR_BGR2RGB)).resize((im.shape[1] * 2, im.shape[0] * 2), Image.LANCZOS).save(OUT + name + ".png")
print("trades ok")
