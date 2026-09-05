"""Emit exact perk labels from ItsNatoriousB's public BOCW asset directory."""

from __future__ import annotations

import csv
import re
from pathlib import Path


source = Path("borrowed/bocw_asset_directory/_data/perks.csv")
native = re.compile(r"^p9_talent_[a-z0-9_]+$")
with source.open(newline="", encoding="utf-8") as handle:
    labels = {
        row[1].strip().lower()
        for row in csv.reader(handle)
        if len(row) == 3 and row[2].strip().lower() == "verified" and native.fullmatch(row[1].strip().lower())
    }

for label in sorted(labels):
    print(label)
