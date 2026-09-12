"""BO4 image and material mirror each other: a material mc/mtl_<core> has textures i_<core>_<chan>.
Measured on published names: 61% of materials have at least one matching image. This pass takes
every known material core and emits i_<core><tail> over the 60 real tails (_c/_n/_g/_o/_s/_m/_r/_e
plus the camo-specific ones like _dotd_exo2_c), and every known image core and emits it under the
12 real material prefixes (mc/mtl_, wc/t8_, mc/t8_, splm/mtl_, clt/mtl_, ei/gfx_, vd/t8_, ...).
Generators: C:/tmp/bo4_vox/mirror.py, mirror_apply.py."""
import os
here = os.path.dirname(os.path.abspath(__file__))
for l in open(os.path.join(here, "bo4_material_image_mirror.txt"), encoding="utf-8"):
    if l.strip(): print(l.strip())
