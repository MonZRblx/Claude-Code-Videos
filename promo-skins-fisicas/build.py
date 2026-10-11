#!/usr/bin/env python3
"""Promo MonZ · Skins y Físicas (TikTok 1080x1920, 30 fps).

Genera una composición Hyperframes por escena (compositions/*.html), index.html y el audio mezclado.
Pasos:  python3 prep_assets.py && python3 gen_voice.py && python3 build.py
        npx hyperframes render -o out/promo-skins-fisicas.mp4
"""
import json, os, random, html, glob
ROOT = os.path.dirname(os.path.abspath(__file__))
os.makedirs(os.path.join(ROOT, "compositions"), exist_ok=True)
HANDLE = "@monzmc05"

# ----------------------------------------------------------------------------------------------
# LÍNEA DE TIEMPO (las escenas caen en tiempos de compás; la voz manda la duración)
# ----------------------------------------------------------------------------------------------
voice = json.load(open(os.path.join(ROOT, "voice.json")))
D = {v["id"]: v["dur"] for v in voice}
SUBTXT = {v["id"]: v["sub"] for v in voice}
BPM = 132
BEAT = 60 / BPM
snap = lambda t: round(round(t / BEAT) * BEAT, 3)

S1 = 0.0
v = {}
v["g1"] = 0.32
S2 = snap(v["g1"] + D["g1"] + 0.05)
v["g2"] = S2 + 0.30
S3 = snap(max(S2 + 3.0, v["g2"] + D["g2"] + 0.45))
v["s1"] = S3 + 0.45
S4 = snap(S3 + 5.0)
v["f1"] = S4 + 0.22
S5 = snap(S4 + 6.9)
v["t1"] = S5 + 0.25
v["t2"] = v["t1"] + D["t1"] + 0.10
v["t3"] = v["t2"] + D["t2"] + 0.10
S6 = snap(max(S5 + 6.0, v["t3"] + D["t3"] + 0.30))
v["m1"] = S6 + 0.28
v["c1"] = v["m1"] + D["m1"] + 0.14
v["c2"] = v["c1"] + D["c1"] + 0.10
END = round(v["c2"] + D["c2"] + 0.95, 2)
TOTAL = END
SC = [("s1", S1, S2), ("s2", S2, S3), ("s3", S3, S4), ("s4", S4, S5), ("s5", S5, S6), ("s6", S6, END)]
DUR = {k: round(b - a, 3) for k, a, b in SC}
START = {k: a for k, a, b in SC}
print("escenas:", {k: (round(a, 2), round(b - a, 2)) for k, a, b in SC}, "total", TOTAL)
assert 30 <= TOTAL <= 35.2, TOTAL

EV = []  # eventos de sonido (t, tipo, volumen)
def sfx(t, kind, vol=1.0): EV.append((round(t, 3), kind, vol))

# ----------------------------------------------------------------------------------------------
# utilidades de plantilla
# ----------------------------------------------------------------------------------------------
def comp(cid, dur, inner, js, data=None):
    js = js.replace("__D__", json.dumps(data if data is not None else {}, ensure_ascii=False))
    return ('<template id="%s-template">\n<div data-composition-id="%s" data-width="1080" data-height="1920" data-start="0" data-duration="%s">\n%s\n<script>\n(function () {\n'
            '  const tl = gsap.timeline({ paused: true });\n  const D = __DATA__;\n%s\n  window.__timelines = window.__timelines || {};\n  window.__timelines["%s"] = tl;\n})();\n</script>\n</div>\n</template>\n'
            % (cid, cid, dur, inner, js, cid)).replace("__DATA__", json.dumps(data if data is not None else {}, ensure_ascii=False))

def write(name, text): open(os.path.join(ROOT, "compositions", name + ".html"), "w").write(text)
def gt(text, kind): # texto con degradado + contorno negro grueso (+ brillo animable)
    return '<span class="gtw"><span class="o">%s</span><span class="f %s">%s</span></span>' % (text, kind, text)
def mask(inner): return '<span class="mask"><span class="rv" style="display:inline-block">%s</span></span>' % inner
def sparks(prefix, n, seed, kinds=""):
    r = random.Random(seed)
    return "".join('<i class="sp %s" id="%s%d" style="left:%dpx;width:%dpx;height:%dpx"></i>' % (kinds, prefix, i, r.randint(0, 1060), s, s)
                   for i in range(n) for s in [r.choice([6, 8, 10, 14, 18])])

# ----------------------------------------------------------------------------------------------
# FONDO PERMANENTE (fibra de carbono, rayos, polvo dorado)
# ----------------------------------------------------------------------------------------------
r = random.Random(5)
dust = [dict(d=round(r.uniform(7, 14), 2), dl=round(r.uniform(0, 6), 2)) for _ in range(34)]
write("bg", comp("bg", TOTAL,
    '<div class="carbon" id="bg-carbon"></div><div class="haze"></div><div class="beam" id="bg-b1"></div><div class="beam b2" id="bg-b2"></div>' + sparks("bgs", 34, 5),
    '''
  tl.fromTo("#bg-carbon", { x: 0, y: 0 }, { x: -120, y: -160, duration: %s, ease: "none" }, 0);
  tl.fromTo("#bg-b1", { rotation: -35 }, { rotation: 35, duration: %s, ease: "none" }, 0);
  tl.fromTo("#bg-b2", { rotation: 40 }, { rotation: -30, duration: %s, ease: "none" }, 0);
  D.dust.forEach((o, i) => tl.fromTo("#bgs" + i, { y: 2000, opacity: 0, scale: .6 }, { y: -120, opacity: .95, scale: 1.1, duration: o.d, repeat: Math.ceil(%s / o.d), ease: "none" }, o.dl));
''' % (TOTAL, TOTAL, TOTAL, TOTAL), dict(dust=dust)))

