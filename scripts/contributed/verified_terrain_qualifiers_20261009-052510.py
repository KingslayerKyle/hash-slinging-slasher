"""Complete qualifier siblings of verified, target-held four-layer terrain blends.

Retains the four numeric layer identities and their order. Only n/dn forms
observed for each numeric identity on the target are combined. Candidates
require normal material-only confirmation and submission for that game.
"""
import argparse
from collections import defaultdict
from itertools import product
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent
while ROOT != ROOT.parent and not (ROOT / 'scripts/snapshot.py').is_file(): ROOT = ROOT.parent
if not (ROOT / 'scripts/snapshot.py').is_file(): ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / 'scripts'))
import snapshot

def corpus():
    names = set(snapshot.table_names('fnv1a_xmaterials_v2'))
    for top in ['all_names', 'submissions', 'findings']:
        for path in (ROOT / top).rglob('material*.txt'):
            for row in path.read_text(encoding='utf-8').splitlines():
                raw, sep, name = row.partition(',')
                if not sep or not name.startswith('twc/*'): continue
                try: key = int(raw, 16) & snapshot.ID_MASK
                except ValueError: continue
                if snapshot.fnv1a(name, 'YAMYAMOK', 'material') & snapshot.ID_MASK == key:
                    names.add(name.lower())
    return names

def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--game', required=True, choices=sorted(snapshot.MODERN))
    args = parser.parse_args()
    shot = snapshot.read(ROOT / 'snapshots' / (args.game.lower() + '.ids'))
    assert shot.game == args.game
    held = set(shot.by_pool()['material'])
    forms, bases, known = defaultdict(set), set(), set()
    for name in corpus():
        if not name.startswith('twc/*') or snapshot.fnv1a(name, args.game, 'material') & snapshot.ID_MASK not in held: continue
        parts = name[5:].split('_')
        matches = [re.fullmatch(r'(\d+)d?n', p) for p in parts]
        if not all(matches): continue
        for part, match in zip(parts, matches): forms[match[1]].add(part)
        if len(parts) == 4:
            bases.add(tuple(m[1] for m in matches))
            known.add(name)
    candidates = set()
    for base in bases:
        for parts in product(*(sorted(forms[n]) for n in base)):
            candidates.add('twc/*' + '_'.join(parts))
    candidates.difference_update(known)
    out = ROOT / 'contrib/verified_terrain_qualifiers' / args.game.lower()
    out.mkdir(parents=True, exist_ok=True)
    target = out / 'quads.txt'
    target.write_text(''.join('0,' + n + '\n' for n in sorted(candidates)), encoding='utf-8')
    print(json.dumps({'game': args.game, 'known_quads': len(known), 'numeric_layer_groups': len(bases),
                      'candidates': len(candidates), 'list': target.relative_to(ROOT).as_posix()}))

if __name__ == '__main__': main()
