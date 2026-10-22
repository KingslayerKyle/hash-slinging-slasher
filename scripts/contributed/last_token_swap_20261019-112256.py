# Fresh finds open families (p8_zmu_signage_label_breakroom_<item>, ..._news_<letter>): replace the LAST token of every
# given name with every token in TOKENS, and append every token, so the whole family comes out in one pass.
# usage: py contrib/bo4_models/last_token_swap.py NAMES.txt TOKENS.txt > cands.txt
import sys
toks=[l.strip() for l in open(sys.argv[2]) if l.strip() and len(l.strip())<=24]
out=sys.stdout; seen=set()
for n in (l.strip().split(",")[-1] for l in open(sys.argv[1]) if l.strip()):
    stem=n.rsplit("_",1)[0]
    if stem in seen: continue
    seen.add(stem)
    for t in toks: out.write(stem+"_"+t+"\n"); out.write(n+"_"+t+"\n")
