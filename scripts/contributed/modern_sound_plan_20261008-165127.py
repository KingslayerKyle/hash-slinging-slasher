"""Modern Warfare sound files as the dot-separated paths they are, asked completely.

    python contrib/modern_sound_plan.py --write-plan plans/mwii_sound.txt
    bin\\windows\\confirm_plan.exe plans/mwii_sound.txt --size

## Why MWII needs its own plan rather than the general pass

A modern sound-file id is the FNV-1a 64 hash, IW offset `0x47F5817A5EF961BA`, of a name whose path
separator is a **period**: `iw9.dst.iw9_dst_street_barricade_03.ln.75.48000.all`. Measured on the
45,911 of those names MWII's own capture and the published tables agree on, **45,882 verify with
periods and 29 with slashes** -- so the separator is a fact about the game, not a display artefact.

`derive_modern_lists.py` finds a name's directory with `rpartition("/")`. On a dotted name that
finds nothing, so the directory collapses into the basename and the measured prefix list can only
ever express a path component that happens to contain no underscore. That is the whole reason
`sound_asset` sits at 18.4% named while `xanim` sits at 80.7% in the same capture: nothing in the
carried vocabulary can spell a five-segment path.

This is `scripts/sab_plan.py`'s shape -- directory x basename x tail on the compiled engine rather
than through a pipe -- pointed at a different separator and a different game. It is deliberately
*not* a new idea; it is a proven one extended to ground nothing has reached.

## The one measurement that makes the cross-game harvest legal

MWIII, BO6, BO7 and MW7 hash their sound files with the **same IW offset** as MWII, so every name in
`fnv1a_xsounds_v2` is a legal MWII candidate: one hash policy, five vocabularies. Their captures
hold 1,148,664 sound-file ids between them against MWII's 249,863, and they share IW-era naming
(`iw9`, `iw8`, `core`, `mp`, `jup`, `sat`, `t10`, `s6` components). A candidate that matches is
proven against MWII's own capture, so harvesting wider costs reach, never correctness.
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

# `<channelspec>.<quality>.48000.<container>`. The channelspec is the only part with letters and
# the rest is a fixed shape, so this is measured rather than listed. `ll` and `sl` carry no `n`,
# which is why the channelspec is `[a-z]{1,4}` and not `n`-shaped: they are a real and sizeable
# group (vehicles and ambiences), and a regex that missed them silently dropped 862 real names.
TAIL = re.compile(r"\.(?P<chan>[a-z]{1,4})\.(?P<qual>\d+)\.48000\.(?P<ext>[a-z_]+)$")

# A trailing index is a variant counter the tail list has to put back, exactly as sab_plan does it.
VARIANT = re.compile(r"_(\d+)$")


def modern_sound_names(only_games=None):
    """Verified names the modern sound table holds, spelled the way it was hashed.

    `only_games` restricts the harvest to names a given game's own capture holds, which is how a
    plan asks for one game's *directories* against another game's *basenames*: the directories are
    ground the target game provably uses, and the basenames are content MWIII, BO6, BO7 or MW7
    names that MWII may well hold under a directory only MWII has.
    """
    table = "fnv1a_xsounds_v2"
    held = None
    if only_games:
        wanted = set()
        for tag in only_games:
            path = [p for p in snapshot.snapshots() if snapshot.read(p).game == tag]
            if not path:
                continue
            wanted |= {k: set(v) for k, v in snapshot.read(path[0]).by_pool().items()}.get(
                "sound_asset", set())
        held = wanted
    path = os.path.join(settings.tables_csv(), table + ".csv")
    with open(path, encoding="utf-8", errors="replace") as handle:
        for line in handle:
            key, sep, display = line.strip().partition(",")
            if not sep:
                continue
            try:
                key = int(key, 16)
            except ValueError:
                continue
            restored = snapshot.verified_database_row(table, key, display)
            if restored is None:
                continue
            full, name = restored
            # Only accept a spelling that reproduces its own key under this table's policy.
            if snapshot.database_source_hash(table, name) & snapshot.ID_MASK != key:
                continue
            if held is not None and key & snapshot.ID_MASK not in held:
                continue
            yield name


def vocabulary(dirs_game=None, stem_games=None):
    """Directories, basenames and encoding tails, measured over the modern sound table."""
    directories = collections.Counter()
    basenames = collections.Counter()
    tails = collections.Counter()
    variants = collections.Counter()
    no_tail = 0
    seen_dirs = set()

    for name in modern_sound_names([dirs_game] if dirs_game else None):
        match = TAIL.search(name)
        if not match:
            continue
        head = name[: match.start()]
        directory, _, _ = head.rpartition(".")
        if directory:
            seen_dirs.add(directory + ".")

    for name in modern_sound_names(stem_games):
        match = TAIL.search(name)
        if not match:
            no_tail += 1
            continue
        head = name[: match.start()]
        directory, _, basename = head.rpartition(".")
        tail = name[match.start():]
        variant = VARIANT.search(basename)
        if variant:
            variants[len(variant.group(1))] += 1
            basename = basename[: variant.start()]
        if len(basename) >= 3:
            if not dirs_game:
                directories[directory + "." if directory else ""] += 1
            basenames[basename] += 1
            tails[tail] += 1

    if dirs_game:
        # Count every measured directory once; the cross product is what matters, not the tally.
        directories = collections.Counter({d: 1 for d in seen_dirs})

    return directories, basenames, tails, variants, no_tail


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--directories", type=int, default=60000)
    parser.add_argument("--basenames", type=int, default=600000)
    parser.add_argument("--variant-coverage", type=float, default=0.999,
                        help="pick the narrowest variant width covering this share of the corpus")
    parser.add_argument("--most-variant", type=int, default=-1,
                        help="variant width to enumerate; 0 emits no variant axis at all, -1 "
                             "picks the narrowest width covering --variant-coverage")
    parser.add_argument("--dirs-game", default="",
                        help="take directories only from this game's capture")
    parser.add_argument("--stem-games", default="",
                        help="comma-separated games to take basenames from; empty means every "
                             "modern game, and naming only the *other* ones asks this game's "
                             "directories against content they name and it does not")
    parser.add_argument("--write-plan", metavar="PATH", required=True)
    options = parser.parse_args(argv)

    dirs_game = options.dirs_game.upper() or None
    stem_games = [t.strip().upper() for t in options.stem_games.split(",") if t.strip()] or None
    directories, basenames, tails, variants, no_tail = vocabulary(dirs_game, stem_games)
    print("directories from %s, basenames from %s"
          % (dirs_game or "every modern game",
             ", ".join(stem_games) if stem_games else "every modern game"),
          file=sys.stderr)
    print("directories %s, basenames %s, tails %s, names with no encoding tail %s"
          % (format(len(directories), ","), format(len(basenames), ","),
             format(len(tails), ","), format(no_tail, ",")),
          file=sys.stderr)
    print("variant index widths: %s" % sorted(variants.items()), file=sys.stderr)
    print("measured tails: %s" % sorted(tails), file=sys.stderr)

    heads = [d for d, _ in directories.most_common(options.directories)]
    stems = [b for b, _ in basenames.most_common(options.basenames)]

    # Which variant indices to enumerate, decided by COVERAGE and not by the widest index seen.
    #
    # Taking the widest was wrong by a factor of a hundred: fourteen names in the corpus carry a
    # four-digit variant, and honouring them pushed the ending list from 7,373 to 730,073 and the
    # whole plan from 3.6T to 352T. Every binary prints its expected coincidental matches, and that
    # number went from 0.28 to 28.1 -- twenty-eight wrong names entering `findings/`, which then seed
    # every later derivation and which CI re-verifies by hash, so nothing downstream catches them.
    # The price of a wider list is paid in the lottery, not in reach.
    seen = sum(variants.values()) or 1
    running = 0
    chosen = max(variants) if variants else 2
    for width in sorted(variants):
        running += variants[width]
        if running / seen >= options.variant_coverage:
            chosen = width
            break
    most = options.most_variant if options.most_variant >= 0 else (10 ** chosen)
    print("variant widths %s; narrowest covering %.3f of them is %d, so most=%d"
          % (sorted(variants.items()), options.variant_coverage, chosen, most),
          file=sys.stderr)

    endings = list(tails)
    for index in range(most):
        for tail in tails:
            endings.append("_%02d%s" % (index, tail))

    # No `end:` line, so the engine cannot peel and sweeps `beginnings x stems` forward instead.
    # Peeling is meant to be nearly free and only is when the ending list is short next to the
    # candidate count; with a few thousand endings and a few thousand beginnings it costs more than
    # the forward sweep it replaces. See contrib/mwii_shared_tail_plan.py --two-column.
    stems = sorted(stem + end for stem in stems for end in endings)
    endings = []

    plan_path = os.path.join(ROOT, options.write_plan)
    base = os.path.splitext(plan_path)[0]
    os.makedirs(os.path.dirname(plan_path), exist_ok=True)
    written = {}
    for what, entries in (("dirs", heads), ("names", stems), ("tails", endings)):
        written[what] = base + ".%s.txt" % what
        with open(written[what], "w", encoding="utf-8", newline="\n") as handle:
            handle.write("\n".join(entries) + "\n")

    relative = lambda path: os.path.relpath(path, ROOT).replace("\\", "/")

    with open(plan_path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(
            "# Written by contrib/modern_sound_plan.py. Regenerate rather than editing.\n"
            "#\n"
            "# Modern sound files are dot-separated paths: iw9.dst.iw9_dst_street_barricade_03"
            ".ln.75.48000.all\n"
            "# is three path components, a basename, and a four-component encoding tail. Nothing\n"
            "# in the carried vocabulary can express that, which is why sound_asset sits at 18.4%%\n"
            "# named in MWII while xanim in the same capture sits at 80.7%%.\n"
            "#\n"
            "# %s directories x %s basenames x %s tails, asked completely on the engine rather\n"
            "# than sampled through a pipe. fold stays yes: these names carry no backslashes at all,\n"
            "# so folding is a no-op here and only Black Ops 4's SAB names need it off.\n\n"
            % (format(len(heads), ","), format(len(stems), ","), format(len(endings), ","))
        )
        handle.write("label: MWII sound paths, whole dot-separated product\n")
        handle.write(
            "describe: every directory measured in the modern sound table crossed with every "
            "basename and every measured encoding tail, with and without a variant index\n\n"
        )
        handle.write("game: MODWAR22\n\n")
        handle.write("begin: @%s\n\n" % relative(written["dirs"]))
        handle.write("stem: @%s\n\n" % relative(written["names"]))
        handle.write("bare: no\n")

    print("\nwrote %s\n\n    bin\\windows\\confirm_plan.exe %s --size"
          % (relative(plan_path), options.write_plan), file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
