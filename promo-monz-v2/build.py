#!/usr/bin/env python3
"""Promo MonZ v2 · tienda (TikTok 1080x1920, 30 fps, ~44 s, SIN voz).

Una composición Hyperframes por escena y por bloque de piezas (compositions/*.html).
Uso:  python3 prep_pieces.py && python3 prep_trades.py && python3 build.py
      npx hyperframes render -o out/promo-monz.mp4
"""
import json, os
from PIL import Image
from data import CATS
ROOT = os.path.dirname(os.path.abspath(__file__))
os.makedirs(os.path.join(ROOT, "compositions"), exist_ok=True)
HANDLE = "@monzmc05"
BPM = 138.4615384615
BEAT = 60 / BPM

# ------------------------------------------------------------------------------------------
# datos
# ------------------------------------------------------------------------------------------
M = json.load(open(os.path.join(ROOT, "pieces.json")))
by = {c["key"]: [m for m in M if m["cat"] == c["key"]] for c in CATS}
CAT = {c["key"]: c for c in CATS}
TITLE_FS = dict(perm=68, fis=84, gp=104, skin=126)
PHRASE = dict(perm=["PERMANENTES", "AL", "MEJOR", "PRECIO"], fis=["LAS", "TIENES", "YA"], gp=["POTENCIA", "TU", "CUENTA"], skin=["LUCE", "DIFERENTE"])

# ------------------------------------------------------------------------------------------
# línea de tiempo (en compases)
# ------------------------------------------------------------------------------------------
BLK_BEATS = 6; BLK = BLK_BEATS * BEAT          # 2.6 s por bloque de piezas
EXIT_AT, EXIT_D = 2.47, .13                    # salida de piezas dentro del bloque
S0, SG, ENTRY = .10, .10, .36                  # primera entrada, escalonado (0.1 s), duración del giro
t = 0.0
def adv(beats):
    global t; a = t; t += beats * BEAT; return a
T_GANCHO = adv(5); T_PRES = adv(5)
blocks = []; cats = []
for c in CATS:
    items = by[c["key"]]; i = 0; start = t
    for bi, n in enumerate(c["blocks"]):
        blocks.append(dict(cat=c["key"], idx=bi, items=items[i:i + n], start=t, id="%s%d" % (c["key"], bi + 1))); i += n; adv(BLK_BEATS)
    cats.append(dict(key=c["key"], start=start, dur=t - start))
T_TRADES = adv(12); T_CIERRE = adv(8)
TOTAL = round(t, 3)
D_GANCHO = 5 * BEAT; D_PRES = 5 * BEAT; D_TRADES = 12 * BEAT; D_CIERRE = 8 * BEAT
print("total", TOTAL, "s |", len(blocks), "bloques")
assert 40 <= TOTAL <= 45, TOTAL

EV = []   # eventos de sonido: (t, tipo, volumen, prioridad)
def sfx(t_, kind, vol=1.0, pr=1): EV.append((round(t_, 3), kind, vol, pr))

def comp(cid, dur, inner, js, data=None):
    return ('<template id="' + cid + '-template">\n<div data-composition-id="' + cid + '" data-width="1080" data-height="1920" data-start="0" data-duration="' + str(round(dur, 3)) + '">\n'
            + inner + '\n<script>\n(function () {\n  const tl = gsap.timeline({ paused: true });\n  const D = ' + json.dumps(data if data is not None else {}, ensure_ascii=False) + ';\n'
            + js + '\n  window.__timelines = window.__timelines || {};\n  window.__timelines["' + cid + '"] = tl;\n})();\n</script>\n</div>\n</template>\n')
def write(name, text): open(os.path.join(ROOT, "compositions", name + ".html"), "w").write(text)
def mask(inner): return '<span class="mask"><span class="rv" style="display:inline-block">' + inner + '</span></span>'
def gtw(text, cls=""): return '<span class="gtw"><span class="o">' + text + '</span><span class="f ' + cls + '">' + text + '</span></span>'

