"""Emit literal BO4 weapon sound-alias labels retained in Skye's public Workshop pack.

Run: python contrib/skye_bo4_workshop_sabl_aliases_20260904.py | target\\release\\confirm_list.exe - --game BLKOPS04 --sounds --no-fold --label "Skye BO4 Steam Workshop SABL aliases" --script contrib\\skye_bo4_workshop_sabl_aliases_20260904.py
Reads: .tmp-steamcmd/steamapps/workshop/content/311210/1845221515/snd/*/*.sabl.
Writes: one deduplicated, lower-case literal wpn_t8_* alias per stdout line.
One-off: requires the public anonymous Steam Workshop payload downloaded by this investigation.
Measured: 307 distinct exact labels from nine SABL banks before confirmation.
"""

from pathlib import Path
import re


ROOT = Path(__file__).resolve()
while ROOT.parent != ROOT and not (ROOT / "scripts" / "snapshot.py").is_file():
    ROOT = ROOT.parent

SABL = ROOT / ".tmp-steamcmd" / "steamapps" / "workshop" / "content" / "311210" / "1845221515" / "snd"
PATTERN = re.compile(rb"wpn_t8_[a-z0-9_]{2,}")

if not SABL.is_dir():
    raise SystemExit(f"Workshop source is absent: {SABL}")

names = set()
for path in SABL.rglob("*.sabl"):
    names.update(match.group().decode("ascii") for match in PATTERN.finditer(path.read_bytes()))

for name in sorted(names):
    print(name)
