"""Transfer independently witnessed complete interior blocks between held aliases.

Example:
  python contrib/verified_alias_interior_blocks.py --game BLACKOP7 \
      --baseline-file independently_sourced_aliases.txt \
      --application-file held_application_aliases.txt \
      --prior-candidate-file previous_candidates.txt --out logs/alias_blocks.txt
  confirm_list logs/alias_blocks.txt --game BLACKOP7 \
      --script contrib/verified_alias_interior_blocks.py \
      --label "independently witnessed complete alias interior blocks"

Select ONLY sound_alias in the official confirmer. This generator does not
confirm, modify findings/configuration, or submit. Probe matches require normal
confirmation and submission, which preserve modern aliases' full 64-bit output.

The explicit immutable baseline must contain independently sourced and verified
names. Generated descendants may be application seeds, but NEVER train rules.
Every supplied baseline/application name must hash into the selected alias pool.
Both original and replacement blocks contain one to three underscore tokens.
The complete prefix/suffix frame must hold both spellings. Three distinct
full-name pairs spanning at least six distinct names must witness each rule,
with identical immediate left/right anchors. Repeated token positions in the
same two names count once. Frames with more than 24 blocks are excluded.

Only canonical minimal replacements qualify: the block's first and last tokens
must both change. Single-token edits and same-width nonadjacent two-token edits
are omitted; the latter are already covered by the frozen paired-token method.
Unchanged anchors transfer the complete block, never a product of slot alphabets.
Apply once to the explicit application file; there is no automatic traversal.
Subtract every provided prior candidate file before probing. Current raw table
keys, all-game history/findings, and open claims exclude already resolved keys.

Initial BO7 measurement: 128,720 independent source aliases and 134,185 held
applications supported 71,936 directed rules; 97,750 known controls, 6,768 prior
candidates removed, 557,984 unseen candidates, and 514 unclaimed alias matches.
Spent by: unchanged baseline/application/prior files (all recorded with SHA256).
Do not treat the resulting descendants as independent witnesses for retraining.
"""
import argparse
from collections import Counter, defaultdict
import hashlib
import itertools
import json
from pathlib import Path
import sys

ROOT = next((p for p in [Path.cwd(), *Path(__file__).resolve().parents]
             if (p/'scripts/snapshot.py').is_file()), None)
if ROOT is None:
    raise SystemExit('Run inside a solver checkout')
sys.path.insert(0, str(ROOT/'scripts'))
import snapshot


def normalized(name):
    return (bool(name) and name.isascii() and name == name.strip().lower()
            and ',' not in name and not any(ord(c) < 32 or ord(c) == 127 for c in name))


def read_names(path, game, held=None):
    data = path.read_bytes()
    names = set()
    for number, row in enumerate(data.decode('utf-8-sig').splitlines(), 1):
        raw, sep, name = row.partition(',')
        if not sep:
            name = row
        if not normalized(name):
            raise ValueError(f'{path.name}:{number}: expected normalized ASCII alias')
        full = snapshot.fnv1a(name, game, 'sound_alias')
        if sep:
            try:
                key = int(raw, 16) & snapshot.ID_MASK
            except ValueError:
                raise ValueError(f'{path.name}:{number}: invalid supplied key')
            if full & snapshot.ID_MASK != key:
                raise ValueError(f'{path.name}:{number}: supplied key does not reproduce')
        if held is not None and full & snapshot.ID_MASK not in held:
            raise ValueError(f'{path.name}:{number}: not held in selected sound_alias pool')
        names.add(name)
    if not names:
        raise ValueError(f'{path.name}: empty input')
    return names, {'file':path.name, 'names':len(names), 'sha256':hashlib.sha256(data).hexdigest()}


def corpus(game):
    names = set(snapshot.table_names('fnv1a_soundbanks_aliases_v2', 'fnv1a_soundbanks_aliases'))
    for top in ('all_names', 'submissions', 'findings'):
        for path in (ROOT/top).rglob('sound_alias*.txt'):
            for row in path.read_text(encoding='utf-8', errors='replace').splitlines():
                raw, sep, name = row.partition(',')
                if not sep or not name:
                    continue
                try:
                    key = int(raw, 16) & snapshot.ID_MASK
                except ValueError:
                    continue
                if snapshot.fnv1a(name, game, 'sound_alias') & snapshot.ID_MASK == key:
                    names.add(name.strip().lower())
    return {name for name in names if normalized(name)}


def excluded_keys(game, aliases):
    known = {key & snapshot.ID_MASK for key in snapshot.known_hashes(game=game)}
    # Keep stored keys even when an export's display spelling is unrestorable.
    paths = list(Path(snapshot.settings.tables_csv()).glob('*.csv'))
    for top in ('all_names', 'submissions', 'findings'):
        paths.extend((ROOT/top).rglob('*.txt'))
    for path in paths:
        with path.open(encoding='utf-8', errors='replace') as handle:
            for row in handle:
                raw, sep, _ = row.partition(',')
                if sep:
                    try:
                        known.add(int(raw.strip(), 16) & snapshot.ID_MASK)
                    except ValueError:
                        pass
    claims = ROOT/'state/claimed.txt'
    if claims.is_file():
        for row in claims.read_text(encoding='utf-8').splitlines():
            try:
                known.add(int(row, 16) & snapshot.ID_MASK)
            except ValueError:
                pass
    known.update(snapshot.fnv1a(n, game, 'sound_alias') & snapshot.ID_MASK for n in aliases)
    return known


