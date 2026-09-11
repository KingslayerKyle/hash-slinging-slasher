"""BO4 sound_alias: second GPU 1-2 token gap fill, run against the 6,617 ids that are genuinely
still unnamed (recomputed by re-hashing every published name, because cod-name-db stores 60-bit
hashes while the snapshot pockets are 63-bit) and with the vocabulary cut to the 4,233 tokens that
actually occur in a real BO4 sound name. 6,000 alias prefixes. Kernel: bo4_aliasfill_gpu.cu."""
import os
here = os.path.dirname(os.path.abspath(__file__))
for l in open(os.path.join(here, "bo4_alias_gapfill_gpu2.txt"), encoding="utf-8"):
    if l.strip(): print(l.strip())
