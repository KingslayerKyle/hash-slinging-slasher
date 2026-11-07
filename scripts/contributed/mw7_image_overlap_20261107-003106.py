"""Where MW7's unnamed image ids live relative to the other modern captures, and what shape those games' names are."""
import collections
import random
import re
import sys

sys.path.insert(0, 'scripts')
import snapshot as S

MASK = (1 << 63) - 1
FILES = {'MODWAR22': 'modwar22', 'YAMYAMOK': 'yamyamok', 'BLACKOP6': 'blackop6', 'BLACKOP7': 'blackop7'}
left = set(int(x, 16) for x in open('logs/mw7_image_unnamed.txt'))
named = [n.strip() for n in open('logs/mw7_image_names.txt', encoding='utf-8')]
named_ids = set(S.fnv1a(n, 'MODWAR7', 'image') & MASK for n in named)
print('unnamed', len(left), 'named', len(named_ids))

other = {}
for game, f in FILES.items():
    snap = S.read('snapshots/%s.ids' % f)
    other[game] = set(i & MASK for i in snap.by_pool()['image'])
    print(game, 'images', len(other[game]), 'shared with MW7 unnamed', len(left & other[game]), 'shared with MW7 named', len(named_ids & other[game]))
anyother = set().union(*other.values())
print('unnamed in any other game', len(left & anyother), 'MW7-only unnamed', len(left - anyother))
print('named in any other game', len(named_ids & anyother), 'MW7-only named', len(named_ids - anyother))

only = [n for n in named if (S.fnv1a(n, 'MODWAR7', 'image') & MASK) not in anyother]
shared = [n for n in named if (S.fnv1a(n, 'MODWAR7', 'image') & MASK) in anyother]
print('heads MW7-only named', collections.Counter(n.split('_')[0] for n in only).most_common(30))
print('heads shared named', collections.Counter(n.split('_')[0] for n in shared).most_common(30))

# The published image table: what do images look like when somebody can read them?
all_img = list(set(n.strip().lower() for n in S.table_names('fnv1a_ximages_v2')))
print('v2 image names', len(all_img))
print('v2 heads', collections.Counter(n.split('_')[0] for n in all_img).most_common(40))
print('v2 tails', collections.Counter(n.rsplit('_', 1)[-1] for n in all_img).most_common(40))
random.seed(7)
print('sample v2:')
for n in random.sample(all_img, 40):
    print('  ', n)
print('sample MW7-only named:')
for n in random.sample(only, min(50, len(only))):
    print('  ', n)
