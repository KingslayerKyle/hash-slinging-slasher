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
import importlib.util

ROOT = Path(__file__).resolve().parent
while not (ROOT / "scripts" / "snapshot.py").is_file() and ROOT != ROOT.parent:
    ROOT = ROOT.parent


def _companion(name, filename):
    """Load the reviewed, versioned companion shipped with this repository."""
    spec = importlib.util.spec_from_file_location(
        name, ROOT / "scripts" / "contributed" / filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

_sound = _companion("sound_tail_swap", "sound_tail_swap_20261008-205512.py")
MODERN, all_names = _sound.MODERN, _sound.all_names
CONTRIB = ROOT / "contrib"


def main():
    CONTRIB.mkdir(parents=True, exist_ok=True)
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
