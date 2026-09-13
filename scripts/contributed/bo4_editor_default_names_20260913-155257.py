"""BO4 light_description: the names are level-editor defaults, "new" followed by a 31-bit
integer (new984592 ... new2143003307). Found by noticing new984592 in an exhaustive 9-character
sweep, then enumerating "new" + 1..12 digits on the GPU (10^12 candidates, 82 s, alphabet
0123456789): 552 names, all in light_description, none anywhere else. Kernel: bo4_tokfind_gpu.cu
with a custom alphabet."""
import os
here = os.path.dirname(os.path.abspath(__file__))
for l in open(os.path.join(here, "bo4_editor_default_names.txt"), encoding="utf-8"):
    if l.strip(): print(l.strip())
