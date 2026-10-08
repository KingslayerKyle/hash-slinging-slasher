"""Walk the measured visual seam backwards using all verified image cores.

Run the generated plan with confirm_plan, the same modern game, and material
selected. Material directories and endings are measured from names actually
held in that capture. Tables use shared source-hash-verified spellings.
No game installations, processes, credentials or network services are accessed.
"""
import argparse
import collections
from pathlib import Path
import re
import sys


def main():
    parser=argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--game',required=True)
    parser.add_argument('--write-plan',type=Path,required=True)
    args=parser.parse_args()
    roots=[Path.cwd(),*Path(__file__).resolve().parents]
    root=next((p for p in roots if (p/'scripts/snapshot.py').is_file()),None)
    if root is None:parser.error('Run inside a solver checkout')
    sys.path.insert(0,str(root/'scripts'))
    import snapshot
    import settings
    game=args.game.upper()
    if game not in snapshot.MODERN:parser.error('Select a modern game')
    capture=snapshot.read(str(Path(settings.path('snapshots','snapshots'))/(game+'.ids')))
    material_ids=set(capture.by_pool().get('material',[]))
    materials=set(snapshot.table_names('fnv1a_xmaterials_v2'))
    materials.update(snapshot.confirmed_names('material'))
    held={name for name in materials if snapshot.fnv1a(name,game,'material')&snapshot.ID_MASK in material_ids}
    prefixes={name.rsplit('/',1)[0]+'/' for name in held if '/' in name}
    if any(name.startswith('mtl_') for name in held):prefixes.add('mtl_')
    suffixes=collections.Counter('_'+name.rsplit('_',1)[-1] for name in held
        if '_' in name and re.fullmatch('[a-z0-9]{1,10}',name.rsplit('_',1)[-1]))
    endings=sorted(token for token,count in suffixes.most_common(32))
    if not endings:raise SystemExit('No verified material conventions in this capture')
    images=set(snapshot.table_names('fnv1a_ximages_v2','fnv1a_ximages'))
    images.update(snapshot.confirmed_names('image'))
    channels={'c','n','g','o','m','s','r','e','col','nml','cm','dm','nm','sm','hm','mask','masks',
              'spc','gls','ao','d','h','a','swatch','preview','thermalmap','albedo','normal','gloss','metal'}
    cores=set()
    for name in images:
        name=name.strip().lower().replace('\\','/')
        if not name.isascii() or '\n' in name:continue
        base=name.rsplit('/',1)[-1]
        for prefix in ('i_','mtl_'):
            if base.startswith(prefix):base=base[len(prefix):];break
        if len(base)<5:continue
        cores.add(base)
        head,sep,tail=base.rpartition('_')
        if len(head)>=5 and (tail in channels or re.fullmatch(r'v\d+',tail)):cores.add(head)
    plan=args.write_plan.resolve();plan.parent.mkdir(parents=True,exist_ok=True)
    stems=plan.with_suffix('.stems.txt');ends=plan.with_suffix('.endings.txt');begins=plan.with_suffix('.beginnings.txt')
    for path,items in [(stems,cores),(ends,endings),(begins,prefixes)]:
        path.write_text('\n'.join('0,'+value for value in sorted(items))+'\n',encoding='utf-8')
    plan.write_text(f'label: modern image-to-material uncapped measured directory siblings\n'
        f'describe: all verified image cores and confirmed image findings, with and without channel/version labels, under every material directory actually held by this capture and its 32 most frequent material endings\n'
        f'game: {game}\nstem: @{stems.as_posix()}\nend: @{ends.as_posix()}\n'
        f'begin: @{begins.as_posix()}\nbare: yes\nfold: yes\n',encoding='utf-8')
    print(f'{len(held)} held verified materials supplied {len(prefixes)} directories and {len(endings)} endings; '
          f'{len(images)} image names supplied {len(cores)} cores; '
          f'{len(cores)*(len(prefixes)+1)*(len(endings)+1)} equivalent candidates')


if __name__=='__main__':main()
