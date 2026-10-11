#!/usr/bin/env python3
"""Genera index.html (composición Hyperframes) y assets/music.mp3 para el video promo.

Uso:  python3 build.py
Edita DATA / SECTIONS para cambiar productos o precios; todo lo demás se recalcula.
"""
import json, math, os, random, subprocess, html
import numpy as np
from scipy import signal
from scipy.io import wavfile

ROOT = os.path.dirname(os.path.abspath(__file__))
HANDLE = "@monzmc05"
BRAND = "MonZ Community"

# ----------------------------------------------------------------------------
# DATOS  (icono = archivo en assets/icons)
# ----------------------------------------------------------------------------
def items(prefix, rows):
    return [dict(name=n, price=p, icon=f"assets/icons/{prefix}_{i:02d}.png") for i, (n, p) in enumerate(rows)]

PERM = items("5", [
    ("Dragón", 625), ("Control", 500), ("Kitsune", 500), ("Magnet", 440), ("Yeti", 375), ("Tiger", 375),
    ("Spirit", 320), ("Gas", 315), ("Venom", 310), ("Shadow", 305), ("Dough", 300), ("T-Rex", 295),
    ("Mammoth", 295), ("Gravity", 290), ("Blizzard", 285), ("Pain", 275), ("Lightning", 265), ("Portal", 250),
    ("Phoenix", 250), ("Sound", 240), ("Spider", 225), ("Creation", 220), ("Love", 215), ("Buddha", 210),
])
FIS = items("6", [
    ("Dragón West", 360), ("Dragón East", 320), ("Magnet", 140), ("Kitsune", 100), ("Control", 55), ("Yeti", 50),
    ("Tiger", 50), ("Gas", 40), ("Dough", 35), ("T-Rex", 25), ("Venom", 20), ("Mammoth", 20),
    ("Spirit", 20), ("Gravity", 20), ("Portal", 20), ("Buddha", 20),
])
GP = items("7", [
    ("Fruit Notifier", 340), ("Dark Blade", 150), ("2x Mastery", 60), ("2x Money", 60),
    ("+1 Fruit Storage", 50), ("Fast Boats", 45), ("2x Boss Drops", 45),
])
SKINS = items("8", [
    ("Galaxy Empyrean Kitsune", 950), ("Ember Dragon", 650), ("Purple Lightbning", 550), ("Arcsteel Magnet", 350),
    ("Super Spirit Pain", 340), ("Red Lightning", 285), ("Runic Fiend Yeti", 250), ("Divine Portal", 240),
    ("Dog Blade", 210), ("Werewolf", 180), ("Fiend Yeti", 180), ("Torment Pain", 30),
])


def chunks(lst, n):
    return [lst[i:i + n] for i in range(0, len(lst), n)]


# categoría -> pantallas
SECTIONS = [
    dict(key="perm", title="FRUTAS", accent="PERMANENTES", sub="Desbloquea la fruta para siempre", screens=chunks(PERM, 6), ch=360, ih=170),
    dict(key="fis", title="FRUTAS", accent="FÍSICAS", sub="La fruta en tu inventario", screens=chunks(FIS, 6), ch=360, ih=170),
    dict(key="gp", title="GAME", accent="PASSES", sub="Mejora tu cuenta", screens=[GP], ch=250, ih=124, layout="h"),
    dict(key="skin", title="SKINS", accent="DE FRUTAS", sub="Luce único en el mar", screens=chunks(SKINS, 6), ch=360, ih=170),
]

# ----------------------------------------------------------------------------
# LÍNEA DE TIEMPO  (128 BPM, 1 unidad = 2 compases = 3.75 s)
# ----------------------------------------------------------------------------
BPM = 128
BEAT = 60 / BPM
UNIT = BEAT * 8

scenes = [dict(kind="intro", units=1)]
for s in SECTIONS:
    for i, scr in enumerate(s["screens"]):
        scenes.append(dict(kind="grid", sec=s, items=scr, page=i + 1, pages=len(s["screens"]), units=1))
scenes.append(dict(kind="outro", units=2))
t = 0.0
for sc in scenes:
    sc["start"] = round(t, 4)
    sc["dur"] = round(sc["units"] * UNIT, 4)
    t += sc["dur"]
