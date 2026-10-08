"""Scan verified visual numeric siblings in native threads, then print capture matches.

Pipe into confirm_list --game TAG. Its shared verifier remains authoritative.
Reads the configured CSV tables and snapshots only. Needs rustc on PATH. The
temporary native worker, seed list and target list are deleted after the run.
No game files, processes, credentials, or network services are accessed.
"""
import argparse
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

NATIVE = r'''
use std::{collections::{HashSet,BTreeSet},env,fs,thread,time::Instant};
const BASIS:u64=0x47F5817A5EF961BA;
const PRIME:u64=0x100000001B3;
const MASK:u64=0x7fffffffffffffff;
fn extend(mut h:u64,bytes:&[u8])->u64 {
    for &b in bytes { let b=if b==b'\\' {b'/'} else {b.to_ascii_lowercase()};
        h=(h ^ b as u64).wrapping_mul(PRIME); }
    h
}
fn keep(seed:&str,targets:&HashSet<u64>,out:&mut BTreeSet<String>){
    if targets.contains(&(extend(BASIS,seed.as_bytes())&MASK)){out.insert(seed.into());}
}
fn scan(seeds:&[String], targets:&HashSet<u64>, max:usize)->(u64,BTreeSet<String>){
    let numbers:Vec<Vec<String>>=(1..=3).map(|width|(0..=max).map(|v|format!("{v:0width$}")).collect()).collect();
    let mut count=0u64; let mut out=BTreeSet::new();
    for seed in seeds {
        keep(seed,targets,&mut out); count+=1;
        let bytes=seed.as_bytes(); let mut at=0;
        while at<bytes.len(){
            if !bytes[at].is_ascii_digit(){at+=1;continue;}
            let start=at; while at<bytes.len() && bytes[at].is_ascii_digit(){at+=1;}
            let width=at-start; if width>3 {continue;}
            let prefix=extend(BASIS,&bytes[..start]);
            for value in &numbers[width-1]{
                if value.as_bytes()==&bytes[start..at]{continue;}
                count+=1;
                let h=extend(extend(prefix,value.as_bytes()),&bytes[at..])&MASK;
                if targets.contains(&h){
                    let mut candidate=String::with_capacity(bytes.len()+3);
                    candidate.push_str(&seed[..start]); candidate.push_str(value);
                    candidate.push_str(&seed[at..]); out.insert(candidate);
                }
            }
        }
        for (before,after) in [("_col","_nml"),("_nml","_col"),("_col","_mask"),("_mp","_sp"),("_sp","_mp"),("_lod0","_lod1")]{
            if seed.contains(before){count+=1;keep(&seed.replace(before,after),targets,&mut out);}
        }
    }
    (count,out)
}
fn main(){
    let args:Vec<String>=env::args().collect(); assert_eq!(args.len(),5);
    let seeds:Vec<String>=fs::read_to_string(&args[1]).unwrap().lines().map(String::from).collect();
    let targets:HashSet<u64>=fs::read_to_string(&args[2]).unwrap().lines().map(|v|u64::from_str_radix(v,16).unwrap()&MASK).collect();
    let max:usize=args[3].parse().unwrap(); assert!(max<=999);
    let workers:usize=args[4].parse().unwrap(); assert!(workers>0 && workers<=256);
    let size=seeds.len().div_ceil(workers).max(1); let began=Instant::now();
    let mut total=0u64; let mut found=BTreeSet::new();
    thread::scope(|scope|{
        let handles:Vec<_>=seeds.chunks(size).map(|chunk|{
            let targets=&targets; scope.spawn(move ||scan(chunk,targets,max))
        }).collect();
        for handle in handles { let (count,names)=handle.join().unwrap();total+=count;found.extend(names); }
    });
    eprintln!("{} verified seeds; {} native candidates; {} distinct capture matches; {:.2}s",seeds.len(),total,found.len(),began.elapsed().as_secs_f64());
    for name in found{println!("{name}");}
}
'''


def solver_root():
    for root in [Path.cwd(), *Path(__file__).resolve().parents]:
        if (root/'scripts/snapshot.py').is_file():
            return root
    raise SystemExit('Run inside a solver checkout')


def main():
    parser=argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--game',required=True)
    parser.add_argument('--index-max',type=int,default=999)
    parser.add_argument('--threads',type=int,default=16)
    parser.add_argument('--scratch-dir',type=Path,help='Parent for a temporary native build and verified inputs')
    args=parser.parse_args()
    if not 0<=args.index_max<=999 or not 1<=args.threads<=256:
        parser.error('index-max must be 0-999 and threads 1-256')
    root=solver_root()
    sys.path.insert(0,str(root/'scripts'))
    import snapshot
    import settings
    game=args.game.upper()
    if game not in snapshot.MODERN:
        parser.error('This prefilter is for modern ordinary visual asset hashes only')
    rustc=shutil.which('rustc')
    if not rustc:
        parser.error('rustc is required')
    names=set()
    for stem in ('fnv1a_ximages','fnv1a_xmaterials','fnv1a_xanims'):
        for suffix in ('_v2',''):
            names.update(snapshot.table_names(stem+suffix))
    # Identical to the earlier numeric generator: verified source table names,
    # ASCII lowercased, with every 1-3 digit run independently replaced.
    lower=str.maketrans('ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz')
    names=sorted(name.translate(lower) for name in names if name and '\n' not in name)
    if any(not name.isascii() for name in names):
        raise SystemExit('Non-ASCII seed requires review before using the native digit scanner')
    known=snapshot.known_hashes(game=game)
    capture=snapshot.read(str(Path(settings.path('snapshots','snapshots'))/(game+'.ids')))
    targets={asset_id for asset_id,pool in capture.records
             if capture.pool_name(pool) in ('image','material','xanim') and asset_id not in known}
    print(f'{game}: {len(names)} unique verified seeds; {len(targets)} visual targets',file=sys.stderr,flush=True)
    scratch=(args.scratch_dir or Path(tempfile.gettempdir())).resolve()
    scratch.mkdir(exist_ok=True,parents=True)
    with tempfile.TemporaryDirectory(prefix='visual_numeric_',dir=scratch) as folder:
        temporary=Path(folder).resolve()
        assert temporary.parent==scratch and temporary.name.startswith('visual_numeric_')
        source=temporary/'numeric.rs'
        source.write_text(NATIVE,encoding='utf-8')
        binary=temporary/('numeric.exe' if sys.platform=='win32' else 'numeric')
        subprocess.run([rustc,str(source),'-O','--edition=2021','-o',str(binary)],check=True)
        seed_file=temporary/'seeds.txt'
        seed_file.write_text('\n'.join(names)+'\n',encoding='utf-8')
        target_file=temporary/'targets.txt'
        target_file.write_text('\n'.join(f'{value:x}' for value in sorted(targets))+'\n',encoding='utf-8')
        subprocess.run([str(binary),str(seed_file),str(target_file),str(args.index_max),str(args.threads)],check=True)


if __name__=='__main__':
    main()
