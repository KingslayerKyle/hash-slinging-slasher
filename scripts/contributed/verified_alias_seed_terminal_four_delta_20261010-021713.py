"""Solve only four terminal alias bytes newly reachable from a supplied public seed commit.

Seeds must reproduce full modern alias keys and belong to their source game's
alias capture. The baseline commit's merged aliases and current verified table
vocabulary exclude previously held four-byte prefixes. BO7 and MW4 also exclude
prefixes covered by the already-ground five-byte domain. Existing two/three-byte
domains, published keys and current claims are excluded. No model search.

Uses the fixed reviewed terminal-four solver from the public library, compiled
locally. Git reads are offline and shell-free. This generator prints candidates;
normal confirm_list and submit are required. Repeating unchanged sources is spent.
"""
import argparse
from collections import defaultdict
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

ROOT=next((p for p in [Path.cwd(),*Path(__file__).resolve().parents]
           if (p/'scripts/snapshot.py').is_file()),None)
if ROOT is None:raise SystemExit('Run inside a solver checkout')
HELPER=ROOT/'scripts/contributed/verified_alias_terminal_four_20261010-003439.py'
if hashlib.sha256(HELPER.read_text(encoding='utf-8').encode()).hexdigest()!='7b6835568f8c74833caa84a72eda050c37bda56f5dffe747d613ec0a0c289dcf':
    raise SystemExit('The reviewed solver dependency changed; review it before reuse')
spec=importlib.util.spec_from_file_location('reviewed_terminal_four',HELPER)
helper=importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper)
snapshot=helper.snapshot

def git(*args):return subprocess.check_output(['git','-C',str(ROOT),*args])

def commit(ref):
    return git('rev-parse','--verify','--end-of-options',ref+'^{commit}').decode().strip()

def blobs(head,paths):
    if not paths:return []
    data=subprocess.check_output(['git','-C',str(ROOT),'cat-file','--batch'],
        input=''.join(head+':'+path+'\n' for path in paths).encode())
    cursor=0
    out=[]
    for path in paths:
        end=data.index(b'\n',cursor)
        _,kind,size=data[cursor:end].split()
        if kind!=b'blob':raise ValueError('Expected a plain vocabulary file')
        size=int(size)
        out.append((path,data[end+1:end+1+size].decode('utf-8')))
        cursor=end+2+size
    if cursor!=len(data):raise ValueError('Unexpected Git blob response')
    return out

def prefixes(baseline,roots,held,game):
    mask=snapshot.ID_MASK
    def target(names):return {n for n in names if len(n)>=12 and snapshot.fnv1a(n,game,'sound_alias')&mask in held}
    old=target(baseline)
    result={n[:-4] for n in target(roots)}-{n[:-4] for n in old}
    if game in {'BLACKOP7','MODWAR7'}:
        old5={n[:-5] for n in old if len(n)>=13}
        result={p for p in result if p[:-1] not in old5}
    return result

def load_seeds(baseline,seed):
    paths=git('diff','--name-only','--diff-filter=A',baseline,seed,'--','submissions').decode().splitlines()
    paths=[p for p in paths if Path(p).name.startswith('sound_alias_') and p.endswith('.txt')]
    roots=set()
    cache={}
    for path,text in blobs(seed,paths):
        game=Path(path).parent.name.split('_')[1]
        if game not in snapshot.MODERN:continue
        if game not in cache:
            shot=snapshot.read(ROOT/'snapshots'/(game.lower()+'.ids'))
            if shot.game!=game:raise ValueError('Wrong source capture game')
            cache[game]=set(shot.by_pool()['sound_alias'])
        for row in text.splitlines():
            raw,name=row.split(',',1)
            key=snapshot.fnv1a(name,game,'sound_alias')
            if int(raw,16)!=key or key&snapshot.ID_MASK not in cache[game]:
                raise ValueError('Seed key or source-game alias pool failed verification')
            if name.isascii() and name==name.strip().lower():roots.add(name)
    return roots

def main():
    parser=argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--game',choices=sorted(snapshot.MODERN),required=True)
    parser.add_argument('--baseline-commit',required=True)
    parser.add_argument('--seed-commit',required=True)
    parser.add_argument('--sample',type=int,default=0)
    args=parser.parse_args()
    if args.sample<0:parser.error('sample must be nonnegative')
    baseline_ref,seed_ref=commit(args.baseline_commit),commit(args.seed_commit)
    roots=load_seeds(baseline_ref,seed_ref)
    baseline=helper.corpus()-roots
    paths=[p for p in git('ls-tree','-r','--name-only',baseline_ref,'all_names').decode().splitlines() if p.endswith('/sound_alias.txt')]
    for _,text in blobs(baseline_ref,paths):
        for row in text.splitlines():
            raw,name=row.split(',',1)
            if snapshot.fnv1a(name,args.game,'sound_alias')&snapshot.ID_MASK==int(raw,16)&snapshot.ID_MASK:baseline.add(name)
    names=baseline|roots
    shot=snapshot.read(ROOT/'snapshots'/(args.game.lower()+'.ids'))
    if shot.game!=args.game:raise ValueError('Wrong target capture game')
    held=set(shot.by_pool()['sound_alias'])
    new_prefixes=prefixes(baseline,roots,held,args.game)
    _,old,ids=helper.inputs(names,held,snapshot.known_hashes(game=args.game))
    for row in (ROOT/'state/claimed.txt').read_text().splitlines():
        try:ids.discard(int(row,16)&snapshot.ID_MASK)
        except ValueError:pass
    population=len(ids)
    if args.sample and population>args.sample:
        ordered=sorted(ids)
        ids={ordered[i*population//args.sample] for i in range(args.sample)}
    found=defaultdict(list)
    for name in helper.run_solver(new_prefixes,ids):
        key=snapshot.fnv1a(name,args.game,'sound_alias')&snapshot.ID_MASK
        if key not in ids or name[:-4] not in new_prefixes:raise ValueError('Solver output failed full-hash domain verification')
        if name in names or name[:-2] in old[0] or name[:-3] in old[1]:continue
        found[key].append(name)
    safe=sorted(v[0] for v in found.values() if len(v)==1)
    print(json.dumps({'game':args.game,'baseline':baseline_ref,'seed':seed_ref,
        'new_prefixes':len(new_prefixes),'population':population,'searched_ids':len(ids),
        'verified_new':len(safe),'ambiguous_ids':sum(len(v)>1 for v in found.values())}),file=sys.stderr)
    for name in safe:print(name)

if __name__=='__main__':main()