# ----------------------------------------------------------------------------------------------
# HUD PERMANENTE (banderas, etiqueta México, usuario)
# ----------------------------------------------------------------------------------------------
write("hud", comp("hud", TOTAL,
    '<div class="hud-flag" id="hud-fl" style="left:26px">🇲🇽</div><div class="hud-flag" id="hud-fr" style="right:26px">🇲🇽</div>'
    '<div class="hud-label" id="hud-lb">VENTA SOLO PARA <b>MÉXICO</b> 🇲🇽<div class="hud-shine" id="hud-sh"></div></div>'
    '<div class="hud-handle" id="hud-hd"><span>%s</span></div>' % HANDLE,
    '''
  tl.fromTo("#hud-fl", { y: -160, rotation: -30, opacity: 0 }, { y: 0, rotation: 0, opacity: 1, duration: .6, ease: "back.out(2)" }, .15);
  tl.fromTo("#hud-fr", { y: -160, rotation: 30, opacity: 0 }, { y: 0, rotation: 0, opacity: 1, duration: .6, ease: "back.out(2)" }, .25);
  tl.fromTo("#hud-lb", { scale: .3, opacity: 0 }, { scale: 1, opacity: 1, duration: .55, ease: "back.out(2.2)" }, .35);
  tl.fromTo("#hud-hd", { y: 60, opacity: 0 }, { y: 0, opacity: 1, duration: .5, ease: "power3.out" }, .6);
  tl.to("#hud-fl", { rotation: 5, duration: .9, yoyo: true, repeat: Math.ceil(D.total / .9), ease: "sine.inOut" }, 1);
  tl.to("#hud-fr", { rotation: -5, duration: .9, yoyo: true, repeat: Math.ceil(D.total / .9), ease: "sine.inOut" }, 1.2);
  for (let t = 1.6; t < D.total; t += 2.6) tl.fromTo("#hud-sh", { x: -120, opacity: .9 }, { x: 860, opacity: .9, duration: .6, ease: "power2.inOut" }, t);
''', dict(total=TOTAL)))

# ----------------------------------------------------------------------------------------------
# SUBTÍTULOS palabra por palabra (dorado con borde negro, rebote en la palabra activa)
# ----------------------------------------------------------------------------------------------
chunks = []
for sid in ["g1", "g2", "s1", "f1", "t1", "t2", "t3", "m1", "c1", "c2"]:
    words = SUBTXT[sid].split()
    w = [len(x.strip(".,:;!?¡¿")) + 1 + (3 if x[-1] in ".,:;!?" else 0) for x in words]
    t0 = v[sid] + 0.02; span = D[sid] - 0.08; tot = sum(w); acc = 0; timed = []
    for x, wt in zip(words, w):
        timed.append((x, round(t0 + span * acc / tot, 3), round(t0 + span * (acc + wt) / tot, 3))); acc += wt
    cur = []; chars = 0
    for x in timed:
        if cur and chars + len(x[0]) > 17:
            chunks.append(cur); cur = []; chars = 0
        cur.append(x); chars += len(x[0]) + 1
    if cur: chunks.append(cur)
sub_html = "".join('<div class="sub" id="sub%d">%s</div>' % (i, "".join('<span class="sw" id="sw%d_%d">%s</span>' % (i, j, html.escape(x[0])) for j, x in enumerate(c))) for i, c in enumerate(chunks))
sub_data = [[dict(t=x[1], e=x[2]) for x in c] for c in chunks]
write("subs", comp("subs", TOTAL, sub_html, '''
  D.chunks.forEach((c, i) => {
    const first = c[0].t, last = c[c.length - 1].e;
    const nxt = D.chunks[i + 1] ? D.chunks[i + 1][0].t - .03 : 1e9;
    tl.set("#sub" + i, { opacity: 1 }, Math.max(0, first - .02));
    tl.set("#sub" + i, { opacity: 0 }, Math.min(last + .22, nxt));
    c.forEach((w, j) => {
      const id = "#sw" + i + "_" + j;
      tl.fromTo(id, { opacity: 0, scale: .55, y: 24 }, { opacity: 1, scale: 1.3, y: 0, duration: .09, ease: "power2.out" }, w.t);
      tl.to(id, { scale: 1, duration: .16, ease: "back.out(2.4)" }, w.t + .09);
    });
  });
''', dict(chunks=sub_data)))

# ----------------------------------------------------------------------------------------------
# ESCENA 1 · GANCHO  (negro → explosión dorada, kinetic typography + glitch, adelanto de objetos)
# ----------------------------------------------------------------------------------------------
LINES = [["¿SKINS", "Y"], ["FÍSICAS"], ["BARATAS", "Y"], ["100%"], ["CONFIABLES?"]]
def s1_text(cls, idn):
    out = '<div class="s1txt %s" id="%s">' % (cls, idn)
    for ln in LINES:
        out += '<span class="ln">' + " ".join('<span class="w"><span class="wi">%s</span></span>' % w for w in ln) + "</span>"
    return out + '<span class="ln"><span class="w"><span class="wi em">😱🔥</span></span></span></div>'
