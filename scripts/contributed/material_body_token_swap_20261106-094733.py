"""Within each material directory, swap the body's first underscore token among frequent tops.

Streams candidates (no giant in-memory set). MIN_TOP keeps the product tractable.

    python contrib/material_body_token_swap.py | confirm_list - --game MODWAR7 \
        --label "material body first-token swap" --script contrib/material_body_token_swap.py
"""
from collections import Counter
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
while not (ROOT / "scripts" / "snapshot.py").is_file() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
sys.path.insert(0, str(ROOT / "scripts"))
import snapshot  # noqa: E402

MIN_TOP = 2000


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

    first = Counter()
    rows = []
    for n in mats:
        if "/" not in n:
            continue
        d, _, body = n.partition("/")
        if "_" not in body:
            continue
        top, _, rest = body.partition("_")
        first[top] += 1
        rows.append((d, top, rest))
    tops = [t for t, c in first.items() if c >= MIN_TOP]
    topset = set(tops)
    out = sys.stdout
    for d, top, rest in rows:
        if top not in topset:
            continue
        for t in tops:
            if t == top:
                continue
            out.write(f"{d}/{t}_{rest}\n")


if __name__ == "__main__":
    main()
