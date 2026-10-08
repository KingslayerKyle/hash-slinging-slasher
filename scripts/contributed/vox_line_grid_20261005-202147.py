r"""Voice lines x every speaker of their group, as files with takes and as aliases (Black Ops 4).

Black Ops 4's voice files are `en\vox\scripted\<group...>\<spk>\vox_<spk>_<line>_<take>.sn100.pc.snd`
and its aliases `vox_<spk>_<line>`. A line recorded for two speakers of a group (the multiplayer
specialists under `mpl\`, a zombies map's crew) is usually recorded for all of them, and the day's
word and pair sweeps keep adding lines nobody had crossed with the rest of the cast. For every line
seen with >= --min speakers of a group this offers every speaker of that group x the takes the line
is seen with (plus 00-03), as files, and the bare line as an alias.

    python contrib/vox_line_grid.py --files | bin\windows\confirm_list.exe - --game BLKOPS04 --no-fold ...
    python contrib/vox_line_grid.py --aliases | bin\windows\confirm_list.exe - --game BLKOPS04 ...
"""
import argparse
import collections
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sound_word_slots import present_unfolded  # noqa: E402

FILE = re.compile(r"^(en/vox/scripted/(?:.+/)?)([a-z0-9_]+)/vox_\2_(.+?)_(\d+)\.(sn100\.pc\.snd)$")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min", type=int, default=2)
    ap.add_argument("--files", action="store_true")
    ap.add_argument("--aliases", action="store_true")
    ap.add_argument("--count", action="store_true")
    args = ap.parse_args()

    names = present_unfolded("BLKOPS04", "sound_asset")
    speakers = collections.defaultdict(set)
    lines = collections.defaultdict(lambda: collections.defaultdict(set))
    width = {}
    for name in names:
        m = FILE.match(name)
        if not m:
            continue
        group, spk, line, take, ext = m.groups()
        speakers[group].add(spk)
        lines[group][line].add(spk)
        width.setdefault((group, line), set()).add(take)
    out = set()
    for group, by_line in lines.items():
        for line, who in by_line.items():
            if len(who) < args.min:
                continue
            takes = set(width[(group, line)])
            w = len(next(iter(takes)))
            takes |= {"%0*d" % (w, i) for i in range(4)}
            for spk in speakers[group]:
                if args.files:
                    for t in takes:
                        out.add("%s%s/vox_%s_%s_%s.sn100.pc.snd" % (group, spk, spk, line, t))
                if args.aliases:
                    out.add("vox_%s_%s" % (spk, line))
    out = {o for o in out if o not in names}
    print("%d candidates" % len(out), file=sys.stderr)
    if not args.count:
        sys.stdout.write("".join((o.replace("/", chr(92)) if args.files else o) + "\n" for o in sorted(out)))


if __name__ == "__main__":
    main()
