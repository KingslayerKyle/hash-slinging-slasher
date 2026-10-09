"""Use newly verified embedded-model vocabulary to derive visual names only.

Modern models are never search targets or findings here. Every supplied model
spelling must independently hash to an existing xmodel key in the selected
capture; supplied hash,name rows must reproduce their key as well. An external
CSV's hash/category columns are not evidence. A raw-name source can first be
filtered by recomputed model-pool membership; this generator then independently
validates every retained spelling before using it as vocabulary.

The baseline model file represents vocabulary already measured by a prior pass.
Only explicit seeds absent from that baseline supply application cores. Models
in their union establish source prefix/suffix shapes. Visual wrappers must be
jointly witnessed by at least three distinct shared cores in verified, target-
held images or materials. Cuts remove at most two tokens from each end, retain
at least three tokens and twelve characters, and preserve literal directories.
Complete source and target wrapper pairs remain correlated.

2026-10-09 BO7: 1,588 raw strings newly rehashed into the model capture were
disjoint from the earlier 462-model baseline. They supplied 47,590 material
candidates (177 controls, seven unclaimed keys) and 8,313 image candidates
(157 controls, 97 unclaimed keys). No model names were reported as recoveries.
The exact prior candidate files had zero overlap. The 108 material and 18 image
wrapper products are small enough that confirm_list is preferable to separate
plans and their mandatory empty-ending additions.

  python contrib/verified_model_visual_source_delta.py --game BLACKOP7 \
      --kind image --seed-file logs/new-model-vocabulary.txt \
      --baseline-file logs/prior-model-vocabulary.txt \
      --prior-candidates logs/prior-model-to-image-candidates.txt \
      --output logs/model-source-image-delta.txt

Use confirm_list with only the selected visual pool and --script. The generator
writes candidates, never findings/config/claims. Official confirmation performs
fresh exclusions. Spent by these model source strings and witnessed wrappers;
an unchanged-source rerun is not new ground.
"""
import argparse
from collections import defaultdict
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


def row_name(row):
    text = row.strip()
    raw, sep, rest = text.partition(',')
    stored = None
    if sep:
        try:
            stored = int(raw, 16) & snapshot.ID_MASK
        except ValueError:
            raise ValueError('Seed rows must be names or valid hexadecimal-key,name rows')
        text = rest.strip()
    name = text.lower()
    if name and (not name.isascii() or any(ord(c) < 32 or ord(c) == 127 for c in name)):
        raise ValueError('One ASCII spelling per row is required')
    return name, stored


def load_models(paths, held, game):
    names = set()
    for path in paths:
        for row in path.read_text(encoding='utf-8-sig').splitlines():
            name, stored = row_name(row)
            if not name:
                continue
            key = snapshot.fnv1a(name, game, 'xmodel') & snapshot.ID_MASK
            if stored is not None and stored != key:
                raise ValueError('A model seed does not reproduce its supplied stored key')
            if key not in held:
                raise ValueError('A model seed does not reproduce an existing target model key')
            names.add(name)
    return names


def cuts(name):
    directory, slash, base = name.rpartition('/')
    parts = base.split('_')
    for left in range(3):
        for right in range(3):
            if len(parts) - left - right < 3:
                continue
            core = '_'.join(parts[left:len(parts) - right if right else None])
            if len(core) < 12:
                continue
            prefix = directory + slash + ('_'.join(parts[:left]) + '_' if left else '')
            suffix = '_' + '_'.join(parts[-right:]) if right else ''
            yield prefix, core, suffix


def generate(baseline, seeds, target):
    index = defaultdict(set)
    for name in baseline | seeds:
        for prefix, core, suffix in cuts(name):
            index[core].add((prefix, suffix))
    supports = defaultdict(set)
    for name in target:
        if any(c in name for c in '~&.*'):
            continue
        for target_prefix, core, target_suffix in cuts(name):
            for source_prefix, source_suffix in index.get(core, ()):
                supports[source_prefix, source_suffix, target_prefix, target_suffix].add(core)
    rules = defaultdict(set)
    for (sp, ss, tp, ts), cores in supports.items():
        if len(cores) >= 3:
            rules[sp, ss].add((tp, ts))
    candidates = set()
    for name in seeds - baseline:
        for prefix, core, suffix in cuts(name):
            for target_prefix, target_suffix in rules.get((prefix, suffix), ()):
                candidates.add(target_prefix + core + target_suffix)
    return candidates, {'baseline_model_names': len(baseline), 'verified_model_seed_names': len(seeds),
                        'new_model_vocabulary': len(seeds - baseline),
                        'target_visual_witnesses': len(target),
                        'joint_wrapper_rules': sum(map(len, rules.values())),
                        'generated_candidates': len(candidates)}


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--game', required=True, choices=sorted(snapshot.MODERN))
    parser.add_argument('--kind', required=True, choices=('material', 'image'))
    parser.add_argument('--seed-file', required=True, action='append', type=Path)
    parser.add_argument('--baseline-file', required=True, action='append', type=Path)
    parser.add_argument('--prior-candidates', action='append', type=Path, default=[])
    parser.add_argument('--output', type=Path)
    parser.add_argument('--size', action='store_true')
    args = parser.parse_args()
    shot = snapshot.read(ROOT / 'snapshots' / (args.game.lower() + '.ids'))
    if shot.game != args.game:
        raise ValueError('Capture game does not match the requested game')
    pools = shot.by_pool()
    models, visual = set(pools['xmodel']), set(pools[args.kind])
    baseline = load_models(args.baseline_file, models, args.game)
    seeds = load_models(args.seed_file, models, args.game)
    target = {n for n in corpus(args.kind, args.game)
              if snapshot.fnv1a(n, args.game, args.kind) & snapshot.ID_MASK in visual}
    candidates, report = generate(baseline, seeds, target)
    prior = {row_name(row)[0] for path in args.prior_candidates
             for row in path.read_text(encoding='utf-8-sig').splitlines() if row.strip()}
    removed = len(candidates & prior)
    candidates -= prior
    report.update(game=args.game, kind=args.kind, prior_candidates_removed=removed,
                  candidates=len(candidates), known_target_controls=len(candidates & target),
                  input_sha256={str(p): hashlib.sha256(p.read_bytes()).hexdigest()
                                for p in args.seed_file + args.baseline_file + args.prior_candidates})
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
