r"""Black Ops 3's official asset names, read from the manifests the tools ship.

    python contrib/harvest_bo3_assetlist.py

Finds the build through the **`TA_TOOLS_PATH`** environment variable the mod tools set, so it
works on anybody's install without a hardcoded path.

## Why only this one path

The obvious version of this script walked the whole Black Ops 3 install, and it was wrong. Most
people using this repository *have* the mod tools -- it is largely why they want these names
unhashed -- and a mod tools tree is a **working directory**, not the shipped game. `model_export/`,
`source_data/`, `texture_assets/` and `share/raw/` are where a modder's own and the community's
assets live, in the thousands.

Measured on the install this was written on, whose owner uses the tools only to release their own
work and so has about the cleanest tree in the community -- a **floor**, not a typical case: one
modder's folder contributed **1,216 names**, and they are the dangerous shape rather than obvious
rubbish:

    t10_ar_coslo723_anim
    wpn_t10_p01_ar_coslo723_barrel_v0_c

`t10` is **Black Ops 6**. Those read exactly like official Treyarch names, they can never be in
either title this project searches, and METHODS.md already records every `_v2` table as measured
dead. On an install with a real mod library that is most of the corpus.

The general rule it cost 867,766 names to learn: **seed only from something every contributor has
identical bytes of.** A method seeded from a user-writable directory gives a different corpus on
every disk, so it cannot be reproduced and its fingerprint -- the whole mechanism that stops two
people grinding the same ground -- means nothing.

`zone_source/all/assetlist/*.csv` passes that test. They are the shipped per-zone manifests, one
`type,name` row per asset. The one edit people do make is to put `//` in front of a row, which is
how the tools let you *override* that asset -- the row is otherwise unchanged, so the name on it is
still Treyarch's and is read rather than skipped. The other trustworthy path is
`zone/` itself, which `contrib/harvest_bo3.py` already reads.
"""
import argparse
import collections
import glob
import os
import re
import sys

STEAM = r"C:\Program Files (x86)\Steam\steamapps\common\Call of Duty Black Ops III"
SEPARATORS = set("_/")

# A row is `type,name`, and the type is a plain identifier.
#
# **A commented-out row still names an official asset.** In the Black Ops 3 tools, putting `//` in
# front of a line in one of these manifests is how you *override* that asset -- the build stops
# taking Treyarch's copy and takes yours instead. Many people do it, and the row is not changed in
# any other way, so the name on it is exactly as shipped. Skipping those would throw away real
# names for no reason, so the marker is stripped and the row is read.
#
# The marker is only ever recognised at the **start of a line**, and only `//`. `#` is legal
# *inside* a name -- a techset is spelled `2d_add#a60c435b` -- so treating it as a comment
# anywhere would quietly truncate names.
COMMENT = "//"
KIND = re.compile(r"^[a-z][a-z0-9_]*$")


def tools_root(given):
    if given:
        return given
    from_environment = os.environ.get("TA_TOOLS_PATH", "").strip().rstrip("\\/")
    return from_environment or STEAM


def keep(text):
    if len(text) < 6 or len(text) > 160:
        return False
    if not any(character in SEPARATORS for character in text):
        return False
    return sum(character.isalpha() for character in text) >= 3


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", default=None, help="overrides TA_TOOLS_PATH")
    parser.add_argument("--all-locales", action="store_true",
                        help="read every zone_source locale, not only `all/`")
    parser.add_argument("--typed", action="store_true",
                        help="write `type,name` rows rather than bare names")
    parser.add_argument("--out", default=os.path.join("borrowed", "bo3_assetlist.txt"))
    options = parser.parse_args(argv)

    root = tools_root(options.root)
    # `all/` is the shared half; the locale folders beside it are the same shipped structure and
    # carry the localised assets -- 247 manifests between them against 19, and about a third more
    # names. Same file, same format, same nobody-edits-it-except-to-override.
    locale = "*" if options.all_locales else "all"
    folder = os.path.join(root, "zone_source", locale, "assetlist")
    manifests = sorted(glob.glob(os.path.join(folder, "*.csv")))
    if not manifests:
        raise SystemExit(
            "no manifests under %s\n"
            "Set TA_TOOLS_PATH, or pass --root, pointing at a Black Ops 3 mod tools install."
            % folder
        )

    names = set()
    kinds = collections.Counter()
    typed = []
    skipped = 0
    overridden = 0

    for path in manifests:
        with open(path, encoding="utf-8-sig", errors="replace") as handle:
            for line in handle:
                row = line.strip()
                if row.startswith(COMMENT):
                    row = row[len(COMMENT) :].strip()
                    overridden += 1
                kind, _, name = row.partition(",")
                kind = kind.strip().strip('"').lower()
                name = name.strip().strip('"').replace("\\", "/").lower()
                if not name:
                    continue
                if not KIND.match(kind):
                    skipped += 1
                    continue
                kinds[kind] += 1
                typed.append((kind, name))
                for spelling in (name, os.path.splitext(name)[0], os.path.basename(name)):
                    if keep(spelling):
                        names.add(spelling)

    with open(options.out, "w", encoding="utf-8") as handle:
        if options.typed:
            handle.write("\n".join("%s,%s" % row for row in sorted(set(typed))) + "\n")
        else:
            handle.write("\n".join(sorted(names)) + "\n")

    print("%d manifest(s) under %s" % (len(manifests), folder), file=sys.stderr)
    if overridden:
        print("   %s row(s) commented out to override the shipped asset; the name is still"
              " Treyarch's, so it is read" % format(overridden, ","), file=sys.stderr)
    if skipped:
        print("   %s row(s) ignored: no asset type" % format(skipped, ","), file=sys.stderr)
    for kind, count in kinds.most_common(10):
        print("   %8s  %s" % (format(count, ","), kind), file=sys.stderr)
    print("\n%s distinct name(s) -> %s" % (format(len(names), ","), options.out), file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
