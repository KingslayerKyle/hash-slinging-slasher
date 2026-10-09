"""Traverse one frozen alias-pair graph through capture-verified fresh vertices.

Run: python contrib/verified_alias_frontier.py --game BLACKOP7 --seed-file new_aliases.txt --baseline-file frozen_baseline.txt --training-exclude-file earlier_seeds.txt --exclude-file earlier_candidates.txt --out logs/alias_frontier.txt
Repeat --training-exclude-file for every previous source/descendant batch and
--exclude-file for every previously tested candidate file. Current seeds are
automatically excluded from training. --max-candidates defaults to100000 new
distinct name hashes; reaching the bound reports partial, never complete.

The selected capture verifies every explicit seed, frozen baseline name, and
training-excluded name. Rules are trained ONCE on the supplied immutable baseline:
both underscore tokens change at separation2..6, supported by at least3 distinct
otherwise-identical frames; 2..24 fillers/frame, 4..18 tokens/name. Descendants
never train rules. These are exactly the original paired-alias rule conventions.

Only explicit seeds start the queue. Earlier candidate strings and known alias
names are excluded before hashing. Every additional queued name must hash to
the actual same-game sound_alias pool and pass full table/history/findings/claim
key exclusions. Unmatched strings are NEVER expanded. Each name/key expands
once; the queue terminates when no fresh verified vertex remains. Resolved and
previously tested vertices are treated as closed, not replayed as corpus roots.
This is one finite graph search, not a driver, method rotation, or scheduled loop.

Writes attempted candidates, JSON counts/input digests, separate probe hits,
and parent/root/token-position provenance for each fresh match. A partial result
includes pending work; it does not resume itself. Probe names require official
confirm_list confirmation with sound_alias selected and this file as --script.
No findings/config mutation, confirmations, or submissions. Name-only output
preserves the official full64 modern-alias output policy.

Verified readers/exclusions are reused from the exact submitted companion
verified_alias_paired_seed_delta_20261009-191812.py, with normalized-source digest
checking and an unchanged contrib staging fallback. Baseline/seed digests and
the fixed rule profile make scope reviewable. Spent by the explicit frontier,
frozen baseline, and prior candidate sets. Initial BO7 traversal from1180 seeds:
20991 attempts,79 new aliases over four verified depths, empty frontier.
"""
import argparse
from collections import Counter, defaultdict, deque
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
while ROOT != ROOT.parent and not (ROOT / 'scripts/snapshot.py').is_file():
    ROOT = ROOT.parent
if not (ROOT / 'scripts/snapshot.py').is_file():
    raise SystemExit('Cannot find the solver checkout')
COMPANION = ROOT / 'scripts/contributed/verified_alias_paired_seed_delta_20261009-191812.py'
if not COMPANION.is_file():
    COMPANION = ROOT / 'contrib/verified_alias_paired_seed_delta.py'
if not COMPANION.is_file():
    raise SystemExit('Missing verified_alias_paired_seed_delta_20261009-191812.py companion')
if hashlib.sha256(COMPANION.read_text(encoding='utf-8').encode('utf-8')).hexdigest() != 'e0db3f60413e5e24b59d616aac2c824cd88ae59131cda485d571d793bc9d32da':
    raise SystemExit('Alias-pair companion differs from the reviewed original')
spec = importlib.util.spec_from_file_location('alias_pair_method', COMPANION)
method = importlib.util.module_from_spec(spec)
spec.loader.exec_module(method)
snapshot = method.snapshot


def train(baseline):
    rows = [tuple(n.split('_')) for n in sorted(baseline) if 4 <= len(n.split('_')) <= 18]
    by_gap, profile = {}, []
    for gap in range(2, 7):
        frames = defaultdict(set)
        for row in rows:
            for i in range(len(row) - gap):
                j = i + gap
                frames[row[:i], row[i+1:j], row[j+1:]].add((row[i], row[j]))
        support = Counter()
        for values in frames.values():
            if 2 <= len(values) <= 24:
                for a, b in itertools.combinations(sorted(values), 2):
                    if a[0] != b[0] and a[1] != b[1]:
                        support[a, b] += 1
        rules = defaultdict(set)
        for (a, b), count in support.items():
            if count >= 3:
                rules[a].add(b)
                rules[b].add(a)
        by_gap[gap] = {a: tuple(sorted(values)) for a, values in sorted(rules.items())}
        profile.append({'gap': gap, 'baseline_frames': len(frames),
                        'supported_directed_rules': sum(map(len, rules.values()))})
    return by_gap, profile


