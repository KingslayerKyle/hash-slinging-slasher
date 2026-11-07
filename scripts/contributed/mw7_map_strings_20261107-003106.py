"""Every map-shaped string in the MW7 harvest, and which pool of the capture (if any) it lands in."""
import collections
import re
import sys

sys.path.insert(0, 'scripts')
import snapshot as S

MASK = (1 << 63) - 1
snap = S.read('snapshots/modwar7.ids')
pool_of = {i & MASK: snap.pool_name(p) for i, p in snap.records}
rows = [l.strip() for l in open('logs/mw7_ff_all.txt', encoding='utf-8', errors='replace') if l.strip()]
PAT = re.compile(r'compass_map|hajin|tumen|mp_rew_sierra|rew_sierra|wz_sierra|x01')

status = collections.Counter()
out = open('logs/mw7_map_strings.txt', 'w', encoding='utf-8')
for name in sorted(n for n in rows if PAT.search(n)):
    pool = pool_of.get(S.fnv1a(name, 'MODWAR7', 'image') & MASK, '-')
    out.write('%-22s %s\n' % (pool, name))
    family = 'compass' if 'compass_map' in name else 'hajin' if 'hajin' in name else 'tumen' if 'tumen' in name else 'sierra' if 'sierra' in name else 'x01'
    status[(family, pool)] += 1
out.close()
for key, count in sorted(status.items(), key=lambda kv: (kv[0][0], -kv[1])):
    print(key, count)

print('\ncompass names by map:')
maps = collections.defaultdict(lambda: collections.Counter())
for line in open('logs/mw7_map_strings.txt', encoding='utf-8'):
    pool, name = line.split(None, 1)
    name = name.strip()
    if 'compass_map' in name:
        m = re.search(r'compass_map_(?:mp_)?((?:re[wx]_)?(?:m_)?[a-z0-9]+)', name)
        maps[m.group(1) if m else name][pool] += 1
for m, c in sorted(maps.items()):
    print('  ', m, dict(c))

print('\nhajin strings:')
for line in open('logs/mw7_map_strings.txt', encoding='utf-8'):
    if 'hajin' in line:
        print('  ', line.strip()[:110])

print('\nx01 compass rows:')
for line in open('logs/mw7_map_strings.txt', encoding='utf-8'):
    if 'compass_map' in line and 'x01' in line:
        print('  ', line.strip()[:110])
