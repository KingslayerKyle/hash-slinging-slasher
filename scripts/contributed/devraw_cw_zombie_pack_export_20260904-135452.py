"""Emit literal non-opaque asset basenames from DevRaw's CW Zombie Pack.

The archive's `_OwensAssets/t9/` model-export subtree is segregated from BO3
placement and source-data trees.  Only actual exported model, animation, and
image basenames are considered; Greyhound's opaque `image_<hash>` / material
placeholders and `$white` conversion artifacts are excluded.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import PurePosixPath


ARCHIVE = 'borrowed/devraw_cw_zombie_pack.zip'
ROOT = '/model_export/_owensassets/t9/'
EXTENSIONS = ('.xmodel_bin', '.xanim_bin', '.png', '.tif', '.tiff')
OPAQUE = re.compile(r'^(?:x?image|material)_[0-9a-f]+(?:_[a-z])?$')


def main() -> None:
    listing = subprocess.check_output(['tar', '-tf', ARCHIVE], text=True)
    names: set[str] = set()
    for path in listing.splitlines():
        normalized = path.replace('\\', '/')
        lowered = normalized.lower()
        if ROOT not in lowered or not lowered.endswith(EXTENSIONS):
            continue
        name = PurePosixPath(lowered).stem
        if name.startswith('$') or OPAQUE.fullmatch(name):
            continue
        names.add(name)
    if len(names) < 300:
        raise SystemExit('archive did not expose the expected literal CW export corpus')
    print(f'DevRaw CW Zombie Pack: {len(names):,} literal names', file=sys.stderr)
    print('\n'.join(sorted(names)))


if __name__ == '__main__':
    main()
