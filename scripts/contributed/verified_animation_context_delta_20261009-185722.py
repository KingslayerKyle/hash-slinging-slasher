"""Recover animations using only paired contexts newly enabled by verified source clips.

Run: python contrib/verified_animation_context_delta.py --game BLACKOP7 --seed-file contrib/verified_animation_context_delta/blackop7/verified_seed_names.txt --exclude-file contrib/verified_animation_context_delta/blackop7/prior_overlap.txt --out logs/animation_context_delta.txt
Optional: add --exclude-file PATH for each prior candidate list to remove its tested space.
Then: bin/windows/confirm_list.exe logs/animation_context_delta.txt --game BLACKOP7 --label "BO7 newly witnessed animation contexts from verified source clips" --script contrib/verified_animation_context_delta.py

Reads source-verified modern animation tables/history, a name-only verified seed
list, optional prior candidate lists, target capture, and current exclusions.
Writes delta candidates, excluded-overlap names, a JSON report, and probe matches.
CSV hash/key metadata is never accepted. Every seed is independently rehashed and
checked against the selected target xanim census. A rule is eligible only if it lacked three
independent sibling frames before these seeds and now has at least three.
Every supplied prior candidate list is subtracted; only newly enabled contexts
are applied. Does not write findings/config, confirm, or submit.
Reusable across modern games; witness token distance remains 2..6, both tokens
must change, and all other name tokens remain fixed. The seed clips are removed
from the counterfactual baseline, not from the independent verified corpus.
Spent by a frozen seed set and unchanged witnessed support; this is not a loop.
Initial BO7 measurement 2026-10-09: 643 verified seeds enable 438 directed rules;
30,829 candidates minus 27 previously tested gives 30,802; 16 unclaimed probe hits.
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

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--game', required=True, choices=sorted(snapshot.MODERN))
parser.add_argument('--seed-file', type=Path, required=True)
parser.add_argument('--exclude-file', type=Path, action='append', default=[])
parser.add_argument('--out', type=Path, required=True)
args = parser.parse_args()
GAME, SOURCE, PRIOR = args.game, args.seed_file, args.exclude_file


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


def support(groups):
    result = Counter()
    for values in groups.values():
        if 2 <= len(values) <= 24:
            for a, b in itertools.combinations(sorted(values), 2):
                if a[0] != b[0] and a[1] != b[1]:
                    result[a, b] += 1
    return result


shot = snapshot.read(ROOT / 'snapshots' / (GAME.lower() + '.ids'))
assert shot.game == GAME
held = set(shot.by_pool()['xanim'])
seeds = set(SOURCE.read_text().splitlines())
if not seeds or any(not n.isascii() or n != n.strip().lower() or ',' in n
                    or any(ord(c) < 32 for c in n) for n in seeds):
    raise SystemExit('Seed input must contain normalized ASCII names only, one per line')
if any(snapshot.fnv1a(n, GAME, 'xanim') & snapshot.ID_MASK not in held for n in seeds):
    raise SystemExit('Every seed must independently reproduce a target xanim ID')
names, known = corpus(GAME)
names.update(seeds)
known.update(snapshot.known_hashes(game=GAME))
hashed = {n: snapshot.fnv1a(n, GAME, 'xanim') & snapshot.ID_MASK for n in names}
known.update(hashed.values())
for row in (ROOT / 'state/claimed.txt').read_text().splitlines():
    try:
        known.add(int(row, 16) & snapshot.ID_MASK)
    except ValueError:
        pass
wanted = held - known
rows = [tuple(n.split('_')) for n in sorted(names) if 4 <= len(n.split('_')) <= 18]
target_rows = [(tuple(n.split('_')), n in seeds) for n in names
               if hashed[n] in held and 4 <= len(n.split('_')) <= 18]
candidates = set()
report = []
for gap in range(2, 7):
    old_groups, new_groups = defaultdict(set), defaultdict(set)
    touched = set()
    for row, is_new in target_rows:
        for i in range(len(row) - gap):
            j = i + gap
            frame = row[:i], row[i+1:j], row[j+1:]
            values = row[i], row[j]
            new_groups[frame].add(values)
            if is_new:
                touched.add(frame)
            else:
                old_groups[frame].add(values)
    old_support, new_support = support(old_groups), support(new_groups)
    rules = defaultdict(set)
    for (a, b), count in new_support.items():
        if count >= 3 and old_support[a, b] < 3:
            rules[a].add(b)
            rules[b].add(a)
    before = len(candidates)
    for row in rows:
        for i in range(len(row) - gap):
            j = i + gap
            for a, b in rules.get((row[i], row[j]), ()):
                changed = list(row)
                changed[i], changed[j] = a, b
                candidate = '_'.join(changed)
                if candidate not in names:
                    candidates.add(candidate)
    report.append({'gap': gap, 'new_source_frames': len(touched), 'newly_supported_directed_rules': sum(map(len, rules.values())),
                   'new_candidates': len(candidates)-before})
raw_count = len(candidates)
excluded_overlap = set()
for path in PRIOR:
    if not path.is_file():
        raise SystemExit('Missing prior candidate file: ' + str(path))
    with path.open(encoding='utf-8') as handle:
        for row in handle:
            name = row.rstrip('\r\n')
            if name in candidates:
                excluded_overlap.add(name)
            candidates.discard(name)
hits = {n for n in candidates if snapshot.fnv1a(n, GAME, 'xanim') & snapshot.ID_MASK in wanted}
out = args.out
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(''.join(n + '\n' for n in sorted(candidates)), encoding='utf-8')
out.with_suffix('.excluded_overlap.txt').write_text(''.join(n + '\n' for n in sorted(excluded_overlap)), encoding='utf-8')
out.with_suffix('.probe_hits.txt').write_text(''.join(n + '\n' for n in sorted(hits)), encoding='utf-8')
summary = {'game': GAME, 'independently_verified_csv_seeds': len(seeds), 'current_typed_names': len(names),
           'current_target_held_eligible': len(target_rows), 'wanted_xanim': len(wanted),
           'raw_new_context_candidates': raw_count, 'prior_tested_removed': raw_count-len(candidates),
           'delta_candidates': len(candidates), 'unresolved_unclaimed_probe_hits': len(hits), 'gaps': report}
out.with_suffix('.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
print(json.dumps(summary), flush=True)
