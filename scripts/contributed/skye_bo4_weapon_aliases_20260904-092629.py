"""Emit BO4-namespaced aliases, but never transformed Skye port file paths."""

import csv
import io
import re
import sys
import urllib.request


URL = (
    "https://raw.githubusercontent.com/FanaticSoftware/Skye-Weapon-Templates/"
    "master/share/raw/sound/aliases/skye_bo4_weapons.csv"
)
ALIAS = re.compile(r"wpn_t8_[a-z0-9_]+$")


def main() -> None:
    request = urllib.request.Request(URL, headers={"User-Agent": "hash-slinging-slasher"})
    with urllib.request.urlopen(request, timeout=60) as response:
        text = response.read().decode("utf-8-sig")
    names = {
        (row.get("Name") or "").strip().lower()
        for row in csv.DictReader(io.StringIO(text))
    }
    names = {name for name in names if ALIAS.fullmatch(name)}
    for name in sorted(names):
        print(name)
    print(f"[source] {len(names)} unique wpn_t8 aliases", file=sys.stderr)


if __name__ == "__main__":
    main()
