# Promo MonZ v3 · Showreel (TikTok 1080×1920, 30 fps, 30.0 s, sin voz, en bucle)

Hyperframes: una composición por escena en `compositions/` (+ fondo, HUD y transiciones).

- `out/promo-monz-v3.mp4` — video final (música + efectos, sin narrador, sin emojis).
- `prep_tiles.py` — extrae las tarjetas ORIGINALES completas (fondo, borde, ícono, nombre y precio) de las capturas 14/18/20/21, sin modificarlas (solo recorte exterior + ampliación con Lanczos).
- `prep_trades.py` (en v2) — las ventanas de trade ya procesadas están en `assets/trades/` (sin número gigante, nombres ajenos difuminados, MonZ visible).
- `build.py` — línea de tiempo, escenas, animaciones y eventos de sonido. `audio.py` — música trap/gamer sintetizada (bucle) y efectos.

## Regenerar
```
pip install scipy numpy pillow
python3 prep_tiles.py && python3 build.py
npx hyperframes render -o out/promo-monz-v3.mp4
```
