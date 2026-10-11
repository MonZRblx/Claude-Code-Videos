#!/usr/bin/env python3
"""Promo MonZ v3 · showreel de la tienda (TikTok 1080x1920, 30 fps, 30.0 s, SIN voz, en bucle).

Una composición Hyperframes por escena (compositions/*.html) + fondo, HUD y transiciones.
Uso:  python3 prep_tiles.py && python3 build.py && npx hyperframes render -o out/promo-monz-v3.mp4
"""
import json, os, random
from PIL import Image
ROOT = os.path.dirname(os.path.abspath(__file__))
os.makedirs(os.path.join(ROOT, "compositions"), exist_ok=True)
HANDLE = "@monzmc05"
BPM = 128.0; BEAT = 60 / BPM; HALF = BEAT / 2
snap = lambda t: round(round(t / HALF) * HALF, 4)

TL = json.load(open(os.path.join(ROOT, "tiles.json"))); TILES = TL["tiles"]
by = {c: [t for t in TILES if t["cat"] == c] for c in ("perm", "fis", "gp", "skin")}
TW, TH = 278, 324                      # tarjeta original a 278x324 (proporción real del tile: 102x119)
COLX = [192, 530]; ROWY = [340, 708, 1076]
POS = [(COLX[i % 2], ROWY[i // 2]) for i in range(6)]      # 2 columnas x 3 filas, dentro de x 60–940 / y 300–1400
ZT = 290                                                    # tope de la zona de contenido
TITLES = dict(perm="FRUTAS PERMANENTES", fis="FRUTAS FÍSICAS", gp="GAMEPASSES", skin="SKINS")
TFS = dict(perm=68, fis=84, gp=104, skin=126)
PHRASE = dict(perm=["PERMANENTES", "AL", "MEJOR", "PRECIO"], fis=["LAS", "TIENES", "YA"], gp=["POTENCIA", "TU", "CUENTA"], skin=["LUCE", "DIFERENTE"])

# ---------------------------------------------------------------- línea de tiempo (30.0 s)
T_HOOK = 0.0
T_INTRO = snap(1.5); T_PERM = snap(3.0); T_FIS = snap(8.5); T_GP = snap(13.5); T_SKIN = snap(18.0)
T_TRUST = snap(22.5); T_CLOSE = snap(26.5); TOTAL = 30.0
SC = dict(hook=(T_HOOK, T_INTRO), intro=(T_INTRO, T_PERM), perm=(T_PERM, T_FIS), fis=(T_FIS, T_GP), gp=(T_GP, T_SKIN), skin=(T_SKIN, T_TRUST), trust=(T_TRUST, T_CLOSE), close=(T_CLOSE, TOTAL))
DUR = {k: round(b - a, 4) for k, (a, b) in SC.items()}
print({k: (round(a, 2), DUR[k]) for k, (a, b) in SC.items()})
WIN = .5; N_TR = 5; T_CLEAN = N_TR * WIN       # ventanas de trade: 0.5 s cada una (local a la escena trust)

EV = []
def sfx(t, kind, vol=1.0, pr=1): EV.append((round(t, 3), kind, vol, pr))
def comp(cid, dur, inner, js, data=None):
    return ('<template id="' + cid + '-template">\n<div data-composition-id="' + cid + '" data-width="1080" data-height="1920" data-start="0" data-duration="' + str(round(dur, 3)) + '">\n'
            + inner + '\n<script>\n(function () {\n  const tl = gsap.timeline({ paused: true });\n  const D = ' + json.dumps(data if data is not None else {}, ensure_ascii=False) + ';\n'
            + js + '\n  window.__timelines = window.__timelines || {};\n  window.__timelines["' + cid + '"] = tl;\n})();\n</script>\n</div>\n</template>\n')
def write(name, text): open(os.path.join(ROOT, "compositions", name + ".html"), "w").write(text)
def mask(inner): return '<span class="mask"><span class="rv" style="display:inline-block">' + inner + '</span></span>'
def gtw(text, cls=""): return '<span class="gtw"><span class="o">' + text + '</span><span class="f ' + cls + '">' + text + '</span></span>'

FLAG = ('<svg class="hud-flag" viewBox="0 0 96 64" style="%s"><rect width="32" height="64" fill="#006847"/><rect x="32" width="32" height="64" fill="#fff"/><rect x="64" width="32" height="64" fill="#CE1126"/>'
        '<g transform="translate(48 33)"><ellipse cx="0" cy="-2" rx="7.5" ry="8.5" fill="#7a4a1e"/><circle cx="-4" cy="-10" r="3" fill="#7a4a1e"/><path d="M-4 -12 l-4 1 l4 1z" fill="#d9a441"/>'
        '<path d="M-5 -4 Q-14 -2 -13 6 Q-8 1 -4 3Z" fill="#a0642a"/><path d="M5 -4 Q14 -2 13 6 Q8 1 4 3Z" fill="#a0642a"/>'
        '<path d="M-13 9 Q0 19 13 9" fill="none" stroke="#2d8a3e" stroke-width="2.6" stroke-linecap="round"/><ellipse cx="0" cy="10.5" rx="6" ry="2.2" fill="#3aa0d8"/></g></svg>')
CROWN = '<svg viewBox="0 0 30 22"><path d="M2 20 L4 5 L10 12 L15 2 L20 12 L26 5 L28 20 Z" fill="#FFC21A" stroke="#fff3b0" stroke-width="1.5" stroke-linejoin="round"/></svg>'
ICONS = dict(
    perm='<svg viewBox="0 0 64 64"><path d="M32 6 L54 24 L32 58 L10 24Z" fill="#FFB000" stroke="#fff" stroke-width="3" stroke-linejoin="round"/><path d="M10 24H54M24 24 L32 6 L40 24 L32 58 L24 24" fill="none" stroke="#fff" stroke-width="2.4" stroke-linejoin="round"/></svg>',
    fis='<svg viewBox="0 0 64 64"><circle cx="32" cy="38" r="20" fill="#FF2D6F" stroke="#fff" stroke-width="3"/><path d="M32 18 Q32 8 38 6" stroke="#fff" fill="none" stroke-width="3.2" stroke-linecap="round"/><path d="M34 14 Q46 6 52 14 Q42 20 34 14Z" fill="#3ddc84" stroke="#fff" stroke-width="2.4"/><path d="M22 34 Q24 28 30 28" stroke="#fff" fill="none" stroke-width="3" stroke-linecap="round" opacity=".8"/></svg>',
    gp='<svg viewBox="0 0 64 64"><path d="M8 18 H56 V26 a6 6 0 0 0 0 12 V46 H8 V38 a6 6 0 0 0 0 -12Z" fill="#2D9BFF" stroke="#fff" stroke-width="3" stroke-linejoin="round"/><path d="M32 24 L35 31 L42 31 L36.5 35.5 L38.5 42 L32 38 L25.5 42 L27.5 35.5 L22 31 L29 31Z" fill="#fff"/></svg>',
    skin='<svg viewBox="0 0 64 64"><path d="M32 4 L39 25 L60 32 L39 39 L32 60 L25 39 L4 32 L25 25Z" fill="#A64DFF" stroke="#fff" stroke-width="3" stroke-linejoin="round"/><circle cx="50" cy="12" r="4" fill="#fff"/></svg>')

# ---------------------------------------------------------------- fondo + HUD
r = random.Random(5)
dust = [dict(d=round(r.uniform(8, 15), 2), dl=round(r.uniform(0, 7), 2)) for _ in range(30)]
spk = "".join('<i class="sp" id="bgs%d" style="left:%dpx;width:%dpx;height:%dpx"></i>' % (i, r.randint(0, 1060), s, s) for i in range(30) for s in [r.choice([6, 8, 10, 14])])
write("bg", comp("bg", TOTAL, '<div class="fill" id="bg-w"><div class="carbon" id="bg-c"></div><div class="haze"></div><div class="beam" id="bg-b1"></div><div class="beam b2" id="bg-b2"></div></div>' + spk, '''
  tl.fromTo("#bg-w", { scale: 1 }, { scale: 1.08, duration: D.total, ease: "none" }, 0);
  tl.fromTo("#bg-c", { x: 0, y: 0 }, { x: -110, y: -150, duration: D.total, ease: "none" }, 0);
  tl.fromTo("#bg-b1", { rotation: -30 }, { rotation: 30, duration: D.total, ease: "none" }, 0);
  tl.fromTo("#bg-b2", { rotation: 35 }, { rotation: -25, duration: D.total, ease: "none" }, 0);
  D.dust.forEach((o, i) => tl.fromTo("#bgs" + i, { y: 2000, opacity: 0, scale: .6 }, { y: -120, opacity: .9, scale: 1.1, duration: o.d, repeat: Math.ceil(D.total / o.d), ease: "none" }, o.dl));
''', dict(total=TOTAL, dust=dust)))
write("hud", comp("hud", TOTAL,
    FLAG.replace('class="hud-flag"', 'class="hud-flag" id="hud-fl"') % "left:28px" + FLAG.replace('class="hud-flag"', 'class="hud-flag" id="hud-fr"') % "left:956px" +
    '<div class="hud-handle" id="hud-hd">' + HANDLE + '</div><div class="hud-tag" id="hud-tg">SOLO <b>MÉXICO</b></div>', '''
  tl.fromTo("#hud-fl", { y: -100, opacity: 0 }, { y: 0, opacity: 1, duration: .35, ease: "back.out(2)" }, .02);
  tl.fromTo("#hud-fr", { y: -100, opacity: 0 }, { y: 0, opacity: 1, duration: .35, ease: "back.out(2)" }, .06);
  tl.fromTo("#hud-hd", { x: -160, opacity: 0 }, { x: 0, opacity: 1, duration: .3, ease: "power3.out" }, .08);
  tl.fromTo("#hud-tg", { y: -50, opacity: 0 }, { y: 0, opacity: 1, duration: .3, ease: "power3.out" }, .1);
  tl.to("#hud-fl", { rotation: 3, duration: 1, yoyo: true, repeat: Math.ceil(D.total), ease: "sine.inOut" }, .6);
  tl.to("#hud-fr", { rotation: -3, duration: 1, yoyo: true, repeat: Math.ceil(D.total), ease: "sine.inOut" }, .8);
''', dict(total=TOTAL)))

# ---------------------------------------------------------------- 1 · HOOK
def words(cls, fs, top, lines, idp):
    return '<div class="gt %s" id="%s" style="top:%dpx;font-size:%dpx">%s</div>' % (cls, idp, top, fs, "".join('<span class="ln">%s</span>' % " ".join('<span class="w">%s</span>' % w for w in ln) for ln in lines))
g1 = [["¿PAGANDO"], ["DE MÁS?"]]; g2 = [["AQUÍ NO."]]
lane = [(by["perm"][0], 300, 1, 0.00), (by["perm"][2], 300, 1, 0.10), (by["fis"][0], 300, 1, 0.20),
        (by["skin"][0], 1076, -1, 0.05), (by["gp"][0], 1076, -1, 0.15), (by["skin"][1], 1076, -1, 0.25)]
cross = "".join('<div class="tc" id="h-t%d" style="left:0;top:%dpx;opacity:1"><img src="assets/tiles/%s"></div>' % (i, y - ZT + 10 + (0 if y < 700 else 0), t["file"]) for i, (t, y, d, s) in enumerate(lane))
write("hook", comp("hook", DUR["hook"],
    '<div class="scn" id="h"><div class="hrays" id="h-rays"></div><div class="zone" style="top:290px">' + cross + '</div><div class="fill" id="h-cam">' +
    words("cy", 160, 690, g1, "g1c") + words("mg", 160, 690, g1, "g1m") + words("white", 160, 690, g1, "g1") + words("white", 200, 760, g2, "g2") + '</div></div>', '''
  tl.fromTo("#h-rays", { rotation: 0, opacity: .9 }, { rotation: 35, opacity: 1, duration: D.dur, ease: "none" }, 0);
  tl.fromTo("#h-cam", { scale: .9 }, { scale: 1.08, duration: D.dur, ease: "power1.in" }, 0);
  ["#g1c", "#g1m", "#g1"].forEach(L => document.querySelectorAll(L + " .w").forEach((el, i) =>
    tl.fromTo(el, { y: 70, scale: 1.3, opacity: .6, rotation: i % 2 ? 4 : -4 }, { y: 0, scale: 1, opacity: 1, rotation: 0, duration: .26, ease: "back.out(1.4)" }, i * .1)));
  tl.fromTo("#g1c", { x: 0, opacity: 0 }, { x: 16, opacity: .9, duration: .05, yoyo: true, repeat: 5, ease: "none" }, .42);
  tl.fromTo("#g1m", { x: 0, opacity: 0 }, { x: -16, opacity: .9, duration: .05, yoyo: true, repeat: 5, ease: "none" }, .42);
  ["#g1c", "#g1m", "#g1"].forEach(L => tl.to(L, { scale: 1.2, opacity: 0, duration: .1, ease: "power2.in" }, .74));
  tl.fromTo("#g2 .w", { scale: 2.6, opacity: 0, rotation: -5 }, { scale: 1, opacity: 1, rotation: 0, duration: .26, ease: "back.out(1.4)" }, .84);
  D.lane.forEach((o, i) => tl.fromTo("#h-t" + i, { x: o.d > 0 ? -300 + (o.s === 0 ? 120 : 0) : 1080 - (o.s === .05 ? 120 : 0), skewX: o.d > 0 ? -14 : 14 }, { x: o.d > 0 ? 1100 : -300, duration: .5, ease: "none" }, o.s));
''', dict(dur=DUR["hook"], lane=[dict(d=d, s=s) for (_, _, d, s) in lane])))
sfx(T_HOOK + .01, "boom", .8, 3); sfx(T_HOOK + .3, "slam", .35); sfx(T_HOOK + .84, "slam", .4, 2)
for (_, _, _, s) in lane: sfx(T_HOOK + s + .12, "whoosh_fast", .22)

# ---------------------------------------------------------------- 2 · INTRO
labels = [("perm", "PERMANENTES"), ("fis", "FÍSICAS"), ("gp", "GAMEPASSES"), ("skin", "SKINS")]
mini = "".join('<div class="mini c-%s" id="i-m%d" style="left:%dpx;top:900px"><div class="d"></div>%s<div class="lb">%s</div></div>' % (k, i, 70 + i * 215, ICONS[k], lb) for i, (k, lb) in enumerate(labels))
write("intro", comp("intro", DUR["intro"],
    '<div class="scn" id="i"><div class="beam" id="i-beam"></div><div class="mz" id="i-t1" style="top:380px">' + mask(gtw("MONZ")) + '</div><div class="mz" id="i-t2" style="top:560px;font-size:150px">' + mask(gtw("STORE", "wh")) + '</div>' + mini +
    '<div class="phrase c-gold" id="i-ph">' + "".join('<span class="pw%s">%s</span>' % (" a" if w == "INVENTARIO" else "", w) for w in ["TODO", "PARA", "TU", "INVENTARIO"]) + '</div></div>', '''
  tl.fromTo("#i-beam", { rotation: -25 }, { rotation: 25, duration: D.dur, ease: "none" }, 0);
  document.querySelectorAll("#i-t1 .rv, #i-t2 .rv").forEach((el, i) => tl.fromTo(el, { y: 240 }, { y: 0, duration: .36, ease: "expo.out" }, .1 + i * .08));
  document.querySelectorAll("#i-t1 .f, #i-t2 .f").forEach((el, i) => tl.fromTo(el, { backgroundPosition: "160% 0, 0 0" }, { backgroundPosition: "-60% 0, 0 0", duration: .6, ease: "power2.inOut" }, .28 + i * .1));
  [0, 1, 2, 3].forEach(i => {
    tl.fromTo("#i-m" + i, { y: 80, scale: .5, opacity: 0, rotationY: 90 }, { y: 0, scale: 1, opacity: 1, rotationY: 0, duration: .32, ease: "back.out(1.6)" }, .45 + i * .08);
  });
  document.querySelectorAll("#i-ph .pw").forEach((el, i) => tl.fromTo(el, { y: 30, opacity: 0 }, { y: 0, opacity: 1, duration: .2, ease: "power3.out" }, .5 + i * .07));
  tl.to(["#i-t1", "#i-t2"], { scale: 7, opacity: 0, duration: .3, ease: "power3.in" }, D.dur - .3);
  tl.to(["#i-m0", "#i-m1", "#i-m2", "#i-m3", "#i-ph"], { opacity: 0, scale: .9, duration: .18, ease: "power2.in" }, D.dur - .28);
''', dict(dur=DUR["intro"])))
for i in range(4): sfx(T_INTRO + .45 + i * .08 + .1, "pop", .3)
sfx(T_INTRO + .3, "shine", .3)

# ---------------------------------------------------------------- 3–6 · CATEGORÍAS (6 tarjetas originales, 2x3)
E, S0, SG = .4, .25, .08
for cat in ("perm", "fis", "gp", "skin"):
    items = by[cat]; k = cat; st = SC[cat][0]
    glow = "".join('<div class="gl" id="%s-g%d" style="left:%dpx;top:%dpx"><div class="halo"></div><div class="floor"></div><div class="burst" id="%s-b%d"></div></div>' % (k, i, x, y - ZT, k, i) for i, (x, y) in enumerate(POS))
    tiles = "".join('<div class="tc" id="%s-c%d" style="left:%dpx;top:%dpx"><img src="assets/tiles/%s"><div class="sheen"><i id="%s-s%d"></i></div></div>' % (k, i, x, y - ZT, items[i]["file"], k, i) for i, (x, y) in enumerate(POS))
    bx, by_ = POS[0][0] + TW // 2, POS[0][1] - ZT
    rays = '<div class="rays" id="%s-rays" style="left:%dpx;top:%dpx"></div>' % (k, bx - 150, by_ - 150 + 18)
    top = '<div class="top" id="%s-top" style="left:%dpx;top:%dpx">%s<b style="font-weight:400">TOP</b></div>' % (k, bx - 58, by_ - 42, CROWN)
    if cat == "perm": th = '<div class="hd" id="%s-hd" style="font-size:%dpx">%s</div>' % (k, TFS[k], "".join('<span class="lt">%s</span>' % (ch if ch != " " else "&nbsp;") for ch in TITLES[k]))
    else: th = '<div class="hd" id="%s-hd" style="font-size:%dpx"><span class="tt" style="display:inline-block">%s</span></div>' % (k, TFS[k], TITLES[k])
    ph = '<div class="phrase" id="%s-ph">%s</div>' % (k, "".join('<span class="pw%s">%s</span>' % (" a" if j == 0 else "", w) for j, w in enumerate(PHRASE[k])))
    reveal = dict(perm='document.querySelectorAll("#perm-hd .lt").forEach((el, i) => tl.fromTo(el, { y: -120, opacity: 0, rotationX: 80 }, { y: 0, opacity: 1, rotationX: 0, duration: .3, ease: "back.out(2)" }, .16 + i * .02));',
                  fis='tl.fromTo("#fis-hd .tt", { x: -520, skewX: 28, opacity: 0 }, { x: 0, skewX: 0, opacity: 1, duration: .38, ease: "expo.out" }, .16);',
                  gp='tl.fromTo("#gp-hd .tt", { scale: 1.5, opacity: 0 }, { scale: 1, opacity: 1, duration: .38, ease: "expo.out" }, .16);',
                  skin='tl.fromTo("#skin-hd .tt", { y: 140, opacity: 0, scale: .6 }, { y: 0, opacity: 1, scale: 1, duration: .4, ease: "back.out(1.8)" }, .16);')[cat]
    write("scene-" + cat, comp("scene-" + cat, DUR[cat],
        '<div class="scn c-%s" id="%s"><div class="hz-t"></div><div class="hz-b"></div><div class="beam tint" id="%s-bm"></div>'
        '<div class="rail" id="%s-r1" style="left:112px"></div><div class="rail" id="%s-r2" style="left:962px"></div>'
        '<div class="zone"><div>%s</div>%s<div>%s</div>%s</div>%s<div class="ul" id="%s-ul"></div>%s</div>' % (cat, k, k, k, k, glow, rays, tiles, top, th, k, ph),
        reveal + '''
  const k = D.k;
  tl.fromTo("#" + k + "-bm", { rotation: -25 }, { rotation: 30, duration: D.dur, ease: "none" }, 0);
  tl.fromTo("#" + k + "-r1, #" + k + "-r2", { opacity: 0 }, { opacity: .7, duration: .4 }, .2);
  tl.fromTo("#" + k + "-ul", { scaleX: 0, opacity: 0 }, { scaleX: 1, opacity: 1, duration: .3, ease: "power3.out" }, .24);
  document.querySelectorAll("#" + k + "-ph .pw").forEach((el, i) => tl.fromTo(el, { y: 36, opacity: 0 }, { y: 0, opacity: 1, duration: .24, ease: "power3.out" }, .4 + i * .08));
  tl.fromTo("#" + k, { scale: 1 }, { scale: 1.03, duration: D.dur, ease: "none" }, 0);
  for (let i = 0; i < 6; i++) {
    const c = "#" + k + "-c" + i, g = "#" + k + "-g" + i, t = D.s0 + D.sg * i, end = t + D.E;
    gsap.set(c, { transformPerspective: 900 });
    if (D.cat === "perm") tl.fromTo(c, { rotationX: 90, y: 30, opacity: 0 }, { rotationX: 0, y: 0, opacity: 1, duration: D.E, ease: "back.out(1.6)" }, t);
    else if (D.cat === "fis") { tl.fromTo(c, { y: -64, opacity: 0 }, { y: 0, opacity: 1, duration: D.E + .1, ease: "bounce.out" }, t); tl.fromTo(c, { scale: .55 }, { scale: 1, duration: D.E, ease: "back.out(2)" }, t); }
    else if (D.cat === "gp") tl.fromTo(c, { x: (i % 2 ? 700 : -700), rotationY: (i % 2 ? -55 : 55), opacity: 0 }, { x: 0, rotationY: 0, opacity: 1, duration: D.E, ease: "back.out(1.3)" }, t);
    else {
      tl.fromTo(c, { scale: 1.18, opacity: 0 }, { scale: 1, opacity: 1, duration: D.E, ease: "expo.out" }, t);
      tl.fromTo("#" + k + "-b" + i, { scale: .3, opacity: .9 }, { scale: 2.2, opacity: 0, duration: .4, ease: "power2.out" }, t);
    }
    tl.fromTo(g, { scale: .6, opacity: 0 }, { scale: 1, opacity: 1, duration: D.E, ease: "power2.out" }, t);
    tl.fromTo("#" + k + "-s" + i, { x: -100, opacity: .9 }, { x: 340, opacity: .9, duration: .45, ease: "power2.inOut" }, end + .1);
    tl.to(c, { y: -3, duration: .8, yoyo: true, repeat: 4, ease: "sine.inOut" }, end + .2);
    tl.fromTo(g, { scale: 1 }, { scale: 1.05, duration: 1.1, yoyo: true, repeat: 3, ease: "sine.inOut", immediateRender: false }, end + .1);
  }
  const e0 = D.s0 + D.E;
  tl.fromTo("#" + k + "-top", { scale: 0, opacity: 0, rotation: -15 }, { scale: 1, opacity: 1, rotation: 0, duration: .28, ease: "back.out(2.2)" }, e0 + .05);
  tl.fromTo("#" + k + "-rays", { opacity: 0 }, { opacity: .55, duration: .3 }, D.s0);
  tl.fromTo("#" + k + "-rays", { rotation: 0 }, { rotation: 50, duration: D.dur, ease: "none" }, D.s0);
  const xs = []; for (let i = 0; i < 6; i++) { xs.push("#" + k + "-c" + i); xs.push("#" + k + "-g" + i); }
  xs.push("#" + k + "-rays"); xs.push("#" + k + "-top");
  tl.to(xs, { opacity: 0, scale: .96, duration: .12, ease: "power1.in" }, D.dur - .36);   // las tarjetas terminan de salir antes de cualquier transición
''', dict(k=k, cat=cat, dur=DUR[cat], E=E, s0=S0, sg=SG)))
    for i in range(6): sfx(st + S0 + SG * i + .06, "pop", .26)
    sfx(st + S0 + E + .08, "coin", .4, 2)

# ---------------------------------------------------------------- 7 · CONFIANZA (trades uno por uno + pantalla limpia)
TR = ["kitsune", "portal_yeti", "portal_bran", "dragon", "darkblade"]
tw = ""
for i, n in enumerate(TR):
    w, h_ = Image.open(os.path.join(ROOT, "assets/trades/%s.png" % n)).size; hh = round(840 * h_ / w)
    tw += '<div class="tw" id="t-w%d" style="top:%dpx;height:%dpx"><img src="assets/trades/%s.png"></div>' % (i, 850 - hh // 2, hh, n)
write("trust", comp("trust", DUR["trust"],
    '<div class="scn c-gold" id="t"><div class="hz-t"></div><div class="hz-b"></div><div class="beam tint" id="t-bm"></div><div class="hd" id="t-hd" style="font-size:96px"><span class="tt" style="display:inline-block">TRADES <span class="g">REALES</span></span></div><div class="ul" id="t-ul"></div>'
    + tw +
    '<svg class="chk" id="t-chk" viewBox="0 0 320 320"><circle id="t-c1" cx="160" cy="160" r="140" fill="rgba(0,0,0,.55)" stroke="#000" stroke-width="30" pathLength="100"/><circle id="t-c2" cx="160" cy="160" r="140" fill="none" stroke="#FFC21A" stroke-width="16" stroke-linecap="round" pathLength="100"/>'
    '<path id="t-k1" d="M92 170 L142 220 L232 112" fill="none" stroke="#000" stroke-width="44" stroke-linecap="round" stroke-linejoin="round" pathLength="100"/><path id="t-k2" d="M92 170 L142 220 L232 112" fill="none" stroke="#fff" stroke-width="26" stroke-linecap="round" stroke-linejoin="round" pathLength="100"/></svg>'
    '<div class="seal" id="t-seal"><div class="sh" id="t-sh"></div>100% CONFIABLE</div><div class="cnt" id="t-cnt"><span class="n">+<span id="t-n">0</span></span><span class="l">REFERENCIAS</span></div></div>', '''
  const W = D.w, N = D.n, f = W * N;
  tl.fromTo("#t-bm", { rotation: -20 }, { rotation: 25, duration: D.dur, ease: "none" }, 0);
  tl.fromTo("#t-hd .tt", { y: -90, opacity: 0, scale: 1.4 }, { y: 0, opacity: 1, scale: 1, duration: .3, ease: "back.out(2)" }, .06);
  tl.fromTo("#t-ul", { scaleX: 0, opacity: 0 }, { scaleX: 1, opacity: 1, duration: .25 }, .2);
  for (let k = 0; k < N; k++) {
    const t = W * k, id = "#t-w" + k;
    tl.fromTo(id, { x: 120, opacity: 0, scale: 1 }, { x: 0, opacity: 1, duration: .08, ease: "power3.out" }, t);
    tl.to(id, { scale: 1.07, duration: W - .06, ease: "none" }, t + .02);
    tl.to(id, { x: -70, opacity: 0, duration: .06, ease: "power2.in" }, t + W - .06);
  }
  ["#t-c1", "#t-c2", "#t-k1", "#t-k2"].forEach(s => gsap.set(s, { strokeDasharray: 100 }));
  tl.fromTo("#t-chk", { opacity: 0, scale: .6 }, { opacity: 1, scale: 1, duration: .2, ease: "back.out(1.8)" }, f);
  tl.fromTo(["#t-c1", "#t-c2"], { strokeDashoffset: 100 }, { strokeDashoffset: 0, duration: .3, ease: "power2.out" }, f + .02);
  tl.fromTo(["#t-k1", "#t-k2"], { strokeDashoffset: 100 }, { strokeDashoffset: 0, duration: .22, ease: "power2.out" }, f + .22);
  tl.fromTo("#t-seal", { scale: 2.2, opacity: 0 }, { scale: 1, opacity: 1, duration: .24, ease: "power4.in" }, f + .16);
  tl.fromTo("#t-sh", { x: -140, opacity: .9 }, { x: 900, opacity: .9, duration: .45, ease: "power2.inOut" }, f + .4);
  tl.fromTo("#t-cnt", { y: 60, opacity: 0 }, { y: 0, opacity: 1, duration: .25, ease: "back.out(2)" }, f + .2);
  tl.fromTo("#t-n", { textContent: 0 }, { textContent: 100, snap: { textContent: 1 }, duration: .8, ease: "power2.out" }, f + .3);
''', dict(dur=DUR["trust"], w=WIN, n=N_TR)))
for i in range(N_TR): sfx(T_TRUST + i * WIN + .01, "whoosh_soft", .22)
sfx(T_TRUST + T_CLEAN + .28, "ach", .8, 3)
for k in range(5): sfx(T_TRUST + T_CLEAN + .34 + k * .15, "tick", .18)

# ---------------------------------------------------------------- 8 · CIERRE
def ctwords(lines, cls=""):
    return "".join('<span class="ln">%s</span>' % " ".join(mask('<span class="wd %s">%s</span>' % (cls, w)) for w in ln) for ln in lines)
write("close", comp("close", DUR["close"],
    '<div class="scn" id="c"><div class="beam" id="c-bm"></div><div class="hrays" id="c-rays"></div>'
    '<div class="ct" id="c-t1" style="top:310px;font-size:122px">' + ctwords([["ESCRÍBEME"], ["POR DM EN"], ["TIKTOK"]]) + '</div>'
    '<svg class="arrow" id="c-arrow" viewBox="0 0 180 110"><g fill="none" stroke="#FFC21A" stroke-width="18" stroke-linecap="round" stroke-linejoin="round"><path id="c-a0" d="M30 6 L90 44 L150 6"/><path id="c-a1" d="M30 42 L90 80 L150 42"/><path id="c-a2" d="M30 78 L90 116 L150 78"/></g></svg>'
    '<div class="neon" id="c-neon">' + HANDLE + '</div>'
    '<div class="ct" id="c-t2" style="top:1060px;font-size:84px">' + ctwords([["SUBE DE NIVEL"], ["TU INVENTARIO"]], "g") + '</div>'
    '<div class="phrase c-gold" id="c-ph" style="font-size:56px"><span class="pw">VENTA SOLO EN MÉXICO</span></div></div>', '''
  tl.fromTo("#c-bm", { rotation: -30 }, { rotation: 25, duration: D.dur, ease: "none" }, 0);
  tl.fromTo("#c-rays", { rotation: 0, opacity: 0 }, { rotation: 40, opacity: .8, duration: D.dur, ease: "none" }, 0);
  document.querySelectorAll("#c-t1 .rv").forEach((el, i) => tl.fromTo(el, { y: 220, rotation: 5 }, { y: 0, rotation: 0, duration: .4, ease: "expo.out" }, .1 + i * .12));
  tl.fromTo("#c-arrow", { y: -30, opacity: 0 }, { y: 0, opacity: 1, duration: .25, ease: "power3.out" }, .55);
  [0, 1, 2].forEach(i => tl.fromTo("#c-a" + i, { opacity: .15, y: -8 }, { opacity: 1, y: 10, duration: .3, yoyo: true, repeat: 7, ease: "sine.inOut" }, .6 + i * .1));
  [[0, .1], [.07, 0], [.14, .1], [.22, 0], [.3, 1]].forEach(f => tl.set("#c-neon", { opacity: f[1] }, .8 + f[0]));
  tl.fromTo("#c-neon", { scale: .85 }, { scale: 1, duration: .4, ease: "back.out(2)" }, 1.05);
  tl.to("#c-neon", { scale: 1.03, duration: .35, yoyo: true, repeat: 4, ease: "sine.inOut" }, 1.5);
  document.querySelectorAll("#c-t2 .rv").forEach((el, i) => tl.fromTo(el, { y: 200 }, { y: 0, duration: .4, ease: "expo.out" }, 1.35 + i * .16));
  tl.fromTo("#c-ph .pw", { y: 30, opacity: 0 }, { y: 0, opacity: 1, duration: .28 }, 1.8);
''', dict(dur=DUR["close"])))
for i in range(5): sfx(T_CLOSE + .1 + i * .12 + .1, "slam", .2)
sfx(T_CLOSE + .85, "neon", .4); sfx(T_CLOSE + 1.35, "whoosh_soft", .3)

# ---------------------------------------------------------------- TRANSICIONES (0.3–0.4 s, ninguna repetida seguida)
bounds = [T_INTRO, T_PERM, T_FIS, T_GP, T_SKIN, T_TRUST, T_CLOSE]
kinds = ["sweep", "zoom", "glitch", "slats", "wave", "sweep2", "curtain"]
slats = "".join('<div class="slat" id="fx-sl%d" style="left:%dpx;background:%s"></div>' % (i, i * 135, "#FFC21A" if i % 2 else "#07070a") for i in range(8))
rsl = random.Random(2)
gsl = [dict(y=i * 275 - 20, h=295, c=["#000", "#FFC21A", "#fff", "#00f0ff", "#ff2bd6", "#FFC21A", "#000"][i], dx=rsl.choice([-1, 1])) for i in range(7)]
gl_html = "".join('<div class="sl" id="fx-gl%d" style="top:%dpx;height:%dpx;background:%s"></div>' % (i, o["y"], o["h"], o["c"]) for i, o in enumerate(gsl))
write("fx", comp("fx", TOTAL,
    '<div class="sweep" id="fx-s1"></div><div class="sweep silver" id="fx-s2"></div><div class="flash" id="fx-gd" style="background:#FFC21A"></div>' + gl_html + slats +
    '<div class="curt" id="fx-c1" style="top:0;border-bottom:8px solid #FFC21A"></div><div class="curt" id="fx-c2" style="top:940px;border-top:8px solid #FFC21A"></div>'
    '<div class="shock" id="fx-shock"></div><div class="flash" id="fx-gf" style="background:#FFC21A;opacity:.94"></div>', '''
  const FT = (s, a, c, t) => tl.fromTo(s, a, { ...c, immediateRender: false }, t);
  const [b1, b2, b3, b4, b5, b6, b7] = D.B, T = D.total;
  tl.to("#fx-gf", { opacity: 0, duration: .45, ease: "power2.out" }, 0);                               // destello dorado inicial (gancho)
  FT("#fx-s1", { x: -300, opacity: 1 }, { x: 1900, opacity: 1, duration: .38, ease: "power2.inOut" }, b1 - .19);
  tl.set("#fx-s1", { opacity: 0 }, b1 + .22);
  FT("#fx-gd", { opacity: 0 }, { opacity: .8, duration: .1, ease: "power2.in" }, b2 - .1);
  tl.to("#fx-gd", { opacity: 0, duration: .22, ease: "power2.out" }, b2);
  D.gl.forEach((o, i) => {
    FT("#fx-gl" + i, { x: o.dx * -1200, opacity: 1 }, { x: 0, duration: .12, ease: "power2.out" }, b3 - .18 + i * .012);
    tl.to("#fx-gl" + i, { x: o.dx * 1200, duration: .13, ease: "power2.in" }, b3 + i * .012);
    tl.set("#fx-gl" + i, { opacity: 0 }, b3 + .26);
  });
  for (let i = 0; i < 8; i++) {
    FT("#fx-sl" + i, { y: -1950, opacity: 1 }, { y: 0, duration: .13, ease: "power2.out" }, b4 - .16 + i * .012);
    tl.to("#fx-sl" + i, { y: 1950, duration: .13, ease: "power2.in" }, b4 + i * .012);
    tl.set("#fx-sl" + i, { opacity: 0 }, b4 + .26);
  }
  FT("#fx-shock", { scale: .1, opacity: 1 }, { scale: 7, opacity: 0, duration: .5, ease: "power2.out" }, b5 - .1);
  FT("#fx-gd", { opacity: 0 }, { opacity: .8, duration: .08 }, b5 - .06);
  tl.to("#fx-gd", { opacity: 0, duration: .24 }, b5 + .02);
  FT("#fx-s2", { x: 0, opacity: 1 }, { x: -2100, opacity: 1, duration: .38, ease: "power2.inOut" }, b6 - .19);
  tl.set("#fx-s2", { opacity: 0 }, b6 + .22);
  FT("#fx-c1", { y: -985, opacity: 1 }, { y: 0, duration: .14, ease: "power3.out" }, b7 - .16);
  FT("#fx-c2", { y: 985, opacity: 1 }, { y: 0, duration: .14, ease: "power3.out" }, b7 - .16);
  tl.to("#fx-c1", { y: -985, duration: .14, ease: "power3.in" }, b7 + .02);
  tl.to("#fx-c2", { y: 985, duration: .14, ease: "power3.in" }, b7 + .02);
  tl.set(["#fx-c1", "#fx-c2"], { opacity: 0 }, b7 + .24);
  FT("#fx-gf", { opacity: 0 }, { opacity: .94, duration: .42, ease: "power2.in" }, T - .45);          // destello dorado final = inicio (bucle)
''', dict(B=bounds, gl=gsl, total=TOTAL)))
wh = dict(sweep="whoosh_up", zoom="whoosh_zoom", glitch="glitch", slats="whoosh_slats", wave="shock", sweep2="whoosh_down", curtain="whoosh_curtain")
for b_, kd in zip(bounds, kinds): sfx(b_ - .2, wh[kd], .5, 3)

# ---------------------------------------------------------------- index.html
mounts = [("bg", 0, TOTAL, 0, "m-bg"), ("hook", T_HOOK, DUR["hook"], 1, "m-scn"), ("intro", T_INTRO, DUR["intro"], 1, "m-scn")]
for c in ("perm", "fis", "gp", "skin"): mounts.append(("scene-" + c, SC[c][0], DUR[c], 1, "m-scn"))
mounts += [("trust", T_TRUST, DUR["trust"], 1, "m-scn"), ("close", T_CLOSE, DUR["close"], 1, "m-scn"), ("fx", 0, TOTAL, 3, "m-fx"), ("hud", 0, TOTAL, 4, "m-hud")]
mh = "\n  ".join('<div id="mt-%s" class="clip mount %s" data-composition-id="%s" data-composition-src="compositions/%s.html" data-start="%s" data-duration="%s" data-track-index="%d"></div>'
                % (c, cl, c, c, round(s, 4), round(d, 4), tr) for c, s, d, tr, cl in mounts)
open(os.path.join(ROOT, "index.html"), "w").write('''<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=1080, height=1920">
<title>Promo MonZ - Showreel</title>
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
''' % (TOTAL, mh, TOTAL, TOTAL))
json.dump(dict(total=TOTAL, bpm=BPM, beat=BEAT, events=EV, bounds=bounds, sc={k: v for k, v in SC.items()}), open(os.path.join(ROOT, "timeline.json"), "w"), indent=1)
if os.environ.get("SKIP_AUDIO") != "1":
    import audio; audio.render(ROOT)
print("OK", TOTAL)
