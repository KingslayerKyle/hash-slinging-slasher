"""BO4 three-way mirror between xmodel, material and image: the core of a model name
(p8_zm_gla_temple_column_01_inlay_skull) reappears as mc/mtl_<core> and i_<core>_<channel>.
Measured on published names the relation is weaker than the material/image pair alone: a model
core is also a material core in 13.3% of cases and an image core in 2.5%. The union of all
197k cores was tried in every direction (model suffixes, 12 material prefixes, 60 image tails).
Generator: C:/tmp/bo4_vox/mirror3.py."""
import os
here = os.path.dirname(os.path.abspath(__file__))
for l in open(os.path.join(here, "bo4_mirror3.txt"), encoding="utf-8"):
    if l.strip(): print(l.strip())
