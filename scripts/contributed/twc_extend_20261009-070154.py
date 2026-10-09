"""twc terrain-blend materials one token longer than a known one, the new token anywhere in 0..7000.

Measured 2026-10-09 on 393k known twc names: 85% of known 4-token names contain a known 3-token
name as an ordered subsequence (59% as their prefix), 88% of 3-token names contain a known pair.
So a k-token name is a known (k-1)-token name with one more token, and that token can range over
the whole numeric alphabet (0..7000 as `n` and `dn`) because the known part pins the rest -- the
range plans only reached quads with every token <= 800.

Writes append/prepend plans for k = 3, 4 and 5 (contrib/twc_ext{3,4}_{app,pre}.plan.txt).

    python contrib/twc_extend.py [--dir tw] [extra seed folders]
    confirm_plan contrib/twc_ext4_app.plan.txt --game BLACKOP6
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
while not (ROOT / "scripts" / "snapshot.py").is_file() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
CONTRIB = ROOT / "contrib"
NL = chr(10)
DIR = "twc"
args = sys.argv[1:]
if args[:1] == ["--dir"]:
    DIR, args = args[1], args[2:]
extra = [Path(p) for p in args]
TAG = "" if DIR == "twc" else "_" + DIR


def known():
    srcs = list((ROOT / "cod-name-db" / "csv").glob("fnv1a_xmaterials_v2*.csv"))
    for top in ("all_names", "findings", "submissions"):
        srcs += list((ROOT / top).rglob("material*.txt"))
    for d in extra:
        srcs += list(d.rglob("*material*.txt"))
    for f in srcs:
        for line in f.open(encoding="utf-8", errors="replace"):
            n = line.rstrip("\r\n").partition(",")[2].lower()
            if n.startswith(DIR + "/*"):
                yield n[len(DIR) + 2:]


by = {2: set(), 3: set(), 4: set()}
for rest in known():
    t = rest.split("_")
    if len(t) in by:
        by[len(t)].add(rest)
tokens = [f"{k}n" for k in range(10001 if TAG else 7001)] + [f"{k}dn" for k in range(10001 if TAG else 7001)]
(CONTRIB / f"twc_ext{TAG}_tok_end.txt").write_text("".join("_" + t + NL for t in tokens), encoding="utf-8")
(CONTRIB / f"twc_ext{TAG}_tok_begin.txt").write_text("".join(DIR + "/*" + t + NL for t in tokens), encoding="utf-8")
for k in (3, 4, 5):
    base = sorted(by[k - 1])
    (CONTRIB / f"twc_ext{TAG}{k}_base_begin.txt").write_text("".join(DIR + "/*" + b + NL for b in base), encoding="utf-8")
    (CONTRIB / f"twc_ext{TAG}{k}_base_stem.txt").write_text("".join("_" + b + NL for b in base), encoding="utf-8")
    desc = (f"describe: every known {k - 1}-token twc name with one token 0..7000 (n and dn) added; "
            f"85% of known 4-token / 88% of 3-token twc names contain a known shorter one; see contrib/twc_extend.py")
    (CONTRIB / f"twc_ext{TAG}{k}_app.plan.txt").write_text(NL.join([
        f"label: {DIR} {k}-token names: known {k - 1}-token name + appended token", desc,
        f"stem: @contrib/twc_ext{TAG}{k}_base_begin.txt", f"end: @contrib/twc_ext{TAG}_tok_end.txt", ""]), encoding="utf-8")
    (CONTRIB / f"twc_ext{TAG}{k}_pre.plan.txt").write_text(NL.join([
        f"label: {DIR} {k}-token names: prepended token + known {k - 1}-token name", desc,
        f"begin: @contrib/twc_ext{TAG}_tok_begin.txt", f"stem: @contrib/twc_ext{TAG}{k}_base_stem.txt", ""]), encoding="utf-8")
    print(f"k={k}: {len(base)} known {k - 1}-token bases x {len(tokens)} tokens", file=sys.stderr)
