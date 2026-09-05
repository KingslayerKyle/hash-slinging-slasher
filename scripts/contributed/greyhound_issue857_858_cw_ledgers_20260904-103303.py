"""Emit source-validated labels from GreyhoundPackageIndex issues 857 and 858.

KingslayerKyle's still-open, explicitly Hash Verified CW image/material issues link
their original attached ``hashes.txt`` ledgers rather than relying on inferred
spellings:
https://github.com/Scobalula/GreyhoundPackageIndex/issues/857
https://github.com/Scobalula/GreyhoundPackageIndex/issues/858
"""
import re
import sys
import urllib.request


SOURCES = (
    "https://github.com/Scobalula/GreyhoundPackageIndex/files/12044806/hashes.txt",
    "https://github.com/Scobalula/GreyhoundPackageIndex/files/12045205/hashes.txt",
)
ROW = re.compile(r"^([0-9a-f]{1,15}),([a-z0-9_./\\-]+)$", re.I)
MASK60 = (1 << 60) - 1


def fnv1a(name):
    value = 0xCBF29CE484222325
    for byte in name.lower().replace("\\", "/").encode("utf-8"):
        value = ((value ^ byte) * 0x100000001B3) & 0xFFFFFFFFFFFFFFFF
    return value


def main():
    labels, malformed, bad_hash = set(), 0, 0
    for source in SOURCES:
        request = urllib.request.Request(source, headers={"User-Agent": "hash-slinging-slasher"})
        for raw in urllib.request.urlopen(request, timeout=60).read().decode("utf-8").splitlines():
            row = ROW.fullmatch(raw.strip())
            if not row:
                malformed += 1
                continue
            short_id, label = row.groups()
            label = label.lower()
            if (fnv1a(label) & MASK60) != int(short_id, 16):
                bad_hash += 1
                continue
            labels.add(label)
    for label in sorted(labels):
        print(label)
    print(
        f"Greyhound issues 857/858: {len(labels)} verified labels; "
        f"{malformed} non-row lines and {bad_hash} FNV-mismatched rows rejected",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
