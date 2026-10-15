"""Carry a verified published image-source delta through frozen stem-pair factors.

Run from the repository (references may be pinned full commit IDs):
  python contrib/published_image_pair_source_delta.py --game BLACKOP7 \
    --old-table-rev e547b93 --new-table-rev 3d42c00 \
    --base-plan-dir contrib/image_stem_pair_suffix_plan/blackop7 \
    --exclude-plan-dir contrib/image_stem_pair_prefix_delta_plan/blackop7 \
    --exclude-plan-dir logs/bo7_visual_recon/prefix120_pair_delta \
    --output-dir contrib/published_image_pair_source_delta/blackop7

Reads the two cod-name-db Git versions through the shared verified database
reader, the target image capture, verified image history, and every explicitly
supplied earlier pair plan. Writes compact factors, provenance and a plan; no
settings or findings change. Reusable only when independently source-verified
names add prefixes outside the UNION of all executed beginning sets. A larger
or re-ranked character alphabet is not a source delta. Every prior plan must
have identical middle/end factors, which are copied without expansion.

Prefixes from a modern image table are borrowed modern image vocabulary;
only the separately reported target-held subset is claimed as target evidence.
The frozen complete pairs retain target-held witnesses, and frozen suffixes
retain their three distinct sibling-core witnesses. This adds application
vocabulary; generated descendants do not train new rules.

2026-10-15 BO7: e547b93 -> 3d42c00 adds 33,469 verified image spellings.
Removing all 63,458 earlier prefixes leaves 14,562, including 4,101 with a
target-held source. The frozen 677 pairs and 5,306 suffixes give 52,318,921,518
cells including the engine's empty ending, with 7,724 known target controls
from the current verified table and name history (7,391 from the table alone).
This is a factor-space measurement, not a claim of discoveries. Select only
image in the official confirmer; root coordinates confirmation and submission.
"""
import argparse
from collections import defaultdict
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

ROOT = next((p for p in [Path.cwd(), *Path(__file__).resolve().parents]
             if (p / 'scripts/snapshot.py').is_file()), None)
if ROOT is None:
    raise SystemExit('Run inside a solver checkout')
sys.path.insert(0, str(ROOT / 'scripts'))
import snapshot


def table_checkout():
    """Use the configured table checkout when pinned Git history is required."""
    folder = Path(snapshot.settings.tables_csv()).resolve()
    for candidate in (folder, folder.parent, ROOT / 'cod-name-db'):
        if (candidate / '.git').exists() and (candidate / 'csv').is_dir():
            return candidate
    raise ValueError('Pinned source revisions require a cod-name-db Git checkout; '
                     'configure tables in config.toml and fetch its history first')

TABLE = 'fnv1a_ximages_v2'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def values(path):
    result = set()
    for row in path.read_text(encoding='utf8').splitlines():
        if not row or row.startswith('#'):
            continue
        value = row.partition(',')[2] if ',' in row else row
        if not value or not value.isascii() or value != value.strip().lower():
            raise ValueError('Factors must be nonempty canonical ASCII strings')
        result.add(value)
    if not result:
        raise ValueError('Empty frozen factor list')
    return result


def table_version(ref):
    def git(*args):
        return subprocess.check_output(['git', '-C', str(table_checkout()), *args])
    commit = git('rev-parse', '--verify', ref + '^{commit}').decode('ascii').strip()
    data = git('show', commit + ':csv/' + TABLE + '.csv')
    names = set(snapshot.database_names(TABLE, data.decode('utf8').splitlines()))
    names = {n for n in names if n.isascii() and n == n.strip().lower()}
    return names, {'commit': commit, 'table_sha256': digest(data), 'verified_names': len(names)}


