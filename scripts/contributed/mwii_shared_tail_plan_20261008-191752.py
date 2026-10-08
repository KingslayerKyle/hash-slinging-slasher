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
from pathlib import Path

ROOT = Path(__file__).resolve().parent
while not (ROOT / "scripts" / "snapshot.py").is_file() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
sys.path.insert(0, str(ROOT / "scripts"))

import settings
import snapshot

ROOT = snapshot.ROOT

# `ll` and `sl` carry no `n`, so the channelspec is `[a-z]{1,4}` rather than `n`-shaped: a stricter
# pattern silently dropped 862 real MWII names in the first version of this measurement.
TAIL = re.compile(r"\.(?P<chan>[a-z]{1,4})\.(?P<qual>\d+)\.48000\.(?P<ext>[a-z_]+)$")
VARIANT = re.compile(r"_\d+$")


def mwii_sound_names(game, harvest):
    """Verified sound-file names, optionally harvested from every modern game's slice of the table.

    All five modern games hash sound files with the **same IW offset**, so a MWIII, BO6, BO7 or MW7
    name is a legal MWII candidate: one hash policy, five vocabularies. A candidate is only ever
    confirmed against MWII's own capture, so harvesting wider costs reach and never correctness --
    and it is the only lever there is, because an unnamed id is a bare hash: it carries no directory
    and no basename, so nothing can be aimed at one pool of ids rather than another.
    """
    table = "fnv1a_xsounds_v2"
    rows = []
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
            restored = snapshot.verified_database_row(table, key, display)
            if restored is None:
                continue
            _, name = restored
            if snapshot.fnv1a(name, game, "sound_asset") & snapshot.ID_MASK != key:
                continue
            rows.append((key, name))

    keep = set()
    for tag in harvest:
        path = [p for p in snapshot.snapshots() if snapshot.read(p).game == tag]
        if not path:
            continue
        keep |= {k: set(v) for k, v in snapshot.read(path[0]).by_pool().items()}.get(
            "sound_asset", set())
    return [name for key, name in rows if key & snapshot.ID_MASK in keep]


def legacy_tails():
    """Trailing token runs from the twelve per-language legacy sound tables.

    Black Ops 4 and Cold War hash sound *files* with the Treyarch offset, so their names are not
    MWII candidates and their directories are worthless here. Their **token runs** are a different
    matter: `vox_frs2_zm_pick_up_weapon_lmg_00` and `vox_kngs_exert_concuss_02` carry exactly the
    trailing phrases MWII writes into `dx_op_ophm_ping_hmmr_pege_enemymovement`, and the line text
    is the part the two eras share -- the speaker code (`frs2`, `ophm`) and the prefix (`vox_`,
    `dx_op_`) are not. 825,316 names across the twelve tables, of which only the tail runs are used.
    """
    folder = Path(settings.tables_csv())
    for path in sorted(folder.glob("fnv1a_*xsounds.csv")):
        table = path.stem
        with path.open(encoding="utf-8", errors="replace") as handle:
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
                _, name = restored
                name = name.replace("\\", "/").lower()
                # Everything from the first dot is the legacy encoding tail, not part of the name.
                directory, _, leaf = name.rpartition("/")
                leaf = leaf.split(".")[0]
                if not leaf or "_" not in leaf:
                    continue
                directory = directory + "/" if directory else ""
                yield directory, VARIANT.sub("", leaf)


def vocabulary(game, min_directories, harvest, own_heads_only=True, legacy=False):
    """Heads from the target game's own names, tails from every harvested game.

    The split matters and is the whole point of widening this way. A **head** is a directory plus
    some of its basename tokens, so a head is only worth carrying if the target game has actually
    been seen to use that directory -- a head borrowed from BO7 reaches nothing in MWII. A **tail**
    is just a trailing token run, and the more games attest one the more likely MWII's own unnamed
    ids wear it, so tails are harvested wide and judged by how many directories attest them.
    """
    heads = collections.Counter()
    support = collections.defaultdict(set)
    tails = collections.Counter()
    variants = collections.Counter()
    names = 0

    for name in mwii_sound_names(game, harvest):
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
        tails[encoding] += 1
        variant = basename[len(core):]
        if variant:
            variants[len(variant) - 1] += 1

        tokens = core.split("_")
        for cut in range(1, len(tokens)):
            tail = "_".join(tokens[cut:])
            support[tail].add(directory)
            if not own_heads_only:
                heads[directory + "_".join(tokens[:cut]) + "_"] += 1

    if own_heads_only:
        # Heads come from the target game's own names alone: a directory MWII has never been seen
        # to use is a directory MWII does not have.
        for name in mwii_sound_names(game, [game]):
            match = TAIL.search(name)
            if not match:
                continue
            directory, _, basename = name[: match.start()].rpartition(".")
            if not directory:
                continue
            core = VARIANT.sub("", basename)
            tokens = core.split("_")
            for cut in range(1, len(tokens)):
                heads[directory + "." + "_".join(tokens[:cut]) + "_"] += 1
        names = len(list(mwii_sound_names(game, [game])))

    carried = {t for t, dirs in support.items() if len(dirs) >= min_directories}
    return heads, carried, tails, variants, names


