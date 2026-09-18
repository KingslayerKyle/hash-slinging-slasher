"""Sound files: parallel subtrees at ANY directory depth, not only the last one.

contrib/bo4_sound_dir_complement.py treats the file's own directory as the slot. Real parallel
families also sit higher up -- zmb\\level\\<map>\\amb\\..., wpn\\<weapon>\\fire\\..., en\\vox\\scripted\\<mode>\\...
-- where the whole subtree below the slot repeats. So for every name and every directory level k:

    prefix = components before k, slot = component k, rest = everything after k
    (the slot's own text, if it also appears in rest, is replaced by a placeholder)

and within each (prefix, k) every slot value is given every rest any *overlapping* slot value has.
Two slots overlap when they share at least --min-shared rests; a slot that shares nothing with its
siblings is not part of a parallel family and gets nothing, which is what keeps the cross from
becoming "every directory x every file". Numbered takes are widened to max+2.

    python contrib/sound_slot_complement.py --game BLKOPS04 | bin/windows/confirm_list.exe - --game BLKOPS04 --no-fold
    python contrib/sound_slot_complement.py --game BLKOPSCW | bin/windows/confirm_list.exe - --game BLKOPSCW
"""
import collections
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BS = "\\"
TAKE = re.compile(r"^(.*?)_(\d{1,3})(\.[^\\]*)$")


def arg(flag, default):
    return type(default)(sys.argv[sys.argv.index(flag) + 1]) if flag in sys.argv else default


GAME = arg("--game", "BLKOPS04").upper()
CAP = arg("--cap", 3_000_000)
MIN_SHARED = arg("--min-shared", 2)


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
                if line:
                    name = line.split(",", 1)[1] if "," in line else line
                    names.add(name.strip().lower().replace("/", BS))
    return names


def map_vocab():
    """--inject: map codenames seen anywhere in this game's names (mp_/zm_/wz_/cp_<x>, 3+ times),
    both bare (frenetic) and full (mp_frenetic), for slot families whose values are maps."""
    count = collections.Counter()
    rx = re.compile(r"(?:^|[^a-z0-9])((?:mp|zm|wz|cp)_([a-z0-9]+))")
    for path in glob.glob(os.path.join(ROOT, "all_names", GAME.lower(), "*.txt")):
        with open(path, encoding="utf-8-sig", errors="replace") as handle:
            for line in handle:
                for full, bare in rx.findall(line.lower()):
                    count[full] += 1
    full = {k for k, c in count.items() if c >= 3}
    return full | {k.split("_", 1)[1] for k in full if len(k.split("_", 1)[1]) >= 3}


def main():
    inject = map_vocab() if "--inject" in sys.argv else set()
    # (prefix, depth) -> slot -> set(rest template);  template -> top take
    fam = collections.defaultdict(lambda: collections.defaultdict(set))
    top = collections.defaultdict(lambda: -1)
    for name in known():
        parts = name.split(BS)
        m = TAKE.match(parts[-1])
        if m:
            parts[-1] = "%s_#%d%s" % (m.group(1), len(m.group(2)), m.group(3))
        for k in range(1, len(parts) - 1):
            slot = parts[k]
            rest = BS.join(parts[k + 1:])
            if len(slot) >= 3:
                rest = rest.replace(slot, "{}")
            prefix = BS.join(parts[:k])
            fam[(prefix, k)][slot].add(rest)
            if m:
                top[rest] = max(top[rest], int(m.group(2)))

    total = used = skipped = 0
    out = sys.stdout
    for (prefix, k), slots in fam.items():
        if len(slots) < 2:
            continue
        # rest -> slots holding it; a slot joins the family when it shares MIN_SHARED rests
        holders = collections.defaultdict(set)
        for slot, rests in slots.items():
            for r in rests:
                holders[r].add(slot)
        shared = collections.Counter()
        for r, hs in holders.items():
            if len(hs) > 1:
                for s in hs:
                    shared[s] += 1
        members = [s for s in slots if shared[s] >= MIN_SHARED]
        if len(members) < 2:
            continue
        union = set().union(*(slots[s] for s in members))
        if inject:
            # only families whose slot values are mostly map names get the unseen maps -- and then
            # ONLY the unseen maps, so the injected run does not repeat the plain one
            if sum(s in inject for s in members) * 2 < len(members):
                continue
            members = sorted(inject - set(slots))
            slots = dict(slots)
            for s in members:
                slots[s] = set()
        width = sum((top[r] + 3) if "#" in r else 1 for r in union)
        size = len(members) * width
        if size > CAP:
            skipped += 1
            continue
        used += 1
        for slot in members:
            have = slots[slot]
            for r in union:
                if r in have and "#" not in r:
                    continue
                if "#" in r:
                    mm = re.search(r"_#(\d)", r)
                    w = int(mm.group(1))
                    rs = [r.replace(mm.group(0), "_%0*d" % (w, i)) for i in range(top[r] + 3)]
                else:
                    rs = [r]
                for x in rs:
                    out.write("%s\\%s\\%s\n" % (prefix, slot, x.replace("{}", slot)))
                    total += 1
    print("slot complement %s: %d families used, %d over cap, %d candidates"
          % (GAME, used, skipped, total), file=sys.stderr)


if __name__ == "__main__":
    main()
