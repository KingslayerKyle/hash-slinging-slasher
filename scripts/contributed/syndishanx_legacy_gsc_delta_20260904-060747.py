#!/usr/bin/env python3
"""Exact BO1/BO2/BO3 literals from the SyndiShanX dump, minus local legacy source."""
import re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
LIT=re.compile(r'(?:#)?["\']([A-Za-z0-9_./\\\\-]{6,160})["\']')
def collect(root):
 out=set()
 for p in root.rglob('*') if root.is_dir() else ():
  if p.is_file() and p.suffix.lower() in {'.gsc','.csc','.lua'}:
   for s in LIT.findall(p.read_text(encoding='utf-8',errors='ignore')):
    s=s.lower().replace('\\\\','/')
    if ('_' in s or '/' in s) and sum(c.isalpha() for c in s)>=3: out.add(s)
 return out
fresh=set().union(*(collect(ROOT/'borrowed'/'SyndiShanX-COD-GSC-Source'/x) for x in ('BO1-GSC','BO2-GSC','BO3-GSC')))
old=collect(ROOT/'borrowed'/'oldcod-source')
print('\n'.join(sorted(fresh-old)))
