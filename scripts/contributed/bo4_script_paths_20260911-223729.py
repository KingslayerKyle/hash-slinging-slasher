"""BO4 scriptparsetree, luafile, ddl, stringtable, structuredtable and constbaseline names, taken
from the file tree of the public w28447 dump. Those pockets are not in the default search set, so
nothing here had ever been aimed at them, yet their names are simply the paths the build ships:
scripts/zm/zm_orange_audiologs.gsc, ui/uieditor/widgets/..., gamedata/tables/....
Every path in the dump (with and without extension, forward and backslash spelling, lowercased)
was hashed and kept only on an exact unnamed-id match. Generator: C:/tmp/bo4_vox/script_paths.py."""
import os
here = os.path.dirname(os.path.abspath(__file__))
for l in open(os.path.join(here, "bo4_script_paths.txt"), encoding="utf-8"):
    if l.strip(): print(l.strip())
