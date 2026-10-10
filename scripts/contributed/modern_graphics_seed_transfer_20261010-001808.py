"""Transfer source-verified images, materials and animations to a modern snapshot.

Emits candidate names only. Feed into confirm_list for the selected game's normal
hashing, asset-pool verification, published/open-name exclusions and run record.
Includes fresh community submissions, which can precede the published database.
"""
import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
while ROOT != ROOT.parent and not (ROOT / 'scripts/snapshot.py').is_file():
    ROOT = ROOT.parent
if not (ROOT / 'scripts/snapshot.py').is_file():
    ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / 'scripts'))
import snapshot

TABLES = {'image': 'fnv1a_ximages', 'material': 'fnv1a_xmaterials', 'xanim': 'fnv1a_xanims'}

def corpus():
    names = set()
    for kind, table in TABLES.items():
        names.update(snapshot.table_names(table, table + '_v2'))
        for top in ['all_names', 'submissions', 'findings']:
            for path in (ROOT / top).rglob(kind + '*.txt'):
                for line in path.read_text(encoding='utf-8').splitlines():
                    raw, sep, name = line.partition(',')
                    if not sep or not name:
                        continue
                    try:
                        key = int(raw, 16) & snapshot.ID_MASK
                    except ValueError:
                        continue
                    if any(snapshot.fnv1a(name, game=game, kind=kind) & snapshot.ID_MASK == key
                           for game in ['YAMYAMOK', 'BLKOPSCW']):
                        names.add(name.lower().replace(chr(92), '/'))
    return names

def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--game', choices=sorted(snapshot.MODERN), default='YAMYAMOK')
    args = parser.parse_args()
    shot = snapshot.read(ROOT / 'snapshots' / (args.game.lower() + '.ids'))
    if shot.game != args.game:
        raise SystemExit('snapshot game mismatch')
    names = corpus()
    print(f'{len(names)} source-verified graphics candidates for {args.game}', file=sys.stderr)
    for name in sorted(names):
        print(name)

if __name__ == '__main__':
    main()
