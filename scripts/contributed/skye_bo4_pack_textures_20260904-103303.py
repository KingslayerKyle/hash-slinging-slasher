"""Emit literal BO4 texture basenames preserved by Skye's original export pack.

The TIFF tree is overwhelmingly Greyhound's ``ximage_<hash>`` placeholders.
Those are intentionally excluded: only an original-looking ``i_`` or ``mtl_``
basename is a spelling that can be checked against the game.
"""

import os
import re
import subprocess
import sys


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARCHIVE = os.path.join(ROOT, "borrowed", "skye_bo4_pack.zip")
PREFIX = "skye's bo4 pack/model_export/skye_ports/t8_"
NAME = re.compile(r"(?:i|mtl)_[a-z0-9_]+$")


def main() -> None:
    if not os.path.isfile(ARCHIVE):
        raise SystemExit("download Skye's public BO4 pack to borrowed/skye_bo4_pack.zip first")
    listing = subprocess.check_output(["tar", "-tf", ARCHIVE], text=True, encoding="utf-8")
    names = set()
    for path in listing.splitlines():
        lowered = path.replace("\\", "/").lower()
        if not lowered.startswith(PREFIX) or not lowered.endswith((".tiff", ".tif")):
            continue
        name = os.path.basename(lowered).rsplit(".", 1)[0]
        if NAME.fullmatch(name):
            names.add(name)
    print("Skye BO4 weapon export: {} literal texture basenames".format(len(names)), file=sys.stderr)
    for name in sorted(names):
        print(name)


if __name__ == "__main__":
    main()
