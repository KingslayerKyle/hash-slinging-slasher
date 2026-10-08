"""MWII sound files as `head + shared tail + encoding`, asked completely.

    python contrib/mwii_shared_tail_plan.py --write-plan plans/mwii_shared.txt
    bin\\windows\\confirm_plan.exe plans/mwii_shared.txt --game MODWAR22 --size

## Why not the whole-product plan next to it

`plans/mwii_sound.txt` (contrib/modern_sound_plan.py, sab_plan's shape) crosses every measured
directory against every measured basename. On MWII that product is **3.56 trillion candidates** and
it found nothing in its first 345 billion. The reason is one measured number: MWII's own corpus
holds **44,077 distinct basenames across 45,049 names**, so a basename is nearly unique to its name
and the product asks 482 million directory/basename pairs to reach the ~253,000 real ones. It buys
almost no reach per candidate.

It also found nothing for a second reason, which this plan fixes. Both plans measured the trailing
tokens by accident -- `_fire_plr_shot_03`, `_reload_empty_fast_magrelease` -- and used them as part
of a whole basename instead of as an axis in their own right.

## What is measured here

Every underscore boundary in a verified MWII sound basename is a possible head/tail cut. A *head* is
`directory + tokens before the cut`; a *tail* is the tokens after it. A tail is only carried if the
corpus attests it in **at least two directories**, so it is repetition that actually exists rather
than a word that happened to occur:

| tails attested in | tails carried | head x tail |
|---:|---:|---:|
| 1 directory | 20,531 | -- (that is just the whole product) |
| 2 directories | 4,896 | 84,715,488 |
| 5 directories | 1,257 | 21,749,871 |
| 10 directories | 511 | 8,841,833 |

`npc` is attested in 179 directories, `ads` in 97, `end` in 95, `raise` in 87, and compounds hold up
too: `fire_npc_med` in 73, `reload_end` in 72, `empty_end` in 68.

Because heads are carried at *every* cut, the correct (head, tail) pairing is always present in the
product; the mismatched pairings are harmless, they simply do not hash to anything the game holds.
"""
import argparse
import collections
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import settings
import snapshot

ROOT = snapshot.ROOT

# `ll` and `sl` carry no `n`, so the channelspec is `[a-z]{1,4}` rather than `n`-shaped: a stricter
# pattern silently dropped 862 real MWII names in the first version of this measurement.
TAIL = re.compile(r"\.(?P<chan>[a-z]{1,4})\.(?P<qual>\d+)\.48000\.(?P<ext>[a-z_]+)$")
VARIANT = re.compile(r"_\d+$")


def mwii_sound_names(game):
    """Verified sound-file names the chosen capture actually holds."""
    path = [p for p in snapshot.snapshots() if snapshot.read(p).game == game][0]
    held = {k: set(v) for k, v in snapshot.read(path).by_pool().items()}
    ids = held.get("sound_asset", set())
    table = "fnv1a_xsounds_v2"
    with open(os.path.join(settings.tables_csv(), table + ".csv"),
              encoding="utf-8", errors="replace") as handle:
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
            yield name


