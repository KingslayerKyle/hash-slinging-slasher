"""Solve a modern sound basename's final byte before its original encoding tail.

The whole filename ends in a codec/rate/language tail, so existing final-byte
methods edit that tail rather than the basename. Peel target-observed encoding
tails from the captured hash, then solve one basename byte using verified sound
prefixes. Preserve original directories and spelling, try both top-bit variants,
and rehash every complete candidate. Normal sound_asset confirmation is required.
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

MASK=(1<<64)-1;TOP=1<<63;INV=pow(snapshot.PRIME,-1,1<<64)
FORMAT=re.compile(r'(?P<stem>.+)(?P<tail>\.[a-z]{1,4}\d*\.\d+\.\d+\.[a-z_]+)$')

def corpus(game):
    names=set(snapshot.table_names('fnv1a_xsounds_v2'))
    for top in ['all_names','submissions','findings']:
        for path in (ROOT/top).rglob('sound_asset*.txt'):
            for row in path.read_text(encoding='utf-8').splitlines():
                raw,sep,name=row.partition(',')
                if not sep or not name:continue
                try:key=int(raw,16)&snapshot.ID_MASK
                except ValueError:continue
                if snapshot.fnv1a(name,game,'sound_asset')&snapshot.ID_MASK==key:names.add(name.strip().lower())
    return {n for n in names if n.isascii() and n==n.strip() and '\n' not in n and '\r' not in n}

def target_tails(names,held,game):
    return {m['tail'] for n in names if (m:=FORMAT.fullmatch(n)) and snapshot.fnv1a(n,game,'sound_asset')&snapshot.ID_MASK in held}

def solve(names,ids,tails,game):
    prefixes={m['stem'][:-1] for n in names if (m:=FORMAT.fullmatch(n)) and len(m['stem'])>1}
    buckets=defaultdict(list)
    for prefix in prefixes:
        h=snapshot.fnv1a(prefix,game,'sound_asset');buckets[h>>8].append((h,prefix))
    found={}
    for tail in sorted(tails):
        # Normalization must be the same as the full hash before running backwards.
        encoded=tail.lower().replace(chr(92),'/').encode('ascii')
        for key in ids:
            for full in [key&snapshot.ID_MASK,(key&snapshot.ID_MASK)|TOP]:
                value=full
                for byte in reversed(encoded):value=((value*INV)&MASK)^byte
                scaled=(value*INV)&MASK
                for h,prefix in buckets.get(scaled>>8,()):
                    byte=scaled^h
                    if not 33<=byte<=126:continue
                    name=prefix+chr(byte)+tail
                    if name not in names and snapshot.fnv1a(name,game,'sound_asset')==full:found[name]=full
    return found,len(prefixes)

def main():
    p=argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument('--game',required=True,choices=sorted(snapshot.MODERN))
    p.add_argument('--kind',choices=['sound_asset'],default='sound_asset')
    a=p.parse_args()
    shot=snapshot.read(ROOT/'snapshots'/(a.game.lower()+'.ids'));assert shot.game==a.game
    names=corpus(a.game);held=set(shot.by_pool()['sound_asset']);tails=target_tails(names,held,a.game)
    if not tails:raise SystemExit('No verified target sound encoding tails')
    known={key&snapshot.ID_MASK for key in snapshot.known_hashes(game=a.game)}
    known.update(snapshot.fnv1a(n,a.game,'sound_asset')&snapshot.ID_MASK for n in names)
    claimed=ROOT/'state/claimed.txt'
    if claimed.exists():
        for row in claimed.read_text().splitlines():
            try:known.add(int(row,16)&snapshot.ID_MASK)
            except ValueError:continue
    ids=held-known
    found,prefixes=solve(names,ids,tails,a.game)
    print(json.dumps({'game':a.game,'verified_sound_seeds':len(names),'original_basename_prefixes':prefixes,'target_observed_encoding_tails':len(tails),'unresolved_unclaimed_sound_ids':len(ids),'solved':len(found)}),file=sys.stderr)
    for n in sorted(found):print(n)

if __name__=='__main__':main()