ico = [("ico_dragon", 300, 1, .72), ("ico_galaxy", 1245, -1, .9), ("ico_kitsune", 420, -1, 1.1), ("ico_ember", 1135, 1, 1.28), ("ico_magnet", 330, 1, 1.5), ("ico_control", 1255, -1, 1.68)]
write("scene-1", comp("scene-1", DUR["s1"],
    '<div class="scn" id="s1"><div class="fill" id="s1-black" style="background:#000"></div><div class="s1gold" id="s1-gold"></div><div class="s1rays" id="s1-rays"></div>'
    '<div class="fill" id="s1-cam">' + "".join('<div class="icc" id="s1-i%d" style="left:0;top:%dpx"><img src="assets/captures/%s.png"></div>' % (i, o[1], o[0]) for i, o in enumerate(ico)) +
    s1_text("gl m", "s1-m") + s1_text("gl c", "s1-c") + s1_text("main", "s1-t") +
    '</div><div class="fill" id="s1-white" style="background:#fff;opacity:0"></div></div>',
    '''
  tl.to("#s1-black", { opacity: 0, duration: .01 }, .12);
  tl.fromTo("#s1-white", { opacity: 0 }, { opacity: 1, duration: .04, ease: "none" }, .1);
  tl.to("#s1-white", { opacity: 0, duration: .3, ease: "power2.out" }, .15);
  tl.fromTo("#s1-gold", { scale: 0 }, { scale: 6, duration: .6, ease: "expo.out" }, .12);
  tl.fromTo("#s1-rays", { rotation: 0, opacity: 0 }, { rotation: 40, opacity: .55, duration: D.dur, ease: "none" }, .12);
  tl.fromTo("#s1-cam", { scale: .8 }, { scale: 1.13, duration: D.dur - .1, ease: "power2.in" }, 0);
  ["#s1-m", "#s1-c", "#s1-t"].forEach(L => document.querySelectorAll(L + " .wi").forEach((el, i) =>
    tl.fromTo(el, { y: 300, scale: 3, opacity: 0, rotation: i % 2 ? 10 : -10 }, { y: 0, scale: 1, opacity: 1, rotation: 0, duration: .34, ease: "back.out(1.6)" }, .32 + i * .115)));
  D.glitch.forEach(t => {
    tl.to("#s1-m", { x: -18, y: 6, duration: .05, yoyo: true, repeat: 5, ease: "none" }, t);
    tl.to("#s1-c", { x: 18, y: -6, duration: .05, yoyo: true, repeat: 5, ease: "none" }, t);
    tl.to("#s1-t", { x: 6, skewX: -6, duration: .05, yoyo: true, repeat: 3, ease: "none" }, t);
  });
  D.ico.forEach((o, i) => tl.fromTo("#s1-i" + i, { x: o.dir > 0 ? -420 : 1500, rotation: o.dir > 0 ? -8 : 8, skewX: o.dir > 0 ? -16 : 16 },
    { x: o.dir > 0 ? 1500 : -420, duration: .55, ease: "power1.inOut" }, o.t));
''', dict(dur=DUR["s1"], glitch=[.95, 1.45, 1.95], ico=[dict(dir=o[2], t=o[3]) for o in ico])))
sfx(S1 + .12, "boom", 1.0); sfx(S1 + .1, "slam", .7)
for i in range(sum(len(l) for l in LINES) + 1): sfx(S1 + .32 + i * .115 + .12, "slam", .5)
for t in (.95, 1.45, 1.95): sfx(S1 + t, "glitch", .55)
for o in ico: sfx(S1 + o[3] + .1, "whoosh_fast", .45)

# ----------------------------------------------------------------------------------------------
# ESCENA 2 · PRESENTACIÓN (título con máscara y brillo, banderas, lluvia de partículas)
# ----------------------------------------------------------------------------------------------
rr = random.Random(11)
rain = [dict(x=rr.randint(0, 1060), s=rr.choice([6, 9, 12, 16]), t=round(rr.uniform(0, 1.8), 2), d=round(rr.uniform(1.2, 2.2), 2)) for _ in range(46)]
write("scene-2", comp("scene-2", DUR["s2"],
    '<div class="scn" id="s2"><div class="fill" id="s2-glow" style="background:linear-gradient(180deg, rgba(255,194,26,.35), rgba(0,0,0,.25) 60%, rgba(0,0,0,.5))"></div>'
    '<div class="beam" id="s2-beam"></div>' +
    "".join('<i class="sp" id="s2r%d" style="left:%dpx;width:%dpx;height:%dpx"></i>' % (i, o["x"], o["s"], o["s"]) for i, o in enumerate(rain)) +
    '<div class="s2title" id="s2-title"><span class="l1">%s %s</span><span class="l2">%s</span></div>' % (mask(gt("SKINS", "sk")), mask(gt("Y", "wh")), mask(gt("FÍSICAS", "fi"))) +
    '<div class="bigflag" id="s2-fl" style="left:16px">🇲🇽</div><div class="bigflag" id="s2-fr" style="right:16px">🇲🇽</div>'
    '<div class="mxpill" id="s2-mx">SOLO <b>MÉXICO</b> 🇲🇽</div></div>',
    '''
  tl.fromTo("#s2-beam", { rotation: -30 }, { rotation: 20, duration: D.dur, ease: "none" }, 0);
  document.querySelectorAll("#s2-title .rv").forEach((el, i) => tl.fromTo(el, { y: 280 }, { y: 0, duration: .55, ease: "expo.out" }, .14 + i * .17));
  document.querySelectorAll("#s2-title .f").forEach((el, i) => tl.fromTo(el, { backgroundPosition: "160% 0, 0 0" }, { backgroundPosition: "-60% 0, 0 0", duration: .95, ease: "power2.inOut" }, .72 + i * .2));
  tl.fromTo("#s2-fl", { x: -300, opacity: 0, rotation: -25 }, { x: 0, opacity: 1, rotation: 0, duration: .6, ease: "back.out(1.8)" }, .3);
  tl.fromTo("#s2-fr", { x: 300, opacity: 0, rotation: 25 }, { x: 0, opacity: 1, rotation: 0, duration: .6, ease: "back.out(1.8)" }, .38);
  tl.to("#s2-fl", { y: -14, duration: .5, yoyo: true, repeat: 5, ease: "sine.inOut" }, .95);
  tl.to("#s2-fr", { y: -14, duration: .5, yoyo: true, repeat: 5, ease: "sine.inOut" }, 1.05);
  tl.fromTo("#s2-mx", { y: 90, opacity: 0, scale: .6 }, { y: 0, opacity: 1, scale: 1, duration: .5, ease: "back.out(2)" }, .95);
  D.rain.forEach((o, i) => tl.fromTo("#s2r" + i, { y: -100, opacity: 1 }, { y: 2000, opacity: 1, duration: o.d, ease: "none" }, o.t));
  tl.to(["#s2-fl", "#s2-fr", "#s2-mx"], { opacity: 0, scale: .6, duration: .25, ease: "power2.in" }, D.dur - .62);
  tl.to("#s2-title", { scale: 9, opacity: 0, duration: .55, ease: "power3.in" }, D.dur - .55);
''', dict(dur=DUR["s2"], rain=rain)))
sfx(S2 + .14, "whoosh_up", .55); sfx(S2 + .30, "pop", .8); sfx(S2 + .38, "pop", .8); sfx(S2 + .95, "pop", .9); sfx(S2 + .78, "shine", .6); sfx(S2 + .98, "shine", .5)
sfx(S2 + DUR["s2"] - .62, "whoosh_zoom", .8)

