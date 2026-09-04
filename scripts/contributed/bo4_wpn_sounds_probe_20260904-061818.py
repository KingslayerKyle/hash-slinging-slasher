#!/usr/bin/env python3
"""Targeted weapon sound asset generator for Black Ops 4.

BO4 sound directories (from bo4_snd_dirs) contain 674 wpn directories:
  wpn\\{class}\\{weap}\\{subfolders}\\...

Observed confirmed turret assets in BO4:
  wpn\\turret\\arav\\lfe\\wpn_arav_lfe.ln100.pc.snd
  wpn\\turret\\arav\\lfe\\wpn_arav_loop_lfe.ll100.pc.snd
  wpn\\turret\\arav\\plr\\wpn_arav_start.ln100.pc.snd
  wpn\\turret\\arav\\plr\\wpn_arav_start_act.ln100.pc.snd
  wpn\\turret\\arav\\plr\\wpn_arav_start_ads.ln100.pc.snd
  wpn\\turret\\arav\\plr\\wpn_arav_stop.ln100.pc.snd
  wpn\\turret\\pbr\\plr\\wpn_pbr_loop.ll100.pc.snd
  wpn\\turret\\pbr\\plr\\wpn_pbr_start.ln100.pc.snd

This generator pairs each wpn directory with the observed verb/action patterns.
"""
import os
import sys

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TAILS = [
    ".ln100.pc.snd", ".ll100.pc.snd", ".sn100.pc.snd", ".sl100.pc.snd"
]

CLASS_SHORT = {
    "assault": "ar",
    "smg": "smg",
    "lmg": "lmg",
    "sniper": "sn",
    "pistol": "pi",
    "shotgun": "sg",
    "tactical": "tr",
    "melee": "melee",
    "turret": "turret",
    "hero": "hero",
    "zmb": "zmb",
    "energy": "energy"
}

ACTIONS = [
    "start", "stop", "loop", "fire", "shot", "lfe", "loop_lfe",
    "start_act", "start_ads", "stop_act", "stop_ads", "loop_ads",
    "fire_act", "fire_ads", "shot_act", "shot_ads",
    "tail", "tail_ext", "tail_int", "mech", "decay",
    "first", "last", "burst", "burst_fire"
]

def generate():
    seen = set()
    def emit(s):
        if s not in seen:
            seen.add(s)
            print(s)

    dirs_file = os.path.join(_root, "scripts", "contributed", "bo4_snd_dirs_20260823-030223.txt")
    if not os.path.exists(dirs_file):
        return

    with open(dirs_file, "r", encoding="utf-8", errors="ignore") as f:
        wpn_dirs = [line.strip().lower() for line in f if line.strip().lower().startswith("wpn\\")]

    for d in wpn_dirs:
        # Strip trailing backslash
        d_clean = d.rstrip("\\")
        parts = d_clean.split("\\")
        if len(parts) < 3:
            continue

        wclass = parts[1]
        weap = parts[2]
        cshort = CLASS_SHORT.get(wclass, wclass)
        sub = "_".join(parts[3:]) if len(parts) > 3 else ""

        # Candidates for weapon name prefixes:
        prefixes = [
            f"wpn_{weap}",
            f"wpn_{cshort}_{weap}",
            f"{weap}",
            f"wpn_{weap}_{sub}" if sub else f"wpn_{weap}",
            f"wpn_{cshort}_{weap}_{sub}" if sub else f"wpn_{cshort}_{weap}"
        ]

        for pfx in prefixes:
            for act in ACTIONS:
                base = f"{pfx}_{act}" if act else pfx
                for t in TAILS:
                    emit(f"{d_clean}\\{base}{t}")

            # Also try sub directly: e.g. wpn_arav_lfe
            if sub:
                for t in TAILS:
                    emit(f"{d_clean}\\{pfx}_{sub}{t}")
                    emit(f"{d_clean}\\{pfx}{t}")

if __name__ == "__main__":
    generate()
