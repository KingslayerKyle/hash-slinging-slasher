r"""Multi-word slots inside sound-file paths: `open_slot_bigrams.py` for the pool it could not split.

`sound_word_slots.py` showed Cold War's sound files open up once a path is split on `_`, `/` and `.`
(143 files on 2026-10-01), and `open_slot_bigrams.py` showed multi-token slots pay with word runs the
corpus uses elsewhere. This is both at once. A frame is an exact path prefix and suffix around --n
adjacent English words, joined by `_` (inside a basename) or `/` (across folders), with the joining
pattern kept as part of the frame; with >= --min distinct fillers it is offered the commonest word
runs of the same joining pattern seen in any sound path of either game or any table.

    python contrib/sound_pair_slots.py --game BLKOPSCW | bin\windows\confirm_list.exe - \
        --game BLKOPSCW --label "sound path two-word slots" --script contrib/sound_pair_slots.py
    python contrib/sound_pair_slots.py --game BLKOPSCW --n 3 ...      three-word slots
"""
import argparse
import collections
import glob
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import token_markov  # noqa: E402
from sound_word_slots import present_unfolded  # noqa: E402

ALPHA = re.compile(r"^[a-z]{3,}$")
SPLIT = re.compile(r"([_/.])")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--game", required=True)
    ap.add_argument("--n", type=int, default=2, help="words in the slot")
    ap.add_argument("--min", type=int, default=4)
    ap.add_argument("--pairs", type=int, default=30000, help="commonest runs offered, per joining pattern")
    ap.add_argument("--from", dest="pair_from", type=int, default=0, help="skip the commonest N runs")
    ap.add_argument("--count", action="store_true")
    args = ap.parse_args()
    n = args.n

    from wordfreq import top_n_list
    english = set(top_n_list("en", 100000))

    def windows(parts):
        """(start, joining pattern, run) for every run of n English words joined by `_` or `/`."""
        for i in range(0, len(parts) - 2 * n + 2, 2):
            run = parts[i:i + 2 * n - 1]
            words, seps = run[0::2], tuple(run[1::2])
            if all(s in ("_", "/") for s in seps) and all(ALPHA.match(w) and w in english for w in words):
                yield i, seps, "".join(run)

    snapshot = token_markov.snapshot
    corpus = set()
    for path in glob.glob(os.path.join(snapshot.settings.tables_csv(), "*sound*.csv")) + \
            glob.glob(os.path.join(snapshot.settings.tables_csv(), "*_sab.csv")):
        with open(path, encoding="utf-8", errors="replace") as handle:
            for line in handle:
                _, _, name = line.partition(",")
                if name.strip():
                    corpus.add(name.strip().lower().replace(chr(92), "/"))
    corpus.update(c.strip().lower().replace(chr(92), "/") for c in snapshot.confirmed_names())
    counts = collections.defaultdict(collections.Counter)
    for name in corpus:
        for _, seps, run in windows(SPLIT.split(name)):
            counts[seps][run] += 1
    vocab = {seps: [r for r, _ in c.most_common(args.pairs)][args.pair_from:] for seps, c in counts.items()}

    backslash = args.game == "BLKOPS04"
    names = present_unfolded(args.game, "sound_asset") if backslash else \
        token_markov.present(args.game, "sound_asset")[0]
    frames = collections.defaultdict(set)
    for name in names:
        parts = SPLIT.split(name)
        for i, seps, run in windows(parts):
            frames[("".join(parts[:i]), "".join(parts[i + 2 * n - 1:]), seps)].add(run)
    kept = [k for k, v in frames.items() if len(v) >= args.min]
    print("%s: n=%d, %d frames, %d candidates" % (args.game, n, len(kept),
          sum(len(vocab.get(k[2], ())) for k in kept)), file=sys.stderr)
    if args.count:
        return
    out = sys.stdout
    for key in kept:
        head, tail, seps = key
        seen = frames[key]
        block = "".join(head + r + tail + "\n" for r in vocab.get(seps, ()) if r not in seen)
        if backslash:
            block = block.replace("/", chr(92))
        out.write(block)


if __name__ == "__main__":
    main()
