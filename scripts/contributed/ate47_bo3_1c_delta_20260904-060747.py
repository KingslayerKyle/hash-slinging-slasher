import re
from pathlib import Path
R=Path(__file__).resolve().parents[1]; L=re.compile(r'(?:#)?["\']([A-Za-z0-9_./\\\\-]{6,160})["\']')
def c(r):
 o=set()
 for p in r.rglob('*') if r.is_dir() else ():
  if p.is_file() and p.suffix.lower() in {'.gsc','.csc','.lua'}:
   for x in L.findall(p.read_text(encoding='utf8',errors='ignore')):
    x=x.lower().replace('\\\\','/')
    if ('_' in x or '/' in x) and sum(q.isalpha() for q in x)>=3:o.add(x)
 return o
print('\n'.join(sorted(c(R/'borrowed'/'ate47-bo3-source')-c(R/'borrowed'/'oldcod-source'))))
