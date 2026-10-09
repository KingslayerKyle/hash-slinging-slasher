"""Sound-alias candidates read off the sound files every game is known to hold.

In the modern games an alias usually names a family of take files:
`iw9/wpn/ar_mike4/weap_mike4_fire_npc_med_01.lnn.85.48000.all` belongs to an alias spelled like
`weap_mike4_fire_npc_med`. So each known sound file (modern or legacy tail) yields its basename
with the tail removed, then without its take number, then with each of those trimmed back one
underscore-segment at a time (an alias often covers a coarser family than its files spell). Every
known alias also contributes its own segment-trims, since a sibling alias is often a trimmed one.

Aliases hash under the Treyarch offset at full width in the modern games; `confirm_list` routes
that by pool, so this only prints strings.

    python contrib/alias_from_files.py | confirm_list - --game BLACKOP6 --script contrib/alias_from_files.py
"""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent
while not (ROOT / "scripts" / "snapshot.py").is_file() and ROOT != ROOT.parent:
    ROOT = ROOT.parent

MODERN = re.compile(r"^(.+?)\.([a-z]{2,3})\.(\d+)\.(\d+)\.([a-z_]+)$")
LEGACY = re.compile(r"^(.+?)\.([a-z]{2}\d+)\.pc\.([a-z_]+)\.snd$")
TAKE = re.compile(r"^(.*?)(?:_v?\d{1,3}[a-z]?)+$")


def rows():
    for f in sorted((ROOT / "cod-name-db" / "csv").glob("*.csv")):
        for line in f.open(encoding="utf-8", errors="replace"):
            _, _, name = line.rstrip("\r\n").partition(",")
            yield f.stem, name.lower()
    for top in ("all_names", "submissions", "findings", "contrib/open_pr_names"):
        for f in sorted((ROOT / top).rglob("*.txt")):
            for line in f.open(encoding="utf-8", errors="replace"):
                _, sep, name = line.rstrip("\r\n").partition(",")
                if sep:
                    yield f.stem, name.lower()


def trims(base, keep=2):
    parts = base.split("_")
    for n in range(len(parts), keep - 1, -1):
        yield "_".join(parts[:n])


def main():
    out = set()
    for source, name in rows():
        m = MODERN.match(name) or LEGACY.match(name)
        if m:
            base = m.group(1).rsplit("/", 1)[-1]
            out.update(trims(base))
            t = TAKE.match(base)
            if t and t.group(1):
                out.update(trims(t.group(1)))
        elif "alias" in source and "/" not in name and "." not in name:
            out.update(trims(name))
    print(f"{len(out)} alias candidates", file=sys.stderr)
    sys.stdout.write("".join(s + "\n" for s in sorted(out) if len(s) > 3))


if __name__ == "__main__":
    main()
