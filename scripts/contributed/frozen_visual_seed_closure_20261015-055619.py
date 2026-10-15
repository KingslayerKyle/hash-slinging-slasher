"""Apply frozen, independently trained visual relations only to explicit fresh seeds.

Run: python contrib/frozen_visual_seed_closure.py --game BLACKOP7 \
  --source-rev 3d42c00 --seed-image findings/blackop7/<run>/image.txt \
  --exclude-pair-plan-dir <executed-factor-dir> --output-dir logs/visual-closure

Reads pinned source-hash-verified image/material tables, capture pools, supplied
image seeds and normal current exclusions. Every locally confirmed image and
material is excluded from relation training. Freeze complete image-opening,
image-ending, material-directory triples supported by three distinct source
cores. Apply those fixed triples in either direction only to supplied roots or
new typed capture matches reached from them. Descendants never train rules.

Writes typed candidate lists, provisional hits, frozen training exclusions,
rules, provenance and an aggregate report. Does not confirm, write findings,
modify configuration or submit. Reusable only for a genuinely fresh seed delta.
An explicit finite candidate/round budget errors instead of calling a truncated
frontier closed. Normal typed confirmation and submission remain necessary.
Training exclusions and --exclude-*-file inputs contain plain names, including
literal commas and leading ``#`` characters. Use --exclude-*-factor-file for
historical candidate files written as explicit ``0,name`` rows; executed plan
factors use that format too. Input formats are explicit, never inferred. A frozen
training replay checks its source, exclusions and complete rules against the
saved measurement before applying any seeds.

BO7 2026-10-15: 152 new image roots applied to 706 frozen triples learned from
80,293 public images and 161,718 public materials after excluding all local
generated training names. 25,660 training pair controls. 1,300 material
candidates reached seven provisional fresh material keys and five known
controls. Their fixed reverse relations produced 472 new-to-prior-space image
candidates (333 earlier candidates removed), two known controls and no fresh
image keys. The two-round frontier closed. This is a measurement; confirm the
full material.candidates.txt with --script pointing at this generator, with
only material selected. Do not substitute a seven-hit-only stream for its scope.
"""
import argparse
from collections import defaultdict
import hashlib
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


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_plain_names(path):
    """Read a name-per-line artifact without interpreting commas as CSV."""
    for row in path.read_text(encoding='utf8').splitlines():
        if not row:
            continue
        yield row.strip().lower()


def read_factor_names(path):
    """Read the explicit zero-count factor format, preserving the entire name."""
    for number, row in enumerate(path.read_text(encoding='utf8').splitlines(), 1):
        if not row or row.startswith('#'):
            continue
        raw, sep, name = row.partition(',')
        if not sep or raw != '0':
            raise ValueError(f'{path}:{number}: expected an explicit 0,name factor row')
        if name:
            yield name.strip().lower()


def serialized_rules(rules):
    return [{'image_prefix': p, 'image_suffix': s, 'material_directory': d,
             'cores': sorted(cores)} for (p, s, d), cores in sorted(rules.items())]


def verify_frozen_training(directory, commit, source_digests, generated, training, rules):
    """Reject a changed freeze rather than silently relearning a different graph."""
    old = json.loads((directory/'measurement.json').read_text(encoding='utf8'))
    checks = {
        'source_commit': commit,
        'source_table_sha256': source_digests,
        'training_descendants_excluded': {k: len(v) for k, v in generated.items()},
        'training': {k: len(v) for k, v in training.items()},
        'frozen_triples': len(rules),
        'training_pair_controls': sum(map(len, rules.values())),
        'frozen_training_exclusion_sha256': {
            k: sha(directory/(k+'.training_exclusions.txt')) for k in generated},
    }
    for key, actual in checks.items():
        if old.get(key) != actual:
            raise ValueError(f'Frozen training replay changed {key}')
    old_rules = json.loads((directory/'rules.json').read_text(encoding='utf8'))
    if old_rules != serialized_rules(rules):
        raise ValueError('Frozen training replay changed the complete rule witnesses')


def load_seeds(paths, held, game):
    result = set()
    for path in paths:
        for row in path.read_text(encoding='utf8').splitlines():
            if not row:
                continue
            raw, sep, name = row.partition(',')
            name = name if sep else raw
            if not name or name != name.strip().lower() or not name.isascii():
                raise ValueError('Seeds must be canonical ASCII image names')
            key = snapshot.fnv1a(name, game, 'image') & snapshot.ID_MASK
            if sep and key != int(raw, 16) & snapshot.ID_MASK:
                raise ValueError('Seed spelling does not reproduce its stored key')
            if key not in held:
                raise ValueError('Seed is not held in the target image pool')
            result.add(name)
    return result


