"""Modern image channels the short-channel seams cannot express, as a compiled plan.

`modern_material_image_seam` and `modern_image_channels` cut a channel with `[a-z]{1,4}\\d?`, so
the most common BO7 channel of all -- `_thermalmap` (4,410 named, 3,843 of them a material core
plus the channel) -- and every two-segment one (`_m0_v2`, `_m1_v2`, `_dmg_v2`, `_translucence`,
`_emissivitymap` ...) was never offered. Measured on BO7 2026-10-09: 16,164 named images are a
named material core plus a channel; the channel list here is measured off exactly those, at any
length and up to three segments.

Stems are every material core (directory cut off, packed `*` codes skipped) and every image core
cut at a measured channel, from the tables, findings and submissions of every game. Writes the
plan's three lists and the plan; the engine multiplies them.

Spent by: the material and image corpora as they stand; re-run after either grows.
"""
from collections import Counter
from pathlib import Path
import argparse
import sys

ROOT = Path(__file__).resolve().parent.parent


def rows(kinds):
    srcs = []
    for k in kinds:
        srcs += list((ROOT / "cod-name-db" / "csv").glob(f"fnv1a_x{k}s*.csv"))
        for folder in ("findings", "submissions"):
            srcs += list((ROOT / folder).rglob(f"{k}*.txt"))
    for p in srcs:
        for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
            key, sep, v = line.partition(",")
            v = (v if sep else key).strip().lower()
            if v and "," not in v:
                yield v


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--channels", type=int, default=300)
    ap.add_argument("--out", default="plans/w_longch")
    a = ap.parse_args()
    mat = set()
    for n in rows(["material"]):
        core = n.partition("/")[2] if "/" in n else n
        if core and not core.startswith("*"):
            mat.add(core)
            if core.startswith("mtl_"):
                mat.add(core[4:])
    imgs = []
    for n in rows(["image"]):
        imgs += n.rpartition("~")[0].split("&") if "~" in n else [n]
    ch = Counter()
    for n in imgs:
        parts = n.split("_")
        for k in (1, 2, 3):
            if len(parts) > k and "_".join(parts[:-k]) in mat:
                ch["_".join(parts[-k:])] += 1
                break
    chans = [c for c, _ in ch.most_common(a.channels)]
    cs = set(chans)
    stems = set(mat)
    for n in imgs:
        parts = n.split("_")
        for k in (1, 2, 3):
            if len(parts) > k and "_".join(parts[-k:]) in cs:
                stems.add("_".join(parts[:-k]))
    out = Path(a.out)
    (ROOT / f"{out}_stem.txt").write_text("\n".join(sorted(stems)) + "\n")
    (ROOT / f"{out}_end.txt").write_text("\n".join("_" + c for c in chans) + "\n")
    (ROOT / f"{out}.txt").write_text(
        f"label: long image channels on every material and image core\n"
        f"stem: @{out}_stem.txt\nend: @{out}_end.txt\nbare: yes\n")
    print(f"{len(stems):,} stems x {len(chans)} channels; top {chans[:12]}", file=sys.stderr)


if __name__ == "__main__":
    main()
