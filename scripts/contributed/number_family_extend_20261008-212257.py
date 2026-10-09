"""Numbered families extended past the highest number anyone has published, at every number slot.

`ui_emblem_116`, `cer_ui_playercard_138`, `loading_jup_0022_preview`, `jup_card_n4917_14`: modern
UI and cosmetic assets are numbered series, and a published table holds whichever members somebody
happened to see. Gap filling (in derive_closure) only fills inside the observed range; the members
beyond it -- added later, or simply never exported -- are where this reaches.

For every known name and every run of digits in it, the family is (text before, text after, digit
width). Each family gets every number from 0 up to max(observed) + max(--extra, observed max / 2),
at the family's width, minus what is already known. Families whose ceiling would pass --cap are cut
there (a 4-digit cosmetic code slot is 10,000 by itself; that stays affordable).

    python contrib/number_family_extend.py | confirm_list - --game BLACKOP7 --script contrib/number_family_extend.py
"""
from pathlib import Path
import argparse
import collections
import re
import sys

ROOT = Path(__file__).resolve().parent
while not (ROOT / "scripts" / "snapshot.py").is_file() and ROOT != ROOT.parent:
    ROOT = ROOT.parent

DIGITS = re.compile(r"\d+")


def names():
    for f in sorted((ROOT / "cod-name-db" / "csv").glob("*.csv")):
        for line in f.open(encoding="utf-8", errors="replace"):
            yield line.rstrip("\r\n").partition(",")[2]
    for top in ("all_names", "submissions", "findings", "contrib/open_pr_names"):
        for f in sorted((ROOT / top).rglob("*.txt")):
            for line in f.open(encoding="utf-8", errors="replace"):
                key, sep, name = line.rstrip("\r\n").partition(",")
                if sep:
                    yield name


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--extra", type=int, default=40)
    ap.add_argument("--cap", type=int, default=10000)
    ap.add_argument("--min-members", type=int, default=2,
                    help="families seen with fewer distinct numbers are skipped")
    a = ap.parse_args()
    known = set()
    families = collections.defaultdict(set)
    for name in names():
        name = name.strip().lower()
        if not name or name in known or "~" in name or "&" in name or name.startswith("twc/"):
            continue
        known.add(name)
        for m in DIGITS.finditer(name):
            if len(m.group()) > 5:
                continue
            families[(name[: m.start()], name[m.end():], len(m.group()))].add(int(m.group()))
    out = sys.stdout
    total = 0
    for (pre, post, width), seen in families.items():
        if len(seen) < a.min_members:
            continue
        top = max(seen)
        ceiling = min(top + max(a.extra, top // 2), a.cap, 10 ** width - 1 if width > 1 else a.cap)
        for i in range(0, ceiling + 1):
            if i in seen:
                continue
            s = f"{i:0{width}d}" if width > 1 else str(i)
            cand = pre + s + post
            if cand not in known:
                out.write(cand + "\n")
                total += 1
    print(f"{len(families)} families, {total} candidates", file=sys.stderr)


if __name__ == "__main__":
    main()
