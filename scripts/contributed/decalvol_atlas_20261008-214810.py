"""`<image>~atlas_decalvolmask`: the one packed-image suffix that is a word rather than a content
hash (the decimal after `~` on every other packed image is a hash of the pixels/settings --
`white`, `white&white` and `white&white&white` all carry the same number). Every known image name
without a `~` of its own, suffixed with it.

    python contrib/decalvol_atlas.py | confirm_list - --game BLACKOP6 --script contrib/decalvol_atlas.py
"""
from pathlib import Path
import sys
import importlib.util

ROOT = Path(__file__).resolve().parent
while not (ROOT / "scripts" / "snapshot.py").is_file() and ROOT != ROOT.parent:
    ROOT = ROOT.parent


def _companion(name, filename):
    """Load the reviewed, versioned companion shipped with this repository."""
    spec = importlib.util.spec_from_file_location(
        name, ROOT / "scripts" / "contributed" / filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

_materials = _companion("material_dir_swap", "material_dir_swap_20261008-205512.py")
rows = _materials.rows


seen = set()
for name in rows("fnv1a_ximages*.csv", ("image",)):
    if name and "~" not in name and name not in seen:
        seen.add(name)
        sys.stdout.write(name + "~atlas_decalvolmask\n")
