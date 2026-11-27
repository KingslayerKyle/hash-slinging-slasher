"""Find dialogue-independent aliases and animations that share a whole event identifier.

Run: python contrib/clip_event_aliases.py --game MODWAR7 --out logs/mw7-clip-events.txt
Confirm: bin/windows/confirm_list.exe logs/mw7-clip-events.txt --game MODWAR7 --label "whole clip event IDs with witnessed sound-alias take blocks" --script contrib/clip_event_aliases.py

Reads the selected capture and source-verified animation and sound-alias names.
For each two-token family, learns full alias or clip endings (one to four tokens,
or the exact same spelling) from pairs with identical event identifiers. Writes
a bounded list and witness counts. Reusable on modern captures with this naming
convention. Spent by the same held event names and witnessed ending blocks.

Initial MODWAR7 measurement: 4,643 alias control pairs and 29 clip control pairs.
The initial 250,000 candidates yielded 433 aliases. Removing those candidates
from the larger --limit 500000 output left 60,080 more, which yielded nine aliases.
Use --exclude to skip tested candidates. At lower witness thresholds, the family
must still contain an ending with at least four independent witnesses.
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

ASSET_NAME = re.compile(r"[a-z0-9]+(?:_[a-z0-9]+){3,}")
MIN_WITNESSES = 4


def family(name):
    return "_".join(name.split("_", 2)[:2])


def usable(names):
    return {name for name in names if not name.startswith("dx_") and ASSET_NAME.fullmatch(name)}


def witnessed_endings(bases, variants, min_witnesses=MIN_WITNESSES):
    witnesses = defaultdict(set)
    for name in variants:
        tokens = name.split("_")
        for base_size in range(max(4, len(tokens) - 4), len(tokens) + 1):
            base = "_".join(tokens[:base_size])
            if base in bases:
                witnesses[family(base), name[len(base):]].add(base)
    endings = defaultdict(dict)
    witnessed_families = {prefix for (prefix, _), known in witnesses.items() if len(known) >= MIN_WITNESSES}
    for (prefix, suffix), known in witnesses.items():
        if prefix in witnessed_families and len(known) >= min_witnesses:
            endings[prefix][suffix] = known
    return endings


def candidates(bases, variants, endings):
    matches = {}
    for base in bases:
        prefix = family(base)
        for ending, known in endings.get(prefix, {}).items():
            candidate = base + ending
            if candidate not in variants:
                matches[candidate] = max(matches.get(candidate, 0), len(known))
    return matches


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--game", required=True, choices=MODERN)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--limit", type=int, default=250_000)
    parser.add_argument("--min-witnesses", type=int, choices=(2, 3, 4), default=MIN_WITNESSES)
    parser.add_argument("--exclude", type=Path, action="append", default=[])
    args = parser.parse_args()
    if args.limit < 1:
        parser.error("--limit must be positive")

    clips = usable(named_names(args.game, "xanim"))
    aliases = usable(named_names(args.game, "sound_alias"))
    alias_endings = witnessed_endings(clips, aliases, args.min_witnesses)
    clip_endings = witnessed_endings(aliases, clips, args.min_witnesses)
    proposed_aliases = candidates(clips, aliases, alias_endings)
    proposed_clips = candidates(aliases, clips, clip_endings)
    combined = {name: max(proposed_aliases.get(name, 0), proposed_clips.get(name, 0))
                for name in proposed_aliases.keys() | proposed_clips.keys()}
    excluded = set()
    for path in args.exclude:
        excluded.update(path.read_text(encoding="utf-8").splitlines())
    ranked = sorted(combined.keys() - excluded, key=lambda name: (-combined[name], name))[:args.limit]

    with args.out.open("w", encoding="utf-8", newline="\n") as handle:
        handle.writelines(f"{name}\n" for name in ranked)
    report = {
        "game": args.game, "source_clips": len(clips), "source_aliases": len(aliases),
        "alias_rules": sum(map(len, alias_endings.values())),
        "clip_rules": sum(map(len, clip_endings.values())),
        "alias_controls": sum(len(known) for family in alias_endings.values() for known in family.values()),
        "clip_controls": sum(len(known) for family in clip_endings.values() for known in family.values()),
        "alias_candidates": len(proposed_aliases), "clip_candidates": len(proposed_clips),
        "distinct_candidates": len(combined), "prior_candidates": len(combined.keys() & excluded),
        "emitted_candidates": len(ranked),
    }
    args.out.with_suffix(".json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report))


if __name__ == "__main__":
    main()
