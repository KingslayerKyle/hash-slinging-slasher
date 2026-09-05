"""Strict model/animation labels from Skye's public individual CW M82 export.

Only exact `.xmodel_bin` and `.xanim_bin` basenames physically retained in the
original-export-backed ZIP are emitted.  Port placement, GDT/source data,
generated image composites, and audio paths without their full native game
path are excluded rather than reconstructed.
"""

from __future__ import annotations

import sys
import zipfile
from pathlib import Path


ARCHIVE = Path(".tmp-skye-cw-m82.zip")


def main() -> None:
    with zipfile.ZipFile(ARCHIVE) as archive:
        names = {
            Path(path).stem.lower()
            for path in archive.namelist()
            if path.endswith((".xmodel_bin", ".xanim_bin"))
        }
    print(
        f"Skye CW M82: {len(names):,} literal xmodel/xanim basenames",
        file=sys.stderr,
    )
    print("\n".join(sorted(names)))


if __name__ == "__main__":
    main()
