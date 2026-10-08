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
    ap.add_argument("--n", type=int, default=2, help="words in the slot (2 = pairs, 3 = triples)")
    ap.add_argument("--from", dest="pair_from", type=int, default=0, help="skip the commonest N pairs")
    ap.add_argument("--mixed", action="store_true",
                    help="windows of any letter-bearing tokens (codes, names) that are not all English words")
    ap.add_argument("--into-single", action="store_true",
                    help="offer the n-word sequences to one-word slots (>= --min word fillers) instead")
    ap.add_argument("--inner", action="store_true", help="only cross each frame's own first and last words")
    ap.add_argument("--count", action="store_true")
    args = ap.parse_args()
    n = args.n

    from wordfreq import top_n_list
    english = set(top_n_list("en", 100000))

    def is_word(t):
        return ALPHA.match(t) and t in english

    token = re.compile(r"^(?!\d+$)[a-z0-9]{2,}$")

    def fits(window):
        # --mixed: any letter-bearing tokens, but not all English words (that half is the default run)
        if args.mixed:
            return all(token.match(t) for t in window) and not all(is_word(t) for t in window)
        return all(is_word(t) for t in window)

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
        for i in range(len(toks) - n + 1):
            if fits(toks[i:i + n]):
                pair_count["_".join(toks[i:i + n])] += 1
    pairs = [p for p, _ in pair_count.most_common(args.pairs)][args.pair_from:]

    frames = collections.defaultdict(set)
    for pool in POOLS:
        names, _ = token_markov.present(args.game, pool)
        for name in names:
            toks = name.split("_")
            for i in range(len(toks) - n + 1):
                if fits(toks[i:i + n]):
                    head = "_".join(toks[:i]) + "_" if i else ""
                    tail = "_" + "_".join(toks[i + n:]) if i + n < len(toks) else ""
                    frames[(head, tail)].add("_".join(toks[i:i + n]))
    if args.into_single:
        frames = collections.defaultdict(set)
        for pool in POOLS:
            names, _ = token_markov.present(args.game, pool)
            for name in names:
                toks = name.split("_")
                for i, tok in enumerate(toks):
                    if is_word(tok):
                        head = "_".join(toks[:i]) + "_" if i else ""
                        tail = "_" + "_".join(toks[i + 1:]) if i < len(toks) - 1 else ""
                        frames[(head, tail)].add(tok)
    kept = [k for k, v in frames.items() if len(v) >= args.min]
    print("%s: %d two-word frames, %d pairs, %d candidates"
          % (args.game, len(kept), len(pairs), len(kept) * len(pairs)), file=sys.stderr)
    if args.count:
        return
    out = sys.stdout
    if args.inner:
        # each frame's own first words x its own last words: `paint_dead` and `rust_clean` offer
        # `paint_clean` and `rust_dead`
        total = 0
        for head, tail in sorted(kept):
            seen = frames[(head, tail)]
            parts = [p.split("_") for p in seen]
            firsts = {p[0] for p in parts}
            rests = {"_".join(p[1:]) for p in parts}
            block = {a + "_" + b for a in firsts for b in rests} - seen
            total += len(block)
            out.write("".join(head + c + tail + "\n" for c in block))
        print("  %d inner candidates" % total, file=sys.stderr)
        return
    for head, tail in sorted(kept):
        seen = frames[(head, tail)]
        out.write("".join(head + p + tail + "\n" for p in pairs if p not in seen))


if __name__ == "__main__":
    main()
