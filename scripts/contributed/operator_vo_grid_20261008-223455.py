"""Operator voice lines: every known phrase, spoken by every known operator.

`iw9/op/valeria/dx_op_valr_ping_vale_pedo_gotoneontheirkneeshe_opg2.snn.20.48000.english` is
(root `iw9/op/`, operator dir `valeria`, codes `valr`/`vale`, category `ping`, phrase
`pedo_gotoneontheirkneeshe_opg2`). Operators record a shared script: of 13,144 phrases parsed from
the known names, 1,720 are already attested for ten or more operators. So each phrase is offered
to every operator (with that operator's own dir and code pair, as attested) under every tail the
voice lines carry.

    python contrib/operator_vo_grid.py | confirm_list - --game BLACKOP6 --script contrib/operator_vo_grid.py
"""
from pathlib import Path
import collections
import re
import sys
import importlib.util

ROOT = Path(__file__).resolve().parent
while not (ROOT / "scripts" / "snapshot.py").is_file() and ROOT != ROOT.parent:
    ROOT = ROOT.parent


def _companion(name, filename):
    """Load the reviewed, versioned companion shipped with this repository."""
    spec = importlib.util.spec_from_file_location(
        name, ROOT / "scripts" / "contributed" / filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

_sound = _companion("sound_tail_swap", "sound_tail_swap_20261008-205512.py")
all_names = _sound.all_names

RX = re.compile(r"^(.*?/op/)([^/]+)/dx_op_([a-z0-9]+)_([a-z0-9]+)_([a-z0-9]+)_(.+?)"
                r"(\.[a-z]{2,3}\.\d+\.\d+\.[a-z_]+)$")


def main():
    ops, phrases, tails = set(), set(), collections.Counter()
    known = set()
    for name in all_names():
        m = RX.match(name)
        if not m:
            continue
        known.add(name)
        root, d, c1, cat, c2, rest, tail = m.groups()
        ops.add((root, d, c1, c2))
        phrases.add((cat, rest))
        tails[tail] += 1
    tails = [t for t, n in tails.most_common() if n >= 20]
    out = sys.stdout
    total = 0
    for root, d, c1, c2 in sorted(ops):
        for cat, rest in sorted(phrases):
            stem = f"{root}{d}/dx_op_{c1}_{cat}_{c2}_{rest}"
            for t in tails:
                if stem + t not in known:
                    out.write(stem + t + "\n")
                    total += 1
    print(f"{len(ops)} operators, {len(phrases)} phrases, {len(tails)} tails, {total:,} candidates",
          file=sys.stderr)


if __name__ == "__main__":
    main()