TOTAL = round(t, 4)

# ----------------------------------------------------------------------------
# HTML
# ----------------------------------------------------------------------------
esc = html.escape

def card_html(it, sid, i, ih, ch, layout=""):
    price = f"<div class=\"price\"><span class=\"cur\">$</span>{it['price']}<span class=\"mxn\">MXN</span></div>"
    nm = f"<div class=\"nm{' sm' if len(it['name']) > 15 else ''}\">{esc(it['name'])}</div>"
    ico = f"<div class=\"ico\" style=\"height:{ih}px\"><img src=\"{it['icon']}\" alt=\"{esc(it['name'])}\"></div>"
    if layout == "h":
        body = f"{ico}<div class=\"tx\">{nm}{price}</div>"
    else:
        body = f"{ico}{nm}{price}"
    return f'''
      <div class="card{' h' if layout == 'h' else ''}" id="{sid}-c{i}" style="height:{ch}px">
        <div class="shine"></div>
        {body}
      </div>'''

def header_html(sc, sid):
    s = sc["sec"]
    pg = "".join(f'<i class="{"on" if k + 1 == sc["page"] else ""}"></i>' for k in range(sc["pages"])) if sc["pages"] > 1 else ""
    return f'''
      <div class="hd" id="{sid}-hd">
        <div class="t1"><em>{esc(s['title'])}</em><span>{esc(s['accent'])}</span></div>
        <div class="t2">{esc(s['sub'])}</div>
        <div class="dots">{pg}</div>
      </div>'''

FLAG = '<span class="flag"><i></i><i></i><i></i></span>'

parts = []
js = []
sparkle_js = []

