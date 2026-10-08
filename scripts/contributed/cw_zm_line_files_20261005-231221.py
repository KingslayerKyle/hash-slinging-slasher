r"""Cold War zombies voice lines: the BO4 reordering, both ways.

Found 2026-10-05: Cold War's zombies map lines follow the same convention as Black Ops 4's
(`bo4_zm_plr_files.py`) -- the alias puts the line first and the speaker and take last, the file puts
the map code and speaker first:

    vox_dark_aether_audiolog_05_alic_6   <->  vox/scripted/zmb/zm_audiologs/vox_<code>_alic_dark_aether_audiolog_05_6.rn75.pc.en.snd

Reading the 950 known files back as aliases returned 412 (4,759 candidates). This does both
directions over every zombies voice folder (folder, map code, extension chain) seen in a known file:

    --aliases   every known zombies voice file read back as `vox_<line>_<speaker>_<take>`
    --files     every known alias of that shape placed into every folder as a file

    python contrib/cw_zm_line_files.py --files | bin\windows\confirm_list.exe - --game BLKOPSCW ...
"""
import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import token_markov  # noqa: E402

FILE = re.compile(r"^(vox/scripted/zmb/[a-z0-9_]+)/vox_([a-z0-9]+)_([a-z0-9]+)_(.+?)_(\d+)\.([a-z0-9]+\.pc\.[a-z]+\.snd)$")
ALIAS = re.compile(r"^vox_(.+)_([a-z][a-z0-9]{2,5})_(\d+)$")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--aliases", action="store_true")
    ap.add_argument("--files", action="store_true")
    ap.add_argument("--count", action="store_true")
    args = ap.parse_args()

    files, _ = token_markov.present("BLKOPSCW", "sound_asset")
    aliases, _ = token_markov.present("BLKOPSCW", "sound_alias")
    folders = set()
    out = set()
    for f in files:
        m = FILE.match(f)
        if not m:
            continue
        folder, code, spk, line, take, ext = m.groups()
        folders.add((folder, code, ext))
        if args.aliases:
            out.add("vox_%s_%s_%s" % (line, spk, take))
    if args.files:
        for a in aliases:
            m = ALIAS.match(a)
            if not m:
                continue
            line, spk, take = m.groups()
            for folder, code, ext in folders:
                out.add("%s/vox_%s_%s_%s_%s.%s" % (folder, code, spk, line, take, ext))
    out -= aliases
    out -= files
    print("%d folders, %d candidates" % (len(folders), len(out)), file=sys.stderr)
    if not args.count:
        sys.stdout.write("".join(o + "\n" for o in sorted(out)))


if __name__ == "__main__":
    main()
