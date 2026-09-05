"""Emit exact BO4 model and image basenames from the Misty Dropbox Greyhound export.

Run:
    python contrib/misty_bo4_dropbox_export_20260904.py | target\\release\\confirm_list.exe - --game BLKOPS04 --label "Misty BO4 Dropbox export" --script contrib/misty_bo4_dropbox_export_20260904.py

Reads `borrowed/t8_farmgirl_misty_bo4.zip` through the system tar reader.  It writes names only
from the archive's `model_export/` tree, retaining native TIFF image and XMODEL/XANIM export
basenames while excluding `source_data`, custom map placement, and directory strings.  Reusable
after downloading the public ModMe-linked Dropbox folder recorded in METHODS.md.
"""
import os
import subprocess
import sys


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARCHIVE = os.path.join(ROOT, "borrowed", "t8_farmgirl_misty_bo4.zip")
EXTENSIONS = (".tiff", ".xmodel_bin", ".xanim_bin")


def main():
    if not os.path.isfile(ARCHIVE):
        raise SystemExit("download the documented Misty Dropbox export to borrowed/ first")
    listing = subprocess.check_output(["tar", "-tf", ARCHIVE], text=True, encoding="utf-8")
    names = set()
    for path in listing.splitlines():
        lowered = path.lower()
        if not lowered.startswith("model_export/") or not lowered.endswith(EXTENSIONS):
            continue
        names.add(os.path.basename(lowered).rsplit(".", 1)[0])
    if len(names) < 20:
        raise SystemExit("archive did not expose the expected model-export name corpus")
    print("Misty BO4 Dropbox export: {:,} exact model/image basenames".format(len(names)), file=sys.stderr)
    for name in sorted(names):
        print(name)


if __name__ == "__main__":
    main()
