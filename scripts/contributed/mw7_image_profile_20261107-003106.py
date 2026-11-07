"""Profile MW7 image names: every known name that hashes into the image pool, and how ids are ordered."""
import collections
import glob
import os
import re
import sys

sys.path.insert(0, 'scripts')
import snapshot as S

GAME = 'MODWAR7'
snap = S.read('snapshots/modwar7.ids')
img = snap.by_pool()['image']
print('image ids', len(img), 'sorted?', img == sorted(img))
print('first ids', [hex(x) for x in img[:3]])

MASK = (1 << 63) - 1
ids = set(i & MASK for i in img)
known = S.known_hashes(game=GAME)
unnamed = ids - known
print('unnamed by table', len(unnamed), 'named by table', len(ids) - len(unnamed))

tabs = sorted(os.path.basename(p)[:-4] for p in glob.glob(os.path.join(S.settings.tables_csv(), '*.csv')))
print('tables', tabs)
print('modern tables', sorted(S.MODERN_TABLES))

# Every name anybody holds, whatever it was filed under, that hashes into this image pool.
names = set()
for table in tabs:
    if table in S.MODERN_TABLES:
        for n in S.table_names(table):
            names.add(n)
print('table names', len(names))
conf = set(S.confirmed_names())
print('confirmed names', len(conf))
hits = {}
for n in names | conf:
    h = S.fnv1a(n, GAME, 'image') & MASK
    if h in ids:
        hits[h] = n.strip().lower()
print('names hitting MW7 image pool', len(hits))

left = ids - known - set(hits)
print('unnamed after confirmed', len(left))

with open('logs/mw7_image_names.txt', 'w', encoding='utf-8') as out:
    for n in sorted(hits.values()):
        out.write(n + '\n')
with open('logs/mw7_image_unnamed.txt', 'w') as out:
    for i in sorted(left):
        out.write('%016x\n' % i)

vals = list(hits.values())
head = collections.Counter(n.split('_')[0] for n in vals)
tail = collections.Counter(n.rsplit('_', 1)[-1] for n in vals)
slash = sum('/' in n for n in vals)
lens = sorted(len(n) for n in vals)
print('with slash', slash, 'median length', lens[len(lens) // 2])
print('heads', head.most_common(40))
print('tails', tail.most_common(40))
