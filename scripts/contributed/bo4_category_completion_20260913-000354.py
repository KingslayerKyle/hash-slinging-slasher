"""BO4: closed-category completion on top of the mined token slots. Three rules: a category whose
members are all numeric is extended past its observed range (padded and unpadded); a category
sharing a common affix has the affix stripped, the residue completed from a closed domain
(language codes, resolutions) and the affix glued back; and every name carrying one of the 51 real
zone names has every other zone substituted in.
Measured limits worth writing down: the <lang>safe_<res>_<zone> family is COMPLETE at four
languages (ara, ger, jp, k15) x two resolutions (1080, 4k) - a 748,980-candidate grid over the
full locale and resolution domains returned zero, so no 1440/2k/other-language variant exists.
Short zone forms (office, orange, ...) substituted into names returned zero over 1.2M candidates;
only full zone names (zm_office -> zm_orange) pay. Generators: C:/tmp/bo4_vox/cats3.py, zonesub.py."""
import os
here = os.path.dirname(os.path.abspath(__file__))
for l in open(os.path.join(here, "bo4_category_completion.txt"), encoding="utf-8"):
    if l.strip(): print(l.strip())
