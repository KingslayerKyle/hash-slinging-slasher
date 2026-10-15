"""Two finite image plans from independently published new complete factors.

Re-read two pinned cod-name-db revisions through the shared verified database
reader. New rule evidence is their name-set difference, restricted to the chosen
image capture, minus every valid locally confirmed image name. Generated local
descendants cannot become rule witnesses merely because the tables absorbed them.

Keep the exact union of the supplied previously executed beginning lists. Their
complete two-byte and suffix lists must be identical. New whole pairs need three
distinct new source cores, each followed by an old suffix. New suffixes need three
distinct new source cores, each holding at least two suffixes at the same cut.
Cuts are the existing one/two-token suffix boundary, not a widened alphabet.

Two plans cover the complete new-factor delta: executed beginnings x new pairs
x all old/new suffixes, and executed beginnings x old pairs x new suffixes.
Their aligned nonempty factor cells are disjoint from the supplied old products
and each other. The engine also appends
an empty ending: the suffix plan therefore repeats old unsuffixed cells, reported
explicitly. Alternative string decompositions and other methods can overlap;
normal confirmation exclusions remain mandatory. New beginnings already verified
and executed by a source-prefix pass are application vocabulary, never witnesses.

  python contrib/published_image_pair_factor_delta_20261015.py --game BLACKOP7 \
      --old-table-rev e547b9391f330edf191e7ccddf0975f2e628853c \
      --new-table-rev 3d42c005d5405af8b225958bef09a041e9ada0be \
      --base-plan-dir contrib/image_stem_pair_suffix_plan/blackop7 \
      --exclude-plan-dir contrib/image_stem_pair_prefix_delta_plan/blackop7 \
      --exclude-plan-dir logs/bo7_visual_recon/prefix120_pair_delta \
      --exclude-plan-dir contrib/published_image_pair_source_delta/blackop7 \
      --exclude-plan-dir contrib/bo7_verified_held_image_prefix_complement_20261015 \
      --output-dir contrib/published_image_pair_factor_delta_20261015/blackop7

--size validates and measures without writing outputs. This builder never runs
searches or modifies settings, findings, exclusions or prior factors. Select only
image for each official confirmer. Spent by the pinned independent source delta,
local-descendant exclusion set and frozen factors; do not repeatedly rebuild it.
"""
import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = next((p for p in [Path.cwd(), *Path(__file__).resolve().parents]
             if (p / 'scripts/snapshot.py').is_file()), None)
if ROOT is None:
    raise SystemExit('Run inside a solver checkout')
sys.path.insert(0, str(ROOT / 'scripts'))
import snapshot

TABLE = 'fnv1a_ximages_v2'
TOKEN = re.compile(r'[a-z0-9]{1,16}')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def names_digest(names):
    return digest(('\n'.join(sorted(names)) + '\n').encode('utf-8'))


def located(path):
    return path.resolve() if path.is_absolute() else (ROOT / path).resolve()


def table_version(ref):
    def git(*args):
        return subprocess.check_output(['git', '-C', str(ROOT / 'cod-name-db'), *args])
    commit = git('rev-parse', '--verify', ref + '^{commit}').decode('ascii').strip()
    data = git('show', commit + ':csv/' + TABLE + '.csv')
    names = {n for n in snapshot.database_names(TABLE, data.decode('utf-8').splitlines())
             if n and n.isascii() and n == n.strip().lower()}
    return names, {'commit': commit, 'table_sha256': digest(data), 'verified_names': len(names)}


def values(path):
    result = set()
    for row in path.read_text(encoding='utf-8').splitlines():
        if not row or row.startswith('#'):
            continue
        value = row.partition(',')[2] if ',' in row else row
        if not value or not value.isascii() or value != value.strip().lower():
            raise ValueError('Factors must be canonical nonempty ASCII strings')
        result.add(value)
    if not result:
        raise ValueError('Empty frozen factor list')
    return result


