r"""The word slots that just paid, offered the whole vocabulary.

The 2026-09-30 lesson about cores ("a family found days ago meeting the tails of its own siblings")
has a word-slot form. A frame that has just yielded a dictionary word is the likeliest frame there
is to hold more unseen words -- `picture_portrait_<x>` gave roosevelt and eisenhower, so its other
cells are other presidents, however rare the word. The sweeps that found them stopped at a frequency
or similarity cut chosen for *every* frame at once; a few hundred hot frames can afford no cut.

So: every name confirmed by a run whose label mentions --labels (default: the open-slot word
methods) since --since, each alphabetic token of it taken as the slot, the frame around it, and the
union of wordfreq's full English list and the GloVe vocabulary offered to each such frame.

    python contrib/hot_word_frames.py --game BLKOPSCW --vectors glove.6B.100d.txt \
        | bin\windows\confirm_list.exe - --game BLKOPSCW --label "hot word frames, whole vocabulary" \
          --script contrib/hot_word_frames.py
"""
import argparse
import glob
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import token_markov  # noqa: E402

ALPHA = re.compile(r"^[a-z]{3,}$")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--game", required=True)
    ap.add_argument("--vectors", required=True)
    ap.add_argument("--since", default="20261001")
    ap.add_argument("--labels", default="open-slot,word slots,pooled grid,english word,hot word frames")
    ap.add_argument("--count", action="store_true")
    ap.add_argument("--sibling-tails", type=int, default=0,
                    help="instead: each hot prefix x every tail any known name continues it with x the top"
                         " N frequency words")
    ap.add_argument("--exclude-labels", default="hot word frames",
                    help="runs whose notes mention this are not read as hot (so a re-run reads only new hits)")
    ap.add_argument("--ledger", action="store_true", help="skip frames already offered, record these")
    ap.add_argument("--seed", action="store_true",
                    help="record, without offering anything, the frames a run before the ledger existed covered")
    args = ap.parse_args()

    root = token_markov.ROOT
    hits = set()
    marks = [m.strip().lower() for m in args.labels.split(",")]
    for notes in glob.glob(os.path.join(root, "findings", args.game.lower(), "run_*", "notes.md")):
        run = os.path.basename(os.path.dirname(notes))
        if run[4:12] < args.since:
            continue
        with open(notes, encoding="utf-8", errors="replace") as handle:
            text = handle.read().lower()
        if not any(m in text for m in marks):
            continue
        if args.exclude_labels and args.exclude_labels.lower() in text and (args.seed or not args.ledger):
            continue
        for path in glob.glob(os.path.join(os.path.dirname(notes), "*.txt")):
            with open(path, encoding="utf-8", errors="replace") as handle:
                for line in handle:
                    _, _, name = line.partition(",")
                    if name.strip():
                        hits.add(name.strip().lower().replace(chr(92), "/"))

    from wordfreq import top_n_list
    vocab = {w for w in top_n_list("en", 10 ** 7) if ALPHA.match(w)}
    with open(args.vectors, encoding="utf-8") as handle:
        for line in handle:
            w = line.split(" ", 1)[0]
            if ALPHA.match(w):
                vocab.add(w)
    vocab = sorted(vocab)

    frames = {}
    for name in hits:
        toks = re.split(r"([_/.])", name)
        for i in range(0, len(toks), 2):
            if ALPHA.match(toks[i]):
                frames.setdefault(("".join(toks[:i]), "".join(toks[i + 1:])), set()).add(toks[i])
    print("%s: %d hot names, %d frames, %d words, %d candidates"
          % (args.game, len(hits), len(frames), len(vocab), len(frames) * len(vocab)), file=sys.stderr)
    if args.sibling_tails:
        heads = {h for h, _ in frames}
        tails = {}
        for pool in ("xmodel", "image", "material", "xanim", "sound_alias", "sound_asset"):
            names, _ = token_markov.present(args.game, pool)
            for name in names:
                toks = re.split(r"([_/.])", name)
                for i in range(0, len(toks), 2):
                    head = "".join(toks[:i])
                    if head in heads and ALPHA.match(toks[i]):
                        tails.setdefault(head, {}).setdefault("".join(toks[i + 1:]), set()).add(toks[i])
        # a tail counts as a family continuation once two different words have led into it; the
        # commonest 200 per prefix, so a short prefix like `vox_` cannot swamp the run
        for head in list(tails):
            ranked = sorted(((len(f), t) for t, f in tails[head].items() if len(f) >= 2), reverse=True)
            tails[head] = [t for _, t in ranked[:200]]
        top = [w for w in top_n_list("en", args.sibling_tails * 2) if ALPHA.match(w)][: args.sibling_tails]
        pairs = [(h, t) for h in heads for t in tails.get(h, ()) if (h, t) not in frames]
        print("  sibling tails: %d heads, %d new (head, tail) pairs, %d candidates"
              % (len(heads), len(pairs), len(pairs) * len(top)), file=sys.stderr)
        if args.count:
            return
        out = sys.stdout
        for head, tail in sorted(pairs):
            block = "".join(head + w + tail + "\n" for w in top)
            if args.game == "BLKOPS04" and ".snd" in tail:
                block = block.replace("/", chr(92))
            out.write(block)
        return
    if args.seed:
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "hot_word_frames_seen_%s.txt" % args.game.lower()), "a", encoding="utf-8") as handle:
            handle.writelines(k[0] + chr(9) + k[1] + chr(10) for k in frames)
        print("  seeded %d frames" % len(frames), file=sys.stderr)
        return
    if args.ledger:
        ledger = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                              "hot_word_frames_seen_%s.txt" % args.game.lower())
        done = set()
        if os.path.exists(ledger):
            with open(ledger, encoding="utf-8") as handle:
                done = {line.rstrip(chr(10)) for line in handle}
        frames = {k: v for k, v in frames.items() if k[0] + chr(9) + k[1] not in done}
        print("  %d frames not yet offered" % len(frames), file=sys.stderr)
        if not args.count:
            with open(ledger, "a", encoding="utf-8") as handle:
                handle.writelines(k[0] + chr(9) + k[1] + chr(10) for k in frames)
    if args.count:
        return
    backslash = args.game == "BLKOPS04"
    out = sys.stdout
    for (head, tail), seen in sorted(frames.items()):
        block = "".join(head + w + tail + "\n" for w in vocab if w not in seen)
        if backslash and ".snd" in tail:
            block = block.replace("/", chr(92))
        out.write(block)


if __name__ == "__main__":
    main()
