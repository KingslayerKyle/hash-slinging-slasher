"""Fill modern sound take families witnessed by this game's captured sound-file pool.

Preserve each witnessed directory, numeric width and exact encoding suffix. At
least two named takes must reproduce IDs in the target game's sound-file pool.
Only bounded gaps and a small edge margin are tried; other asset types and model
names are never used. Rehash every complete candidate, exclude database and
claimed keys, and pass output through normal sound_asset confirmation/submission.
"""
import argparse
from collections import defaultdict
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
while ROOT != ROOT.parent and not (ROOT / 'scripts/snapshot.py').is_file():
    ROOT = ROOT.parent
if not (ROOT / 'scripts/snapshot.py').is_file():
    ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / 'scripts'))
import families
import snapshot
import settings

MASK = (1 << 64) - 1

def feed(value, text):
    for byte in text.encode('ascii'):
        value = ((value ^ byte) * snapshot.PRIME) & MASK
    return value

def corpus():
    names = set(snapshot.table_names('fnv1a_xsounds_v2'))
    for top in ['all_names', 'findings']:
        for path in (ROOT / top).glob('*/sound_asset.txt'):
            for row in path.read_text(encoding='utf-8').splitlines():
                raw, sep, name = row.partition(',')
                if not sep or not name.isascii():
                    continue
                try:
                    key = int(raw, 16) & snapshot.ID_MASK
                except ValueError:
                    continue
                name = name.strip().lower().replace(chr(92), '/')
                if snapshot.fnv1a(name, 'MODWAR7', 'sound_asset') & snapshot.ID_MASK == key:
                    names.add(name)
    return {n.lower().replace(chr(92), '/') for n in names if n.isascii()}

def solve_group(before, width, after, seen, wanted, margin):
    if len(seen) < 2 or max(seen) - min(seen) > families.WIDEST:
        return {}, 0
    found = {}
    tested = 0
    prefix = snapshot.fnv1a(before, 'MODWAR7', 'sound_asset')
    for number in range(max(0, min(seen) - margin), min(999, max(seen) + margin) + 1):
        if number in seen:
            continue
        digits = f'{number:0{width}d}'
        full = feed(feed(prefix, digits), after)
        tested += 1
        key = full & snapshot.ID_MASK
        if key not in wanted:
            continue
        name = before + digits + after
        assert snapshot.fnv1a(name, 'MODWAR7', 'sound_asset') == full
        found[name] = key
    return found, tested

def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument('--game', choices=sorted(snapshot.MODERN), required=True)
    p.add_argument('--margin', type=int, default=16)
    p.add_argument('--measure', action='store_true')
    a = p.parse_args()
    if not 0 <= a.margin <= 64:
        p.error('margin must be 0..64')
    shot = snapshot.read(ROOT / 'snapshots' / (a.game.lower() + '.ids'))
    assert shot.game == a.game
    held = set(shot.by_pool()['sound_asset'])
    names = corpus()
    known = {h & snapshot.ID_MASK for h in snapshot.known_hashes(game=a.game)}
    claimed = ROOT / 'state/claimed.txt'
    if claimed.exists():
        for line in claimed.read_text().splitlines():
            try:
                known.add(int(line, 16) & snapshot.ID_MASK)
            except ValueError:
                pass
    groups = defaultdict(set)
    for name in names:
        key = snapshot.fnv1a(name, a.game, 'sound_asset') & snapshot.ID_MASK
        known.add(key)
        if key not in held:
            continue
        match = families.SOUND_TAKE.fullmatch(name)
        if match:
            before, digits, after = match.groups()
            groups[before, len(digits), after].add(int(digits))
    wanted = held - known
    found = {}
    tested = 0
    witnessed = 0
    for (before, width, after), seen in sorted(groups.items()):
        hits, count = solve_group(before, width, after, seen, wanted, a.margin)
        witnessed += bool(count)
        tested += count
        found.update(hits)
    by_id = defaultdict(list)
    for name, key in found.items():
        by_id[key].append(name)
    safe = {names[0] for names in by_id.values() if len(names) == 1}
    report = dict(game=a.game, witnessed_families=witnessed, candidates=tested,
                  unresolved_unclaimed=len(wanted), verified_new=len(safe),
                  ambiguous_ids=sum(len(v) > 1 for v in by_id.values()))
    print(json.dumps(report), file=sys.stderr)
    if a.measure:
        print(json.dumps(report))
    else:
        for name in sorted(safe):
            print(name)

if __name__ == '__main__':
    main()
