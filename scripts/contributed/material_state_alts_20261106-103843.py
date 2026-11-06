"""Material wear/damage/lod token alternatives."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
while not (ROOT / "scripts" / "snapshot.py").is_file() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
sys.path.insert(0, str(ROOT / "scripts"))
import snapshot  # noqa: E402

GROUPS = [
    ["clean", "dirty", "rust", "rusty", "old", "new", "pristine", "burnt", "burned"],
    ["dmg", "dest", "destroyed", "broken"],
    ["lod0", "lod1", "lod2"],
]


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
    seen = set()
    out = sys.stdout
    for g in GROUPS:
        for n in mats:
            for a in g:
                if f"_{a}_" not in f"_{n}_":
                    continue
                for b in g:
                    if a == b:
                        continue
                    cand = n.replace(a, b, 1)
                    if cand not in seen and cand != n:
                        seen.add(cand)
                        out.write(cand + "\n")


if __name__ == "__main__":
    main()
