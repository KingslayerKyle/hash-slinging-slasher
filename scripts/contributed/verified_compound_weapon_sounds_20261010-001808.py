"""Replace a coupled weapon code in namespace-prefixed reload directories.

Known target-held sound files provide path, namespace and encoding conventions.
Target-held images, animations and aliases provide class-and-weapon pairs.
Verified names establish each source weapon's class, even when a filename
omits the class. Its code must appear in both a namespace-prefixed directory component and the
basename. Bare-code and class-code directories are excluded from this domain. Substitute both together, using only the same verified class.
This reaches coupled names that one-token edits and ordinary alias-to-file
families miss. Original separators and encoding endings remain unchanged.
Run output through normal modern sound_asset confirmation and submission.
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
WEAPON = re.compile(r'(?:^|[_/])(?:sat|t10|jup|iw9|s4|iw8|t9|rex|s6)_(?P<cls>ar|sm|pi|sh|lm|br|dm|sn|me|la)_(?P<code>[a-z][a-z0-9]+)(?![a-z0-9])')


def corpus(kind, game):
    tables = {'sound_asset': ['fnv1a_xsounds_v2'],
              'sound_alias': ['fnv1a_soundbanks_aliases_v2', 'fnv1a_soundbanks_aliases'],
              'image': ['fnv1a_ximages_v2'], 'xanim': ['fnv1a_xanims_v2']}[kind]
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


def build(sounds, aliases, file_ids, alias_ids, game, source_entities=(), target_entities=()):
    weapons = defaultdict(set)
    classes = defaultdict(set)
    held_aliases = {n for n in aliases if snapshot.fnv1a(n, game, 'sound_alias') & snapshot.ID_MASK in alias_ids}
    for name in set(source_entities) | set(aliases) | set(target_entities):
        for match in WEAPON.finditer(name):
            classes[match['code']].add(match['cls'])
    for name in held_aliases | set(target_entities):
        for match in WEAPON.finditer(name):
            weapons[match['cls']].add(match['code'])
    groups = []
    source_pairs = set()
    for name in sorted(sounds):
        encoded = FORMAT.fullmatch(name)
        if not encoded or snapshot.fnv1a(name, game, 'sound_asset') & snapshot.ID_MASK not in file_ids:
            continue
        stem = encoded['stem']
        boundary = max(stem.rfind('/'), stem.rfind(chr(92)), stem.rfind('.')) + 1
        directory, base = stem[:boundary], stem[boundary:]
        components = set(re.split(r'[/\\.]', directory))
        explicit = {match['code']: match['cls'] for match in WEAPON.finditer(base)}
        for component in sorted(components):
            # This domain is disjoint from bare-code and class-code directories.
            qualified = re.fullmatch(r'(sat|t10|jup|iw9|s4|iw8|t9|rex|s6)_([a-z][a-z0-9]+)', component)
            if not qualified or qualified[2] not in classes:
                continue
            code = qualified[2]
            source_classes = {explicit[code]} if code in explicit else classes[code]
            if len(source_classes) != 1:
                continue
            cls = next(iter(source_classes))
            alternatives = weapons.get(cls, set()) - {code}
            if not alternatives:
                continue
            token = re.compile(r'(?<![a-z0-9])' + re.escape(code) + r'(?![a-z0-9])')
            if not token.search(base) or len(token.findall(stem)) < 2:
                continue
            groups.append((stem, encoded['tail'], token, alternatives))
            source_pairs.add((cls, code))
    return groups, {'game': game,
                    'target_held_weapon_codes': sum(map(len, weapons.values())),
                    'weapon_classes': len(weapons),
                    'source_coupled_weapon_pairs': len(source_pairs),
                    'target_held_coupled_files': len(groups),
                    'candidate_product': sum(len(g[3]) for g in groups)}


def candidates(groups, known):
    emitted = set()
    for stem, tail, token, alternatives in groups:
        for code in sorted(alternatives):
            name = token.sub(code, stem) + tail
            if name not in known and name not in emitted:
                emitted.add(name)
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
    source_entities, target_entities = set(), set()
    for kind in ['image', 'xanim']:
        names = corpus(kind, args.game)
        source_entities.update(names)
        ids = set(pools[kind])
        target_entities.update(n for n in names if snapshot.fnv1a(n, args.game, kind) & snapshot.ID_MASK in ids)
    groups, report = build(sounds, aliases, set(pools['sound_asset']),
                           set(pools['sound_alias']), args.game, source_entities, target_entities)
    print(json.dumps(report), file=sys.stderr)
    if args.measure:
        return
    count = 0
    for name in candidates(groups, sounds):
        print(name)
        count += 1
    print(json.dumps({'unseen_candidates_emitted': count}), file=sys.stderr)


if __name__ == '__main__':
    main()
