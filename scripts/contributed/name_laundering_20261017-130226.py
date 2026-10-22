"""Whole-name identity across pools of the same capture: is a known xanim name also an image name?

    PYTHONPATH=scripts python contrib/name_laundering.py [GAME]...

The existing cross-type methods (`cross_type.py`, `images_from_materials.py`) strip a name to a
*core* and re-spell it for another pool. Nobody had measured the simpler relation: take a name the
game holds in pool A, hash it whole under pool B's policy, and ask whether it lands on an id B
actually holds. If it lands on an *unnamed* one, that is a find available with no candidate
generation at all.

Two counts are printed per (A -> B) pair, and the second is the control:

  total   -- names that hash to any id B holds, named or not. ~0 here means the relation does not
             exist, and a zero in the next column would be about the shape of the sweep, not the
             ground.
  unnamed -- names that hash to an id B holds that nothing can name yet. This is the yield.
"""
import collections
import sys

from pathlib import Path
ROOT = Path(__file__).resolve().parent
while not (ROOT / "scripts" / "snapshot.py").is_file() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
if not (ROOT / "scripts" / "snapshot.py").is_file():
    raise SystemExit("Cannot locate the solver checkout")
sys.path.insert(0, str(ROOT / "scripts"))

import snapshot
import settings

POOLS = ("image", "material", "xanim", "xmodel", "sound_alias", "sound_asset")
TABLE = {
    "image": "fnv1a_ximages", "material": "fnv1a_xmaterials", "xanim": "fnv1a_xanims",
    "xmodel": "fnv1a_xmodels", "sound_alias": "fnv1a_soundbanks_aliases",
    "sound_asset": "fnv1a_xsounds",
}
SAMPLE = int(__import__("os").environ.get("SAMPLE", "200000"))


(ROOT / 'contrib').mkdir(parents=True, exist_ok=True)
finds = (ROOT / 'contrib/name_laundering_finds.txt').open('a', encoding='utf-8')


def measure(game):
    paths = [p for p in snapshot.snapshots() if snapshot.read(p).game == game]
    if not paths:
        print(f"{game}: no capture on disk")
        return
    snap = snapshot.read(paths[0])
    known = snapshot.known_hashes(game=game)
    unnamed = snap.unnamed(known)

    held = collections.defaultdict(set)
    for name in snap.by_pool():
        held[name] = set()
    for pool, ids in snap.by_pool().items():
        held[pool] = set(ids)

    # `unnamed()` returns one flat id -> pool mapping for the whole capture, not a dict per pool;
    # reading it per pool silently yields empty sets, which is how the first run of this script
    # printed a column of zeros that meant nothing. Per-pool wanted is the held ids minus what the
    # tables already name -- the same subtraction the engine makes, done where it can be checked.
    wanted = {pool: held[pool] - known for pool in held}

    names = {}
    for pool in POOLS:
        table = TABLE[pool]
        if game in snapshot.MODERN:
            table = table + "_v2"
            if pool == "xmodel":
                continue  # modern models carry embedded names; not huntable here
        got = [n.strip().lower().replace("\\", "/") for n in snapshot.table_names(table) if n.strip()]
        got = list(dict.fromkeys(got))[:SAMPLE]
        if got:
            names[pool] = got
        print(f"  {game} {pool:<12} {len(got):>8} known names sampled, "
              f"{len(held.get(pool, ())) :>9} ids held, {len(wanted.get(pool, ())):>8} unnamed")

    print(f"\n  {game}: whole-name identity across pools (rows = where the name is known, "
          f"columns = the pool tested)")
    header = "          " + "".join(f"{pool[:9]:>11}" for pool in names)
    print(header + "     total  unnamed")
    for source, source_names in names.items():
        total_all = 0
        unnamed_all = 0
        row = f"  {source:<8}"
        for target in names:
            hits = 0
            fresh = 0
            held_ids = held.get(target, set())
            wanted_ids = wanted.get(target, set())
            for name in source_names:
                digest = snapshot.fnv1a(name, game, target) & snapshot.ID_MASK
                if digest in held_ids:
                    hits += 1
                    if digest in wanted_ids:
                        fresh += 1
                        if source != target:
                            # Own-pool rows are excluded: a name that hashes to its own pool is
                            # the table's business, and the 3 the control printed on CW's diagonal
                            # are database-key spellings, not cross-pool finds.
                            finds.write(f"{game},{target},{name}\n")
            total_all += hits
            unnamed_all += fresh
            row += f"{hits:>7}/{fresh:<3}"
        print(row + f"{total_all:>9}{unnamed_all:>8}")


if __name__ == "__main__":
    games = sys.argv[1:] or ["BLKOPSCW", "BLKOPS04", "MODWAR22"]
    for game in games:
        print(f"\n=== {game}")
        measure(game)
