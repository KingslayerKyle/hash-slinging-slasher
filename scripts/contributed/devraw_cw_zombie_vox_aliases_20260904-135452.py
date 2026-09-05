"""Literal alias names from DevRaw's downloadable CW Zombie VOX archive.

Only the CSV Name field is emitted.  The FileSpec paths deliberately point at
the port's `_werelupus` BO3 staging directory and are not native T9 paths.
"""

import csv
import io
import subprocess
from pathlib import Path

ARCHIVE = Path('borrowed/devraw_cw_zombie_vox.7z')
CSV_PATH = 'share/raw/sound/aliases/_werelupus/BOCW_zombies_vox.csv'


def main() -> None:
    payload = subprocess.check_output(['tar', '-xOf', str(ARCHIVE), CSV_PATH])
    rows = csv.DictReader(io.StringIO(payload.decode('utf-8-sig')))
    names = {row['Name'].strip() for row in rows if row.get('Name', '').strip()}
    for name in sorted(names):
        print(name)


if __name__ == '__main__':
    main()
