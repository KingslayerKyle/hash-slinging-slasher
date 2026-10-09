"""Fill unseen numeric gaps in graphics families represented on one capture.

A family is the exact text before and after a numeric run, with its observed
padding width. Requires two verified members on the target. Bounds come from
source-verified modern names of the same asset type; no guessed outer margin.
Generated candidates require normal confirmation and submission for that type.
"""
import argparse
from collections import defaultdict
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent
while ROOT != ROOT.parent and not (ROOT / 'scripts/snapshot.py').is_file(): ROOT = ROOT.parent
if not (ROOT / 'scripts/snapshot.py').is_file(): ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / 'scripts'))
import snapshot

def corpus(kind, table, game):
    result = set(snapshot.table_names(table))
    for top in ['all_names', 'submissions', 'findings']:
        for path in (ROOT / top).rglob(kind + '*.txt'):
            for line in path.read_text(encoding='utf-8').splitlines():
                raw, sep, name = line.partition(',')
                if not sep or not name: continue
                try: key = int(raw, 16) & snapshot.ID_MASK
                except ValueError: continue
                if snapshot.fnv1a(name, game, kind) & snapshot.ID_MASK == key:
                    result.add(name.lower())
    return {n for n in result if n.isascii() and '\n' not in n and '\r' not in n}

def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--game', required=True, choices=sorted(snapshot.MODERN))
    parser.add_argument('--kind', required=True, choices=['image', 'material'])
    args = parser.parse_args()
    shot = snapshot.read(ROOT / 'snapshots' / (args.game.lower() + '.ids'))
    assert shot.game == args.game
    held = set(shot.by_pool()[args.kind])
    table = 'fnv1a_ximages_v2' if args.kind == 'image' else 'fnv1a_xmaterials_v2'
    known = corpus(args.kind, table, args.game)
    source, target = defaultdict(set), defaultdict(set)
    for name in known:
        on_target = snapshot.fnv1a(name, args.game, args.kind) & snapshot.ID_MASK in held
        for match in re.finditer(r'\d+', name):
            if len(match[0]) > 3: continue
            frame = (name[:match.start()], name[match.end():], len(match[0]))
            source[frame].add(int(match[0]))
            if on_target: target[frame].add(int(match[0]))
    candidates = set()
    families = 0
    for frame, numbers in target.items():
        if len(numbers) < 2: continue
        families += 1
        before, after, width = frame
        observed = source[frame]
        for number in range(min(observed), max(observed) + 1):
            if number not in observed:
                candidate = before + f'{number:0{width}d}' + after
                if candidate not in known: candidates.add(candidate)
    out = ROOT / 'contrib/verified_target_number_gaps' / args.game.lower()
    out.mkdir(parents=True, exist_ok=True)
    path = out / (args.kind + '.txt')
    path.write_text(''.join('0,' + n + '\n' for n in sorted(candidates)), encoding='utf-8')
    print(json.dumps({'game': args.game, 'kind': args.kind, 'target_multi_member_families': families,
                      'source_names': len(known), 'candidates': len(candidates), 'list': path.relative_to(ROOT).as_posix()}))

if __name__ == '__main__': main()
