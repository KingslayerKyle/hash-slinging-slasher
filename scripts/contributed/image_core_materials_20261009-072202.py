"""Materials from image cores with the image's prefix *and* channel stripped.

The reverse of contrib/prefixed_mat_images.py: `li_un_foliage_tree_cypress_medium_01_new_translucence`
-> core `un_foliage_tree_cypress_medium_01_new` -> `tmr/<core>_reactive`, `m/<core>`, ...
material_dir_swap.py stripped only the last segment, so a prefixed image never gave its material.

Cores: every known modern image, minus a measured prefix (pmi_prefixes.txt, or none) and minus
its last 1-2 segments. Directories and endings are measured on known modern materials (`<dir>/`
and the 0-2 segment tails after a known base).

    python contrib/prefixed_mat_images.py && python contrib/image_core_materials.py
    confirm_plan contrib/image_core_materials.plan.txt --game BLACKOP7
"""
from pathlib import Path
import collections
import sys

ROOT = Path(__file__).resolve().parent
while not (ROOT / "scripts" / "snapshot.py").is_file() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
CONTRIB = ROOT / "contrib"
CONTRIB.mkdir(parents=True, exist_ok=True)
MODERN = ("blackop6", "blackop7", "yamyamok", "modwar22", "modwar7")
NL = chr(10)


def names(kind, table):
    for line in (ROOT / "cod-name-db" / "csv" / (table + ".csv")).open(encoding="utf-8", errors="replace"):
        yield line.rstrip(chr(13) + NL).partition(",")[2].lower()
    for top in ("all_names", "findings"):
        for g in MODERN:
            for p in (ROOT / top / g).rglob(kind + "*.txt"):
                for line in p.open(encoding="utf-8", errors="replace"):
                    yield line.rstrip(chr(13) + NL).partition(",")[2].lower()


prefixes = (CONTRIB / "pmi_prefixes.txt").read_text(encoding="utf-8").split()
mats = {n for n in names("material", "fnv1a_xmaterials_v2") if n and "*" not in n and "/" in n}
dirs = collections.Counter(n.split("/", 1)[0] + "/" for n in mats)
bases = {n.split("/", 1)[1] for n in mats}
cores = set()
for im in set(names("image", "fnv1a_ximages_v2")):
    if "&" in im or "~" in im or "*" in im:
        continue
    for p in [""] + prefixes:
        if p and not im.startswith(p):
            continue
        t = im[len(p):].split("_")
        for k in (1, 2):
            if len(t) > k + 1:
                cores.add("_".join(t[:-k]))
cores -= bases
tails = collections.Counter()
sb = sorted(bases)
for b in bases:
    t = b.split("_")
    for k in (1, 2):
        if len(t) > k + 1 and "_".join(t[:-k]) in bases:
            tails["_" + "_".join(t[-k:])] += 1
dl = [d for d, c in dirs.most_common() if c >= 20]
tl = [t for t, _ in tails.most_common(400)]
(CONTRIB / "icm_dirs.txt").write_text("".join(d + NL for d in dl), encoding="utf-8")
(CONTRIB / "icm_cores.txt").write_text("".join(c + NL for c in sorted(cores)), encoding="utf-8")
(CONTRIB / "icm_ends.txt").write_text("".join(t + NL for t in tl), encoding="utf-8")
(CONTRIB / "image_core_materials.plan.txt").write_text(NL.join([
    "label: materials from image cores, image prefix and channel both stripped",
    f"describe: {len(dl)} material dirs x {len(cores)} image cores (measured prefix and last 1-2 segments "
    f"removed) x bare and the top {len(tl)} material tails; see contrib/image_core_materials.py",
    "begin: @contrib/icm_dirs.txt", "stem: @contrib/icm_cores.txt", "end: @contrib/icm_ends.txt", ""]),
    encoding="utf-8")
print(f"{len(dl)} dirs, {len(cores)} cores, {len(tl)} ends", file=sys.stderr)
