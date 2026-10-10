"""Traverse one frozen union of paired-token and complete-block alias relations.

Example:
  python contrib/verified_alias_union_frontier.py --game BLACKOP7 \
      --seed-file newly_confirmed_aliases.txt --baseline-file independent_aliases.txt \
      --baseline-sha256 EXPECTED_SHA256 --exclude-file earlier_candidates.txt \
      --out logs/alias_union_frontier.txt
  confirm_list logs/alias_union_frontier.txt --game BLACKOP7 \
      --script contrib/verified_alias_union_frontier.py \
      --label "verified traversal of frozen alias pair and block rules"

Select ONLY sound_alias in the official confirmer. This tool writes diagnostics
and name-only candidate output; it never confirms, modifies findings/config, or
submits. Normal confirmation retains the full64 modern-alias output policy.

Only explicit, capture-verified seeds start the graph. Both relations train ONCE
on the same explicit, independently sourced baseline, checked against its expected
SHA256. Descendants never train rules. Repeat --training-exclude-file to validate
earlier derived batches and reject their presence in the independent baseline.
Repeat --exclude-file for every previously tested candidate set.

The unchanged pair relation jointly replaces two tokens at distance2..6, with
three distinct sibling frames and2..24 fillers per frame. The unchanged complete
block relation preserves immediate anchors, uses canonical1..3-token replacements,
and needs three distinct name-pair witnesses spanning at least six names. These
rules are imported from the exact, digest-checked reviewed block companion.

Every new graph vertex must match the actual same-game sound_alias pool and pass
raw table-key, all-game history/findings, and live claim exclusions. Failed guesses
are never expanded. Every name/key expands once; known and previously attempted
vertices are closed. This is one finite graph search, not a method rotation.
The default100000-attempt bound reports partial output and pending work honestly;
there is no automatic restart or continuation. Provenance records every accepted
edge, root, depth, and relation path. Root and baseline input digests are retained.

Initial BO7 probe:514 newly confirmed block roots and the frozen128720 independent
source baseline yielded14824 unseen attempts and89 unclaimed aliases (72 at depth1,
17 at depth2).603 distinct keys expanded and the frontier emptied; no truncation.
86 matches arrived through pair edges and3 through block edges. No successful path
used both relations after its root. Spent by these roots, baseline and prior files.

Requires the previously submitted verified_alias_interior_blocks.py companion,
found under scripts/contributed/ or its unchanged contrib/ staging filename.
"""
import argparse
from collections import Counter, defaultdict, deque
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path

ROOT = next((p for p in [Path.cwd(), *Path(__file__).resolve().parents]
             if (p/'scripts/snapshot.py').is_file()), None)
if ROOT is None:
    raise SystemExit('Run inside a solver checkout')
COMPANION_SHA256 = '332eea5b2c32bfe8933b27e78c3f5a7caf1cdf6c72ce8c49895e1ec48aaa7aea'
choices = sorted((ROOT/'scripts/contributed').glob('verified_alias_interior_blocks*.py'))
choices.append(ROOT/'contrib/verified_alias_interior_blocks.py')
companion = next((p for p in choices if p.is_file() and
    hashlib.sha256(p.read_text(encoding='utf-8').encode('utf-8')).hexdigest() == COMPANION_SHA256), None)
if companion is None:
    raise SystemExit('Missing unchanged verified_alias_interior_blocks companion')
spec = importlib.util.spec_from_file_location('verified_alias_blocks_companion', companion)
blocks = importlib.util.module_from_spec(spec)
spec.loader.exec_module(blocks)
snapshot = blocks.snapshot


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


def neighbors(name, pair_rules, block_rules):
    row = tuple(name.split('_'))
    if 4 <= len(row) <= 18:
        for gap, offers in sorted(pair_rules.items()):
            for i in range(len(row)-gap):
                j = i+gap
                old = row[i],row[j]
                for new in offers.get(old, ()):
                    changed = list(row)
                    changed[i],changed[j] = new
                    yield '_'.join(changed), {'kind':'pair', 'positions':[i,j], 'old':old, 'new':new}
    for prefix, block, suffix in blocks.cuts(blocks.tokens(name)):
        anchors = prefix[-1],suffix[0]
        for replacement, witnesses in sorted(block_rules.get((anchors,block), {}).items()):
            yield '_'.join(prefix+replacement+suffix), {'kind':'block', 'position':len(prefix),
                'old':block, 'new':replacement, 'anchors':anchors,
                'independent_name_pair_witnesses':len(witnesses), 'witness_pairs':witnesses[:3]}


