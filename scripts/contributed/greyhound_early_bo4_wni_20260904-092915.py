"""Emit the BO4 name delta carried by Greyhound's early public releases.

Versions 1.3.60, 1.3.81 and 1.7.10 are dated BO4 cache snapshots.  Keep only
spellings absent from the already-audited 1.9.9 snapshot; this is a bounded
release-history source, not a re-run of the same package index.
"""

from pathlib import Path
import argparse
import struct


ROOT = Path("borrowed")
EARLY = ("greyhound_1_3_60_0", "greyhound_1_3_81_0", "greyhound_1_7_10_0")
BASELINE = "greyhound_1_9_9_0"
TYPED_FILES = ("bo4_xanim.wni", "bo4_ximage.wni", "bo4_xmodel.wni", "bo4_xmaterial.wni")
SOUND_FILES = ("bo4_sab.wni",)


def unpack_lz4(source: bytes, expected: int) -> bytes:
    output = bytearray()
    at = 0
    while at < len(source):
        token = source[at]
        at += 1
        literal = token >> 4
        if literal == 15:
            while True:
                extra = source[at]
                at += 1
                literal += extra
                if extra != 255:
                    break
        output.extend(source[at : at + literal])
        at += literal
        if at == len(source):
            break
        offset = source[at] | source[at + 1] << 8
        at += 2
        match = token & 15
        if match == 15:
            while True:
                extra = source[at]
                at += 1
                match += extra
                if extra != 255:
                    break
        match += 4
        if not offset or offset > len(output):
            raise ValueError("invalid LZ4 match")
        for _ in range(match):
            output.append(output[-offset])
    if len(output) != expected:
        raise ValueError(f"LZ4 size mismatch: {len(output)} != {expected}")
    return bytes(output)


def names(path: Path) -> set[str]:
    raw = path.read_bytes()
    magic, version, entries, packed, unpacked = struct.unpack_from("<I H I I I", raw)
    if (magic, version) != (0x20494E57, 1):
        raise ValueError(f"unexpected WNI header: {path}")
    data = unpack_lz4(raw[18 : 18 + packed], unpacked)
    at = 0
    result: set[str] = set()
    for _ in range(entries):
        at += 8
        end = data.index(0, at)
        name = data[at:end].decode("utf-8", errors="strict")
        at = end + 1
        if 3 <= len(name) <= 240 and sum(c.isalpha() for c in name) >= 3:
            result.add(name)
    if at != len(data):
        raise ValueError(f"trailing WNI data: {path}")
    return result


def read_release(release: str, files: tuple[str, ...]) -> set[str]:
    path = ROOT / release / "package_index"
    return set().union(*(names(path / filename) for filename in files))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sounds", action="store_true", help="emit SAB paths only")
    options = parser.parse_args()
    files = SOUND_FILES if options.sounds else TYPED_FILES
    baseline = read_release(BASELINE, files)
    early = set().union(*(read_release(release, files) for release in EARLY))
    for name in sorted(early - baseline):
        print(name)


if __name__ == "__main__":
    main()
