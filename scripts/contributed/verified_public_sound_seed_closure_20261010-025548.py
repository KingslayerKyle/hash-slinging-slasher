"""Derive sound-file variants opened by an explicit verified public seed commit.

Read only newly added sound_asset submissions between the supplied commits.
Every spelling must reproduce its key in the correct selected capture pool.
Borrow complete encoding tails and take/encoding pairs only from that same
target directory, preserving take padding and literal separators. Fixed reviewed
dependencies are digest-checked before import. Offline Git reads and candidates
only; no games, downloads, findings/config changes or model search.
Normal confirm_list and submit provide current exclusions and final validation.
Spent by unchanged public seeds and witnessed target-directory conventions.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

ROOT=next((p for p in [Path.cwd(),*Path(__file__).resolve().parents]
           if (p/'scripts/snapshot.py').is_file()),None)
if ROOT is None:raise SystemExit('Run inside a solver checkout')

def reviewed(filename,digest,label):
    path=ROOT/'scripts/contributed'/filename
    if hashlib.sha256(path.read_text(encoding='utf-8').encode()).hexdigest()!=digest:
        raise SystemExit('Reviewed dependency changed; review it before reuse')
    spec=importlib.util.spec_from_file_location(label,path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

reader=reviewed('verified_alias_seed_terminal_four_delta_20261010-021713.py',
                '0ceb5ee182b0f6702230eeefecf6434b2b4187ad0eb59ecabcc0da4d4c576d72','seed_reader')
method=reviewed('verified_sound_delta_closure_20261009-183600.py',
                '3dfd5788a2177c427aaf332a2a6c8ac79783cba438cef57420ad00a683cc3edb','sound_closure')
snapshot=method.snapshot

def read_seeds(base,head,game,held):
    paths=reader.git('diff','--name-only','--diff-filter=A',base,head,'--','submissions').decode().splitlines()
    paths=[p for p in paths if Path(p).parent.name.split('_')[1]==game and
           Path(p).name.startswith('sound_asset_') and p.endswith('.txt')]
    seeds=set()
    for _,text in reader.blobs(head,paths):
        for row in text.splitlines():
            raw,name=row.split(',',1)
            key=snapshot.fnv1a(name,game,'sound_asset')&snapshot.ID_MASK
            if int(raw,16)!=key or key not in held:raise ValueError('Seed key or selected sound pool failed verification')
            if not name.isascii() or name!=name.strip().lower():raise ValueError('Seed spelling is not normalized ASCII')
            seeds.add(name)
    if not seeds:raise ValueError('No newly added verified sound seeds')
    return seeds

def main():
    parser=argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--game',choices=sorted(snapshot.MODERN),required=True)
    parser.add_argument('--baseline-commit',required=True)
    parser.add_argument('--seed-commit',required=True)
    args=parser.parse_args()
    base,head=reader.commit(args.baseline_commit),reader.commit(args.seed_commit)
    shot=snapshot.read(ROOT/'snapshots'/(args.game.lower()+'.ids'))
    if shot.game!=args.game:raise ValueError('Wrong target capture game')
    held=set(shot.by_pool()['sound_asset'])
    seeds=read_seeds(base,head,args.game,held)
    names=method.corpus(args.game)|seeds
    candidates,report=method.generate(seeds,names,held,args.game)
    report.update(game=args.game,baseline=base,seed=head)
    print(json.dumps(report),file=sys.stderr)
    for name in sorted(candidates):print('0,'+name)

if __name__=='__main__':main()
