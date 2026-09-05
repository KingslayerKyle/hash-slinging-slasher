#!/usr/bin/env python3
"""Convert Cold War sound stems into Black Ops 4 SAB backslash format.

Cold War published tables contain ~862k sound asset names with forward slashes:
  wpn/assault/...
  vox/scripted/...
  fly/step/...
  amb/...
  zmb/...

Black Ops 4 sound assets live in SAB files and are hashed unfolded WITH BACKSLASHES:
  wpn\\assault\\...
  fly\\step\\...
  zmb\\...

Because sound_languages.py only emitted forward-slash versions, every Cold War seed
tested against BO4 was hashed with forward slashes and could never match.
This generator emits the backslash form across BO4 encodings.
"""
import os
import sys

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_root, "scripts"))
import snapshot

TABLES = [
    "fnv1a_xsounds",
    "fnv1a_english_xsounds",
]

ENCODINGS = ["ln100", "ll100", "sn100", "sl100", "rn75", "ln75"]

def generate():
    seen = set()
    def emit(s):
        if s not in seen:
            seen.add(s)
            print(s)

    # Read all sound names from tables and confirmed CW sound assets
    seeds = set(snapshot.table_names(*TABLES))
    seeds.update(snapshot.confirmed_names("sound_asset"))

    for name in seeds:
        name = name.strip().lower()
        if not name.endswith(".snd"):
            continue

        pieces = name[:-4].rsplit(".", 3)
        if len(pieces) == 4:
            stem, encoding, platform, language = pieces
        elif len(pieces) == 3:
            stem, encoding, platform = pieces
        else:
            continue

        # Convert forward slashes to backslashes for BO4
        bs_stem = stem.replace("/", "\\")

        for enc in ENCODINGS:
            # Emitted as: {stem}.{enc}.pc.snd
            emit(f"{bs_stem}.{enc}.pc.snd")

if __name__ == "__main__":
    generate()
