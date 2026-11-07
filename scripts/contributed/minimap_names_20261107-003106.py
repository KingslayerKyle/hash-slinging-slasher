"""How the modern titles name minimap / compass images, per game, and what MW7 holds for chosen map codenames."""
import collections
import glob
import os
import re
import sys

sys.path.insert(0, 'scripts')
import snapshot as S

MASK = (1 << 63) - 1
FILES = [('MODWAR22', 'modwar22'), ('YAMYAMOK', 'yamyamok'), ('BLACKOP6', 'blackop6'), ('BLACKOP7', 'blackop7'), ('MODWAR7', 'modwar7')]
names = set(n.strip().lower() for n in S.table_names('fnv1a_ximages_v2'))
names |= set(n.strip().lower() for n in S.confirmed_names('image'))
MAP = re.compile(r'compass|minimap|mini_map|tacmap|tac_map|_map_|^map_|_map$|overhead|fullmap|bigmap|worldmap')
maps = [n for n in names if MAP.search(n)]
print('image names', len(names), 'map-shaped', len(maps))
hashes = {n: S.fnv1a(n, 'MODWAR7', 'image') & MASK for n in maps}

for game, f in FILES:
    ids = set(i & MASK for i in S.read('snapshots/%s.ids' % f).by_pool()['image'])
    hit = sorted(n for n, h in hashes.items() if h in ids)
    comp = [n for n in hit if 'compass' in n]
    print('\n==', game, 'map-shaped named', len(hit), 'with compass', len(comp))
    print('  shapes', collections.Counter(re.sub(r'\d+', '#', re.sub(r'(mp|sp|wz|br|cp|me|sat|t\d+|jup|rex|iw\d)_[a-z0-9]+', r'\1_X', n))[:40] for n in comp).most_common(14))
    step = max(1, len(comp) // 14)
    for n in comp[::step][:14]:
        print('   ', n[:100])

for word in sys.argv[1:] or ['hajin', 'x01', 'x_01', 'exfil', 'dmz']:
    hit = sorted(n for n in names if word in n)
    print('\n-- %r in image names: %d' % (word, len(hit)))
    for n in hit[:25]:
        h = S.fnv1a(n, 'MODWAR7', 'image') & MASK
        print('   ', n[:100])

# Every table and every confirmed type, not just images.
print('\n== any table or type')
words = sys.argv[1:] or ['hajin', 'x01']
for path in sorted(glob.glob(os.path.join(S.settings.tables_csv(), '*.csv'))):
    table = os.path.basename(path)[:-4]
    with open(path, encoding='utf-8', errors='replace') as handle:
        text = handle.read().lower()
    print(table, {w: text.count(w) for w in words if text.count(w)}) if any(w in text for w in words) else None
conf = [n.lower() for n in S.confirmed_names()]
for w in words:
    hit = sorted(set(n for n in conf if w in n))
    print('confirmed containing', w, len(hit), hit[:15])

# Which map codenames the installed fast files actually use.
root = r'C:\Program Files (x86)\Steam\steamapps\common\Call of Duty HQ'
for folder in ('cod26', 'sp26'):
    files = [os.path.basename(p) for p in glob.glob(os.path.join(root, folder, '**', '*.ff'), recursive=True)]
    print('\n', folder, 'ff files', len(files))
    for w in words:
        hit = sorted(f for f in files if w in f.lower())
        print('  ', w, len(hit), hit[:12])
    tops = collections.Counter(re.match(r'((?:mp|sp|wz|cp|dmz)_(?:[a-z]+_)?[a-z0-9]+)', f).group(1) for f in files if re.match(r'((?:mp|sp|wz|cp|dmz)_(?:[a-z]+_)?[a-z0-9]+)', f))
    print('   maps', [k for k, _ in tops.most_common(70)])
