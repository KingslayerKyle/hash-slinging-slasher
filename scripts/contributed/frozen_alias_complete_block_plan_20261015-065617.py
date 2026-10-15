"""Derive and replay a frozen complete-block alias product from declared source inputs.

  python contrib/frozen_alias_complete_block_plan_20261015.py \
    --source-rev 3d42c005d5405af8b225958bef09a041e9ada0be \
    --frozen-input-dir logs/gpu_sound_20261015/final_alias_campaign_factors \
    --output-dir logs/replayed_alias_complete_block_plan

For a new source measurement, omit --frozen-input-dir and supply one or more
--exclude-file plain-name files of locally generated aliases. Without explicit
exclusion files, verified keyed sound_alias rows under findings/ are gathered.
That normal mode derives everything from the pinned tables and current captures;
it needs no previous measurement, training, heldout or factor files.

The declared input directory contains measurement.json and plain-name training,
heldout and local_generated_exclusions files. This builder does NOT load or copy
previous factors. It restores both alias tables from the pinned Git revision,
checks the seven capture identities, removes the explicit local descendants,
and reproduces the deterministic SHA256(name)[0] % 5 training/heldout split.

From training names only, take whole one/two-token underscore endings. An ending
needs three distinct cores, each observed with another ending at that SAME depth.
At those cuts take complete final six-character blocks, which may include an
underscore; each block needs three distinct source cores. Beginnings are those
source cores minus six characters. Never cross independent character alphabets.
Heldout names validate expression but never teach factors or witnesses.

All aliases share the same FNV basis and folded lookup policy across seven games.
A joint search may therefore hash the finite product once against a typed union.
Its returned names still need separate ordinary per-game sound_alias confirmation,
including modern full-64-bit and legacy masked-63-bit output. A returned-hit replay
must report its actual stream length; retain the full product manifest separately.
Select ONLY sound_alias in config.toml before sizing or running aliases.plan.txt;
pass an explicit --game for the intended target.

This is a CPU-only generator, not a GPU backend or launcher. It writes only its
requested output directory and never modifies findings, config, claims or search
state. --size validates and reconstructs without writing. Spent by these frozen
source, split, six-character factors and one/two-token ending inputs; do not widen
or replay unchanged products to bypass fingerprints.
"""
import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT=next((p for p in [Path.cwd(),*Path(__file__).resolve().parents] if (p/'scripts/snapshot.py').is_file()),None)
if ROOT is None:raise SystemExit('Run inside a solver checkout')
sys.path.insert(0,str(ROOT/'scripts'))
import snapshot
TOKEN=re.compile(r'[a-z0-9]+')
WIDTH=6

def byte_digest(data):return hashlib.sha256(data).hexdigest()
def names_digest(names):return byte_digest(('\n'.join(sorted(names))+'\n').encode())

def plain_names(path):
    """Plain names, never CSV or comments; reject silent normalization."""
    rows=path.read_text(encoding='utf8').splitlines()
    for number,name in enumerate(rows,1):
        if not name or not name.isascii() or name!=name.strip().lower() or any(ord(c)<32 for c in name):
            raise ValueError(f'{path}:{number}: expected an exact canonical plain name')
    if len(rows)!=len(set(rows)):raise ValueError(f'{path}: duplicate frozen names')
    return set(rows)

def cuts(name):
    words=name.split('_')
    for depth in (1,2):
        if len(words)<=depth+1 or not all(TOKEN.fullmatch(t) for t in words):continue
        yield depth,'_'.join(words[:-depth]),'_'+'_'.join(words[-depth:])

def expressed(name,begins,blocks,ends):
    for _,core,end in cuts(name):
        if end in ends and core[:-WIDTH] in begins and core[-WIDTH:] in blocks:return True
    return len(name)>WIDTH and name[:-WIDTH] in begins and name[-WIDTH:] in blocks

