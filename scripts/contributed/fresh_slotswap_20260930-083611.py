"""Method 10 (sibling token substitution) applied only to names confirmed recently.

Slotswap -- swap one token of a whole known name for the tokens measured to occupy that same slot
elsewhere -- was last run over the whole corpus on 2026-09-03 and is marked spent. Everything this
project has confirmed since has never had it applied, and on 2026-09-30 the measurement behind
`core_rings.py` showed where the value is: a family found days ago whose siblings are still
unnamed. The commonest sibling in these games is one word different in the middle, which is
exactly this substitution.

The slot alphabet is measured over the whole corpus with slotswap_cores.py's own `measure_offers`
(the same caps slotswap uses); substitution is applied at EVERY slot of each seed name, the last
one included, because here the seed is a whole name, not a core with an ending still to come.

    python contrib/fresh_slotswap.py --since 20260925 | bin/windows/confirm_list.exe - \
        --game BLKOPSCW --label "fresh slotswap" --script contrib/fresh_slotswap.py
"""
from pathlib import Path
import argparse
import glob
import re
import sys

ROOT = Path(__file__).resolve().parent
while not (ROOT / "scripts" / "snapshot.py").is_file() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "contrib"))
import snapshot
import slotswap_cores as sc


def recent_names(since, until):
    names = set()
    for game in ("blkopscw", "blkops04"):
        for folder in glob.glob(str(ROOT / "findings" / game / "run_*")):
            match = re.search(r"run_(\d{8})", folder)
            if match and since <= match.group(1) <= until:
                for path in glob.glob(folder + "/*.txt"):
                    with open(path, encoding="utf-8", errors="ignore") as handle:
                        for line in handle:
                            if line.strip():
                                names.add(line.split(",", 1)[-1].strip().lower().replace("\\", "/"))
    return names


def substitutions(name, offers, max_tokens=16):
    tokens = sc.split(name)
    if len(tokens) > max_tokens or len(tokens) < 2:
        return set()
    texts = [text for text, _ in tokens]
    marks = [mark for _, mark in tokens]
    out = set()
    for index, text in enumerate(texts):
        if not text or text.isdigit():
            continue
        chosen = offers.get(sc.context_of(texts, index))
        if not chosen:
            continue
        head = "".join(t + m for t, m in zip(texts[:index], marks[:index]))
        tail = "".join(t + m for t, m in zip(texts[index + 1:], marks[index + 1:]))
        for other in chosen:
            if other != text:
                out.add(head + other + marks[index] + tail)
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--since", default="20260904")
    parser.add_argument("--until", default="99999999")
    parser.add_argument("--cap", type=int, default=12)
    args = parser.parse_args()

    corpus = snapshot.table_names(*sc.THIS_ERA) + snapshot.confirmed_names()
    corpus = [n.strip().lower().replace("\\", "/") for n in corpus if n.strip()]
    offers = sc.measure_offers(corpus, cap=args.cap)
    seeds = recent_names(args.since, args.until)
    out = set()
    for name in seeds:
        out |= substitutions(name, offers)
    print(f"{len(seeds):,} seed names, {len(offers):,} slot contexts, {len(out):,} candidates",
          file=sys.stderr)
    for candidate in sorted(out):
        print(candidate)


if __name__ == "__main__":
    main()
