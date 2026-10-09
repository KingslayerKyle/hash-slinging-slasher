"""Modern sound transfer and measured directory/tail and alias-segment plans.

Run from the repository: python contrib/mwiii_sound_relations.py --game YAMYAMOK
Names from cod-name-db are restored and verified by the shared reader before use.
Directories and encoding tails come from sounds the requested snapshot actually holds;
basenames and alias fragments can come from any already confirmed game.
Generated working lists are inputs, not new discoveries: confirm_list/confirm_plan must
verify them against the requested game's unnamed sound pools before submission.
"""
from pathlib import Path
import argparse
from collections import Counter
import json
import re
import sys

ROOT = Path(__file__).resolve().parent
while not (ROOT / 'scripts' / 'snapshot.py').is_file() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
if not (ROOT / 'scripts' / 'snapshot.py').is_file():
    ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / 'scripts'))
import settings
import snapshot

TAIL = re.compile(r'(?P<stem>.+)\.(?P<codec>[a-z]{1,4})\.(?P<quality>\d+)\.(?P<rate>\d+)\.(?P<language>[a-z_]+)$')
MODERN = snapshot.MODERN
MASK = snapshot.ID_MASK

def key(kind, name):
    basis = 0xcbf29ce484222325 if kind == 'sound_alias' else 0x47f5817a5ef961ba
    for byte in name.lower().replace(chr(92), '/').encode('utf-8'):
        basis = ((basis ^ byte) * 0x100000001b3) & ((1 << 64) - 1)
    return basis & MASK

def corpus(kind):
    tables = ['fnv1a_xsounds_v2'] if kind == 'sound_asset' else [
        'fnv1a_soundbanks_aliases', 'fnv1a_soundbanks_aliases_v2']
    names = set(snapshot.table_names(*tables))
    for top in ['all_names', 'submissions', 'findings']:
        for path in (ROOT / top).rglob(kind + '*.txt'):
            if kind == 'sound_asset' and not any(game.lower() in str(path).lower() for game in MODERN):
                continue
            for line in path.read_text(encoding='utf-8').splitlines():
                claimed, sep, name = line.partition(',')
                if not sep or not name:
                    continue
                try:
                    if int(claimed, 16) & MASK == key(kind, name):
                        names.add(name.lower())
                except ValueError:
                    continue
    return names

def split_sound(name):
    match = TAIL.fullmatch(name)
    if match is None:
        return None
    stem = match['stem']
    boundary = max(stem.rfind('/'), stem.rfind('.'))
    return stem[:boundary + 1], stem[boundary + 1:], name[len(stem):]

def write_rows(path, rows):
    path.write_text(''.join(row + '\n' for row in sorted(set(rows))), encoding='utf-8')

def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--game', default='YAMYAMOK', choices=sorted(MODERN))
    parser.add_argument('--out', default='contrib/mwiii_sound_work_20261009')
    parser.add_argument('--alias-ends', type=int, default=3000)
    args = parser.parse_args()
    out = ROOT / args.out
    out.mkdir(parents=True, exist_ok=True)
    shot = snapshot.read(ROOT / 'snapshots' / (args.game.lower() + '.ids'))
    assert shot.game == args.game
    held = {kind: set(ids) for kind, ids in shot.by_pool().items()}
    sounds, aliases = corpus('sound_asset'), corpus('sound_alias')
    write_rows(out / 'transfer.txt', sounds | aliases)
    dirs, bases, tails = Counter(), set(), Counter()
    separator_counts = Counter()
    for name in sounds:
        parts = split_sound(name)
        if parts is None:
            continue
        directory, base, tail = parts
        if base:
            bases.add(base)
        if key('sound_asset', name) in held['sound_asset']:
            dirs[directory] += 1
            tails[tail] += 1
            separator_counts[directory[-1:] or 'bare'] += 1
    # Empty directories are represented by the plan's bare flag, never an empty list row.
    bare = '' in dirs
    write_rows(out / 'sound_dirs.txt', (d for d in dirs if d))
    write_rows(out / 'sound_bases.txt', bases)
    write_rows(out / 'sound_tails.txt', tails)
    starts, ends = set(), Counter()
    for alias in aliases:
        if not alias or '/' in alias or '.' in alias or chr(92) in alias:
            continue
        words = alias.split('_')
        for count in range(1, len(words)):
            prefix = '_'.join(words[:count])
            if len(prefix) >= 4:
                starts.add(prefix)
        for count in range(1, min(3, len(words) - 1) + 1):
            ends['_' + '_'.join(words[-count:])] += 1
    write_rows(out / 'alias_stems.txt', starts)
    write_rows(out / 'alias_ends.txt', [name for name, _ in ends.most_common(args.alias_ends)])
    relative = out.relative_to(ROOT).as_posix()
    (out / 'sounds.plan.txt').write_text(
        f'label: {args.game} sound directories and tails with confirmed modern basenames\n'
        'describe: directories and complete encoding tails measured on this snapshot, crossed with modern sound basenames; original separators retained\n'
        f'game: {args.game}\nbegin: @{relative}/sound_dirs.txt\nstem: @{relative}/sound_bases.txt\n'
        f'end: @{relative}/sound_tails.txt\nbare: {"yes" if bare else "no"}\n', encoding='utf-8')
    (out / 'aliases.plan.txt').write_text(
        f'label: {args.game} sound alias segments from the refreshed confirmed corpus\n'
        'describe: observed underscore prefixes crossed with frequent one-to-three segment alias endings, including newly confirmed modern names\n'
        f'game: {args.game}\nstem: @{relative}/alias_stems.txt\nend: @{relative}/alias_ends.txt\n', encoding='utf-8')
    report = {'game': args.game, 'sounds': len(sounds), 'aliases': len(aliases),
              'target_sound_separators': dict(separator_counts), 'sound_dirs': len(dirs),
              'sound_bases': len(bases), 'sound_tails': len(tails),
              'alias_stems': len(starts), 'alias_ends': min(args.alias_ends, len(ends)),
              'sound_candidates': len(dirs) * len(bases) * len(tails),
              'alias_candidates': len(starts) * min(args.alias_ends, len(ends))}
    (out / 'measurement.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report), flush=True)

if __name__ == '__main__':
    main()