def vocabulary(game, min_directories):
    heads = collections.Counter()
    support = collections.defaultdict(set)
    tails = collections.Counter()
    variants = collections.Counter()
    names = 0

    for name in mwii_sound_names(game):
        match = TAIL.search(name)
        if not match:
            continue
        directory, _, basename = name[: match.start()].rpartition(".")
        if not directory:
            continue
        directory += "."
        encoding = name[match.start():]
        core = VARIANT.sub("", basename)
        if "_" not in core:
            continue
        names += 1
        tails[encoding] += 1
        variant = basename[len(core):]
        if variant:
            variants[len(variant) - 1] += 1

        tokens = core.split("_")
        for cut in range(1, len(tokens)):
            head = directory + "_".join(tokens[:cut]) + "_"
            tail = "_".join(tokens[cut:])
            heads[head] += 1
            support[tail].add(directory)

    carried = {t for t, dirs in support.items() if len(dirs) >= min_directories}
    return heads, carried, tails, variants, names


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--game", default="MODWAR22")
    parser.add_argument("--min-directories", type=int, default=2,
                        help="how many directories a tail must be attested in to be carried")
    parser.add_argument("--variant-coverage", type=float, default=0.999)
    parser.add_argument("--most-variant", type=int, default=0)
    parser.add_argument("--two-column", action="store_true",
                        help="fold the endings into the stem column so the engine sweeps forward "
                             "instead of peeling; see the note below")
    parser.add_argument("--write-plan", metavar="PATH", required=True)
    options = parser.parse_args(argv)

    game = options.game.upper()
    heads, carried, tails, variants, names = vocabulary(game, options.min_directories)

    seen = sum(variants.values()) or 1
    running = 0
    chosen = max(variants) if variants else 2
    for width in sorted(variants):
        running += variants[width]
        if running / seen >= options.variant_coverage:
            chosen = width
            break
    most = options.most_variant or (10 ** chosen)

    endings = list(tails)
    for index in range(most):
        for tail in tails:
            endings.append("_%02d%s" % (index, tail))

    print("names decomposed %s -> %s heads, %s shared tails (>=%d directories), %s encodings, "
          "most=%d" % (format(names, ","), format(len(heads), ","),
                       format(len(carried), ","), options.min_directories,
                       format(len(tails), ","), most),
          file=sys.stderr)

    # With an `end:` column the engine picks the *peel* direction, and on this plan that is the
    # wrong pick by a wide margin: it announced "about 23.5B of work against 262.0B peeling" and
    # then spent 32 minutes of eight cores building the peeled set without sweeping a single
    # forward hash. Peeling is meant to be nearly free, and it is only nearly free when the ending
    # list is short relative to the candidate count -- here there are 2,222 endings and 17,303
    # beginnings, so peeling costs more than the 188B forward sweep it replaces.
    #
    # An `end:`-free plan cannot peel at all: the engine sweeps `beginnings x stems` forward, which
    # is 188B hashes at the ~105M/s this machine sustains, about half an hour. Same candidates,
    # same exclusions, same fingerprint inputs -- just asked in the cheaper order.
    stems = sorted(carried)
    ends = endings
    if options.two_column:
        stems = sorted(tail + end for tail in carried for end in endings)
        ends = []

    plan_path = os.path.join(ROOT, options.write_plan)
    base = os.path.splitext(plan_path)[0]
    os.makedirs(os.path.dirname(plan_path), exist_ok=True)
    written = {}
    for what, entries in (("heads", sorted(heads)), ("tails", stems), ("ends", ends)):
        written[what] = base + ".%s.txt" % what
        with open(written[what], "w", encoding="utf-8", newline="\n") as handle:
            handle.write("\n".join(entries) + "\n")

    relative = lambda path: os.path.relpath(path, ROOT).replace("\\", "/")

    with open(plan_path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(
            "# Written by contrib/mwii_shared_tail_plan.py. Regenerate rather than editing.\n"
            "#\n"
            "# Modern sound files are dot-separated paths: iw9.dst.iw9_dst_street_barricade_03"
            ".ln.75.48000.all\n"
            "# A head is the directory plus the basename tokens before an underscore cut; a tail is\n"
            "# the tokens after it, carried only where the corpus attests it in at least %d\n"
            "# directories. Heads exist at EVERY cut, so the correct pairing is always in the product.\n"
            "#\n"
            "# %s heads x %s stems%s. fold stays yes: these names carry no\n"
            "# backslashes at all, so folding is a no-op and only Black Ops 4's SAB names need it off.\n"
            "#\n"
            "# Two-column (no `end:` line) so the engine sweeps forward. With an `end:` column it\n"
            "# peels instead, which on this plan costs more than the sweep it replaces.\n\n"
            % (options.min_directories, format(len(heads), ","), format(len(stems), ","),
               (" x %s endings" % format(len(ends), ",")) if ends else "")
        )
        handle.write("label: MWII sound heads x shared tails\n")
        handle.write(
            "describe: every measured MWII sound head crossed with every trailing token run "
            "attested in two or more directories, wearing every measured encoding tail\n\n"
        )
        handle.write("game: %s\n\n" % game)
        handle.write("begin: @%s\n\n" % relative(written["heads"]))
        handle.write("stem: @%s\n\n" % relative(written["tails"]))
        if ends:
            handle.write("end: @%s\n\n" % relative(written["ends"]))
        handle.write("bare: no\n")

    print("\nwrote %s\n\n    bin\\windows\\confirm_plan.exe %s --game %s --size"
          % (relative(plan_path), options.write_plan, game), file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
