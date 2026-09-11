"""BO4 xanim: GPU three-token gap fill (meet-in-the-middle). 1,500 animation prefixes x three
tokens drawn from the 2,000 real animation tokens x the real animation endings. Only affordable
because the vocabulary was pruned: at 10,000 tokens the forward table is 100M states per prefix,
at 2,000 it is 4M. Kernel: bo4_aliasfill3_gpu.cu."""
import os
here = os.path.dirname(os.path.abspath(__file__))
for l in open(os.path.join(here, "bo4_xanim_gapfill3_gpu.txt"), encoding="utf-8"):
    if l.strip(): print(l.strip())
