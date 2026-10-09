"""Swap whole weapon identifiers inside target-held graphics conventions.

Weapons are source-hash-verified class-and-code pairs, rather than individual
tokens. Beginning and ending spellings come only from verified names of the
selected type held by the target game. Original spelling and namespaces stay
literal. Confirm the emitted plan only against that same asset type.
"""
import argparse
from collections import Counter
import json
from pathlib import Path
import re
import sys

ROOT=Path(__file__).resolve().parent
while ROOT!=ROOT.parent and not (ROOT/'scripts/snapshot.py').is_file():ROOT=ROOT.parent
if not (ROOT/'scripts/snapshot.py').is_file():ROOT=Path.cwd()
sys.path.insert(0,str(ROOT/'scripts'))
import snapshot

TABLES={'image':'fnv1a_ximages_v2','material':'fnv1a_xmaterials_v2','xanim':'fnv1a_xanims_v2','sound_alias':'fnv1a_soundbanks_aliases_v2'}
WEAPON=re.compile(r'(?:^|[_/])(?:sat|t10|jup|iw9|s4|iw8|t9|rex|s6)_((?:ar|sm|pi|sh|lm|br|dm|sn|me|la)_[a-z][a-z0-9]+)(?![a-z0-9])')

def corpus(kind,game):
    names=set(snapshot.table_names(TABLES[kind]))
    for top in ['all_names','submissions','findings']:
        for path in (ROOT/top).rglob(kind+'*.txt'):
            for row in path.read_text(encoding='utf-8').splitlines():
                raw,sep,name=row.partition(',')
                if not sep or not name:continue
                try:key=int(raw,16)&snapshot.ID_MASK
                except ValueError:continue
                if snapshot.fnv1a(name,game,kind)&snapshot.ID_MASK==key:names.add(name.lower())
    return {n for n in names if n.isascii() and '\n' not in n and '\r' not in n}

def build(source,target,held,game,kind):
    weapons={m[1] for n in source for m in WEAPON.finditer(n)}
    if not weapons:raise SystemExit('No source-verified weapon identifiers')
    occ=re.compile(r'(?<![a-z0-9])('+ '|'.join(re.escape(w) for w in sorted(weapons,key=lambda x:(-len(x),x)))+r')(?![a-z0-9])')
    begins=Counter();ends=Counter();used=set();known=represented=0
    for n in target:
        if snapshot.fnv1a(n,game,kind)&snapshot.ID_MASK not in held:continue
        known+=1;matches=False
        for m in occ.finditer(n):
            b,e=n[:m.start()],n[m.end():]
            if b and not b.endswith(('_','/')):continue
            if e and not e.startswith('_'):continue
            begins[b]+=1;ends[e]+=1;used.add(m[1]);matches=True
        represented+=matches
    if not begins or not ends:raise SystemExit('No target-held whole-weapon naming slots')
    return begins,weapons,ends,{'known_target':known,'represented':represented,'source_weapons':len(weapons),'target_weapons':len(used),'beginnings':len(begins),'endings':len(ends),'candidate_product':len(begins)*len(weapons)*len(ends)}

def main():
    p=argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument('--game',required=True,choices=sorted(snapshot.MODERN))
    p.add_argument('--kind',required=True,choices=['image','material'])
    a=p.parse_args()
    shot=snapshot.read(ROOT/'snapshots'/(a.game.lower()+'.ids'));assert shot.game==a.game
    names={k:corpus(k,a.game) for k in TABLES}
    begins,weapons,ends,report=build(set().union(*names.values()),names[a.kind],set(shot.by_pool()[a.kind]),a.game,a.kind)
    out=ROOT/'contrib/verified_typed_weapon_slots'/a.game.lower()/a.kind
    out.mkdir(parents=True,exist_ok=True);paths={}
    for role,values in [('begin',begins),('stem',weapons),('end',ends)]:
        path=out/(role+'.txt');path.write_text(''.join('0,'+v+'\n' for v in sorted(values) if v),encoding='utf-8');paths[role]=path.relative_to(ROOT).as_posix()
    plan=out/'weapons.plan.txt'
    plan.write_text(f'label: {a.game} target-held {a.kind} whole-weapon identifier slots\n'
        f'describe: source-hash-verified class-and-weapon pairs offered inside target-held {a.kind} beginning and ending conventions; original namespace and decoration spelling retained; represents {report["represented"]}/{report["known_target"]} known target names\n'
        f'game: {a.game}\nbegin: @{paths["begin"]}\nstem: @{paths["stem"]}\nend: @{paths["end"]}\nbare: '+('yes' if '' in begins else 'no')+'\nfold: yes\n',encoding='utf-8')
    report.update(game=a.game,kind=a.kind,plan=plan.relative_to(ROOT).as_posix())
    (out/'measurement.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report))

if __name__=='__main__':main()
