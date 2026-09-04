"""Derive Cold War ground, decal, and architecture materials from image cores and map prefixes."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def main():
    cores = set()

    # Extract t9_ cores from ximages
    img_path = ROOT / "cod-name-db" / "csv" / "fnv1a_ximages.csv"
    if img_path.exists():
        with open(img_path, encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split(",")
                if len(parts) >= 2 and parts[1].startswith("i_t9_"):
                    core = parts[1][2:]
                    core = re.sub(r'_[a-z0-9]{1,3}$', '', core)
                    cores.add(core)

    # Extract t9_ cores from xmaterials
    mtl_path = ROOT / "cod-name-db" / "csv" / "fnv1a_xmaterials.csv"
    if mtl_path.exists():
        with open(mtl_path, encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split(",")
                if len(parts) >= 2 and "t9_" in parts[1]:
                    core = parts[1].split("/", 1)[-1] if "/" in parts[1] else parts[1]
                    if core.startswith("mtl_"):
                        core = core[4:]
                    core = re.sub(r'_(dsp|decal|wet|snow|puddle|blend|clean|dirty|dry|lrg|sml|med)$', '', core)
                    if core.startswith("t9_"):
                        cores.add(core)

    prefixes = ["", "mc/", "vd/", "wc/", "splm/", "clt/", "mcs/", "cltp/"]
    suffixes = [
        "", "_dsp", "_decal", "_decal_dsp", "_blend", "_wet", "_snow",
        "_puddle", "_dirty", "_dry", "_lrg", "_sml", "_med"
    ]

    cands = set()
    for core in cores:
        for s in suffixes:
            for p in prefixes:
                cands.add(f"{p}{core}{s}")
                cands.add(f"{p}mtl_{core}{s}")

    for c in sorted(cands):
        sys.stdout.write(c + "\n")

if __name__ == "__main__":
    main()
