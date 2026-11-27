"""Recover campaign dialogue aliases and facial clips that share a line identifier.

Run: python contrib/campaign_face_siblings.py --game MODWAR7 --out logs/mw7-face-candidates.txt
Confirm: bin/windows/confirm_list.exe logs/mw7-face-candidates.txt --game MODWAR7 --label "campaign facial clip and dialogue alias siblings" --script contrib/campaign_face_siblings.py

Reads the selected capture and its source-verified campaign aliases and animations.
Learns exact facial clip suffixes from matched line identifiers. Writes candidates
and a compact control report. Reusable across modern games. Spent by unchanged
target-held dialogue names and observed suffixes.
"""

import argparse
from collections import defaultdict
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent
while ROOT != ROOT.parent and not (ROOT / "scripts" / "snapshot.py").is_file():
    ROOT = ROOT.parent
sys.path.insert(0, str(ROOT / "scripts"))

from generator_inputs import MODERN, named_names

CAMPAIGN_LINE = re.compile(r"dx_sp_(?:[a-z0-9]+_){3,}[a-z0-9]+")
FACIAL_TAKE = re.compile(r"_\d{1,3}_face$")


def generate(animations, aliases):
    clips = {name for name in animations
             if name.endswith("_face") and CAMPAIGN_LINE.fullmatch(name.removesuffix("_face"))}
    lines = {name for name in aliases if CAMPAIGN_LINE.fullmatch(name)}
    controls = defaultdict(set)
    for clip in clips:
        take = FACIAL_TAKE.search(clip)
        endings = ("_face", take[0]) if take else ("_face",)
        for suffix in endings:
            body = clip.removesuffix(suffix)
            if body in lines:
                controls[suffix].add(body)

    suffixes = {suffix for suffix, witnesses in controls.items() if len(witnesses) >= 3}
    stems = set()
    for clip in clips:
        for suffix in suffixes:
            if clip.endswith(suffix):
                body = clip.removesuffix(suffix)
                if CAMPAIGN_LINE.fullmatch(body):
                    stems.add(body)
    alias_candidates = stems - aliases
    animation_candidates = {line + suffix for line in lines for suffix in suffixes} - animations
    report = {
        "facial_clips": len(clips), "campaign_aliases": len(lines),
        "witnesses_by_suffix": {suffix: len(controls[suffix]) for suffix in sorted(controls)},
        "used_suffixes": sorted(suffixes),
        "alias_candidates": len(alias_candidates), "animation_candidates": len(animation_candidates),
    }
    return alias_candidates | animation_candidates, report


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--game", required=True, choices=MODERN)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    candidates, report = generate(named_names(args.game, "xanim"), named_names(args.game, "sound_alias"))
    with args.out.open("w", encoding="utf-8", newline="\n") as handle:
        handle.writelines(f"{name}\n" for name in sorted(candidates))
    report.update(game=args.game, emitted_candidates=len(candidates))
    args.out.with_suffix(".json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report))


if __name__ == "__main__":
    main()
