"""Fill holes in modern path-style fly/ sound-file grids.

MW7's unnamed fly_ mass is mostly slash paths with encoding tails, not the legacy
fly_<axis>_<tail> shape. This takes verified modern sound files under fly/, keeps
directory prefixes that host >=2 basenames and basenames that appear under >=2
prefixes, and offers every missing prefix x basename under tails seen >=3 times.

    python contrib/modern_fly_path_fill.py | confirm_list - --game MODWAR7 \\
        --label "modern fly path fill" --script contrib/modern_fly_path_fill.py
"""
from collections import Counter, defaultdict
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
    out = set()
    for table in ("fnv1a_xsounds_v2",):
        out.update(n.lower() for n in snapshot.table_names(table))
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

    by_base = defaultdict(set)
    by_dir = defaultdict(set)
    tails = Counter()
    for dirs, base, tail in rows:
        by_base[base].add(dirs)
        by_dir[dirs].add(base)
        tails[tail] += 1

    dirs_ok = {d for d, bs in by_dir.items() if len(bs) >= 2}
    bases_ok = {b for b, ds in by_base.items() if len(ds) >= 2}
    ends = [t for t, c in tails.most_common() if c >= 3]
    print(
        f"modern fly path fill: {len(rows)} rows, {len(dirs_ok)} dirs x "
        f"{len(bases_ok)} bases x {len(ends)} tails",
        file=sys.stderr,
    )
    have = {n for n in names() if TAIL.search(n)}
    total = 0
    for d in sorted(dirs_ok):
        prefix = "/".join(d) + "/"
        for b in sorted(bases_ok):
            if b in by_dir[d]:
                continue
            for e in ends:
                cand = prefix + b + e
                if cand not in have:
                    print(cand)
                    total += 1
    print(f"{total} candidates", file=sys.stderr)


if __name__ == "__main__":
    main()
