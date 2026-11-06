"""Swap co-occurring material spelling alternatives (season/paint/size/warmth).

Seeded by heads3 `ntm/` materials carrying autumn/spring/painted_gray/yellow pairs.

    python contrib/material_token_alts.py | confirm_list - --game MODWAR7 \
        --label "material seasonal/paint/size token alts" --script contrib/material_token_alts.py
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
while not (ROOT / "scripts" / "snapshot.py").is_file() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
sys.path.insert(0, str(ROOT / "scripts"))
import snapshot  # noqa: E402

GROUPS = [
    ["autumn", "spring", "summer", "winter", "dry"],
    [
        "painted_gray",
        "painted_yellow",
        "painted_red",
        "painted_blue",
        "painted_green",
        "painted_white",
        "painted_black",
    ],
    ["warm", "cool", "cold"],
    ["wet", "dry"],
    ["small", "large", "medium"],
    ["01", "02", "03", "04", "05"],
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
                if a not in n:
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
