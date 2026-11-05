"""Re-root material paths by swapping the directory among frequent material dirs.

Seeded by heads3 recovering a block of `ntm/...` materials — asks whether bodies
under common dirs (twc/m/tm/...) also exist under the others.

    python contrib/material_dir_top_swap.py | confirm_list - --game MODWAR7 \
        --label "material directory top swap" --script contrib/material_dir_top_swap.py
"""
from collections import Counter, defaultdict
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
while not (ROOT / "scripts" / "snapshot.py").is_file() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
sys.path.insert(0, str(ROOT / "scripts"))
import snapshot  # noqa: E402

MIN_DIR = 20


def main():
    mats = {n.lower() for n in snapshot.table_names("fnv1a_xmaterials_v2")}
    an = ROOT / "state" / "an"
    if an.is_dir():
        for p in an.glob("*_material.named"):
            for line in p.open(encoding="utf-8"):
                n = line.strip().lower()
                if n:
                    mats.add(n)
    for p in (ROOT / "findings").rglob("material*.txt"):
        for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
            _, _, n = line.partition(",")
            if n:
                mats.add(n.lower())

    dirs = Counter()
    bodies = defaultdict(set)
    for n in mats:
        if "/" not in n:
            continue
        d, _, rest = n.partition("/")
        dirs[d] += 1
        bodies[rest].add(d)

    tops = [d for d, c in dirs.items() if c >= MIN_DIR]
    # Always include rare dirs that heads3 opened (ntm) if present.
    for extra in ("ntm",):
        if dirs.get(extra, 0) > 0 and extra not in tops:
            tops.append(extra)
    topset = set(tops)
    seen = set()
    out = sys.stdout
    for rest, have in bodies.items():
        sources = have & topset
        if not sources:
            continue
        for t in tops:
            if t in have:
                continue
            cand = f"{t}/{rest}"
            if cand not in seen:
                seen.add(cand)
                out.write(cand + "\n")


if __name__ == "__main__":
    main()

