"""Restore witnessed material directories from a fresh modern image vocabulary.

Learn complete (image prefix, image suffix, material directory) triples from
verified target-held pairs sharing a core. Each triple needs three distinct
material cores. Only zero, one or two image tokens may be removed at each end;
the material directory is retained exactly, including leading # markers.
Apply matching triples only to supplied, target-verified image seeds, and keep
only cores absent from the prior verified material corpus.

For a simultaneous image/material harvest, --new-material-file excludes those
new material spellings from the baseline and convention evidence, so confirming
the harvest before this derivation does not erase its delta. It is vocabulary
provenance only; the confirmer still excludes every known or claimed hash.

2026-10-09 BO7 frozen-corpus measurement: 2,314 supplied images, 335 witnessed
triples, 20,996 pair controls, 3,777 new cores, 16,107 unique candidates, 149 known
controls and 57 unclaimed material hashes. External CSV hash/key60/func fields
were ignored; every supplied spelling was independently rehashed to its pool.

Example:
  python contrib/verified_image_material_delta.py --game BLACKOP7 \
    --seed-file new-images.txt --new-material-file new-materials.txt \
    --output logs/material-delta.txt
  confirm_list logs/material-delta.txt --game BLACKOP7 --script <this script> \
    --label "verified image vocabulary delta to witnessed material directories"

Select material in the confirmer. No confirmations or settings changes occur
here. Spent by the supplied image cores and witnessed triples; do not repeat
with the same vocabulary merely because the known tables grew.
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


def load_seeds(paths, held, game, kind):
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
            key = snapshot.fnv1a(name, game, kind) & snapshot.ID_MASK
            if stored_key is not None and key != stored_key:
                raise ValueError('A seed spelling does not reproduce its supplied stored key')
            if key not in held:
                raise ValueError('A seed spelling does not reproduce its selected target pool')
            seeds.add(name)
    return seeds


def measure(game, image_paths, material_paths):
    capture = snapshot.read(str(ROOT / 'snapshots' / (game.lower() + '.ids')))
    if capture.game != game:
        raise ValueError('Capture game does not match the requested game')
    pools = capture.by_pool()
    material_ids, image_ids = set(pools['material']), set(pools['image'])
    images = load_seeds(image_paths, image_ids, game, 'image')
    new_materials = load_seeds(material_paths, material_ids, game, 'material')
    prior_materials = corpus('material', game) - new_materials
    prior_bases = {n.rsplit('/', 1)[-1] for n in prior_materials if '*' not in n}
    base_dirs = defaultdict(set)
    for name in prior_materials:
        if '*' in name or snapshot.fnv1a(name, game, 'material') & snapshot.ID_MASK not in material_ids:
            continue
        directory, slash, core = name.rpartition('/')
        base_dirs[core].add(directory + slash)
    witnesses = defaultdict(set)
    for name in corpus('image', game) - images:
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
                if core not in base_dirs:
                    continue
                prefix = '_'.join(parts[:left]) + ('_' if left else '')
                suffix = ('_' if right else '') + '_'.join(parts[-right:] if right else [])
                for directory in base_dirs[core]:
                    witnesses[prefix, suffix, directory].add(core)
    rules = {rule: cores for rule, cores in witnesses.items() if len(cores) >= 3}
    candidates, cores = set(), set()
    for prefix, suffix, directory in rules:
        for name in images:
            if not name.startswith(prefix) or not name.endswith(suffix):
                continue
            core = name[len(prefix):len(name) - len(suffix) if suffix else None]
            if len(core.split('_')) < 2 or core in prior_bases:
                continue
            cores.add(core)
            candidates.add(directory + core)
    report = {'game': game, 'verified_image_seed_names': len(images),
              'new_material_names_excluded_from_baseline': len(new_materials),
              'witnessed_triples': len(rules), 'target_pair_controls': sum(map(len, rules.values())),
              'new_core_vocabulary': len(cores), 'unique_candidates': len(candidates)}
    return sorted(candidates), report


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--game', required=True)
    parser.add_argument('--seed-file', type=Path, action='append', required=True)
    parser.add_argument('--new-material-file', type=Path, action='append', default=[])
    parser.add_argument('--output', type=Path)
    parser.add_argument('--size', action='store_true')
    args = parser.parse_args()
    game = args.game.upper()
    if game not in snapshot.MODERN:
        parser.error('This method uses modern ordinary-asset hash policies')
    candidates, report = measure(game, args.seed_file, args.new_material_file)
    print(json.dumps(report), file=sys.stderr)
    if args.size:
        return
    output = args.output.open('w', encoding='utf-8', newline='\n') if args.output else sys.stdout
    try:
        for name in candidates:
            output.write('0,' + name + '\n')
    finally:
        if args.output:
            output.close()


if __name__ == '__main__':
    main()
