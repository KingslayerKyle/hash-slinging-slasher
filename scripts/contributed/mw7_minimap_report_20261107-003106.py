"""A hash,name list of MW7 map images: proven against the capture, or only named by the build itself."""
import csv
import glob
import re
import sys

sys.path.insert(0, 'scripts')
import snapshot as S

MASK = (1 << 63) - 1
snap = S.read('snapshots/modwar7.ids')
pool_of = {i & MASK: snap.pool_name(p) for i, p in snap.records}

table = {}
for name in S.table_names('fnv1a_ximages_v2', 'fnv1a_xmaterials_v2'):
    table[S.fnv1a(name, 'MODWAR7', 'image') & MASK] = 'published table'
for path in glob.glob('submissions/**/*.txt', recursive=True):
    for line in open(path, encoding='utf-8', errors='replace'):
        name = line.partition(',')[2].strip() or line.strip()
        if 'compass_map' in name or 'deploy_map' in name:
            table.setdefault(S.fnv1a(name, 'MODWAR7', 'image') & MASK, 'merged submission')

names = set()
PAT = re.compile(r'(compass_map_[a-z0-9_]+|ui_rex_menu_dmz_deploy_map_[a-z0-9_]+)')
for line in open('logs/mw7_ff_all.txt', encoding='utf-8', errors='replace'):
    hit = PAT.search(line)
    if hit:
        names.add(hit.group(1))
for path in glob.glob('findings/modwar7/**/image*.txt', recursive=True):
    for line in open(path, encoding='utf-8', errors='replace'):
        name = line.partition(',')[2].strip() or line.strip()
        if 'compass_map' in name or 'deploy_map' in name:
            names.add(name)

rows = []
for name in sorted(names):
    h = S.fnv1a(name, 'MODWAR7', 'image')
    key = h & MASK
    pool = pool_of.get(key, '')
    state = 'in capture' if pool else 'build string only, not in capture'
    rows.append(('%016x' % key, name, pool, state, table.get(key, 'new' if pool else '')))
with open('logs/mw7_minimap_names.csv', 'w', newline='', encoding='utf-8') as handle:
    writer = csv.writer(handle)
    writer.writerow(['hash', 'name', 'capture_pool', 'state', 'already_known_from'])
    writer.writerows(rows)

print('rows', len(rows))
for row in rows:
    if 'x01' in row[1] and row[2]:
        print(row)
    if 'tumen' in row[1] and not re.search(r'_\d\d_\d\d$', row[1]):
        print(row)
    if 'deploy_map' in row[1]:
        print(row)
print('tumen tiles', sum(1 for r in rows if re.search(r'rew_tumen_\d\d_\d\d$', r[1])), 'in capture', sum(1 for r in rows if re.search(r'rew_tumen_\d\d_\d\d$', r[1]) and r[2]))
print('x01 strings', sum('x01' in r[1] for r in rows), 'in capture', sum('x01' in r[1] and bool(r[2]) for r in rows))
