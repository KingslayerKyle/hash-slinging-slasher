"""Lists for the sound directory-swap plan: every known modern sound directory x every known sound
basename (take number kept) x every modern tail.

The same take file is often filed under a different root or folder in another title or mode --
`iw9/wpn/...` beside `jup/wpn/...`, `core/fly/...` beside `t10/fly/...` -- and a basename proven in
one directory is a candidate in every other. A cross product, so it is a plan for the engine
(about 2e10 for 3,000 dirs x 180,000 bases x 41 tails, chance matches ~0.002), not printed.

    python contrib/sound_dir_swap.py
    confirm_plan contrib/sound_dir_swap.plan.txt --game BLACKOP6
"""
from pathlib import Path
import collections
import sys

ROOT = Path(__file__).resolve().parent
while not (ROOT / "scripts" / "snapshot.py").is_file() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
CONTRIB = ROOT / "contrib"
sys.path.insert(0, str(CONTRIB))
from sound_tail_swap import MODERN, all_names  # noqa: E402


def main():
    dirs, bases, tails = set(), set(), collections.Counter()
    for name in all_names():
        m = MODERN.match(name)
        if m:
            d, _, b = m.group(1).rpartition("/")
            if d:
                dirs.add(d + "/")
            bases.add(b)
            tails[name[len(m.group(1)):]] += 1
    tails = [t for t, n in tails.most_common() if n > 1]
    for fname, rows in (("sdir_dirs.txt", sorted(dirs)), ("sdir_bases.txt", sorted(bases)),
                        ("sdir_tails.txt", tails)):
        (CONTRIB / fname).write_text("".join(r + "\n" for r in rows), encoding="utf-8")
    (CONTRIB / "sound_dir_swap.plan.txt").write_text(
        "label: sound directory swap -- known sound dirs x known basenames x modern tails\n"
        "describe: every known modern sound directory, crossed with every known sound basename "
        "(take kept) and every modern tail; see contrib/sound_dir_swap.py\n"
        "begin: @contrib/sdir_dirs.txt\nstem: @contrib/sdir_bases.txt\nend: @contrib/sdir_tails.txt\n",
        encoding="utf-8")
    print(f"{len(dirs)} dirs, {len(bases)} bases, {len(tails)} tails", file=sys.stderr)


if __name__ == "__main__":
    main()
