"""Measure target-witnessed paired animation token substitutions on modern games.

Run: python contrib/verified_modern_animation_pairs.py --game BLACKOP7 --out logs/bo7_pairs.txt
Then: bin/windows/confirm_list.exe logs/bo7_pairs.txt --game BLACKOP7 --label "BO7 target-witnessed paired animation tokens" --script contrib/verified_modern_animation_pairs.py
Reads verified modern animation names, the selected capture and exclusion keys.
Writes all candidate names, a JSON diagnostic, and a separate probe-hit file;
the latter contains hash matches requiring normal confirmation and submission.
Never changes findings or submits.
Reusable: both changed tokens must vary together in at least three otherwise
identical target-held sibling frames. Applies those coupled rules to whole real
modern animation names, preserving token distance and every unchanged token.
Measured 2026-10-09 on BLACKOP7: 153,884 verified seeds, 88,704 target-held
eligible names; 1,137,241 unique candidates, 140 unresolved/unclaimed probe hits.
Spent by a fixed source corpus, target-held frames, and token-distance band.
"""
from pathlib import Path
from collections import Counter, defaultdict
import argparse
import itertools
import json
import sys

ROOT = Path(__file__).resolve().parent
while ROOT != ROOT.parent and not (ROOT / 'scripts/snapshot.py').is_file():
    ROOT = ROOT.parent
sys.path.insert(0, str(ROOT / 'scripts'))
import snapshot


def corpus(game):
    names = set(snapshot.table_names('fnv1a_xanims_v2'))
    keys = set()
    for top in ['all_names', 'submissions', 'findings']:
        for path in (ROOT / top).rglob('xanim*.txt'):
            for row in path.read_text(encoding='utf-8').splitlines():
                raw, sep, name = row.partition(',')
                if not sep or not name:
                    continue
                try:
                    key = int(raw, 16) & snapshot.ID_MASK
                except ValueError:
                    continue
                if snapshot.fnv1a(name, game, 'xanim') & snapshot.ID_MASK == key:
                    names.add(name.strip().lower().replace(chr(92), '/'))
                    keys.add(key)
    return {n for n in names if n.isascii() and n == n.strip() and '\n' not in n and '\r' not in n}, keys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--game', required=True, choices=sorted(snapshot.MODERN))
    parser.add_argument('--out', required=True)
    parser.add_argument('--min-gap', type=int, default=2)
    parser.add_argument('--max-gap', type=int, default=6)
    parser.add_argument('--support', type=int, default=3)
    args = parser.parse_args()
    if not 2 <= args.min_gap <= args.max_gap <= 17:
        parser.error('token gap band must remain inside 2..17')
    if args.support < 3:
        parser.error('--support must be at least three independent sibling frames')
    shot = snapshot.read(ROOT / 'snapshots' / (args.game.lower() + '.ids'))
    assert shot.game == args.game
    held = set(shot.by_pool()['xanim'])
    names, excluded = corpus(args.game)
    excluded.update(snapshot.known_hashes(game=args.game))
    claimed = ROOT / 'state/claimed.txt'
    if claimed.exists():
        for line in claimed.read_text().splitlines():
            try:
                excluded.add(int(line, 16) & snapshot.ID_MASK)
            except ValueError:
                pass
    hashed = {n: snapshot.fnv1a(n, args.game, 'xanim') & snapshot.ID_MASK for n in names}
    excluded.update(hashed.values())
    wanted = held - excluded
    rows = [tuple(n.split('_')) for n in sorted(names) if 4 <= len(n.split('_')) <= 18]
    target_rows = [r for r in rows if hashed['_'.join(r)] in held]
    candidates = set()
    report = []
    for gap in range(args.min_gap, args.max_gap + 1):
        groups = defaultdict(set)
        for row in target_rows:
            for i in range(len(row) - gap):
                j = i + gap
                frame = (row[:i], row[i+1:j], row[j+1:])
                groups[frame].add((row[i], row[j]))
        support = Counter()
        for values in groups.values():
            if 2 <= len(values) <= 24:
                for a, b in itertools.combinations(sorted(values), 2):
                    if a[0] != b[0] and a[1] != b[1]:
                        support[a, b] += 1
        rules = defaultdict(set)
        for (a, b), count in support.items():
            if count >= args.support:
                rules[a].add(b)
                rules[b].add(a)
        before = len(candidates)
        controls = 0
        for row in rows:
            for i in range(len(row) - gap):
                j = i + gap
                for a, b in rules.get((row[i], row[j]), ()):
                    changed = list(row)
                    changed[i], changed[j] = a, b
                    candidate = '_'.join(changed)
                    if candidate in names:
                        controls += 1
                    else:
                        candidates.add(candidate)
        record = {'gap': gap, 'rules': sum(map(len, rules.values())),
                  'known_controls': controls, 'new_candidates': len(candidates) - before}
        report.append(record)
        print(json.dumps(record), flush=True)
    hits = {n for n in candidates if snapshot.fnv1a(n, args.game, 'xanim') & snapshot.ID_MASK in wanted}
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(''.join(n + '\n' for n in sorted(candidates)), encoding='utf-8')
    out.with_suffix('.probe_hits.txt').write_text(''.join(n + '\n' for n in sorted(hits)), encoding='utf-8')
    report = {'game': args.game, 'seeds': len(names), 'target_seed_rows': len(target_rows),
              'wanted': len(wanted), 'candidates': len(candidates), 'unresolved_unclaimed_probe_hits': len(hits),
              'gaps': report}
    out.with_suffix('.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report), flush=True)


if __name__ == '__main__':
    main()