for n, sc in enumerate(scenes):
    sid = f"s{n}"
    st, du = sc["start"], sc["dur"]
    if sc["kind"] == "grid":
        cards = "".join(card_html(it, sid, i, sc["sec"]["ih"], sc["sec"]["ch"], sc["sec"].get("layout", "")) for i, it in enumerate(sc["items"]))
        odd_last = len(sc["items"]) % 2 == 1
        parts.append(f'''
    <section class="scene clip" id="{sid}" data-start="{st}" data-duration="{du}" data-track-index="2">
      {header_html(sc, sid)}
      <div class="grid{' oddlast' if odd_last else ''}" id="{sid}-grid">{cards}
      </div>
      <div class="foot" id="{sid}-ft">{FLAG}<b>{esc(BRAND)}</b> · {HANDLE} · Precios en MXN</div>
    </section>''')
        k = len(sc["items"])
        js.append(f'''
  // ---- {sid}: {sc["sec"]["key"]} pág {sc["page"]}
  tl.fromTo("#{sid}-hd", {{opacity:0, y:-80, scale:.85}}, {{opacity:1, y:0, scale:1, duration:.55, ease:"back.out(1.7)"}}, {st + 0.05});
  tl.fromTo("#{sid}-ft", {{opacity:0, y:60}}, {{opacity:1, y:0, duration:.5, ease:"power3.out"}}, {st + 0.5});''')
        for i in range(k):
            ts = st + 0.3 + 0.13 * i
            side = -1 if i % 2 == 0 else 1
            js.append(f'''  tl.fromTo("#{sid}-c{i}", {{opacity:0, x:{side * 260}, y:90, scale:.5, rotation:{side * -8}}}, {{opacity:1, x:0, y:0, scale:1, rotation:0, duration:.6, ease:"back.out(1.5)"}}, {ts:.3f});
  tl.fromTo("#{sid}-c{i} .ico", {{scale:.8}}, {{scale:1, duration:.7, ease:"elastic.out(1,.45)"}}, {ts + 0.15:.3f});
  tl.fromTo("#{sid}-c{i} .price", {{scale:.4, opacity:0}}, {{scale:1, opacity:1, duration:.5, ease:"back.out(2.4)"}}, {ts + 0.28:.3f});
  tl.fromTo("#{sid}-c{i} .shine", {{x:-260, opacity:.9}}, {{x:620, opacity:.9, duration:.7, ease:"power2.inOut"}}, {ts + 0.7:.3f});
  tl.to("#{sid}-c{i} .ico", {{y:-9, duration:.9, yoyo:true, repeat:{max(1, int((du - (0.3 + 0.13 * i + 0.9) - 0.4) / 0.9))}, ease:"sine.inOut"}}, {ts + 0.9:.3f});''')
        js.append(f'''  tl.to("#{sid}", {{opacity:0, scale:.96, duration:.25, ease:"power2.in"}}, {st + du - 0.27:.3f});''')
        sc["pops"] = [round(st + 0.3 + 0.13 * i, 3) for i in range(k)]

    elif sc["kind"] == "intro":
        float_icons = [PERM[0], PERM[2], FIS[0], SKINS[0]]
        pos = [(60, 1500), (310, 1500), (560, 1500), (810, 1500)]
        fi = "".join(f'<div class="fl sm" id="{sid}-f{i}" style="left:{x}px;top:{y}px"><img src="{ic["icon"]}"></div>' for i, (ic, (x, y)) in enumerate(zip(float_icons, pos)))
        parts.append(f'''
    <section class="scene clip" id="{sid}" data-start="{st}" data-duration="{du}" data-track-index="2">
      {fi}
      <div class="flags" id="{sid}-flags">{FLAG}{FLAG}</div>
      <div class="crown" id="{sid}-crown"><svg viewBox="0 0 120 80"><path d="M8 70 L14 20 L40 44 L60 8 L80 44 L106 20 L112 70 Z" fill="url(#gold)" stroke="#fff3b0" stroke-width="3" stroke-linejoin="round"/></svg></div>
      <div class="big1" id="{sid}-b1">MonZ</div>
      <div class="big2" id="{sid}-b2">BLOX FRUITS</div>
      <div class="big3" id="{sid}-b3">STORE</div>
      <div class="chips" id="{sid}-chips"><span>Frutas</span><span>Gamepasses</span><span>Skins</span></div>
      <div class="from" id="{sid}-from">DESDE <b>$20</b> MXN</div>
    </section>''')
        js.append(f'''
  // ---- intro
  tl.fromTo("#{sid}-flags", {{opacity:0, y:-60}}, {{opacity:1, y:0, duration:.5, ease:"power3.out"}}, {st + 0.05});
  tl.fromTo("#{sid}-crown", {{opacity:0, y:-200, scale:.2, rotation:-25}}, {{opacity:1, y:0, scale:1, rotation:0, duration:.7, ease:"back.out(2)"}}, {st + 0.1});
  tl.fromTo("#{sid}-b1", {{opacity:0, scale:3}}, {{opacity:1, scale:1, duration:.55, ease:"expo.out"}}, {st + 0.45});
  tl.fromTo("#{sid}-b2", {{opacity:0, x:-500}}, {{opacity:1, x:0, duration:.55, ease:"power4.out"}}, {st + 0.8});
  tl.fromTo("#{sid}-b3", {{opacity:0, x:500}}, {{opacity:1, x:0, duration:.55, ease:"power4.out"}}, {st + 0.95});
  tl.fromTo("#{sid}-chips span", {{opacity:0, y:50, scale:.6}}, {{opacity:1, y:0, scale:1, duration:.4, ease:"back.out(2)", stagger:.12}}, {st + 1.4});
  tl.fromTo("#{sid}-from", {{opacity:0, scale:.3, rotation:-6}}, {{opacity:1, scale:1, rotation:-3, duration:.6, ease:"elastic.out(1,.5)"}}, {st + 1.9});
  tl.to("#{sid}-from", {{scale:1.08, duration:.23, yoyo:true, repeat:5, ease:"sine.inOut"}}, {st + 2.6});''')
        for i in range(4):
            js.append(f'''  tl.fromTo("#{sid}-f{i}", {{opacity:0, scale:.2, rotation:{-30 if i % 2 else 30}}}, {{opacity:1, scale:1, rotation:{8 if i % 2 else -8}, duration:.6, ease:"back.out(2)"}}, {st + 0.7 + 0.12 * i:.3f});
  tl.to("#{sid}-f{i}", {{y:-24, duration:.9, yoyo:true, repeat:2, ease:"sine.inOut"}}, {st + 1.4 + 0.12 * i:.3f});''')
        js.append(f'''  tl.to("#{sid}", {{opacity:0, scale:1.06, duration:.25, ease:"power2.in"}}, {st + du - 0.27:.3f});''')
        sc["pops"] = [round(st + 0.45, 3), round(st + 0.8, 3), round(st + 0.95, 3), round(st + 1.9, 3)]

    else:  # outro
        wall = [PERM[0], PERM[2], SKINS[0], SKINS[1], PERM[5], FIS[0], PERM[1]]
        pos = [(60, 170), (310, 170), (560, 170), (810, 170), (185, 350), (435, 350), (685, 350)]
        fi = "".join(f'<div class="fl sm" id="{sid}-f{i}" style="left:{x}px;top:{y}px"><img src="{ic["icon"]}"></div>' for i, (ic, (x, y)) in enumerate(zip(wall, pos)))
        parts.append(f'''
    <section class="scene clip" id="{sid}" data-start="{st}" data-duration="{du}" data-track-index="2">
      {fi}
      <div class="o1" id="{sid}-o1">¿LISTO PARA<br><span>COMPRAR?</span></div>
      <div class="o2" id="{sid}-o2">Escríbeme por DM<br>o entra al link de mi bio</div>
      <div class="cta" id="{sid}-cta">¡ESCRÍBEME YA!</div>
      <div class="handle" id="{sid}-hdl">{FLAG}<b>{esc(BRAND)}</b><br>{HANDLE}</div>
      <div class="o3" id="{sid}-o3">Todos los precios en pesos mexicanos (MXN)</div>
    </section>''')
        js.append(f'''
  // ---- outro
  tl.fromTo("#{sid}-o1", {{opacity:0, scale:2.4}}, {{opacity:1, scale:1, duration:.6, ease:"expo.out"}}, {st + 0.1});
  tl.fromTo("#{sid}-o2", {{opacity:0, y:60}}, {{opacity:1, y:0, duration:.5, ease:"power3.out"}}, {st + 0.8});
  tl.fromTo("#{sid}-cta", {{opacity:0, scale:.2}}, {{opacity:1, scale:1, duration:.7, ease:"elastic.out(1,.5)"}}, {st + 1.4});
  tl.to("#{sid}-cta", {{scale:1.07, duration:.234, yoyo:true, repeat:{int((du - 2.3) / 0.234)}, ease:"sine.inOut"}}, {st + 2.2});
  tl.fromTo("#{sid}-hdl", {{opacity:0, y:50}}, {{opacity:1, y:0, duration:.5, ease:"power3.out"}}, {st + 1.9});
  tl.fromTo("#{sid}-o3", {{opacity:0}}, {{opacity:.85, duration:.5}}, {st + 2.4});''')
        for i in range(7):
            js.append(f'''  tl.fromTo("#{sid}-f{i}", {{opacity:0, scale:.2, rotation:{-25 if i % 2 else 25}}}, {{opacity:1, scale:1, rotation:{6 if i % 2 else -6}, duration:.6, ease:"back.out(2)"}}, {st + 0.3 + 0.1 * i:.3f});
  tl.to("#{sid}-f{i}", {{y:-22, duration:.95, yoyo:true, repeat:{int((du - 1.9) / 0.95)}, ease:"sine.inOut"}}, {st + 1.3 + 0.1 * i:.3f});''')
        sc["pops"] = [round(st + 0.1, 3), round(st + 1.4, 3)] + [round(st + 0.3 + 0.1 * i, 3) for i in range(7)]