# ------------------------------------------------------------------------------------------
# FONDO y HUD (permanentes)
# ------------------------------------------------------------------------------------------
import random
r = random.Random(5)
dust = [dict(d=round(r.uniform(8, 15), 2), dl=round(r.uniform(0, 7), 2)) for _ in range(30)]
spk = "".join('<i class="sp" id="bgs%d" style="left:%dpx;width:%dpx;height:%dpx"></i>' % (i, r.randint(0, 1060), s, s) for i in range(30) for s in [r.choice([6, 8, 10, 14])])
write("bg", comp("bg", TOTAL,
    '<div class="fill" id="bg-w"><div class="carbon" id="bg-c"></div><div class="haze"></div><div class="beam" id="bg-b1"></div><div class="beam b2" id="bg-b2"></div></div>' + spk,
    '''
  tl.fromTo("#bg-w", { scale: 1 }, { scale: 1.08, duration: D.total, ease: "none" }, 0);
  tl.fromTo("#bg-c", { x: 0, y: 0 }, { x: -110, y: -150, duration: D.total, ease: "none" }, 0);
  tl.fromTo("#bg-b1", { rotation: -30 }, { rotation: 30, duration: D.total, ease: "none" }, 0);
  tl.fromTo("#bg-b2", { rotation: 35 }, { rotation: -25, duration: D.total, ease: "none" }, 0);
  D.dust.forEach((o, i) => tl.fromTo("#bgs" + i, { y: 2000, opacity: 0, scale: .6 }, { y: -120, opacity: .9, scale: 1.1, duration: o.d, repeat: Math.ceil(D.total / o.d), ease: "none" }, o.dl));
''', dict(total=TOTAL, dust=dust)))
write("hud", comp("hud", TOTAL,
    '<div class="hud-flag" id="hud-fl" style="left:28px">🇲🇽</div><div class="hud-flag" id="hud-fr" style="right:28px">🇲🇽</div>'
    '<div class="hud-handle" id="hud-hd">' + HANDLE + '</div><div class="hud-tag" id="hud-tg">SOLO <b>MÉXICO</b> 🇲🇽</div>',
    '''
  tl.fromTo("#hud-fl", { y: -120, opacity: 0 }, { y: 0, opacity: 1, duration: .5, ease: "back.out(2)" }, .15);
  tl.fromTo("#hud-fr", { y: -120, opacity: 0 }, { y: 0, opacity: 1, duration: .5, ease: "back.out(2)" }, .22);
  tl.fromTo("#hud-hd", { x: -200, opacity: 0 }, { x: 0, opacity: 1, duration: .45, ease: "power3.out" }, .3);
  tl.fromTo("#hud-tg", { y: -60, opacity: 0 }, { y: 0, opacity: 1, duration: .45, ease: "power3.out" }, .36);
  tl.to("#hud-fl", { rotation: 4, duration: 1, yoyo: true, repeat: Math.ceil(D.total), ease: "sine.inOut" }, .8);
  tl.to("#hud-fr", { rotation: -4, duration: 1, yoyo: true, repeat: Math.ceil(D.total), ease: "sine.inOut" }, 1);
''', dict(total=TOTAL)))

# ------------------------------------------------------------------------------------------
# ESCENA · GANCHO  (negro → destello dorado, "¿PAGANDO DE MÁS? 😱" y luego "AQUÍ NO 🔥")
# ------------------------------------------------------------------------------------------
def words(cls, fs, top, ws, idp):
    return '<div class="gt %s" id="%s" style="top:%dpx;font-size:%dpx">%s</div>' % (cls, idp, top, fs, "".join('<span class="ln">%s</span>' % " ".join('<span class="w">%s</span>' % w for w in ln) for ln in ws))
g1 = [["¿PAGANDO"], ["DE MÁS? 😱"]]; g2 = [["AQUÍ NO 🔥"]]
write("gancho", comp("gancho", D_GANCHO,
    '<div class="scn" id="g"><div class="rays" id="g-rays"></div><div class="burst" id="g-burst"></div><div class="fill" id="g-black" style="background:#000"></div>'
    '<div class="fill" id="g-cam">' + words("cy", 150, 600, g1, "g1c") + words("mg", 150, 600, g1, "g1m") + words("gold", 150, 600, g1, "g1") + words("white", 150, 800, g2, "g2") + '</div>'
    '<div class="fill" id="g-wh" style="background:#fff;opacity:0"></div></div>',
    '''
  tl.to("#g-black", { opacity: 0, duration: .2, ease: "power2.out" }, .08);
  tl.fromTo("#g-wh", { opacity: 0 }, { opacity: .9, duration: .05, ease: "none" }, .08);
  tl.to("#g-wh", { opacity: 0, duration: .3, ease: "power2.out" }, .13);
  tl.fromTo("#g-burst", { scale: 0, opacity: .95 }, { scale: 6, opacity: 0, duration: .7, ease: "expo.out" }, .1);
  tl.fromTo("#g-rays", { rotation: 0, opacity: 0 }, { rotation: 35, opacity: 1, duration: D.dur, ease: "none" }, .1);
  tl.fromTo("#g-cam", { scale: .85 }, { scale: 1.1, duration: D.dur - .1, ease: "power1.in" }, 0);
  ["#g1c", "#g1m", "#g1"].forEach(L => document.querySelectorAll(L + " .w").forEach((el, i) =>
    tl.fromTo(el, { y: 260, scale: 2.8, opacity: 0, rotation: i % 2 ? 8 : -8 }, { y: 0, scale: 1, opacity: 1, rotation: 0, duration: .32, ease: "back.out(1.5)" }, .22 + i * .1)));
  tl.fromTo("#g1c", { x: 0, opacity: 0 }, { x: 16, opacity: .9, duration: .05, yoyo: true, repeat: 5, ease: "none" }, .85);
  tl.fromTo("#g1m", { x: 0, opacity: 0 }, { x: -16, opacity: .9, duration: .05, yoyo: true, repeat: 5, ease: "none" }, .85);
  ["#g1c", "#g1m", "#g1"].forEach(L => tl.to(L, { scale: 1.25, opacity: 0, duration: .13, ease: "power2.in" }, 1.0));
  tl.fromTo("#g2 .w", { scale: 3, opacity: 0, rotation: -6 }, { scale: 1, opacity: 1, rotation: 0, duration: .3, ease: "back.out(1.5)" }, 1.18);
  tl.to("#g2", { scale: 1.06, duration: .8, ease: "power1.in" }, 1.3);
''', dict(dur=D_GANCHO)))
sfx(T_GANCHO + .1, "boom", .8, 3); sfx(T_GANCHO + .25, "slam", .35); sfx(T_GANCHO + .35, "slam", .35); sfx(T_GANCHO + .85, "glitch", .35)
sfx(T_GANCHO + 1.18, "slam", .5, 2)

