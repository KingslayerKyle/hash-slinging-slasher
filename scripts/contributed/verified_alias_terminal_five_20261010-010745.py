"""Recover a new fifth terminal alias byte using target-witnessed prefixes.

Uses verified aliases and the target's alias pool, excludes all known/claimed
keys and the old two-, three- and four-byte domains, and rehashes complete names. The embedded
standalone Rust solver is compiled locally in a temporary directory. It joins
two indexed prefix bytes, a solved middle byte and two reversed tail bytes.
The exact index has a 3 GiB limit; oversized inputs fail without dropping data. No game,
network, other asset pool or prebuilt executable is used. Normal confirmation
and submission are required. --sample measures a finite target subset.
"""
import argparse
from collections import defaultdict
import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent
while ROOT != ROOT.parent and not (ROOT / 'scripts/snapshot.py').is_file():
    ROOT = ROOT.parent
if not (ROOT / 'scripts/snapshot.py').is_file():
    ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / 'scripts'))
import snapshot

RUST = r'''
use std::{collections::HashSet,fs,io::{self,Write},sync::Arc,thread};
const PRIME:u64=0x100000001b3;
const BASIS:u64=0xcbf29ce484222325;
const MASK:u64=0x7fffffffffffffff;
const EMPTY:u64=u64::MAX;
fn feed(h:u64,b:u8)->u64{(h^(b as u64)).wrapping_mul(PRIME)}
fn hash(s:&str)->u64{s.bytes().fold(BASIS,feed)}
fn slot(mut v:u64,mask:usize)->usize{
 v=(v^(v>>30)).wrapping_mul(0xbf58476d1ce4e5b9);
 v=(v^(v>>27)).wrapping_mul(0x94d049bb133111eb);
 ((v^(v>>31)) as usize)&mask
}
fn number(raw:&[u8],at:&mut usize)->u64{
 let n=u64::from_le_bytes(raw[*at..*at+8].try_into().unwrap());*at+=8;n
}
struct Index{keys:Vec<u64>,values:Vec<u64>,prefixes:Vec<String>,mask:usize}
fn main(){
 let args:Vec<String>=std::env::args().collect();
 let raw=fs::read(&args[1]).unwrap();let mut at=0;
 let count=number(&raw,&mut at) as usize;assert!(count<=u32::MAX as usize);
 let mut prefixes=Vec::new();
 for _ in 0..count{
  let len=number(&raw,&mut at) as usize;
  prefixes.push(String::from_utf8(raw[at..at+len].to_vec()).unwrap());at+=len;
 }
 let n=number(&raw,&mut at);let mut ids=Vec::new();
 for _ in 0..n{ids.push(number(&raw,&mut at));}assert_eq!(at,raw.len());
 let alphabet=b"abcdefghijklmnopqrstuvwxyz0123456789_-";
 let entries=count.checked_mul(alphabet.len()*alphabet.len()).unwrap();
 let capacity=(entries.checked_mul(10).unwrap().div_ceil(7)).next_power_of_two();
 assert!(capacity.checked_mul(16).unwrap()<=3*1024*1024*1024,"Exact index exceeds 3 GiB; no prefixes discarded");
 let mut keys=Vec::new();keys.try_reserve_exact(capacity).expect("Index key allocation failed");keys.resize(capacity,EMPTY);
 let mut values=Vec::new();values.try_reserve_exact(capacity).expect("Index payload allocation failed");values.resize(capacity,0);
 let mask=capacity-1;
 for (prefix_id,prefix) in prefixes.iter().enumerate(){
  let h=hash(prefix);
  for &a in alphabet{
   let first=feed(h,a);
   for &b in alphabet{
    let value=feed(first,b);let key=value>>8;
    let mut position=slot(key,mask);
    // Equal upper-56-bit keys retain every payload, rather than overwrite.
    while keys[position]!=EMPTY{position=(position+1)&mask;}
    keys[position]=key;
    values[position]=(prefix_id as u64)|((a as u64)<<32)|((b as u64)<<40)|((value as u8 as u64)<<48);
   }
  }
 }
 let index=Arc::new(Index{keys,values,prefixes,mask});
 let mut inverse=1u64;for _ in 0..6{inverse=inverse.wrapping_mul(2u64.wrapping_sub(PRIME.wrapping_mul(inverse)));}
 assert_eq!(PRIME.wrapping_mul(inverse),1);
 let workers=thread::available_parallelism().map_or(1,usize::from).min(16).min(ids.len().max(1));
 let mut threads=Vec::new();
 for shard in ids.chunks(ids.len().div_ceil(workers).max(1)){
  let part=shard.to_vec();let index=Arc::clone(&index);
  threads.push(thread::spawn(move||{
   let mut found=HashSet::new();
   for key in part{
    for full in [key,key|!MASK]{
     let last_step=full.wrapping_mul(inverse);
     for &e in alphabet{
      let d_step=(last_step^(e as u64)).wrapping_mul(inverse);
      for &d in alphabet{
       let c_step=(d_step^(d as u64)).wrapping_mul(inverse);
       let key56=c_step>>8;let mut position=slot(key56,index.mask);
       while index.keys[position]!=EMPTY{
        if index.keys[position]==key56{
         let value=index.values[position];let c=((value>>48) as u8)^(c_step as u8);
         if alphabet.contains(&c){
          let prefix=&index.prefixes[(value as u32) as usize];
          let a=(value>>32) as u8;let b=(value>>40) as u8;
          let name=format!("{prefix}{}{}{}{}{}",a as char,b as char,c as char,d as char,e as char);
          if hash(&name)==full{found.insert(name);}
         }
        }
        position=(position+1)&index.mask;
       }
      }
     }
    }
   }
   found
  }));
 }
 let mut found=HashSet::new();for worker in threads{found.extend(worker.join().unwrap());}
 let mut rows:Vec<_>=found.into_iter().collect();rows.sort();
 let mut out=io::BufWriter::new(io::stdout().lock());for name in rows{writeln!(out,"{name}").unwrap();}
}
'''

