"""Swap title codes in sound file path bodies."""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent
while not (ROOT / "scripts" / "snapshot.py").is_file() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
sys.path.insert(0, str(ROOT / "scripts"))
import snapshot  # noqa: E402

TAIL = re.compile(r"^(?P<head>.+?)(?P<enc>\.[a-z]{1,4}\.\d{1,3}\.\d{4,6}\.[a-z_]+)$")
CODES = ["jup", "t10", "iw9", "sat", "rex", "s6", "t9", "t8", "veh9", "core", "mp", "zm"]


def main():
    names = {n.lower() for n in snapshot.table_names("fnv1a_xsounds_v2")}
    an = ROOT / "state" / "an"
    if an.is_dir():
        for p in an.glob("*_sound_asset.named"):
            for line in p.open(encoding="utf-8"):
                n = line.strip().lower()
                if n:
                    names.add(n)
    for p in (ROOT / "findings").rglob("sound_asset*.txt"):
        for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
            _, _, n = line.partition(",")
            if n:
                names.add(n.lower())
    seen = set()
    out = sys.stdout
    for n in names:
        m = TAIL.match(n)
        if not m:
            continue
        head, enc = m["head"], m["enc"]
        for a in CODES:
            if f"/{a}/" not in f"/{head}/" and f"_{a}_" not in f"_{head}_" and not head.startswith(a + "/"):
                continue
            for b in CODES:
                if a == b:
                    continue
                cand = head.replace(a, b, 1) + enc
                if cand not in seen:
                    seen.add(cand)
                    out.write(cand + "\n")


if __name__ == "__main__":
    main()
