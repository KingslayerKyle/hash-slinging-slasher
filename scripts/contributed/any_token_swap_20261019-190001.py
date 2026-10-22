# Snowball for fresh model finds: replace ANY one token of each name with every token of a vocabulary list
# (sibling slots like tablet_{water,car,door}_on or loc_{asylum,lobby,moon} sit mid-name, not only at the end).
# usage: py contrib/bo4_models/any_token_swap.py NAMES.txt VOCAB.txt | confirm_list ...
import sys
V=[l.strip() for l in open(sys.argv[2]) if l.strip()]
seen=set(); w=sys.stdout.write
for n in (l.strip().split(",")[-1].split("\t")[-1] for l in open(sys.argv[1]) if l.strip()):
    d,_,b=n.rpartition("/"); d=d+"/" if d else ""; t=b.split("_")
    for i in range(1,len(t)):
        pre="_".join(t[:i]); post="_".join(t[i+1:])
        for v in V: w(d+pre+"_"+v+("_"+post if post else "")+"\n")
