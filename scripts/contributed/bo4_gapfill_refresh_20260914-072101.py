"""BO4 image/material/xmodel/xanim/sound_alias: GPU 1-2 token gap fill re-run after ~5,000 new
names were confirmed - vocabularies (4,000 tokens), prefixes (8,000) and open-id targets all
rebuilt from the enlarged corpus. Kernel: bo4_aliasfill_gpu.cu."""
import os
here = os.path.dirname(os.path.abspath(__file__))
for l in open(os.path.join(here, "bo4_gapfill_refresh.txt"), encoding="utf-8"):
    if l.strip(): print(l.strip())
