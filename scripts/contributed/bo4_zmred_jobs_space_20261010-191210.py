"""jobs_space.txt: per hashed model placed in zm_red, the named models placed nearest it."""
import json, struct, os, re
from collections import Counter
import numpy as np
D = r'C:\tmp\bo4\glossary'
b = open(os.path.join(D, 'out', 'map', 'bo4', 'maps', 'zm_red.glb'), 'rb').read()
g = json.loads(b[20:20 + struct.unpack_from('<I', b, 12)[0]])
remaining = set(open(os.path.join(D, 'remaining_models.txt')).read().split())
vlm = json.load(open(os.path.join(D, 'vlm.json')))
MATS = json.load(open(os.path.join(D, 'remaining_mats.json')))
names, pos = [], []
for n in g['nodes']:
    nm = n.get('name', '')
    if nm.startswith('world/') or 'matrix' not in n:
        continue
    nm = re.sub(r'\.\d+$', '', nm)
    names.append(nm)
    pos.append(n['matrix'][12:15])
pos = np.array(pos)
names = np.array(names)
hashed = np.array([x.startswith('xmodel_') for x in names])
R = float(os.environ.get('R', 600))
K = int(os.environ.get('K', 30))
NUM = ['%02d' % i for i in range(1, 21)] + [str(i) for i in range(1, 10)] + list('abcd') + \
      ['%02d%s' % (i, c) for i in range(1, 6) for c in 'abc']
jobs = 0
with open(os.path.join(D, 'jobs_space.txt'), 'w') as f:
    for m in sorted(set(names[hashed]) | set(MATS)):
        if m not in remaining:
            continue
        near = Counter()
        for p in pos[names == m]:
            d = np.linalg.norm(pos - p, axis=1)
            for j in np.argsort(d)[:200]:
                if d[j] > R:
                    break
                if not hashed[j]:
                    near[names[j]] += 1
        sk, ws = set(), set(NUM)
        stems = set()
        for mat, imgs in MATS.get(m, []):
            if not mat.startswith(('xmaterial_', 'global_', '$')):
                stems.add(mat)
            for i in imgs:
                if i.startswith('i_'):
                    stems.add(re.sub(r'_[a-z]{1,3}$', '', i[2:]))
        for mat in stems:
            t = re.sub(r'^(mc/)?(mtl_)?', '', mat).split('_')
            ws.update(x for x in t if not x.isdigit())
            core = '_'.join(t[1:] if t[0] in ('t8', 't7', 'p8', 'p7') else t)
            for c in range(2, len(core.split('_')) + 1):
                sk.add('p8_' + '_'.join(core.split('_')[:c]))
        if not near and not sk:
            continue
        for nm, _ in near.most_common(K):
            t = nm.split('_')
            sk.add(nm)
            for c in range(3, len(t)):
                sk.add('_'.join(t[:c]))
            ws.update(x for x in t if not x.isdigit())
        for x in [vlm.get(m, {}).get('object', '')] + list(vlm.get(m, {}).get('nouns', [])):
            ws.update(re.findall(r'[a-z]+', str(x).lower()))
        ws.update(['dmg', 'damaged', 'broken', 'full', 'base', 'top', 'cap', 'piece', 'pieces', 'chunk', 'lod', 'sm', 'lg', 'med', 'large', 'small', 'left', 'right', 'mid', 'end', 'corner'])
        jobs += 1
        f.write('J %s\n' % m)
        f.writelines('S %s\n' % s for s in sorted(sk))
        f.writelines('W %s\n' % w for w in sorted(ws) if 1 <= len(w) <= 24)
print('placed hashed models with named neighbours:', jobs, 'of', len(remaining))
