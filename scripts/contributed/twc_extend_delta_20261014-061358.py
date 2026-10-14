"""twc_extend.py, but only for the bases that are new since its last run.

twc_extend.py writes its base lists (contrib/twc_ext<TAG><k>_base_begin.txt) every time it runs, so
the previous lists are a record of what was already extended. This reads them, collects today's
known (k-1)-token names for each terrain directory (state/an/*_material.named, every modern game),
and writes plans over the difference only -- a refill after other people's merges costs a few
seconds instead of the whole space again.

    python contrib/_dump_named.py BLACKOP6 BLACKOP7 YAMYAMOK MODWAR22 MODWAR7
    python contrib/twc_extend_delta.py
    confirm_plan contrib/twc_delta/<dir><k>_{app,pre}.plan.txt --game BLACKOP7
"""
from pathlib import Path
import collections

ROOT = Path(__file__).resolve().parent.parent
CONTRIB = ROOT / "contrib"
OUT = CONTRIB / "twc_delta"
NL = "\n"
DIRS = ["twc", "tw", "twcj", "twck", "twj", "twk", "w", "wc"]

known = collections.defaultdict(set)
for f in (ROOT / "state" / "an").glob("*_material.named"):
    for line in f.open(encoding="utf-8", errors="replace"):
        n = line.strip().lower()
        d, _, rest = n.partition("/*")
        if d in DIRS and rest:
            known[d].add(rest)

OUT.mkdir(exist_ok=True)
for f in OUT.glob("*"):
    f.unlink()
total = 0
for d in DIRS:
    tag = "" if d == "twc" else "_" + d
    top = 10001 if tag else 7001
    tokens = [f"{k}n" for k in range(top)] + [f"{k}dn" for k in range(top)]
    (OUT / f"{d}_tok_end.txt").write_text("".join("_" + t + NL for t in tokens), encoding="utf-8")
    (OUT / f"{d}_tok_begin.txt").write_text("".join(d + "/*" + t + NL for t in tokens), encoding="utf-8")
    for k in (3, 4, 5):
        old_file = CONTRIB / f"twc_ext{tag}{k}_base_begin.txt"
        old = set()
        if old_file.is_file():
            old = {l[len(d) + 2:] for l in old_file.read_text(encoding="utf-8").split() if l}
        base = sorted(b for b in known[d] if b.count("_") == k - 2 and b not in old)
        if not base:
            continue
        (OUT / f"{d}{k}_base_begin.txt").write_text("".join(d + "/*" + b + NL for b in base), encoding="utf-8")
        (OUT / f"{d}{k}_base_stem.txt").write_text("".join("_" + b + NL for b in base), encoding="utf-8")
        desc = f"describe: {k - 1}-token {d} names new since the last twc_extend run, one token 0..{top - 1} (n, dn) added; contrib/twc_extend_delta.py"
        (OUT / f"{d}{k}_app.plan.txt").write_text(NL.join([
            f"label: {d} {k}-token names: new {k - 1}-token name + appended token", desc,
            f"stem: @contrib/twc_delta/{d}{k}_base_begin.txt", f"end: @contrib/twc_delta/{d}_tok_end.txt", ""]), encoding="utf-8")
        (OUT / f"{d}{k}_pre.plan.txt").write_text(NL.join([
            f"label: {d} {k}-token names: prepended token + new {k - 1}-token name", desc,
            f"begin: @contrib/twc_delta/{d}_tok_begin.txt", f"stem: @contrib/twc_delta/{d}{k}_base_stem.txt", "bare: no", ""]), encoding="utf-8")
        total += 2 * len(base) * len(tokens)
        print(f"{d} k={k}: {len(base)} new bases (of {len(known[d])} known, {len(old)} done before)")
print(f"total ~{total / 1e9:.1f}B candidates per game")
