"""Measure target-held terrain blend tokens and build a bounded four-layer plan.

Uses source-verified modern materials and hash-verified community findings.
Only tokens observed on this target capture are used. Generated plans and lists
remain under contrib; confirm_plan must independently verify every recovery.
"""
import argparse
from collections import Counter
from itertools import product
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent
while ROOT != ROOT.parent and not (ROOT / 'scripts/snapshot.py').is_file():
    ROOT = ROOT.parent
if not (ROOT / 'scripts/snapshot.py').is_file():
    ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / 'scripts'))
import snapshot

def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--game', required=True, choices=sorted(snapshot.MODERN))
    parser.add_argument('--top', type=int, default=600)
    args = parser.parse_args()
    if not 1 <= args.top <= 600:
        parser.error('--top must be between 1 and 600')
    shot = snapshot.read(ROOT / 'snapshots' / (args.game.lower() + '.ids'))
    assert shot.game == args.game
    held = set(shot.by_pool()['material'])
    names = set(snapshot.table_names('fnv1a_xmaterials_v2'))
    for top in ['all_names', 'submissions', 'findings']:
        for path in (ROOT / top).rglob('material*.txt'):
            for line in path.read_text(encoding='utf-8').splitlines():
                raw, sep, name = line.partition(',')
                if not sep or not name.startswith('twc/*'):
                    continue
                try:
                    key = int(raw, 16) & snapshot.ID_MASK
                except ValueError:
                    continue
                if snapshot.fnv1a(name, args.game, 'material') & snapshot.ID_MASK == key:
                    names.add(name.lower())
    tokens, layers, quads = Counter(), Counter(), []
    for name in names:
        if not name.startswith('twc/*') or snapshot.fnv1a(name, args.game, 'material') & snapshot.ID_MASK not in held:
            continue
        parts = name[5:].split('_')
        if not all(re.fullmatch(r'\d+d?n', token) for token in parts):
            continue
        tokens.update(parts)
        layers[len(parts)] += 1
        if len(parts) == 4:
            quads.append(parts)
    selected = [token for token, _ in tokens.most_common(args.top)]
    if not selected:
        raise SystemExit('No verified terrain conventions on this capture')
    selected_set = set(selected)
    covered = sum(set(parts) <= selected_set for parts in quads)
    out = ROOT / 'contrib/verified_terrain_blends' / args.game.lower()
    out.mkdir(parents=True, exist_ok=True)
    begin, stem, end = [out / (part + '.txt') for part in ['quad-begins', 'quad-stems', 'quad-ends']]
    with begin.open('w', encoding='utf-8') as stream:
        for a, b in product(selected, repeat=2):
            stream.write(f'0,twc/*{a}_{b}_\n')
    stem.write_text(''.join('0,' + t + '\n' for t in selected), encoding='utf-8')
    end.write_text(''.join('0,_' + t + '\n' for t in selected), encoding='utf-8')
    plan = out / 'quads.plan.txt'
    plan.write_text(f'label: {args.game} four-layer terrain blends from target-held tokens\n'
                    f'describe: four terrain layers crossed over the {len(selected)} most frequent numeric tokens in hash-verified terrain materials on this capture; known four-layer coverage {covered}/{len(quads)}\n'
                    f'game: {args.game}\nbegin: @{begin.relative_to(ROOT).as_posix()}\n'
                    f'stem: @{stem.relative_to(ROOT).as_posix()}\nend: @{end.relative_to(ROOT).as_posix()}\n'
                    'bare: no\nfold: yes\n', encoding='utf-8')
    report = {'game': args.game, 'known_layers': dict(layers), 'tokens': len(tokens), 'selected_tokens': len(selected),
              'known_quads': len(quads), 'covered_quads': covered, 'candidates': len(selected)**4,
              'plan': plan.relative_to(ROOT).as_posix()}
    (out / 'measurement.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report))

if __name__ == '__main__':
    main()
