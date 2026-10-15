# BO4 models: root/skeleton bone names from a Saluki model export (cast files) as model-name candidates.
# Static models often keep the source mesh name as the root bone ("<model>_lod0"). Prints variants:
# the bone, minus _lod<N>/_low/_high, minus a leading base_/geo_, plus splm/ clt/ cltp/ dirs, p7/p8/t8 swaps.
import json,re,sys
b=json.load(open("state/bo4exp/bones.json"))
out=set()
for v in b.values():
    for x in v:
        x=x.lower().replace("|","_").replace(":","_")
        base={x}
        y=re.sub(r"_(lod|lod_)?\d$","",x); base.add(y)
        y2=re.sub(r"_(lod\d+|low|high|hi|lo|geo|mesh|mdl)$","",x); base.add(y2)
        for z in list(base):
            for p in ("base_","geo_","mesh_","pasted__","root_"):
                if z.startswith(p): base.add(z[len(p):])
        for z in list(base):
            m=re.match(r"([pt])([78])_(.*)",z)
            if m: base.add("p%s_%s"%(m.group(2),m.group(3)))
        for z in base:
            out.add(z)
            for d in ("splm/","clt/","cltp/"): out.add(d+z)
for n in sorted(out): print(n)
