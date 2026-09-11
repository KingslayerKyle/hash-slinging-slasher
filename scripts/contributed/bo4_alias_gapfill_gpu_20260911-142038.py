"""BO4 sound_alias names from a GPU 1-2 token gap fill (bo4_aliasfill_gpu.cu, RTX 3090).

Shape: <prefix><t1>[_<t2>]<suffix>, exact-id matched against the still-unnamed pocket-171 ids.
  prefix   every known BO4 alias minus its last one or two tokens, kept when seen twice (4,500)
  t1,t2    the 10,000 commonest tokens of known BO4 alias names and sound-file basenames
  suffix   "" or _0.._9 or _00.._19, the real alias ending set
A 2^28-bit bitmap of the target ids rejects candidates before the binary search, which is what
makes the whole 4,500-prefix sweep about 20 minutes instead of a day. Chance matches expected at
this candidate count: 0.04. Inputs built by C:/tmp/bo4_vox/gen_alias_gpu_inputs.py."""
import os
here = os.path.dirname(os.path.abspath(__file__))
for l in open(os.path.join(here, "bo4_alias_gapfill_gpu.txt"), encoding="utf-8"):
    if l.strip(): print(l.strip())
