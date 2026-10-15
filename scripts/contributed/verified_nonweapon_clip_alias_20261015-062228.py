"""Recover aliases through independently witnessed nonweapon animation namespaces.

Run: python contrib/verified_nonweapon_clip_alias.py --game BLACKOP7 \
  --source-rev 3d42c005d5405af8b225958bef09a041e9ada0be --out logs/clip-alias.txt
Then confirm the COMPLETE output file with only sound_alias selected and
--script contrib/verified_nonweapon_clip_alias.py. The normal confirmer owns
hash validation, current exclusions, full-64-bit modern alias output and results.

Reads pinned, source-hash-verified animation/alias tables, the selected capture,
and verified all_names/submissions/findings. Local generated descendants are
excluded from relation training, but may be application sources. Each fixed
(animation prefix, alias prefix, exact numeric take suffix) relation needs three
distinct common event cores, each at least three tokens and twelve characters.
Take siblings never count as distinct core witnesses. Weapon-class names are
excluded. A known control must retain three witnesses after its own core is
removed. Generated aliases cannot train rules or seed another round.

Writes one deduplicated plain-name candidate file, complete rule witnesses,
input digests and counts. No searches, findings/config edits, or submissions.
Reusable for genuinely fresh sources; spent by unchanged pinned independent
baseline and target-held application vocabulary. Do not widen numeric suffixes
or iteratively retrain from this method's descendants.

BO7 2026-10-15: 36,999 independent nonweapon clips and 70,814 aliases supported
199 exact relations. 97,119 factor applications yielded 77,586 unseen candidate
names, 1,550 held-out known controls, and a separate typed/current-exclusion
probe found four provisional alias keys. This inverse relation is distinct from
the old alias-to-animation probe and the vm/wm weapon-core alias plan.
"""
from pathlib import Path
from collections import defaultdict
import argparse,hashlib,json,re,subprocess,sys

ROOT=next((p for p in [Path.cwd(),*Path(__file__).resolve().parents]
           if (p/'scripts/snapshot.py').is_file()),None)
if ROOT is None:raise SystemExit('Run inside a solver checkout')
sys.path.insert(0,str(ROOT/'scripts'))
import snapshot
WEAPON=re.compile(r'(?:^|_)(ar|sm|pi|sh|lm|br|dm|sn|me|la|ww|smg|pistol|lmg|dmr|shotgun|sniper|rifle|launcher|melee|special)_[a-z0-9]+(?:_|$)')
TABLES={'sound_alias':'fnv1a_soundbanks_aliases_v2','xanim':'fnv1a_xanims_v2'}

def digest(names):
    return hashlib.sha256(''.join(n+'\n' for n in sorted(names)).encode()).hexdigest()

def splits(n):
    ts=n.split('_')
    for k in range(1,min(4,len(ts)-2)):
        core='_'.join(ts[k:])
        if len(core)>=12:yield '_'.join(ts[:k])+'_',core

def variants(n):
    yield n,''
    ts=n.split('_');tail=[]
    for _ in range(2):
        if not ts or not ts[-1].isdigit():break
        tail.insert(0,ts.pop());yield '_'.join(ts),'_'+'_'.join(tail)

def learn(anims,aliases):
    index=defaultdict(set)
    for n in anims:
        for prefix,core in splits(n):index[core].add(prefix)
    support=defaultdict(set)
    for n in aliases:
        for variant,tail in variants(n):
            for prefix,core in splits(variant):
                for animprefix in index.get(core,()):support[animprefix,prefix,tail].add(core)
    rules=defaultdict(dict)
    for (ap,p,tail),cores in support.items():
        if len(cores)>=3:rules[ap][p,tail]=cores
    return rules

def generate(anims,aliases,rules):
    candidates=set();controls=set();cells=0
    for source_name in anims:
        if WEAPON.search(source_name):continue
        for ap,core in splits(source_name):
            for (p,tail),witness in rules.get(ap,{}).items():
                cells+=1;n=p+core+tail
                if n in aliases:
                    if len(witness-{core})>=3:controls.add(n)
                else:candidates.add(n)
    return candidates,controls,cells

def main():
    ap=argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--game',required=True,choices=sorted(snapshot.MODERN))
    ap.add_argument('--source-rev',required=True)
    ap.add_argument('--out',required=True,type=Path)
    a=ap.parse_args()
    shot=snapshot.read(ROOT/'snapshots'/(a.game.lower()+'.ids'))
    if shot.game!=a.game:raise ValueError('Wrong capture game')
    held={k:set(shot.by_pool()[k]) for k in TABLES}
    commit=subprocess.check_output(['git','-C',str(ROOT/'cod-name-db'),'rev-parse','--verify',a.source_rev+'^{commit}']).decode().strip()
    generated={k:set() for k in TABLES};local={k:set() for k in TABLES}
    for kind in TABLES:
        for top in ('all_names','submissions','findings'):
            for path in (ROOT/top).rglob(kind+'*.txt'):
                for row in path.read_text(encoding='utf8',errors='replace').splitlines():
                    raw,sep,n=row.partition(',')
                    if not sep or not n:continue
                    try:key=int(raw,16)&snapshot.ID_MASK
                    except ValueError:continue
                    if snapshot.fnv1a(n,a.game,kind)&snapshot.ID_MASK!=key:continue
                    if top=='findings':generated[kind].add(n)
                    if key in held[kind]:local[kind].add(n)
    baseline={};application={};source_hashes={}
    for kind,table in TABLES.items():
        data=subprocess.check_output(['git','-C',str(ROOT/'cod-name-db'),'show',commit+':csv/'+table+'.csv'])
        source_hashes[kind]=hashlib.sha256(data).hexdigest()
        names={n for n in snapshot.database_names(table,data.decode('utf8').splitlines())
               if n.isascii() and n==n.strip().lower()}
        target={n for n in names if snapshot.fnv1a(n,a.game,kind)&snapshot.ID_MASK in held[kind]}
        baseline[kind]={n for n in target-generated[kind] if not WEAPON.search(n)}
        application[kind]=target|local[kind]
    rules=learn(baseline['xanim'],baseline['sound_alias'])
    candidates,controls,cells=generate(application['xanim'],application['sound_alias'],rules)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(''.join(n+'\n' for n in sorted(candidates)),encoding='utf8')
    serialized=[{'animation_prefix':ap,'alias_prefix':p,'alias_take':tail,'cores':sorted(witness)}
                for ap,by in sorted(rules.items()) for (p,tail),witness in sorted(by.items())]
    a.out.with_suffix('.rules.json').write_text(json.dumps(serialized,indent=2)+'\n')
    report={'game':a.game,'source_commit':commit,'source_table_sha256':source_hashes,
            'training':{k:len(v) for k,v in baseline.items()},
            'training_sha256':{k:digest(v) for k,v in baseline.items()},
            'generated_training_exclusions_sha256':{k:digest(v) for k,v in generated.items()},
            'application':{k:len(v) for k,v in application.items()},
            'application_sha256':{k:digest(v) for k,v in application.items()},
            'rules':len(serialized),'factor_applications':cells,'known_controls':len(controls),
            'candidates':len(candidates),'candidate_sha256':hashlib.sha256(a.out.read_bytes()).hexdigest(),
            'normal_typed_confirmation_required':True}
    a.out.with_suffix('.report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report))

if __name__=='__main__':main()
