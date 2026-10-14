"""Export captured modern names by game and asset type for contributed generators.

Uses the shared verified table reader, then rehashes every seed against the selected
capture and pool. Writes only state/an/<GAME>_<type>.named; never submits anything.
Run after refreshing tables and submissions. Inputs absent from this checkout are
not inferred from a live game or another capture version.
"""
import argparse
from pathlib import Path
import snapshot

TABLES = {
    "image": "fnv1a_ximages_v2", "material": "fnv1a_xmaterials_v2",
    "xanim": "fnv1a_xanims_v2", "sound_asset": "fnv1a_xsounds_v2",
    "sound_alias": "fnv1a_soundbanks_aliases_v2",
}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("games", nargs="*", choices=sorted(snapshot.MODERN))
    args = parser.parse_args()
    selected = set(args.games or snapshot.MODERN)
    shots = [snapshot.read(p) for p in snapshot.snapshots()]
    available = {s.game.upper() for s in shots}
    if selected - available:
        parser.error("Missing captures: " + ", ".join(sorted(selected - available)))
    out = Path(snapshot.ROOT) / "state" / "an"
    out.mkdir(parents=True, exist_ok=True)
    for kind, table in TABLES.items():
        seeds = set(snapshot.table_names(table)) | set(snapshot.confirmed_names(kind))
        for shot in shots:
            game = shot.game.upper()
            if game not in selected:
                continue
            ids = set(shot.by_pool().get(kind, []))
            names = sorted(n for n in seeds if snapshot.fnv1a(n, game, kind) & snapshot.ID_MASK in ids)
            (out / f"{game}_{kind}.named").write_text("\n".join(names) + ("\n" if names else ""), encoding="utf-8")
            print(game, kind, len(names))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
