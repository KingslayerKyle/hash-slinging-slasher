"""Decode exact safe path labels from Atian Tools 3.2.1's bundled WNI cache."""

from pathlib import Path
import re
import struct


SOURCE = Path("borrowed/atian_acts_3_2_1/acts/bin/package_index/path.wni")
NAME = re.compile(r"^[A-Za-z0-9_./\\-]{3,240}$")


def decompress_lz4_block(source: bytes, expected: int) -> bytes:
    output = bytearray()
    cursor = 0
    while cursor < len(source):
        token = source[cursor]
        cursor += 1
        literals = token >> 4
        if literals == 15:
            while True:
                extra = source[cursor]
                cursor += 1
                literals += extra
                if extra != 255:
                    break
        output.extend(source[cursor : cursor + literals])
        cursor += literals
        if cursor == len(source):
            break
        offset = source[cursor] | source[cursor + 1] << 8
        cursor += 2
        match = token & 15
        if match == 15:
            while True:
                extra = source[cursor]
                cursor += 1
                match += extra
                if extra != 255:
                    break
        match += 4
        if not offset or offset > len(output):
            raise ValueError("invalid LZ4 match offset")
        for _ in range(match):
            output.append(output[-offset])
    if len(output) != expected:
        raise ValueError(f"LZ4 size mismatch: got {len(output)}, expected {expected}")
    return bytes(output)


def main() -> None:
    raw = SOURCE.read_bytes()
    magic, version, entries, packed, unpacked = struct.unpack_from("<I H I I I", raw)
    if magic != 0x20494E57 or version != 1:
        raise ValueError("unexpected WNI header")
    data = decompress_lz4_block(raw[18 : 18 + packed], unpacked)
    cursor = 0
    names: set[str] = set()
    for _ in range(entries):
        cursor += 8
        ending = data.index(0, cursor)
        name = data[cursor:ending].decode("utf-8", errors="strict")
        cursor = ending + 1
        if NAME.fullmatch(name) and sum(character.isalpha() for character in name) >= 3:
            names.add(name)
    if cursor != len(data):
        raise ValueError("trailing WNI data")
    print("\n".join(sorted(names)))


if __name__ == "__main__":
    main()
