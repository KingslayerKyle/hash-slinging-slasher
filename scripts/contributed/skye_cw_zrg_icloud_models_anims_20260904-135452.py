"""Strict model/animation labels from Skye's public individual CW ZRG export.

Only exact `.xmodel_bin` and `.xanim_bin` basenames physically retained in the
original-export-backed ZIP are emitted.  Its audio leaf filenames live below
the port staging path, not their original full game paths, and are excluded.
"""

from __future__ import annotations

import sys
import zipfile
from pathlib import Path


ARCHIVE = Path(".tmp-skye-cw-zrg.zip")


def main() -> None:
    with zipfile.ZipFile(ARCHIVE) as archive:
        names = {
            Path(path).stem.lower()
            for path in archive.namelist()
            if path.endswith((".xmodel_bin", ".xanim_bin"))
        }
    print(
        f"Skye CW ZRG 20mm: {len(names):,} literal xmodel/xanim basenames",
        file=sys.stderr,
    )
    print("\n".join(sorted(names)))


if __name__ == "__main__":
    main()
