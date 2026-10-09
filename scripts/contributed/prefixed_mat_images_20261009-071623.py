"""Images named <prefix> + <material base> + <channel>: `li_un_foliage_tree_cypress_medium_01_new_translucence`
for material `tmr/un_foliage_tree_cypress_medium_01_new...`.

mat_to_image crossed every material base with the image endings, bare. Images often carry a
prefix the material does not (measured 2026-10-09 on the modern tables + BO6/BO7 finds: images
that are <prefix><known material base>... -- vm_ 999, li_ 460, tex_jup_ 172, c_ 93, parts_ 63,
mgl_ 53, wzm_ 48 ...). This measures those prefixes and crosses the top --prefixes with every
material base and the top --ends image segment endings.

    python contrib/type_segments.py --kind image && python contrib/prefixed_mat_images.py
    confirm_plan contrib/prefixed_mat_images.plan.txt --game BLACKOP7
"""
from pathlib import Path
import argparse
import collections
import sys

ROOT = Path(__file__).resolve().parent
while not (ROOT / "scripts" / "snapshot.py").is_file() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
CONTRIB = ROOT / "contrib"
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prefixes", type=int, default=60)
    ap.add_argument("--ends", type=int, default=3000)
    a = ap.parse_args()
    mats = {n.split("/", 1)[-1] for n in names("material", "fnv1a_xmaterials_v2") if n and "*" not in n}
    pre = collections.Counter()
    for im in set(names("image", "fnv1a_ximages_v2")):
        t = im.split("_")
        for k in (1, 2):
            rest = t[k:]
            if any("_".join(rest[:j]) in mats for j in range(len(rest), 1, -1)):
                pre["_".join(t[:k]) + "_"] += 1
                break
    pl = [p for p, _ in pre.most_common(a.prefixes) if "&" not in p and "*" not in p]
    ends = (CONTRIB / "seg_image_ends.txt").read_text(encoding="utf-8").splitlines()[:a.ends]
    (CONTRIB / "pmi_prefixes.txt").write_text("".join(p + NL for p in pl), encoding="utf-8")
    (CONTRIB / "pmi_bases.txt").write_text("".join(m + NL for m in sorted(mats)), encoding="utf-8")
    (CONTRIB / "pmi_ends.txt").write_text("".join(e + NL for e in ends), encoding="utf-8")
    (CONTRIB / "prefixed_mat_images.plan.txt").write_text(NL.join([
        "label: prefixed material bases as images -- measured image prefixes x material bases x image endings",
        f"describe: top {len(pl)} prefixes images put before a known material base, x {len(mats)} material "
        f"bases, x top {len(ends)} image endings; see contrib/prefixed_mat_images.py",
        "begin: @contrib/pmi_prefixes.txt", "stem: @contrib/pmi_bases.txt", "end: @contrib/pmi_ends.txt", ""]),
        encoding="utf-8")
    print(f"{len(pl)} prefixes, {len(mats)} bases, {len(ends)} ends", file=sys.stderr)


if __name__ == "__main__":
    main()
