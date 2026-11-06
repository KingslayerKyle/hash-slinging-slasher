"""Season/color token alts on sound file paths (basename tokens only)."""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent
while not (ROOT / "scripts" / "snapshot.py").is_file() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
sys.path.insert(0, str(ROOT / "scripts"))
import snapshot  # noqa: E402

TAIL = re.compile(r"^(?P<head>.+?)(?P<enc>\.[a-z]{1,4}\.\d{1,3}\.\d{4,6}\.[a-z_]+)$")
GROUPS = [
    ["autumn", "spring", "summer", "winter", "fall", "dry", "wet", "snow", "dead"],
    ["gray", "grey", "red", "blue", "green", "yellow", "white", "black"],
    ["plr", "npc"],
    ["small", "large", "medium"],
    ["01", "02", "03", "04", "05", "06", "07", "08"],
]


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
        for g in GROUPS:
            for a in g:
                if f"_{a}_" not in f"_{head}_":
                    continue
                for b in g:
                    if a == b:
                        continue
                    cand = head.replace(a, b, 1) + enc
                    if cand not in seen:
                        seen.add(cand)
                        out.write(cand + "\n")


if __name__ == "__main__":
    main()
