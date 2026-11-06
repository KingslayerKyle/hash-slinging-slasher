"""Swap mid-frequency title/theme codes inside material names (sat/rex/jup/civ/mil/...)."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
while not (ROOT / "scripts" / "snapshot.py").is_file() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
sys.path.insert(0, str(ROOT / "scripts"))
import snapshot  # noqa: E402

# Skip directory-like heads (twc/tm/tw/m/i); keep theme/title codes.
CODES = [
    "jup", "t10", "iw9", "sat", "rex", "s6", "t9", "t8", "veh9",
    "civ", "mil", "zm", "mp", "sgon", "rvl", "dst", "vfx", "att",
    "wpn", "veh", "ee", "core",
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
    for n in mats:
        for a in CODES:
            keyed = f"_{n}_"
            if f"_{a}_" not in keyed and f"/{a}_" not in n and f"/{a}/" not in f"/{n}/":
                # also allow token after dir slash: i/decal_rex_...
                if f"_{a}_" not in f"_{n.replace('/', '_')}_":
                    continue
            for b in CODES:
                if a == b:
                    continue
                cand = n.replace(a, b, 1)
                if cand not in seen and cand != n:
                    seen.add(cand)
                    out.write(cand + "\n")


if __name__ == "__main__":
    main()
