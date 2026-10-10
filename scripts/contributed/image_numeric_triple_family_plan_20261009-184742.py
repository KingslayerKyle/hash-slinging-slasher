"""Probe three-digit image-stem fragments in families proven by numeric-pair hits.

Run: python contrib/image_numeric_triple_family_plan.py --game BLACKOP7 --evidence findings/BLACKOP7/run_20261009-183616_plan --pair-plan-dir contrib/image_stem_pair_suffix_plan/blackop7
Size: confirm_plan contrib/image_numeric_triple_family_plan/blackop7/images.plan.txt --game BLACKOP7 --size
Select only image in config.toml before running the plan. Reads verified modern
images, verified community images, a canonical target capture, and hash-verified
image evidence from a productive pair pass. Writes compact lists, a plan, and
measurement.json under contrib. Reusable with a later productive evidence batch.

Families are the first two underscore tokens of evidence names whose proved
pair-plan core ends in two digits. Every evidence row must reproduce its stored
key and exist in this target's image pool. The optional pair-plan directory
checks the exact prior prefix/pair/suffix combination responsible for the hit.
This BO7 evidence had 59 numeric-pair findings: ui_charm 36, cer_ui 11, mtl_jup 6,
li_decor 5, hud_reticle 1; 53 also had three-digit stem endings.

Suffixes retain the reviewed GLOBAL three-sibling-core witness rule, then each
family keeps only suffixes actually held on its own three-digit-stem images.
Requiring three witnesses inside ui_charm itself would discard its unique theme
suffixes and erase the measured signal. Prefixes come from verified names of
these families with three actual trailing stem digits removed; the full prefix,
including any directory, remains intact. Replacements are only complete three-
digit fragments witnessed on target-held images in these families. No invented
alphabet, numeric range, aliases, or models enter the product. The final compact
plan crosses the unions of these measured lists; it also tests suffix-free cores.

BO7 measurement on 2026-10-09: 715 prefixes x 170 witnessed triples x 83 family-
held suffixes, 10,210,200 candidates. 2,148 target names supplied numeric controls.
6,487,908 candidates were beyond the executed width-two plan. This is a targeted
probe, not evidence that untested candidates are real names. Spent at its exact
evidence families and three lists.
"""
import argparse
from collections import Counter, defaultdict
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
while ROOT != ROOT.parent and not (ROOT / 'scripts/snapshot.py').is_file():
    ROOT = ROOT.parent
if not (ROOT / 'scripts/snapshot.py').is_file():
    raise SystemExit('Run from a solver checkout')
sys.path.insert(0, str(ROOT / 'scripts'))
import snapshot