# ----------------------------------------------------------------------------------------------
# ESCENA 3 · SKINS (cascada con rebote, parallax, aro de luz + moneda)
# ----------------------------------------------------------------------------------------------
SK = [0, 1, 2, 3, 7, 11]   # Galaxy Empyrean Kitsune $950, Ember Dragon $650, Purple Lightbning $550, Arcsteel Magnet $350, Divine Portal $240, Torment Pain $30
cards = []
for i, k in enumerate(SK):
    col, row = i % 3, i // 3
    cards.append(dict(x=70 + col * 320, y=450 + row * 384, side=-1 if col % 2 == 0 else 1, amp=[10, 20, 13][col], dx=[7, -6, 8][col]))
sk_html = "".join(
    '<div class="skc" id="s3-c%d" style="left:%dpx;top:%dpx"><div class="skc-in" id="s3-in%d"><img src="assets/captures/skin_%02d.png"><div class="gloss" id="s3-g%d"></div></div><div class="ring" id="s3-r%d"></div>%s</div>'
    % (i, c["x"], c["y"], i, SK[i], i, i, "".join('<i class="cn" id="s3-n%d_%d"></i>' % (i, j) for j in range(6))) for i, c in enumerate(cards))
rc = random.Random(3)
bursts = [[dict(x=rc.randint(-150, 150), y=-rc.randint(110, 260), rot=rc.randint(-200, 200)) for _ in range(6)] for _ in cards]
HI0, HIS = 1.75, 0.44
write("scene-3", comp("scene-3", DUR["s3"],
    '<div class="scn" id="s3"><div class="beam dark" id="s3-beam"></div><div class="shead" id="s3-head">%s</div>%s</div>' % (gt("SKINS", "sk"), sk_html),
    '''
  tl.fromTo("#s3-beam", { rotation: 25 }, { rotation: -15, duration: D.dur, ease: "none" }, 0);
  tl.fromTo("#s3-head", { scale: .3, opacity: 0, y: 60 }, { scale: 1, opacity: 1, y: 0, duration: .5, ease: "back.out(1.8)" }, .08);
  D.cards.forEach((o, i) => {
    tl.set("#s3-c" + i, { transformPerspective: 900 }, 0);
    tl.fromTo("#s3-c" + i, { y: -1000, scale: .55, rotationY: o.side * 70, opacity: 0 }, { y: 0, scale: 1, rotationY: o.side * 5, opacity: 1, duration: .75, ease: "back.out(1.4)" }, .3 + i * .14);
    tl.to("#s3-in" + i, { y: o.amp, x: o.dx, duration: .9 + .12 * (i % 3), yoyo: true, repeat: 5, ease: "sine.inOut" }, 1 + i * .1);
    const t = D.hi0 + D.his * i;
    tl.fromTo("#s3-r" + i, { opacity: 0, scale: 1.35 }, { opacity: 1, scale: 1, duration: .18, ease: "power3.out" }, t);
    tl.to("#s3-r" + i, { opacity: 0, duration: .25 }, t + .36);
    tl.to("#s3-c" + i, { scale: 1.16, duration: .16, ease: "power2.out" }, t);
    tl.to("#s3-c" + i, { scale: 1, duration: .34, ease: "elastic.out(1,.5)" }, t + .2);
    tl.fromTo("#s3-g" + i, { x: -120, opacity: .9 }, { x: 420, opacity: .9, duration: .45, ease: "power2.inOut" }, t);
    D.bursts[i].forEach((b, j) => tl.fromTo("#s3-n" + i + "_" + j, { x: 0, y: 0, opacity: 1, scale: 1, rotation: 0 }, { x: b.x, y: b.y, opacity: 0, scale: .4, rotation: b.rot, duration: .6, ease: "power2.out" }, t + .05));
    tl.to("#s3-c" + i, { x: -1300, rotationY: 60, skewX: -20, duration: .4, ease: "power3.in" }, D.dur - .45 + i * .03);
  });
  tl.to("#s3-head", { y: -300, opacity: 0, duration: .35, ease: "power3.in" }, D.dur - .4);
''', dict(dur=DUR["s3"], cards=cards, bursts=bursts, hi0=HI0, his=HIS)))
for i in range(len(cards)):
    sfx(S3 + .3 + i * .14 + .35, "pop", .8)
    sfx(S3 + HI0 + HIS * i + .02, "coin", .9)
