"""Restore the selected game's observed directory spelling on modern sounds.

Source names are independently hash-verified. Only directory separators change;
the basename remains literal, and encoding tails come from names held on the
target capture. This reaches sounds named in another engine's directory style.
Prints candidates; normal sound_asset confirmation and submission required.
"""
import argparse
from collections import Counter
from pathlib import Path
import re
import sys

ROOT=Path(__file__).resolve().parent
while ROOT!=ROOT.parent and not (ROOT/'scripts/snapshot.py').is_file(): ROOT=ROOT.parent
if not (ROOT/'scripts/snapshot.py').is_file(): ROOT=Path.cwd()
sys.path.insert(0,str(ROOT/'scripts'))
import snapshot

FORMAT=re.compile(r'(?P<stem>.+)(?P<tail>\.[a-z]{1,4}\d*\.\d+\.\d+\.[a-z_]+)$')

def corpus(game):
    names=set(snapshot.table_names('fnv1a_xsounds_v2'))
    for top in ['all_names','submissions','findings']:
        for path in (ROOT/top).rglob('sound_asset*.txt'):
            for row in path.read_text(encoding='utf-8').splitlines():
                raw,sep,name=row.partition(',')
                if not sep or not name: continue
                try: key=int(raw,16)&snapshot.ID_MASK
                except ValueError: continue
                if snapshot.fnv1a(name,game,'sound_asset')&snapshot.ID_MASK==key: names.add(name.lower())
    return {n for n in names if n.isascii() and '\n' not in n and '\r' not in n}

def measured(names,held,game):
    styles=Counter();tails=set()
    for name in names:
        m=FORMAT.fullmatch(name)
        if m is None or snapshot.fnv1a(name,game,'sound_asset')&snapshot.ID_MASK not in held: continue
        tails.add(m['tail'])
        if '/' in m['stem']: styles['slash']+=1
        elif '.' in m['stem']: styles['dot']+=1
    if not styles or not tails: raise SystemExit('No verified target sound directory convention')
    return styles.most_common(1)[0][0],tails

def converted_stem(stem,style):
    if style=='slash':
        if '/' in stem: return None
        directory,sep,base=stem.rpartition('.')
        return directory.replace('.','/')+'/'+base if sep and directory and base else None
    if '/' not in stem: return None
    directory,_,base=stem.rpartition('/')
    return directory.replace('/','.')+'.'+base if directory and base else None

def candidates(names,style,tails):
    stems={new for n in names if (m:=FORMAT.fullmatch(n)) and (new:=converted_stem(m['stem'],style))}
    sent=0
    for stem in sorted(stems):
        for tail in sorted(tails):
            name=stem+tail
            if name not in names:
                sent+=1;yield name
    print(f'{sent} unseen spellings from {len(stems)} converted stems and {len(tails)} target encoding tails; target style {style}',file=sys.stderr)

def main():
    p=argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument('--game',required=True,choices=sorted(snapshot.MODERN))
    p.add_argument('--kind',choices=['sound_asset'],default='sound_asset')
    a=p.parse_args()
    shot=snapshot.read(ROOT/'snapshots'/(a.game.lower()+'.ids'));assert shot.game==a.game
    names=corpus(a.game);style,tails=measured(names,set(shot.by_pool()['sound_asset']),a.game)
    for name in candidates(names,style,tails): print(name)

if __name__=='__main__': main()
