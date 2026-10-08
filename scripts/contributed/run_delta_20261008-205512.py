"""How many ids each run folder of a game added that no earlier run folder of that game held."""
from pathlib import Path
import sys
game = sys.argv[1].lower()
seen = set()
for d in sorted(Path("findings", game).glob("run_*")):
    ids = set()
    for f in d.glob("*.txt"):
        ids.update(l.split(",", 1)[0] for l in f.open(encoding="utf-8") if "," in l)
    new = ids - seen
    seen |= ids
    note = d / "notes.md"
    m = next((l[10:60] for l in note.open(encoding="utf-8") if l.startswith("- method")), "?") if note.exists() else "(unfinished)"
    if len(sys.argv) < 3 or d.name >= sys.argv[2]:
        print(f"{d.name:32} {len(new):6} {m.strip()}")
print("distinct ids across all runs:", len(seen))
