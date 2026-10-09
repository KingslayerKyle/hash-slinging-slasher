"""Build graphics segment plans from verified names and target-held endings.

Run from a solver checkout with --game and --kind. Writes only ignored working
lists under contrib/verified_graphics_segments. Execute each plan with that game
and asset type selected in confirm_plan; candidates are not discoveries.
"""
import argparse
from collections import Counter
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
while ROOT != ROOT.parent and not (ROOT / 'scripts/snapshot.py').is_file():
    ROOT = ROOT.parent
if not (ROOT / 'scripts/snapshot.py').is_file():
    ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / 'scripts'))
import snapshot

TABLES = {'image': 'fnv1a_ximages', 'material': 'fnv1a_xmaterials', 'xanim': 'fnv1a_xanims'}

def corpus(kind):
    table = TABLES[kind]
    names = set(snapshot.table_names(table, table + '_v2'))
    for top in ['all_names', 'submissions', 'findings']:
        for path in (ROOT / top).rglob(kind + '*.txt'):
            for line in path.read_text(encoding='utf-8').splitlines():
                raw, sep, name = line.partition(',')
                if not sep or not name:
                    continue
                try:
                    key = int(raw, 16) & snapshot.ID_MASK
                except ValueError:
                    continue
                if any(snapshot.fnv1a(name, game=game, kind=kind) & snapshot.ID_MASK == key
                       for game in ['YAMYAMOK', 'BLKOPSCW']):
                    names.add(name.lower().replace(chr(92), '/'))
    return names

def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--game', required=True, choices=sorted(snapshot.MODERN))
    parser.add_argument('--kind', required=True, choices=sorted(TABLES))
    parser.add_argument('--ends', type=int, default=3000)
    args = parser.parse_args()
    if not 1 <= args.ends <= 10000:
        parser.error('--ends must be between 1 and 10000')
    shot = snapshot.read(ROOT / 'snapshots' / (args.game.lower() + '.ids'))
    assert shot.game == args.game
    held = set(shot.by_pool()[args.kind])
    stems, endings, target_endings = set(), Counter(), Counter()
    for name in corpus(args.kind):
        if not name.isascii() or name.startswith('twc/') or any(c in name for c in '~&.\r\n'):
            continue
        head, slash, tail = name.rpartition('/')
        words = tail.split('_')
        on_target = snapshot.fnv1a(name, args.game, args.kind) & snapshot.ID_MASK in held
        for count in range(1, len(words)):
            stem = head + slash + '_'.join(words[:count])
            if len(stem) >= 4:
                stems.add(stem)
        for count in range(1, min(3, len(words) - 1) + 1):
            ending = '_' + '_'.join(words[-count:])
            endings[ending] += 1
            if on_target:
                target_endings[ending] += 1
    selected = [end for end, _ in target_endings.most_common(args.ends)]
    selected.extend(end for end, _ in endings.most_common() if end not in target_endings)
    selected = selected[:args.ends]
    if not stems or not selected:
        raise SystemExit('No measurable graphics vocabulary')
    out = ROOT / 'contrib/verified_graphics_segments' / args.game.lower()
    out.mkdir(parents=True, exist_ok=True)
    stem_file, end_file = out / (args.kind + '.stems.txt'), out / (args.kind + '.ends.txt')
    for path, rows in [(stem_file, sorted(stems)), (end_file, selected)]:
        path.write_text(''.join('0,' + row + '\n' for row in rows), encoding='utf-8')
    plan = out / (args.kind + '.plan.txt')
    plan.write_text(f'label: {args.game} verified {args.kind} segments with target-held endings\n'
                    f'describe: source-hash-verified underscore prefixes, crossed with {len(selected)} measured endings, prioritising names held in this target capture; terrain blends excluded\n'
                    f'game: {args.game}\nstem: @{stem_file.relative_to(ROOT).as_posix()}\n'
                    f'end: @{end_file.relative_to(ROOT).as_posix()}\nbare: yes\nfold: yes\n', encoding='utf-8')
    print(f'{args.game} {args.kind}: {len(stems)} stems, {len(selected)} endings, '
          f'{len(stems)*len(selected)} candidates; {plan.relative_to(ROOT).as_posix()}')

if __name__ == '__main__':
    main()
