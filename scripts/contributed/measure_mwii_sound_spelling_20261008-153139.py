"""Which separator spelling does each modern game actually hash its sound names with?

The published `_v2` sound tables store Saluki *display* paths, which use `/`. For each row this
checks which candidate spelling reproduces the stored database key, and only counts names the
chosen game's own capture actually holds -- so the answer is a property of that game, not of the
table. Writes nothing; prints the breakdown.
"""
import collections
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import settings
import snapshot


def spellings(display):
    """Same candidate order as snapshot.verified_database_row, but labelled."""
    return (
        ("slash", display.replace("\\", "/")),
        ("dot", display.replace("/", ".").replace("\\", ".")),
        ("backslash", display.replace("/", "\\")),
    )


def main():
    game = settings.game()
    if game not in snapshot.MODERN:
        raise SystemExit("modern game only")
    path = [p for p in snapshot.snapshots() if snapshot.read(p).game == game][0]
    snap = snapshot.read(path)
    held = {kind: set(ids) for kind, ids in snap.by_pool().items()}
    tables = [("sound_asset", "fnv1a_xsounds_v2"),
              ("sound_alias", "fnv1a_soundbanks_aliases_v2")]
    out = {}
    for kind, table in tables:
        tally = collections.Counter()
        ids = held.get(kind, set())
        source_mask = snapshot.database_policy(table)[1]
        for line in (Path(settings.tables_csv()) / (table + ".csv")).open(encoding="utf-8"):
            key, sep, display = line.strip().partition(",")
            if not sep:
                continue
            try:
                key = int(key, 16)
            except ValueError:
                continue
            if key not in ids and (key & snapshot.ID_MASK) not in ids:
                continue
            found = None
            for label, candidate in spellings(display):
                if snapshot.database_source_hash(table, candidate) & source_mask == key:
                    found = label
                    break
            tally[found or "unrestorable"] += 1
        out[kind] = {"held": len(ids), **dict(tally)}
    print(json.dumps({"game": game, "spelling": out}, indent=2))


if __name__ == "__main__":
    main()