# ------------------------------------------------------------------------------------------
# ESCENA · PRESENTACIÓN (MONZ STORE con brillo, frase, 4 íconos)
# ------------------------------------------------------------------------------------------
icons = [("perm", by["perm"][0], "PERMANENTES"), ("fis", by["fis"][0], "FÍSICAS"), ("gp", by["gp"][0], "GAMEPASSES"), ("skin", by["skin"][0], "SKINS")]
mini = "".join('<div class="mini c-%s" id="p-m%d" style="left:%dpx;top:860px"><div class="d" id="p-d%d"></div><img src="assets/pieces/%s"><div class="lb">%s</div></div>' % (k, i, 40 + i * 225, i, m["file"], lb) for i, (k, m, lb) in enumerate(icons))
write("presentacion", comp("presentacion", D_PRES,
    '<div class="scn" id="p"><div class="beam" id="p-beam"></div>'
    '<div class="mz" id="p-t1" style="top:380px">' + mask(gtw("MONZ")) + '</div><div class="mz" id="p-t2" style="top:560px;font-size:150px">' + mask(gtw("STORE", "wh")) + '</div>' + mini +
    '<div class="phrase c-perm" id="p-ph">' + "".join('<span class="pw%s">%s</span>' % (" a" if w == "INVENTARIO" else "", w) for w in ["TODO", "PARA", "TU", "INVENTARIO"]) + '</div></div>',
    '''
  tl.fromTo("#p-beam", { rotation: -25 }, { rotation: 25, duration: D.dur, ease: "none" }, 0);
  document.querySelectorAll("#p-t1 .rv, #p-t2 .rv").forEach((el, i) => tl.fromTo(el, { y: 240 }, { y: 0, duration: .5, ease: "expo.out" }, .12 + i * .15));
  document.querySelectorAll("#p-t1 .f, #p-t2 .f").forEach((el, i) => tl.fromTo(el, { backgroundPosition: "160% 0, 0 0" }, { backgroundPosition: "-60% 0, 0 0", duration: .9, ease: "power2.inOut" }, .5 + i * .18));
  [0, 1, 2, 3].forEach(i => {
    tl.fromTo("#p-m" + i, { y: 90, scale: .5, opacity: 0, rotationY: 90 }, { y: 0, scale: 1, opacity: 1, rotationY: 0, duration: .4, ease: "back.out(1.6)" }, .8 + i * .1);
    tl.to("#p-m" + i + " img", { y: -5, duration: .7, yoyo: true, repeat: 3, ease: "sine.inOut" }, 1.25 + i * .1);
  });
  document.querySelectorAll("#p-ph .pw").forEach((el, i) => tl.fromTo(el, { y: 30, opacity: 0 }, { y: 0, opacity: 1, duration: .25, ease: "power3.out" }, .95 + i * .1));
  tl.to(["#p-t1", "#p-t2"], { scale: 7, opacity: 0, duration: .4, ease: "power3.in" }, D.dur - .4);
  tl.to(["#p-m0", "#p-m1", "#p-m2", "#p-m3", "#p-ph"], { opacity: 0, scale: .9, duration: .22, ease: "power2.in" }, D.dur - .36);
''', dict(dur=D_PRES)))
for i in range(4): sfx(T_PRES + .8 + .1 * i + .1, "pop", .35)
sfx(T_PRES + .55, "shine", .35)

