"""BO4 image and material: GPU three-token meet-in-the-middle gap fill. 1,500 prefixes per pocket
x three tokens from the 2,000 real tokens of that pocket x its real endings. Affordable only
after the vocabulary pruning: the forward table is the square of the vocabulary size, so 2,000
tokens means 4M states per prefix instead of 100M. Kernel: bo4_aliasfill3_gpu.cu."""
import os
here = os.path.dirname(os.path.abspath(__file__))
for l in open(os.path.join(here, "bo4_mitm3_image_material.txt"), encoding="utf-8"):
    if l.strip(): print(l.strip())