def derive(train):
    families=defaultdict(set)
    for name in train:
        for depth,core,end in cuts(name):families[depth,core].add(end)
    suffix_witnesses=defaultdict(set)
    for (depth,core),tails in families.items():
        if len(tails)>=2:
            for tail in tails:suffix_witnesses[tail].add(core)
    ends={end for end,cores in suffix_witnesses.items() if len(cores)>=3}
    begins=set();block_witnesses=defaultdict(set);core_sources=defaultdict(set)
    for name in train:
        for depth,core,end in cuts(name):
            if end not in ends or len(core)<=WIDTH:continue
            begins.add(core[:-WIDTH]);block_witnesses[core[-WIDTH:]].add(core);core_sources[core].add(name)
    blocks={block for block,cores in block_witnesses.items() if len(cores)>=3}
    evidence={'complete_block_examples':{},'suffix_sibling_examples':{}}
    for block in sorted(blocks):
        evidence['complete_block_examples'][block]=[{'core':core,'source_name':min(core_sources[core])}
            for core in sorted(block_witnesses[block])[:3]]
    for end in sorted(ends):
        depth=end.count('_');examples=[]
        for core in sorted(suffix_witnesses[end])[:3]:
            siblings=families[depth,core]
            assert end in siblings and len(siblings)>=2
            other=min(siblings-{end});names=[core+end,core+other]
            assert all(name in train for name in names)
            examples.append({'core':core,'depth':depth,'source_names':names})
        evidence['suffix_sibling_examples'][end]=examples
    return (begins,blocks,ends),evidence

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-rev',required=True)
    parser.add_argument('--frozen-input-dir',type=Path)
    parser.add_argument('--exclude-file',type=Path,action='append',default=[],
                        help='Explicit plain generated-alias exclusions for normal source mode')
    parser.add_argument('--output-dir',type=Path,required=True)
    parser.add_argument('--size',action='store_true')
    args=parser.parse_args();out=args.output_dir.resolve();frozen=None;input_files={}
    if args.frozen_input_dir:
        if args.exclude_file:raise ValueError('Frozen replay already declares exclusions; do not mix input modes')
        inputs=args.frozen_input_dir.resolve()
        frozen=json.loads((inputs/'measurement.json').read_text(encoding='utf8'))
        train=plain_names(inputs/'training.txt');holdout=plain_names(inputs/'heldout.txt')
        local=plain_names(inputs/'local_generated_exclusions.txt')
        if train&holdout or (train|holdout)&local:raise ValueError('Training, heldout and descendants are not independent')
        if names_digest(train)!=frozen['training_sha256'] or names_digest(holdout)!=frozen['heldout_sha256']:
            raise ValueError('Frozen split identity changed')
        input_files={part:{'path':str(inputs/(part+'.txt')),'sha256':byte_digest((inputs/(part+'.txt')).read_bytes()),'format':'plain-name-lines'}
                     for part in ('training','heldout','local_generated_exclusions')}
    else:
        local=set()
        if args.exclude_file:
            for path in args.exclude_file:
                local.update(plain_names(path))
                input_files[str(path)]={'path':str(path),'sha256':byte_digest(path.read_bytes()),'format':'plain-name-lines'}
        else:
            for path in (ROOT/'findings').rglob('sound_alias*.txt'):
                for number,row in enumerate(path.read_text(encoding='utf8').splitlines(),1):
                    if not row:continue
                    raw,sep,name=row.partition(',')
                    if not sep or not name.isascii() or name!=name.strip().lower():
                        raise ValueError(f'{path}:{number}: malformed keyed alias finding')
                    key=int(raw,16)
                    if not 0<=key<2**64 or snapshot.fnv1a(name,'BLACKOP7','sound_alias')&snapshot.ID_MASK!=key&snapshot.ID_MASK:
                        raise ValueError(f'{path}:{number}: finding key does not reproduce')
                    local.add(name)
                input_files[str(path)]={'path':str(path),'sha256':byte_digest(path.read_bytes()),'format':'keyed-alias-findings'}
    held={};capture_identities={}
    games=sorted(frozen['capture_sha256'] if frozen else snapshot.MODERN|{'BLKOPS04','BLKOPSCW'})
    for game in games:
        path=ROOT/'snapshots'/f'{game.lower()}.ids'
        actual=byte_digest(path.read_bytes())
        if frozen and actual!=frozen['capture_sha256'][game]:raise ValueError('Source capture identity changed')
        shot=snapshot.read(path)
        if shot.game!=game:raise ValueError('Wrong capture game')
        held[game]=set(shot.by_pool()['sound_alias'])
        capture_identities[game]={'snapshot_sha256':actual,'census_sha256':byte_digest(path.with_suffix('.pools.txt').read_bytes()),
                                'alias_pool_index':shot.pools.index('sound_alias')}
    union=set().union(*held.values())
    def git(*words):return subprocess.check_output(['git','-C',str(ROOT/'cod-name-db'),*words])
    commit=git('rev-parse','--verify',args.source_rev+'^{commit}').decode().strip()
    public=set();source_digests={}
    for table in ('fnv1a_soundbanks_aliases','fnv1a_soundbanks_aliases_v2'):
        expected=frozen['source_table_sha256'][table] if frozen else None
        data=git('show',commit+':csv/'+table+'.csv');actual=byte_digest(data)
        # Git stores LF, while a Windows checkout can have CRLF. Compare only
        # whole-line encodings; asset-name bytes within each row are unchanged.
        lf=data.replace(b'\r\n',b'\n')
        equivalent={actual,byte_digest(lf),byte_digest(lf.replace(b'\n',b'\r\n'))}
        if frozen and expected not in equivalent:raise ValueError('Pinned source-table identity changed')
        source_digests[table]={'git_blob_sha256':actual,'frozen_checkout_sha256':expected}
        public.update(n for n in snapshot.database_names(table,data.decode('utf8').splitlines()) if n.isascii() and n==n.strip().lower())
    public_keys={n:snapshot.fnv1a(n,'BLACKOP7','sound_alias')&snapshot.ID_MASK for n in public}
    source={n for n,key in public_keys.items() if key in union and n not in local}
    rebuilt_train={n for n in source if hashlib.sha256(n.encode()).digest()[0]%5!=0}
    if frozen:
        if source!=train|holdout or rebuilt_train!=train:raise ValueError('Declared sources do not reproduce the frozen split')
    else:train=rebuilt_train;holdout=source-train
    factors,evidence=derive(train);begins,blocks,ends=factors
    expected=frozen['measurements']['whole6'] if frozen else None
    digests={role:names_digest(values) for role,values in zip(('begin','stem','end'),factors)}
    if frozen and digests!=expected['factor_sha256']:raise ValueError('Derived complete factor identity changed')
    cells=len(begins)*len(blocks)*(len(ends)+1)
    if frozen and cells!=expected['cells']:raise ValueError('Candidate count changed')
    controls={game:0 for game in held}
    for name in holdout:
        if expressed(name,begins,blocks,ends):
            for game,keys in held.items():
                if public_keys[name] in keys:controls[game]+=1
    if frozen and controls!={g:v.get('independent_heldout',0) for g,v in expected['heldout_controls_by_game'].items()}:
        raise ValueError('Held-out reconstruction controls changed')
    report={'method':'frozen complete six-character alias blocks before witnessed whole endings','source_commit':commit,
        'source_table_sha256':source_digests,'capture_identities':capture_identities,
        'input_mode':'frozen-replay' if frozen else 'source-revision','input_files':input_files,
        'training_names':len(train),'heldout_names':len(holdout),'local_generated_exclusions':len(local),
        'training_sha256':names_digest(train),'heldout_sha256':names_digest(holdout),
        'whole_block_width':WIDTH,'suffix_token_depths':[1,2],'minimum_distinct_core_witnesses':3,
        'factors':{'begin':len(begins),'stem':len(blocks),'end':len(ends)},'factor_value_sha256':digests,
        'candidate_cells':cells,'implicit_empty_cells':len(begins)*len(blocks),
        'independent_heldout_controls_by_game':controls,'descendants_train_rules':False,
        'target_policy':'sound_alias only; shared standard FNV basis, folded lookup63; modern output64 and legacy output63',
        'novelty_scope':frozen['novelty_scope'] if frozen else 'Source regeneration does not prove novelty; compare prior factors and current fingerprints before any search.',
        'official_confirmation_still_required':True}
    if args.size:print(json.dumps(report));return
    if out.exists():raise ValueError('Choose a fresh output directory; never overwrite frozen products')
    out.mkdir(parents=True)
    for role,values in zip(('begin','stem','end'),factors):
        (out/(role+'.txt')).write_text(''.join('0,'+value+'\n' for value in sorted(values)),encoding='utf8')
    report['factor_file_sha256']={role:byte_digest((out/(role+'.txt')).read_bytes()) for role in ('begin','stem','end')}
    plan=('label: frozen independent all-game complete six-character alias block product\n'
          'describe: pinned source-verified alias tables; local descendants excluded; frozen independent source split; whole blocks and whole sibling endings each need three distinct source cores; heldout names never train; aliases only; see measurement.json\n'
          'game: BLACKOP7\n'+''.join(f'{role}: @{(out/(role+".txt")).as_posix()}\n' for role in ('begin','stem','end'))+
          'bare: no\nfold: yes\n')
    (out/'aliases.plan.txt').write_text(plan,encoding='utf8')
    (out/'factor_witnesses.json').write_text(json.dumps(evidence,separators=(',',':'))+'\n',encoding='utf8')
    (out/'measurement.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'output':str(out),'cells':cells,'factors':report['factors'],'file_sha256':report['factor_file_sha256'],
                      'heldout_controls':controls,'source_and_factors_rederived':True}))

if __name__=='__main__':main()
