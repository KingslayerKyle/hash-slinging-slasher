"""Sound files named after aliases: an alias placed in the folders its family's files live in.

2,245 of the 113,758 published sound files have a basename (text before the first '.') that is
exactly an alias name, and 75,840 named aliases have no file of that basename. This measures
whether that overlap is a convention or a coincidence: for every folder of known sound files, the
aliases sharing the first two tokens of that folder's basenames are tried in the folder with each
extension chain the folder uses. Prints full names with forward slashes; pipe once folded (Cold
War) and once with --backslash for Black Ops 4, whose sound names keep them.

    python contrib/alias_to_file.py | bin/windows/confirm_list.exe - --game BLKOPSCW
    python contrib/alias_to_file.py --backslash | bin/windows/confirm_list.exe - --game BLKOPS04 --no-fold
"""
from pathlib import Path
import collections
import re
import sys

ROOT = Path(__file__).resolve().parent
while not (ROOT / "scripts" / "snapshot.py").is_file() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
sys.path.insert(0, str(ROOT / "scripts"))
import snapshot

BACKSLASH = "\\"


TAKES = 8


def split(name):
    folder, _, base = name.rpartition("/")
    core, _, ext = base.partition(".")
    return folder, core, ext


def family(core):
    return "_".join(core.split("_")[:2])


def main():
    backslash = "--backslash" in sys.argv
    files = [n.lower().replace(BACKSLASH, "/") for n in snapshot.table_names("fnv1a_xsounds")]
    files += [n.lower().replace(BACKSLASH, "/") for n in snapshot.confirmed_names()
              if n.lower().endswith(".snd")]
    aliases = {n.lower() for n in snapshot.table_names("fnv1a_soundbanks_aliases")}
    aliases |= {n.lower() for n in snapshot.confirmed_names()
                if "/" not in n and "\\" not in n and "." not in n and n.lower().startswith(("vox_", "fly_", "evt_", "amb_", "wpn_", "zmb_", "mus_"))}

    by_family = collections.defaultdict(set)
    for alias in aliases:
        by_family[family(alias)].add(alias)

    folder_families = collections.defaultdict(set)
    folder_exts = collections.defaultdict(set)
    # Most sound files are their alias's name plus a take number (`_00`, `_01`); measured
    # 2026-10-01, when 107 Cold War files of the form `<alias>_00.rn75.pc.en.snd` were found by
    # another method straight after their aliases, and the takeless placement below had missed
    # every one. Each folder offers the takes it is seen to use, commonest first.
    folder_takes = collections.defaultdict(collections.Counter)
    for name in files:
        folder, core, ext = split(name)
        if folder and ext:
            folder_families[folder].add(family(core))
            folder_exts[folder].add(ext)
            take = re.search(r"_\d{1,3}$", core)
            if take:
                folder_takes[folder][take.group(0)] += 1

    out = set()
    for folder, families in folder_families.items():
        exts = folder_exts[folder]
        for fam in families:
            for alias in by_family.get(fam, ()):
                for ext in exts:
                    out.add(f"{folder}/{alias}.{ext}")
                    if "--takes" in sys.argv:
                        for take, _ in folder_takes[folder].most_common(TAKES):
                            out.add(f"{folder}/{alias}{take}.{ext}")
    print(f"{len(folder_families):,} folders, {len(aliases):,} aliases, {len(out):,} candidates",
          file=sys.stderr)
    for name in sorted(out):
        print(name.replace("/", BACKSLASH) if backslash else name)


if __name__ == "__main__":
    main()
