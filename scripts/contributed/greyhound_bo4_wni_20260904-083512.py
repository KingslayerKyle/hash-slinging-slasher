"""Decode Greyhound 1.9.9.0's archived BO4 WNI name-cache entries exactly."""

from pathlib import Path
import argparse
import struct
import sys


ROOT = Path("borrowed/greyhound_1_9_9_0/package_index")
TYPED_FILES = ("bo4_xanim.wni", "bo4_ximage.wni", "bo4_xmodel.wni", "bo4_xmaterial.wni")
SOUND_FILES = ("bo4_sab.wni",)


def decompress_lz4_block(source: bytes, expected: int) -> bytes:
    """Decode the raw LZ4 block format Greyhound's WNI reader uses."""
    output = bytearray()
    cursor = 0
    while cursor < len(source):
        token = source[cursor]
        cursor += 1
        literal_length = token >> 4
        if literal_length == 15:
            while True:
                extra = source[cursor]
                cursor += 1
                literal_length += extra
                if extra != 255:
                    break
        output.extend(source[cursor : cursor + literal_length])
        cursor += literal_length
        if cursor == len(source):
            break
        offset = source[cursor] | (source[cursor + 1] << 8)
        cursor += 2
        match_length = token & 15
        if match_length == 15:
            while True:
                extra = source[cursor]
                cursor += 1
                match_length += extra
                if extra != 255:
                    break
        match_length += 4
        if not offset or offset > len(output):
            raise ValueError("invalid LZ4 match offset")
        for _ in range(match_length):
            output.append(output[-offset])
    if len(output) != expected:
        raise ValueError(f"LZ4 size mismatch: got {len(output)}, expected {expected}")
    return bytes(output)


def names_from_wni(path: Path) -> set[str]:
    raw = path.read_bytes()
    magic, version, entries, packed, unpacked = struct.unpack_from("<I H I I I", raw)
    if magic != 0x20494E57 or version != 1:
        raise ValueError(f"unexpected WNI header in {path}")
    data = decompress_lz4_block(raw[18 : 18 + packed], unpacked)
    cursor = 0
    names: set[str] = set()
    for _ in range(entries):
        cursor += 8  # FNV key; candidate confirmation recomputes it independently.
        ending = data.index(0, cursor)
        name = data[cursor:ending].decode("utf-8", errors="strict")
        cursor = ending + 1
        if 3 <= len(name) <= 240 and sum(character.isalpha() for character in name) >= 3:
            names.add(name)
    if cursor != len(data):
        raise ValueError(f"trailing WNI data in {path}")
    return names


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sounds", action="store_true", help="emit only SAB entries")
    options = parser.parse_args()
    names: set[str] = set()
    for filename in SOUND_FILES if options.sounds else TYPED_FILES:
        names.update(names_from_wni(ROOT / filename))
    print("\n".join(sorted(names)))


if __name__ == "__main__":
    main()
