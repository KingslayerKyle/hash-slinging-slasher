"""Tails for Black Ops 4 sound files, spelled the way the game hashes them: backslashes kept.

    python contrib/sound_tails_nofold.py --length 3     writes plans/bo4_sound_tails3.txt

`scripts/tails.py` writes `fold: yes` unconditionally, and Black Ops 4 `sound_asset` ids are the
hash of the name with its backslashes intact -- 8,385 of 8,385 reproduce unfolded, 0 folded. So
every tails and heads pass ever run here built each Black Ops 4 sound file's variants in a
spelling that cannot hash to its id. The largest unnamed pool in either game (70,000+) has never
been asked the one question that is live everywhere else: *this known name, with the end of its
basename changed*.

And "the end" is not the end of the string here. A sound file ends in a dotted encoding tail --
`.sn100.pc.snd`, `.ln100.pc.snd` -- which is fixed, so replacing a name's last k characters only
ever breaks the tail. This cuts k characters off the **basename before its tail** and puts every
k-character string back, followed by every tail the pool is measured to wear (so a name also
tries its siblings' encodings, which the numbered-take sweeps never varied together with text).

Seeds: every name in the tables and in `findings/` + `submissions/` whose unfolded hash is an id
in the Black Ops 4 `sound_asset` pool -- i.e. proven real, spelled exactly.
"""
import argparse
import collections
import itertools
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import snapshot  # noqa: E402


def split(name):
    """(stem up to the basename's end, dotted tail) -- tail starts at the basename's first dot."""
    cut = name.rfind("\\") + 1
    dot = name.find(".", cut)
    if dot < 0:
        return name, ""
    return name[:dot], name[dot:]


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--length", type=int, default=3)
    parser.add_argument("--tails", type=int, default=16, help="how many of the commonest tails to carry")
    parser.add_argument("--alphabet", type=int, default=38)
    options = parser.parse_args()
    k = options.length

    path = [p for p in snapshot.snapshots() if "BLKOPS04" in os.path.basename(p).upper()]
    snap = snapshot.read(path[0])
    pool = {i for i, p in snap.records if snap.pool_name(p) == "sound_asset"}
    print("BLKOPS04 sound_asset ids: %d" % len(pool), file=sys.stderr)

    candidates = set()
    folder = snapshot.settings.tables_csv()
    for table in sorted(os.listdir(folder)):
        if table.endswith(".csv"):
            candidates.update(n for n in snapshot.table_names(table[:-4]) if "\\" in n)
    candidates.update(n for n in snapshot.confirmed_names() if "\\" in n)

    mask = snapshot.ID_MASK
    known = sorted({n.strip().lower() for n in candidates if snapshot.fnv1a_nofold(n) & mask in pool})
    print("known Black Ops 4 sound file names, unfolded and proven: %d" % len(known), file=sys.stderr)

    tails = collections.Counter()
    ends = collections.Counter()
    stems = set()
    for name in known:
        base, tail = split(name)
        if not tail or len(base) - (base.rfind("\\") + 1) <= k:
            continue
        tails[tail] += 1
        stems.add(base[:-k])
        for ch in base[-k:]:
            ends[ch] += 1

    kept_tails = [t for t, _ in tails.most_common(options.tails)]
    alphabet = "".join(c for c, _ in ends.most_common(options.alphabet))
    covered = sum(tails[t] for t in kept_tails)
    print("tails: %d distinct, top %d carry %d of %d names" % (len(tails), len(kept_tails), covered, sum(tails.values())), file=sys.stderr)
    print("alphabet (%d): %s" % (len(alphabet), alphabet), file=sys.stderr)

    prefix = os.path.join(ROOT, "plans", "bo4_sound_tails%d" % k)
    with open(prefix + ".stems.txt", "w", encoding="utf-8", newline="\n") as handle:
        handle.write("\n".join(sorted(stems)) + "\n")
    with open(prefix + ".endings.txt", "w", encoding="utf-8", newline="\n") as handle:
        for combo in itertools.product(alphabet, repeat=k):
            body = "".join(combo)
            for tail in kept_tails:
                handle.write(body + tail + "\n")
    with open(prefix + ".txt", "w", encoding="utf-8", newline="\n") as handle:
        handle.write("label: bo4 sound file tails of length %d, unfolded\n" % k)
        handle.write("describe: every proven Black Ops 4 sound file name with the last %d characters of its basename "
                     "replaced over the measured alphabet, re-tailed with the %d commonest encoding tails, backslashes kept\n\n" % (k, len(kept_tails)))
        handle.write("stem: @plans/bo4_sound_tails%d.stems.txt\n\nend: @plans/bo4_sound_tails%d.endings.txt\n\nbare: yes\nfold: no\n" % (k, k))
    print("%d stems x %d endings = %d candidates" % (len(stems), len(alphabet) ** k * len(kept_tails),
                                                    len(stems) * len(alphabet) ** k * len(kept_tails)), file=sys.stderr)


if __name__ == "__main__":
    main()
