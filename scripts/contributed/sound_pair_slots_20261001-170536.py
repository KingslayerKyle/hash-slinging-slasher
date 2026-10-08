r"""Two-word slots inside sound-file paths: `open_slot_bigrams.py` for the pool it could not split.

`sound_word_slots.py` showed Cold War's sound files open up once a path is split on `_`, `/` and `.`
(143 files on 2026-10-01), and `open_slot_bigrams.py` showed two-token slots pay with pairs the
corpus uses elsewhere. This is both at once. A frame is an exact path prefix and suffix around two
adjacent English words joined by the same separator (`_` inside a basename, `/` between folders);
with >= --min distinct pairs it is offered the commonest pairs of that separator seen in any sound
path of either game or any table.

    python contrib/sound_pair_slots.py --game BLKOPSCW | bin\windows\confirm_list.exe - \
        --game BLKOPSCW --label "sound path two-word slots" --script contrib/sound_pair_slots.py
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
    ap.add_argument("--min", type=int, default=4)
    ap.add_argument("--pairs", type=int, default=30000)
    ap.add_argument("--from", dest="pair_from", type=int, default=0, help="skip the commonest N pairs")
    args = ap.parse_args()

    from wordfreq import top_n_list
    english = set(top_n_list("en", 100000))

    def word(t):
        return ALPHA.match(t) and t in english

    snapshot = token_markov.snapshot
    corpus = set()
    for path in glob.glob(os.path.join(snapshot.settings.tables_csv(), "*sound*.csv")) + \
            glob.glob(os.path.join(snapshot.settings.tables_csv(), "*_sab.csv")):
        with open(path, encoding="utf-8", errors="replace") as handle:
            for line in handle:
                _, _, name = line.partition(",")
                if name.strip():
                    corpus.add(name.strip().lower().replace(chr(92), "/"))
    corpus.update(n.strip().lower().replace(chr(92), "/") for n in snapshot.confirmed_names())
    counts = {"_": collections.Counter(), "/": collections.Counter()}
    for name in corpus:
        parts = SPLIT.split(name)
        for i in range(0, len(parts) - 2, 2):
            sep = parts[i + 1]
            if sep in counts and word(parts[i]) and word(parts[i + 2]):
                counts[sep][parts[i] + sep + parts[i + 2]] += 1
    vocab = {sep: [p for p, _ in c.most_common(args.pairs)][args.pair_from:] for sep, c in counts.items()}

    backslash = args.game == "BLKOPS04"
    names = present_unfolded(args.game, "sound_asset") if backslash else \
        token_markov.present(args.game, "sound_asset")[0]
    frames = collections.defaultdict(set)
    for name in names:
        parts = SPLIT.split(name)
        for i in range(0, len(parts) - 2, 2):
            sep = parts[i + 1]
            if sep in counts and word(parts[i]) and word(parts[i + 2]):
                frames[("".join(parts[:i]), "".join(parts[i + 3:]), sep)].add(parts[i] + sep + parts[i + 2])
    kept = [k for k, v in frames.items() if len(v) >= args.min]
    print("%s: %d frames, %d candidates" % (args.game, len(kept), sum(len(vocab[k[2]]) for k in kept)),
          file=sys.stderr)
    out = sys.stdout
    for key in kept:
        head, tail, sep = key
        seen = frames[key]
        block = "".join(head + p + tail + "\n" for p in vocab[sep] if p not in seen)
        if backslash:
            block = block.replace("/", chr(92))
        out.write(block)


if __name__ == "__main__":
    main()
