# Sibling fill for freshly found model names: every number token shifted over 0..max (same width), size words swapped
# (sml/med/lrg/small/medium/large), sides swapped (lt/rt/left/right/l/r), optional trailing _01/_02/a/b, one token dropped.
# usage: py contrib/bo4_models/sibling_fill.py NAMES.txt [max=24] > cands.txt
import sys,re
A=dict(a.split("=",1) for a in sys.argv[2:] if "=" in a); MX=int(A.get("max",24))
G=[["sml","med","lrg","small","medium","large","sm","md","lg","xl"],["lt","rt","left","right","l","r","lft","rgt"],
   ["on","off"],["open","closed"],["top","bottom","bot","mid","middle"],["front","back","rear"],["full","half","empty"],
   ["clean","dirty","dmg","damaged","broken","destroyed","dest"]]
out=set()
for n in (l.strip().split(",")[-1] for l in open(sys.argv[1]) if l.strip()):
    d,_,b=n.rpartition("/"); d=d+"/" if d else ""; t=b.split("_")
    for i,x in enumerate(t):
        if x.isdigit():
            for k in range(0,MX+1): out.add(d+"_".join(t[:i]+[str(k).zfill(len(x))]+t[i+1:]))
        m=re.fullmatch(r"(\d+)([a-z])",x)
        if m:
            for c in "abcdefgh": out.add(d+"_".join(t[:i]+[m.group(1)+c]+t[i+1:]))
        for g in G:
            if x in g:
                for y in g: out.add(d+"_".join(t[:i]+[y]+t[i+1:]))
        if 2<=i<len(t): out.add(d+"_".join(t[:i]+t[i+1:]))
    for s in ("_01","_02","_03","a","b","_a","_b","_lod","_low","_dmg","_broken","_decal"): out.add(n+s)
sys.stdout.write("".join(x+"\n" for x in out))
