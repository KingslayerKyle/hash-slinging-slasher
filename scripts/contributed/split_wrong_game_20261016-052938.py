"""Move names that do not hash into a game's own capture out of that game's aggregate findings.
(repair helper, not a method)

Rule 3: never write one game's names into another's files. A name whose hash under <GAME>'s policy
is not an id of that pool in <GAME>'s snapshot is not a <GAME> result. Kept lines stay in
findings/<game>/<pool>.txt; removed lines are appended to <quarantine>/<game>/<pool>.wrong_game.txt.
Run only after the originals are copied aside.

    PYTHONPATH=scripts python contrib/split_wrong_game.py <quarantine dir> <GAME>...
"""
from pathlib import Path
import sys

import snapshot

M = snapshot.ID_MASK
check_only = sys.argv[1] == "--check"     # report only; exit 1 if any game holds a wrong name
quarantine = Path(sys.argv[1])
found_wrong = 0
for game in sys.argv[2:]:
    pools = snapshot.read(f"snapshots/{game.lower()}.ids").by_pool()
    for f in sorted(Path(f"findings/{game.lower()}").glob("*.txt")):
        ids = {i & M for i in pools.get(f.stem, [])}
        keep, wrong = [], []
        for line in f.read_text(encoding="utf-8", errors="replace").splitlines():
            _, _, name = line.partition(",")
            # BO4 SAB sound names keep their backslashes and hash unfolded (CLAUDE.md section 6)
            if name and snapshot.fnv1a(name, game, f.stem) & M not in ids \
                    and snapshot.fnv1a_nofold(name) & M not in ids:
                wrong.append(line)
            else:
                keep.append(line)
        found_wrong += len(wrong)
        if check_only:
            if wrong:
                print(game, f.stem, "WRONG-GAME names:", len(wrong))
            continue
        if wrong:
            out = quarantine / game.lower()
            out.mkdir(parents=True, exist_ok=True)
            with (out / f"{f.stem}.wrong_game.txt").open("a", encoding="utf-8") as q:
                q.write("\n".join(wrong) + "\n")
            f.write_text("\n".join(keep) + ("\n" if keep else ""), encoding="utf-8")
        print(game, f.stem, "kept", len(keep), "moved", len(wrong))
if check_only:
    print("wrong-game names in aggregates:", found_wrong)
    sys.exit(1 if found_wrong else 0)
