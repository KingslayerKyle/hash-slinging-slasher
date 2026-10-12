"""Transfer witnessed one-to-two-token interior animation replacements.

Run: python scripts/contributed/witnessed_animation_block_lengths.py --game BLACKOP7 --out logs/animation-block-lengths.txt
Then: bin/windows/confirm_list.exe logs/animation-block-lengths.txt --game BLACKOP7 --script scripts/contributed/witnessed_animation_block_lengths.py --label "witnessed animation block length changes"

Reads source-hash-verified modern animation database names, the selected capture,
and selected-game animation history/findings. Writes a bounded candidate list and
JSON measurement beside it. Confirmation and submission remain separate steps.
Capture and findings folders honor their existing config.toml [paths] overrides.
Reusable after independent source names grow. Rules train only on database names,
never generated descendants, and require three distinct complete sibling pairs
spanning six distinct names. Only ASCII underscore names with 4-18 tokens qualify.
Unlike paired slot substitutions, a rule changes the number of interior tokens.
The immediate left and right anchors must stay unchanged. First and last block
tokens must both change, excluding ordinary single-token insertion/deletion.
Measured on 2026-10-12 from 174,115 independent database seeds and 19,486 directed
rules: BLACKOP7 used 91,815 held seeds, generated 107,071 candidates in 19.5 s,
and confirmed 87 new animations in 1 s. BLACKOP6 used 81,445 held seeds, generated
90,236 candidates in 12.4 s, and confirmed 89 new animations in 1 s. The two runs
share all 87 BO7 hashes and therefore contain 89 unique hashes; deduplicate across
games before submitting. Tables and in-flight claims were excluded by confirm_list.
"""
import argparse
from collections import defaultdict
import hashlib
import itertools
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parent
while ROOT != ROOT.parent and not (ROOT / "scripts/snapshot.py").is_file():
    ROOT = ROOT.parent
if not (ROOT / "scripts/snapshot.py").is_file():
    raise SystemExit("Cannot locate solver scripts/snapshot.py")
sys.path.insert(0, str(ROOT / "scripts"))
import snapshot


def tokens(name):
    row = tuple(name.split("_"))
    if 4 <= len(row) <= 18 and all(token.isascii() and token.isalnum() for token in row):
        return row
    return ()


def cuts(row):
    for width in (1, 2):
        for position in range(1, len(row) - width):
            yield row[:position], row[position:position + width], row[position + width:]


def learn_rules(baseline):
    frames = defaultdict(set)
    for name in sorted(baseline):
        for prefix, block, suffix in cuts(tokens(name)):
            frames[prefix, suffix].add(block)
    supports = defaultdict(set)
    for (prefix, suffix), blocks in frames.items():
        if not 2 <= len(blocks) <= 24:
            continue
        for left, right in itertools.combinations(sorted(blocks), 2):
            if len(left) == len(right) or left[0] == right[0] or left[-1] == right[-1]:
                continue
            witness = ("_".join(prefix + left + suffix), "_".join(prefix + right + suffix))
            supports[(prefix[-1], suffix[0]), left, right].add(witness)
    rules = defaultdict(set)
    for (anchors, left, right), witnesses in supports.items():
        if len(witnesses) >= 3 and len({name for pair in witnesses for name in pair}) >= 6:
            rules[anchors, left].add(right)
            rules[anchors, right].add(left)
    return rules


def held_history(game, held):
    names = set()
    paths = [ROOT / "all_names" / game.lower() / "xanim.txt"]
    findings_root = Path(snapshot.settings.path("findings", "findings"))
    paths.extend((findings_root / game.lower()).rglob("xanim.txt"))
    for path in paths:
        if not path.is_file():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            raw_key, separator, name = line.partition(",")
            if not separator:
                continue
            try:
                key = int(raw_key, 16) & snapshot.ID_MASK
            except ValueError:
                continue
            if key in held and snapshot.fnv1a(name, game, "xanim") & snapshot.ID_MASK == key:
                names.add(name)
    return names


def generate(rules, application, known, limit):
    candidates = set()
    controls = set()
    for name in sorted(application):
        for prefix, block, suffix in cuts(tokens(name)):
            for replacement in rules.get(((prefix[-1], suffix[0]), block), ()):
                candidate = "_".join(prefix + replacement + suffix)
                if candidate in known:
                    controls.add(candidate)
                    continue
                candidates.add(candidate)
                if len(candidates) > limit:
                    raise ValueError("Candidate limit exceeded; narrow the application corpus")
    return candidates, controls


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--game", required=True, choices=sorted(snapshot.MODERN))
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--max-candidates", type=int, default=1000000)
    args = parser.parse_args()
    if args.max_candidates < 1:
        parser.error("--max-candidates must be positive")
    started = time.monotonic()
    baseline = set(snapshot.table_names("fnv1a_xanims_v2"))
    snapshots_root = Path(snapshot.settings.path("snapshots", "snapshots"))
    shot = snapshot.read(snapshots_root / (args.game.lower() + ".ids"))
    if shot.game != args.game:
        parser.error("Selected capture identifies a different game")
    held = {key & snapshot.ID_MASK for key in shot.by_pool()["xanim"]}
    application = {name for name in baseline
                   if snapshot.fnv1a(name, args.game, "xanim") & snapshot.ID_MASK in held}
    application.update(held_history(args.game, held))
    rules = learn_rules(baseline)
    candidates, controls = generate(rules, application, baseline | application, args.max_candidates)
    data = "".join(name + "\n" for name in sorted(candidates)).encode("utf-8")
    report = dict(game=args.game, independent_baseline_names=len(baseline),
                  held_application_names=len(application), directed_rules=sum(map(len, rules.values())),
                  known_reconstruction_controls=len(controls), candidates=len(candidates),
                  candidate_sha256=hashlib.sha256(data).hexdigest(), elapsed_seconds=round(time.monotonic()-started, 3))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_bytes(data)
    args.out.with_suffix(".json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report), flush=True)


if __name__ == "__main__":
    main()
