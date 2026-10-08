"""The take index on its own, aimed at MWII's numbered sound families.

`contrib/mwii_shared_tail_plan.py` reaches names of the form `head + tail + take + encoding`. Two
measurements say where the remaining ground is:

* Dropping the take axis and widening the tail vocabulary to every modern game cost almost
  everything: 12,529,777,117 candidates returned **16** names, one per 783 million, against the
  take-bearing plan's one per 516 million over 188 billion. Cross-game tails are exhausted; the
  take index is not.
* The take index is a real, bounded, measured convention rather than a guess. In MWII's executions
  alone it runs `_01`..`_17` across 163 cores, and `mp.executions.` is the largest group in the pool.
  `exec_baton_impact_head_02`, `exec_049_stand_victim_03_kill_lfe` -- core, take, encoding, always in
  that order.

So this writes the narrow plan the wide one implies: every measured MWII head, crossed with every
take index crossed with every measured encoding, and **no token tail at all**. The take completes a
name outright, which is why the stem list is small enough to be free -- 30 takes x 53 encodings is
1,590 stems, against the wide plan's 724,139.
"""
import argparse
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import settings
import snapshot

ROOT = snapshot.ROOT
TAIL = re.compile(r"\.(?P<chan>[a-z]{1,4})\.(?P<qual>\d+)\.48000\.(?P<ext>[a-z_]+)$")
TAKE = re.compile(r"_\d{1,3}$")


def measured(game):
    """Every encoding and every take width the game's own names attest."""
    path = [p for p in snapshot.snapshots() if snapshot.read(p).game == game][0]
    held = {k: set(v) for k, v in snapshot.read(path).by_pool().items()}
    ids = held.get("sound_asset", set())
    table = "fnv1a_xsounds_v2"
    encodings = set()
    widths = set()
    names = 0
    with (Path(settings.tables_csv()) / (table + ".csv")).open(encoding="utf-8",
                                                               errors="replace") as handle:
        for line in handle:
            key, sep, display = line.strip().partition(",")
            if not sep:
                continue
            try:
                key = int(key, 16)
            except ValueError:
                continue
            if key & snapshot.ID_MASK not in ids:
                continue
            restored = snapshot.verified_database_row(table, key, display)
            if restored is None:
                continue
            _, name = restored
            if snapshot.fnv1a(name, game, "sound_asset") & snapshot.ID_MASK != key:
                continue
            match = TAIL.search(name)
            if not match:
                continue
            names += 1
            encodings.add(name[match.start():])
            take = TAKE.search(name[: match.start()])
            if take:
                widths.add(len(take.group(0)) - 1)
    return encodings, widths, names


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--game", default="MODWAR22", type=str.upper,
                        choices=sorted(snapshot.MODERN))
    parser.add_argument("--heads", default=None,
                        help="head list from this game's shared-tail plan")
    parser.add_argument("--write-plan", required=True)
    parser.add_argument("--most-take", type=int, default=30)
    options = parser.parse_args(argv)
    game = options.game
    plan_path = os.path.join(ROOT, options.write_plan)
    most = options.most_take
    if most < 0:
        parser.error("--most-take must be nonnegative")
    if options.heads is None and game != "MODWAR22":
        parser.error("--heads must name the selected game's head list")
    source_heads = Path(ROOT) / (options.heads or "plans/mwii_shared_xgame.heads.txt")
    if source_heads.resolve() == Path(os.path.splitext(plan_path)[0] + ".heads.txt").resolve():
        parser.error("output head list must differ from the source head list")
    if not source_heads.is_file():
        parser.error("head list is missing; generate it first or pass --heads")
    # Shared-tail heads already end in '_'; takes also start with '_'. Remove one
    # join separator in our own list, preserving the source list for its original plan.
    heads = sorted({head[:-1] if head.endswith("_") else head
                    for line in source_heads.read_text(encoding="utf-8").splitlines()
                    if (head := line.strip())})
    if not heads:
        parser.error("head list is empty")

    encodings, widths, names = measured(game)
    widest = max(widths) if widths else 2
    print("%s: %s names, %s encodings, take widths %s -> enumerating 00..%02d"
          % (game, format(names, ","), len(encodings), sorted(widths), most - 1),
          file=sys.stderr)

    stems = []
    for index in range(most):
        for encoding in sorted(encodings):
            stems.append("_%02d%s" % (index, encoding))
    # The corpus is not uniformly zero-padded: 1,143 of its take indices are a bare `1`.
    for index in range(10):
        for encoding in sorted(encodings):
            stems.append("_%d%s" % (index, encoding))

    base = os.path.splitext(plan_path)[0]
    os.makedirs(os.path.dirname(plan_path), exist_ok=True)
    with open(base + ".heads.txt", "w", encoding="utf-8", newline="\n") as handle:
        handle.write("\n".join(heads) + "\n")
    with open(base + ".takes.txt", "w", encoding="utf-8", newline="\n") as handle:
        handle.write("\n".join(stems) + "\n")

    relative = lambda p: os.path.relpath(p, ROOT).replace("\\", "/")
    with open(plan_path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(
            "# Written by contrib/mwii_take_plan.py. Regenerate rather than editing.\n"
            "#\n"
            "# The take index alone, aimed at MWII's numbered sound families. Measured: dropping the\n"
            "# take axis and widening tails across every modern game cost almost everything, 12.5\n"
            "# billion candidates for 16 names, while the take-bearing plan returned 364 from 188\n"
            "# billion. Cross-game tails are spent; the take index is not.\n"
            "#\n"
            "# %s encodings measured on this game's own names, takes 00..%02d padded and unpadded,\n"
            "# crossed with every measured MWII head and no token tail at all.\n\n"
            % (len(encodings), most - 1)
        )
        handle.write("label: MWII sound heads x take index x encoding\n")
        handle.write(
            "describe: every measured MWII sound head completed by every take index and every "
            "measured encoding tail, with no token tail\n\n"
        )
        handle.write("game: %s\n\n" % game)
        handle.write("begin: @%s\n\n" % relative(base + ".heads.txt"))
        handle.write("stem: @%s\n\n" % relative(base + ".takes.txt"))
        handle.write("bare: no\n")

    print("wrote %s and %s (%s stems)"
          % (relative(plan_path), relative(base + ".takes.txt"), format(len(stems), ",")),
          file=sys.stderr)


if __name__ == "__main__":
    main()
