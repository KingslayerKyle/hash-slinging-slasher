"""Derive aliases and bounded take-number plans from verified sound-file names.

Source spellings come from the shared hash-verified database reader. Local rows
are rehashed before they become seeds. Original modern directory separators
and encoding tails are retained in file plans; every discovery still requires
normal confirm_list/confirm_plan and submission verification on the target.
"""
import argparse
from collections import Counter
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

MODERN = re.compile(r'(?P<stem>.+)\.[a-z]{1,4}\.\d+\.\d+\.[a-z_]+$')
LEGACY = re.compile(r'(?P<stem>.+)\.[a-z]{2}\d+\.pc\.[a-z_]+\.snd$')
TAKE = re.compile(r'(?P<base>.+_)(?P<number>\d{1,3})$')

def corpus(include_legacy):
    tables = ['fnv1a_xsounds_v2'] + (['fnv1a_xsounds'] if include_legacy else [])
    names = set(snapshot.table_names(*tables))
    for top in ['all_names', 'submissions', 'findings']:
        for path in (ROOT / top).rglob('sound_asset*.txt'):
            for line in path.read_text(encoding='utf-8').splitlines():
                raw, sep, name = line.partition(',')
                if not sep or not name:
                    continue
                try:
                    key = int(raw, 16) & snapshot.ID_MASK
                except ValueError:
                    continue
                if snapshot.fnv1a(name, 'YAMYAMOK', 'sound_asset') & snapshot.ID_MASK == key:
                    names.add(name.lower())
                elif include_legacy and any(value & snapshot.ID_MASK == key for value in
                    [snapshot.fnv1a(name), snapshot.fnv1a_nofold(name)]):
                    names.add(name.lower())
    return names

def rows(path, values):
    path.write_text(''.join('0,' + value + '\n' for value in sorted(values)), encoding='utf-8')

def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--game', required=True, choices=sorted(snapshot.MODERN))
    parser.add_argument('--mode', required=True, choices=['aliases', 'takes'])
    parser.add_argument('--max-take', type=int, default=30)
    args = parser.parse_args()
    if not 1 <= args.max_take <= 99:
        parser.error('--max-take must be between 1 and 99')
    shot = snapshot.read(ROOT / 'snapshots' / (args.game.lower() + '.ids'))
    assert shot.game == args.game
    held = set(shot.by_pool()['sound_asset'])
    names = corpus(args.mode == 'aliases')
    out = ROOT / 'contrib/verified_sound_variants' / args.game.lower()
    out.mkdir(parents=True, exist_ok=True)
    if args.mode == 'aliases':
        candidates = set()
        for name in names:
            match = MODERN.fullmatch(name) or LEGACY.fullmatch(name)
            if match is None:
                continue
            stem = match['stem'].replace(chr(92), '/')
            boundary = max(stem.rfind('/'), stem.rfind('.'))
            base = stem[boundary + 1:]
            variants = {base, re.sub(r'_\d+$', '', base), re.sub(r'_[a-z]$', '', base),
                        re.sub(r'_\d+_[a-z]$|_[a-z]_\d+$', '', base)}
            for variant in variants:
                words = variant.split('_')
                candidates.add(variant)
                for trim in range(1, min(3, len(words) - 2) + 1):
                    candidates.update(['_'.join(words[trim:]), '_'.join(words[:-trim])])
        candidates = {name for name in candidates if len(name) >= 4 and '\n' not in name and '\r' not in name}
        (out / 'aliases.txt').write_text(''.join(name + '\n' for name in sorted(candidates)), encoding='utf-8')
        print(json.dumps({'game': args.game, 'mode': args.mode, 'source_names': len(names), 'candidates': len(candidates)}))
        return
    prefixes = {width: set() for width in range(1, 4)}
    target_prefixes = {width: set() for width in range(1, 4)}
    tails = Counter()
    for name in names:
        match = MODERN.fullmatch(name)
        if match is None:
            continue
        on_target = snapshot.fnv1a(name, args.game, 'sound_asset') & snapshot.ID_MASK in held
        if on_target:
            tails[name[len(match['stem']):]] += 1
        take = TAKE.fullmatch(match['stem'])
        if take is not None:
            width = len(take['number'])
            prefixes[width].add(take['base'])
            if on_target:
                target_prefixes[width].add(take['base'])
    if not tails:
        raise SystemExit('No verified modern sound tails on the target capture')
    ending_file = out / 'take-tails.txt'
    rows(ending_file, tails)
    report = {'game': args.game, 'mode': args.mode, 'source_names': len(names), 'tails': len(tails), 'widths': {}}
    for width, beginnings in prefixes.items():
        if not beginnings:
            continue
        begin, numbers = out / f'take{width}-beginnings.txt', out / f'take{width}-numbers.txt'
        takes = {f'{number:0{width}d}' for number in range(args.max_take + 1)}
        rows(begin, beginnings)
        rows(numbers, takes)
        (out / f'take{width}.plan.txt').write_text(
            f'label: {args.game} verified sound takes width {width}\n'
            f'describe: verified recorded sound-file families retaining their observed take padding, takes 0..{args.max_take}, and {len(tails)} original encoding tails measured on the target capture; original directory separators retained\n'
            f'game: {args.game}\nbegin: @{begin.relative_to(ROOT).as_posix()}\n'
            f'stem: @{numbers.relative_to(ROOT).as_posix()}\nend: @{ending_file.relative_to(ROOT).as_posix()}\nbare: no\nfold: yes\n', encoding='utf-8')
        report['widths'][width] = {'families': len(beginnings), 'target_families': len(target_prefixes[width]), 'candidates': len(beginnings)*len(takes)*len(tails)}
    (out / 'take-measurement.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report))

if __name__ == '__main__':
    main()