def history(paths, game):
    names = set()
    for path in paths:
        for row in path.read_text(encoding='utf-8').splitlines():
            raw, sep, name = row.partition(',')
            if not sep or not name or name != name.strip() or not name.isascii():
                continue
            try:
                key = int(raw, 16) & snapshot.ID_MASK
            except ValueError:
                continue
            name = name.lower()
            if snapshot.fnv1a(name, game, 'image') & snapshot.ID_MASK == key:
                names.add(name)
    return names


def cuts(name):
    parts = name.split('_')
    for depth in (1, 2):
        if len(parts) <= depth or not all(TOKEN.fullmatch(t) for t in parts[-depth:]):
            continue
        tail = '_' + '_'.join(parts[-depth:])
        stem = name[:-len(tail)]
        if len(stem) > 1 and stem[-1].isalnum():
            yield depth, stem, tail


def witness_factors(source, old_pairs, old_ends):
    """Require distinct cores, complete pairs, and actual same-depth siblings.

    Three channels on one core cannot supply three independent pair witnesses.
    >>> names = {'frame_agm_c', 'frame_agm_n', 'frame_agm_s'}
    >>> bool(witness_factors(names, set(), {'_c', '_n', '_s'})[0])
    False
    >>> names = {stem + tail for stem in ('first_agm', 'second_agm', 'third_agm')
    ...          for tail in ('_c', '_n')}
    >>> pairs, tails = witness_factors(names, {'aa'}, {'_c'})
    >>> set(pairs), '_n' in tails
    ({'gm'}, True)
    >>> 'gg' in pairs or 'mm' in pairs  # Complete pair, never character products.
    False
    >>> bool(witness_factors({'first_agm_n', 'second_agm_n', 'third_agm_n'}, set(), {'_c'})[1])
    False
    >>> '_c' in tails  # Existing factors never become a new delta.
    False
    """
    pair_sources = defaultdict(lambda: defaultdict(set))
    siblings = defaultdict(lambda: defaultdict(set))
    for name in source:
        for depth, stem, tail in cuts(name):
            siblings[depth, stem][tail].add(name)
            if tail in old_ends and len(stem) > 2 and stem[-2:] not in old_pairs:
                pair_sources[stem[-2:]][stem].add(name)
    tail_sources = defaultdict(dict)
    for (depth, stem), tails in siblings.items():
        if len(tails) < 2:
            continue
        for tail in tails.keys() - old_ends:
            tail_sources[tail][stem] = {'depth': depth,
                'source_names': sorted(tails[tail]),
                'sibling_names': sorted(set().union(*(v for k, v in tails.items() if k != tail)))}
    pairs = {pair: {stem: sorted(names) for stem, names in sorted(cores.items())}
             for pair, cores in pair_sources.items() if len(cores) >= 3}
    tails = {tail: dict(sorted(cores.items())) for tail, cores in tail_sources.items() if len(cores) >= 3}
    return pairs, tails


