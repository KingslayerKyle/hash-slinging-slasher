"""Apply frozen alias-pair rules once to explicitly selected descendant seeds.

Run: python contrib/verified_alias_paired_continuation.py --game BLACKOP7 --seed-file descendant_aliases.txt --baseline-file original_baseline.txt --training-exclude-file original_seeds.txt --exclude-file original_candidates.txt --out logs/alias_continuation.txt
Then select sound_alias in config.toml and confirm_list the output with this
file as --script. This tool only generates and probes; it never confirms.

Reuses verified_alias_paired_seed_delta_20261009-191812.py without changing it.
The exact submitted companion belongs in scripts/contributed; its unchanged
contrib staging copy is accepted before that submission is pulled locally.
It supplies shared verified alias readers, game-specific hashing, atomic paired
rules at distance2..6 witnessed in at least3 distinct baseline frames, and full
table/history/findings/claim exclusions. No independent slot cross product.

--baseline-file freezes the training names. Every baseline, source, and training
exclusion name must independently reproduce a selected-game sound_alias ID.
Both current seeds and all --training-exclude-file names MUST be absent from
the frozen baseline; a contaminated baseline fails rather than silently adding
descendants to training. Only --seed-file names are application seeds.
--exclude-file may repeat and removes prior name-only candidate files exactly.

Writes candidates, provenance JSON with input digests, and separate probe hits.
All inputs are normalized name-only lists or (except prior candidates) verified
hash,name findings rows. Raw external CSVs are not accepted. Name-only output
lets the official confirmer retain all64 modern alias hash bits. This is one
explicit continuation with unchanged rules, not an automatic snowball or loop.
Spent by the frozen baseline, explicit seeds, and prior tested candidate sets.
Initial continuation:2677 seeds,41811 new candidates,1180 unclaimed probes.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
while ROOT != ROOT.parent and not (ROOT / 'scripts/snapshot.py').is_file():
    ROOT = ROOT.parent
if not (ROOT / 'scripts/snapshot.py').is_file():
    raise SystemExit('Cannot find the solver checkout')
COMPANION = ROOT / 'scripts/contributed/verified_alias_paired_seed_delta_20261009-191812.py'
if not COMPANION.is_file():
    COMPANION = ROOT / 'contrib/verified_alias_paired_seed_delta.py'
if not COMPANION.is_file():
    raise SystemExit('Missing the submitted verified_alias_paired_seed_delta_20261009-191812.py companion')
companion_digest = hashlib.sha256(COMPANION.read_text(encoding='utf-8').encode('utf-8')).hexdigest()
if companion_digest != 'e0db3f60413e5e24b59d616aac2c824cd88ae59131cda485d571d793bc9d32da':
    raise SystemExit('Alias-pair companion differs from the reviewed original; refresh its exact submitted version')
spec = importlib.util.spec_from_file_location('alias_pair_baseline_method', COMPANION)
method = importlib.util.module_from_spec(spec)
spec.loader.exec_module(method)
snapshot = method.snapshot


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--game', type=str.upper,
                        choices=sorted(snapshot.MODERN | {'BLKOPS04', 'BLKOPSCW'}), required=True)
    parser.add_argument('--seed-file', type=Path, required=True)
    parser.add_argument('--baseline-file', type=Path, required=True)
    parser.add_argument('--training-exclude-file', type=Path, action='append', required=True)
    parser.add_argument('--exclude-file', type=Path, action='append', required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    shot = snapshot.read(ROOT / 'snapshots' / (args.game.lower() + '.ids'))
    if shot.game != args.game:
        parser.error('Capture tag does not match the selected game')
    held = set(shot.by_pool()['sound_alias'])
    seeds, seed_digest = method.read_seeds(args.seed_file, args.game, held)
    baseline, baseline_digest = method.read_seeds(args.baseline_file, args.game, held)
    training_excluded, training_sources = set(), []
    for path in args.training_exclude_file:
        names, digest = method.read_seeds(path, args.game, held)
        training_excluded.update(names)
        training_sources.append({'file': path.name, 'sha256': digest, 'names': len(names)})
    if baseline & (seeds | training_excluded):
        parser.error('Frozen baseline contains a source or descendant seed held out of training')
    aliases = method.corpus(args.game) | baseline | seeds | training_excluded
    candidates, gaps, train_count, apply_count = method.derive(baseline, seeds, aliases)
    raw_count = len(candidates)
    prior_sources = []
    for path in args.exclude_file:
        data = path.read_bytes()
        prior = set(data.decode('utf-8-sig').splitlines())
        if any(not n or n != n.strip().lower() or ',' in n or not n.isascii()
               or any(ord(c) < 32 or ord(c) == 127 for c in n) for n in prior):
            parser.error('Prior candidate files must contain normalized ASCII names only')
        removed = len(candidates & prior)
        candidates -= prior
        prior_sources.append({'file': path.name, 'sha256': hashlib.sha256(data).hexdigest(),
                              'names': len(prior), 'overlap_removed': removed})
    wanted = held - method.excluded_keys(args.game, aliases)
    hits = {n for n in candidates if snapshot.fnv1a(n, args.game, 'sound_alias') & snapshot.ID_MASK in wanted}
    report = {'game': args.game, 'seed_file': args.seed_file.name, 'seed_sha256': seed_digest,
              'verified_application_seeds': len(seeds), 'baseline_file': args.baseline_file.name,
              'baseline_sha256': baseline_digest, 'baseline_held_aliases': len(baseline),
              'training_exclude_files': training_sources, 'all_explicit_seeds_held_out': True,
              'eligible_training_aliases': train_count, 'eligible_application_seeds': apply_count,
              'prior_candidate_files': prior_sources, 'raw_delta_candidates': raw_count,
              'prior_candidates_removed': raw_count - len(candidates),
              'new_candidates': len(candidates), 'unresolved_unclaimed_alias_matches': len(hits),
              'gaps': gaps}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(''.join(n + '\n' for n in sorted(candidates)), encoding='utf-8')
    args.out.with_suffix('.probe_hits.txt').write_text(''.join(n + '\n' for n in sorted(hits)), encoding='utf-8')
    args.out.with_suffix('.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report), flush=True)


if __name__ == '__main__':
    main()
