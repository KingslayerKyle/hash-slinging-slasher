"""BO4 sound_asset: exact-id probe of the alias-linked files whose path is NOT spelled like their
alias, with a mined abbreviation map applied (impact->imp, zombie->zmb, ambient->amb, loop->lp...)
plus generic short forms (first 3-4 letters, consonant skeleton). Dirs: every known BO4 sound
directory. Generators: C:/tmp/bo4_vox/mine_abbrev.py, gen_abbrev_bases.py, probe_dirs2.cpp."""
import os
here = os.path.dirname(os.path.abspath(__file__))
for l in open(os.path.join(here, "bo4_abbrev_probe.txt"), encoding="utf-8"):
    if l.strip(): print(l.strip())
