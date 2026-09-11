"""BO4, every pocket: every identifier-like string in the public w28447 dump (23,387 files,
2.39M distinct strings), hashed as written, lowercased, and with forward slashes turned into
backslashes, kept only on an exact unnamed-id match. The earlier harvest of the same dump only
checked the six pockets the tool searches by default, which is why the effect pocket (fx),
the gesture, xcam, sanim, footstep and keyvaluepairs pockets were missed entirely.
Generator: C:/tmp/bo4_vox/all_strings.py."""
import os
here = os.path.dirname(os.path.abspath(__file__))
for l in open(os.path.join(here, "bo4_all_dump_strings.txt"), encoding="utf-8"):
    if l.strip(): print(l.strip())
