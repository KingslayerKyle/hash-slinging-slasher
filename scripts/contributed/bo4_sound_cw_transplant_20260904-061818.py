#!/usr/bin/env python3
"""Convert all Cold War sound stems (from all language tables and aliases) into BO4 SAB backslash format.

Cold War tables and confirmed lists contain vast sound asset names:
  amb/...
  zmb/...
  mus/...
  wpn/...
  fly/...
  evt/...

Black Ops 4 sound assets live in SAB files and are hashed unfolded WITH BACKSLASHES:
  amb\\...
  zmb\\...
  mus\\...

This generator harvests stems from all tables and Cold War alias lists, converts forward
slashes to backslashes, and pairs them with BO4 SAB encodings.
"""
import os
import sys

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_root, "scripts"))
import snapshot

TABLES = [
    "fnv1a_xsounds",
    "fnv1a_english_xsounds",
    "fnv1a_french_xsounds",
    "fnv1a_german_xsounds",
    "fnv1a_spanish_xsounds",
    "fnv1a_americanspanish_xsounds",
    "fnv1a_russian_xsounds",
    "fnv1a_xsounds_v2",
]

ENCODINGS = ["ln100", "ll100", "sn100", "sl100", "rn75", "ln75"]

def generate():
    seen = set()
    def emit(s):
        if s not in seen:
            seen.add(s)
            print(s)

    # Read from tables
    seeds = set(snapshot.table_names(*TABLES))
    seeds.update(snapshot.confirmed_names("sound_asset"))

    # Also read CW sound aliases
    cw_alias_file = os.path.join(_root, "all_names", "blkopscw", "sound_alias.txt")
    if os.path.exists(cw_alias_file):
        with open(cw_alias_file, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                parts = line.strip().split(",")
                if len(parts) >= 2:
                    seeds.add(parts[1])

    for name in seeds:
        name = name.strip().lower()
        if not name:
            continue

        if name.endswith(".snd"):
            pieces = name[:-4].rsplit(".", 3)
            if len(pieces) == 4:
                stem = pieces[0]
            elif len(pieces) == 3:
                stem = pieces[0]
            else:
                stem = name[:-4]
        else:
            stem = name

        # Convert forward slashes to backslashes for BO4
        bs_stem = stem.replace("/", "\\")

        for enc in ENCODINGS:
            # Emitted as: {stem}.{enc}.pc.snd
            emit(f"{bs_stem}.{enc}.pc.snd")

if __name__ == "__main__":
    generate()
