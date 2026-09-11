r"""BO4 MP/Blackout: files for the dialog aliases cracked from the mpdialog bundles
(bo4_mpdialog_bundle_aliases*.txt): en\vox\scripted\<mpl|wz>\<tok>\<alias>_<NN>.sn100.pc.snd
(the same alias + variant rule that named 12,846 specialist lines), plus the aliases themselves."""
import os
here = os.path.dirname(os.path.abspath(__file__))
B = chr(92)
al = set()
for fn in ("bo4_mpdialog_bundle_aliases.txt", "bo4_mpdialog_bundle_aliases2.txt"):
    al |= {l.strip() for l in open(os.path.join(here, fn), encoding="utf-8") if l.strip()}
for a in sorted(al):
    print(a)
    p = a.split("_")
    if len(p) < 3: continue
    tok = p[1]
    for mode in ("mpl", "wz", "zmb"):
        for v in range(0, 16):
            for t in (".sn100.pc.snd", ".ln100.pc.snd"):
                print(B.join(["en","vox","scripted",mode,tok,f"{a}_{v:02d}{t}"]))
                if v < 10: print(B.join(["en","vox","scripted",mode,tok,f"{a}_{v}{t}"]))
