"""BO4 image: GPU 1-2 token gap fill over the image pocket. 6,000 image-name prefixes (a known
image name minus its last one or two tokens) x the 4,000 commonest image tokens x the real image
endings (channel letters _c/_n/_g/_o/_s/_m, _icon, _large, ...), exact-id matched against the
26,624 ids of the image pocket that no published name resolves. Kernel: bo4_aliasfill_gpu.cu."""
import os
here = os.path.dirname(os.path.abspath(__file__))
for l in open(os.path.join(here, "bo4_image_gapfill_gpu.txt"), encoding="utf-8"):
    if l.strip(): print(l.strip())
