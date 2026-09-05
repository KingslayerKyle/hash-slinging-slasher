"""Emit literal native asset filenames from pmr360's public BOCW M16A1 export.

The archive is a BO3 port, so placement, GDT and source-data paths are excluded.
Only original-looking Greyhound export filenames beneath model_export/images and
sound_assets are candidates; no opaque hash placeholders or reconstructed names
are emitted.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import PurePosixPath


ARCHIVE = ".tmp-cw-public-exports/pmr360_bocw_m16a1.rar"
MODEL_OR_IMAGE = re.compile(
    r"^(?:model_export/.+/[^/]+\.xmodel_bin|model_export/.+/images/[^/]+\.png)$",
    re.IGNORECASE,
)
SOUND = re.compile(r"^sound_assets/(t9_weapons/.+)\.wav$", re.IGNORECASE)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sounds", action="store_true")
    args = parser.parse_args()
    listing = subprocess.check_output(["tar", "-tf", ARCHIVE], text=True)
    names: set[str] = set()
    for line in listing.splitlines():
        path = line.replace("\\\\", "/")
        if args.sounds:
            match = SOUND.match(path)
            if match:
                names.add(match.group(1))
        elif MODEL_OR_IMAGE.match(path):
            stem = PurePosixPath(path).stem
            if not stem.lower().startswith(("ximage_", "image_", "material_", "xmodel_")):
                names.add(stem)
    kind = "sound paths" if args.sounds else "model and image names"
    print(f"pmr360 BOCW M16A1 archive: {len(names):,} literal native {kind}", file=sys.stderr)
    print("\n".join(sorted(names)))


if __name__ == "__main__":
    main()
