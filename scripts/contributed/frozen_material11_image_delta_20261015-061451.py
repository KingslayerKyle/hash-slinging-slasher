"""Apply the unchanged independent visual graph once to eleven verified material roots.

One-off BO7 source delta measured 2026-10-15: 11 material roots, 706 frozen rules,
25,660 independently revalidated witness pairs, 389 residual image candidates,
zero known target controls and one provisional image key. Standard image-only
confirmation is still required. No training, frontier expansion or new alphabets.

  python contrib/frozen_material11_image_delta_20261015.py
  confirm_list logs/gpu_visual_20261015/material11_reverse_images/image.candidates.txt \
    --game BLACKOP7 --script contrib/frozen_material11_image_delta_20261015.py

Reads the pinned public Git table blobs, BO7 capture, exact frozen rule graph,
explicit raw material root list and documented prior candidate/factor artifacts.
--frozen-dir and --seed-file can relocate those exact inputs; --output-dir changes
where diagnostics go. The frozen rule digest, counts, source hashes and every
original witness are checked before application. The prior input artifact paths
are intentionally fixed because this is one recorded seed delta, not a driver.
All output input hashes/formats and derivation provenance are written alongside
full candidate and hit files. Nothing writes findings, configuration or claims.

Explicit raw-name files preserve literal commas and leading # characters;
explicit 0,name factors split only their first separator. All seven pair products,
earlier byte/numeric products, prior image lists and the frozen complete interior
pair space are excluded. Spent by these exact roots, rules and prior inputs.
"""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import sys
import time

ROOT = next(p for p in [Path.cwd(), *Path(__file__).resolve().parents]
            if (p / 'scripts/snapshot.py').is_file())
OUT = ROOT / 'logs/gpu_visual_20261015/material11_reverse_images'
sys.path.insert(0, str(ROOT / 'scripts'))
import snapshot

FROZEN = ROOT / 'logs/visual_seed_closure_20261015/result'
SEED = ROOT / 'logs/gpu_visual_20261015/structure_directory_tail.hits.txt'
GAME = 'BLACKOP7'
MASK = snapshot.ID_MASK
RULE_SHA = '6f0490f78c696ef6a88a72912fa0a6a56ff4f5264c59f97b36745614969d6d61'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def raw_lines(path):
    """A leading # or comma is part of the name, never a comment/CSV separator."""
    names = set()
    for row in path.read_text(encoding='utf-8').splitlines():
        if not row:
            continue
        if not row.isascii() or row != row.strip().lower():
            raise ValueError(f'Noncanonical raw name in {path}')
        names.add(row)
    return names


def factor_lines(path):
    names = set()
    for row in path.read_text(encoding='utf-8').splitlines():
        if not row or row.startswith('#'):
            continue  # Only the explicit factor format permits metadata comments.
        raw, sep, name = row.partition(',')
        if not sep or raw != '0' or not name.isascii() or name != name.strip().lower():
            raise ValueError(f'Expected explicit 0,name row in {path}')
        if name:
            names.add(name)
    return names


def covered(name, plan):
    begins, stems, ends = plan
    for cut in range(len(name)+1):
        if name[cut:] in ends:
            for width in {len(stem) for stem in stems}:
                if cut >= width and name[:cut-width] in begins and name[cut-width:cut] in stems:
                    return True
    return False


