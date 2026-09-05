#!/usr/bin/env python3
"""Exact Atian-menu Cold War literals absent from all prior CW source trees."""
import re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
LIT = re.compile(r'(?:#)?["\']([A-Za-z0-9_./\\\\-]{6,160})["\']')
OLD = ('bocw-source','t9-src','ColdWarGSCMenu','coldwar.gsc','cwmenu','ColdWar-Lucy-Base','demo_mods','shield_mods','T9_BOCW_GSC_Wiki')
def collect(root):
    out=set()
    for p in root.rglob('*') if root.is_dir() else ():
        if p.is_file() and p.suffix.lower() in {'.gsc','.csc','.lua','.txt','.json'}:
            for s in LIT.findall(p.read_text(encoding='utf-8',errors='ignore')):
                s=s.lower().replace('\\\\','/')
                if ('_' in s or '/' in s) and sum(c.isalpha() for c in s)>=3: out.add(s)
    return out
fresh=collect(ROOT/'borrowed'/'t8-atian-menu'/'coldwar')
old=set().union(*(collect(ROOT/'borrowed'/x) for x in OLD))
print('\n'.join(sorted(fresh-old)))
