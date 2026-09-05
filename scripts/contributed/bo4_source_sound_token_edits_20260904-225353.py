"""Vary one underscore token in each external BO4 source sound basename.

Run with ``python contrib/bo4_source_sound_token_edits_20260905.py``; it reads the
existing source-path ledger and writes candidates to stdout.  This is reusable
for the current ledger, and its measured size is recorded with the confirmation.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LEDGER = ROOT / "contrib" / "bo4_source_sound_paths_20260829.candidates.txt"

def main():
    out = set()
    seeds = 0
    for raw in LEDGER.read_text(encoding="utf-8", errors="ignore").splitlines():
        name = raw.strip().lower()
        if not name:
            continue
        seeds += 1
        cut = max(name.rfind("/"), name.rfind("\\")) + 1
        head, base = name[:cut], name[cut:]
        dot = base.find(".")
        if dot <= 0:
            continue
        core, tail = base[:dot], base[dot:]
        parts = core.split("_")
        if len(parts) < 3:
            continue
        # Delete one interior token, and duplicate one interior token.  Both
        # transformations keep the external path and dotted SAB tail intact.
        for i in range(1, len(parts) - 1):
            out.add(head + "_".join(parts[:i] + parts[i + 1:]) + tail)
            out.add(head + "_".join(parts[:i] + [parts[i], parts[i]] + parts[i + 1:]) + tail)
    print(f"{seeds:,} source paths, {len(out):,} token-edit candidates", file=__import__("sys").stderr)
    print("\n".join(sorted(out)))

if __name__ == "__main__":
    main()
