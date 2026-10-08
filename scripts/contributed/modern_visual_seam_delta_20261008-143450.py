"""Derive measured visual siblings from a batch of newly confirmed names only.

Pipe into confirm_list with the explicit modern game and destination pool.
Supply measured ending/directory lists from the visual seam plan builders.
Seed CSV rows are source-hash verified; only a new batch refills this method.
Reads configured helpers and supplied text files only, with no game/process,
credential or network access.
"""
import argparse
from pathlib import Path
import re
import sys


def values(path):
    return {row.strip().split(',',1)[-1] for row in path.read_text(encoding='utf-8').splitlines() if row.strip()}


def main():
    parser=argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--game',required=True)
    parser.add_argument('--rule',choices=['material-image','image-material'],required=True)
    parser.add_argument('--seed-files',type=Path,nargs='+',required=True)
    parser.add_argument('--endings',type=Path,required=True)
    parser.add_argument('--beginnings',type=Path)
    args=parser.parse_args()
    roots=[Path.cwd(),*Path(__file__).resolve().parents]
    root=next((p for p in roots if (p/'scripts/snapshot.py').is_file()),None)
    if root is None:parser.error('Run inside a solver checkout')
    sys.path.insert(0,str(root/'scripts'))
    import snapshot
    if args.game.upper() not in snapshot.MODERN:parser.error('Select a modern game')
    forward=args.rule=='material-image'
    kind='material' if forward else 'image'
    table='fnv1a_xmaterials_v2' if forward else 'fnv1a_ximages_v2'
    names=set()
    for path in args.seed_files:
        if path.stem.split('_',1)[0]!=kind:parser.error(f'Expected {kind} seed files')
        with path.open(encoding='utf-8') as rows:names.update(snapshot.database_names(table,rows))
    endings=values(args.endings)|{''}
    if forward:beginnings={'','i_','mtl_','i/','m/'}
    else:
        if args.beginnings is None:parser.error('image-material needs a measured beginnings file')
        beginnings=values(args.beginnings)|{''}
    channels={'c','n','g','o','m','s','r','e','col','nml','cm','dm','nm','sm','hm','mask','masks',
              'spc','gls','ao','d','h','a','swatch','preview','thermalmap','albedo','normal','gloss','metal'}
    cores=set()
    for name in names:
        base=name.strip().lower().replace('\\','/').rsplit('/',1)[-1]
        for prefix in ('mtl_','i_'):
            if base.startswith(prefix):base=base[len(prefix):];break
        if len(base)<5:continue
        cores.add(base)
        if forward:
            shortened=re.sub(r'_(?:v\d+|cm|dm|nm|sm|hm|col|nml|mask|swatch)$','',base)
            if len(shortened)>=5:cores.add(shortened)
        else:
            head,sep,tail=base.rpartition('_')
            if len(head)>=5 and (tail in channels or re.fullmatch(r'v\d+',tail)):cores.add(head)
    candidates={prefix+core+suffix for prefix in beginnings for core in cores for suffix in endings}
    for candidate in sorted(candidates):print('0,'+candidate)
    print(f'{len(names)} verified new {kind} seeds; {len(cores)} cores; {len(candidates)} distinct sibling candidates',file=sys.stderr)


if __name__=='__main__':main()
