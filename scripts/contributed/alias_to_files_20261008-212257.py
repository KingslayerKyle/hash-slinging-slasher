"""Sound-file candidates for known aliases that have no known take files: the reverse of
alias_from_files.py.

A modern sound file is `<dir>/<family>_<take>.<tail>` and its alias is usually `<family>`. For an
alias whose family has no known file, the directory is borrowed from the known file families that
share its longest underscore-prefix (`weap_mike4_fire_npc_far` borrows the directories of
`weap_mike4_fire_*`). Each borrowed directory is crossed with the take numbers seen in that
directory (01..12 when padded, 1..12 when not), no take at all, and the target game's tails.

    python contrib/alias_to_files.py --game BLACKOP6 | confirm_list - --game BLACKOP6 --script contrib/alias_to_files.py
"""
from pathlib import Path
import argparse
import collections
import re
import sys

ROOT = Path(__file__).resolve().parent
while not (ROOT / "scripts" / "snapshot.py").is_file() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
sys.path.insert(0, str(ROOT / "contrib"))
from sound_tail_swap import MODERN, all_names, target_tails  # noqa: E402
from alias_segments import known_aliases  # noqa: E402

TAKE = re.compile(r"^(.*?)_(\d{1,3})$")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--game", required=True)
    ap.add_argument("--takes", type=int, default=12)
    ap.add_argument("--dirs", type=int, default=6, help="most directories borrowed per alias")
    a = ap.parse_args()
    tails = target_tails(a.game)
    families = collections.defaultdict(collections.Counter)  # family -> dir counts
    padded = collections.Counter()
    aliases = set()
    for name in all_names():
        m = MODERN.match(name)
        if m:
            d, _, base = m.group(1).rpartition("/")
            t = TAKE.match(base)
            fam = t.group(1) if t else base
            families[fam][d] += 1
            if t:
                padded[len(t.group(2)) > 1] += 1
    aliases = {x for x in known_aliases() if x and "/" not in x and "." not in x}
    # prefix index: every underscore-prefix of a family -> directory counts
    prefix = collections.defaultdict(collections.Counter)
    for fam, dirs in families.items():
        parts = fam.split("_")
        for n in range(2, len(parts) + 1):
            prefix["_".join(parts[:n])].update(dirs)
    takes = [f"_{i:02d}" for i in range(1, a.takes + 1)] + [f"_{i}" for i in range(1, a.takes + 1)] + [""]
    out = sys.stdout
    count = 0
    for alias in sorted(aliases - set(families)):
        parts = alias.split("_")
        dirs = None
        for n in range(len(parts), 1, -1):
            dirs = prefix.get("_".join(parts[:n]))
            if dirs:
                break
        if not dirs:
            continue
        for d, _ in dirs.most_common(a.dirs):
            lead = f"{d}/{alias}" if d else alias
            for t in takes:
                out.write("".join(lead + t + tail + "\n" for tail in tails))
                count += len(tails)
    print(f"{len(aliases)} known aliases, {count} candidates", file=sys.stderr)


if __name__ == "__main__":
    main()
