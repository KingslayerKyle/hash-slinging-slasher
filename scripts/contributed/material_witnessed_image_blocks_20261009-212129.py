"""Transfer jointly witnessed material interior blocks into held image frames.

Only target-held modern material basenames train the substitutions. Two complete
interior blocks of two or three underscore tokens must occur between identical
material prefix/suffix frames on at least three independent basenames. Directory
copies are not independent witnesses. The rule preserves its immediate left and
right anchors and substitutes the complete block in a target-held image. A pair
that differs in only one same-position token is omitted because ordinary slot
substitution already expresses it. No individual token alphabets are crossed.

BO7 measurement, 2026-10-09: 150,888 held materials and 75,053 held images gave
7,604 directed rules, 3,009 eligible source images and 6,801 unique candidates.
Those candidates reproduced 1,497 known image controls and matched 23 unclaimed
image keys after current tables, all-game history/findings and live claim
exclusions. None of the 23 lies in the four earlier byte/pair/numeric image plan
products. The related 2026-08-20 legacy correlated-block method has no retained
generator; this is specifically material-only joint evidence transferred into
image-only application frames, measured on the modern target capture.

The exact product representation has 3,777 mostly one-prefix groups, so emitting
the 6,801 names is more efficient than thousands of separate compiled plans.
Spent by: unchanged held material rule witnesses and held image source frames.

  python contrib/material_witnessed_image_blocks.py --game BLACKOP7 --size
  python contrib/material_witnessed_image_blocks.py --game BLACKOP7 \
      --output logs/material-witnessed-image-blocks.txt
  confirm_list logs/material-witnessed-image-blocks.txt --game BLACKOP7 \
      --script contrib/material_witnessed_image_blocks.py \
      --label "material-witnessed complete interior image blocks"

Select only the image pool in the confirmer. This generator does not confirm,
write findings, change exclusions, or submit. Official confirmation performs the
current exclusions; candidate strings alone are not discoveries.
"""
import argparse
from collections import defaultdict
from itertools import combinations
import json
from pathlib import Path
import sys

ROOT = next((p for p in [Path.cwd(), *Path(__file__).resolve().parents]
             if (p / 'scripts/snapshot.py').is_file()), None)
if ROOT is None:
    raise SystemExit('Run inside a solver checkout')
sys.path.insert(0, str(ROOT / 'scripts'))
import snapshot


def corpus(kind, game):
    table = {'material': 'fnv1a_xmaterials_v2', 'image': 'fnv1a_ximages_v2'}[kind]
    names = set(snapshot.table_names(table))
    for top in ('all_names', 'submissions', 'findings'):
        for path in (ROOT / top).rglob(kind + '*.txt'):
            for row in path.read_text(encoding='utf-8').splitlines():
                raw, sep, name = row.partition(',')
                if not sep or not name:
                    continue
                try:
                    key = int(raw, 16) & snapshot.ID_MASK
                except ValueError:
                    continue
                if snapshot.fnv1a(name, game, kind) & snapshot.ID_MASK == key:
                    names.add(name.strip().lower())
    return {n for n in names if n and n.isascii() and n == n.strip()
            and '\n' not in n and '\r' not in n}


def tokens(name):
    """Exclude terrain blends, packed images and ambiguous non-token syntax."""
    parts = tuple(name.rsplit('/', 1)[-1].split('_'))
    if 5 <= len(parts) <= 16 and all(p and p.isalnum() and p.isascii() for p in parts):
        return parts
    return ()


def cuts(parts):
    for width in (2, 3):
        for pos in range(1, len(parts) - width):
            yield parts[:pos], parts[pos:pos + width], parts[pos + width:]


def learn(materials):
    frames = defaultdict(set)
    for parts in {tokens(n) for n in materials} - {()}:
        for prefix, block, suffix in cuts(parts):
            if any(any(c.isalpha() for c in token) for token in block):
                frames[prefix, suffix].add(block)
    supports = defaultdict(set)
    ambiguous = 0
    for frame, blocks in frames.items():
        # Large unconstrained inventories are not sibling-rule evidence.
        if len(blocks) > 64:
            ambiguous += 1
            continue
        prefix, suffix = frame
        context = prefix[-1], suffix[0]
        for left, right in combinations(sorted(blocks), 2):
            if len(left) == len(right) and sum(a != b for a, b in zip(left, right)) < 2:
                continue
            supports[context, left, right].add(frame)
    rules = defaultdict(set)
    eligible_pairs = 0
    witness_count = 0
    for (context, left, right), witnesses in supports.items():
        if len(witnesses) >= 3:
            rules[context, left].add(right)
            rules[context, right].add(left)
            eligible_pairs += 1
            witness_count += len(witnesses)
    return rules, {'material_frames': len(frames), 'ambiguous_frames_skipped': ambiguous,
                   'undirected_block_rules': eligible_pairs,
                   'independent_rule_frame_witnesses': witness_count,
                   'directed_rules': sum(map(len, rules.values()))}


def generate(materials, images):
    rules, report = learn(materials)
    candidates, eligible = set(), set()
    groups = defaultdict(set)
    for image in images:
        # Material directories are intentionally ignored for independent-rule
        # support. Image paths would need a separate path-preserving method.
        if '/' in image or '\\' in image:
            continue
        for prefix, block, suffix in cuts(tokens(image)):
            replacements = rules.get(((prefix[-1], suffix[0]), block))
            if not replacements:
                continue
            eligible.add(image)
            groups[tuple(sorted(replacements)), suffix].add(prefix)
            for replacement in replacements:
                candidates.add('_'.join(prefix + replacement + suffix))
    report.update(eligible_source_images=len(eligible), unique_candidates=len(candidates),
                  exact_plan_groups=len(groups),
                  known_source_image_controls=len(candidates & images))
    return candidates, report


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--game', required=True, choices=sorted(snapshot.MODERN))
    parser.add_argument('--output', type=Path)
    parser.add_argument('--size', action='store_true')
    args = parser.parse_args()
    shot = snapshot.read(ROOT / 'snapshots' / (args.game.lower() + '.ids'))
    if shot.game != args.game:
        raise ValueError('Capture game does not match the requested game')
    pools = shot.by_pool()
    target = {}
    for kind in ('material', 'image'):
        ids = set(pools[kind])
        target[kind] = {n for n in corpus(kind, args.game)
                        if snapshot.fnv1a(n, args.game, kind) & snapshot.ID_MASK in ids}
    candidates, report = generate(target['material'], target['image'])
    report.update(game=args.game, target_materials=len(target['material']),
                  target_images=len(target['image']))
    print(json.dumps(report, sort_keys=True), file=sys.stderr)
    if args.size:
        return
    output = args.output.open('w', encoding='utf-8', newline='\n') if args.output else sys.stdout
    try:
        for name in sorted(candidates):
            output.write('0,' + name + '\n')
    finally:
        if args.output:
            output.close()


if __name__ == '__main__':
    main()
