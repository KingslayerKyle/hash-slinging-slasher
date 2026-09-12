"""BO4: names read straight out of the retail install's raw CASC packages
(Data/data/data.000..174, 179.8 GB). Every identifier-like run of bytes in the packages was
hashed as written, lowercased, and with forward slashes flipped to backslashes, and kept only on
an exact unnamed-id match. Sequential single-threaded reading matters: the packages sit on a
mechanical disk, and a parallel scan collapses to seek thrashing (measured: 12 threads made no
progress in minutes, one thread sustained 83 MB/s and finished 179.8 GB in ~35 minutes).
Generator: C:/tmp/bo4_vox/scan_game.cpp."""
import os
here = os.path.dirname(os.path.abspath(__file__))
for l in open(os.path.join(here, "bo4_raw_game_scan.txt"), encoding="utf-8"):
    if l.strip(): print(l.strip())
