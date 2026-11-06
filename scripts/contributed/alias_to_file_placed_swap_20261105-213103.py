"""ATF heads with plr<->npc / _plr<->_npc swaps on the alias basename.

Follow-up to alias_to_file_placed: that pass found cells where the file basename
is the alias. This asks whether the unnamed file is the same placement with the
player/npc polarity flipped -- a spelling ATF never emits.

    python contrib/alias_to_file_placed_swap.py MODWAR7
    bin/windows/confirm_plan plans/atfs_MODWAR7.txt --script contrib/alias_to_file_placed_swap.py
"""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent
while not (ROOT / "scripts" / "snapshot.py").is_file() and ROOT != ROOT.parent:
    ROOT = ROOT.parent

# Reuse ATF's stem builder by importing after pathing.
sys.path.insert(0, str(ROOT / "contrib"))
import alias_to_file_placed as atf  # noqa: E402


def polarity_swaps(name: str):
    out = set()
    for a, b in (("plr", "npc"), ("_plr", "_npc"), ("plr_", "npc_")):
        if a in name:
            out.add(name.replace(a, b, 1))
        if b in name:
            out.add(name.replace(b, a, 1))
    out.discard(name)
    return out


def main():
    game = sys.argv[1].upper()
    # Build the plain ATF stems first (writes atf_*.stems.txt).
    sys.argv = ["alias_to_file_placed.py", game]
    atf.main()
    stems_path = ROOT / "contrib" / "out" / f"atf_{game}.stems.txt"
    ends_path = ROOT / "contrib" / "out" / f"stt2_{game}.ends.txt"
    swapped = set()
    for line in stems_path.open(encoding="utf-8"):
        head = line.strip()
        if not head:
            continue
        if "/" in head:
            folder, _, base = head.rpartition("/")
        elif "." in head:
            folder, _, base = head.rpartition(".")
        else:
            continue
        for alt in polarity_swaps(base):
            sep = "." if game in atf.DOTTED else "/"
            swapped.add(f"{folder}{sep}{alt}" if folder else alt)
    out = ROOT / "contrib" / "out"
    (out / f"atfs_{game}.stems.txt").write_text("\n".join(sorted(swapped)) + "\n", encoding="utf-8")
    ends = sum(1 for _ in ends_path.open())
    (ROOT / "plans" / f"atfs_{game}.txt").write_text(
        f"label: ATF heads with plr/npc polarity swap, {game}\n"
        "describe: alias-as-basename placed heads from alias_to_file_placed, with plr<->npc "
        "flipped on the basename, x the target's tails (contrib/alias_to_file_placed_swap.py)\n"
        f"game: {game.lower()}\n"
        f"stem: @contrib/out/atfs_{game}.stems.txt\n"
        f"end: @contrib/out/stt2_{game}.ends.txt\n"
        "bare: yes\n",
        encoding="utf-8",
    )
    print(
        f"{game}: {len(swapped):,} swapped heads x {ends} = {len(swapped) * ends:,}",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
