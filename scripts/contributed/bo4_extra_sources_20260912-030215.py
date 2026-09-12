"""BO4: the same hash-what-is-already-written idea widened to two more sources and to raw bytes.
Sources: the ate47/bo4-source decompiles, the hash databases shipped with acts, and the w28447
dump re-read as raw bytes (latin-1) so that strings inside binary files are seen too, which a
utf-8 read silently mangles. Every identifier-like run of characters, hashed as written,
lowercased and with slashes flipped, kept only on an exact unnamed-id match.
Generator: C:/tmp/bo4_vox/extra_sources.py."""
import os
here = os.path.dirname(os.path.abspath(__file__))
for l in open(os.path.join(here, "bo4_extra_sources.txt"), encoding="utf-8"):
    if l.strip(): print(l.strip())
