#!/usr/bin/env python3
"""Genera la voz del narrador por frases (Kokoro-82M, voz em_alex) -> assets/voice/*.wav + voice.json"""
import json, os, numpy as np, soundfile as sf
from kokoro_onnx import Kokoro
ROOT = os.path.dirname(os.path.abspath(__file__))
C = os.path.expanduser("~/.cache/hyperframes/tts/")
k = Kokoro(C + "models/kokoro-v1.0.onnx", C + "voices/voices-v1.0.bin")
SPEED = 1.2
# id, texto hablado, subtítulo
SEGS = [
 ("g1", "¿Quieres skins y físicas al mejor precio?", "¿QUIERES SKINS Y FÍSICAS AL MEJOR PRECIO?"),
 ("g2", "¡Aquí las tienes!", "¡AQUÍ LAS TIENES!"),
 ("s1", "¡Skins desde treinta pesos,", "¡SKINS DESDE 30 PESOS,"),
 ("f1", "y físicas permanentes para todos los bolsillos!", "Y FÍSICAS PERMANENTES PARA TODOS LOS BOLSILLOS!"),
 ("t1", "Y ojo, aquí no hay engaños:", "Y OJO, AQUÍ NO HAY ENGAÑOS:"),
 ("t2", "es cien por ciento confiable, y ya llevo más de cien referencias.", "ES 100% CONFIABLE, Y YA LLEVO MÁS DE 100 REFERENCIAS."),
 ("t3", "¡Míralas tú mismo!", "¡MÍRALAS TÚ MISMO!"),
 ("m1", "La venta es solo para México.", "LA VENTA ES SOLO PARA MÉXICO."),
 ("c1", "Escríbeme por mensaje directo en TikTok, a arroba, mons, eme ce, cero cinco.", "ESCRÍBEME POR MENSAJE DIRECTO EN TIKTOK, A @MONZMC05."),
 ("c2", "¡Y sube de nivel tu inventario!", "¡Y SUBE DE NIVEL TU INVENTARIO!"),
]
out = []
for sid, text, sub in SEGS:
    y, sr = k.create(text, voice="em_alex", speed=SPEED, lang="es")
    y = np.asarray(y, dtype=np.float32)
    a = np.abs(y); idx = np.where(a > 0.012)[0]
    y = y[max(0, idx[0] - int(.02 * sr)): idx[-1] + int(.06 * sr)]
    sf.write(os.path.join(ROOT, "assets/voice", sid + ".wav"), y, sr)
    out.append(dict(id=sid, text=text, sub=sub, dur=round(len(y) / sr, 3)))
    print(sid, round(len(y) / sr, 2), text)
json.dump(out, open(os.path.join(ROOT, "voice.json"), "w"), ensure_ascii=False, indent=1)
print("total", round(sum(o["dur"] for o in out), 2))
