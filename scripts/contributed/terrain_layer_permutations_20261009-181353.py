"""Recover terrain materials whose witnessed numeric layers occur in another order.

Run: python contrib/terrain_layer_permutations.py --game BLACKOP7 --out logs/terrain_order.txt
Then: confirm_list logs/terrain_order.txt --game BLACKOP7 --script contrib/terrain_layer_permutations.py
Reads source-verified modern material names, verified community findings, and the
selected canonical snapshot. Writes candidate names to stdout or --out, and a
compact measurement to stderr. It never writes findings or changes exclusions.
Reusable for modern captures after genuinely new terrain combinations are found.

Every candidate retains one target-held material's directory and complete two-
to-four-layer token multiset, including n/dn qualifiers. Only order changes; no
numeric identities are invented or crossed between unrelated materials. This
reaches orders missed by top-token grids and triple insertion. A BO7 probe on
2026-10-09 measured 376,255 novel candidates, 14,155 known-order witness rebuilds,
and 129 preliminary unclaimed material matches; normal confirmation is required.
Spent when all permutations of the current target-held token multisets are tested.
"""
import argparse
from collections import Counter
from itertools import permutations
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent
while ROOT != ROOT.parent and not (ROOT / 'scripts/snapshot.py').is_file():
    ROOT = ROOT.parent
if not (ROOT / 'scripts/snapshot.py').is_file():
    raise SystemExit('Run from a solver checkout')
sys.path.insert(0, str(ROOT / 'scripts'))
import snapshot

BLEND = re.compile(r'^([^/]+)/\*((?:\d+d?n_){1,3}\d+d?n)$')


def corpus(game):
    """The shared reader restores CSV display paths only after source-key proof."""
    names = set(snapshot.table_names('fnv1a_xmaterials_v2'))
    for top in ['all_names', 'submissions', 'findings']:
        for path in (ROOT / top).rglob('material*.txt'):
            with path.open(encoding='utf-8') as stream:
                for row in stream:
                    raw, sep, name = row.strip().partition(',')
                    if not sep or BLEND.fullmatch(name) is None:
                        continue
                    try:
                        key = int(raw, 16) & snapshot.ID_MASK
                    except ValueError:
                        continue
                    if snapshot.fnv1a(name, game, 'material') & snapshot.ID_MASK == key:
                        names.add(name)
    return names


def generate(names, held, game):
    groups = set()
    controls = set()
    target_seeds = Counter()
    for name in names:
        match = BLEND.fullmatch(name)
        if match is None or snapshot.fnv1a(name, game, 'material') & snapshot.ID_MASK not in held:
            continue
        directory, text = match.groups()
        parts = tuple(text.split('_'))
        groups.add((directory, tuple(sorted(parts))))
        target_seeds[directory] += 1
    candidates = set()
    for directory, parts in groups:
        for reordered in set(permutations(parts)):
            name = directory + '/*' + '_'.join(reordered)
            if name in names:
                controls.add(name)
            else:
                candidates.add(name)
    report = {'game': game, 'kind': 'material', 'verified_material_names': len(names),
              'target_seeds_by_directory': dict(sorted(target_seeds.items())),
              'unique_layer_multisets': len(groups), 'known_orders_rebuilt': len(controls),
              'candidate_names': len(candidates)}
    return candidates, report


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--game', required=True, choices=sorted(snapshot.MODERN))
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    shot = snapshot.read(ROOT / 'snapshots' / (args.game.lower() + '.ids'))
    if shot.game != args.game:
        raise SystemExit('Selected capture has the wrong game tag')
    names = corpus(args.game)
    candidates, report = generate(names, set(shot.by_pool()['material']), args.game)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        with args.out.open('w', encoding='utf-8', newline='\n') as stream:
            for name in sorted(candidates):
                stream.write('0,' + name + '\n')
        report['output'] = str(args.out)
    else:
        for name in sorted(candidates):
            print('0,' + name)
    print(json.dumps(report, sort_keys=True), file=sys.stderr, flush=True)


if __name__ == '__main__':
    main()
