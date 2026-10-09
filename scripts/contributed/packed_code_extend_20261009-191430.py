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
    print(f"{len(codes):,} codes, {len(bodies):,} bodies, {len(nums):,} numbers")


if __name__ == "__main__":
    main()
