"""Build a fresh-prefix delta against a frozen witnessed image pair/suffix plan.

Only the explicit, target-verified image seed files provide beginnings. The
existing plan's complete pair fragments and suffixes are copied unchanged;
there is no alphabet expansion or re-ranking. Any beginning already carried
by the executed pair plan is removed. All pair fragments must still have a
target-held witness, and every frozen suffix must still pass the reviewed
three-sibling-core evidence rule. Captures, source rows and stored seed keys
are checked under the modern ordinary-image policy.

2026-10-09 BO7: 2,314 independently rehashed CSV images plus 692 newly confirmed
material-wrapper images supplied 1,497 beginnings. One was already covered;
the 1,496 new beginnings x 677 frozen pairs x 5,306 frozen suffixes (and the
engine's empty ending) cover 5,374,887,144 candidates. There were 2,252 known
target controls, 2,223 in the supplied seeds. Aligned prior one-byte overlap
was zero; the prior numeric-triple product covered only 1,932 candidates.

Example:
  python contrib/image_stem_pair_prefix_delta_plan.py --game BLACKOP7 \
    --base-plan-dir contrib/image_stem_pair_suffix_plan/blackop7 \
    --seed-file new-images.txt --seed-file findings/blackop7/<run>/image.txt
  confirm_plan contrib/image_stem_pair_prefix_delta_plan/blackop7/images.plan.txt --size

Select only image in the confirmer. This builder does not run a search or
change settings. Spent by these exact new beginnings and frozen factors.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

ROOT = next((p for p in [Path.cwd(), *Path(__file__).resolve().parents]
             if (p / 'scripts/snapshot.py').is_file()), None)
if ROOT is None:
    raise SystemExit('Run inside a solver checkout')
sys.path.insert(0, str(ROOT / 'scripts'))
import snapshot


def reviewed_companion():
    path = ROOT / 'scripts/contributed/verified_image_channel_byte_parallel_20261009-132951.py'
    spec = importlib.util.spec_from_file_location('_image_delta_plan_companion', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def values(path):
    out = set()
    for row in path.read_text(encoding='utf-8').splitlines():
        row = row.strip()
        if not row or row.startswith('#'):
            continue
        value = row.partition(',')[2] if ',' in row else row
        if not value or not value.isascii():
            raise ValueError('Frozen factors must be nonempty ASCII values')
        out.add(value)
    if not out:
        raise ValueError('A frozen factor file is empty')
    return out


def load_seeds(paths, held, game):
    seeds = set()
    for path in paths:
        for row in path.read_text(encoding='utf-8').splitlines():
            name = row.strip()
            stored_key = None
            raw, sep, rest = name.partition(',')
            if sep:
                try:
                    stored_key = int(raw, 16) & snapshot.ID_MASK
                except ValueError:
                    pass
                else:
                    name = rest.strip()
            name = name.lower()
            if not name:
                continue
            if not name.isascii() or '\n' in name or '\r' in name:
                raise ValueError('Seed files must contain one ASCII name per row')
            key = snapshot.fnv1a(name, game, 'image') & snapshot.ID_MASK
            if stored_key is not None and key != stored_key:
                raise ValueError('Seed spelling does not reproduce its supplied key')
            if key not in held:
                raise ValueError('Seed spelling does not reproduce a target image ID')
            seeds.add(name)
    return seeds


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--game', choices=sorted(snapshot.MODERN), required=True)
    parser.add_argument('--seed-file', type=Path, action='append', required=True)
    parser.add_argument('--base-plan-dir', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path)
    args = parser.parse_args()
    capture = snapshot.read(ROOT / 'snapshots' / (args.game.lower() + '.ids'))
    if capture.game != args.game:
        raise ValueError('Capture game does not match the requested game')
    held = set(capture.by_pool()['image'])
    seeds = load_seeds(args.seed_file, held, args.game)
    helper = reviewed_companion()
    paths = {role: args.base_plan_dir / (role + '.txt') for role in ('begin', 'stem', 'end')}
    prior, pairs, ends = (values(paths[role]) for role in ('begin', 'stem', 'end'))
    if not all(len(pair) == 2 and pair[-1].isalnum() for pair in pairs):
        raise ValueError('Middle factors must be complete two-byte stem fragments')
    names = helper.corpus('image', args.game) | seeds
    witnessed_ends = helper.target_tails(names, held, args.game)
    if not ends <= witnessed_ends:
        raise ValueError('A frozen suffix no longer has the required target-held witnesses')
    target_names = {n for n in names if snapshot.fnv1a(n, args.game, 'image') & snapshot.ID_MASK in held}
    witnessed_pairs = {stem[-2:] for n in target_names for _, stem, tail in helper.cuts(n)
                       if tail in ends and len(stem) > 2}
    if not pairs <= witnessed_pairs:
        raise ValueError('A frozen complete pair lacks a target-held source witness')
    proposed = {stem[:-2] for n in seeds for _, stem, tail in helper.cuts(n)
                if tail in ends and len(stem) > 2}
    beginnings = proposed - prior
    if not beginnings:
        raise SystemExit('No new beginnings beyond the executed pair plan')
    def reachable(name):
        if len(name) > 2 and name[:-2] in beginnings and name[-2:] in pairs:
            return True
        return any(tail in ends and len(stem) > 2 and stem[:-2] in beginnings and stem[-2:] in pairs
                   for _, stem, tail in helper.cuts(name))
    controls = {snapshot.fnv1a(n, args.game, 'image') & snapshot.ID_MASK
                for n in target_names if reachable(n)}
    seed_controls = {snapshot.fnv1a(n, args.game, 'image') & snapshot.ID_MASK
                     for n in seeds if reachable(n)}
    out = (args.output_dir or ROOT / 'contrib/image_stem_pair_prefix_delta_plan' / args.game.lower()).resolve()
    if out == args.base_plan_dir.resolve():
        raise ValueError('The delta output directory must not overwrite frozen inputs')
    out.mkdir(parents=True, exist_ok=True)
    for role, items in [('begin', beginnings), ('stem', pairs), ('end', ends)]:
        (out / (role + '.txt')).write_text(''.join('0,' + v + '\n' for v in sorted(items)), encoding='utf-8')
    plan = out / 'images.plan.txt'
    plan.write_text(
        f'label: {args.game} fresh verified image beginnings under frozen complete pairs\n'
        f'describe: {len(seeds)} target-verified image seeds give {len(beginnings)} prefixes absent from the executed pair plan; unchanged {len(pairs)} complete target-witnessed pairs and {len(ends)} three-core witnessed suffixes; image pool only\n'
        f'game: {args.game}\nbegin: @{(out / "begin.txt").as_posix()}\n'
        f'stem: @{(out / "stem.txt").as_posix()}\nend: @{(out / "end.txt").as_posix()}\n'
        'bare: no\nfold: yes\n', encoding='utf-8')
    report = {'game': args.game, 'kind': 'image', 'verified_seed_names': len(seeds),
              'proposed_beginnings': len(proposed), 'removed_prior_beginnings': len(proposed & prior),
              'new_beginnings': len(beginnings), 'frozen_complete_pairs': len(pairs), 'frozen_suffixes': len(ends),
              'candidates_including_unsuffixed': len(beginnings) * len(pairs) * (len(ends) + 1),
              'known_target_controls': len(controls), 'seed_controls': len(seed_controls),
              'seed_file_sha256': {str(p): digest(p) for p in args.seed_file},
              'frozen_factor_sha256': {role: digest(p) for role, p in paths.items()},
              'input_bytes': sum((out / (role + '.txt')).stat().st_size for role in ('begin', 'stem', 'end')),
              'plan': str(plan), 'required_pool_selection': ['image']}
    (out / 'measurement.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
