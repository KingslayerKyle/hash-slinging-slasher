"""BO7 packed material codes (`twc/*339n_593dn_232n`) as a compiled plan.

80,298 named BO7 materials are `twc/` codes: `*` then two to four `_`-joined tokens, each a small
number with `n` or `dn` after it (measured 2026-10-09: 223,141 `n`, 3,267 `dn`, 2,839 bare; 99% of
the numbers below 1,931). The numbers are not hashes, so the space is enumerable: every token over
0..N-1 in all three spellings, under every `tw*` directory, two and three tokens long.

Writes `<out>_begin.txt`, `<out>_tok.txt`, `<out>_tok_.txt` and the plans `<out>2.txt`, `<out>3.txt`.
Spent by: the token range given; widen --max if the measured range grows.
"""
from pathlib import Path
import argparse

ROOT = next((p for p in Path(__file__).resolve().parents
             if (p / 'scripts/snapshot.py').is_file()), None)
if ROOT is None:
    raise SystemExit('Run this generator from a solver checkout')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max", type=int, default=2500)
    ap.add_argument("--out", default="plans/w_twc")
    a = ap.parse_args()
    o = a.out
    toks = [f"{k}{s}" for k in range(a.max) for s in ("n", "dn", "")]
    (ROOT / f"{o}_begin.txt").write_text("".join(f"{d}/*\n" for d in ("twc", "tw", "twcj", "twck")))
    (ROOT / f"{o}_tok.txt").write_text("\n".join(toks) + "\n")
    (ROOT / f"{o}_tok_.txt").write_text("\n".join(t + "_" for t in toks) + "\n")
    pairs = ROOT / f"{o}_pair_.txt"
    with pairs.open("w") as f:
        for x in toks:
            for y in toks:
                f.write(f"{x}_{y}_\n")
    (ROOT / f"{o}2.txt").write_text(
        f"label: packed material codes, two tokens\nbegin: @{o}_begin.txt\nstem: @{o}_tok_.txt\nend: @{o}_tok.txt\nbare: no\n")
    (ROOT / f"{o}3.txt").write_text(
        f"label: packed material codes, three tokens\nbegin: @{o}_begin.txt\nstem: @{o}_pair_.txt\nend: @{o}_tok.txt\nbare: no\n")


if __name__ == "__main__":
    main()
