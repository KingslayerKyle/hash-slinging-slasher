"""Two-slot slotswap over modern sound aliases: substitute two different token slots at once.

Modern aliases are multi-axis grids -- `stance_<gear>_<who>_<transition>_<part>`,
`melee_<weapon>_<action>_<who>`, `wfoly_<weapon>_<action>_<part>`. Single-slot slotswap reaches a
missing cell only when a known name differs from it in exactly one slot; a cell that differs from
every known name in two slots (a new gear class *and* a new transition) needs both changed at once.

The slot alphabet is measured on aliases alone (slotswap_cores.measure_offers, same contexts), so
the offers are alias vocabulary rather than the whole corpus'. --cap bounds each slot's offers;
the cost per seed is about (slots choose 2) x cap^2.

    python contrib/alias_slotswap2.py --cap 8 | confirm_list - --game BLACKOP6 --script contrib/alias_slotswap2.py
"""
from pathlib import Path
import argparse
import itertools
import sys
import importlib.util

ROOT = Path(__file__).resolve().parent
while not (ROOT / "scripts" / "snapshot.py").is_file() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
sys.path.insert(0, str(ROOT / "scripts"))


def _companion(name, filename):
    """Load the reviewed, versioned companion shipped with this repository."""
    spec = importlib.util.spec_from_file_location(
        name, ROOT / "scripts" / "contributed" / filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

sc = _companion("slotswap_cores", "slotswap_cores_20260926-073306.py")
_aliases = _companion("alias_segments", "alias_segments_20261008-205512.py")
known_aliases = _aliases.known_aliases


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cap", type=int, default=8)
    ap.add_argument("--max-tokens", type=int, default=9)
    a = ap.parse_args()
    corpus = sorted({x for x in known_aliases() if x and "/" not in x and "." not in x})
    offers = sc.measure_offers(corpus, cap=a.cap)
    known = set(corpus)
    out = sys.stdout
    total = 0
    for name in corpus:
        tokens = sc.split(name)
        if not 3 <= len(tokens) <= a.max_tokens:
            continue
        texts = [t for t, _ in tokens]
        marks = [m for _, m in tokens]
        slots = []
        for i, t in enumerate(texts):
            if t and not t.isdigit():
                alts = [o for o in offers.get(sc.context_of(texts, i), ()) if o != t]
                if alts:
                    slots.append((i, alts))
        batch = set()
        for (i, ai), (j, aj) in itertools.combinations(slots, 2):
            for x in ai:
                for y in aj:
                    t2 = list(texts)
                    t2[i], t2[j] = x, y
                    batch.add("".join(t + m for t, m in zip(t2, marks)))
        batch -= known
        total += len(batch)
        out.write("".join(s + "\n" for s in batch))
    print(f"{len(corpus):,} aliases, {len(offers):,} contexts, {total:,} candidates", file=sys.stderr)


if __name__ == "__main__":
    main()
