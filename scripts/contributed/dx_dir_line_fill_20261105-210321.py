"""Fill missing dx_<speaker>_<line> cells within a shared sound-file directory.

Inside one directory, several speakers often share the same line tails. Offer every
speaker that directory already uses every line any sibling speaker has, under tails
seen >=3 times.

    python contrib/dx_dir_line_fill.py | confirm_list - --game MODWAR7 \\
        --label "dx per-dir line fill" --script contrib/dx_dir_line_fill.py
"""
from collections import Counter, defaultdict
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent
while not (ROOT / "scripts" / "snapshot.py").is_file() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
sys.path.insert(0, str(ROOT / "scripts"))
import snapshot

TAIL = re.compile(r"(\.[a-z]{1,4}\.\d+\.\d+\.[a-z_]+)$")
SPK = re.compile(r"^(dx_[a-z0-9]+_)(.+)$")


def names():
    out = set(n.lower() for n in snapshot.table_names("fnv1a_xsounds_v2"))
    for top in ("findings", "submissions", "all_names"):
        base = ROOT / top
        if not base.exists():
            continue
        for path in base.rglob("sound_asset*.txt"):
            for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
                _, sep, name = line.partition(",")
                if sep:
                    out.add(name.lower())
    return out


def main():
    by_dir = defaultdict(set)
    tails = Counter()
    for n in names():
        if "/dx_" not in n and not n.startswith("dx_"):
            continue
        m = TAIL.search(n)
        if not m:
            continue
        head, tail = n[: m.start()], m.group(1)
        d, _, base = head.rpartition("/")
        if not base.startswith("dx_"):
            continue
        by_dir[d].add(base)
        tails[tail] += 1

    ends = [t for t, c in tails.most_common() if c >= 3]
    have = {n for n in names() if TAIL.search(n)}
    total = 0
    for d, bases in by_dir.items():
        by_spk = defaultdict(set)
        lines = set()
        for b in bases:
            m = SPK.match(b)
            if not m:
                continue
            by_spk[m.group(1)].add(m.group(2))
            lines.add(m.group(2))
        if len(by_spk) < 2:
            continue
        for spk, known in by_spk.items():
            for line in lines:
                if line in known:
                    continue
                stem = (d + "/" if d else "") + spk + line
                for e in ends:
                    cand = stem + e
                    if cand not in have:
                        print(cand)
                        total += 1
    print(f"dx dirs={len(by_dir)} candidates={total}", file=sys.stderr)


if __name__ == "__main__":
    main()
