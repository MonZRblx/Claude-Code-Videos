"""Catálogo exacto (leído de las capturas 14–22). Nombre y precio tal como aparecen."""
def P(prefix, rows): return [dict(name=n, price=p) for n, p in rows]
PERM_SRC = [  # (imagen, [items])
 (14, [("Dragón Permanente", 625), ("Control Permanente", 500), ("Kitsune Permanente", 500), ("Magnet Permanente", 440), ("Yeti Permanente", 375), ("Tiger Permanente", 375), ("Spirit Permanente", 320), ("Gas Permanente", 315)]),
 (15, [("Venom Permanente", 310), ("Shadow Permanente", 305), ("Dough Permanente", 300), ("T-Rex Permanente", 295), ("Mammoth Permanente", 295), ("Gravity Permanente", 290), ("Blizzard Permanente", 285), ("Pain Permanente", 275)]),
 (16, [("Lightning Permanente", 265), ("Portal Permanente", 250), ("Phoenix Permanente", 250), ("Sound Permanente", 240), ("Spider Permanente", 225), ("Creation Permanente", 220), ("Love Permanente", 215), ("Buddha Permanente", 210)]),
 (17, [("Quake Permanente", 190), ("Magma Permanente", 165), ("Ghost Permanente", 160), ("Rubber Permanente", 150), ("Light Permanente", 140), ("Diamond Permanente", 125)]),
]
FIS_SRC = [
 (18, [("Dragón West", 360), ("Dragón East", 320), ("Magnet", 140), ("Kitsune", 100), ("Control", 55), ("Yeti", 50), ("Tiger", 50), ("Gas", 40)]),
 (19, [("Dough", 35), ("T-Rex", 25), ("Venom", 20), ("Mammoth", 20), ("Spirit", 20), ("Gravity", 20), ("Portal", 20), ("Buddha", 20)]),
]
GP_SRC = [(20, [("Fruit Notifier", 340), ("Dark Blade", 150), ("2x Mastery", 60), ("2x Money", 60), ("+1 Fruit Storage", 50), ("Fast Boats", 45), ("2x Boss Drops", 45)])]
SKIN_SRC = [
 (21, [("Galaxy Empyrean Kitsune", 950), ("Ember Dragon", 650), ("Purple Lightbning", 550), ("Arcsteel Magnet", 350), ("Super Spirit Pain", 340), ("Red Lightning", 285), ("Runic Fiend Yeti", 250), ("Divine Portal", 240)]),
 (22, [("Dog Blade", 210), ("Werewolf", 180), ("Fiend Yeti", 180), ("Torment Pain", 30)]),
]
CATS = [  # clave, título, fuentes, bloques (tamaños), acento
 dict(key="perm", title="FRUTAS PERMANENTES", src=PERM_SRC, blocks=[6, 6, 6, 6, 6]),
 dict(key="fis", title="FRUTAS FÍSICAS", src=FIS_SRC, blocks=[6, 6, 4]),
 dict(key="gp", title="GAMEPASSES", src=GP_SRC, blocks=[4, 3]),
 dict(key="skin", title="SKINS", src=SKIN_SRC, blocks=[6, 6]),
]
