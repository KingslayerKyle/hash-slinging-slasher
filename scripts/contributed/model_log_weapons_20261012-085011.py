"""Weapon codes from the BO7 model-name list, run through the weapon-slot plan.

contrib/weapon_slot_plan.py measured its 258 `<class>_<name>` weapons on names known at the time,
before most BO7 weapons had a single named asset. The model list (contrib/model_log_stems.py
writes contrib/modellog_names.txt) names every weapon model: `wpn_sat_ar_hawk_...`,
`sat_sh_corso_...`, `sat_lm_hades_...`. Any `<class>_<name>` seen in 3+ model names that the
weapon-slot list lacks goes into the plan, with weapon_slot's own measured beginnings and endings.
Map junk like `lm_rock`/`me_wall` comes along. It costs little and cannot match by meaning.

    python contrib/model_log_weapons.py
    confirm_plan contrib/modellog_weapons.plan.txt --game BLACKOP7
"""
from pathlib import Path
import collections
import re

ROOT = Path(__file__).resolve().parent
while not (ROOT / "scripts" / "snapshot.py").is_file() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
CONTRIB = ROOT / "contrib"
CODE = re.compile(r"(?:^|_)((?:ar|sm|sh|sn|lm|pi|la|me|dm|br|mr)_[a-z]+[0-9]*)")


def main():
    names = (CONTRIB / "modellog_names.txt").read_text(encoding="utf-8").split()
    seen = collections.Counter(code for n in names for code in set(CODE.findall(n)))
    known = set((CONTRIB / "weapon_slot_weapons.txt").read_text(encoding="utf-8").split())
    new = sorted(c for c, k in seen.items() if k >= 3 and c not in known)
    (CONTRIB / "modellog_weapons.txt").write_text("\n".join(new) + "\n", encoding="utf-8")
    (CONTRIB / "modellog_weapons.plan.txt").write_text(
        "label: weapon-slot plan over weapon codes from BO7 model names\n"
        "describe: <class>_<name> codes seen in 3+ BO7 model names and missing from weapon_slot_weapons.txt "
        "(contrib/model_log_weapons.py), between weapon_slot's measured beginnings and endings\n"
        "begin: @contrib/weapon_slot_begins.txt\n"
        "stem: @contrib/modellog_weapons.txt\n"
        "end: @contrib/weapon_slot_ends.txt\n", encoding="utf-8")
    print(f"{len(new)} new weapon codes")


if __name__ == "__main__":
    main()
