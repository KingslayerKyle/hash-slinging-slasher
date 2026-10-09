"""Filter: re-spell sound-file candidates with `.` directory separators for MWII/MWIII.

MWII/MWIII hash sound files dotted (`iw9.dst.x_03.ln.75.48000.all`); every other asset type, and
BO6/BO7 sound files, keep `/`. Lines that end in a modern sound tail (`.<codec>.<n>.<rate>.<lang>`)
are printed dotted; every other line passes through unchanged (`--drop-other` drops them instead).

    python contrib/sound_tail_swap.py --game YAMYAMOK | python contrib/dotify.py | confirm_list - --game YAMYAMOK
"""
import re
import sys

TAIL = re.compile(r"\.[a-z]{1,4}\d*\.\d+\.\d{4,5}\.[a-z_]+$")
drop = "--drop-other" in sys.argv
out = sys.stdout
for line in sys.stdin:
    name = line.rstrip("\r\n")
    if "/" in name and TAIL.search(name.lower()):
        out.write(name.replace("/", ".") + "\n")
    elif not drop:
        out.write(line if line.endswith("\n") else line + "\n")
