"""`li_` foliage/proxy image family: li_<model or material base>[_middle]_<channel>.

Found by the model-name head swap (contrib/model_log_stems.py): 330 BO7 images in one pass, most
of them `li_<model name>_{albedo,normal,depth,geo,translucence}`. Of the 5,740 `li_` images known
when this was written, 2,557 start with a model name from the BO7 model list.

Stems: every model-name prefix (contrib/modellog_stems.txt), also behind `mtl_` and `i_mtl_`,
every known material base (contrib/mat_bases.txt), also behind `i_`, and every known `li_` base. Endings: every middle seen between a base and
its channel (`_proxy`, `_reactive`, `_medium_01`, `_cp_raid_proxy`, ...) crossed with every
channel seen, plus the bare channels.

    python contrib/li_family.py
    confirm_plan contrib/li_family.plan.txt --game BLACKOP7
"""
from pathlib import Path
import collections
import glob

ROOT = Path(__file__).resolve().parent
while not (ROOT / "scripts" / "snapshot.py").is_file() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
CONTRIB = ROOT / "contrib"


def known_li():
    li = set()
    for pattern in ("all_names/*/image.txt", "findings/*/*/image*.txt", "submissions/*/image*.txt"):
        for f in glob.glob(str(ROOT / pattern)):
            for line in open(f, encoding="utf-8", errors="replace"):
                name = line.strip().partition(",")[2].lower()
                if name.startswith("li_"):
                    li.add(name[3:])
    return li


def main():
    li = known_li()
    channels = collections.Counter(n.rsplit("_", 1)[1] for n in li if "_" in n)
    channels = [c for c, k in channels.most_common() if k >= 20 and not c.isdigit()]

    # `li_i_mtl_<model>_proxy_geo`: the proxy is named after the material's image, so each model
    # prefix also goes in as `mtl_<model>` and `i_mtl_<model>`, and each material base as `i_<base>`.
    model_stems = set((CONTRIB / "modellog_stems.txt").read_text(encoding="utf-8").split())
    stems = set(model_stems)
    stems |= {"mtl_" + s for s in model_stems} | {"i_mtl_" + s for s in model_stems}
    mat_bases = CONTRIB / "mat_bases.txt"
    if mat_bases.is_file():
        bases = set(mat_bases.read_text(encoding="utf-8").split())
        stems |= bases | {"i_" + b for b in bases}

    middles = collections.Counter()
    for name in li:
        parts = name.split("_")
        if parts[-1] not in channels:
            continue
        # every split point: base = parts[:k], middle = parts[k:-1]
        for k in range(2, len(parts)):
            stems.add("_".join(parts[:k]))
            middle = parts[k:-1]
            if len(middle) <= 4:
                middles["_" + "_".join(middle) if middle else ""] += 1

    middle_list = [m for m, k in middles.most_common() if k >= 2]
    ends = sorted({m + "_" + c for m in middle_list for c in channels})
    (CONTRIB / "li_stems.txt").write_text("\n".join(sorted(s for s in stems if s)) + "\n", encoding="utf-8")
    (CONTRIB / "li_ends.txt").write_text("\n".join(ends) + "\n", encoding="utf-8")
    (CONTRIB / "li_family.plan.txt").write_text(
        "label: li_ image family -- li_ x model/material bases x measured middles and channels\n"
        "describe: li_<base>[_middle]_<channel>; bases from BO7 model names, material bases and known li_ names, "
        "middles and channels measured on known li_ images; see contrib/li_family.py\n"
        "begin: li_\n"
        "bare: no\n"
        "stem: @contrib/li_stems.txt\n"
        "end: @contrib/li_ends.txt\n", encoding="utf-8")
    print(f"{len(li)} known li_, channels {channels}, {len(stems)} stems, "
          f"{len(middle_list)} middles, {len(ends)} endings")


if __name__ == "__main__":
    main()
