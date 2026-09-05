"""Emit FNV-validated labels from Richkiller's independent BO4 decoded-texture ledger.

Run:
    python contrib/richkiller_bo4_texture_ledger_20260904.py | target\\release\\confirm_list.exe - --game BLKOPS04 --label "Richkiller BO4 decoded texture ledger" --script contrib/richkiller_bo4_texture_ledger_20260904.py

Reads the public plaintext export linked from Richkiller's BO4 decoding post.  It writes exact
labels to stdout and rejects malformed lines: the ledger prints only FNV's low 60 bits, so each
label is independently checked against that truncated source value before confirmation supplies
the full live-game proof.  This is a reusable external-source importer.
"""
import re
import sys
import urllib.request


SOURCE = "https://docs.google.com/document/d/1L-xodTuyZ41blEKUOwshgaRm0u5Fq77tHPIQSW_YooU/export?format=txt"
# The 60-bit display hash is hexadecimal without zero padding: most rows have fifteen digits,
# while values whose high nibble is zero have fourteen (and the grammar permits fewer).
ROW = re.compile(r"^([0-9a-f]{1,15}),([^\r\n,]+)$", re.I)
MASK60 = (1 << 60) - 1


def fnv1a(name):
    value = 0xCBF29CE484222325
    for byte in name.lower().replace("\\", "/").encode("utf-8"):
        value = ((value ^ byte) * 0x100000001B3) & 0xFFFFFFFFFFFFFFFF
    return value


def main():
    text = urllib.request.urlopen(SOURCE, timeout=60).read().decode("utf-8-sig")
    labels, malformed, bad_hash = set(), 0, 0
    for raw in text.splitlines():
        match = ROW.fullmatch(raw.strip())
        if not match:
            malformed += bool(raw.strip())
            continue
        short_id, label = match.groups()
        label = label.strip().lower()
        if fnv1a(label) & MASK60 != int(short_id, 16):
            bad_hash += 1
            continue
        labels.add(label)
    if len(labels) < 20_000 or bad_hash > 10:
        raise SystemExit("source ledger failed its FNV integrity gate")
    print(
        "Richkiller ledger: {:,} verified labels; {} malformed lines; {} hash-mismatched rows".format(
            len(labels), malformed, bad_hash
        ),
        file=sys.stderr,
    )
    for label in sorted(labels):
        print(label)


if __name__ == "__main__":
    main()