def tokens(name):
    row = tuple(name.split('_'))
    return row if 4 <= len(row) <= 18 and all(t.isascii() and t.isalnum() for t in row) else ()


def cuts(row):
    for width in (1, 2, 3):
        for pos in range(1, len(row)-width):
            yield row[:pos], row[pos:pos+width], row[pos+width:]


def novel(left, right):
    if left[0] == right[0] or left[-1] == right[-1]:
        return False
    if len(left) != len(right):
        return True
    changes = [i for i, (a, b) in enumerate(zip(left, right)) if a != b]
    return len(changes) >= 2 and not (len(changes) == 2 and changes[1]-changes[0] >= 2)


def learn(baseline):
    frames = defaultdict(set)
    for name in baseline:
        for prefix, block, suffix in cuts(tokens(name)):
            frames[prefix, suffix].add(block)
    supports = defaultdict(set)
    ignored_frames = 0
    for (prefix, suffix), blocks in frames.items():
        if len(blocks) > 24:
            ignored_frames += 1
            continue
        anchors = prefix[-1], suffix[0]
        for left, right in itertools.combinations(sorted(blocks), 2):
            if novel(left, right):
                pair = tuple(sorted(('_'.join(prefix+left+suffix), '_'.join(prefix+right+suffix))))
                supports[anchors,left,right].add(pair)
    rules = defaultdict(dict)
    profiles = Counter()
    for (anchors,left,right), pairs in supports.items():
        if len(pairs) >= 3 and len({n for pair in pairs for n in pair}) >= 6:
            witnesses = sorted(pairs)
            rules[anchors,left][right] = witnesses
            rules[anchors,right][left] = witnesses
            profiles[f'{len(left)}<->{len(right)}'] += 1
    return rules, {'frames':len(frames), 'wide_frames_skipped':ignored_frames,
        'supported_directed_rules':sum(map(len,rules.values())), 'rule_profiles':dict(profiles)}


def apply_once(rules, application, aliases, prior, cap):
    candidates, controls, removed, sources = set(), set(), set(), set()
    provenance = {}
    for name in sorted(application):
        for prefix, block, suffix in cuts(tokens(name)):
            anchors = prefix[-1], suffix[0]
            for replacement, witnesses in rules.get((anchors,block), {}).items():
                candidate = '_'.join(prefix+replacement+suffix)
                if candidate in aliases:
                    controls.add(candidate)
                    continue
                if candidate in prior:
                    removed.add(candidate)
                    continue
                if len(candidates) >= cap and candidate not in candidates:
                    raise ValueError('Candidate cap exceeded; no output was written')
                candidates.add(candidate)
                sources.add(name)
                provenance.setdefault(candidate, {'source':name, 'position':len(prefix),
                    'old':block, 'new':replacement, 'anchors':anchors,
                    'independent_name_pair_witnesses':len(witnesses), 'witness_pairs':witnesses[:3]})
    return candidates, provenance, {'known_reconstruction_controls':len(controls),
        'prior_candidates_removed':len(removed), 'sources_with_unseen_candidates':len(sources),
        'unseen_candidates':len(candidates)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--game', type=str.upper, required=True,
                        choices=sorted(snapshot.MODERN|{'BLKOPS04','BLKOPSCW'}))
    parser.add_argument('--baseline-file', type=Path, required=True)
    parser.add_argument('--application-file', type=Path, required=True)
    parser.add_argument('--prior-candidate-file', type=Path, action='append', default=[])
    parser.add_argument('--max-candidates', type=int, default=1000000)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    if args.max_candidates < 1:
        parser.error('--max-candidates must be positive')
    shot = snapshot.read(ROOT/'snapshots'/(args.game.lower()+'.ids'))
    if shot.game != args.game:
        parser.error('Capture game differs from selected game')
    held = set(shot.by_pool()['sound_alias'])
    baseline, base_meta = read_names(args.baseline_file, args.game, held)
    application, app_meta = read_names(args.application_file, args.game, held)
    aliases = corpus(args.game) | baseline | application
    prior, prior_meta = set(), []
    for path in args.prior_candidate_file:
        names, meta = read_names(path, args.game)
        prior.update(names)
        prior_meta.append(meta)
    rules, report = learn(baseline)
    candidates, provenance, measured = apply_once(rules, application, aliases, prior, args.max_candidates)
    wanted = held-excluded_keys(args.game, aliases)
    hits = {}
    for name in sorted(candidates):
        key = snapshot.fnv1a(name,args.game,'sound_alias') & snapshot.ID_MASK
        if key in wanted:
            hits.setdefault(key,name)
    report.update(measured)
    report.update(game=args.game, baseline=base_meta, application=app_meta, prior=prior_meta,
        application_only_descendants=len(application-baseline), unresolved_alias_keys=len(wanted),
        unclaimed_capture_matches=len(hits), max_candidates=args.max_candidates)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(''.join(n+'\n' for n in sorted(candidates)), encoding='utf-8')
    args.out.with_suffix('.probe_hits.txt').write_text(''.join(n+'\n' for n in sorted(hits.values())),encoding='utf-8')
    args.out.with_suffix('.provenance.json').write_text(json.dumps({n:provenance[n] for n in sorted(hits.values())},indent=2)+'\n',encoding='utf-8')
    args.out.with_suffix('.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report),flush=True)


if __name__ == '__main__':
    main()
