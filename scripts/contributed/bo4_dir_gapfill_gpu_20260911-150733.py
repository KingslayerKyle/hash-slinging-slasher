"""BO4 sound_asset: GPU 1-2 token gap fill inside every known BO4 sound directory
(2,635 directories x 4,233 real sound tokens x _NN x the five real endings, RTX 3090).
Kernel: bo4_aliasfill_gpu.cu. A measured near-dead end: 10 names for the whole sweep."""
import os
here = os.path.dirname(os.path.abspath(__file__))
for l in open(os.path.join(here, "bo4_dir_gapfill_gpu.txt"), encoding="utf-8"):
    if l.strip(): print(l.strip())