# ------------------------------------------------------------------------------------------
# MARCO DE CATEGORÍA (cabecera, frase, tinte) + BLOQUES DE PIEZAS
# ------------------------------------------------------------------------------------------
for c in cats:
    k = c["key"]; title = CAT[k]["title"]
    if k == "perm":
        th = '<div class="hd c-perm" id="%s-hd" style="font-size:%dpx">%s</div>' % (k, TITLE_FS[k], "".join('<span class="lt">%s</span>' % (ch if ch != " " else "&nbsp;") for ch in title))
    else:
        th = '<div class="hd %s" id="%s-hd" style="font-size:%dpx"><span class="tt" style="display:inline-block">%s</span></div>' % ("c-" + k, k, TITLE_FS[k], title)
    ph = '<div class="phrase c-%s" id="%s-ph">%s</div>' % (k, k, "".join('<span class="pw%s">%s</span>' % (" a" if j == 0 else "", w) for j, w in enumerate(PHRASE[k])))
    reveal = dict(
        perm='document.querySelectorAll("#perm-hd .lt").forEach((el, i) => tl.fromTo(el, { y: -120, opacity: 0, rotationX: 80 }, { y: 0, opacity: 1, rotationX: 0, duration: .35, ease: "back.out(2)" }, .22 + i * .03));',
        fis='tl.fromTo("#fis-hd .tt", { x: -520, skewX: 28, opacity: 0 }, { x: 0, skewX: 0, opacity: 1, duration: .45, ease: "expo.out" }, .22);',
        gp='tl.fromTo("#gp-hd .tt", { scale: 1.5, opacity: 0 }, { scale: 1, opacity: 1, duration: .45, ease: "expo.out" }, .22);',
        skin='tl.fromTo("#skin-hd .tt", { y: 140, opacity: 0, scale: .6 }, { y: 0, opacity: 1, scale: 1, duration: .5, ease: "back.out(1.8)" }, .22);')[k]
    write("cat-" + k, comp("cat-" + k, c["dur"],
        '<div class="scn c-%s" id="%s-f"><div class="hz-t"></div><div class="hz-b"></div><div class="beam tint" id="%s-bm"></div>%s<div class="ul" id="%s-ul"></div>%s</div>' % (k, k, k, th, k, ph),
        reveal + '''
  const k = D.k;
  tl.fromTo("#" + k + "-bm", { rotation: -25 }, { rotation: 30, duration: D.dur, ease: "none" }, 0);
  tl.fromTo("#" + k + "-ul", { scaleX: 0, opacity: 0 }, { scaleX: 1, opacity: 1, duration: .4, ease: "power3.out" }, .35);
  document.querySelectorAll("#" + k + "-ph .pw").forEach((el, i) => tl.fromTo(el, { y: 36, opacity: 0 }, { y: 0, opacity: 1, duration: .28, ease: "power3.out" }, .5 + i * .1));
  tl.fromTo("#" + k + "-f", { scale: 1 }, { scale: 1.035, duration: D.dur, ease: "none" }, 0);
''', dict(k=k, dur=c["dur"])))

