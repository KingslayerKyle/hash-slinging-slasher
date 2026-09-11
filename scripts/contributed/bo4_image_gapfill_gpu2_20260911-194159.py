"""BO4 image: second GPU 1-2 token gap fill, widened to all 20,000 image-name prefixes (the first
pass used 6,000) against the refreshed set of image ids no published name resolves.
Kernel: bo4_aliasfill_gpu.cu."""
import os
here = os.path.dirname(os.path.abspath(__file__))
for l in open(os.path.join(here, "bo4_image_gapfill_gpu2.txt"), encoding="utf-8"):
    if l.strip(): print(l.strip())
