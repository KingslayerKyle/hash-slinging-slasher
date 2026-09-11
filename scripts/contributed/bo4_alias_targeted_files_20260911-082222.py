r"""BO4 sound files found by exact-id targeted search: the w28447/-8 dump's sound tables
(source/tables/sound/<zone>.<lang>.json) link every alias to its file id (assetId). For each unnamed
file id whose alias is named, candidates = en\vox\scripted\<X>\<speaker>\<alias>_<NN>.sn100/ln100
with X = exerts / map names / modes / known middles (plus zombies reorder for vox_plr_N_*), checked
against that one id (bo4_alias_targeted_search.py). 10,633 of 19,156 linked files."""
import os
here = os.path.dirname(os.path.abspath(__file__))
for l in open(os.path.join(here, "bo4_alias_targeted_files.txt"), encoding="utf-8"):
    if l.strip(): print(l.strip())
