"""How many strings in a harvested list hash into MW7's pools, named or not, per pool. Prints no names."""
import collections
import sys

sys.path.insert(0, 'scripts')
import snapshot as S

MASK = (1 << 63) - 1
snap = S.read('snapshots/modwar7.ids')
pool_of = {i & MASK: snap.pool_name(p) for i, p in snap.records}
known = S.known_hashes(game='MODWAR7')
for n in S.confirmed_names():
    known.add(S.fnv1a(n, 'MODWAR7', 'image') & MASK)
    known.add(S.fnv1a(n, 'MODWAR7', 'sound_alias') & MASK)

hits = collections.Counter()
fresh = collections.Counter()
samples = collections.defaultdict(list)
total = 0
for path in sys.argv[1:]:
    for line in open(path, encoding='utf-8', errors='replace'):
        name = line.strip()
        if not name:
            continue
        total += 1
        for kind in ('image', 'sound_alias'):
            h = S.fnv1a(name, 'MODWAR7', kind) & MASK
            if h in pool_of:
                pool = pool_of[h]
                if (kind == 'sound_alias') != (pool == 'sound_alias'):
                    continue
                hits[pool] += 1
                if h not in known:
                    fresh[pool] += 1
                    if len(samples[pool]) < 6:
                        samples[pool].append(name[:80])
print('strings', total)
print('hits by pool', hits.most_common(25))
print('NEW by pool', fresh.most_common(25))
for pool, values in samples.items():
    print(pool, values)
