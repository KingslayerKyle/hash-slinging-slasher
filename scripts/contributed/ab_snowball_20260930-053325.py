"""The all-boundary snowball: rebuild the core lists from today's corpus and search only what is new.

Method 25 (all-boundary cores x uncarried endings) and its slotswap generalisation both read
`contrib/ab_cores.txt`, which is built from every name known *when it was built*. Every name this
project confirms afterwards carries cores nobody has crossed with the endings yet -- and on
2026-09-29 the 1,160 cores that one week of finds added returned 200 names from 0.35B candidates,
one per 1.7M, against one per 40B for the slotswap pass that produced most of those finds. Those
cores are the most productive ground in the project because each one is a fragment of a name
proven real a few days ago.

So this does, per round and per half (visual, then sound):

    1. rebuild ab_cores/ab_ends with the method-25 generator (unchanged, same --top)
    2. search   new cores x all endings    and    all cores x new endings
    3. rebuild the slotswap cores from the fresh base, search the new ones x all endings
    4. derive_closure on both games
    5. submit

"New" is against a ledger (`contrib/ab_snowball_seen_<half>_{cores,ends,slotswap}.txt`), seeded on
the first run from whatever lists already exist on disk, so nothing already searched is searched
again. A round that confirms nothing ends the run: the corpus is then closed under this method until
something else confirms a name.

    python contrib/ab_snowball.py                  visual and sound, both games, until a round is empty
    python contrib/ab_snowball.py --rounds 1       one round
    python contrib/ab_snowball.py --dry-run        report the deltas and stop
    python contrib/ab_snowball.py --no-submit      leave submitting to you
"""
from pathlib import Path
import argparse
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
while not (ROOT / "scripts" / "snapshot.py").is_file() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
CONTRIB = ROOT / "contrib"
PLANS = ROOT / "plans"
LOGS = ROOT / "logs" / "snowball"
GAMES = ("BLKOPSCW", "BLKOPS04")
TOP = {"": 300000, "sound_": 100000}
EXE = ".exe" if sys.platform == "win32" else ""


def tool(name):
    folder = {"win32": "windows", "darwin": "macos"}.get(sys.platform, "linux")
    return str(ROOT / "bin" / folder / (name + EXE))


def lines(path):
    if not path.exists():
        return set()
    with open(path, "rb") as handle:
        return {line.strip() for line in handle if line.strip()}


def write(path, items):
    with open(path, "wb") as handle:
        handle.write(b"\n".join(sorted(items)) + b"\n")


def remember(path, items):
    with open(path, "ab") as handle:
        for item in sorted(items):
            handle.write(item + b"\n")


def run_plan(label, stems, ends, fold, tag, dry_run):
    """Cross `stems` with `ends` on both games; return names added."""
    if not stems or not ends:
        return 0
    stem_file = CONTRIB / f"ab_snowball_{tag}_stems.txt"
    end_file = CONTRIB / f"ab_snowball_{tag}_ends.txt"
    write(stem_file, stems)
    write(end_file, ends)
    plan = PLANS / f"ab_snowball_{tag}.txt"
    plan.write_text(
        f"label: {label}\n"
        f"describe: ab_snowball.py -- {len(stems)} stems x {len(ends)} endings, only ground not "
        f"searched before\n"
        f"stem: @contrib/{stem_file.name}\nend: @contrib/{end_file.name}\n"
        f"bare: yes\nfold: {'yes' if fold else 'no'}\n",
        encoding="utf-8",
    )
    print(f"  {label}: {len(stems):,} x {len(ends):,} = {len(stems) * len(ends) / 1e9:.2f}B")
    if dry_run:
        return 0
    gained = 0
    for game in GAMES:
        log = LOGS / f"{tag}_{game}.log"
        with open(log, "w", encoding="utf-8") as out:
            subprocess.run([tool("confirm_plan"), str(plan), "--game", game, "--anyway"],
                           stdout=out, stderr=subprocess.STDOUT, cwd=ROOT)
        found = re.findall(r"^this run added (\d+)", log.read_text(encoding="utf-8"), re.M)
        added = int(found[-1]) if found else 0
        print(f"    {game}: +{added}")
        gained += added
    return gained


