#!/usr/bin/env python3
"""Systematic Operator Voice Callout Grid Generator for Cold War sound_aliases."""
import os
import re
import sys

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def generate():
    seen = set()
    known = set()
    speakers = set()
    suffixes = set()

    alias_file = os.path.join(_root, "all_names", "blkopscw", "sound_alias.txt")
    if os.path.exists(alias_file):
        with open(alias_file, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                parts = line.strip().split(",")
                if len(parts) >= 2:
                    alias = parts[1].strip().lower()
                    known.add(alias)
                    m = re.match(r"^vox_([a-z0-9]+)_(.+)$", alias)
                    if m:
                        speaker = m.group(1)
                        suffix = m.group(2)
                        speakers.add(speaker)
                        suffixes.add(suffix)

    # Filter out single-use non-operator speakers (keep those that have >= 5 suffixes)
    speaker_counts = {}
    with open(alias_file, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            parts = line.strip().split(",")
            if len(parts) >= 2:
                alias = parts[1].strip().lower()
                m = re.match(r"^vox_([a-z0-9]+)_(.+)$", alias)
                if m:
                    s = m.group(1)
                    speaker_counts[s] = speaker_counts.get(s, 0) + 1

    valid_speakers = {s for s, count in speaker_counts.items() if count >= 10}

    # Also add standard operator variations if missing
    for base in ["mrs", "frs", "bsp", "msp", "epo", "nao", "ncm", "njf", "nlc", "nns", "nsp", "uao", "ucm", "ujf", "ulc", "uns", "usp"]:
        for i in range(1, 10):
            valid_speakers.add(f"{base}{i}")

    sys.stderr.write(f"Speakers: {len(valid_speakers)}, Suffixes: {len(suffixes)}\n")

    for spk in sorted(valid_speakers):
        for sfx in suffixes:
            cand = f"vox_{spk}_{sfx}"
            if cand not in known and cand not in seen:
                seen.add(cand)
                print(cand)

if __name__ == "__main__":
    generate()