def learn(images, materials):
    directories = defaultdict(set)
    for name in materials:
        if '*' not in name:
            directory, slash, core = name.rpartition('/')
            directories[core].add(directory + slash)
    witnesses = defaultdict(set)
    for name in images:
        if any(c in name for c in '&~*/'):
            continue
        parts = name.split('_')
        for left in (0, 1, 2):
            for right in (0, 1, 2):
                if len(parts) - left - right < 2:
                    continue
                core = '_'.join(parts[left:len(parts)-right if right else None])
                prefix = '_'.join(parts[:left]) + ('_' if left else '')
                suffix = ('_' if right else '') + '_'.join(parts[-right:] if right else [])
                for directory in directories.get(core, ()):
                    witnesses[prefix, suffix, directory].add(core)
    return {rule: cores for rule, cores in witnesses.items() if len(cores) >= 3}


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--game', choices=sorted(snapshot.MODERN), required=True)
    ap.add_argument('--source-rev', required=True)
    ap.add_argument('--seed-image', type=Path, action='append', required=True)
    ap.add_argument('--exclude-image-file', type=Path, action='append', default=[])
    ap.add_argument('--exclude-material-file', type=Path, action='append', default=[])
    ap.add_argument('--exclude-image-factor-file', type=Path, action='append', default=[],
                    help='Prior image candidates in explicit 0,name format (not plain names)')
    ap.add_argument('--exclude-material-factor-file', type=Path, action='append', default=[],
                    help='Prior material candidates in explicit 0,name format (not plain names)')
    ap.add_argument('--exclude-pair-plan-dir', type=Path, action='append', default=[])
    ap.add_argument('--frozen-training-exclusions-dir', type=Path,
                    help='Replay the saved image/material training exclusions from an earlier measurement')
    ap.add_argument('--output-dir', type=Path, required=True)
    a = ap.parse_args()
    pools = snapshot.read(str(ROOT / 'snapshots' / (a.game.lower()+'.ids')))
    if pools.game != a.game:
        raise ValueError('Wrong capture game')
    held = {k: set(pools.by_pool()[k]) for k in ('image', 'material')}
    roots = load_seeds(a.seed_image, held['image'], a.game)
    commit = subprocess.check_output(['git', '-C', str(ROOT / 'cod-name-db'), 'rev-parse', '--verify', a.source_rev+'^{commit}']).decode().strip()
    training = {}
    source_digests = {}
    generated = {k: set() for k in held}
    for kind in held:
        if a.frozen_training_exclusions_dir:
            generated[kind].update(read_plain_names(a.frozen_training_exclusions_dir/(kind+'.training_exclusions.txt')))
        for path in ([] if a.frozen_training_exclusions_dir else (ROOT / 'findings').rglob(kind+'*.txt')):
            for row in path.read_text(encoding='utf8').splitlines():
                raw, sep, name = row.partition(',')
                if not sep:
                    continue
                try: key = int(raw, 16) & snapshot.ID_MASK
                except ValueError: continue
                if snapshot.fnv1a(name, a.game, kind) & snapshot.ID_MASK == key:
                    generated[kind].add(name.strip().lower())
        table = {'image':'fnv1a_ximages_v2', 'material':'fnv1a_xmaterials_v2'}[kind]
        data = subprocess.check_output(['git','-C',str(ROOT/'cod-name-db'),'show',commit+':csv/'+table+'.csv'])
        source_digests[kind] = hashlib.sha256(data).hexdigest()
        training[kind] = {n for n in snapshot.database_names(table, data.decode('utf8').splitlines())
                          if n.isascii() and n == n.strip().lower() and n not in generated[kind]
                          and snapshot.fnv1a(n,a.game,kind) & snapshot.ID_MASK in held[kind]}
    if roots & training['image']:
        raise ValueError('Application roots must not enter training')
    rules = learn(training['image'], training['material'])
    if a.frozen_training_exclusions_dir:
        verify_frozen_training(a.frozen_training_exclusions_dir, commit, source_digests,
                               generated, training, rules)
    previous = {'image': set(), 'material': set()}
    excluded_candidate_inputs = {k: [] for k in held}
    groups = [('image',a.exclude_image_file,'plain-name-lines',read_plain_names),
              ('material',a.exclude_material_file,'plain-name-lines',read_plain_names),
              ('image',a.exclude_image_factor_file,'zero-count-name-rows',read_factor_names),
              ('material',a.exclude_material_factor_file,'zero-count-name-rows',read_factor_names)]
    formats_by_path = {}
    for kind, paths, file_format, reader in groups:
        for path in paths:
            resolved = path.resolve()
            if resolved in formats_by_path and formats_by_path[resolved] != (kind,file_format):
                raise ValueError('A prior candidate file was supplied with conflicting kind or format')
            formats_by_path[resolved] = kind,file_format
            names = set(reader(path))
            previous[kind].update(names)
            excluded_candidate_inputs[kind].append({'path':str(path),'sha256':sha(path),
                                                     'format':file_format,'names':len(names)})
    plans = []
    for d in a.exclude_pair_plan_dir:
        begins, pairs, ends = [set(read_factor_names(d/(role+'.txt'))) for role in ('begin','stem','end')]
        plans.append((begins,pairs,ends|{''}))
    def previously_in_image_plan(name):
        for begins, pairs, ends in plans:
            # Every ending is tried as an exact suffix, allowing alternate splits.
            cuts = [len(name)] + [i for i,c in enumerate(name) if c == '_']
            for pos in cuts:
                if name[pos:] in ends and pos >= 2 and name[:pos-2] in begins and name[pos-2:pos] in pairs:
                    return True
        return False
    excluded = {k & snapshot.ID_MASK for k in snapshot.known_hashes(game=a.game)}
    for top in ('all_names','submissions','findings'):
        for path in (ROOT/top).rglob('*.txt'):
            for row in path.read_text(encoding='utf8',errors='replace').splitlines():
                raw,sep,_ = row.partition(',')
                if sep:
                    try: excluded.add(int(raw,16)&snapshot.ID_MASK)
                    except ValueError: pass
    for row in (ROOT/'state/claimed.txt').read_text().splitlines():
        try: excluded.add(int(row,16)&snapshot.ID_MASK)
        except ValueError: pass
    candidates = {k:set() for k in held}
    positives = {k:{} for k in held}
    controls = {k:set() for k in held}
    excluded_previous = {k:set() for k in held}
    provenance = {k:{} for k in held}
    frontier = {'image':roots,'material':set()}
    rounds = []
    for round_index in range(32):
        proposed = {k:{} for k in held}
        for name in frontier['image']:
            for rule in rules:
                prefix,suffix,directory = rule
                if not name.startswith(prefix) or not name.endswith(suffix):
                    continue
                core = name[len(prefix):len(name)-len(suffix) if suffix else None]
                if len(core.split('_')) >= 2:
                    proposed['material'].setdefault(directory+core, (name,rule))
        for name in frontier['material']:
            directory,slash,core = name.rpartition('/')
            for rule in rules:
                prefix,suffix,matdir = rule
                if matdir == directory+slash:
                    proposed['image'].setdefault(prefix+core+suffix,(name,rule))
        frontier = {k:set() for k in held}
        for kind in held:
            for name,(source,rule) in proposed[kind].items():
                if name in candidates[kind]:
                    continue
                if name in previous[kind] or (kind=='image' and previously_in_image_plan(name)):
                    excluded_previous[kind].add(name)
                    continue
                candidates[kind].add(name)
                key = snapshot.fnv1a(name,a.game,kind)&snapshot.ID_MASK
                if key not in held[kind]:
                    continue
                if key in excluded:
                    controls[kind].add(key)
                    continue
                if key in positives[kind]:
                    continue
                positives[kind][key] = name
                provenance[kind][name] = {'source':source,'rule':rule,'round':round_index+1}
                frontier[kind].add(name)
        rounds.append({'round':round_index+1, 'new_materials':len(frontier['material']), 'new_images':len(frontier['image'])})
        if sum(map(len,candidates.values())) > 2_000_000:
            raise ValueError('Finite candidate budget reached; frontier is not claimed closed')
        if not any(frontier.values()):
            break
    else:
        raise ValueError('Finite round budget reached; frontier is not claimed closed')
    a.output_dir.mkdir(parents=True,exist_ok=True)
    for kind in held:
        for label,names in [('candidates',candidates[kind]),('hits',positives[kind].values()),('training_exclusions',generated[kind])]:
            (a.output_dir/(kind+'.'+label+'.txt')).write_text(''.join(n+'\n' for n in sorted(names)),encoding='utf8')
    (a.output_dir/'rules.json').write_text(json.dumps(serialized_rules(rules),indent=2)+'\n',encoding='utf8')
    (a.output_dir/'provenance.json').write_text(json.dumps(provenance,indent=2)+'\n',encoding='utf8')
    report = {'game':a.game,'source_commit':commit,'source_table_sha256':source_digests,'seed_images':len(roots),
        'seed_sha256':{str(p):sha(p) for p in a.seed_image},'training':{k:len(v) for k,v in training.items()},
        'training_descendants_excluded':{k:len(v) for k,v in generated.items()},'frozen_triples':len(rules),
        'training_pair_controls':sum(map(len,rules.values())),'candidates':{k:len(v) for k,v in candidates.items()},
        'prior_candidates_excluded':{k:len(v) for k,v in excluded_previous.items()},
        'known_target_controls':{k:len(v) for k,v in controls.items()},'fresh_typed_keys':{k:len(v) for k,v in positives.items()},
        'rounds':rounds,'closed':True,'normal_confirmation_still_required':True,
        'excluded_candidate_sha256':{str(p):sha(p) for _,paths,_,_ in groups for p in paths},
        'excluded_candidate_inputs':excluded_candidate_inputs,
        'excluded_pair_plan_sha256':{str(d):{r:sha(d/(r+'.txt')) for r in ('begin','stem','end')} for d in a.exclude_pair_plan_dir},
        'frozen_training_exclusion_sha256':{k:sha(a.output_dir/(k+'.training_exclusions.txt')) for k in held}}
    (a.output_dir/'measurement.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
