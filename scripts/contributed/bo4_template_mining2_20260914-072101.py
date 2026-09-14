"""BO4, every pocket: systematic token-slot template mining.

Each known name is abstracted one token at a time into a template (prefix, *, suffix) - at the
path-segment level, at the token-inside-segment level, and over the delimiter set \ / _ . - space #
- then each template is crossed with a token alphabet. What actually pays is a per-pocket template
crossed with a POCKET-WIDE or GLOBAL alphabet (469 + 390 + 285 + 282 names); requiring two
templates inside one pocket to share two fillers collapses the candidate volume by four orders of
magnitude and returns almost nothing (18 and 1). ~30 billion candidates per pass, exact-id matched,
second pass on the enlarged corpus, iterated until a full round over every pocket added zero.
Generators: C:/tmp/bo4_vox/agent_mine.py, agent_run.py, agent_global.py, xprod.cpp."""
import os
here = os.path.dirname(os.path.abspath(__file__))
for l in open(os.path.join(here, "bo4_template_mining2.txt"), encoding="utf-8"):
    if l.strip(): print(l.strip())
