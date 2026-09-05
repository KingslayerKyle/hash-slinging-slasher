"""Emit original BO4 model basenames from DevRaw's Alistair's Folly export.

The public DevRaw release is a BO4-to-BO3 port, but unlike its surrounding BO3
scaffolding it retains a separately labelled ``model_export/bo4_xmodels`` tree.
Only non-placeholder `.xmodel_bin` basenames physically in that tree are
evidence.  The archive is downloaded from the public Drive link recorded in
METHODS.md before this generator is run.
"""
import os
import subprocess
import sys


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARCHIVE = os.path.join(ROOT, "borrowed", "devraw_alistairs_folly_bo4.zip")


def main():
    if not os.path.isfile(ARCHIVE):
        raise SystemExit("download DevRaw Alistair's Folly archive first: " + ARCHIVE)
    listing = subprocess.check_output(["tar", "-tf", ARCHIVE], text=True, encoding="utf-8")
    names = set()
    for path in listing.splitlines():
        lowered = path.lower()
        if "/model_export/bo4_xmodels/" not in lowered or not lowered.endswith(".xmodel_bin"):
            continue
        name = os.path.basename(lowered).removesuffix(".xmodel_bin")
        if not name.startswith("xmodel_"):
            names.add(name)
    if len(names) < 4:
        raise SystemExit("DevRaw archive did not expose its expected BO4 xmodel slice")
    print("DevRaw Alistair's Folly: {} exact BO4 xmodel basenames".format(len(names)), file=sys.stderr)
    print(*sorted(names), sep="\n")


if __name__ == "__main__":
    main()
