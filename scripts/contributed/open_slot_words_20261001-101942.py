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
    ap.add_argument("--word-from", type=int, default=0, help="skip this many top words (already run)")
    ap.add_argument("--max-fill", type=int, default=0, help="only frames with fewer fillers than this")
    ap.add_argument("--vocab-file", help="fill from this word list (one per line) instead of wordfreq")
    ap.add_argument("--lang", default="en", help="wordfreq language(s) for the fillers, comma separated")
    ap.add_argument("--ledger", action="store_true",
                    help="skip frames a previous --ledger run with the same words already covered, and record these")
    ap.add_argument("--count", action="store_true")
    args = ap.parse_args()

    from wordfreq import top_n_list
    import unicodedata
    words, seen_words = [], set()
    for lang in args.lang.split(","):
        picked = []
        for w in top_n_list(lang, args.words * 2):
            w = unicodedata.normalize("NFKD", w).encode("ascii", "ignore").decode()
            if ALPHA.match(w) and w not in seen_words:
                seen_words.add(w)
                picked.append(w)
        words += picked[args.word_from: args.words]
    if args.vocab_file:
        with open(args.vocab_file, encoding="utf-8") as handle:
            words = [w.strip() for w in handle if ALPHA.match(w.strip())][args.word_from: args.words]
    if args.lang != "en" and not args.vocab_file:
        # other languages are wanted for what English lacks; English words are already run
        english_top = set(top_n_list("en", 150000))
        words = [w for w in words if w not in english_top]
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
        if args.max_fill and len(fillers) >= args.max_fill:
            continue
        if len(fillers) >= args.min and sum(f in english for f in fillers) >= args.english * len(fillers):
            kept.append(key)
    ledger = None
    if args.ledger:
        ledger = os.path.join(os.path.dirname(os.path.abspath(__file__)), "open_slot_words_seen_%s_%s_%d_%d_%d.txt"
                              % (args.game.lower(), args.lang.replace(",", "-"), args.word_from, args.words, args.min))
        done = set()
        if os.path.exists(ledger):
            with open(ledger, encoding="utf-8") as handle:
                done = {line.rstrip("\n") for line in handle}
        kept = [k for k in kept if k[0] + "\t" + k[1] not in done]
    print("%s: %d word-slot frames, %d words, %d candidates"
          % (args.game, len(kept), len(words), len(kept) * len(words)), file=sys.stderr)
    if args.count:
        return
    if ledger:
        with open(ledger, "a", encoding="utf-8") as handle:
            handle.writelines(k[0] + "\t" + k[1] + "\n" for k in kept)
    out = sys.stdout
    for head, tail in sorted(kept):
        seen = frames[(head, tail)]
        out.write("".join(head + w + tail + "\n" for w in words if w not in seen))


if __name__ == "__main__":
    main()
