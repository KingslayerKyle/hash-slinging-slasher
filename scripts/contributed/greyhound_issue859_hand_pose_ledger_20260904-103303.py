"""Emit FNV-validated exact labels from GreyhoundPackageIndex issue 859.

pmr360's still-open public issue is explicitly titled ``CW/BO4 hand poses and
more [Hash Verified] [xanim]``:
https://github.com/Scobalula/GreyhoundPackageIndex/issues/859

Every candidate is copied from a source ``low60-FNV,label`` row and independently
rechecked before output.  No pose spelling is generated or inferred.  The issue
contains T8, T9, and untagged names, so the caller should confirm the same exact
source ledger against each named title separately rather than assigning types by
prefix.
"""
import json
import re
import sys
import urllib.request


SOURCE = "https://api.github.com/repos/Scobalula/GreyhoundPackageIndex/issues/859"
ROW = re.compile(r"^([0-9a-f]{1,15}),([a-z0-9_]+)$", re.I)
MASK60 = (1 << 60) - 1


def fnv1a(name):
    value = 0xCBF29CE484222325
    for byte in name.lower().replace("\\", "/").encode("utf-8"):
        value = ((value ^ byte) * 0x100000001B3) & 0xFFFFFFFFFFFFFFFF
    return value


def main():
    request = urllib.request.Request(SOURCE, headers={"Accept": "application/vnd.github+json"})
    body = json.loads(urllib.request.urlopen(request, timeout=60).read().decode("utf-8"))["body"]
    labels, malformed, bad_hash = set(), 0, 0
    for raw in body.splitlines():
        row = ROW.fullmatch(raw.strip())
        if not row:
            continue
        short_id, label = row.groups()
        label = label.lower()
        if (fnv1a(label) & MASK60) != int(short_id, 16):
            bad_hash += 1
            continue
        labels.add(label)
    if len(labels) < 200 or bad_hash > 5:
        raise SystemExit("issue 859 failed FNV integrity gate ({} labels, {} mismatches)".format(len(labels), bad_hash))
    print(
        "Greyhound issue #859: {:,} verified labels; {} FNV-mismatched rows rejected".format(
            len(labels), bad_hash
        ),
        file=sys.stderr,
    )
    for label in sorted(labels):
        print(label)


if __name__ == "__main__":
    main()
