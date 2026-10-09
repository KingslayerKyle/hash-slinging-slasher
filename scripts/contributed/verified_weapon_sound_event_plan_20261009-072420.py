"""Build a weapon-class sound-file plan using verified animation events.

The selected class's sound-file heads and suffixes must occur on the target
capture. Events are taken from source-hash-verified same-class animations and
aliases. Original directory separators, basename prefixes and encoding tails
are preserved. Run the generated plan with sound_asset confirmation only.
"""
import argparse
from collections import Counter
import json
from pathlib import Path
import re
import sys

ROOT=Path(__file__).resolve().parent
while ROOT!=ROOT.parent and not (ROOT/'scripts/snapshot.py').is_file(): ROOT=ROOT.parent
if not (ROOT/'scripts/snapshot.py').is_file(): ROOT=Path.cwd()
sys.path.insert(0,str(ROOT/'scripts'))
import snapshot

CLASSES='ar|sm|pi|sh|lm|br|dm|sn|me|la|smg|pistol|lmg|dmr|shotgun|sniper|rifle|launcher|melee|special'
ANIM=re.compile(r'^(?:[a-z0-9]+_)?(?:(?:vm|wm)_)?(?:[a-z]{0,2}p\d*_)?(?P<class>'+CLASSES+r')_(?P<weapon>[a-z0-9]+)_(?P<event>.+)$')
ALIAS=re.compile(r'^(?:fly|wfoly|wpn|weap)_(?:(?:rex|sat|jup)_)?(?:(?:plr|npc)_)?(?P<class>'+CLASSES+r')_(?P<weapon>[a-z0-9]+)_(?P<event>.+?)(?:_\d{1,3}){0,2}$')
WEAPON=re.compile(r'(?:^|_)(?P<class>'+CLASSES+r')_(?P<weapon>[a-z0-9]+)_(?P<event>.+)$')
FORMAT=re.compile(r'(?P<stem>.+)(?P<tail>\.[a-z]{1,4}\d*\.\d+\.\d+\.[a-z_]+)$')

def corpus(kind,table,game):
    names=set(snapshot.table_names(table))
    for top in ['all_names','submissions','findings']:
        for path in (ROOT/top).rglob(kind+'*.txt'):
            for row in path.read_text(encoding='utf-8').splitlines():
                raw,sep,name=row.partition(',')
                if not sep or not name: continue
                try:key=int(raw,16)&snapshot.ID_MASK
                except ValueError:continue
                if snapshot.fnv1a(name,game,kind)&snapshot.ID_MASK==key:names.add(name.lower())
    return {n for n in names if n.isascii() and '\n' not in n and '\r' not in n}

def build(sounds,animations,aliases,held,game,cls):
    events=set()
    for regex,names in [(ANIM,animations),(ALIAS,aliases)]:
        for n in names:
            m=regex.fullmatch(n)
            if m and m['class']==cls:events.add(m['event'])
    heads=Counter();ends=Counter();known=represented=0
    for n in sounds:
        f=FORMAT.fullmatch(n)
        if f is None or snapshot.fnv1a(n,game,'sound_asset')&snapshot.ID_MASK not in held:continue
        at=max(f['stem'].rfind('/'),f['stem'].rfind(chr(92)),f['stem'].rfind('.'))+1
        w=WEAPON.search(f['stem'][at:])
        if w is None or w['class']!=cls:continue
        known+=1
        head=f['stem'][:at]+f['stem'][at:at+w.start('event')]
        heads[head]+=1
        parts=w['event'].split('_');ends[f['tail']]+=1
        reconstructs=w['event'] in events
        for k in range(1,min(3,len(parts)-1)+1):
            ends['_'+ '_'.join(parts[-k:])+f['tail']]+=1
            reconstructs |= '_'.join(parts[:-k]) in events
        represented+=reconstructs
    if not heads or not ends or not events:raise SystemExit('No target-held sound-file and event vocabulary for this class')
    return heads,events,ends,{'known_target_files':known,'reconstructible_target_files':represented,'heads':len(heads),'events':len(events),'endings':len(ends),'candidate_product':len(heads)*len(events)*len(ends)}

def main():
    p=argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument('--game',required=True,choices=sorted(snapshot.MODERN))
    p.add_argument('--class',dest='cls',required=True,choices=CLASSES.split('|'))
    a=p.parse_args()
    shot=snapshot.read(ROOT/'snapshots'/(a.game.lower()+'.ids'));assert shot.game==a.game
    sounds=corpus('sound_asset','fnv1a_xsounds_v2',a.game)
    anims=corpus('xanim','fnv1a_xanims_v2',a.game)
    aliases=corpus('sound_alias','fnv1a_soundbanks_aliases_v2',a.game)
    heads,events,ends,report=build(sounds,anims,aliases,set(shot.by_pool()['sound_asset']),a.game,a.cls)
    out=ROOT/'contrib/verified_weapon_sound_events'/a.game.lower()/a.cls
    out.mkdir(parents=True,exist_ok=True)
    paths={}
    for role,values in [('begin',heads),('stem',events),('end',ends)]:
        path=out/(role+'.txt');path.write_text(''.join('0,'+v+'\n' for v in sorted(values)),encoding='utf-8');paths[role]=path.relative_to(ROOT).as_posix()
    plan=out/'sound-files.plan.txt'
    plan.write_text(f'label: {a.game} {a.cls} weapon sound files from verified animation events\n'
        f'describe: target-held {a.cls} weapon sound-file directory/basename heads, source-hash-verified same-class animation and alias events, and target-observed subevent plus encoding tails; original spelling retained; reconstructs {report["reconstructible_target_files"]}/{report["known_target_files"]} known target files\n'
        f'game: {a.game}\nbegin: @{paths["begin"]}\nstem: @{paths["stem"]}\nend: @{paths["end"]}\nbare: no\nfold: yes\n',encoding='utf-8')
    report.update(game=a.game,weapon_class=a.cls,plan=plan.relative_to(ROOT).as_posix())
    (out/'measurement.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report))

if __name__=='__main__':main()
