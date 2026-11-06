"""ATF placed heads with the alias basename's last underscore token stripped.

    python contrib/alias_to_file_placed_strip.py MODWAR7
    bin/windows/confirm_plan plans/atfstrip_MODWAR7.txt --script contrib/alias_to_file_placed_strip.py
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
while not (ROOT / "scripts" / "snapshot.py").is_file() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
sys.path.insert(0, str(ROOT / "contrib"))
import alias_to_file_placed as atf  # noqa: E402


def main():
    game = sys.argv[1].upper()
    sys.argv = ["alias_to_file_placed.py", game]
    atf.main()
    stems_path = ROOT / "contrib" / "out" / f"atf_{game}.stems.txt"
    ends_path = ROOT / "contrib" / "out" / f"stt2_{game}.ends.txt"
    stripped = set()
    for line in stems_path.open(encoding="utf-8"):
        head = line.strip()
        if not head:
            continue
        sep = "/" if "/" in head else "."
        folder, _, base = head.rpartition(sep)
        parts = base.split("_")
        if len(parts) < 3:
            continue
        short = "_".join(parts[:-1])
        stripped.add(f"{folder}{sep}{short}" if folder else short)
    out = ROOT / "contrib" / "out"
    (out / f"atfstrip_{game}.stems.txt").write_text(
        "\n".join(sorted(stripped)) + "\n", encoding="utf-8"
    )
    ends = sum(1 for _ in ends_path.open())
    (ROOT / "plans" / f"atfstrip_{game}.txt").write_text(
        f"label: ATF heads with last alias token stripped, {game}\n"
        "describe: alias-as-basename placed heads minus the final underscore token, "
        "x the target's tails (contrib/alias_to_file_placed_strip.py)\n"
        f"game: {game.lower()}\n"
        f"stem: @contrib/out/atfstrip_{game}.stems.txt\n"
        f"end: @contrib/out/stt2_{game}.ends.txt\n"
        "bare: yes\n",
        encoding="utf-8",
    )
    print(
        f"{game}: {len(stripped):,} stripped heads x {ends} = {len(stripped) * ends:,}",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
