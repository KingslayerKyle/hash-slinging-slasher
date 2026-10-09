"""Coordinated swap of a directory name that the basename repeats, for its sibling directories.

Modern weapon sounds name the weapon twice: `t10/wpn/smg/roger31/reloads/fly_plr_smg_roger31_reload_
empty_ext02_magout.tnn.75.48000.all`. A sibling weapon's reload set is the same file list with
`roger31` replaced in BOTH places -- which single-token slotswap cannot produce (it changes one
occurrence) and the directory swap cannot either (the basename still says roger31).

For every known modern sound path and every directory component D (below the root) that also
occurs as a whole `_`-delimited token in the basename, the siblings of D are the other directory
names seen under the same parent path. Each sibling replaces D everywhere in the path. The tail is
kept. Siblings are capped per parent (--siblings, most-populated first).

    python contrib/sibling_dir_swap.py | confirm_list - --game BLACKOP7 --script contrib/sibling_dir_swap.py
"""
from pathlib import Path
import argparse
import collections
import re
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--siblings", type=int, default=80)
    a = ap.parse_args()
    paths = set()
    children = collections.defaultdict(collections.Counter)  # parent path -> child dir counts
    for name in all_names():
        if MODERN.match(name) and "/" in name:
            paths.add(name)
            parts = name.split("/")
            for i in range(1, len(parts) - 1):
                children["/".join(parts[:i])][parts[i]] += 1
    top = {p: [d for d, _ in c.most_common(a.siblings)] for p, c in children.items()}
    out = sys.stdout
    total = 0
    for name in paths:
        parts = name.split("/")
        base = parts[-1]
        for i in range(1, len(parts) - 1):
            d = parts[i]
            rx = re.compile(r"(?<![a-z0-9])" + re.escape(d) + r"(?![a-z0-9])")
            if not rx.search(base):
                continue
            parent = "/".join(parts[:i])
            for sib in top.get(parent, ()):
                if sib == d:
                    continue
                cand = "/".join(parts[:i] + [sib] + parts[i + 1:-1] + [rx.sub(sib, base)])
                if cand not in paths:
                    out.write(cand + "\n")
                    total += 1
    print(f"{len(paths):,} paths, {total:,} candidates", file=sys.stderr)


if __name__ == "__main__":
    main()
