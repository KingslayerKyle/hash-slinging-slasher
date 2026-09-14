"""BO4, every non-sound pocket: numeric-sibling completion. Every digit group inside a known name
is replaced by its neighbours (value-5 .. value+40, zero-padded to the same width and unpadded),
kept only on an exact unnamed-id match. 25.6M candidates. Generator: C:/tmp/bo4_vox/numsib.py."""
import os
here = os.path.dirname(os.path.abspath(__file__))
for l in open(os.path.join(here, "bo4_numeric_siblings.txt"), encoding="utf-8"):
    if l.strip(): print(l.strip())