def half(stem, round_number, dry_run):
    """One round of one half ('' visual, 'sound_' sound). Returns names added."""
    name = "sound" if stem else "visual"
    seen_cores = CONTRIB / f"ab_snowball_seen_{name}_cores.txt"
    seen_ends = CONTRIB / f"ab_snowball_seen_{name}_ends.txt"
    seen_swap = CONTRIB / f"ab_snowball_seen_{name}_slotswap.txt"
    cores_path = CONTRIB / f"ab_{stem}cores.txt"
    ends_path = CONTRIB / f"ab_{stem}ends.txt"
    swap_path = CONTRIB / f"slotswap_{stem}cores_new.txt"

    # First run: everything already on disk counts as searched.
    for seen, current in ((seen_cores, cores_path), (seen_ends, ends_path), (seen_swap, swap_path)):
        if not seen.exists():
            write(seen, lines(current))

    generator = [sys.executable, str(CONTRIB / "uncarried_endings_allboundary.py"),
                 "--top", str(TOP[stem])] + (["--sound-pass"] if stem else [])
    subprocess.run(generator, cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                   check=True)
    cores, ends = lines(cores_path), lines(ends_path)
    new_cores = cores - lines(seen_cores)
    new_ends = ends - lines(seen_ends)
    print(f" {name}: {len(new_cores):,} new cores, {len(new_ends):,} new endings")

    gained = run_plan(f"ab snowball r{round_number} {name}: new cores x all endings",
                      new_cores, ends, True, f"r{round_number}_{name}_newcores", dry_run)
    gained += run_plan(f"ab snowball r{round_number} {name}: all cores x new endings",
                       cores - new_cores, new_ends, True, f"r{round_number}_{name}_newends",
                       dry_run)

    swapper = [sys.executable, str(CONTRIB / "slotswap_cores.py")] + (
        ["--sound-pass"] if stem else [])
    subprocess.run(swapper, cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                   check=True)
    swaps = lines(swap_path)
    new_swaps = swaps - lines(seen_swap)
    print(f" {name}: {len(new_swaps):,} new slotswap cores")
    gained += run_plan(f"ab snowball r{round_number} {name}: new slotswap cores x all endings",
                       new_swaps, ends, True, f"r{round_number}_{name}_slotswap", dry_run)
    gained += run_plan(f"ab snowball r{round_number} {name}: old slotswap cores x new endings",
                       swaps - new_swaps, new_ends, True, f"r{round_number}_{name}_swapends",
                       dry_run)

    # The endings half of the same idea: every boundary tail of a confirmed name that neither
    # ending list carries, crossed with all cores. On 2026-09-30 the 7,409 such tails of the week's
    # 1,411 finds returned 27 names from 28B candidates.
    seen_tails = CONTRIB / f"ab_snowball_seen_{name}_tails.txt"
    tails = confirmed_tails() - ends - lines(ROOT / "data" / f"{stem}suffixes.txt")
    if not seen_tails.exists():
        write(seen_tails, tails)
    new_tails = tails - lines(seen_tails)
    print(f" {name}: {len(new_tails):,} new tails of confirmed names")
    gained += run_plan(f"ab snowball r{round_number} {name}: all cores x new name tails",
                       cores, new_tails, True, f"r{round_number}_{name}_tails", dry_run)

    if not dry_run:
        remember(seen_cores, new_cores)
        remember(seen_ends, new_ends)
        remember(seen_swap, new_swaps)
        remember(seen_tails, new_tails)
    return gained


def confirmed_tails():
    """Every boundary tail (leading `_` or `/` kept) of every name this project has confirmed."""
    sys.path.insert(0, str(ROOT / "scripts"))
    import snapshot
    tails = set()
    for name in snapshot.confirmed_names():
        name = name.strip().lower().replace("\\", "/").encode("utf-8")
        for index, character in enumerate(name):
            if character in b"_/" and 0 < index < len(name) - 1:
                tails.add(name[index:])
    return tails


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--rounds", type=int, default=6)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--no-submit", action="store_true")
    parser.add_argument("--visual-only", action="store_true")
    args = parser.parse_args()
    LOGS.mkdir(parents=True, exist_ok=True)

    total = 0
    for round_number in range(1, args.rounds + 1):
        print(f"round {round_number}")
        gained = half("", round_number, args.dry_run)
        if not args.visual_only:
            gained += half("sound_", round_number, args.dry_run)
        if args.dry_run:
            return 0
        for game in GAMES:
            closure = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "derive_closure.py"), "--game", game,
                 "--anyway"], cwd=ROOT, capture_output=True, text=True)
            found = re.findall(r"^(\d+) names added in total", closure.stdout, re.M)
            added = int(found[-1]) if found else 0
            print(f"  closure {game}: +{added}")
            gained += added
        total += gained
        print(f" round {round_number} added {gained}\n")
        if gained and not args.no_submit:
            subprocess.run([tool("submit")], cwd=ROOT, stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL)
        if not gained:
            print("an empty round: the corpus is closed under this method until something else "
                  "confirms a name.")
            break
    print(f"{total} names added in total.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
