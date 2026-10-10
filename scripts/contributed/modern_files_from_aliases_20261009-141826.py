"""Modern sound-file candidates built from known aliases, placed where their siblings live.

A modern sound file is hashed as a dotted path -- `iw9.wpn.mike4.weap_mike4_reload_end_plr_01.ln.75.48000.all`
-- whose basename is very often an alias plus a take number. The published `_v2` table shows the
same names with `/` for display. For every known modern alias this looks up the files whose
basename shares its first two underscore tokens, takes the directories and encoding tails those
siblings use (most common first, capped), and offers `dir.alias[_take].tail` for the takes the
siblings themselves use. Directories and tails are only ever ones real files carry.

Spent by: the alias and file corpora as they stand; re-run after either grows.
"""
from collections import Counter, defaultdict
from pathlib import Path
import argparse
import re
import sys

ROOT = next((p for p in Path(__file__).resolve().parents
             if (p / 'scripts/snapshot.py').is_file()), None)
if ROOT is None:
    raise SystemExit('Run this generator from a solver checkout')
TAKE = re.compile(r"^(.*?)(_\d+[a-z]?)?$")
MODERN = ("modwar22", "yamyamok", "blackop6", "blackop7", "modwar7")


def rows(path):
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        name = line.partition(",")[2].strip().lower()
        if name:
            yield name


def split_file(name):
    """dir, basename, tail -- from a display (`/`) or hashed (`.`) spelling."""
    name = name.replace("\\", "/")
    if "/" in name:
        folder, _, rest = name.rpartition("/")
        base, _, tail = rest.partition(".")
        return folder.replace("/", "."), base, tail
    parts = name.split(".")
    # dotted: the basename is the component holding an underscore nearest the tail
    for i in range(len(parts) - 1, -1, -1):
        if "_" in parts[i]:
            return ".".join(parts[:i]), parts[i], ".".join(parts[i + 1:])
    return None


def key(base):
    return "_".join(base.split("_")[:2])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--places", type=int, default=24, help="dir/tail pairs per alias")
    ap.add_argument("--takes", type=int, default=10, help="take suffixes per alias")
    ap.add_argument("--slash", action="store_true", help="spell with / separators (MW7 hashes its sound paths that way)")
    args = ap.parse_args()

    places = defaultdict(Counter)
    takes = defaultdict(Counter)
    file_sources = [ROOT / "cod-name-db" / "csv" / "fnv1a_xsounds_v2.csv"]
    alias_sources = [ROOT / "cod-name-db" / "csv" / "fnv1a_soundbanks_aliases_v2.csv"]
    for folder in ("submissions", "findings"):
        base = ROOT / folder
        if not base.exists():
            continue
        for path in base.rglob("*.txt"):
            low = path.as_posix().lower()
            if not any(g in low for g in MODERN):
                continue
            if "/sound_asset" in low or "/sndasset" in low:
                file_sources.append(path)
            elif "/sound_alias" in low:
                alias_sources.append(path)

    for path in file_sources:
        for name in rows(path):
            parsed = split_file(name)
            if not parsed or not parsed[0] or not parsed[2]:
                continue
            folder, base, tail = parsed
            stem, take = TAKE.match(base).groups()
            places[key(stem)][(folder, tail)] += 1
            takes[key(stem)][take or ""] += 1

    aliases = set()
    for path in alias_sources:
        aliases.update(rows(path))

    emitted = 0
    for alias in sorted(aliases):
        k = key(alias)
        if k not in places:
            continue
        spots = [p for p, _ in places[k].most_common(args.places)]
        ts = [t for t, _ in takes[k].most_common(args.takes)]
        for folder, tail in spots:
            for take in ts:
                if args.slash:
                    print(f"{folder.replace('.', '/')}/{alias}{take}.{tail}")
                else:
                    print(f"{folder}.{alias}{take}.{tail}")
                emitted += 1
    print(f"{len(aliases):,} aliases, {emitted:,} candidates", file=sys.stderr)


if __name__ == "__main__":
    main()