def helper_module():
    path = ROOT / 'scripts/contributed/verified_image_channel_byte_parallel_20261009-132951.py'
    spec = importlib.util.spec_from_file_location('_image_numeric_family_helper', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def family_of(name):
    return '_'.join(name.split('_')[:2])


def list_values(path):
    return {line.strip().partition(',')[2] for line in path.open(encoding='utf-8') if ',' in line}


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--game', required=True, choices=sorted(snapshot.MODERN))
    parser.add_argument('--evidence', required=True, nargs='+', type=Path)
    parser.add_argument('--pair-plan-dir', type=Path)
    args = parser.parse_args()
    shot = snapshot.read(ROOT / 'snapshots' / (args.game.lower() + '.ids'))
    if shot.game != args.game:
        raise SystemExit('Selected capture has the wrong game tag')
    held = set(shot.by_pool()['image'])
    helper = helper_module()
    names = helper.corpus('image', args.game)
    global_tails = helper.target_tails(names, held, args.game)
    prior = None
    if args.pair_plan_dir:
        prior = tuple(list_values(args.pair_plan_dir / (role + '.txt')) for role in ['begin', 'stem', 'end'])
    evidence_names = set()
    for source in args.evidence:
        paths = sorted(source.glob('image*.txt')) if source.is_dir() else [source]
        for path in paths:
            for row in path.open(encoding='utf-8'):
                raw, sep, name = row.strip().partition(',')
                if not sep:
                    continue
                try:
                    key = int(raw, 16) & snapshot.ID_MASK
                except ValueError:
                    continue
                if key in held and snapshot.fnv1a(name, args.game, 'image') & snapshot.ID_MASK == key:
                    evidence_names.add(name)
    evidence, three_evidence = Counter(), Counter()
    for name in evidence_names:
        matches = []
        for _, stem, tail in helper.cuts(name):
            if tail not in global_tails or len(stem) <= 2 or not stem[-2:].isdigit():
                continue
            if prior and (stem[:-2] not in prior[0] or stem[-2:] not in prior[1] or tail not in prior[2]):
                continue
            matches.append(stem)
        if matches:
            evidence[family_of(name)] += 1
        if any(len(stem) > 3 and stem[-3:].isdigit() for stem in matches):
            three_evidence[family_of(name)] += 1
    if not evidence:
        raise SystemExit('No target-verified numeric-pair evidence')
    grouped = defaultdict(set)
    for name in names:
        family = family_of(name)
        if family in evidence:
            grouped[family].add(name)
    beginnings, triples, endings, controls = set(), set(), set(), set()
    family_report = []
    for family, group in sorted(grouped.items()):
        target = {name for name in group if snapshot.fnv1a(name, args.game, 'image') & snapshot.ID_MASK in held}
        tails = {tail for name in target for _, stem, tail in helper.cuts(name)
                 if tail in global_tails and len(stem) > 3 and stem[-3:].isascii() and stem[-3:].isdigit()}
        prefixes, fragments = set(), set()
        for name in group:
            for _, stem, tail in helper.cuts(name):
                if tail not in tails or len(stem) <= 3 or not stem[-3:].isascii() or not stem[-3:].isdigit():
                    continue
                prefixes.add(stem[:-3])
                if name in target:
                    fragments.add(stem[-3:])
                    controls.add(name)
        if prefixes and fragments and tails:
            beginnings.update(prefixes)
            triples.update(fragments)
            endings.update(tails)
        family_report.append({'family': family, 'numeric_pair_evidence': evidence[family],
                              'three_digit_evidence': three_evidence[family], 'prefixes': len(prefixes),
                              'witnessed_triples': len(fragments), 'family_held_suffixes': len(tails)})
    if not beginnings or not triples or not endings:
        raise SystemExit('No witnessed three-digit family vocabulary')
    out = ROOT / 'contrib/image_numeric_triple_family_plan' / args.game.lower()
    out.mkdir(parents=True, exist_ok=True)
    files = {}
    for role, values in [('begin', beginnings), ('stem', triples), ('end', endings)]:
        path = out / (role + '.txt')
        path.write_text(''.join('0,' + value + '\n' for value in sorted(values)), encoding='utf-8')
        files[role] = path.relative_to(ROOT).as_posix()
    plan = out / 'images.plan.txt'
    plan.write_text(
        f'label: {args.game} evidence-family image numeric stem triples\n'
        f'describe: families with verified numeric-pair findings; actual numeric-stem prefixes x {len(triples)} complete target-witnessed three-digit fragments x {len(endings)} family-held suffixes retaining global three-core sibling evidence; image only; generator contrib/image_numeric_triple_family_plan.py\n'
        f'game: {args.game}\nbegin: @{files["begin"]}\nstem: @{files["stem"]}\n'
        f'end: @{files["end"]}\nbare: no\nfold: yes\n', encoding='utf-8')
    candidates = len(beginnings) * len(triples) * (len(endings) + 1)
    overlap = None
    if prior:
        overlapping_cores = sum(prefix + fragment[0] in prior[0] and fragment[1:] in prior[1]
                                for prefix in beginnings for fragment in triples)
        overlap = overlapping_cores * (len(endings & prior[2]) + 1)
    report = {'game': args.game, 'kind': 'image', 'evidence_paths': [str(p) for p in args.evidence],
              'numeric_pair_evidence': sum(evidence.values()), 'families': family_report,
              'verified_image_names': len(names), 'beginnings': len(beginnings),
              'complete_witnessed_numeric_triples': len(triples), 'endings': len(endings),
              'known_target_numeric_controls': len(controls), 'candidates': candidates,
              'overlap_with_executed_width2': overlap,
              'new_beyond_executed_width2': candidates - overlap if overlap is not None else None,
              'input_bytes': sum((ROOT / p).stat().st_size for p in files.values()),
              'required_pool_selection': ['image'], 'plan': plan.relative_to(ROOT).as_posix()}
    (out / 'measurement.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, sort_keys=True))


if __name__ == '__main__':
    main()
