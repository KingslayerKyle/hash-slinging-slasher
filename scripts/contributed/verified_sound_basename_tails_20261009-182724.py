"""Build a modern sound plan replacing basename endings before the encoding tail.

Run: python contrib/verified_sound_basename_tails.py --game BLACKOP7 --width 4
With config.toml targeting sound_asset, size the printed plan using
confirm_plan <printed plan> --game BLACKOP7 --size.

Reads source-verified modern sound tables, verified merged/local sound names, and
the target capture. Writes a plan and its lists under contrib/verified_sound_basename_tails.
Unlike whole-filename tails, this changes the basename before its original codec,
quality, rate and language. Cuts must lie strictly inside an alphanumeric token;
underscore-boundary cuts belong to the existing sound segment method. Prefixes
come from verified modern names; replacement endings occur in target-held sounds.
No character alphabet is enumerated. Spent by these exact prefixes and endings.
All findings require normal sound_asset confirmation and submission verification.
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
if not (ROOT / 'scripts/snapshot.py').is_file():
    raise SystemExit('Cannot find the repository')
sys.path.insert(0, str(ROOT / 'scripts'))
import snapshot

FORMAT = re.compile(r'(?P<stem>.+)(?P<tail>\.[a-z]{1,4}\d*\.\d+\.\d+\.[a-z_]+)$')


def corpus(game):
    names = set(snapshot.table_names('fnv1a_xsounds_v2'))
    for top in ['all_names', 'submissions', 'findings']:
        for path in (ROOT / top).rglob('sound_asset*.txt'):
            for row in path.read_text(encoding='utf-8').splitlines():
                raw, sep, name = row.partition(',')
                if not sep or not name:
                    continue
                try:
                    key = int(raw, 16) & snapshot.ID_MASK
                except ValueError:
                    continue
                if snapshot.fnv1a(name, game, 'sound_asset') & snapshot.ID_MASK == key:
                    names.add(name.strip().lower())
    return {name for name in names if name.isascii() and '\n' not in name and '\r' not in name}


def split(name, width):
    match = FORMAT.fullmatch(name)
    if not match:
        return None
    stem, tail = match['stem'], match['tail']
    start = max(stem.rfind('/'), stem.rfind(chr(92)), stem.rfind('.')) + 1
    cut = len(stem) - width
    # Retain at least four basename characters and avoid cuts touching separators.
    if cut - start < 4 or not stem[cut - 1].isalnum() or not stem[cut].isalnum():
        return None
    return stem[:cut], stem[cut:] + tail, stem[cut:]


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--game', required=True, choices=sorted(snapshot.MODERN))
    parser.add_argument('--width', type=int, default=4, choices=range(2, 6))
    args = parser.parse_args()
    shot = snapshot.read(ROOT / 'snapshots' / (args.game.lower() + '.ids'))
    assert shot.game == args.game
    held = set(shot.by_pool()['sound_asset'])
    names = corpus(args.game)
    prefixes, endings, sibling_tails = set(), set(), defaultdict(set)
    target_controls = 0
    for name in names:
        parts = split(name, args.width)
        if parts is None:
            continue
        prefix, ending, basename_tail = parts
        prefixes.add(prefix)
        if snapshot.fnv1a(name, args.game, 'sound_asset') & snapshot.ID_MASK in held:
            endings.add(ending)
            sibling_tails[prefix].add(basename_tail)
            target_controls += 1
    if not prefixes or not endings:
        raise SystemExit('No source-verified target vocabulary for this cut')
    out = ROOT / 'contrib/verified_sound_basename_tails' / args.game.lower()
    out.mkdir(parents=True, exist_ok=True)
    stem_path, end_path = out / f'k{args.width}.stems.txt', out / f'k{args.width}.ends.txt'
    for path, values in [(stem_path, prefixes), (end_path, endings)]:
        path.write_text(''.join(name + '\n' for name in sorted(values)), encoding='utf-8')
    plan_path = out / f'k{args.width}.plan.txt'
    plan_path.write_text(
        f'label: {args.game} sound basename endings inside tokens, width {args.width}\n'
        f'describe: source-verified modern sound prefixes cut {args.width} basename characters before the encoding tail, strictly inside alphanumeric tokens, crossed only with target-held endings including original encoding; excludes underscore-boundary cuts and enumerates no alphabet\n'
        f'game: {args.game}\n'
        f'stem: @{stem_path.relative_to(ROOT).as_posix()}\n'
        f'end: @{end_path.relative_to(ROOT).as_posix()}\n'
        'bare: yes\nfold: yes\n', encoding='utf-8')
    report = {'game': args.game, 'width': args.width, 'verified_sound_seeds': len(names),
              'prefixes': len(prefixes), 'target_observed_endings': len(endings),
              'target_positive_controls': target_controls,
              'target_prefixes_with_multiple_basename_endings': sum(len(tails) > 1 for tails in sibling_tails.values()),
              'candidate_product': len(prefixes) * len(endings),
              'engine_candidates_including_bare': len(prefixes) * (len(endings) + 1),
              'plan': plan_path.relative_to(ROOT).as_posix()}
    (out / f'k{args.width}.measurement.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
