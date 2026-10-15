# Clean cast bone names into name-like cores (shared by groups.py and blocks.py).
import re
GEN=re.compile(r"^(tag_origin|j_.*|tag_.*_jnt|p?cylinder\d*|p?plane\d*|p?cube\d*|box\d*|polysurface\d*|pasted_.*|object\d*|group\d*|mesh\d*|patch_mesh_.*|[a-z]?\d+[a-z0-9]*|root|bone\d*)$")
def bone_cores(bs):
    out=set()
    for x in bs:
        x=x.lower().replace("|","_").replace(":","_").strip("_")
        if GEN.match(x) or len(x)<4: continue
        for _ in range(2):
            x=re.sub(r"_(lod\d+|lod|low|high|hi|geo|node|mdl|mesh|animate|attach)$","",x)
        x=re.sub(r"^(base|geo|mesh|tag)_","",x)
        x=re.sub(r"_(attach|animate)$","",x)
        if len(x)>=4 and not GEN.match(x):
            out.add(x)
            if not re.match(r"(p\d|c|veh|wpn|attach|t\d|fxanim|zm|mp)_",x) and x.count("_")>=2:
                out.add("p8_"+x); out.add("p7_"+x)
        m=re.match(r"t([78])_(.*)",x)
        if m: out.add("p%s_%s"%m.groups())
    return out
