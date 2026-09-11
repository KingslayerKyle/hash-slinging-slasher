r"""BO4 Blackout VO: every named Blackout speaker x every Blackout event ever seen on any speaker
(bo4_wz_events.txt, from the named files) x variants: en\vox\scripted\wz\<spk>\vox_<spk>_<event>_<NN>.sn100.pc.snd"""
import os
here = os.path.dirname(os.path.abspath(__file__))
B = chr(92)
spk = [l.strip() for l in open(os.path.join(here, "bo4_wz_speakers.txt"), encoding="utf-8") if l.strip()]
ev = [l.strip() for l in open(os.path.join(here, "bo4_wz_events.txt"), encoding="utf-8") if l.strip()]
for s in spk:
    for e in ev:
        for v in range(0, 16):
            for t in (".sn100.pc.snd", ".ln100.pc.snd"):
                print(B.join(["en","vox","scripted","wz",s,f"vox_{s}_{e}_{v:02d}{t}"]))
                if v < 10: print(B.join(["en","vox","scripted","wz",s,f"vox_{s}_{e}_{v}{t}"]))
