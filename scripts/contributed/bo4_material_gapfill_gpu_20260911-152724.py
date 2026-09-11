"""BO4 material: GPU 1-2 token gap fill over the material pocket. 6,000 material-name prefixes
(a known material name minus its last one or two tokens) x the 4,000 commonest material tokens x
the real material endings, exact-id matched against the 16,358 material ids no published name
resolves. Kernel: bo4_aliasfill_gpu.cu."""
import os
here = os.path.dirname(os.path.abspath(__file__))
for l in open(os.path.join(here, "bo4_material_gapfill_gpu.txt"), encoding="utf-8"):
    if l.strip(): print(l.strip())
