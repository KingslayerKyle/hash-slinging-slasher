"""Can the three plan lists rebuild a real MWII sound name?

`plans/mwii_sound.txt` composes `directory + basename + tail`. That only works if the
decomposition is lossless -- if stripping the variant index off the basename and the encoding tail
off the end, then handing both back, reproduces the name that hashed to the id. This checks that
on every verified MWII sound name the tables and the capture agree on, without running a search.

Also reports how much of the corpus each list would carry, which is what decides whether the plan
needs the wider cross-game vocabulary or the game's own is enough.
"""
import collections
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import settings
import snapshot

TAIL = re.compile(r"\.(?P<chan>[a-z]{1,4})\.(?P<qual>\d+)\.48000\.(?P<ext>[a-z_]+)$")
VARIANT = re.compile(r"^_(\d+)$")


def main():
    game = settings.game()
    path = [p for p in snapshot.snapshots() if snapshot.read(p).game == game][0]
    held = {k: set(v) for k, v in snapshot.read(path).by_pool().items()}
    ids = held.get("sound_asset", set())

    directories = set()
    basenames = set()
    tails = set()
    rebuilt_ok = 0
    rebuilt_bad = []
    total = 0
    skipped = 0

    for line in (Path(settings.tables_csv()) / "fnv1a_xsounds_v2.csv").open(encoding="utf-8"):
        key, sep, display = line.strip().partition(",")
        if not sep:
            continue
        try:
            key = int(key, 16)
        except ValueError:
            continue
        if key & snapshot.ID_MASK not in ids:
            continue
        restored = snapshot.verified_database_row("fnv1a_xsounds_v2", key, display)
        if restored is None:
            skipped += 1
            continue
        _, name = restored
        total += 1

        match = TAIL.search(name)
        if not match:
            continue
        head = name[: match.start()]
        tail = name[match.start():]
        directory, _, basename = head.rpartition(".")

        # The plan holds the basename with no variant index and the tail list puts one back.
        # Two-digit is what the corpus overwhelmingly shows; rebuild both ways and accept either.
        core = basename
        variant = ""
        split = VARIANT.match(basename[basename.rfind("_"):]) if "_" in basename else None
        if split:
            core, variant = basename[: basename.rfind("_")], basename[basename.rfind("_"):]

        candidates = [directory + "." + core + variant + tail] if directory else []
        candidates.append(directory + "." + core + variant.zfill(2).replace("_0", "_0") + tail
                           if variant else directory + "." + core + tail)
        if any(snapshot.fnv1a(c, game, "sound_asset") & snapshot.ID_MASK == key for c in candidates):
            rebuilt_ok += 1
        elif len(rebuilt_bad) < 8:
            rebuilt_bad.append({"name": name, "dir": directory, "core": core,
                                "variant": variant, "tail": tail})

        directories.add(directory + ".")
        basenames.add(core)
        tails.add(tail)

    print("verified MWII sound names in capture : %s" % format(total, ","))
    print("rows that restore no spelling        : %s" % format(skipped, ","))
    print("rebuilt to the same id from 3 pieces : %s" % format(rebuilt_ok, ","))
    if total:
        print("success rate                          : %.4f%%" % (100 * rebuilt_ok / total))
    print("distinct directories this corpus needs: %s" % format(len(directories), ","))
    print("distinct basenames  this corpus needs: %s" % format(len(basenames), ","))
    print("distinct tails      this corpus needs: %s" % format(len(tails), ","))
    if rebuilt_bad:
        print("\nfirst failures:")
        for row in rebuilt_bad:
            print("  %r -> dir=%r core=%r variant=%r tail=%r" % (
                row["name"], row["dir"], row["core"], row["variant"], row["tail"]))


if __name__ == "__main__":
    main()
