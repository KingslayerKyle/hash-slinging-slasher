"""The material/image seam walked with the target game's own image prefixes and endings.

This is a cross product, so it does not print names -- it writes three lists and a plan and lets the
compiled engine multiply them, the way `scripts/uncarried.py` does (see AGENTS.md and
`src/bin/confirm_plan.rs`):

    python contrib/image_siblings_per_game.py --game BLACKOP7
    bin\\windows\\confirm_plan.exe plans/grind/blackop7_imgseam.txt

## Why the shared lists are the wrong key for a modern capture

`scripts/image_siblings.py` crosses material cores with the 14 prefixes and 35 endings measured off
`fnv1a_ximages` in 2026-09-02 -- a legacy table, whose images are spelled `i_t9_<core>_nm`. Black Ops
7's named images are not: the commonest leading tokens are `ui`, `sat`, `cm`, `jup`, `icon`, `cer`,
and its endings are channel words like `thermalmap`. A modern capture's own vocabulary is what its
unnamed ids are waiting for, and it is measurable: hash every published image name under the game's
policy and keep the ones that land on an id its snapshot actually holds. Measured here on BLACKOP7
that recovers 98,370 of the 839,489 image ids the capture holds, from 182,315 named materials.

## The control, which can fail

Every candidate the plan asks about is also offered back against the game's *named* images, and that
count is printed: it is how many names the game holds this reduction can reach from a named material
with these lists. It proves the lists spell the game's naming. It is never a find -- every name it
rebuilds is already published -- and a 0% control means the reduction does not describe this capture
and the candidate count should be read as noise.
"""
import argparse
import collections
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "scripts"))
import snapshot

MASK = (1 << 63) - 1

# A token has to be seen this often to be a naming convention rather than a one-off.
MIN_LIST_SEEN = 20

# These two multiply into every core, so the caps are the cost of the run.
TOP_PREFIXES = 12
TOP_ENDINGS = 48


def game_ids(tag):
    path = os.path.join(snapshot.settings.path("snapshots", "snapshots"), "%s.ids" % tag.lower())
    snap = snapshot.read(path)
    return {pool: {i & MASK for i in ids} for pool, ids in snap.by_pool().items()}


def names_on_ids(kind, tables, wanted, tag):
    """Published names whose hash lands on an id this capture actually holds in this pool."""
    found = []
    for table in tables:
        for raw in snapshot.table_names(table):
            name = raw.strip()
            if name and snapshot.fnv1a(name, tag, kind) & MASK in wanted:
                found.append(name)
    return found


def head(name):
    return name.split("/")[-1].split("_")[0]


def tail(name):
    return name.rsplit("_", 1)[-1] if "_" in name else ""


def reduce_name(name, prefixes, endings):
    """Strip the directory, one leading convention token, and any trailing convention endings."""
    core = name.split("/")[-1]
    if prefixes and core.split("_")[0] in prefixes and "_" in core:
        core = core.split("_", 1)[1]
    changed = True
    while changed and core:
        changed = False
        for end in endings:
            if core.endswith("_" + end) and len(core) > len(end) + 1:
                core = core[: -(len(end) + 1)]
                changed = True
                break
    return core.strip("_")


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--game", required=True)
    parser.add_argument("--min-core", type=int, default=4, help="shorter cores collide with everything")
    args = parser.parse_args()
    tag = args.game.upper()
    short = tag.lower()

    ids = game_ids(tag)
    if "image" not in ids or "material" not in ids:
        raise SystemExit("%s's snapshot has no image or material pool" % tag)
    images = names_on_ids("image", ["fnv1a_ximages_v2", "fnv1a_ximages"], ids["image"], tag)
    materials = names_on_ids("material", ["fnv1a_xmaterials_v2", "fnv1a_xmaterials"], ids["material"], tag)
    if not images:
        raise SystemExit("%s holds no named image ids -- nothing to measure the lists from" % tag)

    prefix_counts = collections.Counter(head(n) for n in images)
    ending_counts = collections.Counter(tail(n) for n in images)
    prefixes = [p for p, c in prefix_counts.most_common(TOP_PREFIXES) if c >= MIN_LIST_SEEN]
    endings = [e for e, c in ending_counts.most_common(TOP_ENDINGS) if c >= MIN_LIST_SEEN and e]

    named = {n.strip().lower() for n in images} | {n.lower() for n in snapshot.confirmed_names("image")}
    strip = set(prefixes)

    cores = set()
    for name in materials:
        core = reduce_name(name, strip, endings)
        if len(core) >= args.min_core:
            cores.add(core)

    control = 0
    for name in images:
        core = reduce_name(name, strip, endings)
        if len(core) >= args.min_core and core in cores:
            control += 1

    root = snapshot.ROOT
    out = os.path.join(root, "contrib")
    prefix_file = "%s/%s_imgseam_prefixes.txt" % (out, short)
    core_file = "%s/%s_imgseam_cores.txt" % (out, short)
    end_file = "%s/%s_imgseam_endings.txt" % (out, short)
    plan = os.path.join(root, "plans", "grind", "%s_imgseam.txt" % short)

    with open(prefix_file, "w", encoding="utf-8") as handle:
        handle.write("\n".join(prefixes) + "\n")
    with open(core_file, "w", encoding="utf-8") as handle:
        handle.write("\n".join(sorted(cores)) + "\n")
    # The bare spelling (prefix + core) is the same cross product with an empty ending.
    with open(end_file, "w", encoding="utf-8") as handle:
        handle.write("\n".join("_" + e for e in endings) + "\n\n")

    with open(plan, "w", encoding="utf-8") as handle:
        handle.write(
            "label: per-game material-to-image channel seam, %s\n" % tag
            + "describe: image prefixes and endings measured off the %s image names this capture "
              "actually holds (%s of %s ids), crossed with cores reduced off the %s materials it "
              "holds. Control: the reduction reaches %s of those named images from a named material.\n"
              % (tag, f"{len(images):,}", f"{len(ids['image']):,}", f"{len(materials):,}", f"{control:,}")
            + "begin: @%s\n" % os.path.relpath(prefix_file, root)
            + "stem:  @%s\n" % os.path.relpath(core_file, root)
            + "end:   @%s\n" % os.path.relpath(end_file, root)
            + "bare: yes\n"
        )

    print("%s: %s named images / %s image ids, %s named materials, %s cores"
          % (tag, f"{len(images):,}", f"{len(ids['image']):,}", f"{len(materials):,}", f"{len(cores):,}"))
    print("control: %s of %s named images reachable from a named material (%.1f%%)"
          % (f"{control:,}", f"{len(images):,}", 100.0 * control / len(images)))
    print("prefixes: %s" % ", ".join("%s(%s)" % (p, prefix_counts[p]) for p in prefixes))
    print("endings:  %s" % ", ".join("%s(%s)" % (e, ending_counts[e]) for e in endings[:14]))
    print("plan: %s -- %s x %s x %s = %s candidates"
          % (plan, len(prefixes), f"{len(cores):,}", len(endings) + 1,
             f"{len(prefixes) * len(cores) * (len(endings) + 1):,}"))


if __name__ == "__main__":
    main()
