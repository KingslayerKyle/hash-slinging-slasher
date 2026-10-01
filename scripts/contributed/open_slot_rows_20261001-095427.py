r"""Word slots too thin to see one row at a time, read across the rows of their grid.

`open_slot_words.py` qualifies a slot by the fillers *its own frame* holds: `vox_adlr_mtx_execute_<w>`
needs five known words after `vox_adlr_mtx_execute_` before it is offered the dictionary. In a grid
-- forty speakers, fifty skins, a dozen vehicles -- most rows hold one or two known words each, so
each row looks closed while the column plainly is not.

So the evidence is pooled: for every word slot, every *other* token that is a short code (a speaker,
a map, a variant: 2-5 characters, at least one letter) is wildcarded, and the fillers of all rows
sharing that pooled shape are counted together. A pooled slot with at least --min fillers across at
least --rows rows is open, and every row of it that no earlier sweep reached (fewer than 3 fillers
of its own) is offered the top --words English words. Each row is still its own exact frame; rows
are never mixed with each other's pieces.

    python contrib/open_slot_rows.py --game BLKOPSCW | bin\windows\confirm_list.exe - \
        --game BLKOPSCW --label "open-slot words, pooled across grid rows" --script contrib/open_slot_rows.py
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
CODE = re.compile(r"^(?=.*[a-z])[a-z0-9]{2,5}$")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--game", required=True)
    ap.add_argument("--min", type=int, default=8)
    ap.add_argument("--rows", type=int, default=3)
    ap.add_argument("--words", type=int, default=30000)
    ap.add_argument("--vectors", help="instead of the frequency list, offer each thin row the --per GloVe"
                                      " words nearest the centroid of its grid's pooled fillers")
    ap.add_argument("--per", type=int, default=3000)
    args = ap.parse_args()

    from wordfreq import top_n_list
    words = [w for w in top_n_list("en", args.words * 2) if ALPHA.match(w)][: args.words]

    row = collections.defaultdict(set)
    pooled = collections.defaultdict(set)
    members = collections.defaultdict(set)
    for pool in POOLS:
        names, _ = token_markov.present(args.game, pool)
        for name in names:
            toks = name.split("_")
            for i, tok in enumerate(toks):
                if not ALPHA.match(tok):
                    continue
                key = ("_".join(toks[:i]) + "_" if i else "", "_" + "_".join(toks[i + 1:]) if i < len(toks) - 1 else "")
                row[key].add(tok)
                for j, other in enumerate(toks):
                    if j != i and CODE.match(other):
                        shape = list(toks)
                        shape[j], shape[i] = "\0", "\1"
                        shape = "_".join(shape)
                        pooled[shape].add(tok)
                        members[shape].add(key)

    todo = set()
    grid_of = {}
    for shape, fillers in pooled.items():
        if len(fillers) >= args.min and len(members[shape]) >= args.rows:
            for k in members[shape]:
                if len(row[k]) < 3:
                    todo.add(k)
                    if k not in grid_of or len(pooled[grid_of[k]]) < len(fillers):
                        grid_of[k] = shape
    if args.vectors:
        import numpy as np
        from open_slot_neighbours import load
        vocab, index, mat = load(args.vectors)
        shapes = sorted({grid_of[k] for k in todo})
        near = {}
        for start in range(0, len(shapes), 256):
            chunk = shapes[start:start + 256]
            cent = []
            for sh in chunk:
                ids = [index[f] for f in pooled[sh] if f in index]
                cent.append(mat[ids].mean(axis=0) if ids else np.zeros(mat.shape[1], dtype=mat.dtype))
            cent = np.vstack(cent)
            cent /= np.linalg.norm(cent, axis=1, keepdims=True) + 1e-9
            top = np.argpartition(-(cent @ mat.T), args.per, axis=1)[:, : args.per]
            for sh, r in zip(chunk, top):
                near[sh] = [vocab[j] for j in r]
        print("%s: %d thin rows over %d grids, %d candidates" % (args.game, len(todo), len(shapes),
              len(todo) * args.per), file=sys.stderr)
        out = sys.stdout
        for key in sorted(todo):
            head, tail = key
            seen = row[key]
            out.write("".join(head + w + tail + "\n" for w in near[grid_of[key]] if w not in seen))
        return
    print("%s: %d thin rows of open grids, %d candidates" % (args.game, len(todo), len(todo) * len(words)),
          file=sys.stderr)
    out = sys.stdout
    for head, tail in sorted(todo):
        seen = row[(head, tail)]
        out.write("".join(head + w + tail + "\n" for w in words if w not in seen))


if __name__ == "__main__":
    main()
