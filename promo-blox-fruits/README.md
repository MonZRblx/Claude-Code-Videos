# Promo MonZ · Blox Fruits (TikTok vertical 1080×1920)

Video hecho con [Hyperframes](https://hyperframes.dev) (HTML + GSAP → MP4).

- `out/promo-blox-fruits.mp4` — video final (48.8 s, 30 fps, con música).
- `build.py` — **fuente de verdad**: productos, precios, orden de escenas, animaciones y música sintetizada (sin copyright).
- `style.css` — diseño. `index.html` y `assets/music.mp3` se generan con `python3 build.py`.

## Cambiar precios o productos
1. Edita las listas `PERM`, `FIS`, `GP`, `SKINS` al inicio de `build.py`.
2. `python3 build.py`
3. `npx hyperframes render -o out/promo-blox-fruits.mp4`

Los iconos están recortados de tus capturas (`assets/icons`, prefijo = número de imagen, orden de izquierda a derecha y de arriba a abajo).
