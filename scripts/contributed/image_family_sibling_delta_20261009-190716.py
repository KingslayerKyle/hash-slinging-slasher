"""Emit family-supported sibling endings from supplied verified modern images.

Only the supplied image names provide candidate cores. The conventions come
from other verified target images: same first two stem tokens, same one- or
two-token suffix depth, and at least three distinct sibling-bearing cores per
ending. The source ending must be supported too. No numeric range or byte
alphabet is invented. This is a delta application of image sibling channels.

The 2026-10-09 BO7 probe, further restricted to 232 cores absent from the frozen
pre-CSV corpus, measured 27,349 candidates, 319 known controls and four fresh
image hashes. This reusable form retains all supported cores in the explicit
seed file; normal confirmation excludes prior work.

  python contrib/image_family_sibling_delta.py --game BLACKOP7 \
      --seed-file new-image-findings.txt --output logs/image-siblings.txt
  confirm_list logs/image-siblings.txt --game BLACKOP7 --script <this script> \
      --label "verified image vocabulary delta to family sibling endings"

Select image in the confirmer. Spent by the supplied cores and family endings.
"""
import argparse
from collections import defaultdict
import importlib.util
import json
from pathlib import Path
import sys

ROOT = next((p for p in [Path.cwd(), *Path(__file__).resolve().parents]
             if (p / 'scripts/snapshot.py').is_file()), None)
if ROOT is None:
    raise SystemExit('Run inside a solver checkout')
sys.path.insert(0, str(ROOT / 'scripts'))
import snapshot


def helper():
    path = ROOT / 'scripts/contributed/verified_image_channel_byte_parallel_20261009-132951.py'
    spec = importlib.util.spec_from_file_location('_reviewed_image_channels', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_seeds(paths, held, game):
    seeds = set()
    for path in paths:
        for row in path.read_text(encoding='utf-8').splitlines():
            name = row.strip()
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
            key = snapshot.fnv1a(name, game, 'image') & snapshot.ID_MASK
            if stored_key is not None and key != stored_key:
                raise ValueError('Seed spelling does not reproduce the supplied stored key')
            if key not in held:
                raise ValueError('Seed spelling does not reproduce a target image ID')
            seeds.add(name)
    return seeds


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--game', choices=sorted(snapshot.MODERN), required=True)
    parser.add_argument('--seed-file', type=Path, action='append', required=True)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--size', action='store_true')
    args = parser.parse_args()
    capture = snapshot.read(ROOT / 'snapshots' / (args.game.lower() + '.ids'))
    if capture.game != args.game:
        raise ValueError('Capture game does not match the requested game')
    held = set(capture.by_pool()['image'])
    seeds = load_seeds(args.seed_file, held, args.game)
    channel = helper()
    siblings = defaultdict(set)
    for name in channel.corpus('image', args.game) - seeds:
        if snapshot.fnv1a(name, args.game, 'image') & snapshot.ID_MASK not in held:
            continue
        for depth, stem, tail in channel.cuts(name):
            siblings[depth, stem].add(tail)
    witnesses = defaultdict(set)
    for (depth, stem), tails in siblings.items():
        if len(tails) < 2:
            continue
        family = '_'.join(stem.split('_')[:2])
        for tail in tails:
            witnesses[depth, family, tail].add(stem)
    rules = defaultdict(set)
    for (depth, family, tail), cores in witnesses.items():
        if len(cores) >= 3:
            rules[depth, family].add(tail)
    candidates, cores = set(), set()
    for name in seeds:
        for depth, stem, tail in channel.cuts(name):
            endings = rules.get((depth, '_'.join(stem.split('_')[:2])), set())
            if tail not in endings:
                continue
            cores.add((depth, stem))
            candidates.update(stem + end for end in endings)
    print(json.dumps({'game': args.game, 'verified_image_seeds': len(seeds),
                      'supported_family_depth_groups': len(rules),
                      'supported_family_endings': sum(map(len, rules.values())),
                      'seed_defined_image_cores': len(cores),
                      'unique_candidates': len(candidates)}), file=sys.stderr)
    if args.size:
        return
    output = args.output.open('w', encoding='utf-8', newline='\n') if args.output else sys.stdout
    try:
        for name in sorted(candidates):
            output.write('0,' + name + '\n')
    finally:
        if args.output:
            output.close()


if __name__ == '__main__':
    main()
