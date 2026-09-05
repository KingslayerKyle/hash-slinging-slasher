"""Emit literal non-opaque names from DevRaw's CW Die Maschine model export.

The public archive is a BO3 port, but this intentionally reads only the
Greyhound-style model_export tree for the exported `c_t9_zmb_ndu_zombie`
family.  It never emits port placement, GDT, source-data, or `ximage_<hash>`
placeholder labels.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import PurePosixPath


ARCHIVE = 'borrowed/devraw_cw_die_maschine_zombies.rar'
ROOT = '/model_export/midget_blaster/characters/c_t9_zmb_ndu_zombie/'
EXTENSIONS = ('.xmodel_bin', '.xanim_bin', '.png', '.tif', '.tiff')


def main() -> None:
    listing = subprocess.check_output(['tar', '-tf', ARCHIVE], text=True)
    names: set[str] = set()
    for path in listing.splitlines():
        normal = path.replace('\\', '/')
        lower = normal.lower()
        if ROOT not in lower or not lower.endswith(EXTENSIONS):
            continue
        name = PurePosixPath(lower).stem
        # Greyhound's synthetic image export name means its original label was
        # unavailable; it cannot be used as source evidence.
        if name.startswith('ximage_') and all(c in '0123456789abcdef' for c in name[7:]):
            continue
        names.add(name)
    if len(names) < 100:
        raise SystemExit('archive did not expose the expected literal export corpus')
    print(f'DevRaw CW Die Maschine export: {len(names):,} literal names', file=sys.stderr)
    print('\n'.join(sorted(names)))


if __name__ == '__main__':
    main()
