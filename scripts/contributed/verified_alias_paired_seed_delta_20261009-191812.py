"""Apply independently witnessed paired token changes only to explicit alias seeds.

Run: python contrib/verified_alias_paired_seed_delta.py --game BLACKOP7 --seed-file verified_alias_names.txt --out logs/alias_pairs.txt
Then, with sound_alias selected in config.toml:
confirm_list logs/alias_pairs.txt --game BLACKOP7 --script contrib/verified_alias_paired_seed_delta.py

Every seed must independently hash to the selected capture's sound_alias pool.
Input is normalized name-only lines or verified hash,name findings rows, never
an external raw CSV. All supplied seeds are held out of training. Source-verified
alias tables and verified typed history supply the baseline; only aliases held
in this same target capture can witness rules. Application uses only the seeds.

Two nonadjacent underscore tokens change atomically at the same separation,
2..6 slots. Every other token stays fixed. Each paired substitution needs at
least three distinct otherwise-identical baseline sibling frames; both changed
tokens must differ. Frames with 2..24 observed fillers qualify. Eligible names
have 4..18 tokens. These limits and the relation come from the existing
paired_animation_rules_20260922-124650.py, applied here to the alias vocabulary.
Unlike alias_slotswap2_20261008-215933.py, independent slot alternatives are
never multiplied. Alias source verification follows verified_alias_file_prefixes.

Writes candidates plus JSON provenance/counts and separate unclaimed probe
matches. Probes exclude authoritative table keys, all community/findings keys,
open-PR claims, and verified alias names; they still require normal confirmation.
No findings/config changes or submissions. Uses shared game hash/pool policies,
63-bit lookup, and name-only output so confirm_list retains the proper full
modern alias output hash. Spent by an unchanged explicit seed set and unchanged
baseline paired rules; this is a delta derivation, not a global rerun or loop.
Initial BO7 measurement: 3,353 held-out seeds, 29,352 candidates, 2,676 probes.
"""
import argparse
from collections import Counter, defaultdict
import hashlib
import itertools
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
while ROOT != ROOT.parent and not (ROOT / 'scripts/snapshot.py').is_file():
    ROOT = ROOT.parent
if not (ROOT / 'scripts/snapshot.py').is_file():
    raise SystemExit('Cannot find the solver checkout')
sys.path.insert(0, str(ROOT / 'scripts'))
import snapshot


def corpus(game):
    names = set(snapshot.table_names('fnv1a_soundbanks_aliases_v2',
                                     'fnv1a_soundbanks_aliases'))
    for top in ['all_names', 'submissions', 'findings']:
        for path in (ROOT / top).rglob('sound_alias*.txt'):
            for row in path.read_text(encoding='utf-8').splitlines():
                raw, sep, name = row.partition(',')
                if not sep or not name:
                    continue
                try:
                    key = int(raw, 16) & snapshot.ID_MASK
                except ValueError:
                    continue
                if snapshot.fnv1a(name, game, 'sound_alias') & snapshot.ID_MASK == key:
                    names.add(name.strip().lower())
    return {n for n in names if n.isascii() and '\n' not in n and '\r' not in n}


def read_seeds(path, game, held):
    data = path.read_bytes()
    seeds = set()
    for number, row in enumerate(data.decode('utf-8-sig').splitlines(), 1):
        raw, sep, name = row.partition(',')
        if sep:
            try:
                key = int(raw, 16) & snapshot.ID_MASK
            except ValueError:
                raise SystemExit(f'Seed line {number} is not a name or hash,name row')
            if snapshot.fnv1a(name, game, 'sound_alias') & snapshot.ID_MASK != key:
                raise SystemExit(f'Seed line {number} does not reproduce its stored key')
        else:
            name = row
        if not name or not name.isascii() or name != name.strip().lower() or ',' in name or any(ord(c) < 32 or ord(c) == 127 for c in name):
            raise SystemExit(f'Seed line {number} is not a normalized ASCII alias')
        if snapshot.fnv1a(name, game, 'sound_alias') & snapshot.ID_MASK not in held:
            raise SystemExit(f'Seed line {number} is not held in the selected alias pool')
        seeds.add(name)
    if not seeds:
        raise SystemExit('Seed file is empty')
    return seeds, hashlib.sha256(data).hexdigest()


