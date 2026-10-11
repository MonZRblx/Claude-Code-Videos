# Promo MonZ · Skins y Físicas (TikTok 1080×1920, 30 fps, 33 s)

Hecho con Hyperframes: una composición por escena en `compositions/` (+ fondo, HUD, subtítulos y transiciones).

- `out/promo-skins-fisicas.mp4` — video final.
- `build.py` — línea de tiempo, escenas y animaciones (GSAP). La voz marca la duración; las escenas caen en tiempos de compás.
- `audio.py` — música trap/gamer sintetizada (sin copyright), efectos y mezcla con ducking bajo la voz.
- `gen_voice.py` — narrador (Kokoro-82M, voz `em_alex`). Guion en la lista `SEGS`.
- `prep_assets.py` — recorta/amplía las capturas originales (sin alterar su contenido). `BLUR_OTHER_PLAYERS=True` difumina nombres de otros jugadores en los trades.

## Regenerar
```
pip install kokoro-onnx soundfile scipy numpy pillow
python3 prep_assets.py && python3 gen_voice.py && python3 build.py
npx hyperframes render -o out/promo-skins-fisicas.mp4
```
Para añadir un trade: guarda la captura como `assets/captures/trade_<nombre>.png` y vuelve a ejecutar `build.py`
(la de Portal vs Bran debe llamarse `trade_portal_bran.png`).
