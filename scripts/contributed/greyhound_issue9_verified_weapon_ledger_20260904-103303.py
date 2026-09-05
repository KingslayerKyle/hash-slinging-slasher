"""Emit independently FNV-validated BO4 weapon labels from a public ledger.

Source: Scobalula/GreyhoundPackageIndex issue 9, "BO4 Weapon Hashes", posted
by EpicZombieSlayer115 on 2020-11-02:
https://github.com/Scobalula/GreyhoundPackageIndex/issues/9

Only its explicitly labelled ``Weapons (Hash Verified)`` code block is read.
Rows labelled "Non-verified" are intentionally excluded.  The issue prints the
low 60 FNV bits, so each exact source spelling is checked before it reaches the
live-game confirmer.  This is a source importer, never a reconstruction from
the ids.
"""
import json
import re
import sys
import urllib.request


SOURCE = "https://api.github.com/repos/Scobalula/GreyhoundPackageIndex/issues/9"
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
    marker = body.lower().find("weapons (hash verified)")
    if marker < 0:
        raise SystemExit("issue no longer exposes its verified weapon block")
    fences = body[marker:].split("```")
    if len(fences) < 3:
        raise SystemExit("issue no longer exposes a fenced verified weapon block")
    labels, bad = set(), 0
    for raw in fences[1].splitlines():
        row = ROW.fullmatch(raw.strip())
        if not row:
            continue
        short_id, label = row.groups()
        label = label.lower()
        if (fnv1a(label) & MASK60) != int(short_id, 16):
            bad += 1
            continue
        labels.add(label)
    if len(labels) < 100 or bad > 5:
        raise SystemExit("verified block failed its FNV integrity gate ({} accepted, {} mismatched)".format(len(labels), bad))
    print(
        "Greyhound issue #9: {:,} FNV-validated verified weapon labels; {} bad source rows rejected".format(
            len(labels), bad
        ),
        file=sys.stderr,
    )
    for label in sorted(labels):
        print(label)


if __name__ == "__main__":
    main()
