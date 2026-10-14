"""Images named from materials, with the material->image templates measured instead of assumed.

A modern material `m/accessory_cigar_01_lit` holds images `accessory_cigar_01_lit_thermalmap`,
`..._m0_v2`, `cm_<base>_pri` and so on. images_from_materials.rs crosses a fixed set of openings
with every ending in the tables; this measures the (opening, ending) PAIRS that actually occur
between a named material base and a named image, across every modern game (they share one id
space), and applies each measured pair to every named material base. The pair is the unit,
so `cm_` only ever meets `_pri`/`_sec`-style endings and the space stays small.

Bases of a material: the name past its directory, and that with `mtl_` taken off.

    python scripts/export_named.py BLACKOP6 BLACKOP7 YAMYAMOK MODWAR22 MODWAR7
    python contrib/mat_image_templates.py [min_count]
    confirm_plan contrib/mat_image_templates/<n>.plan.txt --game BLACKOP7     (one plan per opening)
"""
from pathlib import Path
import collections
import glob
import sys

ROOT = Path(__file__).resolve().parent
while not (ROOT / "scripts" / "snapshot.py").is_file() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
if not (ROOT / "scripts" / "snapshot.py").is_file():
    raise SystemExit("Run this helper from within a hash-slinging-slasher checkout")
# Prepare these verified, game-and-pool-specific inputs with scripts/export_named.py.
if not (ROOT / "state" / "an").is_dir():
    raise SystemExit("Run python scripts/export_named.py first (see --help)")
AN = ROOT / "state" / "an"
OUTNAME = "img_sibling_templates" if "--image-bases" in sys.argv else "mat_image_templates"
OUT = ROOT / "contrib" / OUTNAME
MIN = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 3
# --image-bases: also take every base a named image shows under a measured (opening, ending) pair,
# so an image whose material is unnamed still lends its base to its siblings' templates.
IMAGE_BASES = "--image-bases" in sys.argv


def lines(pattern):
    out = set()
    for f in glob.glob(str(AN / pattern)):
        for line in open(f, encoding="utf-8", errors="replace"):
            line = line.strip().lower()
            if line:
                out.add(line)
    return out


def bases_of(material):
    bare = material.rsplit("/", 1)[-1]
    if bare.startswith("*") or len(bare) < 4:
        return []
    found = [bare]
    if bare.startswith("mtl_") and len(bare) > 8:
        found.append(bare[4:])
    return found


def main():
    materials = lines("*_material.named")
    images = lines("*_image.named")
    bases = set()
    for m in materials:
        bases.update(bases_of(m))
    print(len(materials), "materials ->", len(bases), "bases;", len(images), "images", file=sys.stderr)

    # For each image, every (opening, base, ending) split where the middle is a known base.
    pairs = collections.Counter()
    for img in images:
        parts = img.split("_")
        n = len(parts)
        for i in range(0, min(n, 4)):          # opening: up to 3 leading tokens
            opening = "_".join(parts[:i]) + ("_" if i else "")
            for j in range(n, i, -1):           # base = parts[i:j], ending = parts[j:]
                if n - j > 4:
                    break
                base = "_".join(parts[i:j])
                if base in bases:
                    ending = ("_" + "_".join(parts[j:])) if j < n else ""
                    pairs[(opening, ending)] += 1
    keep = {p: c for p, c in pairs.items() if c >= MIN and (p[0] or p[1])}
    print(len(pairs), "pairs seen,", len(keep), "kept at >=", MIN, file=sys.stderr)

    if IMAGE_BASES:
        before = len(bases)
        openings = {o for o, _ in keep}
        endings = {e for _, e in keep}
        for img in images:
            for o in openings:
                if o and not img.startswith(o):
                    continue
                rest = img[len(o):]
                parts = rest.split("_")
                for j in range(len(parts) - 1, max(len(parts) - 5, 0), -1):
                    e = "_" + "_".join(parts[j:])
                    if (o, e) in keep and j >= 2:
                        bases.add("_".join(parts[:j]))
        print(len(bases) - before, "bases added from images", file=sys.stderr)

    by_opening = collections.defaultdict(list)
    for (opening, ending), c in sorted(keep.items(), key=lambda kv: -kv[1]):
        by_opening[opening].append((ending, c))

    OUT.mkdir(parents=True, exist_ok=True)
    # Only replace named generated files; never delete unrelated user files.
    (OUT / "bases.txt").write_text("\n".join(sorted(bases)) + "\n", encoding="utf-8")
    total = 0
    for k, (opening, ends) in enumerate(sorted(by_opening.items(), key=lambda kv: -sum(c for _, c in kv[1]))):
        endings = [e for e, _ in ends]
        (OUT / f"{k:03d}.ends.txt").write_text("\n".join(endings) + "\n", encoding="utf-8")
        plan = [
            f"label: material->image template, opening {opening or '(none)'}",
            "describe: named material bases x the endings measured to follow them after this opening; contrib/mat_image_templates.py",
            f"begin: {opening}" if opening else "bare: yes",
            f"stem: @contrib/{OUTNAME}/bases.txt",
        ]
        if opening:
            plan.append("bare: no")
        plan.append(f"end: @contrib/{OUTNAME}/{k:03d}.ends.txt")
        (OUT / f"{k:03d}.plan.txt").write_text("\n".join(plan) + "\n", encoding="utf-8")
        total += len(endings)
        print(f"{k:03d} opening={opening or '-':16} endings={len(endings):5d} support={sum(c for _, c in ends)}", file=sys.stderr)
    print("cost ~", total * len(bases) / 1e9, "B candidates", file=sys.stderr)


if __name__ == "__main__":
    main()
