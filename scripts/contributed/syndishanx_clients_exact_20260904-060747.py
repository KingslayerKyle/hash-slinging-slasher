import re
from pathlib import Path
R=Path(__file__).resolve().parents[1]; L=re.compile(r'(?:#)?["\']([A-Za-z0-9_./\\\\-]{6,160})["\']')
o=set(); s=R/'borrowed'/'SyndiShanX-COD-GSC-Source'
for d in ('S1X-GSC','S2-GSC','S4-GSC','HMW-GSC'):
 for p in (s/d).rglob('*'):
  if p.is_file() and p.suffix.lower() in {'.gsc','.csc','.lua'}:
   for x in L.findall(p.read_text(encoding='utf8',errors='ignore')):
    x=x.lower().replace('\\\\','/')
    if ('_' in x or '/' in x) and sum(c.isalpha() for c in x)>=3:o.add(x)
print('\n'.join(sorted(o)))
