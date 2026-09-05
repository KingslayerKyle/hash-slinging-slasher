"""Emit original-looking T9 weapon aliases preserved by Skye's public template.

The CSV's FileSpec column deliberately points at ported ``skye_ports`` files;
only its Name aliases are source candidates.  Keep the T9-specific namespace
so BO3/port-framework helper rows cannot leak into the live-game check.
"""

import csv
import io
import re
import sys
import urllib.request


URL = (
    "https://raw.githubusercontent.com/FanaticSoftware/Skye-Weapon-Templates/"
    "main/share/raw/sound/aliases/skye_bocw_weapons.csv"
)
ALIAS = re.compile(r"wpn_t9_[a-z0-9_]+$")


def main() -> None:
    request = urllib.request.Request(URL, headers={"User-Agent": "hash-slinging-slasher"})
    with urllib.request.urlopen(request, timeout=60) as response:
        text = response.read().decode("utf-8-sig")
    rows = csv.DictReader(io.StringIO(text))
    names = set()
    for row in rows:
        name = (row.get("Name") or "").strip().lower()
        if ALIAS.fullmatch(name):
            names.add(name)
    for name in sorted(names):
        print(name)
    print(f"[source] {len(names)} unique wpn_t9 aliases", file=sys.stderr)


if __name__ == "__main__":
    main()
