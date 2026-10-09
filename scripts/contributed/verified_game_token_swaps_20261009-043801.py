"""Try target-game codename substitutions in source-verified asset names.

Changes complete namespace tokens only, retaining all other characters,
including the original sound-file separators and encoding tails. Generated
names require normal target-specific confirmation before they are discoveries.
"""
import argparse
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

TABLES = {'image': 'fnv1a_ximages', 'material': 'fnv1a_xmaterials', 'xanim': 'fnv1a_xanims',
          'sound_alias': 'fnv1a_soundbanks_aliases', 'sound_asset': 'fnv1a_xsounds'}
CODES = {'MODWAR22': 'iw9', 'YAMYAMOK': 'jup', 'BLACKOP6': 't10', 'BLACKOP7': 'sat', 'MODWAR7': 'rex'}
TOKEN = re.compile(r'(?<![a-z0-9])(?:iw7|iw8|iw9|jup|t7|t8|t9|t10|sat|rex|s4|h1|h2|s2|s6)(?=[_/\.]|$)')

def corpus(kind):
    table = TABLES[kind]
    names = set(snapshot.table_names(table, table + '_v2'))
    for top in ['all_names', 'submissions', 'findings']:
        for path in (ROOT / top).rglob(kind + '*.txt'):
            for line in path.read_text(encoding='utf-8').splitlines():
                raw, sep, name = line.partition(',')
                if not sep or not name:
                    continue
                try:
                    key = int(raw, 16) & snapshot.ID_MASK
                except ValueError:
                    continue
                values = [snapshot.fnv1a(name, 'YAMYAMOK', kind), snapshot.fnv1a(name)]
                if kind == 'sound_asset':
                    values.append(snapshot.fnv1a_nofold(name))
                if any(value & snapshot.ID_MASK == key for value in values):
                    names.add(name.lower())
    return names

def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--game', required=True, choices=sorted(CODES))
    parser.add_argument('--kind', required=True, choices=sorted(TABLES))
    args = parser.parse_args()
    shot = snapshot.read(ROOT / 'snapshots' / (args.game.lower() + '.ids'))
    assert shot.game == args.game
    code = CODES[args.game]
    names = corpus(args.kind)
    candidates = set()
    changed_sources = 0
    for name in names:
        if '\n' in name or '\r' in name:
            continue
        matches = [match for match in TOKEN.finditer(name) if match.group() != code]
        if not matches:
            continue
        changed_sources += 1
        for match in matches:
            candidates.add(name[:match.start()] + code + name[match.end():])
        candidates.add(TOKEN.sub(code, name))
    candidates.difference_update(names)
    out = ROOT / 'contrib/verified_game_swaps' / args.game.lower()
    out.mkdir(parents=True, exist_ok=True)
    (out / (args.kind + '.txt')).write_text(''.join(name + '\n' for name in sorted(candidates)), encoding='utf-8')
    print(json.dumps({'game': args.game, 'kind': args.kind, 'target_code': code, 'source_names': len(names),
                      'changed_sources': changed_sources, 'candidates': len(candidates)}))

if __name__ == '__main__':
    main()
