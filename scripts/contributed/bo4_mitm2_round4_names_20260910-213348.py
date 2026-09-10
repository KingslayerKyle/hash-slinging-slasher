"""MITM round 4 (bo4_mitm2_gap_fill.cpp) on zm_white / zm_orange with the NPC-speaker seeds, plus
the first prefixes of the GPU 3-token gap fill (bo4_gapfill3_gpu.cu: prefix + t1_t2_t3 + suffix,
forward table of vocab^2 states on the host, backward unhash of target<-suffix<-t3 on the 3090)."""
import os
here = os.path.dirname(os.path.abspath(__file__))
for fn in ("bo4_mitm2_round4_names_20260910.txt", "bo4_gapfill_gpu_3tok_partial_20260910.txt"):
    for l in open(os.path.join(here, fn), encoding="utf-8"):
        if l.strip(): print(l.strip())
