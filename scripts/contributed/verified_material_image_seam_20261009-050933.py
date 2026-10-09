"""Measure image-channel siblings of source-hash-verified material cores.

Uses channels and image directories attested on the selected target capture.
Writes relative ignored plan inputs only. Run with that game and image selected;
generated candidates are not discoveries until normal confirmation/submission.
"""
import argparse
from collections import Counter
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

def corpus(kind):
    table = 'fnv1a_ximages' if kind == 'image' else 'fnv1a_xmaterials'
    names = set(snapshot.table_names(table, table + '_v2'))
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
                if any(snapshot.fnv1a(name, game, kind) & snapshot.ID_MASK == key
                       for game in ['YAMYAMOK', 'BLKOPSCW']):
                    names.add(name.lower().replace(chr(92), '/'))
    return {n for n in names if n.isascii() and not n.startswith('twc/')
            and not any(c in n for c in '~&\r\n')}

def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--game', required=True, choices=sorted(snapshot.MODERN))
    args = parser.parse_args()
    shot = snapshot.read(ROOT / 'snapshots' / (args.game.lower() + '.ids'))
    assert shot.game == args.game
    held = set(shot.by_pool()['image'])
    channels, prefixes = Counter(), Counter()
    measured = 0
    for name in corpus('image'):
        if snapshot.fnv1a(name, args.game, 'image') & snapshot.ID_MASK not in held:
            continue
        measured += 1
        head, slash, tail = name.rpartition('/')
        if slash: prefixes[head + slash] += 1
        for prefix in ['i_', 'mtl_']:
            if tail.startswith(prefix): prefixes[head + slash + prefix] += 1
        _, underscore, ending = tail.rpartition('_')
        if underscore and re.fullmatch('[a-z][a-z0-9]{0,9}', ending):
            channels['_' + ending] += 1
    endings = [n for n, _ in channels.most_common(48)]
    beginnings = [n for n, _ in prefixes.most_common(16)]
    assert endings, 'No target-held image channels'
    materials = corpus('material')
    cores = set()
    for name in materials:
        base = name.rsplit('/', 1)[-1]
        for prefix in ['mtl_', 'i_']:
            if base.startswith(prefix):
                base = base[len(prefix):]
                break
        if len(base) < 5: continue
        cores.add(base)
        shorter = re.sub(r'_(?:v\d+|cm|dm|nm|sm|hm|col|nml|mask|swatch)$', '', base)
        if len(shorter) >= 5: cores.add(shorter)
    out = ROOT / 'contrib/verified_material_image_seam' / args.game.lower()
    out.mkdir(parents=True, exist_ok=True)
    files = {}
    for role, names in [('begin', beginnings), ('stem', sorted(cores)), ('end', endings)]:
        path = out / (role + '.txt')
        path.write_text(''.join('0,' + name + '\n' for name in names), encoding='utf-8')
        files[role] = path.relative_to(ROOT).as_posix()
    plan = out / 'images.plan.txt'
    plan.write_text(f'label: {args.game} verified material-to-image channel seam\n'
                    f'describe: source-hash-verified material basenames and channel/version cuts crossed with {len(endings)} channel endings and {len(beginnings)} image prefixes actually held in the target capture; packed textures and terrain blends excluded\n'
                    f'game: {args.game}\nstem: @{files["stem"]}\nend: @{files["end"]}\n'
                    + (f'begin: @{files["begin"]}\n' if beginnings else '')
                    + 'bare: yes\nfold: yes\n', encoding='utf-8')
    print(f'{args.game}: {measured} target-held images; {len(materials)} verified materials; '
          f'{len(cores)} cores x {len(beginnings)+1} prefixes x {len(endings)+1} endings; {plan.relative_to(ROOT).as_posix()}')

if __name__ == '__main__':
    main()
