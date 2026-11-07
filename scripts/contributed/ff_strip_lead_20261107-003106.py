"""Harvested fast-file strings with their stray leading bytes removed.

The zones store a string after a length or flag byte, and when that byte is printable the scan glues it
to the name: `qcompass_map_mp_rex_tumen_grid_expanded`, `2ui_rex_icon_map_dmz_repair_gear`. Those hash to
nothing, so a raw harvest silently loses them. Prints each string with one and two leading bytes cut.

    python contrib/ff_strip_lead.py logs/mw7_ff_all.txt | confirm_list - --game MODWAR7
"""
import sys

seen = set()
for line in open(sys.argv[1], encoding='utf-8', errors='replace'):
    name = line.strip()
    for cut in (1, 2):
        value = name[cut:]
        if len(value) >= 6 and value not in seen:
            seen.add(value)
            print(value)
