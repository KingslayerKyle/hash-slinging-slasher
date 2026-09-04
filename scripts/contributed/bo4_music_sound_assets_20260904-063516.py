#!/usr/bin/env python3
"""Comprehensive Music Sound Asset Generator for Black Ops 4 SAB pool (unfolded backslashes)."""
import os
import re
import sys

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ENCODINGS = [".ll100.pc.snd", ".ln100.pc.snd", ".sl100.pc.snd", ".sn100.pc.snd"]

def generate():
    seen = set()
    def emit(s):
        s = s.strip()
        if s and s not in seen:
            seen.add(s)
            print(s)

    mus_cores = set()

    # 1. sound aliases in BO4
    alias_path = os.path.join(_root, "all_names", "blkops04", "sound_alias.txt")
    if os.path.exists(alias_path):
        with open(alias_path, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split(",")
                if len(parts) >= 2 and "mus" in parts[1]:
                    mus_cores.add(parts[1])

    # 2. bo3_cores
    bo3_path = os.path.join(_root, "scripts", "contributed", "bo3_cores_20260822-030351.txt")
    if os.path.exists(bo3_path):
        with open(bo3_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip().lower()
                if "mus" in line:
                    core = line.split(".")[0]
                    mus_cores.add(core)

    # 3. bo1_cores
    bo1_path = os.path.join(_root, "scripts", "contributed", "bo1_cores_20260822-031028.txt")
    if os.path.exists(bo1_path):
        with open(bo1_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip().lower()
                if "mus" in line:
                    core = line.split(".")[0].removesuffix("_l").removesuffix("_r")
                    mus_cores.add(core)

    # 4. bo2_sab.csv
    bo2_path = os.path.join(_root, "cod-name-db", "csv", "bo2_sab.csv")
    if os.path.exists(bo2_path):
        with open(bo2_path, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                parts = line.strip().split(",")
                if len(parts) >= 2 and "mus" in parts[1].lower():
                    path = parts[1].strip().lower().replace("/", "\\")
                    core = path.split(".")[0]
                    mus_cores.add(core)

    # Clean and emit
    for raw in mus_cores:
        raw = raw.strip().lower().replace("/", "\\")
        if not raw:
            continue

        # If raw is already a full path like mus\zmb\... or mus\doa\...
        if raw.startswith("mus\\"):
            for enc in ENCODINGS:
                emit(f"{raw}{enc}")
            # Also try under mus\zmb\ if not already
            if not raw.startswith("mus\\zmb\\"):
                rel = raw[len("mus\\"):]
                for enc in ENCODINGS:
                    emit(f"mus\\zmb\\{rel}{enc}")
        else:
            # raw is a core like mus_chap205_19.00 or mus_castle_roundend_1_intro
            for enc in ENCODINGS:
                emit(f"mus\\{raw}{enc}")
                emit(f"mus\\zmb\\{raw}{enc}")
                emit(f"mus\\mpl\\{raw}{enc}")
                emit(f"mus\\wz\\{raw}{enc}")
                emit(f"mus\\frontend\\{raw}{enc}")

if __name__ == "__main__":
    generate()
