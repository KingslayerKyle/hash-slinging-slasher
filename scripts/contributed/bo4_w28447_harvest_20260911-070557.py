"""Names harvested from the public BO4 dump github.com/w28447/-8 (a second acts dump of Black Ops 4,
Aug 2026, with far more hashes resolved than ate47/bo4-source): every identifier-like string in
its 23,423 files (tables, scriptbundles, scripts, sound tables incl. alias->assetId links), hashed
as-is / lowercase / with '/'->'\', kept when it lands on a BO4 pool id (bo4_harvest_w28447.py).
Plus character xmodels cracked by MITM with the xmodel vocabulary (c_t8_zmb_ora_zombie_electric_*)."""
import os
here = os.path.dirname(os.path.abspath(__file__))
for l in open(os.path.join(here, "bo4_w28447_harvest_names.txt"), encoding="utf-8"):
    if l.strip(): print(l.strip())
