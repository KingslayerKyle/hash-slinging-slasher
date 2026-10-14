"""Model-name plans (contrib/model_log_stems.py) over the model names that are NEW since the last run.

Modern xmodels are not searched or submitted here, but their names seed the materials and images
built for them. The model log the user supplied held 36k of BO7's 206k model names. Token edits of
those names (substitute / insert / delete one token, vocabulary from the known model, material and
image names) checked against the BO7 xmodel ids -- 63-bit ids, so a hit is a real model name --
roughly doubled that (contrib/model_seed_expand.cs, run as a local tool; the model names
themselves are never filed). This writes a `Model,<name>` log of all of them, runs
model_log_stems.py on it, then cuts every stem-side list down to the stems the previous run
(contrib/modellog_stems.prev.txt) did not have, so the plans pay only for new ground.

    python contrib/model_seed_delta.py <verified model names file>...
    confirm_plan contrib/modellog_material.plan.txt --game BLACKOP7     (and _image, _wrap_*, _head_*, _insert_*)
"""
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent
CONTRIB = ROOT / "contrib"
prev_file = CONTRIB / "modellog_stems.prev.txt"
cur_file = CONTRIB / "modellog_stems.txt"
if not prev_file.is_file():
    prev_file.write_text(cur_file.read_text(encoding="utf-8"), encoding="utf-8")
prev = set(prev_file.read_text(encoding="utf-8").split())

log = ROOT / "state" / "modelhash" / "combined_models.log"
names = set()
src = ROOT.parent / "assets.log"
if src.is_file():
    for line in open(src, encoding="utf-8", errors="replace"):
        if line.startswith("Model,"):
            names.add(line.strip()[6:].lower())
for p in sys.argv[1:]:
    for line in open(p, encoding="utf-8", errors="replace"):
        if line.strip():
            names.add(line.strip().lower())
log.write_text("".join(f"Model,{n}\n" for n in sorted(names)), encoding="utf-8")
subprocess.run([sys.executable, str(CONTRIB / "model_log_stems.py"), str(log)], check=True)

stems = set(cur_file.read_text(encoding="utf-8").split())
new = sorted(stems - prev)
cur_file.write_text("\n".join(new) + "\n", encoding="utf-8")
rests = set()
for stem in new:
    parts = stem.split("_")
    for k in (1, 2):
        if len(parts) > k:
            rests.add("_" + "_".join(parts[k:]))
old_rests = set()
for stem in prev:
    parts = stem.split("_")
    for k in (1, 2):
        if len(parts) > k:
            old_rests.add("_" + "_".join(parts[k:]))
(CONTRIB / "modellog_rests.txt").write_text("\n".join(sorted(rests - old_rests)) + "\n", encoding="utf-8")
(CONTRIB / "modellog_whole.txt").write_text("\n".join("_" + s for s in new) + "\n", encoding="utf-8")
print(f"{len(names)} model names, {len(stems)} stems, {len(new)} new stems, {len(rests - old_rests)} new rests")
# The next run's baseline is everything known now.
prev_file.write_text("\n".join(sorted(stems | prev)) + "\n", encoding="utf-8")
