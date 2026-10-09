"""What a run actually found, as families -- and the members of those families it missed.

Both a report and a method.

    python scripts/families.py                          what has been found, and its shape
    python scripts/families.py --gaps | confirm_list - --label "family gap filling"

## Why look at your own results

A pass reports a number. A number tells you nothing about what to run next. The shape of what
was found tells you a great deal: forty names all beginning `p9_dun_` says a map's asset set is
half-recovered and worth attacking directly; forty names scattered across forty prefixes says
the general search is working as designed and the next lever is a wider list.

## The gap filler

Where a family is numbered, the numbers found are almost never contiguous. A run that confirms
`..._01`, `..._02` and `..._04` is stating that `..._03` exists, and stating it with more
authority than any global rule: three siblings are evidence about a fourth in a way that a
popularity-ranked ending list cannot be. `--gaps` writes those out, plus a margin past each end
of every observed run.

This is close to `confirm_variants` and not the same. That walks numbers in confirmed names one
at a time against the whole snapshot; this notices that a *family* is incomplete and fills the
holes, including families whose members came from different runs and different contributors.

## Options

    --gaps           write the missing family members as candidates, and nothing else
    --margin N       how far past each end of an observed run to go (default 4)
    --kind TYPE      only this asset type
    --top N          how many rows per section in the report (default 20)
"""
import collections
import os
import re
import sys

import snapshot

# A trailing number, which is where a family index almost always sits, and the width it was
# written at -- `_007` and `_7` are different names and only one of them is right.
NUMBERED = re.compile(r"^(.*?)(\d+)([^0-9]*)$")

# Sound takes sit before the encoding tail, whose quality/rate fields also contain digits.
# Prefer that take only for the recognised modern or legacy tail shapes; otherwise keep the
# ordinary final-number rule. Captures preserve the original spelling and zero-padding.
SOUND_TAKE = re.compile(
    r"^(.*_)(\d{1,3})("
    r"\.[a-z]{1,4}\d*\.\d+\.\d+\.[a-z_]+"
    r"|\.[a-z]{2}\d+\.pc(?:\.[a-z_]+)?\.snd"
    r")$", re.IGNORECASE | re.ASCII
)


def families(names):
    """{(before, width, after): {numbers seen}} over every name carrying a number."""
    found = collections.defaultdict(set)

    for name in names:
        match = SOUND_TAKE.match(name) or NUMBERED.match(name)
        if not match:
            continue

        before, digits, after = match.groups()

        # A one-character stem is not a family, it is a coincidence.
        if len(before) < 3:
            continue

        found[(before, len(digits), after)].add(int(digits))

    return found


# The widest span a family may cover before it stops being a family.
#
# Without this, two names that happen to share a stem and carry `_0` and `_999999` describe a
# million-member family that does not exist, and one such pair drowns every real family in the
# output. Measured on the current corpus: capping at 512 takes the candidate count from 346
# million to a few hundred thousand and loses no family with more than two observed members.
WIDEST = 512


def gaps(found, margin):
    """Every number a family is missing between its members, plus a margin past each end."""
    for (before, width, after), seen in found.items():
        if len(seen) < 2:
            continue

        low, high = min(seen), max(seen)
        if high - low > WIDEST:
            continue

        for number in range(max(0, low - margin), high + margin + 1):
            if number in seen:
                continue
            yield "%s%0*d%s" % (before, width, number, after)


def report(names, top):
    directories = collections.Counter()
    leading = collections.Counter()
    trailing = collections.Counter()
    segments = collections.Counter()

    for name in names:
        head, sep, _ = name.partition("/")
        if sep:
            directories[head + "/"] += 1

        parts = name.replace("/", "_").split("_")
        if len(parts) > 1:
            leading[parts[0] + "_"] += 1
            trailing["_" + parts[-1]] += 1
        segments[len(parts)] += 1

    print("%d names\n" % len(names))

    for title, counter in (
        ("directories", directories),
        ("leading tokens", leading),
        ("trailing tokens", trailing),
    ):
        if not counter:
            continue
        print("%s" % title)
        for value, count in counter.most_common(top):
            print("  %-40s %6d" % (value, count))
        print()

    print("segments per name")
    for count in sorted(segments):
        print("  %2d segments %6d" % (count, segments[count]))

    found = families(names)
    incomplete = [(len(seen), key) for key, seen in found.items() if len(seen) >= 2]
    incomplete.sort(reverse=True)

    print("\n%d numbered families, %d with two or more members" % (len(found), len(incomplete)))
    for count, (before, width, after) in incomplete[:top]:
        print("  %-46s %d members, width %d" % (before + "N" + after, count, width))

    missing = sum(1 for _ in gaps(found, 4))
    print(
        "\n%d candidates would come out of --gaps at the default margin.\n"
        "Those are the strongest candidates this repository can produce: a family with three\n"
        "confirmed members is evidence about a fourth that no global rule can match." % missing
    )


def main(argv):
    kind = argv[argv.index("--kind") + 1] if "--kind" in argv else None
    margin = int(argv[argv.index("--margin") + 1]) if "--margin" in argv else 4
    top = int(argv[argv.index("--top") + 1]) if "--top" in argv else 20

    names = snapshot.confirmed_names(kind)
    names = sorted({name.strip().lower().replace("\\", "/") for name in names if name.strip()})

    if not names:
        raise SystemExit(
            "nothing confirmed yet%s. Run a search first -- this reads what has been found,\n"
            "in `findings/` and in every merged submission in `submissions/`."
            % (" for %s" % kind if kind else "")
        )

    if "--gaps" in argv:
        for candidate in gaps(families(names), margin):
            sys.stdout.write(candidate + "\n")
        return

    report(names, top)


if __name__ == "__main__":
    main(sys.argv[1:])
