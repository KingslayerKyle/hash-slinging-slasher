"""BO4 sound files: give every sibling directory the files its siblings are known to have.

Generalises contrib/bo4_vox_slot_transfer.py (which paid 28 on vox speaker slots, 2026-09-17) to
every BO4 sound path. Under one parent, sibling directories are usually parallel sets -- one per
weapon, character, surface, map -- holding the same file stems. So for each parent:

  - a child's stem is normalised by replacing its own directory token (when the stem contains it)
    with a placeholder, e.g.  fly\\hub\\adler\\fly_adler_step_02  ->  fly_{}_step_02
  - every normalised stem seen under any child is emitted under every other child, with the
    placeholder filled back in
  - suffixes are the ones seen under that parent; numbered takes widened to max+2

Parents whose cross is larger than --cap candidates are skipped (and counted on stderr), which keeps
it to the families that are actually parallel rather than a directory of everything.

    python contrib/bo4_sound_dir_complement.py | bin/windows/confirm_list.exe - --game BLKOPS04 --no-fold
    python contrib/bo4_sound_dir_complement.py --game BLKOPSCW | bin/windows/confirm_list.exe - --game BLKOPSCW
"""
import collections
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BS = "\\"
TAKE = re.compile(r"^(.*?)_(\d{1,3})$")


GAME = sys.argv[sys.argv.index("--game") + 1].upper() if "--game" in sys.argv else "BLKOPS04"


def known():
    names = set()
    paths = [os.path.join(ROOT, "all_names", GAME.lower(), "sound_asset.txt")]
    paths += glob.glob(os.path.join(ROOT, "cod-name-db", "csv", "fnv1a_*xsounds.csv"))
    paths += glob.glob(os.path.join(ROOT, "submissions", "*%s*" % GAME, "sound_asset*.txt"))
    paths += glob.glob(os.path.join(ROOT, "findings", GAME.lower(), "sound_asset.txt"))
    for path in paths:
        with open(path, encoding="utf-8-sig", errors="replace") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                name = line.split(",", 1)[1] if "," in line else line
                names.add(name.strip().lower().replace("/", BS))
    return names


def main():
    cap = 2_000_000
    if "--cap" in sys.argv:
        cap = int(sys.argv[sys.argv.index("--cap") + 1])
    # parent -> child -> set(normalised stem) ; parent -> suffixes ; (parent, stem) -> top take
    fam = collections.defaultdict(lambda: collections.defaultdict(set))
    sfx = collections.defaultdict(set)
    top = collections.defaultdict(lambda: -1)
    rows = []
    for name in known():
        parts = name.split(BS)
        if len(parts) < 3:
            continue
        parent, child, base = BS.join(parts[:-2]), parts[-2], parts[-1]
        dot = base.find(".")
        if dot <= 0:
            continue
        rows.append((parent, child, base[:dot], base[dot:]))
    # --abbrev: a child's slot token is the stem token in >= 80% of its stems and in <= 20% of its
    # siblings' -- orangeox_oran_..., so families that abbreviate the directory still line up
    token = {}
    if "--abbrev" in sys.argv:
        per = collections.defaultdict(lambda: collections.defaultdict(collections.Counter))
        cnt = collections.defaultdict(collections.Counter)
        for parent, child, stem, _ in rows:
            cnt[parent][child] += 1
            for t in set(stem.split("_")):
                if len(t) >= 2 and not t.isdigit():
                    per[parent][child][t] += 1
        for parent, kids in per.items():
            if len(kids) < 2:
                continue
            for child, toks in kids.items():
                n = cnt[parent][child]
                for t, c in toks.most_common(8):
                    if c < 0.8 * n:
                        break
                    others = sum(k[t] for o, k in kids.items() if o != child)
                    rest = sum(cnt[parent].values()) - n
                    if rest and others <= 0.2 * rest and t != child:
                        token[(parent, child)] = t
                        break
    for parent, child, stem, suffix in rows:
        sfx[parent].add(suffix)
        t = token.get((parent, child))
        if t:
            norm = "_".join("{}" if x == t else x for x in stem.split("_"))
        else:
            norm = stem.replace(child, "{}") if len(child) >= 3 else stem
        m = TAKE.match(norm)
        if m:
            key, n, width = m.group(1), int(m.group(2)), len(m.group(2))
            norm = "%s_#%d" % (key, width)
            top[(parent, norm)] = max(top[(parent, norm)], n)
        fam[parent][child].add(norm)

    # --extra-slots FILE: folders known to exist (e.g. scripts/contributed/bo4_sound_folders_*.txt)
    # that hold no named file yet. Each becomes an empty child of its parent and is given the
    # parent's files; ONLY those children are emitted, so this never repeats the plain run.
    only = None
    if "--extra-slots" in sys.argv:
        only = set()
        with open(sys.argv[sys.argv.index("--extra-slots") + 1], encoding="utf-8-sig") as handle:
            for line in handle:
                d = line.strip().lower().replace("/", BS).rstrip(BS)
                if BS not in d:
                    continue
                parent, child = d.rsplit(BS, 1)
                if parent in fam and child not in fam[parent]:
                    fam[parent][child] = set()
                    only.add((parent, child))
    total = skipped = used = 0
    out = sys.stdout
    for parent, children in fam.items():
        if len(children) < 2:
            continue
        union = set().union(*children.values())
        if only is not None:
            children = {c: v for c, v in children.items() if (parent, c) in only}
            if not children:
                continue
        takes = 0
        for norm in union:
            takes += (top[(parent, norm)] + 3) if "#" in norm else 1
        size = len(children) * takes * len(sfx[parent])
        if size > cap:
            skipped += 1
            print("over cap: %s children=%d size=%d" % (parent, len(children), size), file=sys.stderr)
            continue
        used += 1
        for child in children:
            for norm in union:
                if "#" in norm:
                    key, width = norm.rsplit("_#", 1)
                    width = int(width)
                    stems = ["%s_%0*d" % (key, width, i) for i in range(top[(parent, norm)] + 3)]
                else:
                    stems = [norm]
                for stem in stems:
                    stem = stem.replace("{}", token.get((parent, child), child))
                    for s in sfx[parent]:
                        out.write("%s\\%s\\%s%s\n" % (parent, child, stem, s))
                        total += 1
    print("dir complement: %d parents used, %d over cap, %d candidates" % (used, skipped, total),
          file=sys.stderr)


if __name__ == "__main__":
    main()
