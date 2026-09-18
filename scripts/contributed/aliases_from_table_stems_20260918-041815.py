"""Sound aliases from the stems of EVERY published sound file, not only this project's finds.

An alias is very often its file's stem with the take removed:
    vox\\scripted\\operators\\wood\\vox_wood_ss_cuav_use_02.rn75.pc.ru.snd  ->  vox_wood_ss_cuav_use
Method 182 derived these from recovered files. The published xsounds tables hold ~1.2 M file names
across both games (807 K under vox\\scripted alone), which that derivation never read. Emits each
stem as-is, minus a numeric take, and minus a trailing single letter variant.

    python contrib/aliases_from_table_stems.py | bin/windows/confirm_list.exe - --game BLKOPSCW
"""
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
seen = set()
paths = glob.glob(os.path.join(ROOT, "cod-name-db", "csv", "*xsounds*.csv"))
paths += glob.glob(os.path.join(ROOT, "cod-name-db", "csv", "*_sab.csv"))
paths += glob.glob(os.path.join(ROOT, "all_names", "*", "sound_asset.txt"))
for path in paths:
    with open(path, encoding="utf-8-sig", errors="replace") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            name = (line.split(",", 1)[1] if "," in line else line).lower().replace("\\", "/")
            stem = name.rsplit("/", 1)[-1].split(".", 1)[0]
            for s in (stem, re.sub(r"_\d+$", "", stem), re.sub(r"_[a-z]$", "", stem),
                      re.sub(r"_\d+_[a-z]$|_[a-z]_\d+$", "", stem)):
                if s and s not in seen:
                    seen.add(s)
                    sys.stdout.write(s + "\n")
print("aliases from table stems: %d candidates" % len(seen), file=sys.stderr)
