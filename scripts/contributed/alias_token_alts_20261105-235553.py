"""Season/color/size token alts on sound aliases.

    python contrib/alias_token_alts.py | confirm_list - --game MODWAR7 \
        --label "alias token alts colors+seasons" --script contrib/alias_token_alts.py
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
while not (ROOT / "scripts" / "snapshot.py").is_file() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
sys.path.insert(0, str(ROOT / "scripts"))
import snapshot  # noqa: E402

GROUPS = [
    ["autumn", "spring", "summer", "winter", "fall", "dry", "wet", "snow", "dead"],
    ["gray", "grey", "red", "blue", "green", "yellow", "white", "black", "orange", "brown", "pink", "purple", "tan", "gold", "silver"],
    ["warm", "cool", "cold"],
    ["small", "large", "medium"],
    ["plr", "npc"],
    ["01", "02", "03", "04", "05", "06", "07", "08"],
]


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
    for g in GROUPS:
        for n in names:
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
