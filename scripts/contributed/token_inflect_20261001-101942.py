r"""Each word of a known name, re-inflected: plural/singular, -ed, -ing, -er, and back.

Same reasoning as `token_abbrev.py` (2026-10-01): the unnamed names hold tokens the corpus has never
seen, and a token nobody has seen is often a different *form* of one everybody has. The day's word
sweep found `vox_<spk>_mtx_execute_executed` beside `..._execute_terminated` -- and a known
`destroy` is one suffix away from `destroyed`, `destroyer`, `destroying`. Slotswap and token_edits
only move whole tokens the corpus already holds, so none of them can make that step.

Every alphabetic token of three or more letters in every name the game is known to hold is replaced,
one at a time, by its regular inflections and de-inflections (no dictionary check -- the hash is the
check):

    s es ed d ing er r ers ies/y ied  and stripping each of those again

    python contrib/token_inflect.py --game BLKOPSCW | bin\windows\confirm_list.exe - \
        --game BLKOPSCW --label "token inflection" --script contrib/token_inflect.py
"""
import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import token_markov  # noqa: E402

POOLS = ("xmodel", "image", "material", "xanim", "sound_alias")
ALPHA = re.compile(r"^[a-z]{3,}$")
VOWEL = set("aeiou")


def forms(w):
    out = {w + "s", w + "ed", w + "ing", w + "er", w + "ers"}
    if w.endswith("e"):
        out |= {w + "d", w + "r", w + "rs", w[:-1] + "ing"}
    if w.endswith(("s", "x", "z", "ch", "sh")):
        out.add(w + "es")
    if w.endswith("y") and w[-2] not in VOWEL:
        out |= {w[:-1] + "ies", w[:-1] + "ied", w[:-1] + "ier"}
    if len(w) >= 3 and w[-1] not in VOWEL and w[-2] in VOWEL and w[-3] not in VOWEL and w[-1] not in "wxy":
        out |= {w + w[-1] + "ed", w + w[-1] + "ing", w + w[-1] + "er"}
    for suf in ("ies", "ied", "ier"):
        if w.endswith(suf) and len(w) > 4:
            out.add(w[:-3] + "y")
    for suf in ("ers", "ing", "ed", "er", "es", "s", "d", "r"):
        if w.endswith(suf) and len(w) - len(suf) >= 3:
            stem = w[: -len(suf)]
            out.add(stem)
            if suf in ("ing", "ed", "er", "ers"):
                out.add(stem + "e")
                if len(stem) >= 4 and stem[-1] == stem[-2]:
                    out.add(stem[:-1])
    out.discard(w)
    return {f for f in out if ALPHA.match(f)}


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
                subs = cache[tok] = forms(tok)
            head, tail = "".join(parts[:i]), "".join(parts[i + 1:])
            for s in subs:
                cand = head + s + tail
                if cand not in known:
                    out.write(cand + "\n")
                    count += 1
    print("%s: %d candidates" % (args.game, count), file=sys.stderr)


if __name__ == "__main__":
    main()
