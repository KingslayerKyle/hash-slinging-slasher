r"""Slots that hold alphanumeric codes, offered every alphanumeric code the corpus knows.

The word-slot methods (`open_slot_words.py` and its neighbours) only consider slots filled with
letters; `open_slot_codes.py` brute-forces short codes of up to three characters. Between them sits
a class neither reaches: codes of three to eight characters mixing letters and digits -- weapon and
model designations (`mp5`, `ak47`, `m1911`, `rpk74`), map and variant codes (`zm6`, `t8`, `p9`).
A slot that holds several of them is an open class of designations, and its unseen members are
designations used somewhere else.

A frame is an exact known prefix and suffix around one token; it qualifies when its slot holds at
least --min distinct alphanumeric codes (a letter and a digit each). The vocabulary is every such
token of 2-8 characters in any published or confirmed name of any title, commonest first.

    python contrib/open_slot_alnum.py --game BLKOPSCW | bin\windows\confirm_list.exe - \
        --game BLKOPSCW --label "alphanumeric code slots" --script contrib/open_slot_alnum.py
"""
import argparse
import collections
import glob
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import token_markov  # noqa: E402

POOLS = ("xmodel", "image", "material", "xanim", "sound_alias")
CODE = re.compile(r"^(?=.*[a-z])(?=.*\d)[a-z0-9]{2,8}$")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--game", required=True)
    ap.add_argument("--min", type=int, default=4)
    ap.add_argument("--codes", type=int, default=30000)
    ap.add_argument("--count", action="store_true")
    args = ap.parse_args()

    snapshot = token_markov.snapshot
    counts = collections.Counter()
    for path in glob.glob(os.path.join(snapshot.settings.tables_csv(), "*.csv")):
        with open(path, encoding="utf-8", errors="replace") as handle:
            for line in handle:
                _, _, name = line.partition(",")
                for t in re.split(r"[_/\\.]", name.strip().lower()):
                    if CODE.match(t):
                        counts[t] += 1
    for name in snapshot.confirmed_names():
        for t in re.split(r"[_/\\.]", name.lower()):
            if CODE.match(t):
                counts[t] += 1
    codes = [c for c, _ in counts.most_common(args.codes)]

    frames = collections.defaultdict(set)
    for pool in POOLS:
        names, _ = token_markov.present(args.game, pool)
        for name in names:
            toks = name.split("_")
            for i, tok in enumerate(toks):
                if CODE.match(tok):
                    head = "_".join(toks[:i]) + "_" if i else ""
                    tail = "_" + "_".join(toks[i + 1:]) if i < len(toks) - 1 else ""
                    frames[(head, tail)].add(tok)
    kept = [k for k, v in frames.items() if len(v) >= args.min]
    print("%s: %d code frames, %d codes, %d candidates" % (args.game, len(kept), len(codes),
          len(kept) * len(codes)), file=sys.stderr)
    if args.count:
        return
    out = sys.stdout
    for head, tail in sorted(kept):
        seen = frames[(head, tail)]
        out.write("".join(head + c + tail + "\n" for c in codes if c not in seen))


if __name__ == "__main__":
    main()
