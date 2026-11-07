"""Harvested MW7 strings the capture cannot prove, kept only when they read like real names.

    python contrib/mw7_unproven_stems.py
    confirm_plan plans/mw7_unproven/plan.txt --game MODWAR7

`mw7_embedded_stems.py` used strings that hash into a pool, which is clean and also blind: a capture
holds only what was loaded, so an object whose own asset was never captured can still have captured
images. Most of the 2M strings are compressed noise, though, and crossing noise with endings only buys
coincidences. So a string survives only if nearly all its tokens occur in names known to be real, and
the endings are held to those a good number of MW7's named images wear, which keeps the chance figure
well under one.
"""
import collections
import os
import re
import sys

sys.path.insert(0, 'scripts')
import snapshot as S

MASK = (1 << 63) - 1
OUT = 'plans/mw7_unproven'
MIN_ENDING = int(sys.argv[1]) if len(sys.argv) > 1 else 12

snap = S.read('snapshots/modwar7.ids')
pool_of = {i & MASK: snap.pool_name(p) for i, p in snap.records}

vocabulary = collections.Counter()
for table in ('fnv1a_ximages_v2', 'fnv1a_xmaterials_v2', 'fnv1a_xanims_v2'):
    for name in S.table_names(table):
        vocabulary.update(re.split(r'[_/~&.]', name.strip().lower()))
for name in S.confirmed_names():
    vocabulary.update(re.split(r'[_/~&.]', name.strip().lower()))
common = {token for token, count in vocabulary.items() if count >= 3 and len(token) >= 2}
print('vocabulary', len(common))

def wordlike(name):
    tokens = [t for t in name.split('_') if t]
    if len(tokens) < 2:
        return False
    letters = [t for t in tokens if not t.isdigit()]
    if not letters:
        return False
    return sum(t in common for t in letters) / len(letters) >= 0.75

stems = set()
seen = 0
for line in open('logs/mw7_ff_all.txt', encoding='utf-8', errors='replace'):
    seen += 1
    raw = line.strip().rsplit('/', 1)[-1]
    for cut in (0, 1):
        name = raw[cut:]
        if len(name) < 8 or len(name) > 90 or not re.fullmatch(r'[a-z0-9_.\-]+', name):
            continue
        if (S.fnv1a(name, 'MODWAR7', 'image') & MASK) in pool_of:
            continue  # the proven half has already been run
        if wordlike(name):
            stems.add(name)
print('strings', seen, 'wordlike stems', len(stems))

endings = collections.Counter()
for line in open('logs/mw7_image_names.txt', encoding='utf-8'):
    parts = line.strip().split('_')
    for k in range(1, min(4, len(parts))):
        endings['_' + '_'.join(parts[-k:])] += 1
ends = [e for e, count in endings.items() if count >= MIN_ENDING and not re.search(r'\d{3,}', e)]

os.makedirs(OUT, exist_ok=True)
for filename, rows in (('stems.txt', stems), ('endings.txt', ends)):
    with open(os.path.join(OUT, filename), 'w', encoding='utf-8', newline='\n') as handle:
        handle.write('\n'.join(sorted(rows)) + '\n')
with open(os.path.join(OUT, 'plan.txt'), 'w', encoding='utf-8', newline='\n') as handle:
    handle.write('label: images from wordlike MW7 fast file strings the capture cannot prove\n')
    handle.write('describe: harvested strings whose tokens occur in known names x endings of named MW7 images\n')
    handle.write('begin: mtl_\nbegin: li_\nbegin: rex_\nstem: @%s/stems.txt\nend: @%s/endings.txt\nbare: yes\n' % (OUT, OUT))
print('endings', len(ends), 'product', len(stems) * 4 * (len(ends) + 1))