sfx(S3 + .05, "whoosh_zoom_in", .6)

# ----------------------------------------------------------------------------------------------
# ESCENA 4 · FÍSICAS (panel 3D con scroll fluido, zoom y destellos)
# ----------------------------------------------------------------------------------------------
K = 900 / 416
CARD = dict(dragon=(17, 18), control=(115, 18), kitsune=(213, 18), magnet=(311, 18))
TT = .33   # duración de cada movimiento de cámara
targets = [  # (cx, cy, zoom, hold)  en px de la captura original 416x819
    (208, 90, 1.0, .3), (63, 74, 1.9, .5), (161, 74, 1.9, .45), (259, 74, 1.9, .45), (357, 74, 1.9, .45), (208, 190, 1.45, .5), (208, 400, 1.4, .5), (208, 690, 1.4, .6)]
glint_at = [1, 2, 3, 4]
rings = [dict(i=i, x=CARD[k][0] * K, y=CARD[k][1] * K, w=93 * K, h=111 * K, tgt=i + 1) for i, k in enumerate(["dragon", "control", "kitsune", "magnet"])]
write("scene-4", comp("scene-4", DUR["s4"],
    '<div class="scn" id="s4"><div class="beam" id="s4-beam"></div><div class="s4head" id="s4-head">%s</div>'
    '<div class="s4wrap" id="s4-wrap"><div class="s4view"><div class="s4cam" id="s4-cam"><img src="assets/captures/perm_full.png">%s</div><div class="s4glint" id="s4-gl"></div></div></div></div>'
    % (gt("FÍSICAS", "fi"), "".join('<div class="s4ring" id="s4-r%d" style="left:%dpx;top:%dpx;width:%dpx;height:%dpx"></div>' % (r_["i"], r_["x"], r_["y"], r_["w"], r_["h"]) for r_ in rings)),
    '''
  const K = D.K, W = 900, H = 940, IH = 819 * K;
  const cam = (cx, cy, s) => ({ x: Math.min(0, Math.max(W - W * s, W / 2 - cx * K * s)), y: Math.min(0, Math.max(H - IH * s, H / 2 - cy * K * s)), scale: s });
  tl.fromTo("#s4-beam", { rotation: -20 }, { rotation: 30, duration: D.dur, ease: "none" }, 0);
  tl.fromTo("#s4-head", { x: 500, opacity: 0, skewX: -20 }, { x: 0, opacity: 1, skewX: 0, duration: .45, ease: "expo.out" }, .1);
  tl.set("#s4-wrap", { transformPerspective: 1500 }, 0);
  tl.fromTo("#s4-wrap", { x: 500, rotationY: -40, rotationX: 10, opacity: 0 }, { x: 0, rotationY: -9, rotationX: 5, opacity: 1, duration: .55, ease: "expo.out" }, .1);
  tl.to("#s4-wrap", { rotationY: -3, rotationX: 2, duration: 1.7, yoyo: true, repeat: Math.ceil(D.dur / 1.7), ease: "sine.inOut" }, .7);
  let t = .35;
  D.targets.forEach((g, i) => {
    const c = cam(g[0], g[1], g[2]);
    if (i === 0) tl.set("#s4-cam", c, 0); else tl.to("#s4-cam", { ...c, duration: D.tt, ease: "power2.inOut" }, t);
    if (i > 0) t += D.tt;
    D.rings.filter(r => r.tgt === i).forEach(r => {
      tl.fromTo("#s4-r" + r.i, { opacity: 0, scale: 1.3 }, { opacity: 1, scale: 1, duration: .18 }, t);
      tl.to("#s4-r" + r.i, { opacity: 0, duration: .25 }, t + g[3] - .12);
    });
    if (D.glints.includes(i)) tl.fromTo("#s4-gl", { x: -260, opacity: .9 }, { x: 1100, opacity: .9, duration: .55, ease: "power2.inOut" }, t + .05);
    D.times.push(t);
    t += g[3];
  });
  tl.to("#s4-wrap", { x: 1300, rotationY: 50, duration: .4, ease: "power3.in" }, D.dur - .4);
''', dict(dur=DUR["s4"], K=K, targets=targets, glints=glint_at, rings=rings, times=[], tt=TT)))
tt = .35
for i, g in enumerate(targets):
    if i > 0: tt += TT
    if i in glint_at: sfx(S4 + tt + .05, "coin", .85); sfx(S4 + tt + .05, "shine", .5)
    elif i > 0: sfx(S4 + tt, "tick_soft", .5)
    tt += g[3]
sfx(S4 + .1, "whoosh_side", .7)
print("escena 4 usa hasta", round(tt, 2), "de", DUR["s4"])
assert tt < DUR["s4"] - .35, "recorre demasiado para la escena 4"
assert HI0 + HIS * 5 + .5 < DUR["s3"] - .4, "resaltados no caben en la escena 3"

