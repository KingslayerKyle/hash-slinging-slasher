"""MW7 minimap images: compass_map_* for every map the installed build names, in every shape earlier titles used.

    python contrib/mw7_compass_maps.py --out plans/mw7_compass
    confirm_plan plans/mw7_compass/plan.txt --game MODWAR7

Measured off MWII, MWIII, BO6 and BO7 names, the map you pull up in game is a compass image:

    compass_map_mp_<map>                         whole map
    compass_map_mp_<map>_<xx>_<yy>               16x16 tile grid (saw_sierra, saw_avalon)
    compass_map_mp_<map>_ob_<xx>_<yy>            (jup_bigmap_ob, sat_lm_avalon_ob)
    compass_map_mp_<map>_bigmap_<xx>_<yy>        (codcaster_compass_map_mp_jup_bigmap)
    compass_map_<mode>_<map>_floor_<n>           multi level (cp_*_apt_floor_1, zm_t10_*_floor_1)
    compass_map_<mode>_<map>_floor_<n>_<xx>_<yy> multi level tiled (zm_sat_firefly_floor_1_09_05)
    codcaster_ / brcodcaster_ prefixes           the observer copies of each

Written as a plan rather than printed, because it is a pure cross product: beginnings x maps x endings.
The maps come from the fast file names, plus title codes crossed with the bare codenames, so a Warzone
map named wz_hajin elsewhere is asked for under every plausible spelling.
"""
import argparse
import glob
import os
import re

parser = argparse.ArgumentParser()
parser.add_argument('--root', default=r'C:\Program Files (x86)\Steam\steamapps\common\Call of Duty HQ\cod26')
parser.add_argument('--out', default='plans/mw7_compass')
parser.add_argument('--extra', nargs='*', default=['hajin', 'x01', 'sierra', 'tumen', 'zodiac', 'escape', 'dmz_freshstart', 'dmz'])
options = parser.parse_args()

maps = set()
for path in glob.glob(os.path.join(options.root, '*.ff')):
    stem = os.path.basename(path)[:-3]
    stem = re.sub(r'^(eng|ens)_', '', stem)
    stem = re.sub(r'_[0-9a-f]{8}_\d+_tr$', '', stem)
    stem = re.sub(r'_(tr|cg|entities|subset_ai|load)$', '', stem)
    if stem.startswith('mp_') and len(stem.split('_')) <= 4:
        maps.add(stem[3:])
for word in options.extra:
    for code in ('rew', 'rex', 'rew_wz', 'rex_wz', 'wz', 'rew_br', 'rex_br', 'rew_dmz', 'rex_dmz', 'dmz', 'br', 'wz_rew', 'wz_rex', 'dmz_rex', 'dmz_rew'):
        maps.add('%s_%s' % (code, word))
    maps.add(word)

grid = set()
for x in range(0, 33):
    for y in range(0, 33):
        grid.add('%02d_%02d' % (x, y))
        grid.add('%d_%d' % (x, y))
grid = sorted(grid)

levels = ['']
for pattern in ('floor_%d', 'floor%d', 'floor_%02d', 'level_%d', 'level%d', 'level_%02d', 'lvl_%d', 'lvl%d', 'l%d', 'f%d', 'b%d',
                'basement_%d', 'layer_%d', 'map_%d', 'tier_%d', 'deck_%d', 'zone_%d', 'section_%d', 'area_%d', 'part_%d', 'sub_%d', 'ug_%d', 'alt_%d', 'v%d'):
    levels += [pattern % n for n in range(0, 9)]
levels += ['upper', 'lower', 'top', 'bottom', 'underground', 'surface', 'interior', 'exterior', 'ground', 'basement',
           'bunker', 'tunnel', 'tunnels', 'vault', 'mid', 'middle', 'lobby', 'above', 'below', 'indoor', 'outdoor', 'roof', 'sewer', 'overworld', 'underworld']
middles = ['', 'bigmap', 'ob', 'bigmap_ob', 'lm', 'lm_ob', 'gw', 'gw2', 'am', 'pm', 'night', 'day', 'escort', 'dmz', 'exfil',
           'br', 'wz', 'large', 'small', 'tac', 'tacmap', 'full', 'fullmap', 'overhead', 'alt', 'v2', 'new', 'locale', 'map']

endings = set()
for middle in middles:
    for level in levels:
        parts = [p for p in (middle, level) if p]
        body = '_'.join(parts)
        endings.add('_' + body if body else '')
        for g in grid:
            endings.add('_' + '_'.join(parts + [g]))
endings.discard('')

leads = ['compass_map_', 'codcaster_compass_map_', 'brcodcaster_compass_map_', 'cb_compass_map_', 'compass_', 'map_', 'minimap_',
         'tacmap_', 'ui_map_', 'ui_minimap_', 'ui_compass_map_', 'ui_tacmap_', 'ui_rew_map_', 'ui_rex_map_', 'ui_rew_tacmap_',
         'ui_rex_tacmap_', 'ui_rew_minimap_', 'ui_rex_minimap_', 'ui_rew_compass_map_', 'ui_rex_compass_map_', 'hud_map_', 'hud_minimap_']
modes = ['mp_', 'wz_', 'br_', 'cp_', 'dmz_', '']
begins = sorted(lead + mode for lead in leads for mode in modes)

os.makedirs(options.out, exist_ok=True)
def write(name, rows):
    with open(os.path.join(options.out, name), 'w', encoding='utf-8', newline='\n') as handle:
        handle.write('\n'.join(sorted(rows)) + '\n')
write('begins.txt', begins)
write('maps.txt', maps)
write('endings.txt', endings)
with open(os.path.join(options.out, 'plan.txt'), 'w', encoding='utf-8', newline='\n') as handle:
    handle.write('label: mw7 compass map images, every map in the build x tile grids and levels\n')
    handle.write('begin: @%s/begins.txt\n' % options.out)
    handle.write('stem: @%s/maps.txt\n' % options.out)
    handle.write('end: @%s/endings.txt\n' % options.out)
    handle.write('bare: yes\n')
print('begins', len(begins), 'maps', len(maps), 'endings', len(endings), 'product', len(begins) * len(maps) * (len(endings) + 1))
