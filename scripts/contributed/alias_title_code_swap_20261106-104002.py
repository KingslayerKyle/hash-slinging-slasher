"""Swap title codenames embedded in alias title-code swap (jup/t10/iw9/sat/...)."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
while not (ROOT / "scripts" / "snapshot.py").is_file() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
sys.path.insert(0, str(ROOT / "scripts"))
import snapshot  # noqa: E402

CODES = ["jup", "t10", "iw9", "sat", "rex", "s6", "t9", "t8", "veh9"]


def main():
    names = {n.lower() for n in snapshot.table_names("fnv1a_soundbanks_aliases_v2")}
    an = ROOT / "state" / "an"
    if an.is_dir():
        for p in an.glob("*_sound_alias.named"):
            for line in p.open(encoding="utf-8"):
                n = line.strip().lower()
                if n:
                    names.add(n)
    for p in (ROOT / "findings").rglob("sound_alias*.txt"):
        for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
            _, _, n = line.partition(",")
            if n:
                names.add(n.lower())
    seen = set()
    out = sys.stdout
    for n in names:
        for a in CODES:
            keyed = f"_{n}_"
            if f"_{a}_" not in keyed and f"/{a}_" not in n and not n.split("/")[-1].startswith(a + "_"):
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

