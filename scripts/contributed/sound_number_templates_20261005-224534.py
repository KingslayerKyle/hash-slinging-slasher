r"""Numbered sound templates, enumerated: `exec_<NNN>/exec_<NNN>_laststand` for every NNN.

Cold War's execution sounds are `mpl/executions/exec_<NNN>/exec_<NNN>_<part>.ln75.pc.all.snd` and
their aliases `evt_execution_<NNN>_<role>_<pose>_exerts` -- one grid per numbered execution, with only
46 of the numbers named. The numeric methods here (`numeric_slots.py`, `designation_grids.py`) only
read the visual pools, and sound paths carry the number twice (folder and basename).

So: every 2- or 3-digit number in a sound name (path or alias) becomes a placeholder -- the same
value in every place it appears -- names are grouped by the resulting template, and every template
seen with >= --min distinct numbers is filled with every number of that width.

    python contrib/sound_number_templates.py --game BLKOPSCW --pool sound_asset | confirm_list ...
"""
import argparse
import collections
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import token_markov  # noqa: E402
from sound_word_slots import present_unfolded  # noqa: E402

NUM = re.compile(r"(?<![0-9a-z])(\d{2,3})(?![0-9])")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--game", required=True)
    ap.add_argument("--pool", default="sound_asset")
    ap.add_argument("--min", type=int, default=3)
    ap.add_argument("--count", action="store_true")
    args = ap.parse_args()

    backslash = args.game == "BLKOPS04" and args.pool == "sound_asset"
    names = present_unfolded(args.game, args.pool) if backslash else token_markov.present(args.game, args.pool)[0]
    templates = collections.defaultdict(set)
    for name in names:
        values = set(NUM.findall(name.replace("_", " ").replace("/", " ").replace(".", " ")))
        for v in values:
            if len(v) not in (2, 3):
                continue
            # replace this value wherever it stands as a whole token
            tpl = re.sub(r"(?<![0-9])%s(?![0-9])" % v, "\x00", name)
            templates[(tpl, len(v))].add(v)
    out = set()
    for (tpl, width), vals in templates.items():
        if len(vals) < args.min:
            continue
        for n in range(10 ** width):
            out.add(tpl.replace("\x00", "%0*d" % (width, n)))
    out -= names
    print("%s %s: %d templates, %d candidates" % (args.game, args.pool,
          sum(1 for v in templates.values() if len(v) >= args.min), len(out)), file=sys.stderr)
    if not args.count:
        sys.stdout.write("".join((o.replace("/", chr(92)) if backslash else o) + "\n" for o in out))


if __name__ == "__main__":
    main()
