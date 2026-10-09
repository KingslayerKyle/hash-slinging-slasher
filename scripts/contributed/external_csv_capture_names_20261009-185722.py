"""Validate raw CSV names against one selected game's searchable capture pool.

Usage: python contrib/external_csv_capture_names.py --csv candidate.csv --game BLACKOP7 --kind xanim
Pipe stdout to confirm_list with the same --game, this file as --script, and
the intended pool selected in config.toml. This script never confirms anything.

Only the CSV's name column supplies candidate bytes: hash, key60, func, label,
and every other column are ignored. Strict UTF-8 CSV parsing rejects malformed
rows and control characters. Names are stripped, lowercased, deduplicated, and
slash-folded except for BO4 literal sound files. Shared snapshot hash helpers
and the capture's own pool map establish membership at 63 bits; supplied keys
are never evidence. Modern embedded-name models and unsearchable pools fail.

Direct strings only: no guessed hash policy, metadata-based type assignment,
or recombination. Repeated headers are harmless literal name candidates and
must pass the same capture check. Output includes known names; confirm_list
must apply current table/community/open-PR exclusions before counting finds.
The stderr JSON records source basename, SHA-256, and extraction counts.

Provenance: direct-name capture validation of an external name-column export;
spent by an unchanged source, capture, and shared hash/pool policies. No source
data or user-specific path is embedded in this reusable extractor.
"""
import argparse
import csv
import hashlib
import io
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

GAMES = sorted(snapshot.MODERN | {'BLKOPS04', 'BLKOPSCW'})


def read_names(path):
    data = path.read_bytes()
    reader = csv.DictReader(io.StringIO(data.decode('utf-8-sig'), newline=''), strict=True)
    fields = reader.fieldnames
    if not fields or fields.count('name') != 1 or len(fields) != len(set(fields)):
        raise ValueError('CSV requires exactly one name column and unique headers')
    names = set()
    rows = empty = outer = 0
    for row in reader:
        rows += 1
        if None in row or any(value is None for value in row.values()):
            raise ValueError(f'Malformed CSV row ending at line {reader.line_num}')
        raw = row['name']
        if any(ord(char) < 32 or ord(char) == 127 for char in raw):
            raise ValueError(f'Control character in name at line {reader.line_num}')
        outer += raw != raw.strip()
        name = raw.strip().lower()
        if not name:
            empty += 1
            continue
        names.add(name)
    return names, {
        'source_basename': path.name,
        'source_sha256': hashlib.sha256(data).hexdigest(),
        'source_bytes': len(data),
        'rows': rows,
        'empty_names': empty,
        'outer_whitespace_rows': outer,
        'distinct_normalized_names_before_slash_policy': len(names),
        'source_hash_columns_used': False,
    }


def capture_matches(names, game, kind, held):
    if kind not in snapshot.IMPORTANT or not snapshot.searchable(game, kind):
        raise ValueError(f'{game} {kind} is not an allowed searchable pool')
    literal = game == 'BLKOPS04' and kind == 'sound_asset'
    normalized = names if literal else {name.replace('\\', '/') for name in names}
    return sorted(name for name in normalized
                  if ((snapshot.fnv1a_nofold(name) if literal else
                       snapshot.fnv1a(name, game, kind)) & snapshot.ID_MASK) in held)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--csv', type=Path, required=True)
    parser.add_argument('--game', type=str.upper, choices=GAMES, required=True)
    parser.add_argument('--kind', choices=sorted(snapshot.IMPORTANT), required=True)
    args = parser.parse_args()
    if not snapshot.searchable(args.game, args.kind):
        parser.error('Modern models carry embedded names and are excluded')
    paths = [Path(path) for path in snapshot.snapshots()
             if Path(path).stem.lower() == args.game.lower()]
    if len(paths) != 1:
        parser.error('Expected exactly one canonical snapshot for the selected game')
    shot = snapshot.read(paths[0])
    if shot.game != args.game:
        parser.error('Snapshot tag does not match the selected game')
    pools = shot.by_pool()
    if args.kind not in pools:
        parser.error('The selected capture has no requested pool')
    try:
        names, report = read_names(args.csv)
        matches = capture_matches(names, args.game, args.kind, set(pools[args.kind]))
    except (ValueError, UnicodeError, csv.Error) as error:
        parser.error(str(error))
    report.update(game=args.game, kind=args.kind, capture=paths[0].name,
                  capture_matches=len(matches), exclusions_applied=False)
    print(json.dumps(report, sort_keys=True), file=sys.stderr)
    for name in matches:
        print(name)


if __name__ == '__main__':
    main()