def traverse(seeds, rules, held, known, aliases, prior, game, budget):
    seen_names = set(aliases) | prior | seeds
    visited_keys = {snapshot.fnv1a(n, game, 'sound_alias') & snapshot.ID_MASK for n in seeds}
    if len(visited_keys) != len(seeds):
        raise ValueError('Distinct seed spellings share a lookup key; resolve ambiguity first')
    frontier = deque((n, 0, n, ()) for n in sorted(seeds))
    attempted, hits, provenance = set(), {}, {}
    expanded_names, expanded_keys = set(), set()
    depth_attempts, depth_hits, depth_expanded = Counter(), Counter(), Counter()
    bound_reached, partial_vertex, known_key_matches = False, None, 0
    while frontier and not bound_reached:
        name, depth, origin, path_positions = frontier.popleft()
        key = snapshot.fnv1a(name, game, 'sound_alias') & snapshot.ID_MASK
        if key not in held or name in expanded_names or key in expanded_keys:
            raise ValueError('Frontier invariant failed: unverified or repeated vertex')
        expanded_names.add(name)
        expanded_keys.add(key)
        depth_expanded[depth] += 1
        row = tuple(name.split('_'))
        if not 4 <= len(row) <= 18:
            continue
        for gap, offers in rules.items():
            if bound_reached:
                break
            for i in range(len(row) - gap):
                if bound_reached:
                    break
                j = i + gap
                for a, b in offers.get((row[i], row[j]), ()):
                    changed = list(row)
                    changed[i], changed[j] = a, b
                    candidate = '_'.join(changed)
                    if candidate in seen_names:
                        continue
                    if len(attempted) >= budget:
                        bound_reached = True
                        partial_vertex = {'name': name, 'depth': depth}
                        break
                    seen_names.add(candidate)
                    attempted.add(candidate)
                    depth_attempts[depth+1] += 1
                    candidate_key = snapshot.fnv1a(candidate, game, 'sound_alias') & snapshot.ID_MASK
                    if candidate_key not in held:
                        continue
                    if candidate_key in known:
                        known_key_matches += 1
                        continue
                    if candidate_key in visited_keys:
                        continue
                    visited_keys.add(candidate_key)
                    new_path = path_positions + ((i, j),)
                    hits[candidate] = candidate_key
                    provenance[candidate] = {'parent': name, 'origin_seed': origin, 'depth': depth+1,
                                             'token_positions': list(new_path), 'key63': f'{candidate_key:016x}'}
                    depth_hits[depth+1] += 1
                    frontier.append((candidate, depth+1, origin, new_path))
    report = {'max_new_candidate_attempts': budget, 'new_candidate_attempts': len(attempted),
              'unresolved_unclaimed_alias_matches': len(hits), 'known_key_matches_excluded': known_key_matches,
              'verified_vertices_expanded': len(expanded_names), 'expanded_keys_unique': len(expanded_keys),
              'depth_candidate_attempts': dict(depth_attempts), 'depth_new_matches': dict(depth_hits),
              'depth_vertices_expanded': dict(depth_expanded), 'matched_paths_using_multiple_position_pairs':
                  sum(len(set(tuple(p) for p in v['token_positions'])) > 1 for v in provenance.values()),
              'termination': 'candidate_budget' if bound_reached else 'empty_verified_frontier',
              'partial': bound_reached, 'pending_verified_frontier': len(frontier) + (partial_vertex is not None),
              'partially_expanded_vertex': partial_vertex}
    return attempted, hits, provenance, report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--game', type=str.upper, choices=sorted(snapshot.MODERN | {'BLKOPS04', 'BLKOPSCW'}), required=True)
    parser.add_argument('--seed-file', type=Path, required=True)
    parser.add_argument('--baseline-file', type=Path, required=True)
    parser.add_argument('--training-exclude-file', type=Path, action='append', required=True)
    parser.add_argument('--exclude-file', type=Path, action='append', required=True)
    parser.add_argument('--max-candidates', type=int, default=100000)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    if args.max_candidates < 1:
        parser.error('--max-candidates must be positive')
    shot = snapshot.read(ROOT / 'snapshots' / (args.game.lower() + '.ids'))
    if shot.game != args.game:
        parser.error('Capture tag does not match selected game')
    held = set(shot.by_pool()['sound_alias'])
    seeds, seed_sha = method.read_seeds(args.seed_file, args.game, held)
    baseline, baseline_sha = method.read_seeds(args.baseline_file, args.game, held)
    excluded_seeds, training_sources = set(seeds), []
    for path in args.training_exclude_file:
        names, digest = method.read_seeds(path, args.game, held)
        excluded_seeds.update(names)
        training_sources.append({'file': path.name, 'names': len(names), 'sha256': digest})
    if baseline & excluded_seeds:
        parser.error('Frozen baseline contains source or descendant seeds held out of training')
    prior, prior_sources = set(), []
    for path in args.exclude_file:
        data = path.read_bytes()
        names = set(data.decode('utf-8-sig').splitlines())
        if any(not n or n != n.strip().lower() or ',' in n or not n.isascii()
               or any(ord(c) < 32 or ord(c) == 127 for c in n) for n in names):
            parser.error('Prior candidate inputs must contain normalized ASCII names only')
        prior.update(names)
        prior_sources.append({'file': path.name, 'names': len(names), 'sha256': hashlib.sha256(data).hexdigest()})
    rules, profile = train(baseline)
    aliases = method.corpus(args.game) | excluded_seeds | baseline
    known = method.excluded_keys(args.game, aliases)
    attempted, hits, provenance, result = traverse(seeds, rules, held, known, aliases, prior,
                                                  args.game, args.max_candidates)
    report = {'game': args.game, 'seed_file': args.seed_file.name, 'seed_sha256': seed_sha,
              'verified_root_seeds': len(seeds), 'baseline_file': args.baseline_file.name,
              'baseline_sha256': baseline_sha, 'baseline_aliases': len(baseline),
              'all_source_and_descendant_seeds_excluded_from_training': True,
              'training_exclusions': training_sources, 'prior_candidate_files': prior_sources,
              'fixed_rule_profile': profile, **result}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(''.join(n + '\n' for n in sorted(attempted)), encoding='utf-8')
    args.out.with_suffix('.probe_hits.txt').write_text(''.join(n + '\n' for n in sorted(hits)), encoding='utf-8')
    args.out.with_suffix('.provenance.json').write_text(json.dumps(provenance, indent=2) + '\n')
    args.out.with_suffix('.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report), flush=True)


if __name__ == '__main__':
    main()
