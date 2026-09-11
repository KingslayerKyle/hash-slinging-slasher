"""BO4 sound_alias / weapon names cracked from tables/weapon/<zone>/<weapon>.json (bo4-source):
each weapon table carries ~30 hashed sound-alias fields (firesound, firesounddistant, sound240 ...)
plus baseWeapon/sharedWeaponSounds names. 3-token MITM with prefixes 'wpn_' and '' over the
sound vocabulary + the 708 weapon-name tokens, verified against the table's own hash."""
import os
here = os.path.dirname(os.path.abspath(__file__))
for l in open(os.path.join(here, "bo4_weapon_table_aliases.txt"), encoding="utf-8"):
    if l.strip(): print(l.strip())
