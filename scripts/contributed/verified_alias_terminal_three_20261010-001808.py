"""Recover a new third terminal alias byte using target-witnessed prefixes.

Uses verified aliases and the target's alias pool, excludes all known/claimed
keys and the old two-byte domain, and rehashes complete names. The embedded
standalone Rust solver is compiled locally in a temporary directory. No game,
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
use std::{collections::{HashMap,HashSet},fs,io::{self,Write},sync::Arc,thread};
const PRIME:u64=0x100000001b3;
const BASIS:u64=0xcbf29ce484222325;
const MASK:u64=0x7fffffffffffffff;
fn hash(s:&str)->u64{s.bytes().fold(BASIS,|h,b|(h^(b as u64)).wrapping_mul(PRIME))}
fn number(raw:&[u8],at:&mut usize)->u64{
 let n=u64::from_le_bytes(raw[*at..*at+8].try_into().unwrap());*at+=8;n
}
fn main(){
 let args:Vec<String>=std::env::args().collect();
 let raw=fs::read(&args[1]).unwrap();let mut at=0;
 let count=number(&raw,&mut at);
 let mut prefixes:HashMap<u64,Vec<(u8,String)>>=HashMap::new();
 for _ in 0..count{
  let len=number(&raw,&mut at) as usize;
  let s=String::from_utf8(raw[at..at+len].to_vec()).unwrap();at+=len;
  let value=hash(&s);prefixes.entry(value>>8).or_default().push((value as u8,s));
 }
 let n=number(&raw,&mut at);let mut keys=Vec::new();
 for _ in 0..n{keys.push(number(&raw,&mut at));}assert_eq!(at,raw.len());
 let alphabet=b"abcdefghijklmnopqrstuvwxyz0123456789_-";
 let mut inverse=1u64;for _ in 0..6{inverse=inverse.wrapping_mul(2u64.wrapping_sub(PRIME.wrapping_mul(inverse)));}
 assert_eq!(PRIME.wrapping_mul(inverse),1);
 let workers=thread::available_parallelism().map_or(1,usize::from).min(16).min(keys.len().max(1));
 let index=Arc::new(prefixes);let mut threads=Vec::new();
 for shard in keys.chunks(keys.len().div_ceil(workers).max(1)){
  let part=shard.to_vec();let index=Arc::clone(&index);
  threads.push(thread::spawn(move||{
   let mut found=HashSet::new();
   for key in part{
    for full in [key,key|!MASK]{
     let last_step=full.wrapping_mul(inverse);
     for &last in alphabet{
      let middle_step=(last_step^(last as u64)).wrapping_mul(inverse);
      for &middle in alphabet{
       let first_step=(middle_step^(middle as u64)).wrapping_mul(inverse);
       if let Some(bucket)=index.get(&(first_step>>8)){
        for (low,prefix) in bucket{
         let first=low^(first_step as u8);
         if !alphabet.contains(&first){continue;}
         let name=format!("{prefix}{}{}{}",first as char,middle as char,last as char);
         if hash(&name)==full{found.insert(name);}
        }
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
    with tempfile.TemporaryDirectory(prefix='alias_terminal_three_') as temp:
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
    prefixes = {n[:-3] for n in target_names if len(n) >= 11}
    old = {n[:-2] for n in names if len(n) > 2}
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
        if name in names or name[:-2] in old:
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
