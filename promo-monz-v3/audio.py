"""Audio SIN voz: música trap/gamer sintetizada (sin copyright) + efectos sutiles, sincronizados con la línea de tiempo."""
import json, os, subprocess
import numpy as np
from scipy import signal
from scipy.io import wavfile

SR = 44100
rng = np.random.default_rng(11)
def tt(d): return np.arange(int(d * SR)) / SR
def noise(d): return rng.standard_normal(int(d * SR))
def lp(x, f, o=2): return signal.lfilter(*signal.butter(o, min(.99, f / (SR / 2)), "low"), x)
def hp(x, f, o=2): return signal.lfilter(*signal.butter(o, f / (SR / 2), "high"), x)
def bp(x, a, b, o=2): return signal.lfilter(*signal.butter(o, [a / (SR / 2), min(.99, b / (SR / 2))], "band"), x)
def midi(n): return 440 * 2 ** ((n - 69) / 12)
def add(buf, start, sig, gain=1.0):
    i = int(start * SR)
    if i < 0 or i >= len(buf): return
    sig = sig[: len(buf) - i]; buf[i:i + len(sig)] += sig * gain
def sweep_noise(d, f0, f1, q=.6, curve=1.0):
    n = noise(d); out = np.zeros_like(n); ch = 1024
    for k in range(0, len(n), ch):
        fc = f0 * (f1 / f0) ** ((k / len(n)) ** curve)
        b, a = signal.butter(2, [max(30, fc * (1 - q)) / (SR / 2), min(.98, fc * (1 + q) / (SR / 2))], "band")
        out[k:k + ch] = signal.lfilter(b, a, n[k:k + ch])
    return out

# ---------------- efectos (todos discretos) ----------------
def bell(f, d, g=1.0):
    t = tt(d); return (np.sin(2 * np.pi * f * t) + .45 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t * 14) + .2 * np.sin(2 * np.pi * f * 5.4 * t) * np.exp(-t * 25)) * np.exp(-t * (30 / d)) * g
