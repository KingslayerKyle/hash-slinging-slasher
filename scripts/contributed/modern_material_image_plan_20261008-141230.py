"""Derive uncapped image siblings from verified material cores and measured channels.

Use an explicit modern game and an image-only pool selection with confirm_plan.
Reads source-hash-verified tables and confirmed findings. Writes a plan and its
lists; it accesses no game installation, process, credential or network service.
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
    image_ids=set(capture.by_pool().get('image',[]))
    image_names=set(snapshot.table_names('fnv1a_ximages_v2'))
    image_names.update(snapshot.confirmed_names('image'))
    measured=set()
    for name in image_names:
        if snapshot.fnv1a(name,game,'image')&snapshot.ID_MASK in image_ids:measured.add(name)
    channels=collections.Counter('_'+name.rsplit('_',1)[-1] for name in measured
        if '_' in name and re.fullmatch('[a-z0-9]{1,10}',name.rsplit('_',1)[-1]))
    endings=sorted(token for token,count in channels.most_common(48))
    if not endings:raise SystemExit('No verified image conventions in this capture')
    materials=set(snapshot.table_names('fnv1a_xmaterials_v2','fnv1a_xmaterials'))
    materials.update(snapshot.confirmed_names('material'))
    cores=set()
    for name in materials:
        name=name.strip().lower().replace('\\','/')
        if not name.isascii() or '\n' in name:continue
        base=name.rsplit('/',1)[-1]
        for prefix in ('mtl_','i_'):
            if base.startswith(prefix):base=base[len(prefix):];break
        if len(base)<5:continue
        cores.add(base)
        # Material versions and map-channel labels survive in image names, but
        # also hide the core that takes a different measured channel.
        shorter=re.sub(r'_(?:v\d+|cm|dm|nm|sm|hm|col|nml|mask|swatch)$','',base)
        if len(shorter)>=5:cores.add(shorter)
    plan=args.write_plan.resolve();plan.parent.mkdir(parents=True,exist_ok=True)
    stems=plan.with_suffix('.stems.txt');ends=plan.with_suffix('.endings.txt')
    stems.write_text('\n'.join('0,'+name for name in sorted(cores))+'\n',encoding='utf-8')
    ends.write_text('\n'.join(endings)+'\n',encoding='utf-8')
    plan.write_text(f'label: modern material-to-image uncapped measured channel siblings\n'
        f'describe: all verified material cores and confirmed material findings, with and without version/map-channel labels, respelled using the 48 most frequent image endings actually held in this capture; bare, i_, mtl_, i/ and m/ forms\n'
        f'game: {game}\nstem: @{stems.as_posix()}\nend: @{ends.as_posix()}\n'
        'begin: i_\nbegin: mtl_\nbegin: i/\nbegin: m/\nbare: yes\nfold: yes\n',encoding='utf-8')
    print(f'{len(measured)} held verified images supplied {len(endings)} endings; '
          f'{len(materials)} material names supplied {len(cores)} cores; '
          f'{len(cores)*5*(len(endings)+1)} equivalent candidates')


if __name__=='__main__':main()
