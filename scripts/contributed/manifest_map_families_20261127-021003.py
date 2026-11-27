"""Find map-family siblings using identifiers from shipped techset manifests.

Run: python contrib/manifest_map_families.py --game MODWAR7 --manifest <path>/cod26/techsets_manifest.csv --manifest <path>/sp26/techsets_manifest.csv --out logs/mw7-map-candidates.txt
Confirm: bin/windows/confirm_list.exe logs/mw7-map-candidates.txt --game MODWAR7 --label "shipped manifest map siblings" --script contrib/manifest_map_families.py

Reads explicit retail CSV manifests, the configured capture and verified corpus.
Tracks which maps independently establish each spelling. Writes a bounded list
of candidates plus a JSON report with per-pool controls and candidate counts.
Reusable on modern captures. Spent by the same manifest identifiers and held
asset names witnessing the same templates. No game process or payload is read.
"""

import argparse
from collections import Counter, defaultdict
import csv
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent
while ROOT != ROOT.parent and not (ROOT / "scripts" / "snapshot.py").is_file():
    ROOT = ROOT.parent
sys.path.insert(0, str(ROOT / "scripts"))

from generator_inputs import MODERN, TABLES, named_names

ZONE_FILE = re.compile(r"techsets_((?:mp|sp|zm|cp|wz|br|coop)_[a-z0-9]+_[a-z0-9_]+)\.ff")
SUBZONE_ENDINGS = ("_entities", "_subset_ai")


def manifest_zones(paths):
    zones = set()
    for path in paths:
        with path.open(encoding="utf-8-sig", newline="") as handle:
            for row in csv.reader(handle):
                match = ZONE_FILE.fullmatch(row[0].strip().lower()) if row else None
                if match:
                    zones.add(match[1])
    return {
        zone for zone in zones
        if not any(zone.endswith(end) and zone.removesuffix(end) in zones for end in SUBZONE_ENDINGS)
    }


def zone_forms(zones):
    forms = defaultdict(set)
    choices = defaultdict(set)
    for zone in zones:
        mode, code, short = zone.split("_", 2)
        for form, spelling in (("zone", zone), ("code-map", f"{code}_{short}")):
            forms[spelling].add((mode, form, zone))
            choices[mode, form].add((zone, spelling))
    alternatives = "|".join(map(re.escape, sorted(forms, key=lambda x: (-len(x), x))))
    pattern = re.compile(rf"(?<![a-z0-9])(?:{alternatives})(?![a-z0-9])")
    return forms, choices, pattern


def witnessed_templates(names, forms, pattern):
    witnesses = defaultdict(set)
    for name in names:
        if not name.isascii() or "," in name:
            continue
        for match in pattern.finditer(name):
            for mode, form, zone in forms[match[0]]:
                frame = (mode, form, name[:match.start()], name[match.end():])
                witnesses[frame].add(zone)
    return witnesses


def generate(game, zones):
    forms, choices, pattern = zone_forms(zones)
    data = []
    seen_zones = Counter()
    for kind in TABLES:
        names = named_names(game, kind)
        witnesses = witnessed_templates(names, forms, pattern)
        for group in witnesses.values():
            seen_zones.update(group)
        data.append((kind, names, witnesses))

    scores = {}
    report = {}
    for kind, names, witnesses in data:
        frames = [(frame, group) for frame, group in witnesses.items() if len(group) >= 2]
        proposed = set()
        for (mode, form, before, after), group in frames:
            for zone, spelling in choices[mode, form]:
                if zone in group:
                    continue
                candidate = before + spelling + after
                if candidate in names:
                    continue
                proposed.add(candidate)
                score = (bool(seen_zones[zone]), len(group), seen_zones[zone])
                scores[candidate] = max(scores.get(candidate, score), score)
        report[kind] = {
            "held_names": len(names),
            "matching_zones": len(set().union(*witnesses.values())),
            "witnessed_patterns": len(frames),
            "leave_one_zone_out_controls": sum(len(group) for _, group in frames if len(group) >= 3),
            "candidate_names": len(proposed),
        }
    return scores, report


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--game", required=True, choices=MODERN)
    parser.add_argument("--manifest", required=True, type=Path, action="append")
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--limit", type=int, default=25_000)
    args = parser.parse_args()
    if args.limit < 1:
        parser.error("--limit must be positive")
    zones = manifest_zones(args.manifest)
    if not zones:
        parser.error("no map zones found in the supplied manifests")

    scores, pools = generate(args.game, zones)
    candidates = sorted(scores, key=lambda name: (*(-v for v in scores[name]), name))[:args.limit]
    with args.out.open("w", encoding="utf-8", newline="\n") as handle:
        handle.writelines(f"{name}\n" for name in candidates)
    report = {"game": args.game, "manifest_zones": len(zones), "pools": pools,
              "distinct_candidates": len(scores), "emitted_candidates": len(candidates)}
    args.out.with_suffix(".json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report))


if __name__ == "__main__":
    main()
