"""Build a visual-only suffix plan from verified modern/legacy tables and findings.

Example: python modern_visual_tail_plan.py --game MODWAR7 --length 4 --write-plan plans/visual_tail4.txt
Then run confirm_plan with the same explicit game and visual pool selection.
Reads shared source-hash-verified spellings, never Saluki export path guesses.
No game files, processes or network services are accessed.
"""
import argparse
import collections
import itertools
from pathlib import Path
import sys


def solver_root():
    for root in [Path.cwd(),*Path(__file__).resolve().parents]:
        if (root/'scripts/snapshot.py').is_file():
            return root
    raise SystemExit('Run inside a solver checkout')


def main():
    parser=argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--game',required=True)
    parser.add_argument('--length',type=int,choices=(3,4),default=4)
    parser.add_argument('--alphabet',type=int,default=37)
    parser.add_argument('--write-plan',type=Path,required=True)
    args=parser.parse_args()
    if not 1<=args.alphabet<=40:
        parser.error('alphabet must be between 1 and 40')
    root=solver_root()
    sys.path.insert(0,str(root/'scripts'))
    import snapshot
    game=args.game.upper()
    if game not in snapshot.MODERN:
        parser.error('Select a modern game')
    names=set()
    for kind,table in [('image','fnv1a_ximages'),('material','fnv1a_xmaterials'),('xanim','fnv1a_xanims')]:
        for suffix in ('_v2',''):
            names.update(snapshot.table_names(table+suffix))
        names.update(snapshot.confirmed_names(kind))
    names={name.strip().lower().replace('\\','/') for name in names
           if name.strip() and name.isascii() and '\n' not in name}
    counted=collections.Counter(char for name in names for char in name[-4:])
    alphabet=sorted(char for char,count in counted.most_common(args.alphabet) if not char.isspace())
    stems=sorted({name[:-args.length] for name in names if len(name)>args.length+3})
    plan=args.write_plan.resolve()
    plan.parent.mkdir(parents=True,exist_ok=True)
    stem_file=plan.with_suffix('.stems.txt')
    end_file=plan.with_suffix('.endings.txt')
    # The reader accepts hash,name rows. This protects literal leading '#' names
    # from its comment handling, and preserves commas inside an asset name.
    stem_file.write_text('\n'.join('0,'+stem for stem in stems)+'\n',encoding='utf-8')
    with end_file.open('w',encoding='utf-8') as stream:
        for chars in itertools.product(alphabet,repeat=args.length):
            stream.write(''.join(chars)+'\n')
    plan.write_text(
        f'label: modern visual verified full-corpus tails of length {args.length}\n'
        f'describe: verified image/material/xanim source names and confirmed findings, cut by {args.length} characters; all {args.length}-character endings from the {len(alphabet)} most frequent observed final characters, without the general vocabulary caps\n'
        f'game: {game}\nstem: @{stem_file.as_posix()}\nend: @{end_file.as_posix()}\nbare: yes\nfold: yes\n',encoding='utf-8')
    print(f'{len(names)} verified names; {len(stems)} distinct stems; alphabet {alphabet}; '
          f'{len(alphabet)**args.length} endings; {len(stems)*(len(alphabet)**args.length)} equivalent candidates')


if __name__=='__main__':
    main()
