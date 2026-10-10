"""Derive sound encoding/take siblings only from explicitly supplied new seeds.

Run: python contrib/verified_sound_delta_closure.py --game BLACKOP7 --seed-file logs/bo7_sound_delta_seeds44.txt --out logs/bo7_sound_delta.txt
Then, with config.toml targeting sound_asset:
confirm_list logs/bo7_sound_delta.txt --game BLACKOP7 --script contrib/verified_sound_delta_closure.py

Reads the seed CSV, verified modern sound tables and typed community/local
history, the target capture, and exclusions. Every seed must reproduce its key
under the selected game's sound policy and belong to its sound_asset pool.
Only those seeds generate candidates. Complete encoding/language tails and
take+encoding pairs must occur in that seed's exact target-held directory;
take padding is preserved. No codec, language, number, or directory is invented.
Writes candidates, a JSON report including the seed digest, and separate probe
hits under --out. Probes require normal confirmation; no findings are changed.
Adapted from sound_tail_swap_20261008-223455.py and
verified_sound_stem_variants_20261009-043204.py. Spent by unchanged explicit
seeds and target-directory conventions; this is a delta derivation, not a loop.
"""
import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent
while ROOT != ROOT.parent and not (ROOT / 'scripts/snapshot.py').is_file():
    ROOT = ROOT.parent
if not (ROOT / 'scripts/snapshot.py').is_file():
    raise SystemExit('Cannot find the solver checkout')
sys.path.insert(0, str(ROOT / 'scripts'))
import snapshot

FORMAT = re.compile(r'(?P<stem>.+)(?P<tail>\.[a-z]{1,4}\d*\.\d+\.\d+\.[a-z_]+)$')
TAKE = re.compile(r'(?P<family>.+)(?P<take>_\d{1,3})$')


def corpus(game):
    names = set(snapshot.table_names('fnv1a_xsounds_v2'))
    for top in ['all_names', 'submissions', 'findings']:
        for path in (ROOT / top).rglob('sound_asset*.txt'):
            for row in path.read_text(encoding='utf-8').splitlines():
                raw, sep, name = row.partition(',')
                if not sep or not name:
                    continue
                try:
                    key = int(raw, 16) & snapshot.ID_MASK
                except ValueError:
                    continue
                if snapshot.fnv1a(name, game, 'sound_asset') & snapshot.ID_MASK == key:
                    names.add(name.strip().lower())
    return {name for name in names if name.isascii() and name == name.strip()
            and '\n' not in name and '\r' not in name}


def read_seeds(path, game, held):
    data = path.read_bytes()
    seeds = set()
    for number, line in enumerate(data.decode('utf-8-sig').splitlines(), 1):
        if not line.strip():
            continue
        raw, sep, name = line.partition(',')
        try:
            key = int(raw, 16) & snapshot.ID_MASK
        except ValueError:
            raise SystemExit(f'{path}:{number}: seed must be a hash,name row')
        if not sep or not name or not name.isascii() or name != name.strip():
            raise SystemExit(f'{path}:{number}: invalid seed spelling')
        if snapshot.fnv1a(name, game, 'sound_asset') & snapshot.ID_MASK != key:
            raise SystemExit(f'{path}:{number}: spelling does not reproduce the sound key')
        if key not in held:
            raise SystemExit(f'{path}:{number}: seed is not held in {game} sound_asset')
        seeds.add(name)
    if not seeds:
        raise SystemExit('The explicit seed file contains no verified sound rows')
    return seeds, hashlib.sha256(data).hexdigest()


def parts(name):
    match = FORMAT.fullmatch(name)
    if match is None:
        return None
    stem, tail = match['stem'], match['tail']
    boundary = max(stem.rfind('/'), stem.rfind(chr(92)), stem.rfind('.')) + 1
    directory, base = stem[:boundary], stem[boundary:]
    take = TAKE.fullmatch(base)
    return (directory, base, tail, take['family'] if take else base,
            take['take'] if take else '')


def generate(seeds, names, held, game):
    encodings, take_endings = defaultdict(set), defaultdict(set)
    target_names = 0
    for name in names:
        parsed = parts(name)
        if parsed is None or snapshot.fnv1a(name, game, 'sound_asset') & snapshot.ID_MASK not in held:
            continue
        directory, _, tail, _, take = parsed
        target_names += 1
        encodings[directory].add(tail)
        if take:
            take_endings[directory, len(take) - 1].add(take + tail)
    candidates, controls, directories = set(), set(), set()
    parsed_seeds = numbered_seeds = 0
    for seed in seeds:
        parsed = parts(seed)
        if parsed is None:
            continue
        directory, base, _, family, take = parsed
        parsed_seeds += 1
        directories.add(directory)
        proposed = {directory + base + ending for ending in encodings[directory]}
        if take:
            numbered_seeds += 1
            proposed.update(directory + family + ending
                            for ending in take_endings[directory, len(take) - 1])
        for name in proposed:
            if name in names:
                controls.add(name)
            else:
                candidates.add(name)
    report = {'delta_seeds': len(seeds), 'parsed_seeds': parsed_seeds,
              'numbered_seeds': numbered_seeds, 'target_directories': len(directories),
              'known_target_sound_names': target_names, 'positive_controls': len(controls),
              'unseen_candidates': len(candidates)}
    return candidates, report


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--game', required=True, choices=sorted(snapshot.MODERN))
    parser.add_argument('--seed-file', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    shot = snapshot.read(ROOT / 'snapshots' / (args.game.lower() + '.ids'))
    if shot.game != args.game:
        raise SystemExit('Selected capture has the wrong game tag')
    held = set(shot.by_pool()['sound_asset'])
    seeds, seed_digest = read_seeds(args.seed_file, args.game, held)
    names = corpus(args.game)
    # Explicit verified seeds are real vocabulary even on a different contributor's checkout.
    names.update(seeds)
    candidates, report = generate(seeds, names, held, args.game)
    known = {key & snapshot.ID_MASK for key in snapshot.known_hashes(game=args.game)}
    known.update(snapshot.fnv1a(name, args.game, 'sound_asset') & snapshot.ID_MASK for name in names)
    # The startup/submit cache carries merged and open community submissions.
    claims = ROOT / 'state/claimed.txt'
    if claims.is_file():
        for row in claims.read_text(encoding='utf-8').splitlines():
            try:
                known.add(int(row, 16) & snapshot.ID_MASK)
            except ValueError:
                continue
    for path in (ROOT / 'findings').rglob('*.txt'):
        for row in path.read_text(encoding='utf-8').splitlines():
            raw, sep, _ = row.partition(',')
            if sep:
                try:
                    known.add(int(raw, 16) & snapshot.ID_MASK)
                except ValueError:
                    continue
    wanted = held - known
    hits = {name for name in candidates
            if snapshot.fnv1a(name, args.game, 'sound_asset') & snapshot.ID_MASK in wanted}
    report.update(game=args.game, seed_file=str(args.seed_file), seed_sha256=seed_digest,
                  unresolved_unclaimed_sound_ids=len(wanted), unclaimed_probe_hits=len(hits),
                  provenance=['scripts/contributed/sound_tail_swap_20261008-223455.py',
                              'scripts/contributed/verified_sound_stem_variants_20261009-043204.py'])
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(''.join(name + '\n' for name in sorted(candidates)), encoding='utf-8')
    args.out.with_suffix('.probe_hits.txt').write_text(''.join(name + '\n' for name in sorted(hits)), encoding='utf-8')
    args.out.with_suffix('.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
