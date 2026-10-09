"""twc 4-token names with the extra token in the middle of a known 3-token name: a_T_b_c, a_b_T_c.

contrib/twc_extend.py covers append/prepend; ~26% of known quads hold their known triple only
with the new token inside it. Quads' tokens are small (95% have every token <= 574, measured
2026-10-09), so T runs 0..--max as `n`. Printed, since the coupling (same known triple on both
sides of T) is not a cross product.

    python contrib/twc_middle.py | confirm_list - --game BLACKOP6
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
while not (ROOT / "scripts" / "snapshot.py").is_file() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
top = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
base = [l.strip()[5:] for l in (ROOT / "contrib" / "twc_ext4_base_begin.txt").open(encoding="utf-8")]
toks = [f"_{k}n_" for k in range(top + 1)]
w = sys.stdout.write
for b in base:
    a, s, c = b.split("_")
    p1, s1 = "twc/*" + a, s + "_" + c + "\n"
    p2, s2 = "twc/*" + a + "_" + s, c + "\n"
    w("".join(p1 + t + s1 for t in toks))
    w("".join(p2 + t + s2 for t in toks))
