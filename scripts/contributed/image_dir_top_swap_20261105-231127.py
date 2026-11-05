"""Re-root image paths by swapping the first directory among frequent image dirs.

    python contrib/image_dir_top_swap.py | confirm_list - --game MODWAR7 \
        --label "image directory top swap" --script contrib/image_dir_top_swap.py
"""
from collections import Counter, defaultdict
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
while not (ROOT / "scripts" / "snapshot.py").is_file() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
sys.path.insert(0, str(ROOT / "scripts"))
import snapshot  # noqa: E402

MIN_DIR = 2000


def main():
    imgs = {n.lower() for n in snapshot.table_names("fnv1a_ximages_v2")}
    an = ROOT / "state" / "an"
    if an.is_dir():
        for p in an.glob("*_image.named"):
            for line in p.open(encoding="utf-8"):
                n = line.strip().lower()
                if n:
                    imgs.add(n)
    for p in (ROOT / "findings").rglob("image*.txt"):
        for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
            _, _, n = line.partition(",")
            if n:
                imgs.add(n.lower())

    dirs = Counter()
    bodies = defaultdict(set)
    for n in imgs:
        if "/" not in n:
            continue
        d, _, rest = n.partition("/")
        dirs[d] += 1
        bodies[rest].add(d)

    tops = [d for d, c in dirs.items() if c >= MIN_DIR]
    topset = set(tops)
    seen = set()
    out = sys.stdout
    for rest, have in bodies.items():
        if not (have & topset):
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
