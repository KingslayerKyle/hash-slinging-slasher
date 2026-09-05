"""Substitute basename tokens using alternatives observed in the same BO4 SAB directory.

Run with ``python contrib/bo4_source_sound_context_token_subs_20260905.py``; it reads
the external source-path ledger and prints bounded unfolded candidates.  It is reusable
for future ledger refreshes and writes only candidate names to stdout.
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "contrib" / "bo4_source_sound_paths_20260829.candidates.txt"

def main():
    by_dir = {}
    rows = []
    for raw in LEDGER.read_text(encoding="utf-8", errors="ignore").splitlines():
        name = raw.strip().lower().replace("/", "\\")
        if not name:
            continue
        cut = name.rfind("\\")
        if cut < 0:
            continue
        base = name[cut + 1:]
        dot = base.find(".")
        if dot <= 0:
            continue
        core, tail = base[:dot], base[dot:]
        parts = core.split("_")
        if len(parts) < 3:
            continue
        directory = name[:cut]
        rows.append((directory, parts, tail))
        by_dir.setdefault(directory, set()).update(parts[1:-1])
    out = set()
    for directory, parts, tail in rows:
        alternatives = by_dir[directory]
        for i in range(1, len(parts) - 1):
            for token in alternatives:
                if token != parts[i]:
                    out.add(directory + "\\" + "_".join(parts[:i] + [token] + parts[i + 1:]) + tail)
    print(f"{len(rows):,} source paths, {len(out):,} contextual-token candidates", file=sys.stderr)
    print("\n".join(sorted(out)))

if __name__ == "__main__":
    main()
