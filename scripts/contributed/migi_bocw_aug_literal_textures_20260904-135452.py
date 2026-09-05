"""Emit exact BOCW-texture basenames retained in MIGI's public AUG VPK.

This is deliberately not a conversion-path importer.  The release is a
Source-engine port, but its VPK directory has a small contiguous group of
literal `weapon_vm_sm_t9powerburst_*` texture filenames.  They are retained
verbatim from the package; ordinary Source paths, game scripts, and generated
skin icons are excluded.
"""

from __future__ import annotations

import struct
from pathlib import Path


ARCHIVE = Path(".tmp-migi-aug/m_bocw_aug.vpk")
PREFIX = "weapon_vm_sm_t9powerburst_"


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
    paths = vpk_paths(ARCHIVE)
    labels = {
        Path(path).stem.lower()
        for path in paths
        if Path(path).stem.lower().startswith(PREFIX)
    }
    print(
        f"MIGI BOCW AUG: {len(paths):,} VPK entries, "
        f"{len(labels):,} literal T9 texture basenames",
        file=__import__("sys").stderr,
    )
    print("\n".join(sorted(labels)))


if __name__ == "__main__":
    main()
