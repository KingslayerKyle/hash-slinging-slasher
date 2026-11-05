"""Tighter modern fly/ path fill: only between directories that already share a basename.

The unrestricted modern_fly_path_fill cross product returned 0 on MODWAR7. This only
offers a basename from dir A to dir B when A and B already share at least one basename,
then pairs with tails seen >=3 times.

    python contrib/modern_fly_pair_fill.py | confirm_list - --game MODWAR7 \\
        --label "modern fly pair-linked path fill" --script contrib/modern_fly_pair_fill.py
"""
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent
while not (ROOT / "scripts" / "snapshot.py").is_file() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
sys.path.insert(0, str(ROOT / "scripts"))
import snapshot

TAIL = re.compile(r"(\.[a-z]{1,4}\.\d+\.\d+\.[a-z_]+)$")


def names():
    out = set(n.lower() for n in snapshot.table_names("fnv1a_xsounds_v2"))
    for top in ("findings", "submissions", "all_names"):
        base = ROOT / top
        if not base.exists():
            continue
        for path in base.rglob("sound_asset*.txt"):
            for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
                _, sep, name = line.partition(",")
                if sep:
                    out.add(name.lower())
    return out


def main():
    rows = []
    for n in names():
        m = TAIL.search(n)
        if not m:
            continue
        head, tail = n[: m.start()], m.group(1)
        if "/fly/" not in "/" + head and not head.startswith("fly/"):
            continue
        parts = head.split("/")
        if len(parts) < 3:
            continue
        rows.append((tuple(parts[:-1]), parts[-1], tail))

    by_dir = defaultdict(set)
    by_base = defaultdict(set)
    tails = Counter()
    for d, b, t in rows:
        by_dir[d].add(b)
        by_base[b].add(d)
        tails[t] += 1

    pair_bases = defaultdict(set)
    for b, ds in by_base.items():
        for a, c in combinations(sorted(ds), 2):
            pair_bases[(a, c)].add(b)

    ends = [t for t, c in tails.most_common() if c >= 3]
    have = {n for n in names() if TAIL.search(n)}
    print(
        f"pair-linked fly fill: {len(pair_bases)} dir-pairs, {len(ends)} tails",
        file=sys.stderr,
    )
    total = 0
    for (a, c), _shared in pair_bases.items():
        for src, dst in ((a, c), (c, a)):
            for b in by_dir[src] - by_dir[dst]:
                stem = "/".join(dst) + "/" + b
                for e in ends:
                    cand = stem + e
                    if cand not in have:
                        print(cand)
                        total += 1
    print(f"{total} candidates", file=sys.stderr)


if __name__ == "__main__":
    main()
