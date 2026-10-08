r"""Two-word slots, filled with the word pairs the corpus uses anywhere.

`open_slot_words.py` fills one-token slots. Many open slots span two: `..._<paint>_<dead>_mpx_...`,
`vox_<spk>_<well>_<done>`, and the pair varies as a unit. A frame here is an exact known prefix and
suffix around two adjacent tokens, both English words; it qualifies with >= --min distinct pairs.
The vocabulary is every adjacent pair of English words in any published or confirmed name, in
either game or any table, ranked by how often it occurs -- the top --pairs of them offered to each
frame on its own.

    python contrib/open_slot_bigrams.py --game BLKOPSCW | bin\windows\confirm_list.exe - \
        --game BLKOPSCW --label "two-word slots" --script contrib/open_slot_bigrams.py
"""
import argparse
import collections
import glob
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import token_markov  # noqa: E402

POOLS = ("xmodel", "image", "material", "xanim", "sound_alias")
ALPHA = re.compile(r"^[a-z]{3,}$")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--game", required=True)
    ap.add_argument("--min", type=int, default=5)
    ap.add_argument("--pairs", type=int, default=20000)
    ap.add_argument("--count", action="store_true")
    args = ap.parse_args()

    from wordfreq import top_n_list
    english = set(top_n_list("en", 100000))

    def is_word(t):
        return ALPHA.match(t) and t in english

    snapshot = token_markov.snapshot
    corpus = set()
    for path in glob.glob(os.path.join(snapshot.settings.tables_csv(), "*.csv")):
        with open(path, encoding="utf-8", errors="replace") as handle:
            for line in handle:
                _, _, name = line.partition(",")
                if name.strip():
                    corpus.add(name.strip().lower())
    corpus.update(n.strip().lower() for n in snapshot.confirmed_names())
    pair_count = collections.Counter()
    for name in corpus:
        toks = re.split(r"[_/\\.]", name)
        for i in range(len(toks) - 1):
            if is_word(toks[i]) and is_word(toks[i + 1]):
                pair_count[toks[i] + "_" + toks[i + 1]] += 1
    pairs = [p for p, _ in pair_count.most_common(args.pairs)]

    frames = collections.defaultdict(set)
    for pool in POOLS:
        names, _ = token_markov.present(args.game, pool)
        for name in names:
            toks = name.split("_")
            for i in range(len(toks) - 1):
                if is_word(toks[i]) and is_word(toks[i + 1]):
                    head = "_".join(toks[:i]) + "_" if i else ""
                    tail = "_" + "_".join(toks[i + 2:]) if i + 2 < len(toks) else ""
                    frames[(head, tail)].add(toks[i] + "_" + toks[i + 1])
    kept = [k for k, v in frames.items() if len(v) >= args.min]
    print("%s: %d two-word frames, %d pairs, %d candidates"
          % (args.game, len(kept), len(pairs), len(kept) * len(pairs)), file=sys.stderr)
    if args.count:
        return
    out = sys.stdout
    for head, tail in sorted(kept):
        seen = frames[(head, tail)]
        out.write("".join(head + p + tail + "\n" for p in pairs if p not in seen))


if __name__ == "__main__":
    main()
