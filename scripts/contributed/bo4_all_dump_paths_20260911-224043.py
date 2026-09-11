"""BO4, every pocket: the names are the dump's own file tree. For each file in the public w28447
dump, every suffix of its path was tried (full relative path down to the bare stem), with and
without extension, in forward and backslash spelling, lowercased, and kept only on an exact
unnamed-id match. That reaches the pockets no search targets: scriptbundle, scriptparsetree,
luafile, ddl, aitype, character, weapon tunables, gametype tables, storage files, spray/gesture
lists and more. Generator: C:/tmp/bo4_vox/all_paths.py."""
import os
here = os.path.dirname(os.path.abspath(__file__))
for l in open(os.path.join(here, "bo4_all_dump_paths.txt"), encoding="utf-8"):
    if l.strip(): print(l.strip())
