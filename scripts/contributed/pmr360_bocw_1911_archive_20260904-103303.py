"""Emit literal native asset names preserved by pmr360's public BOCW 1911 export.

The archive is a BO3 port, so this deliberately carries only filenames under
Greyhound-style ``model_export``, ``xanim_export``, image, and ``sound_assets``
trees.  It never turns BO3 placement folders or GDT/script text into candidates.
"""

from __future__ import annotations

import re
import subprocess
import sys
import argparse
from pathlib import PurePosixPath


ARCHIVE = "borrowed/pmr360_bocw_1911.rar"
NATIVE = re.compile(
    r"^(?:model_export|xanim_export)/.+/(?:[^/]+)\.(?:xmodel_bin|xanim_bin)$"
    r"|^model_export/.+/images/(?:[^/]+)\.png$"
    r"|^sound_assets/(t9_weapons/.+)\.wav$",
    re.IGNORECASE,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sounds", action="store_true")
    args = parser.parse_args()
    listing = subprocess.check_output(["tar", "-tf", ARCHIVE], text=True)
    names: set[str] = set()
    for line in listing.splitlines():
        path = line.replace("\\", "/")
        match = NATIVE.match(path)
        if not match:
            continue
        if match.group(1):
            names.add(match.group(1))
        else:
            stem = PurePosixPath(path).stem
            # Greyhound uses opaque ximage_* exports when the original name was
            # unavailable; those are not source-derived names.
            if not stem.lower().startswith("ximage_"):
                names.add(stem)
    names = {name for name in names if name.startswith("t9_weapons/") == args.sounds}
    kind = "sound paths" if args.sounds else "model, animation, and image names"
    print(
        f"pmr360 BOCW 1911 archive: {len(names):,} literal native {kind}",
        file=sys.stderr,
    )
    print("\n".join(sorted(names)))


if __name__ == "__main__":
    main()
