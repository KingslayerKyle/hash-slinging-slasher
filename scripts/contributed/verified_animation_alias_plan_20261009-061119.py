"""Measure target-held animation-to-alias naming and build a compact plan.

Only source-hash-verified animation cores are used. Alias prefixes and take
endings must be observed in the selected target capture with those cores.
Generated candidates require an explicit sound_alias confirmation for that
game, followed by normal submission. Reads tables and snapshots only.
"""
import argparse
from collections import Counter
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent
while ROOT != ROOT.parent and not (ROOT / 'scripts/snapshot.py').is_file():
    ROOT = ROOT.parent
if not (ROOT / 'scripts/snapshot.py').is_file(): ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / 'scripts'))
import snapshot

CORE = re.compile(r'^(?:[a-z0-9]+_)?(?:vm|wm)_(.+)$')

def corpus(kind, table, game):
    result = set(snapshot.table_names(table))
    for top in ['all_names', 'submissions', 'findings']:
        for path in (ROOT / top).rglob(kind + '*.txt'):
            for line in path.read_text(encoding='utf-8').splitlines():
                raw, sep, name = line.partition(',')
                if not sep or not name: continue
                try: key = int(raw, 16) & snapshot.ID_MASK
                except ValueError: continue
                if snapshot.fnv1a(name, game, kind) & snapshot.ID_MASK == key:
                    result.add(name.lower())
    return {n for n in result if n.isascii() and '\n' not in n and '\r' not in n}

def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--game', required=True, choices=sorted(snapshot.MODERN))
    args = parser.parse_args()
    shot = snapshot.read(ROOT / 'snapshots' / (args.game.lower() + '.ids'))
    assert shot.game == args.game
    held = {kind: set(ids) for kind, ids in shot.by_pool().items()}
    cores = {m[1] for n in corpus('xanim', 'fnv1a_xanims_v2', args.game)
             if (m := CORE.fullmatch(n)) and len(m[1]) >= 4}
    prefixes, endings = Counter(), Counter()
    known = represented = 0
    for name in corpus('sound_alias', 'fnv1a_soundbanks_aliases_v2', args.game):
        if snapshot.fnv1a(name, args.game, 'sound_alias') & snapshot.ID_MASK not in held['sound_alias']: continue
        known += 1
        matched = False
        for count in range(3):
            regex = r'(?:_\d{1,3}){' + str(count) + '}$' if count else '$'
            at = re.search(regex, name)
            if at is None: continue
            stem, tail = name[:at.start()], name[at.start():]
            positions = [0] + [i+1 for i, c in enumerate(stem) if c == '_'][:5]
            for index in positions:
                if stem[index:] in cores:
                    prefixes[stem[:index]] += 1
                    endings[tail] += 1
                    matched = True
        represented += matched
    assert cores and prefixes and endings, 'No verified animation-to-alias convention on target'
    out = ROOT / 'contrib/verified_animation_aliases' / args.game.lower()
    out.mkdir(parents=True, exist_ok=True)
    paths = {}
    for role, values in [('begin', prefixes), ('stem', cores), ('end', endings)]:
        path = out / (role + '.txt')
        path.write_text(''.join('0,' + v + '\n' for v in sorted(values) if v), encoding='utf-8')
        paths[role] = path.relative_to(ROOT).as_posix()
    plan = out / 'aliases.plan.txt'
    plan.write_text(f'label: {args.game} target-measured animation cores to sound aliases\n'
                    f'describe: source-hash-verified vm/wm animation cores with prefixes and zero, one or two numeric take endings actually observed on this capture; relation represents {represented}/{known} verified target aliases; includes bare core and bare ending\n'
                    f'game: {args.game}\nbegin: @{paths["begin"]}\nstem: @{paths["stem"]}\nend: @{paths["end"]}\n'
                    'bare: yes\nfold: yes\n', encoding='utf-8')
    report = {'game': args.game, 'cores': len(cores), 'known_aliases': known, 'represented': represented,
              'prefixes': len(prefixes), 'endings': len(endings), 'plan': plan.relative_to(ROOT).as_posix()}
    (out / 'measurement.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report))

if __name__ == '__main__': main()
