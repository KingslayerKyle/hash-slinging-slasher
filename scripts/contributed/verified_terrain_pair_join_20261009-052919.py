"""Join two verified terrain pairs to predict four-layer blends on one target.

The measured pair identities preserve numeric tokens, qualifiers and order.
Writes a compact plan for the compiled engine; confirm material-only on this
explicit game. Reads verified names and the canonical capture, never a game.
"""
import argparse
from collections import defaultdict
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent
while ROOT != ROOT.parent and not (ROOT / 'scripts/snapshot.py').is_file():
    ROOT = ROOT.parent
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
    pairs, quads = set(), set()
    for name in corpus():
        if not name.startswith('twc/*') or snapshot.fnv1a(name, args.game, 'material') & snapshot.ID_MASK not in held: continue
        parts = tuple(name[5:].split('_'))
        if not all(re.fullmatch(r'\d+d?n', p) for p in parts): continue
        if len(parts) == 2: pairs.add(parts)
        elif len(parts) == 4: quads.add(parts)
    assert pairs, 'No verified pairs on this target'
    covered = sum(q[:2] in pairs and q[2:] in pairs for q in quads)
    out = ROOT / 'contrib/verified_terrain_pair_join' / args.game.lower()
    out.mkdir(parents=True, exist_ok=True)
    begin, stem = out / 'begins.txt', out / 'stems.txt'
    begin.write_text(''.join('0,twc/*' + '_'.join(p) + '_\n' for p in sorted(pairs)), encoding='utf-8')
    stem.write_text(''.join('0,' + '_'.join(p) + '\n' for p in sorted(pairs)), encoding='utf-8')
    plan = out / 'quads.plan.txt'
    plan.write_text(f'label: {args.game} terrain four-layer joins of target-held pairs\n'
                    f'describe: join two hash-verified two-layer blends held in the target capture, preserving their qualifiers and layer order; represents {covered}/{len(quads)} already verified target quads\n'
                    f'game: {args.game}\nbegin: @{begin.relative_to(ROOT).as_posix()}\n'
                    f'stem: @{stem.relative_to(ROOT).as_posix()}\nbare: no\nfold: yes\n', encoding='utf-8')
    report = {'game': args.game, 'pairs': len(pairs), 'known_quads': len(quads), 'covered_known_quads': covered,
              'candidates': len(pairs)**2, 'plan': plan.relative_to(ROOT).as_posix()}
    (out / 'measurement.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report))

if __name__ == '__main__': main()
