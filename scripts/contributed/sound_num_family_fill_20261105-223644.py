"""Fill holes in numbered modern sound basename families (stem_01..N) within a folder+encoding.

Seeded by topseg finds that completed t10/.../dst_wood_crate_small_01..08 as a block.

    python contrib/sound_num_family_fill.py | confirm_list - --game MODWAR7 \
        --label "sound numbered family gap fill" --script contrib/sound_num_family_fill.py
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
NUM = re.compile(r"^(?P<pre>.*_)(?P<num>\d{2,3})$")


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

    fam = defaultdict(set)
    for n in names:
        m = TAIL.match(n)
        if not m:
            continue
        head, enc = m["head"], m["enc"]
        d, _, base = head.rpartition("/")
        nm = NUM.match(base)
        if not nm:
            continue
        fam[(d, nm["pre"], enc)].add(int(nm["num"]))

    seen = set()
    out = sys.stdout
    for (d, pre, enc), nums in fam.items():
        if len(nums) < 2:
            continue
        lo, hi = min(nums), max(nums)
        if hi - lo + 1 > 40:
            continue
        width = max(len(str(max(nums))), 2)
        for i in range(1, hi + 5):
            if i in nums:
                continue
            base = f"{pre}{i:0{width}d}"
            cand = f"{d}/{base}{enc}" if d else f"{base}{enc}"
            if cand not in seen:
                seen.add(cand)
                out.write(cand + "\n")


if __name__ == "__main__":
    main()
