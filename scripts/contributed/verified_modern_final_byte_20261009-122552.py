"""Solve a modern asset's final byte from verified names of the same type.

Unlike the original legacy-table final_byte method, seeds include modern tables
and every hash operation explicitly selects the game and asset type. Aliases
use their own offset. Both full-hash top-bit variants are tried. A bucket on the
upper 56 bits replaces 256 lookups per target; each solution is hashed back.
Names already resolved or claimed remain excluded. Print candidates for the
normal typed confirmation/submission pipeline; no models are searched.
"""
import argparse
from collections import defaultdict
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parent
while ROOT!=ROOT.parent and not (ROOT/'scripts/snapshot.py').is_file():ROOT=ROOT.parent
if not (ROOT/'scripts/snapshot.py').is_file():ROOT=Path.cwd()
sys.path.insert(0,str(ROOT/'scripts'))
import snapshot

TABLES={'image':'fnv1a_ximages_v2','material':'fnv1a_xmaterials_v2','xanim':'fnv1a_xanims_v2','sound_alias':'fnv1a_soundbanks_aliases_v2'}
MASK=(1<<64)-1
TOP=1<<63
INVERSE=pow(snapshot.PRIME,-1,1<<64)

def corpus(kind,game):
    names=set(snapshot.table_names(TABLES[kind]))
    if kind=='sound_alias':names.update(snapshot.table_names('fnv1a_soundbanks_aliases'))
    for top in ['all_names','submissions','findings']:
        for path in (ROOT/top).rglob(kind+'*.txt'):
            for row in path.read_text(encoding='utf-8').splitlines():
                raw,sep,name=row.partition(',')
                if not sep or not name:continue
                try:key=int(raw,16)&snapshot.ID_MASK
                except ValueError:continue
                if snapshot.fnv1a(name,game,kind)&snapshot.ID_MASK==key:names.add(name.strip().lower())
    return {n for n in names if n.isascii() and n==n.strip() and '\n' not in n and '\r' not in n}

def wanted(held,names,known,game,kind):
    excluded={key&snapshot.ID_MASK for key in known}
    excluded.update(snapshot.fnv1a(n,game,kind)&snapshot.ID_MASK for n in names)
    return {key&snapshot.ID_MASK for key in held}-excluded

def solve(names,ids,game,kind):
    buckets=defaultdict(list)
    for prefix in {n[:-1] for n in names if len(n)>1}:
        h=snapshot.fnv1a(prefix,game,kind);buckets[h>>8].append((h,prefix))
    found={}
    for key in ids:
        for value in [key&snapshot.ID_MASK,(key&snapshot.ID_MASK)|TOP]:
            scaled=(value*INVERSE)&MASK
            for h,prefix in buckets.get(scaled>>8,()):
                byte=scaled^h
                if not 33<=byte<=126:continue
                name=prefix+chr(byte)
                if name not in names and snapshot.fnv1a(name,game,kind)==value:found[name]=value
    return found

def main():
    p=argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument('--game',required=True,choices=sorted(snapshot.MODERN))
    p.add_argument('--kind',required=True,choices=sorted(TABLES))
    a=p.parse_args()
    shot=snapshot.read(ROOT/'snapshots'/(a.game.lower()+'.ids'));assert shot.game==a.game
    names=corpus(a.kind,a.game);known=snapshot.known_hashes(game=a.game)
    claimed=ROOT/'state/claimed.txt'
    if claimed.exists():
        for row in claimed.read_text().splitlines():
            try:known.add(int(row,16)&snapshot.ID_MASK)
            except ValueError:continue
    ids=wanted(set(shot.by_pool()[a.kind]),names,known,a.game,a.kind)
    found=solve(names,ids,a.game,a.kind)
    print(json.dumps({'game':a.game,'kind':a.kind,'verified_seed_names':len(names),'unresolved_unclaimed_typed_ids':len(ids),'solved':len(found)}),file=sys.stderr)
    for name in sorted(found):print(name)

if __name__=='__main__':main()
