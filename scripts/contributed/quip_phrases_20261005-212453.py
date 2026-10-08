r"""Stream English phrases, chained from web bigrams, onto one voice-line prefix.

For a phrase grid (`phrase_grid.py`) whose every phrase exists for the whole cast, one speaker is
enough to detect a phrase, so the phrase list can be tens of millions long. Cold War's execution
quips (`vox_<spk>_mtx_execute_<phrase>`) are short lines with filler dropped -- `see_hell`,
`close_eyes`, `that_enough`, `just_another_day`, `never_saw_me` -- so each chained phrase is offered
as written and with function words removed.

Phrases are chained from Norvig's web bigram counts (`count_2w.txt`): every bigram among the top
--top2, each followed by its --k3 most frequent continuations (trigrams), and among the top --top4
bigrams, two further steps (4-grams) and optionally a third (--five). Phrases in --skip files (already
probed) are not printed.

    python contrib/quip_phrases.py --bigrams count_2w.txt --head vox_adlr_mtx_execute_ \
        | bin\windows\confirm_list.exe - --game BLKOPSCW --label "execution quips, deep phrases" ...
"""
import argparse
import collections
import re
import sys

W = re.compile(r"^[a-z]{2,}$|^[ai]$")
STOP = set("a an the you your youre i im me my mine we our us it its is are was were be been to of in "
           "on at for with and or but so this that thats there theres here will would can could do does "
           "did dont just very really s t ll ve re d m".split())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bigrams", required=True)
    ap.add_argument("--head", required=True)
    ap.add_argument("--top2", type=int, default=286000)
    ap.add_argument("--k3", type=int, default=60)
    ap.add_argument("--top4", type=int, default=120000)
    ap.add_argument("--k4", type=int, default=20)
    ap.add_argument("--five", type=int, default=0, help="also 5-word chains from the top N bigrams")
    ap.add_argument("--skip", nargs="*", default=[])
    args = ap.parse_args()

    big = collections.Counter()
    with open(args.bigrams, encoding="utf-8", errors="replace") as handle:
        for line in handle:
            k, _, n = line.rstrip("\n").partition("\t")
            p = [x.lower().replace("'", "") for x in k.split()]
            if len(p) == 2 and all(W.match(x) for x in p):
                big[(p[0], p[1])] += int(n)
    nxt = collections.defaultdict(list)
    for (a, b), _ in big.most_common():
        if len(nxt[a]) < max(args.k3, args.k4):
            nxt[a].append(b)
    skip = set()
    for path in args.skip:
        with open(path, encoding="utf-8") as handle:
            skip |= {line.strip() for line in handle}
    seen = set()
    out = sys.stdout
    count = 0

    def emit(seq):
        nonlocal count
        for phrase in ("_".join(seq), "_".join(w for w in seq if w not in STOP)):
            if phrase and phrase not in seen and phrase not in skip:
                seen.add(phrase)
                out.write(args.head + phrase + "\n")
                count += 1

    ranked = big.most_common(args.top2)
    for (a, b), _ in ranked:
        emit([a, b])
        for c in nxt.get(b, ())[: args.k3]:
            emit([a, b, c])
    for (a, b), _ in ranked[: args.top4]:
        for c in nxt.get(b, ())[: args.k4]:
            for e in nxt.get(c, ())[: args.k4]:
                emit([a, b, c, e])
    for (a, b), _ in ranked[: args.five]:
        for c in nxt.get(b, ())[:8]:
            for e in nxt.get(c, ())[:8]:
                for f in nxt.get(e, ())[:8]:
                    emit([a, b, c, e, f])
    print("%d phrases" % count, file=sys.stderr)


if __name__ == "__main__":
    main()
