"""Audit literal labels retained in the public MIGI BOCW Melee VPK release."""

from __future__ import annotations

import struct
import sys
from pathlib import Path


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


root = Path(sys.argv[1]) if len(sys.argv) == 2 else Path("borrowed/migi_melee_unpacked")
labels: set[str] = set()
for archive in sorted(root.glob("*.vpk")):
    names = vpk_paths(archive)
    print(f"{archive.name}: {len(names)} entries", file=sys.stderr)
    for name in names:
        print(name, file=sys.stderr)
        stem = Path(name).stem.lower()
        # These are native-style literal filenames retained by the export.  The
        # surrounding Source paths and all converted Source labels are excluded.
        if stem.startswith("mtl_wpn_t9_"):
            labels.add(stem)

for label in sorted(labels):
    print(label)
