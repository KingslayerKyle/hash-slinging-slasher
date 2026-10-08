r"""Each word of a known name, abbreviated the ways artists abbreviate -- and expanded back.

The 2026-10-01 holdout measurement (`token_markov.py --holdout`) says the unnamed remainder is made
of tokens the corpus has never seen: a trigram model of the named set regenerates 56% of held-out
known names and 0 unnamed ones. A token nobody has seen can still be a *spelling* of one everybody
has: `concrete` is also `conc` and `cncrt`, `damaged` is `dmg`, `window` is `wndw`, and one asset
set routinely ships both spellings. Nothing here produces those: slotswap and token_edits only
move whole tokens the corpus already holds.

For every name the game is known to hold, each alphabetic token of four or more letters is
replaced, one at a time, by

    - its truncations to 2..len-1 letters                  concrete -> co, con, conc, ... concret
    - its consonant skeleton (first letter kept)           concrete -> cncrt, and that truncated to 3-4
    - its doubled-letter collapse                          spotted  -> spoted

and each short token (2-4 letters) by the --expand most frequent corpus tokens it is a prefix of
(`conc` -> `concrete`, `concealed`): the same relation run the other way.

    python contrib/token_abbrev.py --game BLKOPSCW | bin\windows\confirm_list.exe - \
        --game BLKOPSCW --label "token abbreviation and expansion" --script contrib/token_abbrev.py
"""
import argparse
import collections
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import token_markov  # noqa: E402

POOLS = ("xmodel", "image", "material", "xanim", "sound_alias")
ALPHA = re.compile(r"^[a-z]+$")


def skeleton(word):
    return word[0] + re.sub(r"[aeiou]", "", word[1:])


def variants(word):
    out = set()
    if len(word) >= 4:
        for n in range(2, len(word)):
            out.add(word[:n])
        sk = skeleton(word)
        if 2 <= len(sk) < len(word):
            out.add(sk)
            for n in (3, 4):
                if n < len(sk):
                    out.add(sk[:n])
        collapsed = re.sub(r"(.)\1", r"\1", word)
        if collapsed != word:
            out.add(collapsed)
    out.discard(word)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--game", required=True)
    ap.add_argument("--expand", type=int, default=8)
    args = ap.parse_args()

    known = set()
    for pool in POOLS:
        names, _ = token_markov.present(args.game, pool)
        known |= names
    freq = collections.Counter(t for n in known for t in re.split(r"[_/]", n) if ALPHA.match(t))
    by_prefix = collections.defaultdict(list)
    for tok, _ in freq.most_common():
        if len(tok) >= 5:
            for n in range(2, 5):
                lst = by_prefix[tok[:n]]
                if len(lst) < args.expand:
                    lst.append(tok)

    cache = {}
    out = sys.stdout
    count = 0
    for name in known:
        parts = re.split(r"([_/])", name)
        for i in range(0, len(parts), 2):
            tok = parts[i]
            if not ALPHA.match(tok or "0"):
                continue
            subs = cache.get(tok)
            if subs is None:
                subs = variants(tok)
                if 2 <= len(tok) <= 4:
                    subs.update(t for t in by_prefix.get(tok, ()) if t != tok)
                cache[tok] = subs
            if not subs:
                continue
            head, tail = "".join(parts[:i]), "".join(parts[i + 1:])
            for s in subs:
                cand = head + s + tail
                if cand not in known:
                    out.write(cand + "\n")
                    count += 1
    print("%s: %d known names, %d candidates (with repeats)" % (args.game, len(known), count), file=sys.stderr)


if __name__ == "__main__":
    main()
