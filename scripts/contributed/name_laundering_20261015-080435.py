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
  unnamed -- names that hash to an id B holds that neither the current tables nor merged/open claims name yet. This is provisional yield.
"""
import argparse
from pathlib import Path
import collections
import sys

ROOT = Path(__file__).resolve().parent
while not (ROOT / "scripts/snapshot.py").is_file() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
if not (ROOT / "scripts/snapshot.py").is_file():
    raise SystemExit("Run inside a hash-slinging-slasher checkout")
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


def hash_for(name, game, pool):
    value = snapshot.fnv1a_nofold(name) if game == 'BLKOPS04' and pool == 'sound_asset' else snapshot.fnv1a(name, game, pool)
    return value & snapshot.ID_MASK


def claimed_ids(game):
    keys = set()
    for folder in (ROOT / 'submissions', Path(settings.path('findings', 'findings'))):
        for path in folder.rglob('*.txt'):
            for row in path.read_text(encoding='utf8', errors='replace').splitlines():
                raw, sep, _ = row.partition(',')
                if sep:
                    try: keys.add(int(raw, 16) & snapshot.ID_MASK)
                    except ValueError: pass
    path = ROOT / 'state/claimed.txt'
    if not path.is_file():
        raise ValueError('Run start first: current open-PR claims are required to measure unclaimed yield')
    for row in path.read_text(encoding='utf8').splitlines():
        try: keys.add(int(row, 16) & snapshot.ID_MASK)
        except ValueError: pass
    return keys


def measure(game, finds):
    paths = [p for p in snapshot.snapshots() if snapshot.read(p).game == game]
    if not paths:
        print(f"{game}: no capture on disk")
        return
    snap = snapshot.read(paths[0])
    known = {key & snapshot.ID_MASK for key in snapshot.known_hashes(game=game)}
    known.update(claimed_ids(game))

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
        got = [n for n in snapshot.table_names(table) if n and hash_for(n, game, pool) in held.get(pool, set())]
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
                digest = hash_for(name, game, target)
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
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('games', nargs='*', choices=sorted(snapshot.MODERN | {'BLKOPS04', 'BLKOPSCW'}))
    parser.add_argument('--output', type=Path, default=ROOT / 'contrib/name_laundering_finds.txt')
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('a', encoding='utf8') as finds:
        for game in args.games or ['BLKOPSCW', 'BLKOPS04', 'MODWAR22']:
            print(f"\n=== {game}")
            measure(game, finds)
