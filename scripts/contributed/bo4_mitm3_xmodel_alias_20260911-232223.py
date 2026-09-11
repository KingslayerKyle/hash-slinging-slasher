"""BO4 xmodel and sound_alias: GPU three-token meet-in-the-middle gap fill, 1,500 prefixes per
pocket x three tokens from that pocket's 2,000 real tokens x its real endings.
Kernel: bo4_aliasfill3_gpu.cu."""
import os
here = os.path.dirname(os.path.abspath(__file__))
for l in open(os.path.join(here, "bo4_mitm3_xmodel_alias.txt"), encoding="utf-8"):
    if l.strip(): print(l.strip())
