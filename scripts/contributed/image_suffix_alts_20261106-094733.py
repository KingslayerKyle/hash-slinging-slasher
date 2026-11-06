"""Image suffix alts among observed endings."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
while not (ROOT / "scripts" / "snapshot.py").is_file() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
sys.path.insert(0, str(ROOT / "scripts"))
import snapshot  # noqa: E402

SUFS = ("_c", "_n", "_s", "_g", "_e", "_a", "_m", "_l", "_opacity", "_noshadow", "_col", "_ng", "_masks")


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
    seen = set()
    out = sys.stdout
    for n in imgs:
        hit = None
        for s in SUFS:
            if n.endswith(s) and len(n) > len(s) + 2:
                hit = s
                break
        if not hit:
            continue
        base = n[: -len(hit)]
        for t in SUFS:
            if t == hit:
                continue
            cand = base + t
            if cand not in seen:
                seen.add(cand)
                out.write(cand + "\n")


if __name__ == "__main__":
    main()
