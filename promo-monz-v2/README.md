# Promo MonZ v2 · Tienda (TikTok 1080×1920, 30 fps, 44.2 s, SIN voz)

Hyperframes: una composición por escena y por bloque de piezas en `compositions/` (+ fondo, HUD y transiciones).

- `out/promo-monz.mp4` — video final (música + efectos, sin narrador).
- `data.py` — catálogo exacto de los 65 objetos (nombres y precios tal como en tus capturas 14–22) y cómo se dividen en bloques.
- `prep_pieces.py` — recorta cada objeto: ícono limpio (sin fondo cuadrado) con contorno tipo sticker.
- `prep_trades.py` — trades: quita el número de la cuenta regresiva y difumina los nombres de otros jugadores (MonZ visible).
- `build.py` — línea de tiempo (a compases de 138.5 BPM), escenas, animaciones y eventos de sonido. `audio.py` — música trap/gamer sintetizada y efectos.

## Regenerar
```
pip install scipy numpy pillow opencv-python-headless
python3 prep_pieces.py && python3 prep_trades.py && python3 build.py
npx hyperframes render -o out/promo-monz.mp4
```
Para cambiar un precio o nombre: edita `data.py` (y vuelve a ejecutar los 3 pasos).
