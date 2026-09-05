#!/usr/bin/env python3
"""Fill a near-complete terminal-state counterpart in real ``evt_`` aliases.

This is intentionally not a state grid.  It learns only the two terminal
spellings whose same-base pairing is overwhelmingly attested, then emits a
missing side only when the observed pairing is at least 98% complete and has
at least twenty full-name controls.
"""
from collections import defaultdict
from pathlib import Path
import sys

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / "scripts"))
import snapshot

STATES = ("prone", "stand")
MIN_CONTROLS = 20
MIN_COMPLETENESS = 0.98


def split_state(name: str):
    for state in STATES:
        marker = "_" + state
        if name.startswith("evt_") and name.endswith(marker):
            return name[:-len(marker)], state
    return None


def main() -> None:
    known = {
        name.strip().lower().replace("\\", "/")
        for name in snapshot.table_names("fnv1a_soundbanks_aliases")
        if name.strip()
    }
    known.update(
        name.strip().lower().replace("\\", "/")
        for name in snapshot.confirmed_names("sound_alias")
        if name.strip()
    )
    bases = defaultdict(set)
    for name in known:
        pair = split_state(name)
        if pair:
            base, state = pair
            bases[base].add(state)
    observed = [states for states in bases.values() if states]
    controls = sum(len(states) for states in observed if len(states) == len(STATES))
    complete = sum(1 for states in observed if len(states) == len(STATES))
    if controls < MIN_CONTROLS or complete / len(observed) < MIN_COMPLETENESS:
        return
    candidates = {
        f"{base}_{state}"
        for base, states in bases.items()
        if len(states) == 1
        for state in STATES
        if state not in states
    }
    print("\n".join(sorted(candidates)))


if __name__ == "__main__":
    main()
