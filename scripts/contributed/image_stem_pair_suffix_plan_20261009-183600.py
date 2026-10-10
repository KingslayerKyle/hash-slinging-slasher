"""Build a compiled image-prefix x witnessed complete byte-pair x suffix plan.

Run: python contrib/image_stem_pair_suffix_plan.py --game BLACKOP7
Size: confirm_plan contrib/image_stem_pair_suffix_plan/blackop7/images.plan.txt --game BLACKOP7 --size
Run with only the image pool selected in config.toml; plans cannot select pools.
Reads source-verified modern images, verified community images, and the canonical
target capture through the reviewed byte-before-channel helper. Writes three
compact lists, a plan, and measurement.json under contrib. No findings are written.
Reusable after genuinely new verified image frames or witnessed pairs appear.

Suffix evidence is unchanged from the reviewed one-byte method: one or two
underscore tokens with at least three target-held sibling-core witnesses.
Beginnings are verified source image cores with their final TWO bytes removed.
The middle list contains only complete two-byte endings actually witnessed on
target-held image cores with these suffixes. It never independently crosses
character alphabets. A pair may include an underscore as its first byte; that
whole pair must itself have a real target-held witness. No aliases or models
seed the lists. Candidate strings require ordinary image-only confirmation.

BO7 reconnaissance on 2026-10-09 measured 61,925 prefixes, 677 complete pairs,
and 5,306 suffixes: 222,486,555,075 candidates including suffix-free cores.
Only 3.630 percent overlap the one-byte product reconstructed from the same
current corpus. This comparison conservatively includes its newly acquired
prefixes and suffixes, not just the smaller earlier executed lists. The engine
chooses its direction; no Python candidate cross product is emitted. Spent at
these exact lists. The generator reports structure, never discovered names.
"""
import argparse
from collections import Counter
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
while ROOT != ROOT.parent and not (ROOT / 'scripts/snapshot.py').is_file():
    ROOT = ROOT.parent
if not (ROOT / 'scripts/snapshot.py').is_file():
    raise SystemExit('Run from a solver checkout')
sys.path.insert(0, str(ROOT / 'scripts'))
import snapshot


def reviewed_companion():
    path = ROOT / 'scripts/contributed/verified_image_channel_byte_parallel_20261009-132951.py'
    spec = importlib.util.spec_from_file_location('_image_pair_plan_companion', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--game', required=True, choices=sorted(snapshot.MODERN))
    args = parser.parse_args()
    shot = snapshot.read(ROOT / 'snapshots' / (args.game.lower() + '.ids'))
    if shot.game != args.game:
        raise SystemExit('Selected capture has the wrong game tag')
    held = set(shot.by_pool()['image'])
    helper = reviewed_companion()
    names = helper.corpus('image', args.game)
    suffixes = helper.target_tails(names, held, args.game)
    width1_prefixes = helper.prefixes(names, suffixes)
    beginnings = {stem[:-2] for name in names for _, stem, tail in helper.cuts(name)
                  if tail in suffixes and len(stem) > 2}
    pairs = set()
    for name in names:
        if snapshot.fnv1a(name, args.game, 'image') & snapshot.ID_MASK not in held:
            continue
        for _, stem, tail in helper.cuts(name):
            if tail in suffixes and len(stem) > 2:
                pairs.add(stem[-2:])
    if not beginnings or not pairs or not suffixes:
        raise SystemExit('No source-verified target image vocabulary')
    if not all(len(pair) == 2 and pair.isascii() and pair[-1].isalnum() for pair in pairs):
        raise SystemExit('Unexpected complete-pair shape')
    first_counts = Counter(pair[0] for pair in pairs)
    overlapping_cores = sum(sum(prefix + first in width1_prefixes for prefix in beginnings) * count
                            for first, count in first_counts.items())
    out = ROOT / 'contrib/image_stem_pair_suffix_plan' / args.game.lower()
    out.mkdir(parents=True, exist_ok=True)
    files = {}
    for role, values in [('begin', beginnings), ('stem', pairs), ('end', suffixes)]:
        path = out / (role + '.txt')
        path.write_text(''.join('0,' + value + '\n' for value in sorted(values)), encoding='utf-8')
        files[role] = path.relative_to(ROOT).as_posix()
    plan = out / 'images.plan.txt'
    plan.write_text(
        f'label: {args.game} verified image complete stem pairs crossed with witnessed suffixes\n'
        f'describe: verified image cores minus final two bytes x {len(pairs)} complete two-byte endings actually witnessed on target image cores x {len(suffixes)} suffixes with three target-held sibling-core witnesses; no Cartesian character alphabets; image pool only; generator contrib/image_stem_pair_suffix_plan.py\n'
        f'game: {args.game}\nbegin: @{files["begin"]}\nstem: @{files["stem"]}\n'
        f'end: @{files["end"]}\nbare: no\nfold: yes\n', encoding='utf-8')
    candidates = len(beginnings) * len(pairs) * (len(suffixes) + 1)
    overlap = overlapping_cores * (len(suffixes) + 1)
    report = {'game': args.game, 'kind': 'image', 'verified_image_names': len(names),
              'beginnings': len(beginnings), 'complete_witnessed_pairs': len(pairs),
              'endings': len(suffixes), 'candidates_including_unsuffixed_cores': candidates,
              'overlap_with_current_width1_product': overlap,
              'new_beyond_current_width1_product': candidates - overlap,
              'overlap_percent': 100 * overlap / candidates,
              'input_bytes': sum((ROOT / path).stat().st_size for path in files.values()),
              'plan': plan.relative_to(ROOT).as_posix(), 'required_pool_selection': ['image']}
    (out / 'measurement.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, sort_keys=True))


if __name__ == '__main__':
    main()