# ----------------------------------------------------------------------------------------------
# ESCENA 5 · CONFIANZA (trades en abanico, sello, contador, TRADES REALES)
# ----------------------------------------------------------------------------------------------
TR = [os.path.basename(p)[:-4] for p in sorted(glob.glob(os.path.join(ROOT, "assets/captures/trade_*.png")))]
order = ["trade_kitsune", "trade_portal_yeti", "trade_dragon", "trade_portal_bran", "trade_darkblade"]
TR = [x for x in order if x in TR] + [x for x in TR if x not in order]
N = len(TR)
slot0, slotw = 1.75, (DUR["s5"] - 1.75 - .25) / N
fan = [dict(rot=round((i - (N - 1) / 2) * 11, 2), x=round((i - (N - 1) / 2) * 140), y=round(abs(i - (N - 1) / 2) * 24)) for i in range(N)]
tc_html = "".join('<div class="tc" id="s5-c%d"><img src="assets/captures/%s.png"><div class="gloss" id="s5-g%d"></div></div>' % (i, TR[i], i) for i in reversed(range(N)))
head = "".join('<span class="lt" style="display:inline-block%s">%s</span>' % (";width:.35em" if ch == " " else "", ch if ch != " " else "&nbsp;") for ch in "TRADES REALES")
CNT0 = 1.6
write("scene-5", comp("scene-5", DUR["s5"],
    '<div class="scn" id="s5"><div class="beam" id="s5-beam"></div>'
    '<div class="s5head" id="s5-head"><span class="g">%s</span> <span class="ck" id="s5-k0">✅</span><span class="ck" id="s5-k1">✅</span><span class="ck" id="s5-k2">✅</span></div>%s'
    '<div class="seal" id="s5-seal">✅ 100%% CONFIABLE<div class="hud-shine" id="s5-sh" style="height:120px"></div></div>'
    '<div class="counter" id="s5-count">+<b id="s5-cnt">0</b> REFERENCIAS</div></div>' % (head, tc_html),
    '''
  tl.fromTo("#s5-beam", { rotation: 10 }, { rotation: -35, duration: D.dur, ease: "none" }, 0);
  document.querySelectorAll("#s5-head .lt").forEach((el, i) => tl.fromTo(el, { y: -90, opacity: 0, scale: 1.6 }, { y: 0, opacity: 1, scale: 1, duration: .3, ease: "back.out(2)" }, .1 + i * .05));
  [0, 1, 2].forEach(i => tl.fromTo("#s5-k" + i, { scale: 0, rotation: -40 }, { scale: 1, rotation: 0, duration: .45, ease: "elastic.out(1,.45)" }, .85 + i * .22));
  const N = D.fan.length;
  for (let i = 0; i < N; i++) {
    tl.set("#s5-c" + i, { transformPerspective: 1100 }, 0);
    tl.fromTo("#s5-c" + i, { y: -1300, rotation: (i % 2 ? 25 : -25), scale: .9, opacity: 1 }, { y: 4 * (N - i), x: 0, rotation: 0, scale: .9, duration: .5, ease: "back.out(1.5)" }, .1 + i * .08);
    tl.to("#s5-c" + i, { x: D.fan[i].x, y: D.fan[i].y - 20, rotation: D.fan[i].rot, scale: .86, duration: .55, ease: "back.out(1.6)" }, .75);
    const t = D.slot0 + D.slotw * i;
    tl.to("#s5-c" + i, { x: 0, y: -10, rotation: 0, scale: 1.1, rotationY: 0, duration: .45, ease: "power3.out" }, t);
    tl.fromTo("#s5-g" + i, { x: -200, opacity: .9 }, { x: 1000, opacity: .9, duration: .6, ease: "power2.inOut" }, t + .2);
    if (i < N - 1) tl.to("#s5-c" + i, { x: -1300, y: -260, rotation: -28, scale: .8, duration: .4, ease: "power3.in" }, t + D.slotw - .32);
    else tl.to("#s5-c" + i, { scale: 1.16, duration: D.slotw, ease: "none" }, t + .45);
  }
  tl.fromTo("#s5-seal", { scale: 2.8, rotation: -14, opacity: 0 }, { scale: 1, rotation: -3, opacity: 1, duration: .5, ease: "back.out(1.7)" }, D.seal);
  tl.to("#s5-seal", { scale: 1.06, duration: .32, yoyo: true, repeat: 7, ease: "sine.inOut" }, D.seal + .6);
  for (let t = D.seal + .7; t < D.dur - .4; t += 1.3) tl.fromTo("#s5-sh", { x: -120, opacity: .9 }, { x: 560, opacity: .9, duration: .55, ease: "power2.inOut" }, t);
  tl.fromTo("#s5-count", { y: 120, opacity: 0 }, { y: 0, opacity: 1, duration: .45, ease: "back.out(2)" }, D.cnt0 - .2);
  tl.fromTo("#s5-cnt", { textContent: 0 }, { textContent: 100, snap: { textContent: 1 }, duration: D.cnt1, ease: "power2.out" }, D.cnt0);
  tl.to("#s5-count", { scale: 1.12, duration: .2, yoyo: true, repeat: 1 }, D.cnt0 + D.cnt1);
''', dict(dur=DUR["s5"], fan=fan, slot0=slot0, slotw=slotw, seal=.95, cnt0=CNT0, cnt1=2.4)))
sfx(S5 + .02, "impact", .9)
for i in range(N): sfx(S5 + .1 + i * .08 + .35, "pop", .7)
sfx(S5 + .75, "whoosh_fan", .6)
for i in range(N): sfx(S5 + slot0 + slotw * i, "whoosh_fast", .45)
for i in range(3): sfx(S5 + .85 + i * .22 + .1, "ding", .6 + .1 * i)
sfx(S5 + .95 + .15, "ach", .95)
for k in range(10): sfx(S5 + CNT0 + .2 + k * .22, "tick", .5)
sfx(S5 + CNT0 + 2.45, "coin", .8)

