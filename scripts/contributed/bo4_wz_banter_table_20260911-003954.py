r"""BO4 Blackout banter, from the hashed stringtable hashed/stringtable/file_5ec1825aeab754a2.csv
(bo4-source): rows are (#char1, #char2, #hash alias1, #hash alias2). With the speaker tokens
already known (seraph=sera ... mason=alex, primis_dempsey=pdem, ofc_dempsey=udem ...) the alias is
vox_<spk>_<idx>_banter_<c1>_<c2>_<line> (c1<c2), verified against the row's own hash; the file is
en\vox\scripted\wz\<spk>\<alias>_<NN>.sn100.pc.snd. 670 aliases + 669 files from 537 rows."""
import os
here = os.path.dirname(os.path.abspath(__file__))
for fn in ("bo4_wz_banter_table_aliases.txt", "bo4_wz_banter_table_files.txt"):
    for l in open(os.path.join(here, fn), encoding="utf-8"):
        if l.strip(): print(l.strip())
