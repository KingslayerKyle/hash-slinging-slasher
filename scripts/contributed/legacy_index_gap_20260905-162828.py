#!/usr/bin/env python3
"""Names found on disk that the published tables never picked up.

Scraped name data does not always survive being folded into the tables everybody uses now --
the fold is done file by file, and one file's names can be dropped or half-carried without
anybody noticing. This prints the shortfall: every scraped name whose string is absent from
the current tables, plus the cheap decompositions of the composite texture spelling some of
that data uses, so the cores are offered as well as the whole.

Each candidate is a name known to be real somewhere, which is the seeding principle: it is
offered verbatim to the two titles this project solves, where it may or may not exist.

Usage:  python legacy_index_gap.py <names.txt>  |  confirm_list -
"""
import sys


def variants(name):
    """The name itself, plus the pieces the composite spelling is built from."""
    yield name
    if name.startswith("*"):
        yield name[1:]
    # `colour_map&spec_map~<decimal>` is one image built from two. Offer both halves and the
    # undecorated pair, since neither game spells a composite this way and only a core can carry.
    head = name.split("~", 1)[0]
    if head != name:
        yield head
    for part in head.split("&"):
        if part and part != name:
            yield part


def main():
    seen = set()
    for path in sys.argv[1:] or ["-"]:
        fh = sys.stdin if path == "-" else open(path, encoding="utf-8", errors="replace")
        for line in fh:
            name = line.strip()
            if not name:
                continue
            for v in variants(name):
                if v not in seen:
                    seen.add(v)
                    print(v)


if __name__ == "__main__":
    main()
