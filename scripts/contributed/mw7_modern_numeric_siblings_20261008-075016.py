"""Emit bounded numeric and texture/mode siblings from verified database names.

Run from a solver checkout and pipe into confirm_list. This emits candidates only;
the compiled confirmer checks the selected capture, game hash policy and exclusions.
It preserves original sound spellings through snapshot.database_names, never uses
export paths as names, and performs no network, process or game-file operations.

Example: python contrib/mw7_modern_numeric_siblings.py --rows 20000 > plans/mw7-siblings.list
"""
from pathlib import Path
import argparse
import re
import sys


def solver_root():
    for root in [Path.cwd(), *Path(__file__).resolve().parents]:
        if (root/'scripts/snapshot.py').is_file():
            return root
    raise SystemExit('Run inside a hash-slinging-slasher checkout')


sys.path.insert(0,str(solver_root()/'scripts'))
import settings
import snapshot

STEMS={'image':'fnv1a_ximages','material':'fnv1a_xmaterials',
       'xanim':'fnv1a_xanims','sound_alias':'fnv1a_soundbanks_aliases'}
TRANSFORMS=[('_col','_nml'),('_nml','_col'),('_col','_mask'),
            ('_mp','_sp'),('_sp','_mp'),('_lod0','_lod1')]


def variants(seed, maximum):
    yield seed
    for match in re.finditer(r'\d+',seed):
        digits=match.group()
        if len(digits)>3:
            continue
        for index in range(maximum+1):
            value=str(index).zfill(len(digits))
            if value!=digits:
                yield seed[:match.start()]+value+seed[match.end():]
    for before,after in TRANSFORMS:
        if before in seed:
            yield seed.replace(before,after)


def main():
    parser=argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--rows',type=int,default=20000,help='verified seeds per source table')
    parser.add_argument('--index-max',type=int,default=16)
    parser.add_argument('--families',default='image,sound_alias')
    parser.add_argument('--game',choices=sorted(snapshot.MODERN))
    args=parser.parse_args()
    if args.rows<1 or not 0<=args.index_max<=999:
        parser.error('rows must be positive and index-max must be between 0 and 999')
    game=settings.game()
    if game not in snapshot.MODERN:
        parser.error('select a modern game in the solver first')
    kinds=args.families.split(',')
    if any(kind not in STEMS for kind in kinds):
        parser.error('families are image, material, xanim and sound_alias')
    seeds=candidates=0
    for kind in kinds:
        for suffix in ['_v2','']:
            table=STEMS[kind]+suffix
            path=Path(settings.tables_csv())/(table+'.csv')
            if not path.exists():
                continue
            with path.open(encoding='utf-8') as rows:
                verified=snapshot.database_names(table,rows)
                for number,name in enumerate(verified):
                    if number>=args.rows:
                        break
                    seed=name.translate(str.maketrans('ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'))
                    seeds+=1
                    for candidate in variants(seed,args.index_max):
                        print(candidate)
                        candidates+=1
    print(f'{game}: {seeds} verified seeds; {candidates} candidates',file=sys.stderr)


if __name__=='__main__':
    main()
