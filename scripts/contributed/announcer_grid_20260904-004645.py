"""Fill missing announcer lines in Black Ops sound aliases.

Compares announcer voice sets (anbo, anme, abnd, adgi, ahva, ami6) and generates
candidates for lines shared between primary announcers but omitted from others.
"""
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
while ROOT != os.path.dirname(ROOT) and not os.path.isfile(os.path.join(ROOT, "scripts", "snapshot.py")):
    ROOT = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import snapshot


def main():
    names = set(snapshot.table_names("fnv1a_soundbanks_aliases"))
    names.update(snapshot.confirmed_names("sound_alias"))

    announcers = ["anbo", "anme", "abnd", "adgi", "ahva", "ami6"]
    anbo_tails = {n[len("vox_anbo_"):] for n in names if n.startswith("vox_anbo_")}
    anme_tails = {n[len("vox_anme_"):] for n in names if n.startswith("vox_anme_")}
    common_tails = anbo_tails & anme_tails

    candidates = set()
    for op in ["abnd", "adgi", "ahva", "ami6"]:
        op_tails = {n[len(f"vox_{op}_"):] for n in names if n.startswith(f"vox_{op}_")}
        for t in common_tails - op_tails:
            cand = f"vox_{op}_{t}"
            if cand not in names:
                candidates.add(cand)

    print(f"Generated {len(candidates)} announcer candidates from {len(common_tails)} shared tails", file=sys.stderr)
    for cand in sorted(candidates):
        print(cand)


if __name__ == "__main__":
    main()
