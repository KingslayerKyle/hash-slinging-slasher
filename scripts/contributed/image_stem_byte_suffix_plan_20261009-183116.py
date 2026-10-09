"""Build a compiled image-prefix x witnessed stem-byte x witnessed-suffix plan.

Run: python contrib/image_stem_byte_suffix_plan.py --game BLACKOP7
Size: confirm_plan contrib/image_stem_byte_suffix_plan/blackop7/images.plan.txt --game BLACKOP7 --size
Run the generated plan with only the image pool selected in config.toml. The
plan format cannot select pools; its game line checks the explicit --game tag.
Reads verified modern image names, verified community images, and the target
canonical capture through the reviewed byte-before-channel implementation.
Writes three compact plan inputs, a plan, and measurement.json under contrib.
Reusable after new verified image prefixes or suffix witnesses appear.

Suffixes follow the reviewed evidence rule: one or two complete underscore
tokens, witnessed by at least three distinct target-held cores which each have
sibling suffixes. A beginning is a verified image core minus its final byte.
Replacement bytes are only those witnessed immediately before these suffixes
on the selected target. No sound aliases, models, or other asset types seed it.

Unlike frozen_image_suffix_byte.py, this also crosses prefixes with other
witnessed suffixes. This is the complete compact three-list product, not a
Python-emitted candidate expansion. It has the same prefix/suffix reach as the
reviewed inverse method but restricts replacement bytes to a target-witnessed
alphabet. The engine also tests each repaired core without a suffix.

BO7 measurement on 2026-10-09: 63,229 prefixes x 36 bytes x 5,303 suffixes,
12,073,198,176 candidates including suffix-free cores; about 2.16 MB of input.
2,197,863 expanded cores were absent from conservatively regenerated current
image all-boundary stems, and 3,164 suffixes absent from all saved old image
ending lists. run_best is expected to choose forward hashing: its sorting cost
estimate makes peeling more expensive at this product size. No search result
is implied by these structural measurements. Spent at its exact three lists.
"""
import argparse
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
    spec = importlib.util.spec_from_file_location('_image_byte_plan_companion', path)
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
    beginnings = helper.prefixes(names, suffixes)
    alphabet = set()
    for name in names:
        if snapshot.fnv1a(name, args.game, 'image') & snapshot.ID_MASK not in held:
            continue
        for _, stem, tail in helper.cuts(name):
            if tail in suffixes:
                alphabet.add(stem[-1])
    if not beginnings or not alphabet or not suffixes:
        raise SystemExit('No source-verified target image vocabulary')
    # corpus() restricts source names to ASCII and cuts() requires alphanumeric
    # final stem bytes. Assert the shape instead of silently widening it.
    if not all(len(byte) == 1 and byte.isascii() and byte.isalnum() for byte in alphabet):
        raise SystemExit('Unexpected replacement-byte alphabet')
    out = ROOT / 'contrib/image_stem_byte_suffix_plan' / args.game.lower()
    out.mkdir(parents=True, exist_ok=True)
    files = {}
    for role, values in [('begin', beginnings), ('stem', alphabet), ('end', suffixes)]:
        path = out / (role + '.txt')
        path.write_text(''.join('0,' + value + '\n' for value in sorted(values)), encoding='utf-8')
        files[role] = path.relative_to(ROOT).as_posix()
    plan = out / 'images.plan.txt'
    plan.write_text(
        f'label: {args.game} verified image stem bytes crossed with witnessed suffixes\n'
        f'describe: verified image cores minus their final byte x {len(alphabet)} stem bytes witnessed on this capture x {len(suffixes)} suffixes with three target-held sibling-core witnesses; compiled extension beyond suffix-preserving edits; image pool only; generator contrib/image_stem_byte_suffix_plan.py\n'
        f'game: {args.game}\nbegin: @{files["begin"]}\nstem: @{files["stem"]}\n'
        f'end: @{files["end"]}\nbare: no\nfold: yes\n', encoding='utf-8')
    report = {'game': args.game, 'kind': 'image', 'verified_image_names': len(names),
              'beginnings': len(beginnings), 'replacement_bytes': ''.join(sorted(alphabet)),
              'stems': len(alphabet), 'endings': len(suffixes),
              'candidates_including_unsuffixed_cores': len(beginnings) * len(alphabet) * (len(suffixes) + 1),
              'input_bytes': sum((ROOT / path).stat().st_size for path in files.values()),
              'plan': plan.relative_to(ROOT).as_posix(),
              'required_pool_selection': ['image']}
    (out / 'measurement.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, sort_keys=True))


if __name__ == '__main__':
    main()
