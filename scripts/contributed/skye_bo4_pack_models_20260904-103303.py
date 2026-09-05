"""Emit preserved BO4 xmodel basenames from Skye's original BO4 export pack.

The public archive is the BO4 Weapon Pack linked from the archived ModMe master
thread: https://raw.githubusercontent.com/dtzxporter/ModmeForum/main/wiki/threads/2565.md
and the direct Mega payload is:
https://mega.nz/file/kPAEEKyD#LmMqT3b0rzqcWl6_EV5lZBpQa_SbeyeHgMzMvl7AkaE

Only XMODEL_BIN names inside the pack's ``model_export/skye_ports/t8_*`` export
tree are emitted.  That excludes its separately bundled H1/Scobalula assets,
converted map placement, and ximage_<hash> placeholders.  These are exact
basenames as preserved by the BO4 export, not labels reconstructed from hashes.
"""
import os
import subprocess
import sys


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARCHIVE = os.path.join(ROOT, "borrowed", "skye_bo4_pack.zip")
PREFIX = "skye's bo4 pack/model_export/skye_ports/t8_"


def main():
    if not os.path.isfile(ARCHIVE):
        raise SystemExit("download Skye's public BO4 pack to borrowed/skye_bo4_pack.zip first")
    listing = subprocess.check_output(["tar", "-tf", ARCHIVE], text=True, encoding="utf-8")
    names = set()
    for path in listing.splitlines():
        lowered = path.replace("\\", "/").lower()
        if not lowered.startswith(PREFIX) or not lowered.endswith(".xmodel_bin"):
            continue
        names.add(os.path.basename(lowered).rsplit(".", 1)[0])
    if len(names) < 100:
        raise SystemExit("archive did not expose the expected BO4 model-export corpus")
    print("Skye BO4 weapon export: {:,} preserved xmodel basenames".format(len(names)), file=sys.stderr)
    for name in sorted(names):
        print(name)


if __name__ == "__main__":
    main()