# chispas de fondo persistentes
rnd = random.Random(7)
spark_html = []
for i in range(34):
    x = rnd.randint(0, 1060); sz = rnd.choice([6, 8, 10, 14]); d = rnd.uniform(7, 13); dl = rnd.uniform(0, 8)
    spark_html.append(f'<i class="sp" id="sp{i}" style="left:{x}px;width:{sz}px;height:{sz}px"></i>')
    reps = int(TOTAL / d) + 1
    sparkle_js.append(f'  tl.fromTo("#sp{i}", {{y:2000, opacity:.0, scale:.6}}, {{y:-120, opacity:.9, scale:1.1, duration:{d:.2f}, repeat:{reps}, ease:"none"}}, {dl:.2f});')

css = open(os.path.join(ROOT, "style.css")).read()

doc = f'''<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=1080, height=1920">
<title>Promo MonZ - Blox Fruits</title>
<style>
{css}
</style>
</head>
<body>
<div id="root" data-composition-id="root" data-width="1080" data-height="1920" data-start="0" data-duration="{TOTAL}">
  <svg width="0" height="0" style="position:absolute"><defs><linearGradient id="gold" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff0a0"/><stop offset=".5" stop-color="#ffc400"/><stop offset="1" stop-color="#d98200"/></linearGradient></defs></svg>
  <div class="bg"></div>
  <div class="beam b1" id="beam1"></div>
  <div class="beam b2" id="beam2"></div>
  <div class="vig"></div>
  <div class="sparks">{"".join(spark_html)}</div>
  <div class="mark" id="wm">MonZ</div>
  {"".join(parts)}
  <audio id="music" src="assets/music.mp3" data-start="0" data-duration="{TOTAL}" data-track-index="1" data-volume="0.9" data-fade-out="1.2"></audio>
</div>
<script src="assets/vendor/gsap.min.js"></script>
<script>
(function () {{
  const tl = gsap.timeline({{ paused: true }});
  tl.set(".scene", {{ transformOrigin: "50% 50%" }}, 0);
  tl.fromTo("#beam1", {{ rotation: -35 }}, {{ rotation: 35, duration: {TOTAL}, ease: "none" }}, 0);
  tl.fromTo("#beam2", {{ rotation: 40 }}, {{ rotation: -30, duration: {TOTAL}, ease: "none" }}, 0);
{chr(10).join(sparkle_js)}
{"".join(js)}
  window.__timelines = window.__timelines || {{}};
  window.__timelines["root"] = tl;
}})();
</script>
</body>
</html>
'''
open(os.path.join(ROOT, "index.html"), "w").write(doc)

