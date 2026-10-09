"""Plans that grow every known packed `twc/*` and `tw/*` material code by one slot, at either end.

`packed_material_codes.py` asks the full two- and three-slot grids; a four-slot grid is 6,000^4 and
out of reach. But published and confirmed codes run to eight slots (`twc/*5n_17n_203n_9n`), and a
longer code is very often a shorter one with one more slot: KingslayerKyle's MWIII batch of
2026-10-09 holds 6,165 four-slot and 300+ five-to-eight-slot codes. So every known code of any
length, in any game, is offered with every observed number appended, and with every observed number
prepended. Each is a two-list product the engine multiplies:

    append:   begin = <known code>_      stem = <number>      end = n
    prepend:  begin = <twc|tw>/*<number>n_      stem = <known body without its final n>   end = n

    python contrib/packed_code_extend.py
    confirm_plan plans/pce_append.txt --game YAMYAMOK
    confirm_plan plans/pce_prepend.txt --game YAMYAMOK

Spent by: the code set as it stands; re-run after new codes are confirmed (it snowballs one slot a
round).
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
PATTERN = re.compile(r"^(twc|tw)/\*((?:\d+n_)*\d+n)$")


def main():
    codes = set()
    sources = list((ROOT / "cod-name-db" / "csv").glob("fnv1a_xmaterials*.csv"))
    for folder in ("submissions", "findings"):
        base = ROOT / folder
        if base.exists():
            sources.extend(base.rglob("material*.txt"))
    for path in sources:
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            k, sep, v = line.partition(",")
            m = PATTERN.match((v if sep else k).strip().lower())
            if m:
                codes.add((m.group(1), m.group(2)))
    nums = sorted({n for _, body in codes for n in re.findall(r"\d+", body)}, key=int)
    bodies = sorted({body for _, body in codes})
    plans = ROOT / "plans"
    plans.mkdir(exist_ok=True)
    (plans / "pce_codes_.txt").write_text("".join(f"{p}/*{b}_\n" for p in ("twc", "tw") for b in bodies))
    (plans / "pce_bodies.txt").write_text("".join(b[:-1] + "\n" for b in bodies))
    (plans / "pce_nums.txt").write_text("".join(n + "\n" for n in nums))
    (plans / "pce_begins.txt").write_text("".join(f"{p}/*{n}n_\n" for p in ("twc", "tw") for n in nums))
    tail = "end: n\nbare: no\nfold: yes\n"
    (plans / "pce_append.txt").write_text(
        "label: packed twc/tw codes, every known code with one more slot appended\n"
        "describe: <twc|tw>/*<known code>_<number>n over every known code and observed number\n"
        "begin: @plans/pce_codes_.txt\nstem: @plans/pce_nums.txt\n" + tail)
    (plans / "pce_prepend.txt").write_text(
        "label: packed twc/tw codes, every known code with one more slot prepended\n"
        "describe: <twc|tw>/*<number>n_<known code> over every known code and observed number\n"
        "begin: @plans/pce_begins.txt\nstem: @plans/pce_bodies.txt\n" + tail)
    # Siblings of every code of four or more slots: its last slot, or its first, swapped for every
    # number. The heads and tails need not be codes themselves, which is what append cannot reach.
    long = [b for b in bodies if b.count("_") >= 3]
    heads = sorted({b.rsplit("_", 1)[0] for b in long})
    tails = sorted({b.split("_", 1)[1][:-1] for b in long})
    (plans / "pce_heads_.txt").write_text("".join(f"{p}/*{h}_\n" for p in ("twc", "tw") for h in heads))
    (plans / "pce_tails.txt").write_text("".join(t + "\n" for t in tails))
    (plans / "pce_sib_last.txt").write_text(
        "label: packed twc/tw codes, last slot of every 4+ slot code swapped\n"
        "describe: <head of a known 4+ slot code>_<number>n\n"
        "begin: @plans/pce_heads_.txt\nstem: @plans/pce_nums.txt\n" + tail)
    (plans / "pce_sib_first.txt").write_text(
        "label: packed twc/tw codes, first slot of every 4+ slot code swapped\n"
        "describe: <twc|tw>/*<number>n_<tail of a known 4+ slot code>\n"
        "begin: @plans/pce_begins.txt\nstem: @plans/pce_tails.txt\n" + tail)
    # The two middle slots of a four-slot code: a known outer part on one side, every number in the
    # slot, and a known two-slot part of some four-slot code on the other. The first-slot swap above
    # out-found the last-slot one 586 to 20 on MWII, so the inner slots vary too.
    four = [b for b in bodies if b.count("_") == 3]
    tails2 = sorted({"n_" + "_".join(b.split("_")[2:]) for b in four})
    heads2 = sorted({"_".join(b.split("_")[:2]) for b in four})
    lasts = sorted({"n_" + b.split("_")[3] for b in four})
    (plans / "pce_tails2.txt").write_text("".join(t + "\n" for t in tails2))
    (plans / "pce_heads2_.txt").write_text("".join(f"{p}/*{h}_\n" for p in ("twc", "tw") for h in heads2))
    (plans / "pce_lasts.txt").write_text("".join(t + "\n" for t in lasts))
    mid = "bare: no\nfold: yes\n"
    (plans / "pce_mid2.txt").write_text(
        "label: packed twc/tw codes, second of four slots over every number\n"
        "describe: <twc|tw>/*<a>n_<number>n_<last two slots of a known four-slot code>\n"
        "begin: @plans/pce_begins.txt\nstem: @plans/pce_nums.txt\nend: @plans/pce_tails2.txt\n" + mid)
    (plans / "pce_mid3.txt").write_text(
        "label: packed twc/tw codes, third of four slots over every number\n"
        "describe: <first two slots of a known four-slot code>_<number>n_<d>n\n"
        "begin: @plans/pce_heads2_.txt\nstem: @plans/pce_nums.txt\nend: @plans/pce_lasts.txt\n" + mid)
    print(f"{len(codes):,} codes, {len(bodies):,} bodies, {len(nums):,} numbers, "
          f"{len(heads):,} heads, {len(tails):,} tails")


if __name__ == "__main__":
    main()
