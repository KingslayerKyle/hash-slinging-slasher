"""Volume lighting textures: fill each content-hash group's own small axes.

Shapes: volume<V>_state<S>_<body>_<hex>_<n>, body = gi_xyz_texture_mip<M> | reflection_probes | ...
The hex is a content hash (written without leading zeros) and is never crossed between groups --
that is the trap METHODS.md method 11 warns about. Within one hex, everything else is crossed:
the volumes, states and bodies seen anywhere in the group, and n run from 0 past the group's max.
"""
import collections
import re
import sys

NAMED = sys.argv[1]
MODE = sys.argv[2] if len(sys.argv) > 2 else "stats"
EXTRA = int(sys.argv[3]) if len(sys.argv) > 3 else 64

rx = re.compile(r"^(volume-?\d+)_(state\d+)_(.+?)_([0-9a-f]{1,8})_(\d+)$")
groups = collections.defaultdict(lambda: [set(), set(), set(), -1, set()])
shapes = collections.Counter()
for line in open(NAMED, encoding="utf-8"):
    n = line.strip()
    m = rx.match(n)
    if not m:
        continue
    v, s, body, h, k = m.groups()
    g = groups[h]
    g[0].add(v); g[1].add(s); g[2].add(body); g[3] = max(g[3], int(k)); g[4].add(n)
    shapes[re.sub(r"\d+", "#", body)] += 1

if MODE == "stats":
    print("hex groups:", len(groups), " named:", sum(len(g[4]) for g in groups.values()))
    print("bodies:", shapes.most_common(10))
    total = 0
    for h, (vs, ss, bs, mx, have) in groups.items():
        total += len(vs) * len(ss) * len(bs) * (mx + 1 + EXTRA) - len(have)
    print("candidates (excluding named):", total)
    sys.exit()

for h, (vs, ss, bs, mx, have) in groups.items():
    for v in sorted(vs):
        for s in sorted(ss):
            for b in sorted(bs):
                for k in range(mx + 1 + EXTRA):
                    name = f"{v}_{s}_{b}_{h}_{k}"
                    if name not in have:
                        print(name)
