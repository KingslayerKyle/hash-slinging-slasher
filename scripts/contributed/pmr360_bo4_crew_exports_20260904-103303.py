"""Emit literal asset basenames from pmr360's original BO4 crew exports.

The public archive URLs are documented in METHODS.md.  These are Greyhound/
CoDCharacterTools model exports for the Chaos crew and IX crew.
Only names physically present below ``model_export/`` are used: original XMODEL/XANIM
export basenames and literal PNG/TIFF texture basenames.  The archives also contain
port scaffolding, GDTs and source-data paths, none of which is candidate evidence.
"""
import os
import subprocess
import sys


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARCHIVES = (
    "pmr360_bo4_chaos_main_20260904.zip",
    "pmr360_bo4_chaos_ix_20260904.zip",
)
EXTENSIONS = (".png", ".tiff", ".xmodel_bin", ".xanim_bin")


def main():
    archives = [os.path.join(ROOT, "borrowed", name) for name in ARCHIVES]
    absent = [path for path in archives if not os.path.isfile(path)]
    if absent:
        raise SystemExit("download documented pmr360 BO4 crew archives first: " + ", ".join(absent))
    names = set()
    for archive in archives:
        listing = subprocess.check_output(["tar", "-tf", archive], text=True, encoding="utf-8")
        for path in listing.splitlines():
            lowered = path.lower()
            if "/model_export/" not in lowered or not lowered.endswith(EXTENSIONS):
                continue
            names.add(os.path.basename(lowered).rsplit(".", 1)[0])
    if len(names) < 100:
        raise SystemExit("archives did not expose expected BO4 export corpus")
    print("pmr360 BO4 crew exports: {:,} exact model/image/xanim basenames".format(len(names)), file=sys.stderr)
    for name in sorted(names):
        print(name)


if __name__ == "__main__":
    main()
