"""BO4: GPU gap fill aimed at the game's own enemy list. The w28447 dump's source/tables/aitype
holds 102 spawner entries (gegenees, crimson_nosferatu, gladiator_destroyer/marauder, tiger,
towers_boss/_2/_rider, weeping_angel, werewolf, blight_father, catalyst_*, brutus, avogadro,
nova_crawler, mannequin, skeleton_*, eddie/pablo/samantha). Each name was turned into image,
xmodel and material prefixes in the real BO4 shapes. A measured near-dead end: 14 names, because
those families are already largely named. Generator: C:/tmp/bo4_vox/boss_prefixes.py."""
import os
here = os.path.dirname(os.path.abspath(__file__))
for l in open(os.path.join(here, "bo4_boss_prefixes_gpu.txt"), encoding="utf-8"):
    if l.strip(): print(l.strip())