# ----------------------------------------------------------------------------------------------
# ESCENA 6 · CIERRE (fondo dorado, revelado por palabras, flecha, neón, zoom-out final)
# ----------------------------------------------------------------------------------------------
def words_html(lines, cls):
    return "".join('<span class="ln">%s</span>' % " ".join(mask('<span class="wd">%s</span>' % w) for w in ln) for ln in lines)
rs = random.Random(9)
sp6 = [dict(x=rs.randint(0, 1060), s=rs.choice([8, 10, 14, 18]), d=round(rs.uniform(4, 8), 2), dl=round(rs.uniform(0, 3), 2)) for _ in range(26)]
write("scene-6", comp("scene-6", DUR["s6"],
    '<div class="scn" id="s6"><div class="fill s6gold" id="s6-gold"></div><div class="beam dark" id="s6-b1"></div><div class="beam dark" id="s6-b2" style="height:240px"></div>' +
    "".join('<i class="sp" id="s6p%d" style="left:%dpx;width:%dpx;height:%dpx;background:#fff;box-shadow:0 0 14px 5px rgba(255,255,255,.85)"></i>' % (i, o["x"], o["s"], o["s"]) for i, o in enumerate(sp6)) +
    '<div class="s6txt" id="s6-txt">' + words_html([["ESCRÍBEME"], ["POR", "DM", "EN"], ["TIKTOK", "📩"]], "") + '</div>'
    '<svg class="arrow" id="s6-arrow" viewBox="0 0 200 130"><g fill="none" stroke="#0b0b0b" stroke-width="22" stroke-linecap="round" stroke-linejoin="round">'
    '<path id="s6-a0" d="M30 8 L100 52 L170 8"/><path id="s6-a1" d="M30 48 L100 92 L170 48"/><path id="s6-a2" d="M30 88 L100 132 L170 88"/></g></svg>'
    '<div class="neon" id="s6-neon">%s</div>'
    '<div class="slogan" id="s6-slogan">%s</div><div class="only" id="s6-only">Venta solo en México 🇲🇽</div>'
    '<div class="fill" id="s6-white" style="background:#fff;opacity:0"></div></div>'
    % (HANDLE, words_html([["¡SUBE", "DE", "NIVEL"], ["TU", "INVENTARIO!"]], "")),
    '''
  tl.fromTo("#s6-gold", { opacity: 0 }, { opacity: 1, duration: .25 }, 0);
  tl.fromTo("#s6-b1", { rotation: -30 }, { rotation: 35, duration: D.dur, ease: "none" }, 0);
  tl.fromTo("#s6-b2", { rotation: 50 }, { rotation: -20, duration: D.dur, ease: "none" }, 0);
  D.sp.forEach((o, i) => tl.fromTo("#s6p" + i, { y: 2000, opacity: 0 }, { y: -120, opacity: .95, duration: o.d, repeat: Math.ceil(D.dur / o.d), ease: "none" }, o.dl));
  document.querySelectorAll("#s6-txt .rv").forEach((el, i) => tl.fromTo(el, { y: 260, rotation: 6 }, { y: 0, rotation: 0, duration: .5, ease: "expo.out" }, D.t0 + i * .2));
  tl.fromTo("#s6-arrow", { y: -40, opacity: 0 }, { y: 0, opacity: 1, duration: .35, ease: "power3.out" }, D.t0 + 1.5);
  [0, 1, 2].forEach(i => tl.fromTo("#s6-a" + i, { opacity: .15, y: -10 }, { opacity: 1, y: 14, duration: .32, yoyo: true, repeat: 15, ease: "sine.inOut" }, D.t0 + 1.6 + i * .12));
  [[0, .1], [.08, 0], [.16, .1], [.24, 0], [.34, 1]].forEach(f => tl.set("#s6-neon", { opacity: f[1] }, D.t1 + f[0]));
  tl.fromTo("#s6-neon", { scale: .85 }, { scale: 1, duration: .5, ease: "back.out(2)" }, D.t1 + .3);
  tl.to("#s6-neon", { scale: 1.04, duration: .35, yoyo: true, repeat: 9, ease: "sine.inOut" }, D.t1 + 1);
  document.querySelectorAll("#s6-slogan .rv").forEach((el, i) => tl.fromTo(el, { y: 220 }, { y: 0, duration: .5, ease: "expo.out" }, D.t2 + i * .22));
  tl.fromTo("#s6-only", { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: .45 }, D.t2 + .6);
  tl.fromTo("#s6-white", { opacity: 0 }, { opacity: .9, duration: .12, ease: "power2.out" }, D.dur - .5);
  tl.to("#s6-white", { opacity: 0, duration: .4, ease: "power2.in" }, D.dur - .38);
  tl.fromTo("#s6", { scale: 1.0 }, { scale: .93, duration: .95, ease: "power2.inOut" }, D.dur - .95);
''', dict(dur=DUR["s6"], sp=sp6, t0=.2, t1=1.9, t2=3.5)))
sfx(S6 + .02, "shock", 1.0)
for i in range(6): sfx(S6 + .2 + i * .2 + .1, "slam", .45)
sfx(S6 + 1.9 + .3, "neon", .7); sfx(S6 + 3.5, "whoosh_up", .5); sfx(S6 + 3.7, "slam", .6)
sfx(END - .5, "impact", .9); sfx(END - .5, "shine", .8)

