"""Mezcla de audio: música trap/gamer sintetizada (sin copyright) + efectos + narrador, con ducking de la música bajo la voz."""
import json, os, subprocess
import numpy as np
import soundfile as sf
from scipy import signal
from scipy.io import wavfile

SR = 44100
rng = np.random.default_rng(7)

def tt(d): return np.arange(int(d * SR)) / SR
def noise(d): return rng.standard_normal(int(d * SR))
def lp(x, f, o=2): return signal.lfilter(*signal.butter(o, min(.99, f / (SR / 2)), "low"), x)
def hp(x, f, o=2): return signal.lfilter(*signal.butter(o, f / (SR / 2), "high"), x)
def bp(x, a, b, o=2): return signal.lfilter(*signal.butter(o, [a / (SR / 2), min(.99, b / (SR / 2))], "band"), x)
def midi(n): return 440 * 2 ** ((n - 69) / 12)

def add(buf, start, sig, gain=1.0):
    i = int(start * SR)
    if i < 0 or i >= len(buf): return
    sig = sig[: len(buf) - i]
    buf[i:i + len(sig)] += sig * gain

def sweep_noise(d, f0, f1, q=.55, curve=1.0):
    n = noise(d); out = np.zeros_like(n); ch = 1024
    for k in range(0, len(n), ch):
        p = (k / len(n)) ** curve
        fc = f0 * (f1 / f0) ** p
        b, a = signal.butter(2, [max(30, fc * (1 - q)) / (SR / 2), min(.98, fc * (1 + q) / (SR / 2))], "band")
        out[k:k + ch] = signal.lfilter(b, a, n[k:k + ch])
    return out

# ---------------- efectos ----------------
def s_boom():
    t = tt(1.1); f = 36 + 120 * np.exp(-t * 9)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 3.2)
    x += hp(noise(1.1), 400) * np.exp(-t * 6) * .5
    return x * 1.2
def s_slam():
    t = tt(.2); return (np.sin(2 * np.pi * np.cumsum(70 + 160 * np.exp(-t * 40)) / SR) * np.exp(-t * 18) + bp(noise(.2), 800, 5000) * np.exp(-t * 30) * .5)
