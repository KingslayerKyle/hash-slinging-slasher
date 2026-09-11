"""BO4 sound_asset: index completion. Every known sound file whose basename ends in _NN has its
whole index range retried (_0.._9, _00.._119, _000.._009) against the five real endings
(.sn100/.ln100/.ll100/.sl100/.pn100.pc.snd), kept only on an exact unnamed-id match.
Generator: C:/tmp/bo4_vox/gen_index_completion.py; names in bo4_index_completion.txt."""
import os
here = os.path.dirname(os.path.abspath(__file__))
for l in open(os.path.join(here, "bo4_index_completion.txt"), encoding="utf-8"):
    if l.strip(): print(l.strip())