def main():
    global OUT, FROZEN, SEED
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--frozen-dir', type=Path, default=FROZEN)
    parser.add_argument('--seed-file', type=Path, default=SEED, help='Explicit raw material name list')
    parser.add_argument('--output-dir', type=Path, default=OUT)
    args = parser.parse_args()
    OUT, FROZEN, SEED = args.output_dir, args.frozen_dir, args.seed_file
    started = time.monotonic()
    capture_path = ROOT / 'snapshots/blackop7.ids'
    capture = snapshot.read(capture_path)
    assert capture.game == GAME
    held = {kind: set(capture.by_pool()[kind]) for kind in ('image', 'material')}
    measurement = json.loads((FROZEN / 'measurement.json').read_text())
    rule_path = FROZEN / 'rules.json'
    assert sha(rule_path) == RULE_SHA
    rules = json.loads(rule_path.read_text())
    training, source_digests = {}, {}
    for kind, table in [('image', 'fnv1a_ximages_v2'), ('material', 'fnv1a_xmaterials_v2')]:
        exclusion_path = FROZEN / (kind + '.training_exclusions.txt')
        assert sha(exclusion_path) == measurement['frozen_training_exclusion_sha256'][kind]
        generated = raw_lines(exclusion_path)
        assert len(generated) == measurement['training_descendants_excluded'][kind]
        data = subprocess.check_output(['git', '-C', str(ROOT / 'cod-name-db'), 'show',
                                        measurement['source_commit'] + ':csv/' + table + '.csv'])
        source_digests[kind] = hashlib.sha256(data).hexdigest()
        assert source_digests[kind] == measurement['source_table_sha256'][kind]
        training[kind] = {n for n in snapshot.database_names(table, data.decode('utf-8').splitlines())
                          if n.isascii() and n == n.strip().lower() and n not in generated
                          and snapshot.fnv1a(n, GAME, kind) & MASK in held[kind]}
        assert len(training[kind]) == measurement['training'][kind]
    pair_controls = 0
    for rule in rules:
        p, s, d, cores = (rule[k] for k in ('image_prefix', 'image_suffix', 'material_directory', 'cores'))
        assert len(set(cores)) == len(cores) >= 3
        for core in cores:
            assert p + core + s in training['image'] and d + core in training['material']
        pair_controls += len(cores)
    assert (len(rules), pair_controls) == (706, 25660)

    roots = raw_lines(SEED)
    assert len(roots) == 11 and not roots.intersection(training['material'])
    for name in roots:
        assert snapshot.fnv1a(name, GAME, 'material') & MASK in held['material']
    proposals, provenance = set(), {}
    for name in sorted(roots):
        directory, slash, core = name.rpartition('/')
        for rule in rules:
            if rule['material_directory'] == directory + slash:
                candidate = rule['image_prefix'] + core + rule['image_suffix']
                proposals.add(candidate)
                provenance.setdefault(candidate, {'material_root': name,
                    'rule': {k: rule[k] for k in ('image_prefix', 'image_suffix', 'material_directory')},
                    'independent_witness_cores': rule['cores'][:3]})

    plan_dirs = [
        'contrib/image_stem_pair_suffix_plan/blackop7',
        'contrib/image_stem_pair_prefix_delta_plan/blackop7',
        'logs/bo7_visual_recon/prefix120_pair_delta',
        'contrib/published_image_pair_source_delta/blackop7',
        'contrib/bo7_verified_held_image_prefix_complement_20261015',
        'contrib/published_image_pair_factor_delta_20261015/blackop7/pairs',
        'contrib/published_image_pair_factor_delta_20261015/blackop7/suffixes',
        'contrib/image_stem_byte_suffix_plan/blackop7',
        'contrib/image_numeric_triple_family_plan/blackop7',
    ]
    candidates = set(proposals)
    overlap, inputs = {}, {}
    for relative in plan_dirs:
        paths = [ROOT / relative / (role + '.txt') for role in ('begin', 'stem', 'end')]
        plan = [factor_lines(path) for path in paths]
        plan[2].add('')
        removed = {n for n in candidates if covered(n, plan)}
        overlap[relative] = len(removed)
        candidates.difference_update(removed)
        inputs[relative] = {'format': 'zero-count-factor-rows',
                            'sha256': {path.name: sha(path) for path in paths}}
    lists = [
        ('logs/bo7_visual_recon/csv_material_image_delta_candidates.txt', 'factor'),
        ('logs/bo7_visual_recon/csv_model_visual_delta.image.final_candidates.txt', 'factor'),
        ('logs/bo7_visual_recon/csv_image_sibling_delta_candidates.txt', 'factor'),
        ('logs/bo7_visual_recon/material_blocks.candidates.txt', 'factor'),
        ('logs/bo7_model_to_image_candidates.txt', 'raw'),
        ('logs/bo7_visual_structure_ideas/wrapper_residual_candidates.txt', 'raw'),
        ('logs/bo7_image_conditioned_triples_recon/residual_candidates.txt', 'raw'),
        ('logs/visual_seed_closure_20261015/result/image.candidates.txt', 'raw'),
        ('logs/visual_seed_closure_20261015/replay_fixed_initial152/image.candidates.txt', 'raw'),
        ('logs/visual_seed_closure_20261015/replay_fixed_suffix19/image.candidates.txt', 'raw'),
        ('logs/visual_suffix_seed_closure_20261015/image.candidates.txt', 'raw'),
    ]
    for relative, kind in lists:
        path = ROOT / relative
        earlier = factor_lines(path) if kind == 'factor' else raw_lines(path)
        removed = candidates & earlier
        overlap[relative] = len(removed)
        candidates.difference_update(removed)
        inputs[relative] = {'format': kind, 'names': len(earlier), 'sha256': sha(path)}
    frame_path = ROOT / 'logs/gpu_visual_20261015/interior_slot_frames.json'
    vocabulary_path = ROOT / 'logs/gpu_visual_20261015/interior_slot_vocab.txt'
    frames = json.loads(frame_path.read_text())
    vocabulary = raw_lines(vocabulary_path)
    def interior_covered(name):
        return any(name.startswith(p) and name.endswith(s)
                   and name[len(p):len(name)-len(s)] in vocabulary for p, s, _ in frames)
    removed = {n for n in candidates if interior_covered(n)}
    overlap['frozen_complete_interior_pair_slots'] = len(removed)
    candidates.difference_update(removed)
    inputs['frozen_complete_interior_pair_slots'] = {
        'frames_sha256': sha(frame_path), 'vocabulary_sha256': sha(vocabulary_path)}

    excluded = {k & MASK for k in snapshot.known_hashes(game=GAME)}
    for top in ('all_names', 'submissions', 'findings'):
        for path in (ROOT / top).rglob('*.txt'):
            for row in path.read_text(encoding='utf-8', errors='replace').splitlines():
                raw, sep, _ = row.partition(',')
                if sep:
                    try:
                        excluded.add(int(raw, 16) & MASK)
                    except ValueError:
                        pass
    for row in (ROOT / 'state/claimed.txt').read_text().splitlines():
        try:
            excluded.add(int(row, 16) & MASK)
        except ValueError:
            pass
    hits, controls, prior_controls = set(), set(), set()
    for name in proposals:
        key = snapshot.fnv1a(name, GAME, 'image') & MASK
        if key in held['image'] and key in excluded:
            prior_controls.add(name)
        if name not in candidates or key not in held['image']:
            continue
        if key in excluded:
            controls.add(name)
        else:
            hits.add(name)
    report = {'game': GAME, 'one_step_only': True, 'material_roots': len(roots),
              'roots_are_provisional_until_official_confirmation': True,
              'frozen_rules': len(rules), 'independently_revalidated_pair_controls': pair_controls,
              'training': {k: len(v) for k, v in training.items()},
              'proposed_images': len(proposals), 'prior_exclusions': overlap,
              'residual_candidates': len(candidates), 'known_controls_before_prior_exclusion': len(prior_controls),
              'known_controls_after_prior_exclusion': len(controls), 'fresh_image_names': len(hits),
              'unclaimed_image_keys': len(held['image'] - excluded),
              'chance_hit_expectation': len(candidates)*len(held['image']-excluded)/(1<<63),
              'seed_sha256': sha(SEED), 'rules_sha256': sha(rule_path),
              'capture_sha256': sha(capture_path), 'source_commit': measurement['source_commit'],
              'source_table_sha256': source_digests, 'prior_input_artifacts': inputs,
              'seconds': round(time.monotonic()-started, 3)}
    OUT.mkdir(exist_ok=True)
    for label, names in [('candidates', candidates), ('hits', hits), ('known_controls', controls)]:
        (OUT / ('image.' + label + '.txt')).write_text(''.join(n+'\n' for n in sorted(names)), encoding='utf-8')
    (OUT / 'provenance.json').write_text(json.dumps({n: provenance[n] for n in sorted(candidates)}, indent=2)+'\n')
    (OUT / 'measurement.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps({k: v for k, v in report.items() if k not in ('prior_input_artifacts', 'source_table_sha256', 'prior_exclusions')}))


if __name__ == '__main__':
    main()
