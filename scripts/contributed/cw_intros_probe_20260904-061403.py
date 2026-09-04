#!/usr/bin/env python3
"""MP & Zombies Intro cutscenes sound alias and sound asset generator for Cold War."""

FACTIONS = ["cia", "kgb", "bnd", "dgi", "hva", "mi6", "mi5", "spz", "ussr"]
MAPS = [
    "moscow", "miami", "satellite", "cartel", "dune", "armada", "crossroads",
    "checkmate", "garrison", "mall", "apocalypse", "yamantau", "echelon",
    "slums", "drivein", "zoo", "express", "raid", "standoff", "hijacked",
    "nuketown", "nuketown6", "village", "rus_amerika", "rus_yamantau", "rus_kgb"
]
ELEMENTS = [
    "door", "door_sweet", "foley", "veh", "whoosh", "engine", "sweet",
    "tread", "sfx", "sirens", "susp", "skid", "boat", "boat_imp", "helo",
    "ramp_sweet", "heli_sweet", "stinger", "wind", "turret", "wreck", "tree_whoosh",
    "tree_whoosh_sweet", "bg", "intro", "outro", "mid", "sfx_ep", "sfx_mid",
    "sfx_outro", "sfx_outro_npc"
]

TAILS = [
    ".ln75.pc.all.snd", ".ll75.pc.all.snd", ".sn75.pc.all.snd",
    ".rn75.pc.all.snd", ".sl75.pc.all.snd", ".rr75.pc.all.snd",
    ".ln75.pc.snd", ".sn75.pc.snd"
]

VEHICLES = ["van", "heli", "helo", "truck", "boat", "tank", "apc", "car", "snowmobile", "buggy", "rover", "tram"]

def generate():
    seen = set()
    def emit(s):
        s = s.strip()
        if s and s not in seen:
            seen.add(s)
            print(s)

    # 1. Sound aliases: evt_igc_{faction}_{map}_{element}
    for f in FACTIONS:
        for m in MAPS:
            for el in ELEMENTS:
                emit(f"evt_igc_{f}_{m}_{el}")
                emit(f"evt_igc_{f}_{el}")
                emit(f"evt_igc_{m}_{el}")
                emit(f"evt_igc_{f}_{m}")

    # Also map intros: evt_igc_mp_{map}_intro_{element}
    for m in MAPS:
        for el in ["intro", "intro_foley", "intro_heli_sweet", "intro_ramp_sweet", "intro_stinger", "intro_wind", "intro_veh", "intro_door"]:
            emit(f"evt_igc_mp_{m}_{el}")
            emit(f"evt_igc_zm_{m}_{el}")

    # 2. Sound assets: mpl/intros/mp_{map}/...
    for m in MAPS:
        folder = f"mp_{m}"
        for v_num in range(1, 16):
            for el in ["van_door", "van_foley", "van_engine", "van_stop", "door", "foley", "engine", "veh", "heli_sweet", "ramp_sweet"]:
                for t in TAILS:
                    emit(f"mpl/intros/{folder}/{folder}_{el}_v{v_num}{t}")
                    emit(f"mpl/intros/{folder}/{el}_v{v_num}{t}")

            for veh in VEHICLES:
                for sub in ["door", "foley", "engine", "drive", "stop", "interior", "exterior"]:
                    for t in TAILS:
                        emit(f"mpl/intros/{folder}/{folder}_{veh}_{sub}_v{v_num}{t}")
                        emit(f"mpl/intros/{folder}/{veh}_{sub}_v{v_num}{t}")

if __name__ == "__main__":
    generate()