# ----------------------------------------------------------------------------
# MÚSICA  (síntesis propia: sin copyright)
# ----------------------------------------------------------------------------
SR = 44100
N = int((TOTAL + 1.5) * SR)
mix = np.zeros(N)
rng = np.random.default_rng(3)

def add(buf, start, sig, gain=1.0):
    i = int(start * SR)
    if i >= len(buf): return
    sig = sig[: len(buf) - i]
    buf[i:i + len(sig)] += sig * gain

def tt(d): return np.arange(int(d * SR)) / SR
def noise(d): return rng.standard_normal(int(d * SR))
def hp(x, f): return signal.lfilter(*signal.butter(2, f / (SR / 2), "high"), x)
def lp(x, f): return signal.lfilter(*signal.butter(2, f / (SR / 2), "low"), x)
def bp(x, a, b): return signal.lfilter(*signal.butter(2, [a / (SR / 2), b / (SR / 2)], "band"), x)

def kick():
    t = tt(.32); f = 45 + 110 * np.exp(-t * 28)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9) * 1.0
def clap():
    t = tt(.22); n = bp(noise(.22), 900, 3500)
    env = np.exp(-t * 22) + .6 * np.exp(-((t - .012) ** 2) * 40000) + .5 * np.exp(-((t - .026) ** 2) * 40000)
    return n * env * 0.9
def hat(d=.06, g=.35):
    return hp(noise(d), 7000) * np.exp(-tt(d) * 70) * g
def bass(f, d):
    t = tt(d); s = signal.sawtooth(2 * np.pi * f * t) * .6 + np.sin(2 * np.pi * f * t) * .6
    return lp(s, 420) * np.minimum(1, t * 200) * np.exp(-t * 3.2)
def pluck(f, d=.22):
    t = tt(d); s = (signal.square(2 * np.pi * f * t, .35) * .5 + signal.sawtooth(2 * np.pi * f * 1.004 * t) * .5)
    return lp(s, 2600) * np.exp(-t * 14) * np.minimum(1, t * 400)
def pad(freqs, d):
    t = tt(d); s = sum(np.sin(2 * np.pi * f * t) + .5 * np.sin(2 * np.pi * f * 2.003 * t) for f in freqs)
    env = np.minimum(1, t * 6) * np.minimum(1, (d - t) * 6)
    return lp(s, 1800) * env / len(freqs)
