"""Plans for the packed `twc/*` and `tw/*` material codes: every observed number in every slot.

Modern titles publish ~413,000 materials named `twc/*274n_215n`, `twc/*134n_31n_19n`, `tw/*310n_5n` --
two to four `<number>n` slots after a packing prefix -- built from only 5,362 distinct numbers. A
code's slots are independent, so the missing codes are the grid of observed numbers. This writes
`confirm_plan` plans for the two- and three-slot grids (the engine multiplies them; never print them):

    python contrib/packed_material_codes.py
    confirm_plan plans/twc2.txt --game YAMYAMOK      57.5M candidates
    confirm_plan plans/twc3.txt --game YAMYAMOK      ~3 x 10^11 candidates, expected chance matches printed

First run (2 slots): 483 new on MWIII, 790 on MWII, 0 on BO7/BO6/MW7. The idea came from a parallel
BLACKOP7 worker (`packed_material_codes`), which measured the 80k-name precedent.

Spent by: the number set as it stands; re-run when new codes add numbers.
"""
from pathlib import Path
import re

ROOT = next((p for p in Path(__file__).resolve().parents
             if (p / 'scripts/snapshot.py').is_file()), None)
if ROOT is None:
    raise SystemExit('Run this generator from a solver checkout')
PATTERN = re.compile(r"^(twc|tw)/\*((?:\d+n_?)+)$")


def main():
    nums = set()
    sources = list((ROOT / "cod-name-db" / "csv").glob("fnv1a_xmaterials*.csv"))
    for folder in ("submissions", "findings"):
        base = ROOT / folder
        if base.exists():
            sources.extend(base.rglob("material*.txt"))
    for path in sources:
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            m = PATTERN.match(line.partition(",")[2].strip().lower())
            if m:
                nums.update(re.findall(r"\d+", m.group(2)))
    nums = sorted(nums, key=int)
    plans = ROOT / "plans"
    plans.mkdir(exist_ok=True)
    (plans / "twc_nums_n_.txt").write_text("".join(n + "n_\n" for n in nums))
    (plans / "twc_nums_n.txt").write_text("".join(n + "n\n" for n in nums))
    (plans / "twc_begins3.txt").write_text("".join(f"{p}/*{n}n_\n" for p in ("twc", "tw") for n in nums))
    common = "stem: @plans/twc_nums_n_.txt\nend: @plans/twc_nums_n.txt\nbare: no\nfold: yes\n"
    (plans / "twc2.txt").write_text(
        "label: packed twc/tw material codes, two slots, every observed number\n"
        "describe: twc/*<a>n_<b>n and tw/*<a>n_<b>n over every number published codes use\n"
        "begin: twc/*\nbegin: tw/*\n" + common)
    (plans / "twc3.txt").write_text(
        "label: packed twc/tw material codes, three slots, every observed number\n"
        "describe: twc/*<a>n_<b>n_<c>n and tw/*... over every number published codes use\n"
        "begin: @plans/twc_begins3.txt\n" + common)
    print(f"{len(nums):,} numbers")


if __name__ == "__main__":
    main()
