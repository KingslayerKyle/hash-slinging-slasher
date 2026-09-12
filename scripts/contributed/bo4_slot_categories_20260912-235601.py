"""BO4, every pocket: token-slot categories mined from the whole known corpus.
Each of the 451,605 known names is abstracted one token at a time into a template (prefix, *,
suffix); 101,857 templates carry three or more different fillers. Two templates that share at
least two fillers are treated as drawing on the same category, so their filler lists merge - which
lets a template be offered a token it has never carried but a sibling template has. 11.7M
candidates, all exact-id matched. Generators: C:/tmp/bo4_vox/slots.py, cats.py."""
import os
here = os.path.dirname(os.path.abspath(__file__))
for l in open(os.path.join(here, "bo4_slot_categories.txt"), encoding="utf-8"):
    if l.strip(): print(l.strip())
