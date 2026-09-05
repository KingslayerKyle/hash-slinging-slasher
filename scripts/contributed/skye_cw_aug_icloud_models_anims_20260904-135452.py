"""Strict model/animation labels from Skye's public individual CW AUG export.

The ZIP is an original-export-backed BO3 port.  Only verbatim `.xmodel_bin`
and `.xanim_bin` basenames physically present in its export trees are emitted.
Placement, GDT/source-data, generated image composites, and audio paths whose
original full game path is not preserved are deliberately excluded.
"""

from __future__ import annotations

import sys
import zipfile
from pathlib import Path


ARCHIVE = Path(".tmp-skye-cw-aug.zip")


def main() -> None:
    with zipfile.ZipFile(ARCHIVE) as archive:
        names = {
            Path(path).stem.lower()
            for path in archive.namelist()
            if path.endswith((".xmodel_bin", ".xanim_bin"))
        }
    print(
        f"Skye CW AUG: {len(names):,} literal xmodel/xanim basenames",
        file=sys.stderr,
    )
    print("\n".join(sorted(names)))


if __name__ == "__main__":
    main()
