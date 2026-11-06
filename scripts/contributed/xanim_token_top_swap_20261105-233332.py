"""Re-root xanim names by swapping the first underscore token among frequent tops.

    python contrib/xanim_token_top_swap.py | confirm_list - --game MODWAR7 \
        --label "xanim first-token top swap" --script contrib/xanim_token_top_swap.py
"""
from collections import Counter
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
while not (ROOT / "scripts" / "snapshot.py").is_file() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
sys.path.insert(0, str(ROOT / "scripts"))
import snapshot  # noqa: E402

MIN_TOP = 500


def main():
    names = {n.lower() for n in snapshot.table_names("fnv1a_xanims_v2")}
    an = ROOT / "state" / "an"
    if an.is_dir():
        for p in an.glob("*_xanim.named"):
            for line in p.open(encoding="utf-8"):
                n = line.strip().lower()
                if n:
                    names.add(n)
    for p in (ROOT / "findings").rglob("xanim*.txt"):
        for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
            _, _, n = line.partition(",")
            if n:
                names.add(n.lower())

    first = Counter()
    rows = []
    for n in names:
        if "_" not in n:
            continue
        top, _, rest = n.partition("_")
        first[top] += 1
        rows.append((top, rest))
    tops = [t for t, c in first.items() if c >= MIN_TOP]
    topset = set(tops)
    seen = set()
    out = sys.stdout
    for top, rest in rows:
        if top not in topset:
            continue
        for t in tops:
            if t == top:
                continue
            cand = f"{t}_{rest}"
            if cand not in seen:
                seen.add(cand)
                out.write(cand + "\n")


if __name__ == "__main__":
    main()
