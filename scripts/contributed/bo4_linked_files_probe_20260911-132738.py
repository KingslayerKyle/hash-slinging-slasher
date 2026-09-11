"""BO4 sound_asset file names recovered by exact-id probing of the alias->assetId link in the
public w28447 dump (source/tables/sound/*.json): for every file id still unnamed whose linked
alias IS named, rebuild <known directory> + <alias> + _NN variant + .sn100/.ln100.pc.snd and keep
only candidates whose fnv1a-63 equals that exact file id. Directories come from the directory set
of already-named files, indexed by the alias' own speaker/family token.
Generator: C:/tmp/bo4_vox/gen_linked_files_probe.py; names in bo4_linked_files_probe.txt."""
import os
here = os.path.dirname(os.path.abspath(__file__))
for l in open(os.path.join(here, "bo4_linked_files_probe.txt"), encoding="utf-8"):
    if l.strip(): print(l.strip())
