"""Rename linked namespace occurrences across a modern sound path together.

The existing codename_swap changes one token at a time. Sound paths often repeat
the same namespace in the directory and basename, so that misses a coherent
rename of both. Require at least two whole-token occurrences in a source-verified
sound, replace all occurrences of that source namespace, preserve the basename,
and use only target-held directory style and original encoding tails. Emit
candidates for normal sound_asset confirmation; models are never searched.
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

FORMAT=re.compile(r'(?P<stem>.+)(?P<tail>\.[a-z]{1,4}\d*\.\d+\.\d+\.[a-z_]+)$')
CODES=['iw7','iw8','iw9','jup','t7','t8','t9','t10','sat','s4','s6','rex']
PATTERNS={c:re.compile(r'(?<![a-z0-9])'+re.escape(c)+r'(?=[_/.]|$)') for c in CODES}

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
    return {n for n in names if n.isascii() and '\n' not in n and '\r' not in n}

def styled(stem,style):
    if style=='slash' and '/' not in stem:
        directory,sep,base=stem.rpartition('.')
        if sep:return directory.replace('.','/')+'/'+base
    if style=='dot' and '/' in stem:
        directory,_,base=stem.rpartition('/')
        return directory.replace('/','.')+'.'+base
    return stem

def build(names,held,game):
    target=set();tails=set();styles=Counter();codes=Counter()
    for n in names:
        m=FORMAT.fullmatch(n)
        if not m or snapshot.fnv1a(n,game,'sound_asset')&snapshot.ID_MASK not in held:continue
        target.add(m['stem']);tails.add(m['tail'])
        if '/' in m['stem']:styles['slash']+=1
        elif '.' in m['stem']:styles['dot']+=1
        for c,rx in PATTERNS.items():
            if len(rx.findall(m['stem']))>=2:codes[c]+=1
    if not codes or not styles or not tails:raise SystemExit('No verified repeated target sound namespaces')
    # The dominant repeated target namespace is measured; do not rotate every code.
    to=codes.most_common(1)[0][0];style=styles.most_common(1)[0][0]
    stems=set();eligible=Counter()
    for n in names:
        m=FORMAT.fullmatch(n)
        if not m:continue
        for old,rx in PATTERNS.items():
            if old==to or len(rx.findall(m['stem']))<2:continue
            eligible[old]+=1
            renamed=rx.sub(to,m['stem'])
            stems.add(renamed);stems.add(styled(renamed,style))
    return stems,tails,{'game':game,'target_namespace':to,'target_directory_style':style,'target_namespace_support':codes[to],'source_names_by_repeated_namespace':dict(eligible),'renamed_stems':len(stems),'known_target_stems_reconstructed':len(stems&target),'target_encoding_tails':len(tails),'candidate_product':len(stems)*len(tails)}

def main():
    p=argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument('--game',required=True,choices=sorted(snapshot.MODERN))
    p.add_argument('--kind',choices=['sound_asset'],default='sound_asset')
    a=p.parse_args()
    shot=snapshot.read(ROOT/'snapshots'/(a.game.lower()+'.ids'));assert shot.game==a.game
    names=corpus(a.game);stems,tails,report=build(names,set(shot.by_pool()['sound_asset']),a.game)
    print(json.dumps(report),file=sys.stderr)
    sent=0
    for stem in sorted(stems):
        for tail in sorted(tails):
            candidate=stem+tail
            if candidate not in names:print(candidate);sent+=1
    print(json.dumps({'unseen_candidates_emitted':sent}),file=sys.stderr)

if __name__=='__main__':main()
