"""BO4 sound files: move every known vox line onto every speaker that shares its directory.

BO4 vox files are laid out  <parent>\\<speaker>\\vox_<speaker>_<line><take>.<suffix>  --
en\\vox\\scripted\\mpl\\cras\\vox_cras_..., en\\vox\\scripted\\wz\\plr_4\\vox_plr_4_callout_greet_00...
A speaker directory is a slot, and the lines recorded for one slot are very largely recorded for
its siblings (same script, different actor). So from every name known to be real:

  - speakers  = every <speaker> seen under a <parent> (plr_<n> also extended to plr_0..plr_15)
  - lines     = every <line> seen under that <parent>, for any speaker
  - takes     = the trailing _NN, extended 00 .. max+3 per line
  - suffixes  = the .sn100.pc.snd style endings seen under that parent

and prints parent x speaker x line x take x suffix. Seeded from the tables, all_names and any
submissions (including _inflight_ open-PR seeds), so it refills whenever a vox slot gains names.

    python contrib/bo4_vox_slot_transfer.py | bin/windows/confirm_list.exe --game BLKOPS04 --no-fold
"""
import collections
import csv
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def known():
    names = set()
    paths = [os.path.join(ROOT, "all_names", "blkops04", "sound_asset.txt")]
    paths += glob.glob(os.path.join(ROOT, "cod-name-db", "csv", "fnv1a_*xsounds.csv"))
    paths += glob.glob(os.path.join(ROOT, "submissions", "*BLKOPS04*", "sound_asset*.txt"))
    paths += glob.glob(os.path.join(ROOT, "findings", "blkops04", "sound_asset.txt"))
    for path in paths:
        with open(path, encoding="utf-8-sig", errors="replace") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                name = line.split(",", 1)[1] if "," in line else line
                names.add(name.strip().lower().replace("/", "\\"))
    return names


TAKE = re.compile(r"^(.*?)(?:_(\d{1,3}))?$")


def main():
    parents = collections.defaultdict(lambda: {"spk": set(), "lines": collections.defaultdict(int),
                                               "sfx": set(), "width": collections.Counter()})
    for name in known():
        if "\\vox\\" not in name:
            continue
        parts = name.split("\\")
        if len(parts) < 3:
            continue
        spk, base = parts[-2], parts[-1]
        dot = base.find(".")
        if dot < 0:
            continue
        stem, sfx = base[:dot], base[dot:]
        head = "vox_" + spk + "_"
        if not stem.startswith(head):
            continue
        rest = stem[len(head):]
        m = TAKE.match(rest)
        line, take = m.group(1), m.group(2)
        p = parents["\\".join(parts[:-2])]
        p["spk"].add(spk)
        p["sfx"].add(sfx)
        n = int(take) if take is not None else -1
        if take is not None:
            p["width"][len(take)] += 1
        p["lines"][line] = max(p["lines"][line], n)

    if "--wide" in sys.argv:
        # pool speakers (not lines) across every parent that shares a grandparent
        groups = collections.defaultdict(list)
        for parent in parents:
            groups[parent.rsplit("\\", 1)[0]].append(parent)
        pooled = {}
        for members in groups.values():
            spk, lines = set(), collections.defaultdict(int)
            for m in members:
                spk |= parents[m]["spk"]
                for line, top in parents[m]["lines"].items():
                    lines[line] = max(lines[line], top)
            for m in members:
                pooled[m] = (spk, lines)
        for m, (spk, lines) in pooled.items():
            parents[m]["spk"] = set(spk)
            pass  # lines stay per parent: pooling both is ~9M cells x takes
    out = sys.stdout
    total = 0
    for parent, p in parents.items():
        speakers = set(p["spk"])
        if any(re.fullmatch(r"plr_\d+", s) for s in speakers):
            speakers |= {"plr_%d" % i for i in range(16)}
        width = p["width"].most_common(1)[0][0] if p["width"] else 2
        for spk in speakers:
            for line, top in p["lines"].items():
                takes = [""] if top < 0 else ["_%0*d" % (width, i) for i in range(top + 4)]
                for take in takes:
                    for sfx in p["sfx"]:
                        out.write("%s\\%s\\vox_%s_%s%s%s\n" % (parent, spk, spk, line, take, sfx))
                        total += 1
    print("vox slot transfer: %d parents, %d candidates" % (len(parents), total), file=sys.stderr)


if __name__ == "__main__":
    main()
