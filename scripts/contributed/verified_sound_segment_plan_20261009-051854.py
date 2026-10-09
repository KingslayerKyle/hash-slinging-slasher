"""Build sound-file segment plans using source-verified original spellings.

Encoding tails and segment endings are measured on the selected target capture.
Retains periods or slashes exactly as hashed; reads no game or process data.
Generated plans belong in an explicit sound_asset-only confirmation run.
"""
import argparse
from collections import Counter
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent
while ROOT != ROOT.parent and not (ROOT / 'scripts/snapshot.py').is_file():
    ROOT = ROOT.parent
if not (ROOT / 'scripts/snapshot.py').is_file(): ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / 'scripts'))
import snapshot

FORMAT = re.compile(r'(?P<stem>.+)(?P<tail>\.[a-z]{1,4}\d*\.\d+\.\d+\.[a-z_]+)$')

def corpus():
    names = set(snapshot.table_names('fnv1a_xsounds_v2'))
    for top in ['all_names', 'submissions', 'findings']:
        for path in (ROOT / top).rglob('sound_asset*.txt'):
            for row in path.read_text(encoding='utf-8').splitlines():
                raw, sep, name = row.partition(',')
                if not sep or not name: continue
                try: key = int(raw, 16) & snapshot.ID_MASK
                except ValueError: continue
                if snapshot.fnv1a(name, 'YAMYAMOK', 'sound_asset') & snapshot.ID_MASK == key:
                    names.add(name.lower())
    return sorted(name for name in names if '\n' not in name and '\r' not in name)

def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--game', required=True, choices=sorted(snapshot.MODERN))
    parser.add_argument('--ends', type=int, default=4000)
    parser.add_argument('--heads', action='store_true')
    args = parser.parse_args()
    if not 1 <= args.ends <= 12000: parser.error('--ends must be between 1 and 12000')
    shot = snapshot.read(ROOT / 'snapshots' / (args.game.lower() + '.ids'))
    assert shot.game == args.game
    held = set(shot.by_pool()['sound_asset'])
    fragments, measured = set(), Counter()
    names = corpus()
    target_names = 0
    for name in names:
        match = FORMAT.fullmatch(name)
        if match is None: continue
        stem, tail = match['stem'], match['tail']
        at = max(stem.rfind('/'), stem.rfind(chr(92)), stem.rfind('.')) + 1
        directory, parts = stem[:at], stem[at:].split('_')
        on_target = snapshot.fnv1a(name, args.game, 'sound_asset') & snapshot.ID_MASK in held
        target_names += on_target
        if args.heads:
            for count in range(1, min(2, len(parts) - 1) + 1):
                beginning = directory + '_'.join(parts[:count])
                if on_target: measured[beginning] += 1
                fragments.add('_' + '_'.join(parts[count:]) + tail)
        else:
            for count in range(1, len(parts)):
                beginning = directory + '_'.join(parts[:count])
                if len(beginning) >= 4: fragments.add(beginning)
            if on_target:
                for count in range(1, min(3, len(parts) - 1) + 1):
                    measured['_' + '_'.join(parts[-count:]) + tail] += 1
    selected = [n for n, _ in measured.most_common(args.ends)]
    assert selected and fragments, 'No target-held sound-file vocabulary'
    out = ROOT / 'contrib/verified_sound_segments' / args.game.lower()
    out.mkdir(parents=True, exist_ok=True)
    mode = 'heads' if args.heads else 'tails'
    paths = {}
    for role, values in [('stem', selected if args.heads else sorted(fragments)),
                         ('end', sorted(fragments) if args.heads else selected)]:
        path = out / (mode + '.' + role + '.txt')
        path.write_text(''.join('0,' + v + '\n' for v in values), encoding='utf-8')
        paths[role] = path.relative_to(ROOT).as_posix()
    plan = out / (mode + '.plan.txt')
    plan.write_text(f'label: {args.game} source-verified sound-file {mode}\n'
                    f'describe: verified modern sound-file segments with {len(selected)} target-held {mode} conventions, preserving original directory separators and encoding tails\n'
                    f'game: {args.game}\nstem: @{paths["stem"]}\nend: @{paths["end"]}\n'
                    'bare: yes\nfold: yes\n', encoding='utf-8')
    print(f'{args.game}: {len(names)} verified sounds, {target_names} on target; '
          f'{len(fragments)} fragments, {len(selected)} measured {mode}; '
          f'{len(fragments)*len(selected)} candidates; {plan.relative_to(ROOT).as_posix()}')

if __name__ == '__main__': main()
