"""The ending-side mirror of rule_substituted_cores.py.

That script applies each `coordinated_identifiers`-learned substitution rule to the ALL-BOUNDARY
CORE list and crosses the new fragments against the standing (unchanged) ending lists -- new
cores, old endings. This is the other half of the same idea: apply the same rules to the ENDING
lists instead, and cross the new endings against the standing (unchanged) core list -- old cores,
new endings. Neither pass subsumes the other; a core and an ending can each independently carry a
rule-eligible token, and the corpus does not say which side a given real name's token sits on.

    python contrib/rule_substituted_endings.py                reuses contrib/ab_cores.txt / ab_ends.txt
    python contrib/rule_substituted_endings.py --sound-pass    reuses the sound equivalents

Then cross with the plan engine, cores unchanged, only the endings new:

    bin\\windows\\confirm_plan.exe plans/rulesub_ends_visual.txt --size
"""
from pathlib import Path
import argparse
import json
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rule_substituted_cores import ROOT, VISUAL_TABLES, SOUND_TABLES, learn_rules, substitute


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--sound-pass", action="store_true")
    args = ap.parse_args()

    stem = "sound_" if args.sound_pass else ""
    tables = SOUND_TABLES if args.sound_pass else VISUAL_TABLES
    base_ends_path = ROOT / "contrib" / f"ab_{stem}ends.txt"
    base_ends = {line.strip() for line in base_ends_path.read_text(encoding="utf-8").splitlines()
                 if line.strip()}

    rules, report = learn_rules(tables)

    new_ends = set()
    for end in base_ends:
        new_ends |= substitute(end, rules)
    new_ends -= base_ends

    out_path = ROOT / "contrib" / f"rulesub_{stem}ends_new.txt"
    out_path.write_text("\n".join(sorted(new_ends)) + "\n", encoding="utf-8")

    result = dict(base_ends=len(base_ends), rule_tokens=len(rules),
                  supported_pairs=sum(map(len, rules.values())) // 2,
                  per_type=report, new_ends=len(new_ends))
    print(json.dumps(result, indent=2), file=sys.stderr)
    Path(str(out_path) + ".json").write_text(json.dumps(result, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
