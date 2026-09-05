"""Emit original T9 asset basenames from Eric Maynard's ModelGetter perk archive.

Run:
    python contrib/eric_p9_perk_archive_20260904.py | target\\release\\confirm_list.exe - --game BLKOPSCW --label "Eric P9 perk archive original names" --script contrib/eric_p9_perk_archive_20260904.py

Reads the downloaded `borrowed/eric_p9_perk_machines.rar` archive through the system `tar`
reader and writes one exact basename per line.  The archive includes imported T8/T7 files for
placement; only original T9/P9 image, xmodel, and xanim export names are retained.  Reusable
after downloading the public ModMe MediaFire attachment recorded in METHODS.md.
"""
import os
import re
import subprocess
import sys


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARCHIVE = os.path.join(ROOT, "borrowed", "eric_p9_perk_machines.rar")
EXTENSIONS = (".png", ".xmodel_bin", ".xanim_bin")
ORIGINAL = re.compile(r"^(?:i_p9_|i_mtl_wpn_t9_|i_wpn_t9_|p9_|t9_|wpn_zm_.*t9$|vm_.*t9$)")


def main():
    if not os.path.isfile(ARCHIVE):
        raise SystemExit("download the documented ModMe attachment to borrowed/ first")
    paths = subprocess.check_output(["tar", "-tf", ARCHIVE], text=True, encoding="utf-8")
    names = set()
    for path in paths.splitlines():
        name = os.path.basename(path).lower()
        if not name.endswith(EXTENSIONS):
            continue
        name = name.rsplit(".", 1)[0]
        if ORIGINAL.match(name):
            names.add(name)
    # `vm_` assets have no T9 marker in their basename, but this archive's only xanim exports
    # sit inside `model_export/t9_perks/`; retain those by rechecking their full archive path.
    for path in paths.splitlines():
        if "/t9_perks/" not in path.lower() or not path.lower().endswith(".xanim_bin"):
            continue
        names.add(os.path.basename(path).lower().rsplit(".", 1)[0])
    print("Eric P9 perk archive: {:,} original-looking T9/P9 basenames".format(len(names)), file=sys.stderr)
    for name in sorted(names):
        print(name)


if __name__ == "__main__":
    main()
