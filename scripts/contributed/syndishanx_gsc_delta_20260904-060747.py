#!/usr/bin/env python3
"""Exact literal delta from SyndiShanX's independently dumped BO4/CW scripts."""
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'borrowed' / 'SyndiShanX-COD-GSC-Source'
LITERAL = re.compile(r'(?:#)?["\']([A-Za-z0-9_./\\\\-]{6,160})["\']')
EXTENSIONS = {'.gsc', '.csc', '.lua'}
SETS = {
    'BO4': (('BO4-GSC', 'BO4-LUA'), ('bo4-source', 'bo4-source-lua', 't8-src',
        'BO4-BlackoutBots', 'bo4-lucy-menu', 'BO4-BlackOps4ShieldMenu', 'BlackoutBotsBO4',
        'Abomination-Unofficial', 'Synergy-BO4-GSC-Menu', 't8-tests', 'Shield-Menu-BO4',
        'bo4-pap-mod', 'demo_mods', 'shield_mods')),
    'CW': (('CW-GSC',), ('bocw-source', 't9-src', 'ColdWarGSCMenu', 'coldwar.gsc', 'cwmenu',
        'ColdWar-Lucy-Base', 'demo_mods', 'shield_mods')),
}


def collect(root: Path) -> set[str]:
    found = set()
    for path in root.rglob('*') if root.is_dir() else ():
        if path.is_file() and path.suffix.lower() in EXTENSIONS:
            for value in LITERAL.findall(path.read_text(encoding='utf-8', errors='ignore')):
                value = value.lower().replace('\\\\', '/')
                if ('_' in value or '/' in value) and sum(c.isalpha() for c in value) >= 3:
                    found.add(value)
    return found


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--game', choices=SETS, required=True)
    args = parser.parse_args()
    fresh_dirs, old_dirs = SETS[args.game]
    fresh = set().union(*(collect(SOURCE / directory) for directory in fresh_dirs))
    old = set().union(*(collect(ROOT / 'borrowed' / directory) for directory in old_dirs))
    delta = fresh - old
    print(f'{args.game}: {len(fresh):,} source literals, {len(delta):,} new after prior sources', file=sys.stderr)
    print('\n'.join(sorted(delta)))


if __name__ == '__main__':
    main()
