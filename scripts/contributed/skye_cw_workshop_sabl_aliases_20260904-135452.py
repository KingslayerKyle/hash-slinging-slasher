"""Emit literal Cold War weapon sound-alias labels retained in Skye's public Workshop pack.

Run: python contrib/skye_cw_workshop_sabl_aliases_20260904.py | target\\release\\confirm_list.exe - --game BLKOPSCW --sounds --label "Skye CW Steam Workshop SABL aliases" --script contrib\\skye_cw_workshop_sabl_aliases_20260904.py
Reads: .tmp-steamcmd/steamapps/workshop/content/311210/2753027294/snd/*/*.sabl.
Writes: one deduplicated, lower-case literal wpn_t9_* alias per stdout line.
One-off: requires the public anonymous Steam Workshop payload from this investigation.
Measured: 1,836 distinct exact labels from nine SABL banks before confirmation.
"""
from pathlib import Path
import re

root = Path(__file__).resolve()
while root.parent != root and not (root / "scripts" / "snapshot.py").is_file():
    root = root.parent
sabl = root / ".tmp-steamcmd" / "steamapps" / "workshop" / "content" / "311210" / "2753027294" / "snd"
if not sabl.is_dir():
    raise SystemExit(f"Workshop source is absent: {sabl}")
pat = re.compile(rb"wpn_t9_[a-z0-9_]{2,}")
names = set()
for path in sabl.rglob("*.sabl"):
    names.update(m.group().decode("ascii") for m in pat.finditer(path.read_bytes()))
for name in sorted(names):
    print(name)
