"""Measure per-game candidate fragments from reproducible names held in its capture.

python scripts/derive_modern_lists.py --game BLACKOP6
Writes ignored data/modern/<game> lists; preserves the committed BO4/CW vocabulary.
"""
import collections
import json
from pathlib import Path
import re
import sys
import settings
import snapshot


def main():
    game = settings.game()
    if game not in snapshot.MODERN:
        raise SystemExit("Use derive_lists.py for the legacy corpus")
    paths = [Path(p) for p in snapshot.snapshots() if snapshot.read(p).game == game]
    if len(paths) != 1:
        raise SystemExit("Need one combined capture for this game")
    snap = snapshot.read(paths[0])
    held = {kind: set(ids) for kind, ids in snap.by_pool().items()}
    tables = [("image", "fnv1a_ximages_v2"), ("material", "fnv1a_xmaterials_v2"),
              ("xanim", "fnv1a_xanims_v2"), ("sound_asset", "fnv1a_xsounds_v2"),
              ("sound_alias", "fnv1a_soundbanks_aliases_v2")]
    measured = {}
    verified = {}
    for kind, table in tables:
        begins, ends = collections.Counter(), collections.Counter()
        seen = set()
        for line in (Path(settings.tables_csv()) / (table+".csv")).open(encoding="utf-8"):
            key, _, name = line.strip().partition(",")
            try:
                key = int(key, 16)
            except ValueError:
                continue
            if key & snapshot.ID_MASK not in held.get(kind, set()):
                continue
            restored = snapshot.verified_database_row(table,key,name)
            if restored is None:
                continue
            full,name = restored
            if snapshot.fnv1a(name, game, kind) != full or name in seen:
                continue
            seen.add(name)
            local_begins, local_ends = set(), set()
            directory, _, base = name.rpartition("/")
            if directory:
                local_begins.add(directory+"/")
            parts = base.split("_")
            for width in range(1, min(3, len(parts))):
                local_begins.add((directory+"/" if directory else "")+"_".join(parts[:width])+"_")
                local_ends.add("_"+"_".join(parts[-width:]))
            # Actual encoding tails are essential for both dotted IW names and slash-style names.
            match = re.search(r"\.(?:l|s|t|r)n[^/]*$", base)
            if match:
                local_ends.add(match[0])
            begins.update(local_begins)
            ends.update(local_ends)
        measured[kind] = (begins, ends)
        verified[kind] = len(seen)
    folder = Path(settings.ROOT) / "data/modern" / game.lower()
    folder.mkdir(parents=True, exist_ok=True)
    for sounds in (False, True):
        selected = [pair for kind, pair in measured.items() if kind.startswith("sound") == sounds]
        for column, label, limit in [(0, "prefixes", 700), (1, "suffixes", 4800)]:
            total = collections.Counter()
            guaranteed = set()
            for pair in selected:
                total.update(pair[column])
                guaranteed.update(item for item, _ in pair[column].most_common(limit//max(1,len(selected))*1//2))
            ranked = [item for item, _ in total.most_common() if item not in guaranteed]
            items = sorted(guaranteed | set(ranked[:max(0,limit-len(guaranteed))]))
            (folder / (("sound." if sounds else "")+label+".txt")).write_text("\n".join(items)+"\n")
    report = {"game": game, "verified_names_by_type": verified, "snapshot": paths[0].name}
    (folder / "measurement.json").write_text(json.dumps(report, indent=2)+"\n")
    print(json.dumps(report))


if __name__ == "__main__":
    main()
