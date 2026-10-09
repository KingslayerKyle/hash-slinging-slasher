"""Build disjoint four-layer terrain plans for an untested numeric domain.

The pure n-token domain is bounded explicitly. With --completed-tokens, omit
every combination contained in the already completed token grid: partition by
the first layer whose token was absent there. Use its original token file,
never a remeasured ranking. Plans require explicit material confirmation and
normal submission for this game. No game/process or network access.
"""
import argparse
from itertools import product
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent
while ROOT != ROOT.parent and not (ROOT / 'scripts/snapshot.py').is_file(): ROOT = ROOT.parent
if not (ROOT / 'scripts/snapshot.py').is_file(): ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / 'scripts'))
import snapshot

def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--game', required=True, choices=sorted(snapshot.MODERN))
    parser.add_argument('--limit', type=int, default=1000)
    parser.add_argument('--completed-tokens', type=Path)
    args = parser.parse_args()
    if not 1 <= args.limit <= 1200: parser.error('--limit must be between 1 and 1200')
    shot = snapshot.read(ROOT / 'snapshots' / (args.game.lower() + '.ids'))
    assert shot.game == args.game and 'material' in shot.by_pool()
    completed = set()
    if args.completed_tokens is not None:
        path = args.completed_tokens if args.completed_tokens.is_absolute() else ROOT / args.completed_tokens
        for line in path.read_text(encoding='utf-8').splitlines():
            token = line.partition(',')[2] if ',' in line else line.strip()
            if not re.fullmatch(r'\d+d?n', token):
                raise SystemExit('Completed token list must contain only numeric n/dn tokens')
            completed.add(token)
    domain = {f'{number}n' for number in range(args.limit + 1)}
    old, new = sorted(domain & completed), sorted(domain - completed)
    all_tokens = sorted(domain)
    if not new: raise SystemExit('This numeric domain is entirely covered by the completed grid')
    out = ROOT / 'contrib/verified_terrain_numeric_delta' / args.game.lower()
    out.mkdir(parents=True, exist_ok=True)
    files = {}
    for key, tokens in [('all', all_tokens), ('old', old), ('new', new)]:
        for role in ['stem', 'end']:
            path = out / f'{key}-{role}.txt'
            path.write_text(''.join('0,' + ('_' if role == 'end' else '') + t + '\n' for t in tokens), encoding='utf-8')
            files[key, role] = path.relative_to(ROOT).as_posix()
    pair_sets = {'new-all': (new, all_tokens), 'old-new': (old, new), 'old-old': (old, old)}
    for key, (first, second) in pair_sets.items():
        path = out / (key + '-begin.txt')
        with path.open('w', encoding='utf-8') as stream:
            for a, b in product(first, second): stream.write(f'0,twc/*{a}_{b}_\n')
        files[key, 'begin'] = path.relative_to(ROOT).as_posix()
    phases = [('new-all', 'all', 'all', len(new)*len(domain)**3),
              ('old-new', 'all', 'all', len(old)*len(new)*len(domain)**2),
              ('old-old', 'new', 'all', len(old)**2*len(new)*len(domain)),
              ('old-old', 'old', 'new', len(old)**3*len(new))]
    plans = []
    for index, (begin, stem, end, candidates) in enumerate(phases):
        if not candidates: continue
        path = out / f'layer{index+1}-new.plan.txt'
        path.write_text(f'label: {args.game} terrain numeric domain 0..{args.limit}, first untested layer {index+1}\n'
                        f'describe: pure n terrain indices 0..{args.limit}; excludes the completed token grid; this disjoint phase puts the first previously untested token in layer {index+1}\n'
                        f'game: {args.game}\nbegin: @{files[begin,"begin"]}\nstem: @{files[stem,"stem"]}\nend: @{files[end,"end"]}\n'
                        'bare: no\nfold: yes\n', encoding='utf-8')
        plans.append({'first_new_layer': index+1, 'candidates': candidates, 'plan': path.relative_to(ROOT).as_posix()})
    assert sum(p['candidates'] for p in plans) == len(domain)**4 - len(old)**4
    report = {'game': args.game, 'limit': args.limit, 'domain': len(domain), 'completed_intersection': len(old), 'new_tokens': len(new),
              'omitted_completed_combinations': len(old)**4, 'candidates': sum(p['candidates'] for p in plans), 'plans': plans}
    (out / 'measurement.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report))

if __name__ == '__main__': main()