def layout(n):
    xs = [40, 510]
    if n == 6: return [(xs[i % 2], 300 + 370 * (i // 2)) for i in range(6)]
    if n == 4: return [(xs[i % 2], 495 + 370 * (i // 2)) for i in range(4)]
    if n == 3: return [(xs[0], 495), (xs[1], 495), (275, 865)]
    raise ValueError(n)

CROWN = '<svg viewBox="0 0 30 22"><path d="M2 20 L4 5 L10 12 L15 2 L20 12 L26 5 L28 20 Z" fill="#FFC21A" stroke="#fff3b0" stroke-width="1.5" stroke-linejoin="round"/></svg>'
for b in blocks:
    k = b["cat"]; n = len(b["items"]); pos = layout(n)
    top = max(range(n), key=lambda i: (b["items"][i]["price"], -i))
    h = ""
    for i, (it, (x, y)) in enumerate(zip(b["items"], pos)):
        p = "%s-p%d" % (b["id"], i); nm = it["name"]; cls = "xs" if len(nm) > 20 else ("s" if len(nm) > 18 else ("m" if len(nm) > 16 else "l"))
        h += ('<div class="pc c-%s" id="%s" style="left:%dpx;top:%dpx"><div class="pc-bg"></div>%s<div class="pc-disc" id="%s-disc"></div><div class="pc-sh"></div>'
              '<img class="pc-ico" id="%s-ico" src="assets/pieces/%s"><div class="pc-shine" id="%s-shine"></div><div class="pc-wash" id="%s-wash"></div>%s'
              '<div class="pc-nm %s">%s</div><div class="pc-flash" id="%s-fl"></div><div class="pc-pr" id="%s-pr"><span class="in"><span class="coin">$</span><span class="num">%d</span><span class="mxn">MXN</span></span></div></div>'
              % (k, p, x, y - 290, ('<div class="pc-rays" id="%s-rays"></div>' % p) if i == top else "", p, p, it["file"], p, p,
                 ('<div class="pc-top" id="%s-top">%s<b style="font-weight:400">TOP</b></div>' % (p, CROWN)) if i == top else "", cls, nm, p, p, it["price"]))
        t0 = b["start"] + S0 + SG * i
        sfx(t0 + .05, "pop", .30)
        if i == top: sfx(t0 + ENTRY + .02, "coin", .42, 2)
    write("blk-" + b["id"], comp("blk-" + b["id"], BLK, '<div class="zone">' + h + '</div>', '''
  const E = D.E;
  for (let i = 0; i < D.n; i++) {
    const p = "#" + D.bid + "-p" + i, t = D.s0 + D.sg * i, end = t + E;
    gsap.set(p, { transformPerspective: 900 });
    if (D.cat === "perm") tl.fromTo(p, { rotationY: -100, y: 40, opacity: 0, scale: .92 }, { rotationY: 0, y: 0, opacity: 1, scale: 1, duration: E, ease: "back.out(1.5)" }, t);
    else if (D.cat === "fis") tl.fromTo(p, { y: -560, rotationX: 55, opacity: 0 }, { y: 0, rotationX: 0, opacity: 1, duration: E, ease: "bounce.out" }, t);
    else if (D.cat === "gp") tl.fromTo(p, { x: (i % 2 ? 650 : -650), rotationY: (i % 2 ? -80 : 80), opacity: 0 }, { x: 0, rotationY: 0, opacity: 1, duration: E, ease: "back.out(1.3)" }, t);
    else {
      tl.fromTo(p, { scale: 1.35, rotationY: 110, opacity: 0 }, { scale: 1, rotationY: 0, opacity: 1, duration: E, ease: "expo.out" }, t);
      tl.fromTo(p + "-wash", { opacity: .5 }, { opacity: 0, duration: .3, ease: "power2.out" }, t + E - .05);
    }
    tl.fromTo(p + "-pr", { scale: 1.6, opacity: 0 }, { scale: 1, opacity: 1, duration: .12, ease: "power3.in" }, end);
    tl.to(p + "-pr", { y: 2, duration: .04, yoyo: true, repeat: 1, ease: "none" }, end + .12);
    tl.fromTo(p + "-fl", { scale: .85, opacity: .95 }, { scale: 1.55, opacity: 0, duration: .32, ease: "power2.out", immediateRender: false }, end + .1);
    tl.fromTo(p + "-shine", { x: -150, opacity: .85 }, { x: 560, opacity: .85, duration: .5, ease: "power2.inOut" }, end + .14);
    tl.to(p + "-ico", { y: -5, duration: .8, yoyo: true, repeat: 3, ease: "sine.inOut" }, end + .2);
    tl.fromTo(p + "-disc", { scale: 1 }, { scale: 1.05, duration: 1.1, yoyo: true, repeat: 2, ease: "sine.inOut" }, end + .1);
    if (D.top === i) {
      tl.fromTo(p + "-top", { scale: 0, rotation: -20 }, { scale: 1, rotation: 0, duration: .3, ease: "back.out(2.2)" }, end + .05);
      tl.fromTo(p + "-rays", { opacity: 0, rotation: 0 }, { opacity: .55, rotation: 50, duration: 2.5, ease: "none" }, t);
    }
    tl.to(p, { opacity: 0, y: -14, scale: .96, duration: D.xd, ease: "power1.in" }, D.xa + i * .012);
  }
''', dict(cat=k, n=n, bid=b["id"], top=top, E=ENTRY, s0=S0, sg=SG, xa=EXIT_AT, xd=EXIT_D)))

# ------------------------------------------------------------------------------------------
# ESCENA · TRADES + CONFIANZA
# ------------------------------------------------------------------------------------------
TR = ["kitsune", "portal_yeti", "portal_bran", "dragon", "darkblade"]
tw = ""
for i, n in enumerate(TR):
    w, h_ = Image.open(os.path.join(ROOT, "assets/trades/%s.png" % n)).size; hh = round(860 * h_ / w)
    tw += '<div class="tw" id="t-w%d" style="top:%dpx;height:%dpx"><img src="assets/trades/%s.png"></div>' % (i, 850 - hh // 2, hh, n)
WIN = .8
write("trades", comp("trades", D_TRADES,
    '<div class="scn c-perm" id="t"><div class="hz-t"></div><div class="hz-b"></div><div class="beam tint" id="t-bm"></div><div class="hd" id="t-hd" style="font-size:78px"><span class="tt" style="display:inline-block">TRADES <span class="g">REALES</span> ✅</span></div><div class="ul" id="t-ul"></div>'
    + tw + '<div class="dots" id="t-dots">' + "<i></i>" * 5 + '</div>'
    '<div class="seal" id="t-seal"><div class="sh" id="t-sh"></div>✅ 100% CONFIABLE</div><div class="cnt" id="t-cnt"><span class="n">+<span id="t-n">0</span></span><span class="l">REFERENCIAS</span></div></div>',
    '''
  tl.fromTo("#t-bm", { rotation: -20 }, { rotation: 25, duration: D.dur, ease: "none" }, 0);
  tl.fromTo("#t-hd .tt", { y: -90, opacity: 0, scale: 1.4 }, { y: 0, opacity: 1, scale: 1, duration: .4, ease: "back.out(2)" }, .08);
  tl.fromTo("#t-ul", { scaleX: 0, opacity: 0 }, { scaleX: 1, opacity: 1, duration: .35 }, .3);
  tl.fromTo("#t-dots", { opacity: 0 }, { opacity: 1, duration: .2 }, .1);
  for (let k = 0; k < D.n; k++) {
    const t = D.w * k, id = "#t-w" + k;
    tl.fromTo(id, { x: 140, opacity: 0, scale: 1, rotationY: -12 }, { x: 0, opacity: 1, rotationY: 0, duration: .16, ease: "power3.out" }, t);
    tl.to(id, { scale: 1.06, duration: D.w - .08, ease: "none" }, t + .08);
    tl.to(id, { x: -90, opacity: 0, duration: .1, ease: "power2.in" }, t + D.w - .12);
    document.querySelectorAll("#t-dots i").forEach((d, j) => tl.set(d, { className: j === k ? "on" : "" }, t));
  }
  const f = D.w * D.n;
  tl.to("#t-dots", { opacity: 0, duration: .15 }, f - .05);
  tl.fromTo("#t-seal", { scale: 2.6, rotation: -10, opacity: 0 }, { scale: 1, rotation: 0, opacity: 1, duration: .32, ease: "power4.in" }, f + .02);
  tl.to("#t-seal", { y: 4, duration: .05, yoyo: true, repeat: 1 }, f + .34);
  tl.fromTo("#t-sh", { x: -140, opacity: .9 }, { x: 900, opacity: .9, duration: .6, ease: "power2.inOut" }, f + .42);
  tl.fromTo("#t-cnt", { y: 70, opacity: 0 }, { y: 0, opacity: 1, duration: .3, ease: "back.out(2)" }, f + .22);
  tl.fromTo("#t-n", { textContent: 0 }, { textContent: 100, snap: { textContent: 1 }, duration: .8, ease: "power2.out" }, f + .3);
''', dict(dur=D_TRADES, n=5, w=WIN)))
for i in range(5): sfx(T_TRADES + WIN * i + .02, "whoosh_soft", .3)
sfx(T_TRADES + 5 * WIN + .3, "ach", .8, 3)
for i in range(6): sfx(T_TRADES + 5 * WIN + .34 + i * .13, "tick", .22)

# ------------------------------------------------------------------------------------------
# ESCENA · CIERRE
# ------------------------------------------------------------------------------------------
def ctwords(lines, cls="", extra=""):
    return "".join('<span class="ln">%s</span>' % " ".join(mask('<span class="wd %s">%s</span>' % (cls, w)) for w in ln) for ln in lines)
write("cierre", comp("cierre", D_CIERRE,
    '<div class="scn" id="c"><div class="beam" id="c-bm"></div><div class="rays" id="c-rays" style="opacity:.8"></div>'
    '<div class="ct" id="c-t1" style="top:320px;font-size:128px">' + ctwords([["ESCRÍBEME"], ["POR DM EN"], ["TIKTOK 📩"]]) + '</div>'
    '<svg class="arrow" id="c-arrow" viewBox="0 0 180 110"><g fill="none" stroke="#FFC21A" stroke-width="18" stroke-linecap="round" stroke-linejoin="round"><path id="c-a0" d="M30 6 L90 44 L150 6"/><path id="c-a1" d="M30 42 L90 80 L150 42"/><path id="c-a2" d="M30 78 L90 116 L150 78"/></g></svg>'
    '<div class="neon" id="c-neon">' + HANDLE + '</div>'
    '<div class="ct" id="c-t2" style="top:1090px;font-size:86px">' + ctwords([["SUBE DE NIVEL"], ["TU INVENTARIO"]], "g") + '</div>'
    '<div class="phrase c-perm" id="c-ph" style="font-size:54px"><span class="pw">Venta solo en México 🇲🇽</span></div>'
    '<div class="fill" id="c-wh" style="background:#fff;opacity:0"></div></div>',
    '''
  tl.fromTo("#c-bm", { rotation: -30 }, { rotation: 25, duration: D.dur, ease: "none" }, 0);
  tl.fromTo("#c-rays", { rotation: 0 }, { rotation: 40, duration: D.dur, ease: "none" }, 0);
  document.querySelectorAll("#c-t1 .rv").forEach((el, i) => tl.fromTo(el, { y: 220, rotation: 5 }, { y: 0, rotation: 0, duration: .45, ease: "expo.out" }, .12 + i * .14));
  tl.fromTo("#c-arrow", { y: -30, opacity: 0 }, { y: 0, opacity: 1, duration: .3, ease: "power3.out" }, .6);
  [0, 1, 2].forEach(i => tl.fromTo("#c-a" + i, { opacity: .15, y: -8 }, { opacity: 1, y: 10, duration: .3, yoyo: true, repeat: 7, ease: "sine.inOut" }, .65 + i * .1));
  [[0, .1], [.07, 0], [.14, .1], [.22, 0], [.3, 1]].forEach(f => tl.set("#c-neon", { opacity: f[1] }, .85 + f[0]));
  tl.fromTo("#c-neon", { scale: .85 }, { scale: 1, duration: .45, ease: "back.out(2)" }, 1.1);
  tl.to("#c-neon", { scale: 1.03, duration: .35, yoyo: true, repeat: 5, ease: "sine.inOut" }, 1.6);
  document.querySelectorAll("#c-t2 .rv").forEach((el, i) => tl.fromTo(el, { y: 200 }, { y: 0, duration: .45, ease: "expo.out" }, 1.35 + i * .18));
  tl.fromTo("#c-ph .pw", { y: 30, opacity: 0 }, { y: 0, opacity: 1, duration: .3 }, 1.9);
  tl.fromTo("#c-wh", { opacity: 0 }, { opacity: .85, duration: .1, ease: "power2.out" }, D.dur - .38);
  tl.to("#c-wh", { opacity: 0, duration: .28, ease: "power2.in" }, D.dur - .27);
  tl.fromTo("#c", { scale: 1.0 }, { scale: .95, duration: .7, ease: "power2.inOut" }, D.dur - .7);
''', dict(dur=D_CIERRE)))
for i in range(5): sfx(T_CIERRE + .12 + i * .14 + .1, "slam", .22)
sfx(T_CIERRE + .9, "neon", .45); sfx(T_CIERRE + 1.35, "whoosh_soft", .35)

# ------------------------------------------------------------------------------------------
# TRANSICIONES (todas distintas, ninguna repetida seguida)
# ------------------------------------------------------------------------------------------
bounds = [T_PRES, cats[0]["start"], cats[1]["start"], cats[2]["start"], cats[3]["start"], T_TRADES, T_CIERRE]
kinds = ["sweep", "zoom", "slide", "slats", "sweep2", "curtain", "shock"]
slats = "".join('<div class="slat" id="fx-sl%d" style="left:%dpx;background:%s"></div>' % (i, i * 135, "#FFC21A" if i % 2 else "#07070a") for i in range(8))
write("fx", comp("fx", TOTAL,
    '<div class="sweep" id="fx-s1"></div><div class="sweep silver" id="fx-s2"></div><div class="flash" id="fx-gd" style="background:#FFC21A"></div>'
    '<div class="panel" id="fx-p1" style="background:#FFC21A"></div><div class="panel" id="fx-p2" style="background:#07070a"></div>' + slats +
    '<div class="curt" id="fx-c1" style="top:0;border-bottom:8px solid #FFC21A"></div><div class="curt" id="fx-c2" style="top:940px;border-top:8px solid #FFC21A"></div>'
    '<div class="shock" id="fx-shock"></div><div class="flash" id="fx-wh" style="background:#fff"></div>',
    '''
  const FT = (s, a, c, t) => tl.fromTo(s, a, { ...c, immediateRender: false }, t);
  const [b1, b2, b3, b4, b5, b6, b7] = D.B;
  FT("#fx-s1", { x: -300, opacity: 1 }, { x: 1900, opacity: 1, duration: .56, ease: "power2.inOut" }, b1 - .28);
  tl.set("#fx-s1", { opacity: 0 }, b1 + .3);
  FT("#fx-gd", { opacity: 0 }, { opacity: .8, duration: .1, ease: "power2.in" }, b2 - .12);
  tl.to("#fx-gd", { opacity: 0, duration: .28, ease: "power2.out" }, b2 - .02);
  FT("#fx-p1", { x: -1100, opacity: 1 }, { x: 0, duration: .2, ease: "power3.out" }, b3 - .22);
  FT("#fx-p2", { x: -1100, opacity: 1 }, { x: 0, duration: .2, ease: "power3.out" }, b3 - .18);
  tl.to("#fx-p1", { x: 1100, duration: .2, ease: "power3.in" }, b3);
  tl.to("#fx-p2", { x: 1100, duration: .2, ease: "power3.in" }, b3 + .04);
  tl.set(["#fx-p1", "#fx-p2"], { opacity: 0 }, b3 + .3);
  for (let i = 0; i < 8; i++) {
    FT("#fx-sl" + i, { y: -1950, opacity: 1 }, { y: 0, duration: .16, ease: "power2.out" }, b4 - .2 + i * .015);
    tl.to("#fx-sl" + i, { y: 1950, duration: .16, ease: "power2.in" }, b4 + i * .015);
    tl.set("#fx-sl" + i, { opacity: 0 }, b4 + .3);
  }
  FT("#fx-s2", { x: 0, opacity: 1 }, { x: -2100, opacity: 1, duration: .56, ease: "power2.inOut" }, b5 - .28);
  tl.set("#fx-s2", { opacity: 0 }, b5 + .3);
  FT("#fx-c1", { y: -985, opacity: 1 }, { y: 0, duration: .17, ease: "power3.out" }, b6 - .19);
  FT("#fx-c2", { y: 985, opacity: 1 }, { y: 0, duration: .17, ease: "power3.out" }, b6 - .19);
  tl.to("#fx-c1", { y: -985, duration: .17, ease: "power3.in" }, b6 + .02);
  tl.to("#fx-c2", { y: 985, duration: .17, ease: "power3.in" }, b6 + .02);
  tl.set(["#fx-c1", "#fx-c2"], { opacity: 0 }, b6 + .3);
  FT("#fx-shock", { scale: .1, opacity: 1 }, { scale: 7, opacity: 0, duration: .75, ease: "power2.out" }, b7 - .08);
  FT("#fx-gd", { opacity: 0 }, { opacity: .85, duration: .08 }, b7 - .06);
  tl.to("#fx-gd", { opacity: 0, duration: .3 }, b7 + .02);
''', dict(B=bounds)))
wh = dict(sweep="whoosh_up", zoom="whoosh_zoom", slide="whoosh_slide", slats="whoosh_slats", sweep2="whoosh_down", curtain="whoosh_curtain", shock="shock")
for b_, kd in zip(bounds, kinds): sfx(b_ - .26, wh[kd], .5, 3)
sfx(TOTAL - .75, "final", 1.0, 5)

# ------------------------------------------------------------------------------------------
# index.html
# ------------------------------------------------------------------------------------------
mounts = [("bg", 0, TOTAL, 0, "m-bg"), ("gancho", T_GANCHO, D_GANCHO, 1, "m-gancho m-scn"), ("presentacion", T_PRES, D_PRES, 1, "m-pres m-scn")]
for c in cats: mounts.append(("cat-" + c["key"], c["start"], c["dur"], 1, "m-cat-%s m-scn" % c["key"]))
for b in blocks: mounts.append(("blk-" + b["id"], b["start"], BLK, 2, "m-blk"))
mounts += [("trades", T_TRADES, D_TRADES, 1, "m-scn"), ("cierre", T_CIERRE, D_CIERRE, 1, "m-scn"), ("fx", 0, TOTAL, 3, "m-fx"), ("hud", 0, TOTAL, 4, "m-hud")]
mh = "\n  ".join('<div id="mt-%s" class="clip mount %s" data-composition-id="%s" data-composition-src="compositions/%s.html" data-start="%s" data-duration="%s" data-track-index="%d"></div>'
                % (c, cl, c, c, round(s, 3), round(d, 3), tr) for c, s, d, tr, cl in mounts)
open(os.path.join(ROOT, "index.html"), "w").write('''<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=1080, height=1920">
<title>Promo MonZ - Tienda</title>
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

json.dump(dict(total=TOTAL, bpm=BPM, beat=BEAT, events=EV, bounds=bounds,
               sections=dict(gancho=T_GANCHO, pres=T_PRES, perm=cats[0]["start"], fis=cats[1]["start"], gp=cats[2]["start"], skin=cats[3]["start"], trades=T_TRADES, cierre=T_CIERRE)),
          open(os.path.join(ROOT, "timeline.json"), "w"), indent=1)
if os.environ.get("SKIP_AUDIO") != "1":
    import audio; audio.render(ROOT)
print("OK", TOTAL)
