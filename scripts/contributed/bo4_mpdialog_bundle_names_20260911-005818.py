"""BO4 sound_alias names cracked from scriptbundle/mpdialog_player/*.json (bo4-source): each
dialog key (boostwin, exertpainstun, characterselect...) maps to a hashed alias; the alias is
vox_<character token>_<key with underscores restored>, found by segmenting the key over the game
+ English vocabulary and verifying against the bundle's own hash (bo4_crack_mpdialog_bundles.py)."""
import os
here = os.path.dirname(os.path.abspath(__file__))
for l in open(os.path.join(here, "bo4_mpdialog_bundle_aliases.txt"), encoding="utf-8"):
    if l.strip(): print(l.strip())
