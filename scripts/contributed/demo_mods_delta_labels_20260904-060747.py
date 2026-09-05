#!/usr/bin/env python3
"""Emit demo-mod literals absent from every already-mined BO4/CW source tree."""
from pathlib import Path
import importlib.util


ROOT = Path.cwd()
SOURCE = ROOT / "contrib" / "t9_src_delta_literals_20260904.py"


def load_collector():
    spec = importlib.util.spec_from_file_location("t9_literals", SOURCE)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module.collect


def main() -> None:
    collect = load_collector()
    prior_roots = (
        "bocw-source", "t9-src", "ColdWarGSCMenu", "coldwar.gsc", "cwmenu",
        "ColdWar-Lucy-Base", "bo4-source", "t8-src", "BO4-BlackoutBots",
        "bo4-lucy-menu", "BO4-BlackOps4ShieldMenu", "BlackoutBotsBO4",
        "Abomination-Unofficial", "Synergy-BO4-GSC-Menu", "t8-tests",
        "Shield-Menu-BO4", "bo4-pap-mod",
    )
    prior = set()
    for directory in prior_roots:
        prior |= collect(ROOT / "borrowed" / directory)
    print("\n".join(sorted(collect(ROOT / "borrowed" / "demo_mods") - prior)))


if __name__ == "__main__":
    main()
