r"""Word slots inside sound-file paths, filled from a dictionary and from word embeddings.

`open_slot_words.py` and `open_slot_neighbours.py` split names on `_` only, so a sound file -- a
path, `amb/environment/wind/gusts/sand/dunes/sand_dune_gusts_01.rn75.pc.all.snd` -- offers them
almost nothing: its directories and its extension chain are glued into one token. Split on `_`,
`/` and `.` instead, and every directory component and every basename word becomes a slot with an
exact known prefix and suffix around it, the same frame those two methods use.

A frame qualifies when its slot holds at least --min distinct alphabetic fillers, mostly words
(the GloVe vocabulary decides). Each frame is offered, on its own:

    - the top --words English words by frequency (`wordfreq`), and
    - the --per GloVe words nearest the centroid of its fillers,

deduplicated. Black Ops 4's sound files keep backslashes and must be confirmed unfolded, so for that
game the output is written with backslashes; run it with `--no-fold`.

    python contrib/sound_word_slots.py --game BLKOPSCW --vectors glove.6B.100d.txt \
        | bin\windows\confirm_list.exe - --game BLKOPSCW --label "sound path word slots" \
          --script contrib/sound_word_slots.py
    python contrib/sound_word_slots.py --game BLKOPS04 --vectors glove.6B.100d.txt \
        | bin\windows\confirm_list.exe - --game BLKOPS04 --no-fold ...
"""
import argparse
import collections
import os
import re
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import token_markov  # noqa: E402
from open_slot_neighbours import load  # noqa: E402

ALPHA = re.compile(r"^[a-z]{3,}$")
SPLIT = re.compile(r"([_/.])")


def present_unfolded(game, pool):
    """Black Ops 4 sound files: hashed with their backslashes, returned with forward slashes."""
    import glob
    snapshot = token_markov.snapshot
    for path in snapshot.snapshots():
        snap = snapshot.read(path)
        if snap.game == game:
            ids = {i & token_markov.MASK for i, p in snap.records if snap.pool_name(p) == pool}
    names = set()
    for path in glob.glob(os.path.join(snapshot.settings.tables_csv(), "*.csv")):
        with open(path, encoding="utf-8", errors="replace") as handle:
            for line in handle:
                _, _, name = line.partition(",")
                if name.strip():
                    names.add(name.strip())
    names.update(n.strip() for n in snapshot.confirmed_names())
    out = set()
    for name in names:
        spelled = name.replace("/", chr(92))
        if snapshot.fnv1a_nofold(spelled) & token_markov.MASK in ids:
            out.add(spelled.lower().replace(chr(92), "/"))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--game", required=True)
    ap.add_argument("--vectors", required=True)
    ap.add_argument("--pool", default="sound_asset")
    ap.add_argument("--min", type=int, default=4)
    ap.add_argument("--words", type=int, default=30000)
    ap.add_argument("--per", type=int, default=3000)
    args = ap.parse_args()

    from wordfreq import top_n_list
    common = [w for w in top_n_list("en", args.words * 2) if ALPHA.match(w)][: args.words]
    words, index, mat = load(args.vectors)

    backslash = args.game == "BLKOPS04" and args.pool == "sound_asset"
    if backslash:
        names = present_unfolded(args.game, args.pool)
    else:
        names, _ = token_markov.present(args.game, args.pool)
    frames = collections.defaultdict(set)
    for name in names:
        parts = SPLIT.split(name)
        for i in range(0, len(parts), 2):
            if ALPHA.match(parts[i]):
                frames[("".join(parts[:i]), "".join(parts[i + 1:]))].add(parts[i])
    kept = []
    for key, fillers in frames.items():
        vec = [index[f] for f in fillers if f in index]
        if len(fillers) >= args.min and len(vec) >= 0.6 * len(fillers):
            kept.append((key, vec))
    print("%s %s: %d names, %d frames" % (args.game, args.pool, len(names), len(kept)), file=sys.stderr)

    out = sys.stdout
    total = 0
    for start in range(0, len(kept), 256):
        chunk = kept[start:start + 256]
        cent = np.vstack([mat[v].mean(axis=0) for _, v in chunk])
        cent /= np.linalg.norm(cent, axis=1, keepdims=True) + 1e-9
        top = np.argpartition(-(cent @ mat.T), args.per, axis=1)[:, : args.per]
        for ((head, tail), _), row in zip(chunk, top):
            pick = (set(common) | {words[j] for j in row}) - frames[(head, tail)]
            block = "".join(head + w + tail + "\n" for w in pick)
            if backslash:
                block = block.replace("/", chr(92))
            out.write(block)
            total += len(pick)
    print("%d candidates" % total, file=sys.stderr)


if __name__ == "__main__":
    main()
