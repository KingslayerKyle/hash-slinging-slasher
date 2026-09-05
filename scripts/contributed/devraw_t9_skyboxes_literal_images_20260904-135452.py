"""Emit literal image labels physically retained by Nastian's T9 Skyboxes ZIP."""

import sys
import zipfile
from pathlib import Path


ARCHIVE = Path(".tmp-devraw-t9-skyboxes")
PREFIX = "nastian - t9 skyboxes/texture_assets/black_ops_cw/skyboxes/"


def main() -> None:
    with zipfile.ZipFile(ARCHIVE) as archive:
        labels = {
            Path(entry.filename).stem.lower()
            for entry in archive.infolist()
            if not entry.is_dir()
            and entry.filename.lower().startswith(PREFIX)
            and entry.filename.lower().endswith(".exr")
        }
    for label in sorted(labels):
        print(label)


if __name__ == "__main__":
    main()
