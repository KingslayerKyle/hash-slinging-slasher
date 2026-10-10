"""Transfer source-hash-verified shared assets between the modern games.

Reads merged, typed all_names files only. Offers names held by the selected
game's same typed pool, excluding its existing names, published database keys,
and cached shared-family claims. Merged source names are usually already
claimed across every modern game, so a zero result is expected. No directory
re-spelling, models, processes or network access. Output
still requires normal confirmation and submission for the selected asset type.
"""
import argparse
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parent
while ROOT!=ROOT.parent and not (ROOT/'scripts/snapshot.py').is_file(): ROOT=ROOT.parent
if not (ROOT/'scripts/snapshot.py').is_file(): ROOT=Path.cwd()
sys.path.insert(0,str(ROOT/'scripts'))
import snapshot

KINDS=['image','material','xanim','sound_asset','sound_alias']

def main():
    p=argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument('--game',required=True,choices=sorted(snapshot.MODERN))
    p.add_argument('--kind',required=True,choices=KINDS)
    a=p.parse_args()
    shot=snapshot.read(ROOT/'snapshots'/(a.game.lower()+'.ids'))
    assert shot.game==a.game
    held=set(shot.by_pool()[a.kind])
    known=snapshot.known_hashes(game=a.game)
    cache=ROOT/'state/claimed.txt'
    if cache.is_file():
        for row in cache.read_text(encoding='utf-8').splitlines():
            try: key=int(row.strip(),16)
            except ValueError: continue
            known.update([key,key&snapshot.ID_MASK])
    ownpath=ROOT/'all_names'/a.game.lower()/(a.kind+'.txt')
    own={int(row.partition(',')[0],16)&snapshot.ID_MASK for row in ownpath.read_text(encoding='utf-8').splitlines()}
    wanted=held-known-own
    seen=set();found=set();verified=0
    for game in sorted(snapshot.MODERN):
        if game==a.game: continue
        path=ROOT/'all_names'/game.lower()/(a.kind+'.txt')
        if not path.is_file(): continue
        for row in path.read_text(encoding='utf-8').splitlines():
            raw,sep,name=row.partition(',')
            if not sep or not name or not name.isascii(): continue
            try: key=int(raw,16)
            except ValueError: continue
            full=snapshot.fnv1a(name,game,a.kind)
            expected=full if a.kind=='sound_alias' else full&snapshot.ID_MASK
            if key!=expected or name in seen: continue
            seen.add(name);verified+=1
            if full&snapshot.ID_MASK in wanted: found.add(name)
    for name in sorted(found): print(name)
    print(f'{verified} distinct source-verified {a.kind} names; {len(found)} shared unclaimed names on {a.game}',file=sys.stderr)

if __name__=='__main__': main()