def s_boom(): t = tt(1.0); return (np.sin(2 * np.pi * np.cumsum(36 + 110 * np.exp(-t * 9)) / SR) * np.exp(-t * 3.4) + hp(noise(1.0), 400) * np.exp(-t * 7) * .4) * 1.1
def s_slam(): t = tt(.18); return np.sin(2 * np.pi * np.cumsum(70 + 150 * np.exp(-t * 40)) / SR) * np.exp(-t * 19) + bp(noise(.18), 800, 5000) * np.exp(-t * 32) * .4
def s_glitch():
    out = np.zeros(int(.35 * SR)); t0 = 0.0
    for k in range(6):
        d = rng.uniform(.02, .05); n = int(d * SR); hold = rng.integers(10, 60)
        x = np.repeat(rng.standard_normal(n // hold + 1), hold)[:n]; i = int(t0 * SR); out[i:i + n] += np.sign(x)[:len(out) - i] * .3; t0 += d + rng.uniform(0, .03)
    return out
def s_pop(): t = tt(.1); return np.sin(2 * np.pi * np.cumsum(820 * np.exp(-t * 12)) / SR) * np.exp(-t * 28) * .7
def s_coin():
    out = np.zeros(int(.6 * SR)); add(out, 0, bell(1568, .45, .5)); add(out, .07, bell(2093, .5, .6)); return out
def s_tick(): t = tt(.035); return np.sin(2 * np.pi * 1900 * t) * np.exp(-t * 90) * .5
def s_shine(): d = .5; t = tt(d); return hp(noise(d), 6500) * np.exp(-t * 7) * .35 + np.sin(2 * np.pi * 3200 * t) * np.exp(-t * 9) * .1
def s_neon(): d = .45; t = tt(d); return signal.sawtooth(2 * np.pi * 110 * t) * np.exp(-t * 7) * .3 * (np.sin(2 * np.pi * 55 * t) > -.2)
def s_ach():
    out = np.zeros(int(1.1 * SR))
    for k, n in enumerate((72, 76, 79, 84)): add(out, k * .08, bell(midi(n), .55, .5))
    add(out, .32, hp(noise(.6), 5000) * np.exp(-tt(.6) * 5) * .22); add(out, .32, bell(midi(96), .7, .3)); return out
def s_whoosh_up(): d = .65; t = tt(d); return sweep_noise(d, 300, 7500, .7, 1.6) * (t / d) ** 1.4 * np.minimum(1, (d - t) * 16) * 1.7
def s_whoosh_down(): d = .6; t = tt(d); return sweep_noise(d, 6500, 350, .7, 1.2) * np.sin(np.pi * np.clip(t / d, 0, 1)) ** .7 * 1.6
def s_whoosh_zoom(): d = .6; t = tt(d); return sweep_noise(d, 4500, 300, .7, 1.2) * np.minimum(1, t * 40) * (1 - t / d) ** .3 * 1.5 + np.sin(2 * np.pi * np.cumsum(800 * np.exp(-t * 3)) / SR) * .12 * np.exp(-t * 4)
def s_whoosh_slide(): d = .5; t = tt(d); return sweep_noise(d, 700, 3000, .9, 1.0) * np.sin(np.pi * t / d) ** 1.5 * 1.6
def s_whoosh_slats():
    d = .5; x = np.zeros(int(d * SR))
    for k in range(8): add(x, k * .03, bp(noise(.07), 1500 + 300 * k, 6000) * np.exp(-tt(.07) * 40), 1.2)
    return x + sweep_noise(d, 800, 4500, .8, 1.0) * np.sin(np.pi * tt(d) / d) * .6
def s_whoosh_curtain(): d = .5; t = tt(d); return sweep_noise(d, 250, 1800, .8, 1.0) * np.sin(np.pi * t / d) * 1.5 + np.sin(2 * np.pi * np.cumsum(70 * np.exp(-np.clip(t - .22, 0, 9) * 8)) / SR) * np.exp(-np.abs(t - .25) * 12) * .6
def s_whoosh_soft(): d = .28; t = tt(d); return sweep_noise(d, 900, 4200, .8, 1.0) * np.sin(np.pi * t / d) * 1.0
def s_shock(): d = 1.0; t = tt(d); return sweep_noise(d, 200, 7000, .7, 2.0) * (t / d) ** 1.3 * 1.3 + np.sin(2 * np.pi * np.cumsum(40 + 90 * (t / d)) / SR) * (t / d) * .45
def s_final():
    d = 1.6; t = tt(d); out = np.zeros(int(d * SR))
    for n in (53, 56, 60, 65): add(out, 0, (signal.sawtooth(2 * np.pi * midi(n) * t) * .5 + np.sin(2 * np.pi * midi(n) * t)) * np.exp(-t * 2.4) * .22, 1)
    add(out, 0, np.sin(2 * np.pi * np.cumsum(38 + 90 * np.exp(-t * 8)) / SR) * np.exp(-t * 2.2) * .9)
    add(out, 0, hp(noise(d), 3000) * np.exp(-t * 4) * .35)
    for n in (77, 84, 89): add(out, 0, bell(midi(n), 1.2, .25))
    return out
SF = dict(boom=s_boom, slam=s_slam, glitch=s_glitch, pop=s_pop, coin=s_coin, tick=s_tick, shine=s_shine, neon=s_neon, ach=s_ach, whoosh_up=s_whoosh_up, whoosh_down=s_whoosh_down,
          whoosh_zoom=s_whoosh_zoom, whoosh_slide=s_whoosh_slide, whoosh_slats=s_whoosh_slats, whoosh_curtain=s_whoosh_curtain, whoosh_soft=s_whoosh_soft, shock=s_shock, final=s_final)

# ---------------- música ----------------
def kick(): t = tt(.4); return np.sin(2 * np.pi * np.cumsum(48 + 125 * np.exp(-t * 32)) / SR) * np.exp(-t * 7)
def clap(): t = tt(.24); return bp(noise(.24), 1000, 4200) * (np.exp(-t * 22) + .6 * np.exp(-((t - .013) ** 2) * 30000) + .4 * np.exp(-((t - .028) ** 2) * 30000)) * .9
def hat(d=.05, g=.28): return hp(noise(d), 7500) * np.exp(-tt(d) * 85) * g
def b808(f, d):
    t = tt(d); x = np.tanh(np.sin(2 * np.pi * np.cumsum(f * (1 + .55 * np.exp(-t * 30))) / SR) * 2.0) * .8
    return x * np.minimum(1, t * 400) * np.exp(-t * 2.2) * np.minimum(1, (d - t) * 60)
def pluck(f, d=.26, g=1.0): t = tt(d); return lp(signal.sawtooth(2 * np.pi * f * t) * .55 + np.sin(2 * np.pi * f * 2 * t) * .3, 3000) * np.exp(-t * 11) * np.minimum(1, t * 300) * g
def pad(freqs, d): t = tt(d); s = sum(np.sin(2 * np.pi * f * t) + .4 * np.sin(2 * np.pi * f * 2.005 * t) for f in freqs) / len(freqs); return lp(s, 1500) * np.minimum(1, t * 3) * np.minimum(1, (d - t) * 3)

def riser(d=1.5):
    t = tt(d); return sweep_noise(d, 300, 9000, .7, 1.8) * (t / d) ** 1.5 * 1.1

def music(T):
    total, beat = T["total"], T["beat"]; N = int((total + 2.0) * SR); buf = np.zeros(N); st = beat / 4
    prog = [(29, [53, 56, 60, 63]), (25, [49, 53, 56, 60]), (32, [56, 60, 63, 67]), (27, [51, 55, 58, 62])]   # Fm - Db - Ab - Eb
    sc = T["sc"]
    def sec(t):
        for name in ("hook", "intro", "perm", "fis", "gp", "skin", "trust", "close"):
            if t < sc[name][1] - 1e-6: return name
        return "close"
    nsteps = int(round(total / st))
    for s_ in range(nsteps):
        t = s_ * st; b = s_ / 4; bar = int(b // 4); root, ch = prog[bar % 4]; name = sec(t); k = s_ % 16
        if name == "trust":
            if k == 0: add(buf, t, b808(midi(root), st * 14), .55); add(buf, t, pad([midi(n + 12) for n in ch], beat * 4), .2)
            if k % 4 == 0: add(buf, t, pluck(midi(ch[(k // 4 + bar) % 4] + 24), .5, .22))
            if k in (8, 12): add(buf, t, hat(.03, .12))
            continue
        if k in (0, 7, 10) or (bar % 2 == 1 and k == 14): add(buf, t, kick(), .95)
        if k == 8: add(buf, t, clap(), .5 if name != "intro" else .3)
        if k % 2 == 0: add(buf, t, hat(.05, .26 if k % 4 else .32))
        if name != "intro" and bar % 2 == 1 and k in (13, 14, 15): add(buf, t, hat(.03, .2))
        if k in (0, 10): add(buf, t, b808(midi(root), st * (6 if k == 0 else 5)), .8)
        if k in (3, 11, 14) and bar % 2: add(buf, t, b808(midi(root + (12 if k == 14 else 0)), st * 2), .35)
        arp = [0, 1, 2, 3, 2, 1, 3, 2] if name == "gp" else [0, 2, 1, 3, 2, 0, 1, 3]
        octv = 24 if name in ("gp", "skin") else 12
        if k % 2 == 0: add(buf, t, pluck(midi(ch[arp[(k // 2) % 8] % 4] + octv), .26, .17))
        if k == 0: add(buf, t, pad([midi(n + 12) for n in ch], beat * 4), .13 if name != "skin" else .19)
        if k == 0 and bar % 2 == 0 and name in ("skin", "close", "gp"): add(buf, t, pluck(midi(ch[3] + 24), beat * 2, .13))
    # remate hacia el bucle: subida de ruido + redoble en el último compás (conduce al golpe del inicio)
    add(buf, total - 1.5, riser(1.5), .55)
    for k in range(8): add(buf, total - 0.9 + k * (0.9 / 8) * (1 - .05 * k), clap(), .12 + .03 * k)
    return buf

def render(root):
    T = json.load(open(os.path.join(root, "timeline.json"))); total = T["total"]; N = int((total + 2.0) * SR); e_ = int(total * SR)
    mus = music(T) * .62
    ev = sorted(T["events"], key=lambda e: (e[0], -e[3]))
    keep = []
    for e in ev:   # si coinciden varios efectos (< 80 ms) se deja solo el de mayor prioridad
        if keep and e[0] - keep[-1][0] < .08:
            if e[3] > keep[-1][3] or (e[3] == keep[-1][3] and e[2] > keep[-1][2]): keep[-1] = e
            continue
        keep.append(e)
    fxb = np.zeros(N)
    for t, kind, vol, pr in keep:
        if kind in SF: add(fxb, t, SF[kind](), .62 * vol)
    mix = mus + fxb * .85
    tail = mix[e_:e_ + int(1.5 * SR)].copy(); mix = mix[:e_]; mix[:len(tail)] += tail            # empalme circular para el bucle
    mix = np.tanh(mix * .95); mix = mix / (np.max(np.abs(mix)) + 1e-9) * .84
    wav = os.path.join(root, "assets", "audio.wav"); wavfile.write(wav, SR, (mix * 32767).astype(np.int16))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-codec:a", "libmp3lame", "-q:a", "2", os.path.join(root, "assets", "audio.mp3")], check=True)
    os.remove(wav); print("audio ok", round(total, 2), "s ·", len(keep), "efectos")