def traverse(seeds, pair_rules, block_rules, held, known, aliases, prior, game, cap):
    hash_name = lambda n: snapshot.fnv1a(n,game,'sound_alias') & snapshot.ID_MASK
    root_keys = {hash_name(n) for n in seeds}
    if len(root_keys) != len(seeds) or not root_keys <= held:
        raise ValueError('Root keys are unheld or ambiguous')
    seen_names = aliases | prior | seeds
    visited_keys = set(root_keys)
    frontier = deque((n,0,n,()) for n in sorted(seeds))
    attempted, hits, provenance = set(), {}, {}
    expanded_names, expanded_keys = set(), set()
    attempt_depths, hit_depths, expansion_depths = Counter(),Counter(),Counter()
    edge_attempts, edge_hits = Counter(),Counter()
    known_key_matches, partial_vertex = 0,None
    while frontier and partial_vertex is None:
        name,depth,origin,path_kinds = frontier.popleft()
        key = hash_name(name)
        if key not in held or name in expanded_names or key in expanded_keys:
            raise ValueError('Unverified or duplicate expanded vertex')
        expanded_names.add(name)
        expanded_keys.add(key)
        expansion_depths[depth] += 1
        for candidate, edge in neighbors(name,pair_rules,block_rules):
            if candidate in seen_names:
                continue
            if len(attempted) >= cap:
                partial_vertex = {'name':name, 'depth':depth}
                break
            seen_names.add(candidate)
            attempted.add(candidate)
            attempt_depths[depth+1] += 1
            edge_attempts[edge['kind']] += 1
            candidate_key = hash_name(candidate)
            if candidate_key not in held:
                continue
            if candidate_key in known:
                known_key_matches += 1
                continue
            if candidate_key in visited_keys:
                continue
            visited_keys.add(candidate_key)
            next_kinds = path_kinds + (edge['kind'],)
            hits[candidate] = candidate_key
            provenance[candidate] = {'parent':name, 'origin_seed':origin, 'depth':depth+1,
                'edge':edge, 'path_kinds':next_kinds, 'key63':f'{candidate_key:016x}'}
            frontier.append((candidate,depth+1,origin,next_kinds))
            hit_depths[depth+1] += 1
            edge_hits[edge['kind']] += 1
    report = {'max_candidate_attempts':cap, 'new_candidate_attempts':len(attempted),
        'unclaimed_alias_matches':len(hits), 'known_key_matches_excluded':known_key_matches,
        'verified_vertices_expanded':len(expanded_names), 'unique_keys_expanded':len(expanded_keys),
        'depth_attempts':dict(attempt_depths), 'depth_hits':dict(hit_depths),
        'depth_expanded':dict(expansion_depths), 'edge_attempts':dict(edge_attempts),
        'edge_hits':dict(edge_hits), 'matches_using_both_relations':sum(len(set(p['path_kinds']))==2 for p in provenance.values()),
        'partial':partial_vertex is not None, 'termination':'candidate_budget' if partial_vertex else 'empty_verified_frontier',
        'pending_vertices':len(frontier)+(partial_vertex is not None), 'partial_vertex':partial_vertex}
    return attempted,hits,provenance,report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--game', type=str.upper, required=True,
                        choices=sorted(snapshot.MODERN|{'BLKOPS04','BLKOPSCW'}))
    parser.add_argument('--seed-file', type=Path, required=True)
    parser.add_argument('--baseline-file', type=Path, required=True)
    parser.add_argument('--baseline-sha256', required=True)
    parser.add_argument('--training-exclude-file', type=Path, action='append', default=[])
    parser.add_argument('--exclude-file', type=Path, action='append', required=True)
    parser.add_argument('--max-candidates', type=int, default=100000)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    if args.max_candidates < 1:
        parser.error('--max-candidates must be positive')
    shot = snapshot.read(ROOT/'snapshots'/(args.game.lower()+'.ids'))
    if shot.game != args.game:
        parser.error('Capture game differs from selected game')
    held = set(shot.by_pool()['sound_alias'])
    seeds, seed_meta = blocks.read_names(args.seed_file,args.game,held)
    baseline, baseline_meta = blocks.read_names(args.baseline_file,args.game,held)
    if baseline_meta['sha256'] != args.baseline_sha256.lower():
        parser.error('Baseline SHA256 differs from the explicit frozen input digest')
    training_excluded = set(seeds)
    training_meta = []
    for path in args.training_exclude_file:
        names,meta = blocks.read_names(path,args.game,held)
        training_excluded.update(names)
        training_meta.append(meta)
    if baseline & training_excluded:
        parser.error('Derived seed names must not be present in the training baseline')
    prior,prior_meta = set(),[]
    for path in args.exclude_file:
        names,meta = blocks.read_names(path,args.game)
        prior.update(names)
        prior_meta.append(meta)
    pair_rules,pair_profile = train(baseline)
    block_rules,block_profile = blocks.learn(baseline)
    aliases = blocks.corpus(args.game) | baseline | training_excluded
    known = blocks.excluded_keys(args.game,aliases)
    attempted,hits,provenance,report = traverse(seeds,pair_rules,block_rules,held,known,
        aliases,prior,args.game,args.max_candidates)
    report.update(game=args.game, roots=seed_meta, baseline=baseline_meta, prior=prior_meta,
        training_exclusions=training_meta, pair_rules=pair_profile, block_rules=block_profile,
        companion_sha256=COMPANION_SHA256, descendants_train_rules=False)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(''.join(n+'\n' for n in sorted(attempted)),encoding='utf-8')
    args.out.with_suffix('.probe_hits.txt').write_text(''.join(n+'\n' for n in sorted(hits)),encoding='utf-8')
    args.out.with_suffix('.provenance.json').write_text(json.dumps(provenance,indent=2)+'\n',encoding='utf-8')
    args.out.with_suffix('.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report),flush=True)


if __name__ == '__main__':
    main()
