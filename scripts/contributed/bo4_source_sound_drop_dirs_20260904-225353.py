"""Drop one interior directory component from each external BO4 SAB path.

The source ledger preserves complete paths.  This bounded probe tests whether
some consumers refer to the same recording through a shallower path, while
keeping the observed basename and dotted tail intact.
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "contrib" / "bo4_source_sound_paths_20260829.candidates.txt"

def main():
    out = set()
    seeds = 0
    for raw in LEDGER.read_text(encoding="utf-8", errors="ignore").splitlines():
        name = raw.strip().lower().replace("/", "\\")
        if not name:
            continue
        seeds += 1
        bits = name.split("\\")
        # Preserve the top-level semantic head and leaf; remove only an
        # interior directory, never the recording basename.
        if len(bits) < 4:
            continue
        for i in range(1, len(bits) - 1):
            out.add("\\".join(bits[:i] + bits[i + 1:]))
    print(f"{seeds:,} source paths, {len(out):,} dropped-directory candidates", file=sys.stderr)
    print("\n".join(sorted(out)))

if __name__ == "__main__":
    main()
