r"""Every word and every pair of words near a phrase grid's own vocabulary, on one probe prefix.

`quip_phrases.py` chains web bigrams, so it only reaches phrases web text uses. A voice grid's
phrases share a *topic* instead -- Cold War's execution quips are knives, arteries, hostiles,
nightmares, lessons -- and the words of an unseen quip are likely near that topic even when the
pair is not a common web bigram. So: the centroid of the GloVe vectors of every word in the grid's
known phrases, the --top nearest words to it (plus those words themselves), and every single word
and every ordered pair of them as a phrase after --head.

    python contrib/glove_phrase_pairs.py --vectors glove.6B.100d.txt --category mtx_execute \
        --head vox_hdsn_mtx_execute_ | bin\windows\confirm_list.exe - --game BLKOPSCW ...
"""
import argparse
import os
import re
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import token_markov  # noqa: E402
from open_slot_neighbours import load  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--vectors", required=True)
    ap.add_argument("--game", default="BLKOPSCW")
    ap.add_argument("--category", required=True)
    ap.add_argument("--head", required=True)
    ap.add_argument("--top", type=int, default=3000)
    ap.add_argument("--open", type=int, default=0,
                    help="instead of topic x topic, topic x the N commonest English words, both orders")
    ap.add_argument("--triples", type=int, default=0,
                    help="instead: every ordered triple of (the N nearest topic words + common function words)")
    args = ap.parse_args()

    names, _ = token_markov.present(args.game, "sound_alias")
    marker = "_%s_" % args.category
    seeds = set()
    for name in names:
        if name.startswith("vox_") and marker in name:
            seeds |= set(name.split(marker, 1)[1].split("_"))
    words, index, mat = load(args.vectors)
    ids = [index[w] for w in seeds if w in index]
    c = mat[ids].mean(axis=0)
    c /= np.linalg.norm(c) + 1e-9
    near = [words[j] for j in np.argpartition(-(mat @ c), args.top)[: args.top]]
    vocab = sorted(set(near) | {w for w in seeds if w.isalpha()})
    out = sys.stdout
    if args.triples:
        from wordfreq import top_n_list
        function = [w.replace("'", "") for w in top_n_list("en", 150)]
        function = [w for w in dict.fromkeys(function) if re.match(r"^[a-z]+$", w)][:100]
        order = np.argsort(-(mat @ c))
        topic = []
        for j in order:
            if len(topic) >= args.triples:
                break
            if re.match(r"^[a-z]+$", words[j]):
                topic.append(words[j])
        small = list(dict.fromkeys(topic + function + sorted(w for w in seeds if w.isalpha())))
        for a in small:
            for b in small:
                out.write("".join(args.head + a + "_" + b + "_" + x + "\n" for x in small))
        print("%d words, %d triples" % (len(small), len(small) ** 3), file=sys.stderr)
        return
    if args.open:
        from wordfreq import top_n_list
        common = [w.replace("'", "") for w in top_n_list("en", args.open * 2)]
        common = [w for w in dict.fromkeys(common) if re.match(r"^[a-z]+$", w)][: args.open]
        for a in vocab:
            out.write("".join(args.head + a + "_" + b + "\n" for b in common))
            out.write("".join(args.head + b + "_" + a + "\n" for b in common))
        print("%d topic words x %d common words x 2 orders" % (len(vocab), len(common)), file=sys.stderr)
        return
    for a in vocab:
        out.write(args.head + a + "\n")
        out.write("".join(args.head + a + "_" + b + "\n" for b in vocab if b != a))
    print("%d seed words, %d vocabulary, about %d candidates" % (len(seeds), len(vocab), len(vocab) ** 2),
          file=sys.stderr)


if __name__ == "__main__":
    main()
