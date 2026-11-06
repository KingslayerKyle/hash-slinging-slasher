"""Sound files whose path body+encoding already exist under >=2 title tops, missing tops filled.

ATF recovered `iw9/...` and `rex/...` cells; this asks whether a path body shared by two
title roots also exists under the other frequent roots (iw9/t10/rex/s6/jup/core/sat/...).

    python contrib/sound_topseg_swap.py | confirm_list - --game MODWAR7 --anyway \
        --label "sound title-top segment swap" --script contrib/sound_topseg_swap.py
"""
from collections import Counter, defaultdict
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent
while not (ROOT / "scripts" / "snapshot.py").is_file() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
sys.path.insert(0, str(ROOT / "scripts"))
import snapshot  # noqa: E402

TAIL = re.compile(r"^(?P<head>.+?)(?P<enc>\.[a-z]{1,4}\.\d{1,3}\.\d{4,6}\.[a-z_]+)$")
MIN_TOP = 5000


def named_sounds():
    names = set()
    for n in snapshot.table_names("fnv1a_xsounds_v2"):
        names.add(n.lower())
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
    return names


def main():
    first = Counter()
    by_rest = defaultdict(set)
    for n in named_sounds():
        m = TAIL.match(n)
        if not m or "/" not in m["head"]:
            continue
        head, enc = m["head"], m["enc"]
        top, _, rest = head.partition("/")
        first[top] += 1
        by_rest[(rest, enc)].add(top)

    tops = {t for t, c in first.items() if c >= MIN_TOP}
    out = sys.stdout
    seen = set()
    for (rest, enc), have_tops in by_rest.items():
        if len(have_tops) < 2:
            continue
        for t in tops:
            if t in have_tops:
                continue
            cand = f"{t}/{rest}{enc}"
            if cand not in seen:
                seen.add(cand)
                out.write(cand + "\n")


if __name__ == "__main__":
    main()
