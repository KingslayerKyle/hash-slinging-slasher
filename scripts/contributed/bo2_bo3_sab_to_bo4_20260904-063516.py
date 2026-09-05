#!/usr/bin/env python3
"""Transfer BO2 & BO3 SAB stems into BO4's unfolded literal-backslash sound_asset pool."""
import os
import re
import sys

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ENCODINGS = [".ln100.pc.snd", ".ll100.pc.snd", ".sn100.pc.snd", ".sl100.pc.snd"]
LANGS = {"english", "russian", "french", "german", "spanish", "italian", "japanese", "polish", "korean", "chinese"}

def generate():
    seen = set()
    def emit(s):
        s = s.strip()
        if s and s not in seen:
            seen.add(s)
            print(s)

    stems = set()
    csv_files = [
        os.path.join(_root, "cod-name-db", "csv", "bo2_sab.csv"),
        os.path.join(_root, "cod-name-db", "csv", "bo3_sab.csv")
    ]

    for csv_file in csv_files:
        if not os.path.exists(csv_file):
            continue
        with open(csv_file, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                parts = line.strip().split(",")
                if len(parts) < 2:
                    continue
                path = parts[1].strip().lower().replace("/", "\\")
                m = re.match(r"^(.*?)\.[a-z0-9]+\.(?:pc|xenon|ps3|all)\.snd.*$", path)
                if m:
                    stem = m.group(1)
                else:
                    stem = path.split(".")[0]
                if not stem:
                    continue
                stems.add(stem)

                # Also try without devraw\ or language prefix
                clean = re.sub(r"^(?:devraw\\)?(?:[a-z]+)\\", lambda match: "" if match.group(0).split("\\")[-2] in LANGS or "devraw" in match.group(0) else match.group(0), stem)
                if clean and clean != stem:
                    stems.add(clean)

    for stem in stems:
        for enc in ENCODINGS:
            emit(f"{stem}{enc}")

if __name__ == "__main__":
    generate()
