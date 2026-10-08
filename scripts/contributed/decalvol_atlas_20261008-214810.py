"""`<image>~atlas_decalvolmask`: the one packed-image suffix that is a word rather than a content
hash (the decimal after `~` on every other packed image is a hash of the pixels/settings --
`white`, `white&white` and `white&white&white` all carry the same number). Every known image name
without a `~` of its own, suffixed with it.

    python contrib/decalvol_atlas.py | confirm_list - --game BLACKOP6 --script contrib/decalvol_atlas.py
"""
import sys
sys.path.insert(0, __file__.rsplit("contrib", 1)[0] + "contrib")
from material_dir_swap import rows

seen = set()
for name in rows("fnv1a_ximages*.csv", ("image",)):
    if name and "~" not in name and name not in seen:
        seen.add(name)
        sys.stdout.write(name + "~atlas_decalvolmask\n")
