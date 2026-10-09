"""Infer modern sound files by reversing witnessed alias-to-file prefix changes.

Run: python contrib/verified_alias_file_prefixes.py --game BLACKOP7 > candidates.txt
Then, with config.toml targeting sound_asset:
confirm_list candidates.txt --game BLACKOP7 --script contrib/verified_alias_file_prefixes.py

Reads source-verified sound and alias tables, verified local/merged names, and the
selected capture. Each prefix rewrite needs three distinct shared bodies in one
directory. Common body tokens remain anchors. Apply these contextual rewrites to
target-held aliases, retaining that directory's recorded take/encoding endings.
This complements unchanged-alias directory borrowing and file-to-alias rewrites.
Only absent target file families are emitted, to stdout; no findings are written.
--measure checks the generated candidates against unresolved, unclaimed file IDs.
Spent by unchanged target aliases, witnessed prefix rules, and directory endings.
"""
import argparse
from collections import defaultdict
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent
while ROOT != ROOT.parent and not (ROOT / 'scripts/snapshot.py').is_file():
    ROOT = ROOT.parent
if not (ROOT / 'scripts/snapshot.py').is_file():
    raise SystemExit('Run from a checkout containing scripts/snapshot.py')
sys.path.insert(0, str(ROOT / 'scripts'))
import snapshot

FORMAT = re.compile(r'(?P<stem>.+)(?P<tail>\.[a-z]{1,4}\d*\.\d+\.\d+\.[a-z_]+)$')
TAKE = re.compile(r'(?P<family>.+)(?P<take>_\d{1,3})$')


def corpus(kind, game):
    tables = ['fnv1a_xsounds_v2'] if kind == 'sound_asset' else [
        'fnv1a_soundbanks_aliases_v2', 'fnv1a_soundbanks_aliases']
    names = set(snapshot.table_names(*tables))
    for top in ['all_names', 'submissions', 'findings']:
        for path in (ROOT / top).rglob(kind + '*.txt'):
            for row in path.read_text(encoding='utf-8').splitlines():
                raw, sep, name = row.partition(',')
                if not sep or not name:
                    continue
                try:
                    key = int(raw, 16) & snapshot.ID_MASK
                except ValueError:
                    continue
                if snapshot.fnv1a(name, game, kind) & snapshot.ID_MASK == key:
                    names.add(name.strip().lower())
    return {name for name in names if name.isascii() and '\n' not in name and '\r' not in name}


def splits(name):
    words = name.split('_')
    for count in range(min(5, len(words) - 3) + 1):
        yield ('_'.join(words[:count]) + '_' if count else ''), '_'.join(words[count:])


def build(sounds, aliases, file_ids, alias_ids, game):
    families, endings, bodies = set(), defaultdict(set), defaultdict(set)
    for name in sounds:
        match = FORMAT.fullmatch(name)
        if not match or snapshot.fnv1a(name, game, 'sound_asset') & snapshot.ID_MASK not in file_ids:
            continue
        stem = match['stem']
        boundary = max(stem.rfind('/'), stem.rfind(chr(92)), stem.rfind('.')) + 1
        directory, base = stem[:boundary], stem[boundary:]
        take = TAKE.fullmatch(base)
        family = take['family'] if take else base
        families.add((directory, family))
        endings[directory].add((take['take'] if take else '') + match['tail'])
    for directory, family in families:
        for prefix, body in splits(family):
            bodies[body].add((directory, prefix))
    target_aliases = {name for name in aliases if not any(c in name for c in '/.\\')
                      and snapshot.fnv1a(name, game, 'sound_alias') & snapshot.ID_MASK in alias_ids}
    witnesses = defaultdict(set)
    for alias in target_aliases:
        for alias_prefix, body in splits(alias):
            for directory, file_prefix in bodies.get(body, ()):
                if file_prefix != alias_prefix:
                    witnesses[alias_prefix, directory, file_prefix].add(body)
    rules = defaultdict(list)
    for (alias_prefix, directory, file_prefix), witnessed in witnesses.items():
        if len(witnessed) >= 3:
            anchors = set.intersection(*(set(body.split('_')) for body in witnessed))
            rules[alias_prefix].append((directory, file_prefix, anchors))
    groups, controls = defaultdict(set), set()
    for alias in target_aliases:
        for alias_prefix, body in splits(alias):
            for directory, file_prefix, anchors in rules.get(alias_prefix, ()):
                if not anchors <= set(body.split('_')):
                    continue
                family = file_prefix + body
                if (directory, family) in families:
                    controls.add((directory, family))
                else:
                    groups[directory].add(family)
    report = {'game': game, 'target_held_aliases': len(target_aliases),
              'witnessed_prefix_rules': sum(map(len, rules.values())),
              'held_control_file_families': len(controls), 'directories': len(groups),
              'inferred_missing_file_families': sum(map(len, groups.values())),
              'candidate_product': sum(len(stems) * len(endings[d]) for d, stems in groups.items())}
    return groups, endings, report


def candidates(groups, endings, sounds):
    for directory, families in sorted(groups.items()):
        for family in sorted(families):
            for ending in sorted(endings[directory]):
                name = directory + family + ending
                if name not in sounds:
                    yield name


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--game', required=True, choices=sorted(snapshot.MODERN))
    parser.add_argument('--measure', action='store_true')
    args = parser.parse_args()
    shot = snapshot.read(ROOT / 'snapshots' / (args.game.lower() + '.ids'))
    assert shot.game == args.game
    pools = shot.by_pool()
    sounds, aliases = corpus('sound_asset', args.game), corpus('sound_alias', args.game)
    groups, endings, report = build(sounds, aliases, set(pools['sound_asset']),
                                    set(pools['sound_alias']), args.game)
    emitted = 0
    if args.measure:
        known = {key & snapshot.ID_MASK for key in snapshot.known_hashes(game=args.game)}
        known.update(snapshot.fnv1a(name, args.game, 'sound_asset') & snapshot.ID_MASK for name in sounds)
        claims = ROOT / 'state/claimed.txt'
        if claims.is_file():
            for row in claims.read_text(encoding='utf-8').splitlines():
                try:
                    known.add(int(row, 16) & snapshot.ID_MASK)
                except ValueError:
                    continue
        wanted = set(pools['sound_asset']) - known
        matches = set()
        for name in candidates(groups, endings, sounds):
            emitted += 1
            if snapshot.fnv1a(name, args.game, 'sound_asset') & snapshot.ID_MASK in wanted:
                matches.add(name)
        report['unresolved_unclaimed_sound_ids'] = len(wanted)
        report['unclaimed_typed_matches'] = len(matches)
    else:
        for name in candidates(groups, endings, sounds):
            print(name)
            emitted += 1
    report['unseen_candidates'] = emitted
    print(json.dumps(report), file=sys.stderr)


if __name__ == '__main__':
    main()
