"""Tails and heads of length k, over only the names sitting in open pull requests.

    python contrib/inflight_edges.py --length 4 [--game BLKOPS04]

`tails.py` and `heads` run over the whole corpus, which every contributor shares, and have been
swept to exhaustion on it. An open pull request's names are not in anybody's corpus until it
merges -- `snapshot.confirmed_names` reads `submissions/`, and their folders are not there yet --
so no edge variation has ever been asked of them. This writes two plans whose stems are those
names alone, against the ending and beginning lists `tails.py` already wrote for k:

    plans/inflight_tails<k>.txt    each in-flight name with its last k characters replaced
    plans/inflight_heads<k>.txt    the mirror: its first k characters replaced

A few thousand stems instead of a million, so k=4 is seconds rather than fifteen minutes.

Seeds are read from `submissions/_inflight_*/` -- see `inflight_fetch.py`, which writes them from
the open pull requests' diffs under a prefix that cannot collide with the real folder when the
pull request merges. `sound_asset` files are skipped: Black Ops 4 sound names keep their
backslashes and these plans fold (see `sound_tails_nofold.py` for those).

## Measured 2026-09-14: 0, and the closure is where in-flight seeds pay

    Black Ops 4, 20 open pull requests, 2,815 names (1,903 outside sound_asset)
    tails k=4: 1,547 stems, 0.36 B scanned per pool pass, 0 matched
    heads k=4: 1,899 stems, 0.50 B scanned per pool pass, 0 matched

The same seeds through `derive_closure` returned **41** (image siblings and channels of the
in-flight materials and images) plus **3** from `final_byte` -- so the open pull requests' authors
had already run edge variation over their own names and had not run the cross-type derivations.
Seed the closure first; these two plans are the cheap check after it.

Closed-unmerged pull requests were checked the same way and are empty: 25 of them, 5,476 names,
every one already in the tables (5,249) or claimed (227).
"""
import argparse
import glob
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def inflight_names(game):
    names = set()
    for path in glob.glob(os.path.join(ROOT, "submissions", "_inflight_*", "*.txt")):
        folder = os.path.basename(os.path.dirname(path))
        if game and "_%s_" % game not in folder:
            continue
        if os.path.basename(path).startswith("sound_asset"):
            continue
        with open(path, encoding="utf-8", errors="replace") as handle:
            for line in handle:
                key, _, name = line.partition(",")
                name = (name or key).strip().lower().replace("\\", "/")
                if name:
                    names.add(name)
    return sorted(names)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--length", type=int, default=4)
    parser.add_argument("--game", default="BLKOPS04")
    options = parser.parse_args()
    k = options.length

    names = inflight_names(options.game)
    tails = sorted({n[:-k] for n in names if len(n) > k})
    heads = sorted({n[k:] for n in names if len(n) > k})

    for kind, stems, side, bare in (("tails", tails, "end", "yes"), ("heads", heads, "begin", "no")):
        endings = "plans/%s%d.endings.txt" % (kind, k)
        if not os.path.exists(os.path.join(ROOT, endings)):
            raise SystemExit("%s is missing -- run scripts/tails.py --length %d%s --write-plan plans/%s%d.txt first"
                             % (endings, k, " --head" if kind == "heads" else "", kind, k))
        stem_file = "plans/inflight_%s%d.stems.txt" % (kind, k)
        with open(os.path.join(ROOT, stem_file), "w", encoding="utf-8", newline="\n") as handle:
            handle.write("\n".join(stems) + "\n")
        with open(os.path.join(ROOT, "plans", "inflight_%s%d.txt" % (kind, k)), "w", encoding="utf-8", newline="\n") as handle:
            handle.write("label: in-flight %s of length %d\n" % (kind, k))
            handle.write("describe: names in open pull requests, %s %d characters replaced over the measured alphabet\n\n" % (kind, k))
            handle.write("stem: @%s\n\n%s: @%s\n\nbare: %s\nfold: yes\n" % (stem_file, side, endings, bare))
        print("%s k=%d: %d in-flight names -> %d stems" % (kind, k, len(names), len(stems)))


if __name__ == "__main__":
    main()
