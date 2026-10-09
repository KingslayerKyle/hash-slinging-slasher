"""Reach unnamed modern sound files from target-held aliases and sibling paths.

The older alias_to_files excludes a family if any game has a known file for it.
Here only target-held file families count as represented, so a foreign game's
directory does not hide a target file. Borrow directories from the deepest
underscore-prefix shared with target-held file families (at least three tokens).
Number/encoding endings must co-occur in that exact target directory. Source
rows use verified original spellings; normal sound_asset confirmation is required.
"""
import argparse
from collections import defaultdict
import json
from pathlib import Path
import re
import sys

ROOT=Path(__file__).resolve().parent
while ROOT!=ROOT.parent and not (ROOT/'scripts/snapshot.py').is_file():ROOT=ROOT.parent
if not (ROOT/'scripts/snapshot.py').is_file():ROOT=Path.cwd()
sys.path.insert(0,str(ROOT/'scripts'))
import snapshot

FORMAT=re.compile(r'(?P<stem>.+)(?P<tail>\.[a-z]{1,4}\d*\.\d+\.\d+\.[a-z_]+)$')
TAKE=re.compile(r'(?P<family>.+)(?P<take>_\d{1,3})$')

def corpus(kind,game):
    tables=['fnv1a_xsounds_v2'] if kind=='sound_asset' else ['fnv1a_soundbanks_aliases_v2','fnv1a_soundbanks_aliases']
    names=set(snapshot.table_names(*tables))
    for top in ['all_names','submissions','findings']:
        for path in (ROOT/top).rglob(kind+'*.txt'):
            for row in path.read_text(encoding='utf-8').splitlines():
                raw,sep,name=row.partition(',')
                if not sep or not name:continue
                try:key=int(raw,16)&snapshot.ID_MASK
                except ValueError:continue
                if snapshot.fnv1a(name,game,kind)&snapshot.ID_MASK==key:names.add(name.strip().lower())
    return {n for n in names if n.isascii() and '\n' not in n and '\r' not in n}

def build(sounds,aliases,file_ids,alias_ids,game):
    families=defaultdict(set);endings=defaultdict(set)
    for n in sounds:
        f=FORMAT.fullmatch(n)
        if not f or snapshot.fnv1a(n,game,'sound_asset')&snapshot.ID_MASK not in file_ids:continue
        at=max(f['stem'].rfind('/'),f['stem'].rfind(chr(92)),f['stem'].rfind('.'))+1
        directory,base=f['stem'][:at],f['stem'][at:]
        take=TAKE.fullmatch(base)
        family=take['family'] if take else base
        families[family].add(directory)
        endings[directory].add((take['take'] if take else '')+f['tail'])
    target_aliases={n for n in aliases if not any(c in n for c in '/.\\') and snapshot.fnv1a(n,game,'sound_alias')&snapshot.ID_MASK in alias_ids}
    prefixes=defaultdict(set)
    for family,dirs in families.items():
        parts=family.split('_')
        for k in range(3,len(parts)+1):prefixes['_'.join(parts[:k])].update(dirs)
    groups=[];missing=target_aliases-set(families);cost=matched=0
    for alias in sorted(missing):
        parts=alias.split('_')
        for k in range(len(parts),2,-1):
            dirs=prefixes.get('_'.join(parts[:k]))
            if dirs:
                groups.append((alias,dirs));matched+=1
                cost+=sum(len(endings[d]) for d in dirs)
                break
    return groups,endings,{'game':game,'target_held_aliases':len(target_aliases),'target_file_families':len(families),'missing_target_alias_file_families':len(missing),'families_with_target_sibling_paths':matched,'target_directories':len(endings),'candidate_product':cost}

def candidates(groups,endings,known):
    for alias,dirs in groups:
        for directory in sorted(dirs):
            for ending in sorted(endings[directory]):
                name=directory+alias+ending
                if name not in known:yield name

def main():
    p=argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument('--game',required=True,choices=sorted(snapshot.MODERN))
    p.add_argument('--kind',choices=['sound_asset'],default='sound_asset')
    p.add_argument('--measure',action='store_true')
    a=p.parse_args()
    shot=snapshot.read(ROOT/'snapshots'/(a.game.lower()+'.ids'));assert shot.game==a.game
    pools=shot.by_pool();sounds=corpus('sound_asset',a.game);aliases=corpus('sound_alias',a.game)
    groups,endings,report=build(sounds,aliases,set(pools['sound_asset']),set(pools['sound_alias']),a.game)
    print(json.dumps(report),file=sys.stderr)
    if a.measure:return
    sent=0
    for n in candidates(groups,endings,sounds):print(n);sent+=1
    print(json.dumps({'unseen_candidates_emitted':sent}),file=sys.stderr)

if __name__=='__main__':main()
