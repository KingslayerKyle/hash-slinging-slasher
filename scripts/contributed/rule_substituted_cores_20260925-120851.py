"""All-boundary cores, each also offered with every learned sibling-token substitution applied.

`coordinated_identifiers.py` (scripts/contributed/coordinated_identifiers_20260922-122153.py)
learns, per asset type, that a token filling a repeated slot in one name is interchangeable with a
different token filling the identical masked template in another name -- then only ever applies
that rule back onto WHOLE names that already contain the token repeated. That is close to the
tightest possible use of a rule this precise: learned from real sibling evidence, applied only to
reproduce or extend real sibling names.

But the rule asserts something looser and more useful than that: token A and token B are the same
KIND of thing in this game's naming (a faction code, a camo colour, an operator name) wherever
either one appears -- not only inside a name that happens to repeat it. This applies each learned
rule to every ALL-BOUNDARY CORE (method 25: a known name cut at every segment boundary, not the
depth-matched ending-sized cut) that carries the token anywhere, repeated or not, and writes the
substituted cores that are NOT already in the base all-boundary core list -- the incremental ground
this adds, since the base cores against these same endings are stale ground this session already
measured today. Cross the result against the standard ending lists with the plan engine:

    bin\\windows\\confirm_plan.exe plans/rulesub.txt --size
    bin\\windows\\confirm_plan.exe plans/rulesub.txt

Rules are learned separately per type (xmodel, material, image, xanim for the visual pass;
sound_asset, sound_alias for the sound pass) because a fresh cross-type pooling test the same day
found the per-type template-matching evidence never transfers -- learning across types produced
zero cross-kind-supported rules. What IS pooled here, deliberately, is the application side: once a
rule exists, it is applied to the whole visual (or sound) core pool at once, since a core is already
a type-agnostic fragment in every other all-boundary run in this project, and there is no evidence
requirement being violated by trying a material-learned camo-colour swap on a core cut from an
image name.

    python contrib/rule_substituted_cores.py                reuses contrib/ab_cores.txt / ab_ends.txt
    python contrib/rule_substituted_cores.py --sound-pass    reuses the sound equivalents
"""
from pathlib import Path
from collections import Counter, defaultdict
import argparse
import itertools
import json
import re
import sys

ROOT = Path(__file__).resolve().parent
while not (ROOT / "scripts" / "snapshot.py").is_file() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
sys.path.insert(0, str(ROOT / "scripts"))
import snapshot

VISUAL_TABLES = {"xmodel": "fnv1a_xmodels", "material": "fnv1a_xmaterials", "image": "fnv1a_ximages",
                 "xanim": "fnv1a_xanims"}
SOUND_TABLES = {"sound_asset": "fnv1a_xsounds", "sound_alias": "fnv1a_soundbanks_aliases"}


def learn_rules(tables):
    """Rules unioned across every type in `tables`, each learned from that type alone."""
    rules = defaultdict(set)
    report = {}
    for kind, table in tables.items():
        known = {n.strip().lower() for n in itertools.chain(
            snapshot.table_names(table), snapshot.confirmed_names(kind)) if n.strip()}
        groups = defaultdict(set)
        for name in known:
            parts = re.split(r"([^a-z0-9]+)", name)
            repeated = [t for t, count in Counter(parts[::2]).items()
                        if count >= 2 and len(t) >= 2 and not t.isdigit()]
            for token in repeated:
                template = tuple("" if i % 2 == 0 and p == token else p for i, p in enumerate(parts))
                groups[template].add(token)
        support = Counter()
        for values in groups.values():
            if 2 <= len(values) <= 100:
                support.update(itertools.combinations(sorted(values), 2))
        kind_rules = 0
        for (a, b), count in support.items():
            if count >= 2:
                rules[a].add(b)
                rules[b].add(a)
                kind_rules += 1
        report[kind] = dict(seeds=len(known), rule_pairs=kind_rules)
    return rules, report


def substitute(core, rules):
    """Every core with one rule-eligible token swapped for each of its learned partners."""
    parts = re.split(r"([^a-z0-9]+)", core)
    tokens = set(parts[::2])
    out = set()
    for token in tokens:
        if len(token) < 2 or token.isdigit() or token not in rules:
            continue
        for other in rules[token]:
            out.add("".join(other if i % 2 == 0 and p == token else p for i, p in enumerate(parts)))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--sound-pass", action="store_true")
    args = ap.parse_args()

    stem = "sound_" if args.sound_pass else ""
    tables = SOUND_TABLES if args.sound_pass else VISUAL_TABLES
    base_cores_path = ROOT / "contrib" / f"ab_{stem}cores.txt"
    base_cores = {line.strip() for line in base_cores_path.read_text(encoding="utf-8").splitlines()
                  if line.strip()}

    rules, report = learn_rules(tables)

    new_cores = set()
    for core in base_cores:
        new_cores |= substitute(core, rules)
    new_cores -= base_cores

    out_path = ROOT / "contrib" / f"rulesub_{stem}cores_new.txt"
    out_path.write_text("\n".join(sorted(new_cores)) + "\n", encoding="utf-8")

    result = dict(base_cores=len(base_cores), rule_tokens=len(rules),
                  supported_pairs=sum(map(len, rules.values())) // 2,
                  per_type=report, new_cores=len(new_cores))
    print(json.dumps(result, indent=2), file=sys.stderr)
    Path(str(out_path) + ".json").write_text(json.dumps(result, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
