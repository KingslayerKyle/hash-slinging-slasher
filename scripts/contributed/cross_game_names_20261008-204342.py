"""Every name known for any game, printed once, for confirming against a different game.

The five modern games share one hash policy for ordinary assets (IW offset, 63 bits) and one for
aliases (Treyarch offset, full width), and they reuse each other's assets heavily: BO6 ships MWII's
`iw9/...` sound files and Cold War's `ai_t9_zm_...` animations under their original names. A name
proven in one game is therefore a candidate in every other, at no generation cost at all.

`confirm_list` already routes each candidate to the right policy per pool, so this only has to
gather and de-duplicate. Sources: every cod-name-db table (all games, `_v2` and legacy alike), every
game's `all_names/`, every submission file and every local finding. Lowercased, because every
policy lowercases before hashing (BO4 SAB backslashes are kept as written).

    python contrib/cross_game_names.py | confirm_list - --game BLACKOP7 --script contrib/cross_game_names.py

First measured 2026-10-08 on BO6: 3,817,006 candidates in one second, 1,052 new names
(949 sound files, 55 anims, 37 aliases, 11 images).
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
while not (ROOT / "scripts" / "snapshot.py").is_file() and ROOT != ROOT.parent:
    ROOT = ROOT.parent


def names():
    for f in sorted((ROOT / "cod-name-db" / "csv").glob("*.csv")):
        for line in f.open(encoding="utf-8", errors="replace"):
            _, _, name = line.rstrip("\r\n").partition(",")
            yield name
    for top in ("all_names", "submissions", "findings"):
        for f in sorted((ROOT / top).rglob("*.txt")):
            for line in f.open(encoding="utf-8", errors="replace"):
                key, sep, name = line.rstrip("\r\n").partition(",")
                if sep:
                    yield name


def main():
    seen = set()
    out = sys.stdout
    for name in names():
        name = name.strip().lower()
        if name and name not in seen:
            seen.add(name)
            out.write(name + "\n")


if __name__ == "__main__":
    main()