def companion():
    path = ROOT / 'scripts/contributed/verified_image_channel_byte_parallel_20261009-132951.py'
    spec = importlib.util.spec_from_file_location('_published_image_pair_companion', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def delta_prefixes(names, prior, ends, cuts):
    provenance = defaultdict(set)
    for name in names:
        for _, stem, tail in cuts(name):
            if tail in ends and len(stem) > 2 and stem[:-2] not in prior:
                provenance[stem[:-2]].add(name)
    return provenance


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--game', choices=sorted(snapshot.MODERN), required=True)
    parser.add_argument('--old-table-rev', required=True)
    parser.add_argument('--new-table-rev', required=True)
    parser.add_argument('--base-plan-dir', type=Path, required=True)
    parser.add_argument('--exclude-plan-dir', type=Path, action='append', default=[])
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    old, old_info = table_version(args.old_table_rev)
    current, current_info = table_version(args.new_table_rev)
    delta = current - old
    if not delta:
        raise ValueError('No verified published source delta')
    shot = snapshot.read(str(ROOT / 'snapshots' / (args.game.lower() + '.ids')))
    if shot.game != args.game:
        raise ValueError('Capture game differs from requested game')
    held = set(shot.by_pool()['image'])
    helper = companion()
    pairs = values(args.base_plan_dir / 'stem.txt')
    ends = values(args.base_plan_dir / 'end.txt')
    if not all(len(p) == 2 and p[-1].isalnum() for p in pairs):
        raise ValueError('Expected complete two-byte fragments')
    prior, prior_info = set(), []
    prior_dirs = [args.base_plan_dir, *args.exclude_plan_dir]
    for directory in prior_dirs:
        if args.output_dir.resolve() == directory.resolve():
            raise ValueError('Output must not overwrite a prior factor directory')
        if values(directory / 'stem.txt') != pairs or values(directory / 'end.txt') != ends:
            raise ValueError('Excluded plans must have the identical frozen pair and suffix sets')
        beginnings = values(directory / 'begin.txt')
        prior.update(beginnings)
        prior_info.append({'directory': str(directory), 'begin_count': len(beginnings),
                           'sha256': {r: digest((directory / (r + '.txt')).read_bytes())
                                      for r in ('begin', 'stem', 'end')}})
    names = helper.corpus('image', args.game) | current
    target_names = {n for n in names if snapshot.fnv1a(n, args.game, 'image') & snapshot.ID_MASK in held}
    if not ends <= helper.target_tails(target_names, held, args.game):
        raise ValueError('A frozen suffix lacks its three distinct sibling-core witnesses')
    witnessed_pairs = {stem[-2:] for n in target_names for _, stem, tail in helper.cuts(n)
                       if tail in ends and len(stem) > 2}
    if not pairs <= witnessed_pairs:
        raise ValueError('A frozen complete pair lacks a target-held witness')
    provenance = delta_prefixes(delta, prior, ends, helper.cuts)
    beginnings = set(provenance)
    if not beginnings:
        raise ValueError('Every new source beginning is already in the executed union')
    held_delta = delta & target_names
    held_beginnings = {p for p, sources in provenance.items() if sources & held_delta}
    controls = {snapshot.fnv1a(n, args.game, 'image') & snapshot.ID_MASK for n in target_names
                if any(tail in ends and len(stem) > 2 and stem[:-2] in beginnings and stem[-2:] in pairs
                       for _, stem, tail in helper.cuts(n))
                or (len(n) > 2 and n[:-2] in beginnings and n[-2:] in pairs)}
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)
    for role, items in [('begin', beginnings), ('stem', pairs), ('end', ends)]:
        (out / (role + '.txt')).write_text(''.join('0,' + s + '\n' for s in sorted(items)), encoding='utf8')
    (out / 'source_delta.txt').write_text(''.join(n + '\n' for n in sorted(delta)), encoding='utf8')
    (out / 'prefix_provenance.json').write_text(json.dumps({p: sorted(provenance[p]) for p in sorted(provenance)}, indent=2) + '\n', encoding='utf8')
    plan = out / 'images.plan.txt'
    plan.write_text(
        f'label: {args.game} published modern-image source delta under frozen complete pairs\n'
        f'describe: {len(delta)} source-hash-verified new public image names since {old_info["commit"][:8]}; {len(beginnings)} prefixes absent from all {len(prior)} executed prefixes; borrowed modern image vocabulary, {len(held_beginnings)} prefixes have target-held sources; unchanged {len(pairs)} target-witnessed pairs and {len(ends)} three-core sibling suffixes; image only; generator contrib/published_image_pair_source_delta.py\n'
        f'game: {args.game}\nbegin: @{(out / "begin.txt").as_posix()}\nstem: @{(out / "stem.txt").as_posix()}\n'
        f'end: @{(out / "end.txt").as_posix()}\nbare: no\nfold: yes\n', encoding='utf8')
    report = {'game': args.game, 'kind': 'image', 'source_previous': old_info, 'source_current': current_info,
              'source_verified_delta_names': len(delta), 'target_held_delta_names': len(held_delta),
              'prior_plans': prior_info, 'prior_prefix_union': len(prior), 'new_prefixes': len(beginnings),
              'new_prefixes_with_target_held_source': len(held_beginnings), 'frozen_pairs': len(pairs),
              'frozen_suffixes': len(ends), 'candidate_cells': len(beginnings) * len(pairs) * (len(ends) + 1),
              'known_target_controls': len(controls), 'plan': str(plan), 'required_pool_selection': ['image']}
    (out / 'measurement.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf8')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
