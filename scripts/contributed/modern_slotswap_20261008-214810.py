"""Slotswap (method 10: swap one token of a whole known name for the tokens measured to fill that
same slot elsewhere) applied to the modern games for the first time.

`fresh_slotswap.py` is wired to the BO4/CW tables and to BO4/CW findings. The modern titles share
one id space and their own vocabulary (`_v2` tables, MWII/MWIII/BO6/BO7/MW7 findings, other
contributors' open pull requests), and nobody has run the substitution there at all, so here the
seeds are every modern name, not only recent ones. The slot alphabet and the substitution are
slotswap_cores.py's and fresh_slotswap.py's own, unchanged.

    python contrib/modern_slotswap.py | confirm_list - --game BLACKOP6 --script contrib/modern_slotswap.py
"""
from pathlib import Path
import argparse
import sys

ROOT = Path(__file__).resolve().parent
while not (ROOT / "scripts" / "snapshot.py").is_file() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "contrib"))
import slotswap_cores as sc  # noqa: E402
from fresh_slotswap import substitutions  # noqa: E402

MODERN_GAMES = ("blackop6", "blackop7", "modwar22", "modwar7", "yamyamok")


def modern_names(kinds):
    for f in sorted((ROOT / "cod-name-db" / "csv").glob("*_v2.csv")):
        if kinds and not any(k in f.stem for k in kinds):
            continue
        for line in f.open(encoding="utf-8", errors="replace"):
            yield line.rstrip("\r\n").partition(",")[2]
    roots = [ROOT / "findings" / g for g in MODERN_GAMES] + [ROOT / "all_names" / g for g in MODERN_GAMES]
    roots += [ROOT / "contrib" / "open_pr_names"]
    roots += [p for p in (ROOT / "submissions").iterdir() if any(g.upper() in p.name for g in MODERN_GAMES)]
    for root in roots:
        if not root.exists():
            continue
        for f in sorted(root.rglob("*.txt")):
            for line in f.open(encoding="utf-8", errors="replace"):
                key, sep, name = line.rstrip("\r\n").partition(",")
                if sep:
                    yield name


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cap", type=int, default=12)
    ap.add_argument("--kinds", default="", help="comma list of table-name fragments, e.g. ximages,aliases")
    a = ap.parse_args()
    kinds = [k for k in a.kinds.split(",") if k]
    corpus = sorted({n.strip().lower().replace("\\", "/") for n in modern_names(kinds) if n.strip()})
    corpus = [n for n in corpus if "~" not in n and "&" not in n and not n.startswith("twc/")]
    offers = sc.measure_offers(corpus, cap=a.cap)
    out = sys.stdout
    total = 0
    for name in corpus:
        subs = substitutions(name, offers)
        total += len(subs)
        out.write("".join(s + "\n" for s in subs))
    print(f"{len(corpus):,} seeds, {len(offers):,} slot contexts, {total:,} candidates", file=sys.stderr)


if __name__ == "__main__":
    main()
