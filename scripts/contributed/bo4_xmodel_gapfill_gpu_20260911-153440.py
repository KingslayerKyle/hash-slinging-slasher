"""BO4 xmodel: GPU 1-2 token gap fill over the xmodel pocket. 6,000 xmodel-name prefixes (a known
xmodel name minus its last one or two tokens) x the 4,000 commonest xmodel tokens x the real
xmodel endings (_view/_world/_lod, ...), exact-id matched against the 11,026 xmodel ids no
published name resolves. Kernel: bo4_aliasfill_gpu.cu."""
import os
here = os.path.dirname(os.path.abspath(__file__))
for l in open(os.path.join(here, "bo4_xmodel_gapfill_gpu.txt"), encoding="utf-8"):
    if l.strip(): print(l.strip())
