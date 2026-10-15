"""Freeze only independently verified productive destinations of a joint image probe.

The source image factor product stays byte-for-byte unchanged. A private joint
diagnostic must have excluded every BO7 image key and all then-known/claimed
keys, rehashed sparse results on CPU and checked each destination image pool.
This builder independently rechecks every supplied row and freezes one ordinary
plan per positive destination, not a blind game rotation. The vocabulary remains
borrowed from the stated source game; it is not newly learned target grammar.

  python contrib/freeze_productive_borrowed_image_plans_20261015.py \
    --diagnostic-dir logs/gpu_sound_20261015/joint_modern_image_factor_probe \
    --product public_prefix --output-dir contrib/borrowed_public_image_prefix_20261015

Run each generated plan through the normal official readiness, image-only pool
selection, fingerprint, exclusions, validation and submission path. This script
never searches, modifies settings/findings, invokes a GPU or submits. --size
performs all source and typed-result checks without writing output. Spent by the
frozen source factor digests and measured productive destinations; do not rebuild
unchanged plans to bypass fingerprints. All timestamps are provenance, not a rule.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT=next(p for p in [Path.cwd(),*Path(__file__).resolve().parents] if (p/'scripts/snapshot.py').is_file())
sys.path.insert(0,str(ROOT/'scripts'))
import snapshot

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def load(path):
    return json.loads(path.read_text(encoding='utf-8'))

def values(path):
    out=set()
    for row in path.read_text(encoding='utf-8').splitlines():
        if not row or row.startswith('#'):continue
        value=row.partition(',')[2] if ',' in row else row
        if not value or not value.isascii() or value!=value.strip().lower():
            raise ValueError('Expected frozen nonempty normalized ASCII factors')
        out.add(value)
    return out

def decomposition(name,factors,allow_empty):
    begins,pairs,ends=factors
    for i in range(1,len(name)-1):
        if name[:i] in begins and name[i:i+2] in pairs:
            end=name[i+2:]
            if end in ends or (allow_empty and not end):
                return {'begin':name[:i],'stem':name[i:i+2],'end':end}
    return None

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--diagnostic-dir',type=Path,required=True)
    parser.add_argument('--product',required=True)
    parser.add_argument('--output-dir',type=Path,required=True)
    parser.add_argument('--size',action='store_true')
    args=parser.parse_args()
    diagnostic=args.diagnostic_dir.resolve();out=args.output_dir.resolve()
    prepared=load(diagnostic/'prepared.json');verified=load(diagnostic/'verified.json')
    product=prepared['products'][args.product];result=verified['products'][args.product]
    if not result['all_sparse_results_cpu_rehashed_for_each_game'] or not result['exact_factor_provenance_verified']:
        raise ValueError('Diagnostic has not passed independent result validation')
    source_plan=Path(product['source_plan']);source=source_plan.parent
    for part,expected in product['source_factor_sha256'].items():
        if digest(source/f'{part}.txt')!=expected:raise ValueError('Source factors changed')
    factors=[values(source/f'{part}.txt') for part in ('begin','stem','end')]
    if any(len(p)!=2 for p in factors[1]):raise ValueError('Expected complete pair factors')
    count=len(factors[0])*len(factors[1])*(len(factors[2])+1)
    if count!=product['candidate_cells'] or count!=result['candidate_cells']:raise ValueError('Candidate-count mismatch')
    bo7_path=ROOT/'snapshots/blackop7.ids'
    if digest(bo7_path)!=prepared['capture_identities']['BLACKOP7']['capture_sha256']:
        raise ValueError('BO7 exclusion capture changed')
    bo7=set(snapshot.read(bo7_path).by_pool()['image'])
    provenance=load(diagnostic/'provenance.json').get(args.product,{})
    destinations={}
    for game,expected_count in sorted(result['unique_current_unresolved_keys_by_game'].items()):
        if not expected_count:continue
        if game not in snapshot.MODERN or game=='BLACKOP7':raise ValueError('Unexpected destination game')
        capture=ROOT/'snapshots'/f'{game.lower()}.ids';shot=snapshot.read(capture)
        identity=prepared['capture_identities'][game]
        if shot.game!=game or digest(capture)!=identity['capture_sha256'] or digest(capture.with_suffix('.pools.txt'))!=identity['census_sha256']:
            raise ValueError('Destination capture/census changed')
        held=set(shot.by_pool()['image']);rows={}
        hitfile=diagnostic/f'{args.product}.{game}.hits.txt'
        for row in hitfile.read_text(encoding='utf-8').splitlines():
            raw,sep,name=row.partition(',');key=int(raw,16)&snapshot.ID_MASK
            if not sep or snapshot.fnv1a(name,game,'image')&snapshot.ID_MASK!=key or key not in held or key in bo7:
                raise ValueError('Diagnostic row fails typed independent rehash or BO7 subtraction')
            split=decomposition(name,factors,args.product!='new_suffix')
            if split is None or game not in provenance[name]['games']:raise ValueError('Missing exact factor or destination provenance')
            rows[key]={'name':name,'factors':split}
        if len(rows)!=expected_count:raise ValueError('Verified diagnostic key count changed')
        destinations[game]={'provisional_unique_keys':len(rows),
            'known_non_bo7_typed_control_keys':product['known_non_bo7_typed_control_keys'][game],
            'diagnostic_hits_sha256':digest(hitfile),'capture':identity,
            'candidate_provenance':{f'{k:016x}':v for k,v in sorted(rows.items())}}
    if not destinations:raise ValueError('No measured productive destination')
    report={'source_game':'BLACKOP7','vocabulary':'borrowed modern image source prefix delta and frozen complete pairs/suffixes',
            'source_plan':str(source_plan),'source_factor_sha256':product['source_factor_sha256'],
            'candidate_cells_per_plan':count,'source_product':args.product,
            'diagnostic_inputs':{p:{'path':str(diagnostic/p),'sha256':digest(diagnostic/p)} for p in ('prepared.json','verified.json','provenance.json')},
            'destinations':destinations,'required_pool_selection':['image'],
            'boundary':'Provisional measured matches; each destination still requires ordinary official exclusions, confirmation and submission.'}
    source_measurement=source/'measurement.json'
    if source_measurement.is_file():
        report['source_measurement']={'path':str(source_measurement),'sha256':digest(source_measurement),
                                      'data':load(source_measurement)}
    source_prefix_provenance=source/'prefix_provenance.json'
    if source_prefix_provenance.is_file():
        sources=load(source_prefix_provenance)
        used={row['factors']['begin'] for details in destinations.values() for row in details['candidate_provenance'].values()}
        report['source_prefix_witnesses']={'path':str(source_prefix_provenance),'sha256':digest(source_prefix_provenance),
            'productive_prefix_sources':{prefix:sources[prefix] for prefix in sorted(used)}}
    if args.size:
        print(json.dumps({'candidate_cells_per_plan':count,'productive_destinations':{g:v['provisional_unique_keys'] for g,v in destinations.items()}}));return
    if out.exists():raise ValueError('Choose a fresh output directory; never overwrite frozen plans')
    out.mkdir(parents=True)
    for game,details in destinations.items():
        folder=out/game.lower();folder.mkdir()
        for part in ('begin','stem','end'):
            (folder/f'{part}.txt').write_bytes((source/f'{part}.txt').read_bytes())
            assert digest(folder/f'{part}.txt')==product['source_factor_sha256'][part]
        desc=(f'Unchanged borrowed BO7 modern-image source prefix vocabulary; joint diagnostic excluded every BO7 image key and current known/claimed keys; '
              f'{details["provisional_unique_keys"]} independently CPU-rehashed provisional {game} image keys; '
              f'{details["known_non_bo7_typed_control_keys"]} typed known non-BO7 image reconstruction controls; '
              'see ../measurement.json for source/diagnostic digests and exact hit decompositions; ordinary official exclusions still required; image only')
        text=(f'label: {game} measured borrowed modern image public prefix delta\ndescribe: {desc}\ngame: {game}\n'+
              ''.join(f'{part}: @{(folder/(part+".txt")).as_posix()}\n' for part in ('begin','stem','end'))+
              'bare: no\nfold: yes\n')
        (folder/'images.plan.txt').write_text(text,encoding='utf-8')
        details['plan']=str(folder/'images.plan.txt')
    (out/'measurement.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'output_dir':str(out),'plans':{g:v['plan'] for g,v in destinations.items()},'candidate_cells_per_plan':count}))

if __name__=='__main__':main()
