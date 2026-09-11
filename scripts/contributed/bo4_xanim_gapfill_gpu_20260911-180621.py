"""BO4 xanim: GPU 1-2 token gap fill over the animation pocket, never attacked before.
6,000 animation-name prefixes (a known xanim name minus its last one or two tokens) x the 4,000
commonest animation tokens x the real animation endings, exact-id matched against the 5,017
animation ids no published name resolves. Kernel: bo4_aliasfill_gpu.cu."""
import os
here = os.path.dirname(os.path.abspath(__file__))
for l in open(os.path.join(here, "bo4_xanim_gapfill_gpu.txt"), encoding="utf-8"):
    if l.strip(): print(l.strip())
