"""How much of each modern image pool is packed `A&B~N` names, and is N a function of A&B?

Decides whether MW7's unnamed images are reachable at all: a `~N` tail with an unknown 64-bit N carries
no information, because for any prefix some N reaches any target id.
"""
import collections
import sys

sys.path.insert(0, 'scripts')
import snapshot as S

MASK = (1 << 63) - 1
names = set(n.strip().lower() for n in S.table_names('fnv1a_ximages_v2'))
names |= set(n.strip().lower() for n in S.confirmed_names('image'))
print('image names', len(names))
packed = [n for n in names if '~' in n and n.rsplit('~', 1)[1].isdigit()]
amp = [n for n in packed if '&' in n]
print('with ~digits', len(packed), 'of which with &', len(amp))

groups = collections.defaultdict(set)
for n in packed:
    a, b = n.rsplit('~', 1)
    groups[a].add(b)
print('distinct bodies', len(groups), 'bodies with >1 N', sum(len(v) > 1 for v in groups.values()),
      'max N per body', max(len(v) for v in groups.values()))
for a, v in sorted(groups.items(), key=lambda kv: -len(kv[1]))[:6]:
    print('  ', a, sorted(v)[:4])

hashes = {n: S.fnv1a(n, 'MODWAR7', 'image') & MASK for n in names}
inv = collections.defaultdict(list)
for n, h in hashes.items():
    inv[h].append(n)

allpools = {}
for game, f in [('MODWAR22', 'modwar22'), ('YAMYAMOK', 'yamyamok'), ('BLACKOP6', 'blackop6'), ('BLACKOP7', 'blackop7'), ('MODWAR7', 'modwar7')]:
    ids = set(i & MASK for i in S.read('snapshots/%s.ids' % f).by_pool()['image'])
    allpools[game] = ids
    hit = [n for h in ids if h in inv for n in inv[h]]
    p = sum('~' in n and n.rsplit('~', 1)[1].isdigit() for n in hit)
    tails = collections.Counter(n.rsplit('~', 1)[0].rsplit('_', 1)[-1] for n in hit if '~' in n and n.rsplit('~', 1)[1].isdigit())
    print(game, 'pool', len(ids), 'named', len(hit), 'packed named', p, 'plain named', len(hit) - p,
          'unnamed', len(ids) - len(set(hashes[n] for n in hit)))
    print('   packed tails', tails.most_common(8))

# Are packed names shared between titles, the way plain ones are?
pk = {hashes[n] for n in packed}
games = list(allpools)
for i, a in enumerate(games):
    print(a, [(b, len(pk & allpools[a] & allpools[b])) for b in games[i + 1:]])
