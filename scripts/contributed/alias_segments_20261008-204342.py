"""Writes the stem and ending lists for the alias segment plan (contrib/alias_segments.plan.txt).

Stems: every alias candidate `alias_from_files.py` derives from known sound files, plus every
segment-trim of every alias known in any game. Endings: every 1-3 segment tail (`_plr`,
`_npc_far`, `_lr_close`) that known aliases carry, ranked by how many distinct aliases carry it.
The engine multiplies the two; printing that product would take Python hours.

    python contrib/alias_segments.py --ends 3000
    confirm_plan contrib/alias_segments.plan.txt --game BLACKOP6
"""
from pathlib import Path
import argparse
import collections
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
while not (ROOT / "scripts" / "snapshot.py").is_file() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
CONTRIB = ROOT / "contrib"


def known_aliases():
    for f in sorted((ROOT / "cod-name-db" / "csv").glob("*aliases*.csv")):
        for line in f.open(encoding="utf-8", errors="replace"):
            yield line.rstrip("\r\n").partition(",")[2].lower()
    for top in ("all_names", "submissions", "findings"):
        for f in sorted((ROOT / top).rglob("sound_alias*.txt")):
            for line in f.open(encoding="utf-8", errors="replace"):
                key, sep, name = line.rstrip("\r\n").partition(",")
                if sep:
                    yield name.lower()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ends", type=int, default=3000)
    a = ap.parse_args()
    stems = set(subprocess.run([sys.executable, str(CONTRIB / "alias_from_files.py")],
                               capture_output=True, text=True, check=True).stdout.split())
    ends = collections.Counter()
    for alias in set(known_aliases()):
        if not alias or "/" in alias or "." in alias:
            continue
        parts = alias.split("_")
        for n in range(1, len(parts)):
            stems.add("_".join(parts[:n]))
        for k in range(1, min(3, len(parts) - 1) + 1):
            ends["_" + "_".join(parts[-k:])] += 1
    stems = sorted(s for s in stems if len(s) > 2)
    top = [e for e, _ in ends.most_common(a.ends)]
    (CONTRIB / "alias_stems.txt").write_text("".join(s + "\n" for s in stems), encoding="utf-8")
    (CONTRIB / "alias_ends.txt").write_text("".join(e + "\n" for e in top), encoding="utf-8")
    print(f"{len(stems)} stems, {len(top)} endings", file=sys.stderr)


if __name__ == "__main__":
    main()
