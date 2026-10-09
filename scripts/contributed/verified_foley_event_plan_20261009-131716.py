"""Complete modern weapon-foley aliases with shared same-class event sequences.

Target-held aliases supply the literal namespace, actor, class and weapon head.
An ending is eligible only if two distinct weapon codes already use that exact
event sequence in the same class and actor role. Numeric event/take tokens are
retained. This reaches cells differing in several tokens that one-token edits
miss. Write one measured class/actor grid for normal sound_alias confirmation.
Reads verified names and public snapshots; writes only relative plan data.
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

CLASSES = ['ar', 'sm', 'pi', 'sh', 'lm', 'br', 'dm', 'sn', 'me', 'la']
ALIAS = re.compile(r'^(?P<head>wfoly_(?:(?:rex|sat|jup|iw9|iw8|t10|t9|s4|s6)_)?'
                   r'(?P<actor>plr|npc)_(?P<cls>' + '|'.join(CLASSES) + r')_'
                   r'(?P<weapon>[a-z][a-z0-9]+)_)(?P<event>.+)$')


def corpus(game):
    names = set(snapshot.table_names('fnv1a_soundbanks_aliases_v2', 'fnv1a_soundbanks_aliases'))
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


def build(names, held, game):
    support = defaultdict(lambda: defaultdict(set))
    heads = defaultdict(set)
    controls = defaultdict(set)
    for name in names:
        match = ALIAS.fullmatch(name)
        if not match:
            continue
        group = match['cls'], match['actor']
        support[group][match['event']].add(match['weapon'])
        if snapshot.fnv1a(name, game, 'sound_alias') & snapshot.ID_MASK in held:
            heads[group].add(match['head'])
            controls[group].add((name, match['event']))
    grids, report = {}, []
    for group in sorted(heads):
        events = {e for e, codes in support[group].items() if len(codes) >= 2}
        if not events:
            continue
        control = sum(event in events for _, event in controls[group])
        grids[group] = heads[group], events
        report.append({'weapon_class': group[0], 'actor': group[1],
                       'target_held_heads': len(heads[group]),
                       'shared_same_class_events': len(events),
                       'known_target_aliases': len(controls[group]),
                       'known_controls_reconstructible': control,
                       'candidate_product': len(heads[group]) * len(events)})
    return grids, report


def write_plan(game, cls, actor, heads, events):
    out = ROOT / 'contrib/verified_foley_events' / game.lower() / (cls + '_' + actor)
    out.mkdir(parents=True, exist_ok=True)
    paths = {}
    for role, values in [('begin', heads), ('stem', events)]:
        path = out / (role + '.txt')
        path.write_text(''.join('0,' + n + '\n' for n in sorted(values)), encoding='utf-8')
        paths[role] = path.relative_to(ROOT).as_posix()
    plan = out / 'foley.plan.txt'
    plan.write_text(f'label: {game} {cls} {actor} shared weapon-foley event grid\n'
                    f'describe: literal target-held weapon-foley alias heads with exact event sequences attested under at least two distinct weapon codes in the same class and actor role; numeric event/take tokens retained\n'
                    f'game: {game}\nbegin: @{paths["begin"]}\nstem: @{paths["stem"]}\n'
                    'bare: no\nfold: yes\n', encoding='utf-8')
    return plan.relative_to(ROOT).as_posix()


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--game', required=True, choices=sorted(snapshot.MODERN))
    parser.add_argument('--class', dest='cls', choices=CLASSES)
    parser.add_argument('--actor', choices=['plr', 'npc'])
    parser.add_argument('--write-plan', action='store_true')
    args = parser.parse_args()
    shot = snapshot.read(ROOT / 'snapshots' / (args.game.lower() + '.ids'))
    assert shot.game == args.game
    grids, report = build(corpus(args.game), set(shot.by_pool()['sound_alias']), args.game)
    print(json.dumps({'game': args.game, 'groups': report}))
    if args.write_plan:
        group = args.cls, args.actor
        if group not in grids:
            parser.error('Choose a measured class and actor with a viable grid')
        plan = write_plan(args.game, args.cls, args.actor, *grids[group])
        print(json.dumps({'plan': plan}))


if __name__ == '__main__':
    main()
