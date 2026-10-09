"""Emit witnessed image wrappers over newly supplied modern material vocabulary.

Each input spelling must hash to a material in the selected capture. Its base
is retained only when absent from the prior verified material corpus (the input
spellings themselves are removed before that comparison). An image wrapper is
learned from target-held material/image pairs sharing an exact base, with zero,
one or two image tokens before and after it. At least three distinct prior
material bases must witness each complete prefix/suffix pair. The pair stays
correlated; independent prefix/suffix multiplication is deliberately avoided.

This is a delta application of the established material/image core seam. The
2026-10-09 external CSV supplied 3,391 new BO7 material bases; a frozen prior
corpus measured 196 wrappers, 18,525 pair controls, 664,636 candidates, 169 known
target controls and 692 unclaimed image hashes. CSV hash/key60/func columns were
never trusted. Inputs and conventions are revalidated against the capture here.

Example (material seed file may be raw names or hash,name findings):
  python contrib/verified_material_image_delta.py --game BLACKOP7 \
      --seed-file findings/blackop7/<run>/material.txt --output logs/images.txt
  confirm_list logs/images.txt --game BLACKOP7 --script <this script> \
      --label "verified material vocabulary delta to witnessed image wrappers"

Select the image pool in the confirmer. This script only emits candidates.
Spent by: the exact supplied material bases and measured wrapper pairs; fresh
material vocabulary or a genuinely new wrapper relation can reopen the seam.
"""
import argparse
from collections import defaultdict
import json
from pathlib import Path
import sys


ROOT = next((p for p in [Path.cwd(), *Path(__file__).resolve().parents]
             if (p / 'scripts/snapshot.py').is_file()), None)
if ROOT is None:
    raise SystemExit('Run inside a solver checkout')
sys.path.insert(0, str(ROOT / 'scripts'))
import snapshot


def corpus(kind, game):
    table = {'material': 'fnv1a_xmaterials_v2', 'image': 'fnv1a_ximages_v2'}[kind]
    names = set(snapshot.table_names(table))
    for top in ['all_names', 'submissions', 'findings']:
        for path in (ROOT / top).rglob(kind + '*.txt'):
            for row in path.read_text(encoding='utf-8').splitlines():
                raw, sep, name = row.partition(',')
                if not sep or not name:
                    continue
                try:
                    key = int(raw, 16) & snapshot.ID_MASK
                except ValueError:
                    continue
                if snapshot.fnv1a(name, game, kind) & snapshot.ID_MASK == key:
                    names.add(name.strip().lower())
    return {n for n in names if n and n.isascii() and n == n.strip()
            and '\n' not in n and '\r' not in n}


def load_seeds(paths, material_ids, game):
    seeds = set()
    for path in paths:
        for line in path.read_text(encoding='utf-8').splitlines():
            name = line.strip()
            stored_key = None
            raw, sep, rest = name.partition(',')
            if sep:
                try:
                    stored_key = int(raw, 16) & snapshot.ID_MASK
                except ValueError:
                    pass
                else:
                    name = rest.strip()
            name = name.lower()
            if not name:
                continue
            if not name.isascii() or '\n' in name or '\r' in name:
                raise ValueError('Seed files must contain one ASCII name per row')
            key = snapshot.fnv1a(name, game, 'material') & snapshot.ID_MASK
            if stored_key is not None and key != stored_key:
                raise ValueError('A seed spelling does not reproduce its supplied stored key')
            if key not in material_ids:
                raise ValueError('A seed spelling does not reproduce a target material ID')
            seeds.add(name)
    return seeds


def measure(game, paths):
    capture = snapshot.read(str(ROOT / 'snapshots' / (game.lower() + '.ids')))
    if capture.game != game:
        raise ValueError('Capture game does not match the requested game')
    pools = capture.by_pool()
    material_ids, image_ids = set(pools['material']), set(pools['image'])
    seeds = load_seeds(paths, material_ids, game)
    prior_materials = corpus('material', game) - seeds
    prior_bases = {n.rsplit('/', 1)[-1] for n in prior_materials if '*' not in n}
    target_bases = {n.rsplit('/', 1)[-1] for n in prior_materials if '*' not in n
                    and snapshot.fnv1a(n, game, 'material') & snapshot.ID_MASK in material_ids}
    new_bases = {n.rsplit('/', 1)[-1] for n in seeds if '*' not in n} - prior_bases
    witnesses = defaultdict(set)
    for name in corpus('image', game):
        if any(c in name for c in '&~*/'):
            continue
        if snapshot.fnv1a(name, game, 'image') & snapshot.ID_MASK not in image_ids:
            continue
        parts = name.split('_')
        for left in (0, 1, 2):
            for right in (0, 1, 2):
                if len(parts) - left - right < 2:
                    continue
                core = '_'.join(parts[left:len(parts) - right if right else None])
                if core not in target_bases:
                    continue
                prefix = '_'.join(parts[:left]) + ('_' if left else '')
                suffix = ('_' if right else '') + '_'.join(parts[-right:] if right else [])
                witnesses[prefix, suffix].add(core)
    rules = {r: cores for r, cores in witnesses.items() if len(cores) >= 3}
    report = {'game': game, 'verified_material_seed_names': len(seeds),
              'new_material_bases': len(new_bases), 'witnessed_wrapper_rules': len(rules),
              'target_pair_controls': sum(map(len, rules.values())),
              'candidate_product': len(new_bases) * len(rules)}
    return sorted(new_bases), sorted(rules), report


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--game', required=True)
    parser.add_argument('--seed-file', type=Path, action='append', required=True)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--size', action='store_true')
    args = parser.parse_args()
    game = args.game.upper()
    if game not in snapshot.MODERN:
        parser.error('This method uses modern ordinary-asset hash policies')
    bases, rules, report = measure(game, args.seed_file)
    print(json.dumps(report), file=sys.stderr)
    if args.size:
        return
    output = args.output.open('w', encoding='utf-8', newline='\n') if args.output else sys.stdout
    try:
        for prefix, suffix in rules:
            for base in bases:
                output.write('0,' + prefix + base + suffix + '\n')
    finally:
        if args.output:
            output.close()


if __name__ == '__main__':
    main()
