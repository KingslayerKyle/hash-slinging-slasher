"""Re-root modern sound paths across frequent title tops (iw9/t10/rex/...).

Loose form: every named path body under a frequent top, spelled under every other.

    python contrib/sound_topseg_loose.py | confirm_list - --game MODWAR7 --anyway \
        --label "sound title-top loose re-root" --script contrib/sound_topseg_loose.py
"""
from collections import Counter
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


def main():
    names = {n.lower() for n in snapshot.table_names("fnv1a_xsounds_v2")}
    an = ROOT / "state" / "an"
    if an.is_dir():
        for p in an.glob("*_sound_asset.named"):
            for line in p.open(encoding="utf-8"):
                n = line.strip().lower()
                if n:
                    names.add(n)
    first = Counter()
    rows = []
    for n in names:
        m = TAIL.match(n)
        if not m or "/" not in m["head"]:
            continue
        top, _, rest = m["head"].partition("/")
        first[top] += 1
        rows.append((top, rest, m["enc"]))
    tops = [t for t, c in first.items() if c >= MIN_TOP]
    seen = set()
    out = sys.stdout
    for top, rest, enc in rows:
        if top not in tops:
            continue
        for t in tops:
            if t == top:
                continue
            cand = f"{t}/{rest}{enc}"
            if cand not in seen:
                seen.add(cand)
                out.write(cand + "\n")


if __name__ == "__main__":
    main()
