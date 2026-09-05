"""Emit literal Cold War weapon sound-alias labels retained in Mountain Defence's SABL bank.

Run: python contrib/mountain_defence_cw_sabl_aliases_20260904.py | target\\release\\confirm_list.exe - --game BLKOPSCW --sounds --label "Mountain Defence CW SABL aliases" --script contrib\\mountain_defence_cw_sabl_aliases_20260904.py
Reads: .tmp-steamcmd/steamapps/workshop/content/311210/2565091359/snd/*/*.sabl.
Writes: one deduplicated, lower-case literal wpn_t9_* alias per stdout line.
One-off: requires the anonymous Steam Workshop payload from this investigation.
Measured: 6 distinct exact labels from nine SABL banks before confirmation.
"""

from pathlib import Path
import re


ROOT = Path(__file__).resolve()
while ROOT.parent != ROOT and not (ROOT / "scripts" / "snapshot.py").is_file():
    ROOT = ROOT.parent

SABL = ROOT / ".tmp-steamcmd" / "steamapps" / "workshop" / "content" / "311210" / "2565091359" / "snd"
PATTERN = re.compile(rb"wpn_t9_[a-z0-9_]{2,}")

if not SABL.is_dir():
    raise SystemExit(f"Workshop source is absent: {SABL}")

names = set()
for path in SABL.rglob("*.sabl"):
    names.update(match.group().decode("ascii") for match in PATTERN.finditer(path.read_bytes()))

for name in sorted(names):
    print(name)
