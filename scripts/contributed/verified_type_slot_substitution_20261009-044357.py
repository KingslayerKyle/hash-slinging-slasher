"""Context-conditioned token substitutions within verified names of one type.

Uses the existing reviewed slot-context algorithm with a source-hash-verified,
type-specific corpus. Streams candidates to confirm_list; candidates alone are
not discoveries. No game files, network services or processes are accessed.
"""
import argparse
import importlib.util
import json
from pathlib import Path
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
    return sorted(name for name in names if name and '\n' not in name and '\r' not in name
                  and '~' not in name and '&' not in name and not name.startswith('twc/'))

def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--game', required=True, choices=sorted(snapshot.MODERN))
    parser.add_argument('--kind', required=True, choices=sorted(TABLES))
    parser.add_argument('--cap', type=int, default=12)
    args = parser.parse_args()
    if not 2 <= args.cap <= 32:
        parser.error('--cap must be between 2 and 32')
    shot = snapshot.read(ROOT / 'snapshots' / (args.game.lower() + '.ids'))
    assert shot.game == args.game
    companion = ROOT / 'scripts/contributed/slotswap_cores_20260926-073306.py'
    spec = importlib.util.spec_from_file_location('_verified_slot_core', companion)
    core = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(core)
    names = corpus(args.kind)
    offers = core.measure_offers(names, cap=args.cap)
    print(json.dumps({'game': args.game, 'kind': args.kind, 'verified_seeds': len(names), 'contexts': len(offers)}), file=sys.stderr)
    made = 0
    for name in names:
        tokens = core.split(name)
        if not 2 <= len(tokens) <= 16:
            continue
        texts = [text for text, _ in tokens]
        marks = [mark for _, mark in tokens]
        candidates = set()
        for index, text in enumerate(texts):
            if not text or text.isdigit():
                continue
            head = ''.join(t + mark for t, mark in zip(texts[:index], marks[:index]))
            tail = ''.join(t + mark for t, mark in zip(texts[index + 1:], marks[index + 1:]))
            for other in offers.get(core.context_of(texts, index), ()):
                if other != text:
                    candidates.add(head + other + marks[index] + tail)
        for candidate in sorted(candidates):
            print('0,' + candidate)
        made += len(candidates)
    print(json.dumps({'game': args.game, 'kind': args.kind, 'candidates': made}), file=sys.stderr)

if __name__ == '__main__':
    main()
