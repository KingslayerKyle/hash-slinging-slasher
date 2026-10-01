r"""Each word of a known name, misspelt the ways people misspell -- and respelt UK <-> US.

Same reasoning as `token_abbrev.py` and `token_inflect.py` (2026-10-01): the unnamed names hold
tokens nobody has seen, and a token nobody has seen is often a variant spelling of one everybody
has. Asset names are typed by hand, by artists on two continents: the published tables already hold
`licence` beside `license`, `armour` beside `armor`, and a typo committed once is the asset's
name for ever.

Every alphabetic token of four or more letters in every name the game is known to hold is replaced,
one at a time, by

    - each adjacent transposition       (recieve <- receive)
    - each single-letter deletion       (enviroment <- environment)
    - each single-letter doubling       (pannel <- panel)
    - UK <-> US respellings             (-our/-or, -ise/-ize, -yse/-yze, -re/-er, -ll-/-l-, grey/gray)

    python contrib/token_typos.py --game BLKOPSCW | bin\windows\confirm_list.exe - \
        --game BLKOPSCW --label "token misspellings and UK/US respellings" --script contrib/token_typos.py
"""
import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import token_markov  # noqa: E402

POOLS = ("xmodel", "image", "material", "xanim", "sound_alias")
ALPHA = re.compile(r"^[a-z]{4,}$")
SWAPS = (("our", "or"), ("ise", "ize"), ("ised", "ized"), ("ising", "izing"), ("isation", "ization"),
         ("yse", "yze"), ("tre", "ter"), ("bre", "ber"), ("lled", "led"), ("lling", "ling"),
         ("ller", "ler"), ("grey", "gray"), ("ence", "ense"), ("ogue", "og"), ("aluminium", "aluminum"),
         ("tyre", "tire"), ("kerb", "curb"), ("plough", "plow"), ("mould", "mold"))


def variants(w):
    out = set()
    for i in range(len(w) - 1):
        if w[i] != w[i + 1]:
            out.add(w[:i] + w[i + 1] + w[i] + w[i + 2:])
    for i in range(len(w)):
        out.add(w[:i] + w[i + 1:])
        out.add(w[:i] + w[i] + w[i:])
    for a, b in SWAPS:
        for x, y in ((a, b), (b, a)):
            if x in w:
                out.add(w.replace(x, y))
    out.discard(w)
    return {v for v in out if len(v) >= 3}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--game", required=True)
    args = ap.parse_args()

    known = set()
    for pool in POOLS:
        names, _ = token_markov.present(args.game, pool)
        known |= names
    cache = {}
    out = sys.stdout
    count = 0
    for name in known:
        parts = re.split(r"([_/])", name)
        for i in range(0, len(parts), 2):
            tok = parts[i]
            if not ALPHA.match(tok):
                continue
            subs = cache.get(tok)
            if subs is None:
                subs = cache[tok] = variants(tok)
            head, tail = "".join(parts[:i]), "".join(parts[i + 1:])
            block = [head + s + tail for s in subs]
            out.write("".join(c + "\n" for c in block if c not in known))
            count += len(block)
    print("%s: about %d candidates" % (args.game, count), file=sys.stderr)


if __name__ == "__main__":
    main()
