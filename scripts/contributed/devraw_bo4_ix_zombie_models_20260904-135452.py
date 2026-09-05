"""Emit literal non-opaque model/image labels from DevRaw's BO4 IX export."""

import re
import sys
import zipfile
from pathlib import PurePosixPath


ARCHIVE = ".tmp-devraw-bo4-ix-zombie-models"
ROOT = "model_export/_werelupus/bo4/ix zombie models/"
SUFFIXES = (".xmodel_bin", ".png", ".tif", ".tiff", ".dds", ".tga")
OPAQUE = re.compile(r"^(?:x?image|material)_[0-9a-f]+(?:_[a-z])?$")


def main() -> None:
    with zipfile.ZipFile(ARCHIVE) as archive:
        labels = {
            PurePosixPath(entry.filename.lower()).stem
            for entry in archive.infolist()
            if not entry.is_dir()
            and entry.filename.lower().startswith(ROOT)
            and entry.filename.lower().endswith(SUFFIXES)
            and not PurePosixPath(entry.filename).stem.startswith("$")
            and not OPAQUE.fullmatch(PurePosixPath(entry.filename.lower()).stem)
        }
    print(f"DevRaw BO4 IX export: {len(labels):,} literal labels", file=sys.stderr)
    for label in sorted(labels):
        print(label)


if __name__ == "__main__":
    main()
