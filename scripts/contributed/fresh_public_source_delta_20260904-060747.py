#!/usr/bin/env python3
"""Emit exact asset-shaped literals from newly acquired public source trees.

Each title has a deliberately separate set of fresh trees.  Literals already
present in the source trees confirmed earlier are removed before output, so
the confirmation is a true source delta rather than a replay of those runs.

    python contrib/fresh_public_source_delta_20260904.py --game BO4
    python contrib/fresh_public_source_delta_20260904.py --game CW
"""
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LITERAL = re.compile(r'(?:#)?["\']([A-Za-z0-9_./\\\\-]{6,160})["\']')
EXTENSIONS = {'.gsc', '.csc', '.cfg', '.csv', '.ddl', '.gdb', '.graph', '.lua',
              '.raw', '.txt', '.vision', '.json', '.js', '.ts', '.py', '.md'}

SOURCES = {
    'BO4': (
        ('Aurora-BO4-Lucy-Menu', 'BlackOps4Shop', 'BO4-Director-s-Cut',
         'Bo4HashFinder', 't8-atian-menu', 't8-custom-ee'),
        ('bo4-source', 'bo4-source-lua', 't8-src', 'BO4-BlackoutBots',
         'bo4-lucy-menu', 'BO4-BlackOps4ShieldMenu', 'BlackoutBotsBO4',
         'Abomination-Unofficial', 'Synergy-BO4-GSC-Menu', 't8-tests',
         'Shield-Menu-BO4', 'bo4-pap-mod', 'demo_mods', 'shield_mods'),
    ),
    'CW': (
        ('T9_BOCW_GSC_Wiki', 'T9-Assets-Extracted-List',
         'COD-BOCW-Asset-Directory'),
        ('bocw-source', 't9-src', 'ColdWarGSCMenu', 'coldwar.gsc', 'cwmenu',
         'ColdWar-Lucy-Base', 'demo_mods', 'shield_mods'),
    ),
}


def collect(root: Path) -> set[str]:
    names = set()
    if not root.is_dir():
        return names
    for path in root.rglob('*'):
        if not path.is_file() or path.suffix.lower() not in EXTENSIONS:
            continue
        try:
            text = path.read_text(encoding='utf-8', errors='ignore')
        except OSError:
            continue
        for name in LITERAL.findall(text):
            name = name.lower().replace('\\\\', '/')
            if (('_' in name or '/' in name)
                    and sum(char.isalpha() for char in name) >= 3):
                names.add(name)
    return names


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--game', choices=SOURCES, required=True)
    options = parser.parse_args()
    fresh, old = SOURCES[options.game]
    fresh_names = set().union(*(collect(ROOT / 'borrowed' / item) for item in fresh))
    old_names = set().union(*(collect(ROOT / 'borrowed' / item) for item in old))
    delta = fresh_names - old_names
    print(f'{options.game}: {len(fresh_names):,} fresh literals - '
          f'{len(fresh_names & old_names):,} inherited = {len(delta):,} delta', file=sys.stderr)
    print('\n'.join(sorted(delta)))


if __name__ == '__main__':
    main()
