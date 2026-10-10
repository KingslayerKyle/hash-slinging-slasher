"""Learn alias-to-file prefix changes witnessed by target-held sound families.

Each rule requires three distinct shared underscore bodies, rather than three
codec or take variants of one file. Common body tokens remain mandatory when
applying a rule, preserving directory-specific weapon or character anchors.
Only verified original spellings and target-held aliases/files seed rules.
Use the normal sound_asset confirmation and submission workflow on the output.
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
    ROOT = Path.cwd()
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
    return {n for n in names if n.isascii() and '\n' not in n and '\r' not in n}


def splits(name):
    """Change at most five leading tokens; keep at least three body tokens."""
    parts = name.split('_')
    for cut in range(min(5, len(parts) - 3) + 1):
        yield ('_'.join(parts[:cut]) + '_' if cut else ''), '_'.join(parts[cut:])


def build(sounds, aliases, file_ids, alias_ids, game):
    families = set()
    endings = defaultdict(set)
    file_bodies = defaultdict(set)
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
            file_bodies[body].add((directory, prefix))
    held_aliases = {n for n in aliases if not any(c in n for c in '/.\\')
                    and snapshot.fnv1a(n, game, 'sound_alias') & snapshot.ID_MASK in alias_ids}
    witnesses = defaultdict(set)
    for alias in held_aliases:
        for alias_prefix, body in splits(alias):
            for directory, file_prefix in file_bodies.get(body, ()):
                if file_prefix != alias_prefix:
                    witnesses[(alias_prefix, directory, file_prefix)].add(body)
    rules = defaultdict(list)
    support = 0
    for (alias_prefix, directory, file_prefix), bodies in sorted(witnesses.items()):
        if len(bodies) < 3:
            continue
        common = set.intersection(*(set(body.split('_')) for body in bodies))
        rules[alias_prefix].append((directory, file_prefix, common))
        support += len(bodies)
    generated = set()
    held_controls = set()
    for alias in held_aliases:
        for alias_prefix, body in splits(alias):
            tokens = set(body.split('_'))
            for directory, file_prefix, common in rules.get(alias_prefix, ()):
                if not common <= tokens:
                    continue
                pair = (directory, file_prefix + body)
                if pair in families:
                    held_controls.add(pair)
                else:
                    generated.add(pair)
    groups = sorted(generated)
    report = {'game': game, 'target_held_aliases': len(held_aliases),
              'target_file_families': len(families),
              'witnessed_prefix_rules': sum(map(len, rules.values())),
              'distinct_body_support_total': support,
              'held_control_families_reconstructed': len(held_controls),
              'new_candidate_families': len(groups),
              'candidate_product': sum(len(endings[d]) for d, _ in groups)}
    return groups, endings, report


def candidates(groups, endings, known):
    for directory, family in groups:
        for ending in sorted(endings[directory]):
            name = directory + family + ending
            if name not in known:
                yield name


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--game', required=True, choices=sorted(snapshot.MODERN))
    parser.add_argument('--kind', choices=['sound_asset'], default='sound_asset')
    parser.add_argument('--measure', action='store_true')
    args = parser.parse_args()
    shot = snapshot.read(ROOT / 'snapshots' / (args.game.lower() + '.ids'))
    assert shot.game == args.game
    pools = shot.by_pool()
    sounds, aliases = corpus('sound_asset', args.game), corpus('sound_alias', args.game)
    groups, endings, report = build(sounds, aliases, set(pools['sound_asset']),
                                    set(pools['sound_alias']), args.game)
    print(json.dumps(report), file=sys.stderr)
    if args.measure:
        return
    count = 0
    for name in candidates(groups, endings, sounds):
        print(name)
        count += 1
    print(json.dumps({'unseen_candidates_emitted': count}), file=sys.stderr)


if __name__ == '__main__':
    main()
