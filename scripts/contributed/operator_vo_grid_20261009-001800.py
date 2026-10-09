"""Operator voice-line aliases as the grid they are: dx_op_<category>_<event>_<speaker>.

Modern operator lines are flat four-token aliases -- `dx_op_ping_pwsh_ryes`, `dx_op_bttl_aamo_rnin`
-- where a category and a four-letter event code are recorded by every operator, each with its own
four-letter speaker code. A run on MWIII returned 3,015 of them with each speaker code under ~137
events, which is a filled grid. This takes every (category, event) pair and every speaker code
attested in any known alias, from any game, and offers the whole product.

Spent by: the pair and speaker sets as they stand; re-run when a new speaker or event turns up.
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent


def aliases():
    sources = list((ROOT / "cod-name-db" / "csv").glob("fnv1a_soundbanks_aliases*.csv"))
    for folder in ("submissions", "findings", "all_names"):
        base = ROOT / folder
        if base.exists():
            sources.extend(base.rglob("sound_alias*.txt"))
    for path in sources:
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            key, sep, value = line.partition(",")
            name = (value if sep else key).strip().lower()
            if name.startswith("dx_op_"):
                yield name


def main():
    pairs, speakers = set(), set()
    for name in aliases():
        tokens = name.split("_")
        if len(tokens) == 5:
            pairs.add((tokens[2], tokens[3]))
            speakers.add(tokens[4])
    for category, event in sorted(pairs):
        for speaker in sorted(speakers):
            print(f"dx_op_{category}_{event}_{speaker}")
    print(f"{len(pairs):,} category/event pairs x {len(speakers):,} speakers = "
          f"{len(pairs) * len(speakers):,}", file=sys.stderr)


if __name__ == "__main__":
    main()