def corpus():
    names = set(snapshot.table_names('fnv1a_soundbanks_aliases_v2'))
    for top in ['all_names', 'findings']:
        for path in (ROOT / top).glob('*/sound_alias.txt'):
            for row in path.read_text(encoding='utf-8').splitlines():
                raw, sep, name = row.partition(',')
                if not sep or not name.isascii():
                    continue
                try:
                    key = int(raw, 16) & snapshot.ID_MASK
                except ValueError:
                    continue
                name = name.strip().lower().replace(chr(92), '/')
                if snapshot.fnv1a(name, 'MODWAR7', 'sound_alias') & snapshot.ID_MASK == key:
                    names.add(name)
    return {n.lower().replace(chr(92), '/') for n in names if n.isascii() and n.strip() == n}

def run_solver(prefixes, ids):
    if not prefixes or not ids:
        return []
    with tempfile.TemporaryDirectory(prefix='alias_terminal_five_') as temp:
        folder = Path(temp)
        source = folder / 'solve.rs'
        binary = folder / ('solve.exe' if sys.platform == 'win32' else 'solve')
        source.write_text(RUST, encoding='utf-8')
        subprocess.run(['rustc', '--edition=2021', '-O', str(source), '-o', str(binary)], check=True)
        payload = bytearray(struct.pack('<Q', len(prefixes)))
        for prefix in sorted(prefixes):
            data = prefix.encode('ascii')
            payload.extend(struct.pack('<Q', len(data)))
            payload.extend(data)
        payload.extend(struct.pack('<Q', len(ids)))
        for key in sorted(ids):
            payload.extend(struct.pack('<Q', key))
        data_path = folder / 'inputs.bin'
        data_path.write_bytes(payload)
        result = subprocess.check_output([str(binary), str(data_path)])
        return result.decode('utf-8').splitlines()

def inputs(names, held, known):
    target_names = {n for n in names if snapshot.fnv1a(n, 'MODWAR7', 'sound_alias') & snapshot.ID_MASK in held}
    prefixes = {n[:-5] for n in target_names if len(n) >= 13}
    old = ({n[:-2] for n in names if len(n) > 2},
           {n[:-3] for n in names if len(n) > 3},
           {n[:-4] for n in names if len(n) > 4})
    excluded = {key & snapshot.ID_MASK for key in known}
    excluded.update(snapshot.fnv1a(n, 'MODWAR7', 'sound_alias') & snapshot.ID_MASK for n in names)
    return prefixes, old, held - excluded

def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument('--game', choices=sorted(snapshot.MODERN), required=True)
    p.add_argument('--sample', type=int, default=0)
    a = p.parse_args()
    if a.sample < 0:
        p.error('sample must be nonnegative')
    shot = snapshot.read(ROOT / 'snapshots' / (a.game.lower() + '.ids'))
    assert shot.game == a.game
    held = set(shot.by_pool()['sound_alias'])
    names = corpus()
    known = snapshot.known_hashes(game=a.game)
    claimed = ROOT / 'state/claimed.txt'
    if claimed.exists():
        for row in claimed.read_text().splitlines():
            try:
                known.add(int(row, 16))
            except ValueError:
                pass
    prefixes, old, ids = inputs(names, held, known)
    population = len(ids)
    if a.sample and len(ids) > a.sample:
        ordered = sorted(ids)
        ids = {ordered[i * len(ordered) // a.sample] for i in range(a.sample)}
    found = defaultdict(list)
    for name in run_solver(prefixes, ids):
        key = snapshot.fnv1a(name, a.game, 'sound_alias') & snapshot.ID_MASK
        assert key in ids
        if name in names or name[:-2] in old[0] or name[:-3] in old[1] or name[:-4] in old[2]:
            continue
        found[key].append(name)
    safe = sorted(v[0] for v in found.values() if len(v) == 1)
    print(json.dumps(dict(game=a.game, target_prefixes=len(prefixes), population=population,
                         searched_ids=len(ids), verified_new=len(safe),
                         ambiguous_ids=sum(len(v) > 1 for v in found.values()))), file=sys.stderr)
    for name in safe:
        print(name)

if __name__ == '__main__':
    main()
