"""Sound-file vocabulary the committed lists cannot express.

    python contrib/sound_shape.py            write the three lists
    python contrib/sound_shape.py --report   print the counts and stop

Why these three files exist: `scripts/reach.py --missing` measures `fnv1a_xsounds.csv` at 100%
*reached* but 3.3% *named*, and the reason is one number. The published table uses nine distinct
file endings -- `.sn100.pc.snd` heads 115,027 of 174,836 names on its own -- and `grep -Fx` finds
zero of those nine in `data/sound.suffixes.txt`. The committed 3,014 sound suffixes carry fused
forms like `_00.rn75.pc.en.snd`; the bare `.sn100.pc.snd` shape, which is two thirds of the corpus,
is not among them. A sound pass therefore cannot name these ids whatever its stems are, and no
amount of re-measuring `derive_lists.py` changes that, because the list is capped rather than wrong.

The beginning side has the same problem in a different way. These names live in deep directories
(`en/vox/scripted/zmb/white`) and `data/sound.prefixes.txt` keeps 700 short first-token prefixes
(`vox/`, `zmb/`), which is a different cut of the same string. Both are carried here so a plan can
choose.

Stems are basenames with the ending removed, which is the whole published vocabulary. Crossed with
the directories it recombines families that were never published together -- a white-vox line under
`bod`, a numbered index past the ones the tables hold.

Both slash spellings are kept as the table has them, which matters more than it looks: 60,501 of
the 174,838 published names are spelled with backslashes, and Black Ops 4 SAB names hash with
exactly those literal backslashes (AGENTS.md section 5). So a directory cut has to split on both
separators and still emit the original spelling, or every BO4 sound name collapses into one long
"stem" and the pass searches a shape that cannot exist. Run the backslash half with --no-fold and
the forward-slash half with the fold on.
"""
import os
import re
import sys
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TABLE = os.path.join(ROOT, "cod-name-db", "csv", "fnv1a_xsounds.csv")
OUT = os.path.join(ROOT, "contrib")

# .sn100.pc.snd / .ln75.pc.all.snd / .snd and their rarer siblings, measured off the table.
ENDING = re.compile(r"(\.(?:sn|ln|rn|sl|an)\d+\.pc\.(?:all\.)?snd(?:_transient)?|\.snd)$")


def names():
    out = []
    with open(TABLE, encoding="utf-8", errors="replace") as handle:
        for line in handle:
            parts = line.rstrip("\n").rstrip("\r").split(",", 1)
            if len(parts) == 2 and parts[1]:
                out.append(parts[1])
    return out


def main():
    report_only = "--report" in sys.argv
    rows = names()
    dirs, stems, ends = set(), set(), set()
    dirs_bs, stems_bs = set(), set()

    for name in rows:
        match = ENDING.search(name)
        if not match:
            continue
        ends.add(match.group(1))
        body = name[: match.start()]
        # Split on whichever separator this name actually uses, so a BO4 path stays one path
        # instead of collapsing into a single 60-character "stem".
        sep = "\\" if chr(92) in body and "/" not in body else "/"
        head, _, tail = body.rpartition(sep)
        if not head and chr(92) in body:
            head, _, tail = body.rpartition(chr(92))
        if head:
            (dirs_bs if sep == "\\" else dirs).add(head + sep)
        else:
            continue
        if tail:
            (stems_bs if sep == "\\" else stems).add(tail)

    # A stem that is only ever seen once in a directory adds nothing but cost; keep the ones the
    # naming convention repeats, which is where a recombination has a chance of being real.
    counts = {}
    for name in rows:
        body = ENDING.sub("", name)
        sep = "\\" if chr(92) in body and "/" not in body else "/"
        tail = body.rpartition(sep)[2]
        if not tail and chr(92) in body:
            tail = body.rpartition(chr(92))[2]
        if tail:
            counts[tail] = counts.get(tail, 0) + 1
    stems = {s for s in stems if counts.get(s, 0) >= 2}
    stems_bs = {s for s in stems_bs if counts.get(s, 0) >= 2}

    print(f"published sound names : {len(rows):,}")
    print(f"  endings             : {len(ends):,}")
    print(f"  directories         : {len(dirs):,} forward-slash, {len(dirs_bs):,} backslash")
    print(f"  repeat stems        : {len(stems):,} forward-slash, {len(stems_bs):,} backslash")

    carried = subprocess.run(
        ["grep", "-Fx", "-f", "-", os.path.join(ROOT, "data", "sound.suffixes.txt")],
        input="\n".join(sorted(ends)), text=True, capture_output=True,
    ).stdout.strip()
    print(f"  of those endings, carried by data/sound.suffixes.txt: {len([c for c in carried.splitlines() if c])}")

    if report_only:
        return

    for filename, values in (
        ("snd_dirs.txt", dirs),
        ("snd_stems.txt", stems),
        ("snd_dirs_bs.txt", dirs_bs),
        ("snd_stems_bs.txt", stems_bs),
        ("snd_ends.txt", ends),
    ):
        path = os.path.join(OUT, filename)
        with open(path, "w", encoding="utf-8", newline="\n") as handle:
            for value in sorted(values):
                handle.write(value + "\n")
        print(f"wrote {os.path.relpath(path, ROOT)}  ({len(values):,} lines)")


if __name__ == "__main__":
    main()
