"""Translate complete image prefix/tail pairs witnessed by original name pairs.

Read an explicit frozen baseline of independently verified, target-held images.
Strip 1..3 leading and 1..2 trailing underscore tokens, preserving a body of
at least three tokens. A translation changes BOTH complete wrappers together,
and requires three distinct original name pairs with different intact bodies.
Pairs sharing an original name cannot count as independent witnesses. Generated
descendants never join the supplied baseline. Prefix/tail alphabets are never
crossed independently, and neither wrapper may be empty.

BO7 2026-10-09: 71,519 frozen images supplied 1,435 translations and 45,192
unseen candidates. Removing exact earlier byte/pair/numeric products left
29,216 candidates and three provisionally unclaimed image keys. Official
confirmation and submission remain necessary. This is distinct from channel
sibling changes and material-to-image wrappers: both sides are image names,
and the image namespace and ending must change together.

  python contrib/verified_image_joint_wrappers.py --game BLACKOP7 \
    --baseline logs/bo7_visual_structure_ideas/wrapper_baseline.txt \
    --exclude-plan-dir contrib/image_stem_byte_suffix_plan/blackop7 \
    --exclude-plan-dir contrib/image_stem_pair_suffix_plan/blackop7 \
    --exclude-file earlier-image-candidates.txt --output candidates.txt

Use confirm_list with only image selected and --script pointing here. Small
irregular translations belong on CPU, not an inflated GPU product. This script
never changes config, confirms, writes findings or submits. Spent by the frozen
baseline and prior spaces; a generated descendant is not new training evidence.
"""
import argparse
from collections import defaultdict, Counter
from itertools import combinations
import hashlib
import json
from pathlib import Path
import sys

ROOT = next((p for p in [Path.cwd(), *Path(__file__).resolve().parents]
             if (p / 'scripts/snapshot.py').is_file()), None)
if ROOT is None:
    raise SystemExit('Run inside a solver checkout')
sys.path.insert(0, str(ROOT / 'scripts'))
import snapshot


def baseline(path, held, game):
    names = set()
    for row in path.read_text(encoding='utf-8').splitlines():
        if not row.strip():
            continue
        key, sep, name = row.partition(',')
        if not sep or not name or name != name.strip().lower() or not name.isascii():
            raise ValueError('Baseline rows must contain a stored key and canonical ASCII name')
        key = int(key, 16) & snapshot.ID_MASK
        actual = snapshot.fnv1a(name, game, 'image') & snapshot.ID_MASK
        if key != actual or actual not in held:
            raise ValueError('Baseline name does not reproduce its key and target image pool')
        names.add(name)
    return names


def learn(images):
    frames, sourcecuts = defaultdict(dict), defaultdict(list)
    for name in sorted(images):
        tokens = tuple(name.split('_'))
        if not 5 <= len(tokens) <= 16 or not all(t.isascii() and t.isalnum() for t in tokens):
            continue
        for left in (1, 2, 3):
            for right in (1, 2):
                if len(tokens) - left - right < 3:
                    continue
                body = tokens[left:-right]
                wrapper = tokens[:left], tokens[-right:]
                frames[body][wrapper] = name
                sourcecuts[wrapper].append((name, body))
    supports = defaultdict(set)
    for wrappers in frames.values():
        if len(wrappers) > 32:
            continue
        for a, b in combinations(sorted(wrappers), 2):
            if a[0] != b[0] and a[1] != b[1]:
                supports[a, b].add(tuple(sorted((wrappers[a], wrappers[b]))))
    rules = {}
    for rule, pairs in supports.items():
        independent, used = set(), set()
        for pair in sorted(pairs):
            if not used.intersection(pair):
                independent.add(pair)
                used.update(pair)
        if len(independent) >= 3:
            rules[rule] = independent
    return rules, sourcecuts, len(frames)


def generate(images):
    rules, sourcecuts, frame_count = learn(images)
    candidates, controls = set(), set()
    for (a, b), pairs in rules.items():
        for source, target in ((a, b), (b, a)):
            for name, body in sourcecuts[source]:
                candidate = '_'.join(target[0] + body + target[1])
                if candidate in images:
                    # A reconstruction does not supply its own evidence.
                    if sum(name not in p and candidate not in p for p in pairs) >= 3:
                        controls.add(candidate)
                else:
                    candidates.add(candidate)
    return candidates, {'target_image_training_names': len(images),
                        'core_frames': frame_count, 'joint_rules': len(rules),
                        'independent_holdout_controls': len(controls),
                        'unseen_candidates_before_prior_exclusion': len(candidates)}


def values(path):
    return {row.partition(',')[2] if ',' in row else row
            for row in path.read_text(encoding='utf-8').splitlines()
            if row and not row.startswith('#')}


def covered(name, plan):
    begins, middles, ends = plan
    # Accept arbitrary literal ending factors, not only underscore endings.
    for cut in range(len(name) + 1):
        if name[cut:] not in ends:
            continue
        for width in {len(m) for m in middles}:
            if cut >= width and name[:cut-width] in begins and name[cut-width:cut] in middles:
                return True
    return False


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument('--game', required=True, choices=sorted(snapshot.MODERN))
    p.add_argument('--baseline', type=Path, required=True)
    p.add_argument('--exclude-plan-dir', type=Path, action='append', default=[])
    p.add_argument('--exclude-file', type=Path, action='append', default=[])
    p.add_argument('--output', type=Path)
    args = p.parse_args()
    capture = snapshot.read(ROOT / 'snapshots' / (args.game.lower() + '.ids'))
    if capture.game != args.game:
        raise ValueError('Capture game differs from requested game')
    images = baseline(args.baseline, set(capture.by_pool()['image']), args.game)
    candidates, report = generate(images)
    inputs = {str(args.baseline): digest(args.baseline)}
    overlaps = Counter()
    for folder in args.exclude_plan_dir:
        paths = [folder / (part + '.txt') for part in ('begin', 'stem', 'end')]
        plan = [values(path) for path in paths]
        plan[2].add('')  # confirm_plan always includes the empty ending.
        removed = {n for n in candidates if covered(n, plan)}
        overlaps[str(folder)] = len(removed)
        candidates.difference_update(removed)
        inputs.update({str(path): digest(path) for path in paths})
    for path in args.exclude_file:
        before = len(candidates)
        candidates.difference_update(values(path))
        overlaps[str(path)] = before - len(candidates)
        inputs[str(path)] = digest(path)
    report.update(game=args.game, prior_overlap=dict(overlaps),
                  residual_candidates=len(candidates), input_sha256=inputs)
    print(json.dumps(report, sort_keys=True), file=sys.stderr)
    output = args.output.open('w', encoding='utf-8', newline='\n') if args.output else sys.stdout
    try:
        for name in sorted(candidates):
            output.write(name + '\n')
    finally:
        if args.output:
            output.close()


if __name__ == '__main__':
    main()
