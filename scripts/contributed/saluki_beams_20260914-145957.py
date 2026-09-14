"""Beam names Saluki has already recovered, offered as candidates.

Saluki (the live Cordycep-backed asset browser most of this project's confirmations are checked
against) ships its own recovered-hash list for the `beam` pool -- a type this project's default
`pools` list does not hunt, because it sits outside the five wanted asset types. `beam` is a real,
small pool (130 ids in Black Ops 4) that cod-name-db has no dedicated table for either, so a name
recovered here is filed under `submit`'s general "every pool" handling rather than one of the six
usual csv files.

Where the source file comes from: open the `beam` category in Saluki with a game loaded and export
its recovered list (the export is `hash,name` per line, hex hash first). This is not something
`start` or a fresh clone can regenerate on its own -- it needs Saluki and a loaded game, the same
prerequisite `name_field_probe` and `loader_strings` already carry elsewhere in this project.

    python contrib/saluki_beams.py "C:/path/to/beams_recovered.csv"
    python contrib/saluki_beams.py "C:/path/to/beams_recovered.csv" | bin\\windows\\confirm_list.exe - --game BLKOPS04

Measured 2026-09-14: 34 names exported this way, 26 confirmed new against Black Ops 4's `beam`
pool with `all_pools = true`, none against the standard six -- this pool needs that config flag
or it is invisible to `confirm_list`, since it is not part of the default `pools` list.
"""
import sys


def main():
    if len(sys.argv) != 2:
        print("usage: saluki_beams.py <beams_recovered.csv>", file=sys.stderr)
        raise SystemExit(2)
    with open(sys.argv[1], encoding="utf-8", errors="replace") as fh:
        for line in fh:
            _hash, _, name = line.strip().partition(",")
            name = name.strip()
            if name:
                print(name)


if __name__ == "__main__":
    main()
