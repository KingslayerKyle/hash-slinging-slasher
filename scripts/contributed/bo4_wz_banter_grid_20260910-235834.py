r"""BO4 Blackout character banter files. Known shape (from the alias rule, e.g.
en\vox\scripted\wz\stuh\vox_stuh_0_banter_stuh_tedd_0_00.sn100.pc.snd):
    en\vox\scripted\wz\<spk>\vox_<spk>_<idx>_banter_<c1>_<c2>_<line>_<NN>.sn100.pc.snd
spk = the speaking character (one of c1/c2), ~60 Blackout speaker tokens already named."""
B = chr(92)
spk = ["prop","batt","ruin","fire","zero","spec","reap","noma","outr","sera","tedd","mist","stuh","ptak","russ","marl","matt","wood","alex","huds","pnik","pdem","cras","engi","rezn","swat","pric","reco","bom1","bom2","bom3","bom4","bop1","bop2","bop3","bop4","bop5","bof1","bof2","bof3","bof4","weav","yuri","udem","utak","uric","unik","mene","sara","blac","ctre","cpri","zmm1","zmf1","serg","ward","numb","ajax","torq"]
for a in spk:
    for b in spk:
        if a == b: continue
        c1, c2 = sorted([a, b])
        for s in (a, b):
            for idx in range(0, 8):
                for line in range(0, 6):
                    for nn in range(0, 4):
                        for t in (".sn100.pc.snd", ".ln100.pc.snd"):
                            print(B.join(["en","vox","scripted","wz",s,f"vox_{s}_{idx}_banter_{c1}_{c2}_{line}_{nn:02d}{t}"]))
