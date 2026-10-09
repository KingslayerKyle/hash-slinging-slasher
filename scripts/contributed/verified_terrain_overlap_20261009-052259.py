"""Join overlapping, target-held terrain triples to predict four-layer blends.

An observed a_b_c and b_c_d suggest a_b_c_d. Measures this relation against all
verified four-layer names already held on the target before producing candidates.
Reads verified names and the canonical snapshot only; no game/process access.
Confirm the generated list with this explicit game and material selected.
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
if not (ROOT / 'scripts/snapshot.py').is_file(): ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / 'scripts'))
import snapshot

def corpus():
    names = set(snapshot.table_names('fnv1a_xmaterials_v2'))
    for top in ['all_names', 'submissions', 'findings']:
        for path in (ROOT / top).rglob('material*.txt'):
            for row in path.read_text(encoding='utf-8').splitlines():
                raw, sep, name = row.partition(',')
                if not sep or not name.startswith('twc/*'): continue
                try: key = int(raw, 16) & snapshot.ID_MASK
                except ValueError: continue
                if snapshot.fnv1a(name, 'YAMYAMOK', 'material') & snapshot.ID_MASK == key:
                    names.add(name.lower())
    return names

def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--game', required=True, choices=sorted(snapshot.MODERN))
    args = parser.parse_args()
    shot = snapshot.read(ROOT / 'snapshots' / (args.game.lower() + '.ids'))
    assert shot.game == args.game
    held = set(shot.by_pool()['material'])
    triples, quads = set(), set()
    for name in corpus():
        if not name.startswith('twc/*') or snapshot.fnv1a(name, args.game, 'material') & snapshot.ID_MASK not in held:
            continue
        parts = tuple(name[5:].split('_'))
        if not all(re.fullmatch(r'\d+d?n', p) for p in parts): continue
        if len(parts) == 3: triples.add(parts)
        elif len(parts) == 4: quads.add(parts)
    continuation = defaultdict(set)
    for a, b, c in triples:
        continuation[a, b].add(c)
    covered = sum(q[:3] in triples and q[1:] in triples for q in quads)
    candidates = sum(len(continuation.get((b, c), ())) for a, b, c in triples)
    out = ROOT / 'contrib/verified_terrain_overlap' / args.game.lower()
    out.mkdir(parents=True, exist_ok=True)
    report = {'game': args.game, 'triples': len(triples), 'known_quads': len(quads),
              'covered_known_quads': covered, 'candidates_before_known_removal': candidates}
    made = 0
    with (out / 'quads.txt').open('w', encoding='utf-8') as stream:
        for a, b, c in sorted(triples):
            for d in sorted(continuation.get((b, c), ())):
                q = (a, b, c, d)
                if q not in quads:
                    stream.write('0,twc/*' + '_'.join(q) + '\n')
                    made += 1
    report['new_candidates'] = made
    report['list'] = (out / 'quads.txt').relative_to(ROOT).as_posix()
    (out / 'measurement.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report))

if __name__ == '__main__': main()