# ----------------------------------------------------------------------------------------------
# TRANSICIONES (cada una distinta)
# ----------------------------------------------------------------------------------------------
B = [S2, S3, S4, S5, S6]
rsl = random.Random(2)
slices = [dict(y=i * 275 - 20, h=275 + 20, c=["#000", "#FFC21A", "#fff", "#00f0ff", "#ff2bd6", "#FFC21A", "#000"][i], dx=rsl.choice([-1, 1])) for i in range(7)]
write("fx", comp("fx", TOTAL,
    '<div class="sweep" id="fx-sweep"></div>' + "".join('<div class="sl" id="fx-sl%d" style="top:%dpx;height:%dpx;background:%s"></div>' % (i, o["y"], o["h"], o["c"]) for i, o in enumerate(slices)) +
    '<div class="flash" id="fx-wh" style="background:#fff"></div><div class="flash" id="fx-gd" style="background:#FFC21A"></div><div class="shock" id="fx-shock"></div><div class="flash" id="fx-end" style="background:#fff"></div>',
    '''
  const [b2, b3, b4, b5, b6] = D.B;
  const FT = (s, a, c, t) => tl.fromTo(s, a, { ...c, immediateRender: false }, t);
  // 1→2 barrido de luz dorada
  FT("#fx-sweep", { x: -300, opacity: 1 }, { x: 1900, opacity: 1, duration: .62, ease: "power2.inOut" }, b2 - .3);
  tl.set("#fx-sweep", { opacity: 0 }, b2 + .34);
  // 2→3 zoom a través del título (flash dorado)
  FT("#fx-gd", { opacity: 0 }, { opacity: .85, duration: .12, ease: "power2.in" }, b3 - .14);
  tl.to("#fx-gd", { opacity: 0, duration: .35, ease: "power2.out" }, b3 - .02);
  // 3→4 glitch lateral por franjas
  D.sl.forEach((o, i) => {
    FT("#fx-sl" + i, { x: o.dx * -1200, opacity: 1 }, { x: 0, duration: .13, ease: "power2.out" }, b4 - .22 + i * .02);
    tl.to("#fx-sl" + i, { x: o.dx * 1200, duration: .15, ease: "power2.in" }, b4 + .02 + i * .02);
    tl.set("#fx-sl" + i, { opacity: 0 }, b4 + .3);
  });
  // 4→5 corte seco con destello blanco
  FT("#fx-wh", { opacity: 1 }, { opacity: 0, duration: .3, ease: "power2.out" }, b5);
  // 5→6 onda de luz dorada
  FT("#fx-shock", { scale: .1, opacity: 1 }, { scale: 7, opacity: 0, duration: .8, ease: "power2.out" }, b6 - .08);
  FT("#fx-gd", { opacity: 0 }, { opacity: .9, duration: .08 }, b6 - .06);
  tl.to("#fx-gd", { opacity: 0, duration: .35 }, b6 + .02);
''', dict(B=B, sl=slices)))
sfx(S2 - .3, "whoosh_up", .9); sfx(S3 - .5, "whoosh_zoom", .3); sfx(S3 - .08, "impact", .55)
sfx(S4 - .22, "glitch", .9); sfx(S4 - .2, "whoosh_side", .8)
sfx(S5, "impact", .9)
sfx(S6 - .1, "shock", .6)

# ----------------------------------------------------------------------------------------------
# index.html
# ----------------------------------------------------------------------------------------------
mounts = [("bg", 0, TOTAL, 0)] + [("scene-%d" % (i + 1), START["s%d" % (i + 1)], DUR["s%d" % (i + 1)], 1) for i in range(6)] + [("fx", 0, TOTAL, 2), ("hud", 0, TOTAL, 3), ("subs", 0, TOTAL, 4)]
mid = {"bg": "m-bg", "fx": "m-fx", "hud": "m-hud", "subs": "m-subs"}
mhtml = "\n  ".join('<div id="%s" class="clip mount" data-composition-id="%s" data-composition-src="compositions/%s.html" data-start="%s" data-duration="%s" data-track-index="%d"></div>'
                    % (mid.get(c, "m-s" + c[-1]), c, c, round(s, 3), round(d, 3), tr) for c, s, d, tr in mounts)
open(os.path.join(ROOT, "index.html"), "w").write('''<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=1080, height=1920">
<title>Promo MonZ - Skins y Físicas</title>
<link rel="stylesheet" href="assets/style.css">
</head>
<body>
<div id="root" data-composition-id="root" data-width="1080" data-height="1920" data-start="0" data-duration="%s">
  <script src="assets/vendor/gsap.min.js"></script>
  %s
  <audio id="mix" src="assets/audio.mp3" data-start="0" data-duration="%s" data-track-index="9" data-volume="1"></audio>
  <script>
    const tl = gsap.timeline({ paused: true });
    tl.to({}, { duration: %s }, 0);
    window.__timelines = window.__timelines || {};
    window.__timelines["root"] = tl;
  </script>
</div>
</body>
</html>
''' % (TOTAL, mhtml, TOTAL, TOTAL))

json.dump(dict(total=TOTAL, scenes={k: [round(a, 3), round(b, 3)] for k, a, b in SC}, voice=v, events=EV, bpm=BPM, beat=BEAT,
               voice_files=[x["id"] for x in voice]), open(os.path.join(ROOT, "timeline.json"), "w"), indent=1)
if os.environ.get("SKIP_AUDIO") != "1":
    import audio; audio.render(ROOT)
print("OK", TOTAL)
