"""Model-name seeds from an asset-name list (BO7's 35,998 model names, as a `Model,<name>` log).

Modern models carry their names, so they are never searched here -- but they are real names from
the same art pipeline, and the materials and images built for a model start with the model's own
name: `tm/<model>_dark`, `m/<model>_glass`, `<model>_m0_v2`, `<model>_thermalmap`. Measured on the
names already known before this was written: 2,160 named BO6/BO7 materials and 541 images begin
with one of these model names. A direct list pass (model name + material directory) returned 218
new BO7 materials and 81 BO6.

Writes every underscore-prefix of every model name (2+ segments) as plan stems, the directories
known modern materials and images carry as beginnings, and two plans that cross them with the
segment plans' measured endings (contrib/type_segments.py writes those):

    python contrib/model_log_stems.py "..\\assets.log"
    confirm_plan contrib/modellog_material.plan.txt --game BLACKOP7
    confirm_plan contrib/modellog_image.plan.txt --game BLACKOP7

Lines like `Model,#tm7/base::name` (a hashed scope in front of the name) contribute the part
after `::`, and `tm/name`, `~tm/name`, `lm8_8_tml/name` the base after the directory.
"""
from pathlib import Path
import collections
import re
import sys

ROOT = Path(__file__).resolve().parent
while not (ROOT / "scripts" / "snapshot.py").is_file() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
CONTRIB = ROOT / "contrib"
MODERN = ("blackop6", "blackop7", "modwar7", "modwar22", "yamyamok")


def model_names(path):
    names = set()
    for line in open(path, encoding="utf-8", errors="replace"):
        kind, sep, name = line.strip().partition(",")
        if not sep:
            continue
        name = name.strip().lower()
        if "::" in name:
            name = name.rsplit("::", 1)[1]
        name = re.sub(r"^\(\w+\)", "", name)
        # `tm/`, `~tm/`, `#tm7/`, `lm8_8_tml/`, `android:` -- the stem is the base after them
        name = re.split(r"[/:]", name)[-1]
        if re.fullmatch(r"[a-z0-9_]+", name or ""):
            names.add(name)
    return names


def known(kind):
    for top in ("all_names", "submissions", "findings"):
        for game in MODERN:
            for f in sorted((ROOT / top).rglob(kind + "*.txt")):
                if game not in str(f).lower():
                    continue
                for line in f.open(encoding="utf-8", errors="replace"):
                    key, sep, name = line.rstrip("\r\n").partition(",")
                    if sep:
                        yield name.lower()


def directories(kind, minimum):
    count = collections.Counter()
    for name in known(kind):
        head, sep, tail = name.rpartition("/")
        if sep and tail and not name.startswith("*"):
            count[head + "/"] += 1
    return [d for d, n in count.most_common() if n >= minimum]


