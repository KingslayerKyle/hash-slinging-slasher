"""BO4: exhaustive speaker-token search. Every token over [a-z0-9_] of length 3, 4 and 5 is tried
in place of the speaker, on the alias side (vox_<TOK><suffix>) and in the VO path shape
(en\vox\scripted\<dir>\<TOK>\vox_<TOK><suffix>), against the real suffix sets taken from named VO.
Subsumes any hand-written list of character or operator abbreviations. Kernel: bo4_tokfind_gpu.cu."""
import os
here = os.path.dirname(os.path.abspath(__file__))
for l in open(os.path.join(here, "bo4_tokfind_gpu.txt"), encoding="utf-8"):
    if l.strip(): print(l.strip())
