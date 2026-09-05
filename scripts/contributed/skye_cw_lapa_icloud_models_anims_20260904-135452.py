"""Emit literal model and animation labels retained by Skye's public LAPA archive.

The source is the public iCloud document Skye_CW_LAPA.zip.  Only .xmodel_bin
and .xanim_bin entry stems are retained.  WAV leaves deliberately remain
excluded: all are in the port staging directory sound_assets/skye_ports and
are not original native sound-file paths or aliases.
"""

import sys
import zipfile
from pathlib import Path


ARCHIVE = Path(".tmp-skye-cw-lapa.zip")
NATIVE_SUFFIXES = (".xmodel_bin", ".xanim_bin")


def main() -> None:
    with zipfile.ZipFile(ARCHIVE) as archive:
        labels = {
            Path(entry.filename).stem.lower()
            for entry in archive.infolist()
            if not entry.is_dir() and entry.filename.lower().endswith(NATIVE_SUFFIXES)
        }
    for label in sorted(labels):
        print(label)


if __name__ == "__main__":
    main()
