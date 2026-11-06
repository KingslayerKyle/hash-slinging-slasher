"""Fill missing sound encodings inside a directory that already holds the basename.

If a folder has `foo.lnl....` and also uses `.dnl....` on other files, emit
`foo.dnl....`. Seeded by ATF finds that were same-basename / different encoding.

    python contrib/dir_encoding_fill.py | confirm_list - --game MODWAR7 --anyway \
        --label "per-dir sound encoding fill" --script contrib/dir_encoding_fill.py
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


def named_sounds():
    names = set()
    for n in snapshot.table_names("fnv1a_xsounds_v2"):
        names.add(n.lower())
    for p in (ROOT / "findings").rglob("sound_asset*.txt"):
        for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
            _, _, n = line.partition(",")
            if n:
                names.add(n.lower())
    an = ROOT / "state" / "an"
    if an.is_dir():
        for p in an.glob("*_sound_asset.named"):
            for line in p.open(encoding="utf-8"):
                n = line.strip().lower()
                if n:
                    names.add(n)
    return names


def main():
    by_dir_base = defaultdict(set)
    encs_by_dir = defaultdict(set)
    for n in named_sounds():
        m = TAIL.match(n)
        if not m:
            continue
        head, enc = m["head"], m["enc"]
        d, _, b = head.rpartition("/")
        by_dir_base[(d, b)].add(enc)
        encs_by_dir[d].add(enc)

    seen = set()
    out = sys.stdout
    for (d, b), have in by_dir_base.items():
        missing = encs_by_dir[d] - have
        if not missing:
            continue
        for enc in missing:
            cand = f"{d}/{b}{enc}" if d else f"{b}{enc}"
            if cand not in seen:
                seen.add(cand)
                out.write(cand + "\n")


if __name__ == "__main__":
    main()
