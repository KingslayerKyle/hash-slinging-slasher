"""Emit literal model/image labels from Shadowily's public BO4 Misty export."""

import re
import sys
import zipfile
from pathlib import PurePosixPath


ARCHIVE = ".tmp-modme-misty-bo4.zip"
ROOT = "model_export/shadowily/xmodels/"
SUFFIXES = (".xmodel_bin", ".tiff", ".tif", ".png", ".dds", ".tga")
OPAQUE = re.compile(r"^(?:x?image|material)_[0-9a-f]+(?:_[a-z])?$")


def main() -> None:
    with zipfile.ZipFile(ARCHIVE) as archive:
        labels = {
            PurePosixPath(entry.filename.lower()).stem
            for entry in archive.infolist()
            if not entry.is_dir()
            and entry.filename.lower().startswith(ROOT)
            and entry.filename.lower().endswith(SUFFIXES)
            and not OPAQUE.fullmatch(PurePosixPath(entry.filename.lower()).stem)
        }
    print(f"Modme BO4 Misty export: {len(labels):,} literal labels", file=sys.stderr)
    for label in sorted(labels):
        print(label)


if __name__ == "__main__":
    main()