def add_legacy_tails(min_directories):
    """Legacy token runs that at least `min_directories` legacy directories attest."""
    support = collections.defaultdict(set)
    rows = 0
    for directory, leaf in legacy_tails():
        tokens = leaf.split("_")
        for cut in range(1, len(tokens)):
            support["_".join(tokens[cut:])].add(directory)
            rows += 1
    carried = {t for t, dirs in support.items() if len(dirs) >= min_directories}
    return carried, rows, len(support)


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--game", default="MODWAR22")
    parser.add_argument("--min-directories", type=int, default=2,
                        help="how many directories a tail must be attested in to be carried")
    parser.add_argument("--variant-coverage", type=float, default=0.999)
    parser.add_argument("--most-variant", type=int, default=-1,
                        help="variant width to enumerate; 0 emits no variant axis at all, -1 "
                             "picks the narrowest width covering --variant-coverage. The take axis "
                             "multiplies the tail list, so on a wide cross-game tail vocabulary it "
                             "is also what decides whether the plan fits in memory at all: 13,663 "
                             "tails x 53 encodings x 101 variants is 73 million stem strings, a "
                             "2.8 GB list, on a machine with 8 GB of RAM in total.")
    parser.add_argument("--two-column", action="store_true",
                        help="fold the endings into the stem column so the engine sweeps forward "
                             "instead of peeling; see the note below")
    parser.add_argument("--legacy-tails", action="store_true",
                        help="also harvest trailing token runs from the twelve legacy "
                             "(Black Ops 4 / Cold War) per-language sound tables. Those names are "
                             "Treyarch-hashed and are not MWII candidates; only their line text "
                             "is shared, and it is what MWII's own `dx_op_*_ping_*` names end in.")
    parser.add_argument("--legacy-min-directories", type=int, default=0,
                        help="threshold for legacy tails specifically; 0 reuses "
                             "--min-directories. Dropping it to 1 admits every trailing run the "
                             "twelve legacy tables attest at all -- 117,289 of them against the "
                             "11,581 that two directories agree on. The 'seen twice' test prunes "
                             "noise out of a *shared* vocabulary; 825,316 real voice lines are "
                             "evidence of a different kind, and a phrase recorded once is still a "
                             "phrase the game used.")
    parser.add_argument("--harvest", default="",
                        help="comma-separated modern games to take tails from; empty means the "
                             "target game's own capture")
    parser.add_argument("--write-plan", metavar="PATH", required=True)
    options = parser.parse_args(argv)

    game = options.game.upper()
    harvest = [t.strip().upper() for t in options.harvest.split(",") if t.strip()] or [game]
    heads, carried, tails, variants, names = vocabulary(game, options.min_directories, harvest)
    print("heads from %s, tails harvested from %s"
          % (game, ", ".join(harvest)), file=sys.stderr)
    if options.legacy_tails:
        threshold = options.legacy_min_directories or options.min_directories
        extra, rows, seen = add_legacy_tails(threshold)
        before = len(carried)
        carried = set(carried) | extra
        print("legacy tails at >=%d directories: %d attested cuts over %d distinct runs, %d "
              "carried; tail list %d -> %d"
              % (threshold, rows, seen, len(extra), before, len(carried)),
              file=sys.stderr)

    seen = sum(variants.values()) or 1
    running = 0
    chosen = max(variants) if variants else 2
    for width in sorted(variants):
        running += variants[width]
        if running / seen >= options.variant_coverage:
            chosen = width
            break
    most = options.most_variant if options.most_variant >= 0 else (10 ** chosen)

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