def reachable(name, beginnings, pairs, endings):
    # Explicitly include the engine's empty ending. All nonempty factors follow
    # exactly the one/two-token cuts, so there are no omitted alternative cuts.
    if len(name) > 2 and name[:-2] in beginnings and name[-2:] in pairs:
        return True
    return any(tail in endings and len(stem) > 2 and stem[:-2] in beginnings and stem[-2:] in pairs
               for _, stem, tail in cuts(name))


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--game', required=True, choices=sorted(snapshot.MODERN))
    ap.add_argument('--old-table-rev', required=True)
    ap.add_argument('--new-table-rev', required=True)
    ap.add_argument('--base-plan-dir', required=True, type=Path)
    ap.add_argument('--exclude-plan-dir', action='append', default=[], type=Path)
    ap.add_argument('--output-dir', required=True, type=Path)
    ap.add_argument('--size', action='store_true')
    args = ap.parse_args()
    old, old_info = table_version(args.old_table_rev)
    current, current_info = table_version(args.new_table_rev)
    if old_info['commit'] == current_info['commit']:
        raise ValueError('Two distinct pinned source revisions are required')
    capture_path = ROOT / 'snapshots' / (args.game.lower() + '.ids')
    shot = snapshot.read(capture_path)
    if shot.game != args.game:
        raise ValueError('Capture game differs from requested game')
    held = set(shot.by_pool()['image'])
    findings_root = Path(snapshot.settings.path('findings', 'findings'))
    local_descendants = history(findings_root.rglob('image*.txt'), args.game)
    source_delta = current - old
    held_delta = {n for n in source_delta if snapshot.fnv1a(n, args.game, 'image') & snapshot.ID_MASK in held}
    source = held_delta - local_descendants
    base = located(args.base_plan_dir)
    prior_dirs = [base, *(located(p) for p in args.exclude_plan_dir)]
    output = located(args.output_dir)
    if any(output == p or p in output.parents or output in p.parents for p in prior_dirs):
        raise ValueError('Output must be separate from every frozen input directory')
    old_pairs, old_ends = values(base / 'stem.txt'), values(base / 'end.txt')
    if not all(len(p) == 2 and p[-1].isalnum() for p in old_pairs):
        raise ValueError('Frozen pairs must be complete two-byte fragments')
    beginnings, prior_info = set(), []
    for directory in prior_dirs:
        if values(directory / 'stem.txt') != old_pairs or values(directory / 'end.txt') != old_ends:
            raise ValueError('Prior beginning plans must share identical pair and suffix factors')
        begins = values(directory / 'begin.txt')
        beginnings.update(begins)
        prior_info.append({'directory': str(directory), 'begin_count': len(begins),
                           'sha256': {role: digest((directory / (role + '.txt')).read_bytes())
                                      for role in ('begin', 'stem', 'end')}})
    pair_provenance, tail_provenance = witness_factors(source, old_pairs, old_ends)
    new_pairs, new_ends = set(pair_provenance), set(tail_provenance)
    if not new_pairs or not new_ends:
        raise ValueError('Both independently witnessed factor deltas must be nonempty')
    if not all(len(p) == 2 and p.isascii() and p[-1].isalnum() for p in new_pairs):
        raise ValueError('New pair shape is invalid')
    # Revalidate old factors as well; history can support frozen factors and
    # controls but cannot add independent new rule evidence.
    known = set(current) | local_descendants
    for top in ('all_names', 'submissions'):
        known.update(history((ROOT / top).rglob('image*.txt'), args.game))
    target = {n for n in known if snapshot.fnv1a(n, args.game, 'image') & snapshot.ID_MASK in held}
    _, witnessed_tails = witness_factors(target, old_pairs, set())
    witnessed_pairs = {stem[-2:] for n in target for _, stem, tail in cuts(n)
                       if tail in old_ends and len(stem) > 2}
    if not old_pairs <= witnessed_pairs or not old_ends <= witnessed_tails.keys():
        raise ValueError('A frozen pair or suffix lost its original target evidence')
    plans = {}
    for label, pairs, endings in (('pairs', new_pairs, old_ends | new_ends), ('suffixes', old_pairs, new_ends)):
        controls = {n for n in target if reachable(n, beginnings, pairs, endings)}
        empty_controls = {n for n in controls if len(n) > 2 and n[:-2] in beginnings and n[-2:] in pairs}
        nonempty_controls = {n for n in controls if any(
            tail in endings and len(stem) > 2 and stem[:-2] in beginnings and stem[-2:] in pairs
            for _, stem, tail in cuts(n))}
        independent_controls = set()
        for name in controls:
            decompositions = [(stem, tail) for _, stem, tail in cuts(name) if tail in endings]
            if label == 'pairs':
                decompositions.append((name, ''))
            for stem, tail in decompositions:
                if len(stem) <= 2 or stem[:-2] not in beginnings or stem[-2:] not in pairs:
                    continue
                independent_pair = label != 'pairs' or len(pair_provenance[stem[-2:]].keys() - {stem}) >= 3
                independent_tail = tail not in new_ends or len(tail_provenance[tail].keys() - {stem}) >= 3
                if independent_pair and independent_tail:
                    independent_controls.add(name)
        nonempty_cells = len(beginnings) * len(pairs) * len(endings)
        empty_cells = len(beginnings) * len(pairs)
        plans[label] = {'beginnings': len(beginnings), 'complete_pairs': len(pairs), 'suffixes': len(endings),
            'candidate_cells': nonempty_cells + empty_cells, 'nonempty_candidate_cells': nonempty_cells,
            'implicit_empty_cells': empty_cells,
            'aligned_old_product_overlap_cells': empty_cells if label == 'suffixes' else 0,
            'chance_match_upper_bound_before_exclusions': (nonempty_cells + empty_cells) * len(held) / (1 << 63),
            'known_target_controls': len(controls), 'known_empty_ending_controls': len(empty_controls),
            'known_nonempty_controls': len(nonempty_controls),
            'known_nonempty_only_controls': len(nonempty_controls - empty_controls),
            'controls_independent_of_new_factor_evidence': len(independent_controls),
            'plan': str(output / label / 'images.plan.txt')}
    report = {'game': args.game, 'kind': 'image', 'source_previous': old_info, 'source_current': current_info,
        'source_delta_names': len(source_delta), 'target_held_source_delta_names': len(held_delta),
        'local_descendants_removed': len(held_delta & local_descendants), 'independent_source_names': len(source),
        'independent_source_sha256': names_digest(source), 'local_descendant_names_sha256': names_digest(local_descendants),
        'capture_sha256': digest(capture_path.read_bytes()), 'prior_plans': prior_info,
        'prior_beginning_union': len(beginnings), 'new_complete_pairs': len(new_pairs), 'new_suffixes': len(new_ends),
        'minimum_pair_core_witnesses': min(map(len, pair_provenance.values())),
        'minimum_suffix_sibling_core_witnesses': min(map(len, tail_provenance.values())), 'plans': plans,
        'overlap_scope': 'Aligned factor cells only; alternative decompositions and other methods may overlap.',
        'required_pool_selection': ['image']}
    if args.size:
        print(json.dumps(report, sort_keys=True))
        return
    output.mkdir(parents=True, exist_ok=True)
    (output / 'independent_source.txt').write_text('\n'.join(sorted(source)) + '\n', encoding='utf-8')
    (output / 'provenance.json').write_text(json.dumps({'pairs': pair_provenance, 'suffixes': tail_provenance}, indent=2) + '\n', encoding='utf-8')
    for label, pairs, endings in (('pairs', new_pairs, old_ends | new_ends), ('suffixes', old_pairs, new_ends)):
        directory = output / label
        directory.mkdir(exist_ok=True)
        for role, factors in (('begin', beginnings), ('stem', pairs), ('end', endings)):
            (directory / (role + '.txt')).write_text(''.join('0,' + x + '\n' for x in sorted(factors)), encoding='utf-8')
        description = (f'{len(source)} independently published target-held image sources after local-descendant exclusion; '
            f'{len(beginnings)} previously executed verified prefixes only; {len(pairs)} complete pairs; {len(endings)} complete suffixes; '
            f'new {label} need three independent source cores; '
            f'implicit empty-ending old overlap {plans[label]["aligned_old_product_overlap_cells"]} cells; '
            'image only; generator contrib/published_image_pair_factor_delta_20261015.py')
        (directory / 'images.plan.txt').write_text(
            f'label: {args.game} independently published complete image {label} delta\ndescribe: {description}\n'
            f'game: {args.game}\nbegin: @{(directory / "begin.txt").as_posix()}\n'
            f'stem: @{(directory / "stem.txt").as_posix()}\nend: @{(directory / "end.txt").as_posix()}\n'
            'bare: no\nfold: yes\n', encoding='utf-8')
    (output / 'measurement.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, sort_keys=True))


if __name__ == '__main__':
    main()