def s_glitch():
    out = np.zeros(int(.4 * SR)); t0 = 0.0
    for k in range(7):
        d = rng.uniform(.02, .06); n = int(d * SR); hold = rng.integers(8, 60)
        x = np.repeat(rng.standard_normal(n // hold + 1), hold)[:n] * (1 if k % 2 else .6)
        x = np.sign(x) * np.abs(x) ** .5
        i = int(t0 * SR); out[i:i + n] += x[:len(out) - i] * .5; t0 += d + rng.uniform(0, .03)
    return out
def s_whoosh_up(d=.7): t = tt(d); return sweep_noise(d, 300, 8000, .7, 1.6) * (t / d) ** 1.4 * np.minimum(1, (d - t) * 18) * 2.0
def s_whoosh_zoom(d=.65):
    t = tt(d); x = sweep_noise(d, 5000, 300, .7, 1.2) * (1 - t / d) ** .3 * np.minimum(1, t * 40)
    return (x * 1.6 + np.sin(2 * np.pi * np.cumsum(900 * np.exp(-t * 3)) / SR) * .2 * np.exp(-t * 4))
def s_whoosh_zoom_in(d=.5): t = tt(d); return sweep_noise(d, 400, 5000, .6, 1.4) * np.sin(np.pi * t / d) * 1.7
def s_whoosh_fast(d=.24): t = tt(d); return sweep_noise(d, 1200, 5200, .8, 1.0) * np.sin(np.pi * t / d) * 1.3
def s_whoosh_side(d=.5): t = tt(d); return sweep_noise(d, 800, 3200, .9, 1.0) * np.sin(np.pi * t / d) ** 1.5 * 1.7
def s_whoosh_fan(d=.5): t = tt(d); return sweep_noise(d, 500, 3500, .8, 1.2) * np.sin(np.pi * t / d) * 1.6
def s_impact():
    t = tt(.9); return s_boom()[:len(t)] * .85 + hp(noise(.9), 2500) * np.exp(-t * 7) * .55
def s_shock():
    d = 1.0; t = tt(d); sw = sweep_noise(d, 200, 7000, .7, 2.0) * (t / d) ** 1.3
    return sw * 1.4 + np.sin(2 * np.pi * np.cumsum(40 + 90 * (t / d)) / SR) * (t / d) * .5
def s_pop(f=900): t = tt(.12); return np.sin(2 * np.pi * np.cumsum(f * np.exp(-t * 12)) / SR) * np.exp(-t * 26) * .8
def bell(f, d, g=1.0):
    t = tt(d); return (np.sin(2 * np.pi * f * t) + .45 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t * 14) + .25 * np.sin(2 * np.pi * f * 5.4 * t) * np.exp(-t * 25)) * np.exp(-t * (30 / d)) * g
def s_coin():
    out = np.zeros(int(.7 * SR)); add(out, 0, bell(1568, .5, .6)); add(out, .075, bell(2093, .6, .75)); add(out, 0, hp(noise(.05), 6000) * np.exp(-tt(.05) * 60) * .5); return out
def s_ding(): return bell(1319, .5, .7)
def s_ach():
    out = np.zeros(int(1.2 * SR))
    for k, n in enumerate((72, 76, 79, 84)): add(out, k * .075, bell(midi(n), .6, .55))
    add(out, .3, hp(noise(.7), 5000) * np.exp(-tt(.7) * 5) * .25); add(out, .3, bell(midi(96), .8, .35)); return out
def s_tick(): t = tt(.04); return np.sin(2 * np.pi * 1900 * t) * np.exp(-t * 90) * .6
def s_tick_soft(): t = tt(.03); return np.sin(2 * np.pi * 1200 * t) * np.exp(-t * 110) * .4
def s_shine(): d = .55; t = tt(d); return hp(noise(d), 6500) * np.exp(-t * 7) * .45 + np.sin(2 * np.pi * 3200 * t) * np.exp(-t * 9) * .12
def s_neon(): d = .5; t = tt(d); return signal.sawtooth(2 * np.pi * 110 * t) * np.exp(-t * 7) * .35 * (np.sin(2 * np.pi * 60 * t) > -.2) + hp(noise(.03), 3000).mean() * 0
SF = dict(boom=s_boom, slam=s_slam, glitch=s_glitch, whoosh_up=s_whoosh_up, whoosh_zoom=s_whoosh_zoom, whoosh_zoom_in=s_whoosh_zoom_in, whoosh_fast=s_whoosh_fast,
          whoosh_side=s_whoosh_side, whoosh_fan=s_whoosh_fan, impact=s_impact, shock=s_shock, pop=s_pop, coin=s_coin, ding=s_ding, ach=s_ach, tick=s_tick,
          tick_soft=s_tick_soft, shine=s_shine, neon=s_neon)

# ---------------- música trap/gamer en Fa menor ----------------
def kick():
    t = tt(.4); return np.sin(2 * np.pi * np.cumsum(48 + 130 * np.exp(-t * 32)) / SR) * np.exp(-t * 7) * 1.0
def clap():
    t = tt(.26); n = bp(noise(.26), 1000, 4200)
    env = np.exp(-t * 20) + .7 * np.exp(-((t - .013) ** 2) * 30000) + .5 * np.exp(-((t - .028) ** 2) * 30000)
    return n * env * 1.1
def hat(d=.05, g=.3): return hp(noise(d), 7500) * np.exp(-tt(d) * 85) * g
def b808(f, d):
    t = tt(d); fr = f * (1 + .6 * np.exp(-t * 30))
    x = np.sin(2 * np.pi * np.cumsum(fr) / SR); x = np.tanh(x * 2.2) * .8
    return x * np.minimum(1, t * 400) * np.exp(-t * 2.4) * np.minimum(1, (d - t) * 60)
def pluck(f, d=.3, g=1.0):
    t = tt(d); return lp(signal.sawtooth(2 * np.pi * f * t) * .6 + np.sin(2 * np.pi * f * 2.0 * t) * .3, 3200) * np.exp(-t * 11) * np.minimum(1, t * 300) * g
def pad(freqs, d):
    t = tt(d); s = sum(np.sin(2 * np.pi * f * t) + .4 * np.sin(2 * np.pi * f * 2.005 * t) for f in freqs) / len(freqs)
    return lp(s, 1500) * np.minimum(1, t * 3) * np.minimum(1, (d - t) * 3)

def music(total, bpm):
    N = int((total + 1.2) * SR); buf = np.zeros(N); beat = 60 / bpm; st = beat / 4
    prog = [(29, [53, 56, 60, 63]), (25, [49, 53, 56, 60]), (32, [56, 60, 63, 67]), (27, [51, 55, 58, 62])]  # Fm - Dbmaj - Abmaj - Ebmaj (bajo MIDI, acorde)
    start = .12; nbar = int((total - start) / (beat * 4)) + 2
    kicks_pos = np.zeros(N)
    for bar in range(nbar):
        t0 = start + bar * beat * 4; root, ch = prog[bar % 4]
        fx = (bar % 2 == 1)
        for s_ in range(16):
            t = t0 + s_ * st
            if t >= total: break
            if s_ in (0, 7, 10) or (fx and s_ == 14):
                add(buf, t, kick(), .95); i0 = int(t * SR); kicks_pos[i0:i0 + int(.22 * SR)] = 1
            if s_ == 8: add(buf, t, clap(), .55)
            if s_ % 2 == 0: add(buf, t, hat(.05, .28 if s_ % 4 else .34))
            if bar % 2 == 1 and s_ in (13, 14, 15): add(buf, t, hat(.03, .22))
            if s_ == 15 and bar % 4 == 3:
                for k in range(3): add(buf, t + k * st / 3, hat(.025, .25))
            if s_ in (0, 10): add(buf, t, b808(midi(root), st * (6 if s_ == 0 else 5)), .8)
            if s_ in (3, 11, 14) and bar % 2: add(buf, t, b808(midi(root + (12 if s_ == 14 else 0)), st * 2), .4)
            if s_ % 2 == 0: add(buf, t, pluck(midi(ch[(s_ // 2 + bar) % 4] + 12), .26, .2))
        add(buf, t0, pad([midi(n + 12) for n in ch], beat * 4), .13)
        if bar % 2 == 0: add(buf, t0, pluck(midi(ch[3] + 24), beat * 2, .13))
    return buf, kicks_pos

def render(root):
    T = json.load(open(os.path.join(root, "timeline.json")))
    total, bpm = T["total"], T["bpm"]; N = int((total + 1.2) * SR)
    mus, _ = music(total, bpm)
    # voz
    voice = np.zeros(N)
    for sid in T["voice_files"]:
        y, sr = sf.read(os.path.join(root, "assets/voice", sid + ".wav"))
        if y.ndim > 1: y = y.mean(1)
        if sr != SR: y = signal.resample_poly(y, SR, sr)
        y = hp(y, 90); y = y / (np.max(np.abs(y)) + 1e-9) * .9
        y = np.tanh(y * 1.5) / np.tanh(1.5) * .95   # algo de presencia/compresión
        add(voice, T["voice"][sid], y, 1.0)
    # ducking de la música bajo la voz
    env = lp(np.abs(voice), 7, 1); env = np.clip(env / (np.percentile(env[env > 0.001], 90) + 1e-9), 0, 1)
    duck = 1 - .6 * env
    mus = mus * duck * .62
    # efectos
    fxb = np.zeros(N)
    for t, kind, vol in T["events"]:
        if kind in SF and vol > 0: add(fxb, t, SF[kind](), .7 * vol)
    mix = mus + voice * 1.0 + fxb
    # cierre con fade y límite suave
    fe = int(1.1 * SR); e = int(total * SR); mix[e:] = 0; mix[e - fe:e] *= np.linspace(1, 0, fe)
    mix = np.tanh(mix * .95)
    mix = mix[:e] / (np.max(np.abs(mix[:e])) + 1e-9) * .85
    wav = os.path.join(root, "assets", "audio.wav")
    wavfile.write(wav, SR, (mix * 32767).astype(np.int16))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-codec:a", "libmp3lame", "-q:a", "2", os.path.join(root, "assets", "audio.mp3")], check=True)
    os.remove(wav)
    print("audio ok", round(total, 2), "s")
