#!/usr/bin/env python3
"""Fill all numbered gaps and expand indices for all known BO4 sound asset paths.

Observed in BO4 sound_asset:
  blk\\maps\\wz_open_skyscrapers\\destinations\\asylum\\amb_spooky\\amb_spooky_00.ln100.pc.snd
  (01, 02, 04, 06, 08, 09, 11, 12, 13, 14 present, but 03, 05, 07, 10 missing!)
  amb\\environment\\industrial\\generic\\amb_industrial_loop_00.ll100.pc.snd
  (02 present, 01 missing!)
"""
import os
import re
import sys

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ENCODINGS = ["ln100", "ll100", "sn100", "sl100", "rn75", "ln75", "rn100", "rr100"]

def generate():
    seen = set()
    def emit(s):
        if s not in seen:
            seen.add(s)
            print(s)

    known_file = os.path.join(_root, "all_names", "blkops04", "sound_asset.txt")
    if not os.path.exists(known_file):
        return

    stems = set()
    with open(known_file, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            parts = line.strip().split(",")
            if len(parts) >= 2:
                name = parts[1]
                if name.endswith(".snd"):
                    stem = name[:-4].rsplit(".", 2)[0]
                    stems.add(stem)

    # For each stem, if it ends in digits, expand digits from 0 to 30
    for stem in stems:
        m = re.search(r"^(.*?)_([0-9]+)$", stem)
        if m:
            prefix, num_str = m.group(1), m.group(2)
            width = len(num_str)
            for i in range(35):
                # Form with same width
                num_formatted = f"{i:0{width}d}"
                # Also 1-digit or 2-digit
                for enc in ENCODINGS:
                    emit(f"{prefix}_{num_formatted}.{enc}.pc.snd")
                    emit(f"{prefix}_{i:02d}.{enc}.pc.snd")
                    emit(f"{prefix}_{i}.{enc}.pc.snd")
        else:
            # Stem without digits: try appending _00.._15
            for i in range(16):
                for enc in ENCODINGS:
                    emit(f"{stem}_{i:02d}.{enc}.pc.snd")
                    emit(f"{stem}_{i}.{enc}.pc.snd")
            # Also try without digits across all encodings
            for enc in ENCODINGS:
                emit(f"{stem}.{enc}.pc.snd")

if __name__ == "__main__":
    generate()
