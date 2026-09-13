"""BO4, every pocket: contracted forms of proper nouns substituted into creature-bearing templates.
9,222 proper nouns (subtitle capitalised words, spawner tokens, the boss/character roster) each
yield consonant skeletons (blightfather -> bltfthr), initial-preserving skeletons, truncations to
3..6 letters and their combinations: 27,829 variants. Every known name carrying a proper noun or
one of its variants becomes a template (934,323), and every variant is tried in the slot.
26 billion candidates, exact-id matched, in seconds with the C++ engine (subst.cpp) after a pure
Python attempt ran for three hours without finishing. Generators: C:/tmp/bo4_vox/skeleton_dump.py,
subst.cpp."""
import os
here = os.path.dirname(os.path.abspath(__file__))
for l in open(os.path.join(here, "bo4_proper_noun_contractions.txt"), encoding="utf-8"):
    if l.strip(): print(l.strip())
