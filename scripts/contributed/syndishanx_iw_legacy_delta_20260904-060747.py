#!/usr/bin/env python3
"""Exact pre-BO4 IW-era literals from the independent SyndiShanX script dump."""
import re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
L=re.compile(r'(?:#)?["\']([A-Za-z0-9_./\\\\-]{6,160})["\']')
def c(r):
 o=set()
 for p in r.rglob('*') if r.is_dir() else ():
  if p.is_file() and p.suffix.lower() in {'.gsc','.csc','.lua'}:
   for s in L.findall(p.read_text(encoding='utf8',errors='ignore')):
    s=s.lower().replace('\\\\','/')
    if ('_' in s or '/' in s) and sum(x.isalpha() for x in s)>=3:o.add(s)
 return o
s=ROOT/'borrowed'/'SyndiShanX-COD-GSC-Source'
print('\n'.join(sorted(set().union(*(c(s/x) for x in ('WAW-GSC','IW4-GSC','IW4x-GSC','IW5-GSC','IW6-GSC','IW7-GSC')))-c(ROOT/'borrowed'/'oldcod-source'))))
