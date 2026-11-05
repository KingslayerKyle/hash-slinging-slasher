"""Re-spell modern sound paths by swapping the second path segment among frequent mids.

Mirror of sound_topseg_loose for the category folder (wpn/op/fly/zm/...).

    python contrib/sound_midseg_loose.py | confirm_list - --game MODWAR7 \
        --label "sound mid-segment loose swap" --script contrib/sound_midseg_loose.py
"""
from collections import defaultdict
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent
while not (ROOT / "scripts" / "snapshot.py").is_file() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
sys.path.insert(0, str(ROOT / "scripts"))
import snapshot  # noqa: E402

TAIL = re.compile(r"^(?P<head>.+?)(?P<enc>\.[a-z]{1,4}\.\d{1,3}\.\d{4,6}\.[a-z_]+)$")
MIN_MID = 2000


def main():
    names = {n.lower() for n in snapshot.table_names("fnv1a_xsounds_v2")}
    an = ROOT / "state" / "an"
    if an.is_dir():
        for p in an.glob("*_sound_asset.named"):
            for line in p.open(encoding="utf-8"):
                n = line.strip().lower()
                if n:
                    names.add(n)
    from collections import Counter

    sec = Counter()
    rows = []
    for n in names:
        m = TAIL.match(n)
        if not m:
            continue
        parts = m["head"].split("/")
        if len(parts) < 3:
            continue
        top, mid, rest = parts[0], parts[1], "/".join(parts[2:])
        sec[mid] += 1
        rows.append((top, mid, rest, m["enc"]))
    mids = {s for s, c in sec.items() if c >= MIN_MID}
    by = defaultdict(set)
    for top, mid, rest, enc in rows:
        if mid not in mids:
            continue
        by[(top, rest, enc)].add(mid)
    seen = set()
    out = sys.stdout
    for (top, rest, enc), have in by.items():
        for mid in mids:
            if mid in have:
                continue
            cand = f"{top}/{mid}/{rest}{enc}"
            if cand not in seen:
                seen.add(cand)
                out.write(cand + "\n")


if __name__ == "__main__":
    main()