def main():
    log = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT.parent / "assets.log"
    names = model_names(log)

    stems = set()
    for name in names:
        parts = name.split("_")
        for k in range(2, len(parts) + 1):
            stem = "_".join(parts[:k])
            if len(stem) >= 4:
                stems.add(stem)

    (CONTRIB / "modellog_names.txt").write_text("\n".join(sorted(names)) + "\n", encoding="utf-8")
    (CONTRIB / "modellog_stems.txt").write_text("\n".join(sorted(stems)) + "\n", encoding="utf-8")

    mat_dirs = directories("material", 5)
    img_dirs = directories("image", 5)
    (CONTRIB / "modellog_mat_dirs.txt").write_text("\n".join(mat_dirs) + "\n", encoding="utf-8")

    plans = {
        "modellog_material.plan.txt": (
            "label: model-name stems as materials -- known material dirs x model prefixes x material endings\n"
            "describe: every 2+ segment underscore-prefix of BO7's model names (contrib/model_log_stems.py), "
            "behind each directory known modern materials use, crossed with the material segment plan's endings\n"
            "begin: @contrib/modellog_mat_dirs.txt\n"
            "bare: no\n"
            "stem: @contrib/modellog_stems.txt\n"
            "end: @contrib/seg_material_ends.txt\n"),
        "modellog_image.plan.txt": (
            "label: model-name stems as images -- model prefixes x image endings\n"
            "describe: every 2+ segment underscore-prefix of BO7's model names (contrib/model_log_stems.py), "
            "crossed with the image segment plan's endings (`_m0_v2`, `_thermalmap`, ...)\n"
            + "".join(f"begin: {d}\n" for d in img_dirs) +
            "bare: yes\n"
            "stem: @contrib/modellog_stems.txt\n"
            "end: @contrib/seg_image_ends.txt\n"),
    }
    # Prop animations carry the model's name too: `<model>_fxsim`, `<model>_open`, `<model>_close`.
    plans["modellog_xanim.plan.txt"] = (
        "label: model-name stems as animations -- model prefixes x animation endings\n"
        "describe: every 2+ segment underscore-prefix of BO7's model names (contrib/model_log_stems.py), "
        "crossed with the animation segment plan's endings (`_fxsim`, `_open`, `_idle`, ...)\n"
        "bare: yes\n"
        "stem: @contrib/modellog_stems.txt\n"
        "end: @contrib/seg_xanim_ends.txt\n")

    # Wrappers: longer heads in front of a whole model name -- `m/mtl_<model>`, `tm/li_<model>`,
    # `li_i_mtl_<model>`, `cm_<model>`, `ui_icon_thumb_<model>`. Measured on known modern names:
    # whatever precedes a 3+ segment model prefix, kept when it occurs 3+ times.
    for kind in ("material", "image"):
        heads = collections.Counter()
        for name in set(known(kind)):
            parts = name.split("_")
            done = False
            for i in range(0, min(len(parts) - 1, 4)):
                for j in range(len(parts), i + 2, -1):
                    if "_".join(parts[i:j]) in stems:
                        heads["_".join(parts[:i]) + "_" if i else ""] += 1
                        done = True
                        break
                if done:
                    break
        wrap = [h for h, n in heads.most_common() if h and n >= 3]
        (CONTRIB / f"modellog_{kind}_wraps.txt").write_text("\n".join(wrap) + "\n", encoding="utf-8")
        plans[f"modellog_wrap_{kind}.plan.txt"] = (
            f"label: model-name stems inside measured {kind} wrappers (m/mtl_, tm/li_, li_i_mtl_, cm_, ...)\n"
            f"describe: every 2+ segment prefix of BO7's model names behind each head known modern {kind} names "
            f"put in front of a model name 3+ times (contrib/model_log_stems.py), then the {kind} segment endings\n"
            f"begin: @contrib/modellog_{kind}_wraps.txt\n"
            "bare: no\n"
            "stem: @contrib/modellog_stems.txt\n"
            f"end: @contrib/seg_{kind}_ends.txt\n")

    # Head swap: the same object under another game's code or directory (`sat_zm_x` the model,
    # `tm/t10_zm_x` the material). Every stem minus its first 1-2 segments, behind the measured
    # beginnings the material/image head-swap plans use, then the top endings of that type.
    rests = set()
    for stem in stems:
        parts = stem.split("_")
        for k in (1, 2):
            if len(parts) > k:
                rests.add("_" + "_".join(parts[k:]))
    (CONTRIB / "modellog_rests.txt").write_text("\n".join(sorted(rests)) + "\n", encoding="utf-8")
    for kind in ("material", "image"):
        ends = (CONTRIB / f"seg_{kind}_ends.txt").read_text(encoding="utf-8").split()[:300]
        (CONTRIB / f"modellog_{kind}_ends300.txt").write_text("\n".join(ends) + "\n", encoding="utf-8")
        plans[f"modellog_head_{kind}.plan.txt"] = (
            f"label: model-name remainders under measured {kind} beginnings (head swap)\n"
            f"describe: each BO7 model-name prefix minus its first 1-2 segments (contrib/model_log_stems.py), "
            f"behind the top 3000 {kind} beginnings (contrib/head_{kind}_begins.txt), then the top 300 {kind} endings\n"
            f"begin: @contrib/head_{kind}_begins.txt\n"
            "bare: no\n"
            "stem: @contrib/modellog_rests.txt\n"
            f"end: @contrib/modellog_{kind}_ends300.txt\n")

    # Insertion: the whole model prefix behind a measured beginning -- `tm/mtl_jup` + `_us_bathroom_
    # product_set`, `tm/head` + `_c_sat_npc_...`. The head swap above only tries cut-down remainders.
    (CONTRIB / "modellog_whole.txt").write_text(
        "\n".join(sorted("_" + s for s in stems)) + "\n", encoding="utf-8")
    for kind in ("material", "image"):
        plans[f"modellog_insert_{kind}.plan.txt"] = (
            f"label: whole model-name prefixes under measured {kind} beginnings (code insertion)\n"
            f"describe: each 2+ segment prefix of BO7's model names, whole, behind the top 3000 {kind} beginnings "
            f"(contrib/head_{kind}_begins.txt), then the top 300 {kind} endings; see contrib/model_log_stems.py\n"
            f"begin: @contrib/head_{kind}_begins.txt\n"
            "bare: no\n"
            "stem: @contrib/modellog_whole.txt\n"
            f"end: @contrib/modellog_{kind}_ends300.txt\n")

    for file, text in plans.items():
        (CONTRIB / file).write_text(text, encoding="utf-8")

    print(f"{len(names)} model names, {len(stems)} stems, "
          f"{len(mat_dirs)} material dirs, {len(img_dirs)} image dirs")


if __name__ == "__main__":
    main()
