"""Offer same-class animation events to weapon alias heads held in one game.

Alias heads and take endings must be attested on the target capture. Event
vocabulary comes from source-hash-verified animations and aliases in the same
weapon class. --completed-plan excludes an earlier whole-animation-core grid.
Prints candidates only; normal sound_alias confirmation and submission required.
"""
import argparse
from collections import defaultdict
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent
while ROOT != ROOT.parent and not (ROOT / 'scripts/snapshot.py').is_file(): ROOT = ROOT.parent
if not (ROOT / 'scripts/snapshot.py').is_file(): ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / 'scripts'))
import snapshot

CLASSES = 'ar|sm|pi|sh|lm|br|dm|sn|me|la|smg|pistol|lmg|dmr|shotgun|sniper|rifle|launcher|melee|special'
ANIM = re.compile(r'^(?:[a-z0-9]+_)?(?:(?:vm|wm)_)?(?:[a-z]{0,2}p\d*_)?(?P<class>' + CLASSES + r')_(?P<weapon>[a-z0-9]+)_(?P<event>.+)$')
ALIAS = re.compile(r'^(?P<prefix>(?:fly|wfoly|wpn|weap)_(?:(?:rex|sat|jup)_)?(?:(?:plr|npc)_)?)(?P<class>' + CLASSES + r')_(?P<weapon>[a-z0-9]+)_(?P<event>.+?)(?P<take>(?:_\d{1,3}){0,2})$')

def corpus(kind, table, game):
    out = set(snapshot.table_names(table))
    for top in ['all_names', 'submissions', 'findings']:
        for path in (ROOT / top).rglob(kind + '*.txt'):
            for row in path.read_text(encoding='utf-8').splitlines():
                raw, sep, name = row.partition(',')
                if not sep or not name: continue
                try: key = int(raw, 16) & snapshot.ID_MASK
                except ValueError: continue
                if snapshot.fnv1a(name, game, kind) & snapshot.ID_MASK == key: out.add(name.lower())
    return {n for n in out if n.isascii() and '\n' not in n and '\r' not in n}

def completed_grid(path):
    if path is None: return set(), set(), set()
    path = path if path.is_absolute() else ROOT / path
    fields = defaultdict(set)
    bare = False
    for line in path.read_text(encoding='utf-8').splitlines():
        key, _, value = line.partition(':'); value = value.strip()
        if key == 'bare': bare = value == 'yes'
        if key not in {'begin', 'stem', 'end'}: continue
        values = (ROOT / value[1:]).read_text(encoding='utf-8').splitlines() if value.startswith('@') else [value]
        fields[key].update(row.partition(',')[2] if ',' in row else row for row in values)
    if bare: fields['begin'].add('')
    # The engine always tests the beginning+stem without an ending as well.
    fields['end'].add('')
    return fields['begin'], fields['stem'], fields['end']

def candidates(animations, aliases, held, game, previous):
    events, heads, takes = defaultdict(set), defaultdict(set), defaultdict(set)
    for name in animations:
        m = ANIM.fullmatch(name)
        if m: events[m['class']].add(m['event'])
    for name in aliases:
        m = ALIAS.fullmatch(name)
        if not m: continue
        cls = m['class']; events[cls].add(m['event'])
        if snapshot.fnv1a(name, game, 'sound_alias') & snapshot.ID_MASK in held:
            heads[cls].add((m['prefix'], m['weapon'])); takes[cls].add(m['take'])
    begins, stems, ends = previous
    sent = 0
    for cls in sorted(heads):
        for prefix, weapon in sorted(heads[cls]):
            for event in sorted(events[cls]):
                core = cls + '_' + weapon + '_' + event
                covered = prefix in begins and core in stems
                for take in sorted(takes[cls]):
                    if covered and take in ends: continue
                    name = prefix + core + take
                    if name not in aliases:
                        sent += 1
                        yield name
    print(f'{sent} candidates from {sum(map(len, heads.values()))} target-held heads in {len(heads)} weapon classes', file=sys.stderr)

def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument('--game', required=True, choices=sorted(snapshot.MODERN))
    p.add_argument('--kind', choices=['sound_alias'], default='sound_alias')
    p.add_argument('--completed-plan', type=Path)
    a = p.parse_args()
    shot = snapshot.read(ROOT / 'snapshots' / (a.game.lower() + '.ids'))
    assert shot.game == a.game
    animations = corpus('xanim', 'fnv1a_xanims_v2', a.game)
    aliases = corpus('sound_alias', 'fnv1a_soundbanks_aliases_v2', a.game)
    for name in candidates(animations, aliases, set(shot.by_pool()['sound_alias']), a.game, completed_grid(a.completed_plan)):
        print(name)

if __name__ == '__main__': main()
