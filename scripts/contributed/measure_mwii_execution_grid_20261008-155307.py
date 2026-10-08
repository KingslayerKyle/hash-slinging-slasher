"""How far does the MWII execution-take grid actually run, and what does it cost to fill?

`mp.executions.` is the largest single group in MWII's sound-file pool -- 2,953 named names, more
than any other directory. It is also unusually clean: every name is an execution core, a take index,
and an encoding.

    exec_baton_impact_head_02.pnn.75.48000.all
    exec_049_stand_victim_03_kill_lfe.pn.75.48000.all

So the naming convention states the range: strip the take, and what is left is a core the game has
already shown it uses; the question is only how far the take index runs past the last one anybody
has published. The observed counts decay sharply -- `_01` 505, `_02` 494, `_03` 444, `_04` 375,
`_05` 315, `_06` 171, `_07` 76 ... `_17` 3 -- which is what a filled grid looks like from the
outside, and it is why the pool is only 18.4% named while `xanim` in the same capture is 80.7%.

Prints the core vocabulary, the take range, and what a core x take x encoding product costs. Writes
nothing.
"""
import collections
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import settings
import snapshot

TAIL = re.compile(r"\.(?P<chan>[a-z]{1,4})\.(?P<qual>\d+)\.48000\.(?P<ext>[a-z_]+)$")
TAKE = re.compile(r"^(?P<core>.+?)_(?P<take>\d{1,3})$")


def main():
    game = settings.game()
    path = [p for p in snapshot.snapshots() if snapshot.read(p).game == game][0]
    held = {k: set(v) for k, v in snapshot.read(path).by_pool().items()}
    ids = held.get("sound_asset", set())
    table = "fnv1a_xsounds_v2"

    cores = collections.Counter()
    takes = collections.Counter()
    encodings = collections.Counter()
    cores_by_take = collections.defaultdict(set)
    total = 0
    named_by_directory = collections.Counter()

    with (Path(settings.tables_csv()) / (table + ".csv")).open(encoding="utf-8",
                                                               errors="replace") as handle:
        for line in handle:
            key, sep, display = line.strip().partition(",")
            if not sep:
                continue
            try:
                key = int(key, 16)
            except ValueError:
                continue
            if key & snapshot.ID_MASK not in ids:
                continue
            restored = snapshot.verified_database_row(table, key, display)
            if restored is None:
                continue
            _, name = restored
            if snapshot.fnv1a(name, game, "sound_asset") & snapshot.ID_MASK != key:
                continue
            head = name.replace("/", ".")
            if not head.startswith("mp.executions."):
                continue
            total += 1
            match = TAIL.search(head)
            if not match:
                continue
            directory, _, basename = head[: match.start()].rpartition(".")
            named_by_directory[directory + "."] += 1
            split = TAKE.match(basename)
            if not split:
                continue
            cores[split.group("core")] += 1
            takes[split.group("take")] += 1
            cores_by_take[split.group("core")].add(split.group("take"))
            encodings[head[match.start():]] += 1

    print("execution names in capture : %s" % format(total, ","))
    print("distinct directories       : %s -> %s"
          % (len(named_by_directory), dict(named_by_directory)))
    print("distinct cores             : %s" % format(len(cores), ","))
    print("distinct encodings         : %s -> %s"
          % (format(len(encodings), ","), sorted(encodings)))
    print("take indices observed      : %s"
          % sorted(((int(t), c) for t, c in takes.items())))
    print("takes per core: max %d, mean %.2f"
          % (max(len(v) for v in cores_by_take.values()),
             sum(len(v) for v in cores_by_take.values()) / len(cores_by_take)))
    print()
    for width in (20, 30, 40, 60, 100):
        product = len(cores) * width * len(encodings)
        print("cores x takes 00..%03d x encodings = %s candidates"
              % (width - 1, format(product, ",")))
    print()
    print("cores with the most takes:")
    for core, seen in sorted(cores_by_take.items(), key=lambda kv: -len(kv[1]))[:15]:
        print("  %-44s %2d takes, %3d names" % (core, len(seen), cores[core]))


if __name__ == "__main__":
    main()