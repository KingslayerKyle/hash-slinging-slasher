r"""Word slots offered the words nearest their own fillers, by word embedding.

`open_slot_words.py` offers every word slot the same dictionary in frequency order, so reaching a
rare word means paying for every commoner one in every frame: words ranked 30k-150k returned one
name per 26M candidates against one per 2.6M for the top 30k. But a slot's fillers are a semantic
class -- `picture_portrait_<x>` holds roosevelt and eisenhower, a decal slot holds donations,
deliveries, manufacturing -- and its missing members are the words *nearest that class*, however
rare. So each frame gets its own ranking: the centroid of its fillers' GloVe vectors, the whole
400k-word GloVe vocabulary scored against it, the top --per words offered.

A frame is the same as in `open_slot_words.py`: an exact known prefix and suffix around one token,
whose slot holds at least --min distinct alphabetic fillers. Frames are never mixed.

The vectors are GloVe 6B (Wikipedia + Gigaword, 400k words): https://nlp.stanford.edu/data/glove.6B.zip
-- pass the extracted `glove.6B.100d.txt` with --vectors. Keep it out of `contrib/`, which `submit`
copies into the pull request.

    python contrib/open_slot_neighbours.py --game BLKOPSCW --vectors path/glove.6B.100d.txt \
        | bin\windows\confirm_list.exe - --game BLKOPSCW --label "open-slot embedding neighbours" \
          --script contrib/open_slot_neighbours.py
"""
import argparse
import collections
import os
import re
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import token_markov  # noqa: E402

POOLS = ("xmodel", "image", "material", "xanim", "sound_alias")
ALPHA = re.compile(r"^[a-z]{3,}$")


def load(path):
    words, rows = [], []
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            word, _, rest = line.partition(" ")
            if ALPHA.match(word):
                words.append(word)
                rows.append(np.array(rest.split(), dtype=np.float32))
    mat = np.vstack(rows)
    mat /= np.linalg.norm(mat, axis=1, keepdims=True) + 1e-9
    return words, {w: i for i, w in enumerate(words)}, mat


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--game", required=True)
    ap.add_argument("--vectors", required=True)
    ap.add_argument("--min", type=int, default=3)
    ap.add_argument("--per", type=int, default=3000)
    ap.add_argument("--mode", choices=("centroid", "knn"), default="centroid",
                    help="knn: the union of each filler's own --knn nearest words, for slots whose fillers"
                         " form several clusters a centroid would blur")
    ap.add_argument("--knn", type=int, default=200)
    ap.add_argument("--max-fill", type=int, default=0, help="only frames with fewer fillers than this")
    ap.add_argument("--count", action="store_true")
    args = ap.parse_args()

    words, index, mat = load(args.vectors)
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
        vec = [index[f] for f in fillers if f in index]
        # a word slot: enough fillers, and most of them real words the vectors know
        if args.max_fill and len(fillers) >= args.max_fill:
            continue
        if len(fillers) >= args.min and len(vec) >= max(args.min, 0.6 * len(fillers)):
            kept.append((key, vec))
    print("%s: %d frames, %d words in the vectors, %d candidates"
          % (args.game, len(kept), len(words), len(kept) * args.per), file=sys.stderr)
    if args.count:
        return

    out = sys.stdout
    if args.mode == "knn":
        fillers = sorted({i for _, v in kept for i in v})
        near = {}
        for start in range(0, len(fillers), 512):
            ids = fillers[start:start + 512]
            scores = mat[ids] @ mat.T
            top = np.argpartition(-scores, args.knn + 1, axis=1)[:, : args.knn + 1]
            for i, row in zip(ids, top):
                near[i] = row
        total = 0
        for key, v in kept:
            head, tail = key
            seen = frames[key]
            pick = {words[j] for i in v for j in near[i]} - seen
            total += len(pick)
            out.write("".join(head + w + tail + chr(10) for w in sorted(pick)))
        print("%d candidates" % total, file=sys.stderr)
        return
    batch = 256
    for start in range(0, len(kept), batch):
        chunk = kept[start:start + batch]
        cent = np.vstack([mat[v].mean(axis=0) for _, v in chunk])
        cent /= np.linalg.norm(cent, axis=1, keepdims=True) + 1e-9
        scores = cent @ mat.T
        top = np.argpartition(-scores, args.per, axis=1)[:, : args.per]
        for (key, _), row in zip(chunk, top):
            head, tail = key
            seen = frames[key]
            out.write("".join(head + words[j] + tail + "\n" for j in row if words[j] not in seen))


if __name__ == "__main__":
    main()
