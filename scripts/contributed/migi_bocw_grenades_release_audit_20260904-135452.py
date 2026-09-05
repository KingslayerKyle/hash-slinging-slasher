"""Emit literal native T9 material filenames from MIGI's BOCW grenade VPKs.

This public GitHub release is a Source-engine conversion.  The surrounding
Source paths are deliberately not candidates: only unaltered mtl_wpn_t9_*
filenames physically retained in the VPK directory trees are emitted.
"""

from __future__ import annotations

import struct
import sys
from pathlib import Path


ROOT = Path(".tmp-cw-public-exports/migi_grenades_unpacked")


def c_string(blob: bytes, at: int) -> tuple[str, int]:
    end = blob.index(0, at)
    return blob[at:end].decode("utf-8", "replace"), end + 1


def vpk_paths(path: Path) -> list[str]:
    blob = path.read_bytes()
    if struct.unpack_from("<I", blob, 0)[0] != 0x55AA1234:
        raise ValueError(f"not a VPK: {path}")
    version = struct.unpack_from("<I", blob, 4)[0]
    if version not in (1, 2):
        raise ValueError(f"unsupported VPK version {version}: {path}")
    at = 28 if version == 2 else 12
    tree_end = at + struct.unpack_from("<I", blob, 8)[0]
    paths: list[str] = []
    while at < tree_end:
        extension, at = c_string(blob, at)
        if not extension:
            break
        while True:
            directory, at = c_string(blob, at)
            if not directory:
                break
            while True:
                basename, at = c_string(blob, at)
                if not basename:
                    break
                paths.append(f"{directory}/{basename}.{extension}")
                preload = struct.unpack_from("<H", blob, at + 4)[0]
                at += 18 + preload
    return paths


def main() -> None:
    labels: set[str] = set()
    entries = 0
    for archive in sorted(ROOT.glob("*.vpk")):
        paths = vpk_paths(archive)
        entries += len(paths)
        for name in paths:
            stem = Path(name).stem.lower()
            if stem.startswith("mtl_wpn_t9_"):
                labels.add(stem)
    print(
        f"MIGI BOCW grenade release: {entries:,} VPK entries, "
        f"{len(labels):,} literal native material labels",
        file=sys.stderr,
    )
    print("\n".join(sorted(labels)))


if __name__ == "__main__":
    main()
