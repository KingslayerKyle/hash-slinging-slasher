"""Fill material suffix variants among observed endings (_opacity/_noshadow/...).

Only for names that already wear one of the suffixes — don't append blindly to every material.

    python contrib/material_suffix_alts.py | confirm_list - --game MODWAR7 \
        --label "material suffix alts" --script contrib/material_suffix_alts.py
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
while not (ROOT / "scripts" / "snapshot.py").is_file() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
sys.path.insert(0, str(ROOT / "scripts"))
import snapshot  # noqa: E402

SUFS = (
    "_opacity",
    "_noshadow",
    "_shadow",
    "_lit",
    "_unlit",
    "_emissive",
    "_gloss",
    "_metal",
    "_ct",
    "_sbx",
)


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
        hit = None
        for s in SUFS:
            if n.endswith(s):
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
        if base not in seen:
            seen.add(base)
            out.write(base + "\n")


if __name__ == "__main__":
    main()
