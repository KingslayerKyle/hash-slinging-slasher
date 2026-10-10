"""Vary one witnessed image-stem byte while retaining that image's own suffix.

Run: python contrib/frozen_image_suffix_byte.py --game BLACKOP7 --out logs/image_suffix_byte.txt
Then: confirm_list logs/image_suffix_byte.txt --game BLACKOP7 --script contrib/frozen_image_suffix_byte.py
Reads verified modern images, verified community names, and one canonical game
capture. Writes candidates to stdout or --out and measurements to stderr; never
writes findings or changes exclusions. Reusable after new prefix/suffix frames
or suffix-specific byte alphabets are discovered.

This is a bounded, in-place variant of the reviewed byte-before-channel method.
A suffix must have at least three target-held sibling-core witnesses, and must
be longer than three characters so final-three-byte sweeps cannot reach the
changed stem byte. Each candidate keeps a source image's suffix and prefix up
to the final stem byte. Replacement bytes are observed in that same position
with that same suffix on the target capture. It does not cross every prefix
with every suffix. All candidates still require ordinary confirmation.

A BO7 reconnaissance pass on 2026-10-09 generated 1,715,197 unseen candidates
with 104,853 known frame/byte controls and 47 preliminary unclaimed image hits.
The broader inverse method's BO7 profile required 4.07 billion reverse queries;
this subset took about ten seconds to generate and measure on the same corpus.
Spent when the current source frames and witnessed alphabets are exhausted.
"""
import argparse
from collections import defaultdict
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
    """Reuse the library's source verification and witnessed suffix definition."""
    path = ROOT / 'scripts/contributed/verified_image_channel_byte_parallel_20261009-132951.py'
    spec = importlib.util.spec_from_file_location('_frozen_image_byte_companion', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def generate(names, held, game, helper):
    tails = helper.target_tails(names, held, game)
    alphabets = defaultdict(set)
    for name in names:
        if snapshot.fnv1a(name, game, 'image') & snapshot.ID_MASK not in held:
            continue
        for _, stem, tail in helper.cuts(name):
            if tail in tails and len(tail) > 3:
                alphabets[tail].add(stem[-1])
    frames = {(stem[:-1], tail) for name in names for _, stem, tail in helper.cuts(name)
              if tail in alphabets}
    candidates = set()
    controls = 0
    for prefix, tail in frames:
        for byte in alphabets[tail]:
            candidate = prefix + byte + tail
            if candidate in names:
                controls += 1
            else:
                candidates.add(candidate)
    return candidates, {'game': game, 'kind': 'image', 'verified_names': len(names),
                        'observed_suffixes': len(alphabets), 'source_frames': len(frames),
                        'known_frame_byte_controls': controls,
                        'candidate_names': len(candidates)}


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--game', required=True, choices=sorted(snapshot.MODERN))
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    shot = snapshot.read(ROOT / 'snapshots' / (args.game.lower() + '.ids'))
    if shot.game != args.game:
        raise SystemExit('Selected capture has the wrong game tag')
    helper = reviewed_companion()
    names = helper.corpus('image', args.game)
    candidates, report = generate(names, set(shot.by_pool()['image']), args.game, helper)
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
