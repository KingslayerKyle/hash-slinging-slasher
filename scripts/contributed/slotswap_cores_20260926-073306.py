"""slotswap.py's context-conditioned substitution, applied to all-boundary core fragments.

`scripts/contributed/slotswap_20260819-225818.py` (method 10) measures, for every token slot in
every known name, what other tokens the corpus has seen filling a slot with the same left/right
neighbours -- then substitutes only inside WHOLE known names. That is the same restriction
`rule_substituted_cores.py` found and removed for `coordinated_identifiers.py` two days ago: the
context vocabulary slotswap learns is a fact about what token belongs next to what neighbour, and
that fact does not stop being true just because the place it is being applied is a fragment rather
than a complete name.

This measures the identical slot alphabet slotswap does (unchanged: neighbours with digits folded
to `#`, `--cap`/`--min-seen`/`--min-alt` defaults), then walks every ALL-BOUNDARY CORE (method 25)
and substitutes at every INTERIOR slot -- every token except the last, since the last token sits at
the core's own cut boundary and is exactly what the ending half of the cross product already
varies; touching it here would just be a worse-informed version of the ending sweep. Keeps only
substituted cores not already in the base all-boundary list, then crosses the new fragments against
the standing wide ending lists with the plan engine, the same shape as rule_substituted_cores.py.

    python contrib/slotswap_cores.py                reuses contrib/ab_cores.txt
    python contrib/slotswap_cores.py --sound-pass    reuses contrib/ab_sound_cores.txt
"""
from pathlib import Path
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parent
while not (ROOT / "scripts" / "snapshot.py").is_file() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
sys.path.insert(0, str(ROOT / "scripts"))
import snapshot

BOUNDARY = "_/"

THIS_ERA = [
    "fnv1a_xmodels", "fnv1a_xmaterials", "fnv1a_ximages", "fnv1a_xanims",
    "fnv1a_xsounds", "fnv1a_soundbanks_aliases", "fnv1a_strings",
] + ["fnv1a_%s_xsounds" % language for language in (
    "english french german italian spanish americanspanish brazilianportugese "
    "russian polish japanese korean chinese"
).split()]


def split(name):
    tokens, current = [], ""
    for character in name:
        if character in BOUNDARY:
            tokens.append((current, character))
            current = ""
        else:
            current += character
    tokens.append((current, ""))
    return tokens


def shape(token):
    out, in_run = [], False
    for character in token:
        if character.isdigit():
            if not in_run:
                out.append("#")
                in_run = True
        else:
            out.append(character)
            in_run = False
    return "".join(out)


def context_of(texts, index):
    before = shape(texts[index - 1]) if index else "^"
    after = shape(texts[index + 1]) if index + 1 < len(texts) else "$"
    return (before, after)


def measure_offers(names, cap=12, min_seen=4, min_alt=2, max_tokens=16):
    import collections
    alphabet = collections.defaultdict(collections.Counter)
    for name in names:
        tokens = split(name)
        if len(tokens) > max_tokens:
            continue
        texts = [text for text, _ in tokens]
        for index, text in enumerate(texts):
            if text:
                alphabet[context_of(texts, index)][text] += 1
    offers = {}
    for key, counter in alphabet.items():
        if sum(counter.values()) < min_seen:
            continue
        chosen = [text for text, count in counter.most_common(cap) if count >= min_alt]
        if len(chosen) > 1:
            offers[key] = chosen
    return offers


def substituted_cores(core, offers, max_tokens=16):
    tokens = split(core)
    if len(tokens) > max_tokens or len(tokens) < 2:
        return set()
    texts = [text for text, _ in tokens]
    marks = [mark for _, mark in tokens]
    out = set()
    # Every slot except the last: the last sits at the core's own cut point, which the
    # ending half of the cross product already varies.
    for index in range(len(texts) - 1):
        text = texts[index]
        if not text or text.isdigit():
            continue
        chosen = offers.get(context_of(texts, index))
        if not chosen:
            continue
        head = "".join(t + m for t, m in zip(texts[:index], marks[:index]))
        tail = "".join(t + m for t, m in zip(texts[index + 1:], marks[index + 1:]))
        for other in chosen:
            if other != text:
                out.add(head + other + marks[index] + tail)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--sound-pass", action="store_true")
    args = ap.parse_args()

    stem = "sound_" if args.sound_pass else ""
    base_cores_path = ROOT / "contrib" / f"ab_{stem}cores.txt"
    base_cores = {line.strip() for line in base_cores_path.read_text(encoding="utf-8").splitlines()
                  if line.strip()}

    names = snapshot.table_names(*THIS_ERA) + snapshot.confirmed_names()
    names = [n.strip().lower().replace("\\", "/") for n in names if n.strip()]
    offers = measure_offers(names)

    new_cores = set()
    for core in base_cores:
        new_cores |= substituted_cores(core, offers)
    new_cores -= base_cores

    out_path = ROOT / "contrib" / f"slotswap_{stem}cores_new.txt"
    out_path.write_text("\n".join(sorted(new_cores)) + "\n", encoding="utf-8")

    result = dict(known_names=len(names), slot_contexts=len(offers),
                  base_cores=len(base_cores), new_cores=len(new_cores))
    print(json.dumps(result, indent=2), file=sys.stderr)
    Path(str(out_path) + ".json").write_text(json.dumps(result, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
