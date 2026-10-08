r"""Sound paths whose folder and basename repeat a word, filled with every value the family uses there.

`sound_number_templates.py` (772 execution sounds on 2026-10-05) worked because a sound path repeats
its number in folder and basename. Paths repeat *words* the same way --
`wpn/smg/cqb/plr/wpn_smg_cqb_loop.ll75.pc.all.snd`, `fly/weapon/reload/sniper_cannon/fly_sniper_cannon_inspect`
-- and the repeated word is the asset's subject: a weapon, a vehicle, a creature.

Every token that appears both in a folder and in the basename becomes a placeholder (all its
occurrences), names group by template, and each template is filled with every value seen in the
placeholder of any template of its *family* (the same template text with the placeholder's folder
parent -- i.e. the same first two path components) -- so a weapon's whole file set is offered to
every weapon its family knows.

    python contrib/sound_word_templates.py --game BLKOPSCW | bin\windows\confirm_list.exe - --game BLKOPSCW ...
"""
import argparse
import collections
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import token_markov  # noqa: E402
from sound_word_slots import present_unfolded  # noqa: E402

TOKEN = re.compile(r"^[a-z][a-z0-9]{1,}$")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--game", required=True)
    ap.add_argument("--cap", type=int, default=400, help="most values offered per template")
    ap.add_argument("--count", action="store_true")
    args = ap.parse_args()

    backslash = args.game == "BLKOPS04"
    names = present_unfolded(args.game, "sound_asset") if backslash else token_markov.present(args.game, "sound_asset")[0]
    templates = collections.defaultdict(set)
    for name in names:
        folder, _, base = name.rpartition("/")
        if not folder:
            continue
        ftoks = set(folder.split("/"))
        btoks = set(re.split(r"[_.]", base))
        for tok in (ftoks & btoks):
            if not TOKEN.match(tok):
                continue
            parts = re.split(r"([/_.])", name)
            tpl = "".join("\x00" if p == tok else p for p in parts)
            templates[tpl].add(tok)
    family = collections.defaultdict(collections.Counter)
    for tpl, vals in templates.items():
        fam = "/".join(tpl.split("/")[:2])
        family[fam].update(vals)
    out = set()
    for tpl, vals in templates.items():
        fam = "/".join(tpl.split("/")[:2])
        if len(family[fam]) < 2:
            continue
        for v, _ in family[fam].most_common(args.cap):
            out.add(tpl.replace("\x00", v))
    out -= names
    print("%s: %d templates, %d candidates" % (args.game, len(templates), len(out)), file=sys.stderr)
    if not args.count:
        sys.stdout.write("".join((o.replace("/", chr(92)) if backslash else o) + "\n" for o in out))


if __name__ == "__main__":
    main()
