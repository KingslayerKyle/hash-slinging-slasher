"""Generate BO4 SAB sound paths by locally attested directory-token substitutions.

For each known sound basename, collect directory tokens observed at each depth for
that exact basename, then substitute only those same-depth alternatives.
"""
import os,sys,collections
sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","scripts"))
import snapshot

known=set(snapshot.table_names("fnv1a_xsounds")); known.update(snapshot.confirmed_names("sound_asset"))
# BO4 native SAB paths hash with backslashes; normalize seed spelling only for lookup.
rows=[]
for raw in known:
    n=raw.strip().lower().replace("/", "\\")
    if not n or "\\" not in n: continue
    bits=n.split("\\")
    if len(bits)<2: continue
    rows.append((bits[:-1],bits[-1]))
bybase=collections.defaultdict(list)
for dirs,base in rows: bybase[base].append(dirs)
alts=collections.defaultdict(set)
for base, groups in bybase.items():
    for dirs in groups:
        for other in groups:
            for i in range(min(len(dirs),len(other))):
                if dirs[i]!=other[i]: alts[(base,i,len(dirs))].add(other[i])
out=set(); eligible=0
for dirs,base in rows:
    local=False
    for i in range(len(dirs)):
        for tok in alts.get((base,i,len(dirs)),()):
            cand="\\".join(dirs[:i]+[tok]+dirs[i+1:]+[base])
            if cand not in known: out.add(cand); local=True
    eligible += local
print(f"{len(rows):,} native paths, {eligible:,} with same-basename context, {len(out):,} candidates",file=sys.stderr)
print("\n".join(sorted(out)))
