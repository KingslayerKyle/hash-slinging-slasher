r"""English words, dropped into the slots the game fills with English words.

Companion to `open_slot_codes.py`, for the other kind of open class. The 2026-10-01 holdout
measurement says the unnamed names are built from tokens nobody has seen. Where a slot is filled
by short codes, brute force covers it. Where it is filled by *words* -- `c_t8_mp_spe_recon_<outfit>`
takes samurai, viking, roman, paladin, egyptian -- the unseen members are words too, and no
recombination of the corpus can supply a word the corpus never held. A dictionary can.

A frame is an exact known prefix and exact known suffix around one slot. It qualifies when its slot
holds at least --min distinct fillers and at least --english of them are English words (by
`wordfreq`'s list), which marks it as a word slot rather than a code or number slot. Each qualifying
frame is offered the top --words English words on its own, never mixed with another frame's
pieces.

    pip install --user wordfreq
    python contrib/open_slot_words.py --game BLKOPS04 | bin\windows\confirm_list.exe - \
        --game BLKOPS04 --label "open-slot english words" --script contrib/open_slot_words.py
"""
import argparse
import collections
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
    ap.add_argument("--english", type=float, default=0.6)
    ap.add_argument("--words", type=int, default=30000)
    ap.add_argument("--count", action="store_true")
    args = ap.parse_args()

    from wordfreq import top_n_list
    words = [w for w in top_n_list("en", args.words * 2) if ALPHA.match(w)][: args.words]
    english = set(top_n_list("en", 200000))

    frames = collections.defaultdict(set)
    for pool in POOLS:
        names, _ = token_markov.present(args.game, pool)
        for name in names:
            toks = name.split("_")
            for i, tok in enumerate(toks):
                if ALPHA.match(tok):
                    head = "_".join(toks[:i]) + "_" if i else ""
                    tail = "_" + "_".join(toks[i + 1:]) if i < len(toks) - 1 else ""
                    frames[(head, tail)].add(tok)
    kept = []
    for key, fillers in frames.items():
        if len(fillers) >= args.min and sum(f in english for f in fillers) >= args.english * len(fillers):
            kept.append(key)
    print("%s: %d word-slot frames, %d words, %d candidates"
          % (args.game, len(kept), len(words), len(kept) * len(words)), file=sys.stderr)
    if args.count:
        return
    out = sys.stdout
    for head, tail in sorted(kept):
        seen = frames[(head, tail)]
        out.write("".join(head + w + tail + "\n" for w in words if w not in seen))


if __name__ == "__main__":
    main()
