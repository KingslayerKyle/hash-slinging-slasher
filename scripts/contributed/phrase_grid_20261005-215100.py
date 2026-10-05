r"""Voice-line phrase grids: probe a huge phrase vocabulary on two speakers, then fill every speaker.

Measured 2026-10-05: 357 of the 365 names English web bigrams found in Cold War were one family,
`vox_<spk>_mtx_execute_<phrase>` -- execution quips like `real_challenge`, `wrong_time`,
`just_starting` -- and every phrase exists for ~35 of its 37 operators. That changes the economics:
a phrase only has to be *detected* once, on one or two speakers, and the grid can then be filled.
So a vocabulary of millions of phrases costs millions of candidates, not tens of millions.

A *category* is the text between a speaker code and a phrase (`mtx_execute`). For every category
whose phrases are shared by many speakers (>= --speakers speakers, >= --phrases phrases each seen
with >= 3 speakers), this

    --probe   offers every phrase of the vocabulary to the two speakers holding the most phrases
    --fill    offers every phrase known for any speaker of the category to every speaker of it

The vocabulary (`--vocab` files, one phrase per line, words joined by `_`) is meant to be large:
single words, web bigrams, the corpus's own word pairs and triples, chained bigrams.

    python contrib/phrase_grid.py --probe --vocab phrases.txt | bin\windows\confirm_list.exe - --game BLKOPSCW ...
    python contrib/phrase_grid.py --fill | bin\windows\confirm_list.exe - --game BLKOPSCW ...
"""
import argparse
import collections
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import token_markov  # noqa: E402

PHRASE = re.compile(r"^[a-z]+(?:_[a-z]+){0,4}$")


def categories(names, min_speakers, min_phrases, family="vox"):
    """{category: (speakers, phrases)} for vox_<spk>_<category>_<phrase> grids."""
    seen = collections.defaultdict(lambda: collections.defaultdict(set))
    speakers_of = collections.defaultdict(set)
    for name in names:
        if not name.startswith(family + "_"):
            continue
        toks = name.split("_")
        if len(toks) < 4:
            continue
        spk = toks[1]
        rest = toks[2:]
        for k in range(1, min(4, len(rest))):
            cat, phrase = "_".join(rest[:k]), "_".join(rest[k:])
            if PHRASE.match(phrase):
                seen[cat][phrase].add(spk)
                speakers_of[cat].add(spk)
    out = {}
    for cat, phrases in seen.items():
        shared = {p for p, who in phrases.items() if len(who) >= 3}
        if len(speakers_of[cat]) >= min_speakers and len(shared) >= min_phrases:
            out[cat] = (speakers_of[cat], phrases)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--game", default="BLKOPSCW")
    ap.add_argument("--speakers", type=int, default=10)
    ap.add_argument("--phrases", type=int, default=5)
    ap.add_argument("--probe", action="store_true")
    ap.add_argument("--fill", action="store_true")
    ap.add_argument("--vocab", nargs="*", default=[])
    ap.add_argument("--category", nargs="*", help="only these categories (e.g. mtx_execute)")
    ap.add_argument("--probes", type=int, default=2, help="speakers each phrase is tried on")
    ap.add_argument("--cross", action="store_true",
                    help="inside each category, every phrase's first word x every remainder seen, x every speaker"
                         " (ss_<streak>_<event> is a streak x event grid of its own)")
    ap.add_argument("--split", type=int, default=1, help="--cross: how many leading words form the row")
    ap.add_argument("--family", default="vox",
                    help="first token of the names; the second plays the speaker (wpn_<weapon>_..., fly_<x>_...)")
    ap.add_argument("--count", action="store_true")
    args = ap.parse_args()

    names, _ = token_markov.present(args.game, "sound_alias")
    cats = categories(names, args.speakers, args.phrases, args.family)
    if args.category:
        cats = {c: v for c, v in cats.items() if c in args.category}
    out = set()
    if args.fill:
        for cat, (speakers, phrases) in cats.items():
            for phrase in phrases:
                for spk in speakers:
                    out.add("%s_%s_%s_%s" % (args.family, spk, cat, phrase))
    if args.cross:
        for cat, (speakers, phrases) in cats.items():
            parts = [p.split("_") for p in phrases]
            split = [("_".join(t[:args.split]), "_".join(t[args.split:])) for t in parts if len(t) > args.split]
            rows = {a for a, _ in split}
            cols = {b for _, b in split}
            if len(rows) * len(cols) * len(speakers) > 2000000:
                continue
            for a in rows:
                for b in cols:
                    for spk in speakers:
                        out.add("%s_%s_%s_%s_%s" % (args.family, spk, cat, a, b))
    if args.probe:
        vocab = set()
        for path in args.vocab:
            with open(path, encoding="utf-8", errors="replace") as handle:
                vocab |= {v.strip() for v in handle if PHRASE.match(v.strip())}
        # streamed, not collected: a large vocabulary over every category is hundreds of millions
        total = 0
        for cat, (speakers, phrases) in cats.items():
            per = collections.Counter()
            for phrase, who in phrases.items():
                per.update(who)
            probes = [s for s, _ in per.most_common(args.probes)]
            for spk in probes:
                head = "%s_%s_%s_" % (args.family, spk, cat)
                total += len(vocab)
                if not args.count:
                    sys.stdout.write("".join(head + p + "\n" for p in vocab if p not in phrases))
        print("%s: probing %d categories with %d phrases, about %d candidates"
              % (args.game, len(cats), len(vocab), total), file=sys.stderr)
        return
    out -= names
    print("%s: %d grid categories (%s), %d candidates" % (args.game, len(cats),
          ", ".join(sorted(cats)[:12]) + (" ..." if len(cats) > 12 else ""), len(out)), file=sys.stderr)
    if not args.count:
        sys.stdout.write("".join(o + "\n" for o in sorted(out)))


if __name__ == "__main__":
    main()