def whoosh(d=1.0):
    t = tt(d); n = noise(d)
    out = np.zeros_like(n); chunk = 2048
    for k in range(0, len(n), chunk):
        fc = 300 + 7000 * (k / len(n)) ** 2
        b, a = signal.butter(2, [fc / (SR / 2) * .7, min(.98, fc / (SR / 2) * 1.5)], "band")
        out[k:k + chunk] = signal.lfilter(b, a, n[k:k + chunk])
    return out * (t / d) ** 1.6 * 1.6
def boom():
    t = tt(.9); return np.sin(2 * np.pi * (38 + 60 * np.exp(-t * 6)) * t) * np.exp(-t * 3.5) * 1.1
def pop(f=900):
    t = tt(.11); return np.sin(2 * np.pi * np.cumsum(f * np.exp(-t * 11)) / SR) * np.exp(-t * 28) * .5
def coin():
    t = tt(.35); return (np.sin(2 * np.pi * 1320 * t) + np.sin(2 * np.pi * 1760 * t)) * np.exp(-t * 9) * .22

def midi(n): return 440 * 2 ** ((n - 69) / 12)
# Am - F - C - G
prog = [(57, [57, 60, 64]), (53, [53, 57, 60]), (48, [48, 52, 55]), (55, [55, 59, 62])]
arp_pat = [0, 1, 2, 1, 2, 1, 0, 2]   # sobre acordes, corcheas
nbeats = int(TOTAL / BEAT) + 4
duck = np.ones(N)
total_bars = int(nbeats / 4) + 1
for beat in range(nbeats):
    tb = beat * BEAT
    bar = beat // 4; root, ch = prog[bar % 4]
    lvl = 1.0
    if bar >= 1:  # bombo desde el compás 2
        add(mix, tb, kick(), .95)
        i0 = int(tb * SR); i1 = min(N, i0 + int(.18 * SR))
        duck[i0:i1] = np.minimum(duck[i0:i1], np.linspace(.25, 1, i1 - i0) ** 1.3)
    if beat % 4 in (1, 3) and bar >= 1: add(mix, tb, clap(), .5)
    add(mix, tb + BEAT / 2, hat(), 1.0)
    if bar >= 2:
        add(mix, tb + BEAT / 4, hat(.04, .2)); add(mix, tb + 3 * BEAT / 4, hat(.04, .2))
    # bajo en contratiempo
    if bar >= 1:
        add(mix, tb + BEAT / 2, bass(midi(root - 12), BEAT * .45), .55)
    # arpegio
    for k in range(2):
        idx = arp_pat[(beat * 2 + k) % 8]
        add(mix, tb + k * BEAT / 2, pluck(midi(ch[idx] + 12), .2), .22 if bar >= 1 else .14)
    if beat % 4 == 0:
        add(mix, tb, pad([midi(n + 12) for n in ch], BEAT * 4), .16)

# efectos alineados con la animación
for sc in scenes:
    s = sc["start"]
    if s > 0: add(mix, s - 0.9, whoosh(.9), .5)
    add(mix, s, boom(), .8)
    for i, p in enumerate(sc["pops"]):
        add(mix, p + .15, pop(700 + 40 * (i % 6)), .7)
        if sc["kind"] == "grid": add(mix, p + .4, coin(), .5)

mix *= duck * 0.55 + 0.45 * 1  # sidechain ligero sobre todo
# el sidechain debe afectar a bajo/pad/arp más que a bombo: aproximación suave
mix = np.tanh(mix * 1.1)
fade = int(1.3 * SR); mix[int(TOTAL * SR):] = 0
mix[int(TOTAL * SR) - fade:int(TOTAL * SR)] *= np.linspace(1, 0, fade)
mix = mix[: int(TOTAL * SR)]
mix = mix / np.max(np.abs(mix)) * .89
wav = os.path.join(ROOT, "assets", "music.wav")
wavfile.write(wav, SR, (mix * 32767).astype(np.int16))
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-codec:a", "libmp3lame", "-q:a", "2", os.path.join(ROOT, "assets", "music.mp3")], check=True)
os.remove(wav)
json.dump([{k: v for k, v in sc.items() if k in ("kind", "start", "dur")} for sc in scenes], open(os.path.join(ROOT, "timeline.json"), "w"), indent=1)
print(f"OK · {len(scenes)} escenas · {TOTAL}s")
