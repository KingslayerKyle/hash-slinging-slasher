"""BO4 sound_alias (pocket 171) names for zombies dialogue, built exactly as zm_audio.gsc /
zm_vo.gsc build them at runtime:
    <suffix>_plr_<n>_<v>                 suffix = col 3 of zm_<map>_vox.csv (cracked list) or a
                                         hashed script argument, n = character index 1..20
    vox_<idx>_banter_<chr1>_<chr2>_plr_<n>_<v>   conversations (zm_vo.gsc function_2b7b1675)
The suffixes are the same oracle-verified strings that name the files; the alias is the other
half of the same construction."""
import os
here = os.path.dirname(os.path.abspath(__file__))
suf = {l.split(",")[1] for l in open(os.path.join(here, "bo4_zm_vox_csv_suffixes_cracked.txt"), encoding="utf-8") if "," in l}
suf |= {l.strip() for l in open(os.path.join(here, "bo4_zm_script_vo_suffixes_cracked.txt"), encoding="utf-8") if l.strip()}
for s in sorted(suf):
    for n in range(0, 21):
        for v in range(0, 16):
            print(f"{s}_plr_{n}_{v}")
        print(f"{s}_plr_{n}")
chars = ["brun","dieg","scar","shaw","demp","niko","rich","take","udem","unik","uric","utak","mist","marl","russ","stuh","brig","butl","guns","psyc"]
for idx in range(0, 31):
    for c1 in chars:
        for c2 in chars:
            if c1 == c2: continue
            for n in range(1, 21):
                for v in range(0, 8):
                    print(f"vox_{idx}_banter_{c1}_{c2}_plr_{n}_{v}")
                    if idx == 0: print(f"vox_banter_{c1}_{c2}_plr_{n}_{v}")
