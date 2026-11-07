"""Image names from the model, physics and scriptable names MW7's fast files embed.

    python contrib/mw7_embedded_stems.py
    confirm_plan plans/mw7_embedded/plan.txt --game MODWAR7

Modern titles keep xmodel names in the zone, so no search ever needed them, and they are not in any
table or submission: `submit` refuses modern models. That left the richest vocabulary in the build
outside every stem list. Images are named after the object they dress (`furniture_chair_lounge_...`,
`rex_parts_boots_work_b_black_thermalmap`), so each harvested name that lands in a real pool is a
stem, and its endings are the ones MW7's named images actually wear. Only harvested strings proven by
hashing into the capture are used, so the fast-file noise never reaches the search.
"""
import collections
import os
import re
import sys

sys.path.insert(0, 'scripts')
import snapshot as S

MASK = (1 << 63) - 1
OUT = 'plans/mw7_embedded'
SOURCE = {'xmodel', 'physicsasset', 'scriptable', 'xcompositemodel', 'material', 'image', 'decalvolumematerial', 'camo',
          'dynamicbones', 'physicsfxshape', 'particlesystem', 'reticle', 'attachmentblueprint', 'weaponblueprint', 'operatorskin'}
TAIL = re.compile(r'(_lod\d+|_mp|_sp|_dyn|_rigged|_s\d+_f\d+|_destr|_sfx|_phys|_cg|_br)+$')

snap = S.read('snapshots/modwar7.ids')
pool_of = {i & MASK: snap.pool_name(p) for i, p in snap.records}
stems = set()
for line in open('logs/mw7_ff_all.txt', encoding='utf-8', errors='replace'):
    name = line.strip()
    if pool_of.get(S.fnv1a(name, 'MODWAR7', 'image') & MASK) not in SOURCE:
        continue
    name = name.rsplit('/', 1)[-1]
    variants = {name, TAIL.sub('', name)}
    for value in list(variants):
        if value.startswith('mtl_'):
            variants.add(value[4:])
        else:
            variants.add('mtl_' + value)
    stems |= {v for v in variants if len(v) >= 5}

# Endings measured from names MW7's image pool is proven to hold, cut at every underscore.
endings = collections.Counter()
for line in open('logs/mw7_image_names.txt', encoding='utf-8'):
    parts = line.strip().split('_')
    for k in range(1, min(5, len(parts))):
        endings['_' + '_'.join(parts[-k:])] += 1
ends = [e for e, count in endings.items() if count >= 2 and not re.search(r'\d{3,}', e)]

begins = ['mtl_', 'li_', 'i_', 'c_', 'cm_', 'parts_', 'wpn_', 'veh_', 'rex_', 'rex_parts_', 'ui_rex_', 'ui_rew_', 'me_', 'as_', 'ee_', 'eu_', 'un_', 'body_', 'head_']
os.makedirs(OUT, exist_ok=True)
for filename, rows in (('stems.txt', stems), ('endings.txt', ends), ('begins.txt', begins)):
    with open(os.path.join(OUT, filename), 'w', encoding='utf-8', newline='\n') as handle:
        handle.write('\n'.join(sorted(rows)) + '\n')
with open(os.path.join(OUT, 'plan.txt'), 'w', encoding='utf-8', newline='\n') as handle:
    handle.write('label: images from names embedded in the MW7 fast files\n')
    handle.write('describe: harvested names proven against the capture x endings measured from named MW7 images\n')
    handle.write('begin: @%s/begins.txt\nstem: @%s/stems.txt\nend: @%s/endings.txt\nbare: yes\n' % (OUT, OUT, OUT))
print('stems', len(stems), 'endings', len(ends), 'begins', len(begins), 'product', len(stems) * (len(begins) + 1) * (len(ends) + 1))
