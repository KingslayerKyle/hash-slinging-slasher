"""Operator voice-line sound files: every operator crossed with every line any operator speaks.

A modern operator line is `<root>/op/<dir>/dx_op_<op>_<ctx>_<spk>_<code>_<phrase>[_opgN].<tail>`
(`iw9/op/gaz/dx_op_gaz1_bttl_gazz_vkbo_sunktheirboat_opg3.snn.20.48000.english`). The context
(`ping`, `bttl`), the line code and often the phrase are shared across operators, so each
operator's (dir, op, spk, opg style, tail) is crossed with every (ctx, code, phrase) attested under
the same root. `operator_vo_grid` does this for aliases; this is the file side.

Spent by: the operator sound-file corpus as it stands; re-run after it grows.
"""
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
R = re.compile(r"^([a-z0-9]+)/op/([^/]+)/dx_op_([a-z0-9]+)_([a-z]+)_([a-z0-9]+)_([a-z0-9]+)_(.+?)(_opg\d+)?"
               r"(\.[a-z]+\.\d+\.\d+\.[a-z_]+)$")


def main():
    srcs = list((ROOT / "cod-name-db" / "csv").glob("fnv1a_xsounds*.csv"))
    for folder in ("findings", "submissions"):
        srcs += list((ROOT / folder).rglob("sound_asset*.txt"))
    ops, lines, known = defaultdict(set), defaultdict(set), set()
    for p in srcs:
        for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
            k, sep, v = line.partition(",")
            v = (v if sep else k).strip().lower()
            m = R.match(v)
            if not m:
                continue
            known.add(v)
            root, d, op, ctx, spk, code, phrase, opg, tail = m.groups()
            ops[root].add((d, op, spk, opg or "", tail))
            lines[root].add((ctx, code, phrase))
    n = 0
    for root in ops:
        for d, op, spk, opg, tail in ops[root]:
            for ctx, code, phrase in lines[root]:
                c = f"{root}/op/{d}/dx_op_{op}_{ctx}_{spk}_{code}_{phrase}{opg}{tail}"
                if c not in known:
                    print(c)
                    n += 1
    print(f"{sum(map(len, ops.values()))} operators, {sum(map(len, lines.values()))} lines, {n:,} candidates",
          file=sys.stderr)


if __name__ == "__main__":
    main()