def derive(baseline, seeds, aliases):
    rows = [tuple(n.split('_')) for n in sorted(baseline) if 4 <= len(n.split('_')) <= 18]
    seed_rows = [tuple(n.split('_')) for n in sorted(seeds) if 4 <= len(n.split('_')) <= 18]
    candidates, reports = set(), []
    for gap in range(2, 7):
        groups = defaultdict(set)
        for row in rows:
            for i in range(len(row) - gap):
                j = i + gap
                groups[row[:i], row[i+1:j], row[j+1:]].add((row[i], row[j]))
        support = Counter()
        for values in groups.values():
            if 2 <= len(values) <= 24:
                for a, b in itertools.combinations(sorted(values), 2):
                    if a[0] != b[0] and a[1] != b[1]:
                        support[a, b] += 1
        rules = defaultdict(set)
        for (a, b), count in support.items():
            if count >= 3:
                rules[a].add(b)
                rules[b].add(a)
        controls, before = 0, len(candidates)
        for row in seed_rows:
            for i in range(len(row) - gap):
                j = i + gap
                for a, b in rules.get((row[i], row[j]), ()):
                    changed = list(row)
                    changed[i], changed[j] = a, b
                    candidate = '_'.join(changed)
                    if candidate in aliases:
                        controls += 1
                    else:
                        candidates.add(candidate)
        reports.append({'gap': gap, 'baseline_frames': len(groups),
                        'supported_directed_rules': sum(map(len, rules.values())),
                        'known_controls_from_seed_applications': controls,
                        'additional_candidates': len(candidates) - before})
    return candidates, reports, len(rows), len(seed_rows)


def excluded_keys(game, aliases):
    known = {key & snapshot.ID_MASK for key in snapshot.known_hashes(game=game)}
    for top in ['all_names', 'submissions', 'findings']:
        for path in (ROOT / top).rglob('*.txt'):
            for row in path.read_text(encoding='utf-8', errors='replace').splitlines():
                raw, sep, _ = row.partition(',')
                if sep:
                    try:
                        known.add(int(raw.strip(), 16) & snapshot.ID_MASK)
                    except ValueError:
                        pass
    claims = ROOT / 'state/claimed.txt'
    if claims.is_file():
        for raw in claims.read_text(encoding='utf-8').splitlines():
            try:
                known.add(int(raw, 16) & snapshot.ID_MASK)
            except ValueError:
                pass
    known.update(snapshot.fnv1a(n, game, 'sound_alias') & snapshot.ID_MASK for n in aliases)
    return known


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--game', type=str.upper,
                        choices=sorted(snapshot.MODERN | {'BLKOPS04', 'BLKOPSCW'}), required=True)
    parser.add_argument('--seed-file', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    shot = snapshot.read(ROOT / 'snapshots' / (args.game.lower() + '.ids'))
    if shot.game != args.game:
        parser.error('Capture tag does not match selected game')
    held = set(shot.by_pool()['sound_alias'])
    seeds, digest = read_seeds(args.seed_file, args.game, held)
    aliases = corpus(args.game) | seeds
    baseline = {n for n in aliases - seeds
                if snapshot.fnv1a(n, args.game, 'sound_alias') & snapshot.ID_MASK in held}
    candidates, gaps, train_count, apply_count = derive(baseline, seeds, aliases)
    wanted = held - excluded_keys(args.game, aliases)
    hits = {n for n in candidates if snapshot.fnv1a(n, args.game, 'sound_alias') & snapshot.ID_MASK in wanted}
    report = {'game': args.game, 'seed_file': args.seed_file.name, 'seed_sha256': digest,
              'verified_delta_seeds': len(seeds), 'baseline_held_aliases': len(baseline),
              'eligible_training_aliases': train_count, 'eligible_application_seeds': apply_count,
              'all_seeds_held_out_of_training': not bool(baseline & seeds),
              'delta_candidates': len(candidates), 'unresolved_unclaimed_alias_matches': len(hits),
              'unresolved_alias_ids': len(wanted), 'gaps': gaps}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(''.join(n + '\n' for n in sorted(candidates)), encoding='utf-8')
    args.out.with_suffix('.probe_hits.txt').write_text(''.join(n + '\n' for n in sorted(hits)), encoding='utf-8')
    args.out.with_suffix('.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report), flush=True)


if __name__ == '__main__':
    main()
