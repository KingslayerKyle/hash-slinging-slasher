r"""Sound paths whose folder and basename repeat a word, filled with every value the family uses there.

`sound_number_templates.py` (772 execution sounds on 2026-10-05) worked because a sound path repeats
its number in folder and basename. Paths repeat *words* the same way --
`wpn/smg/cqb/plr/wpn_smg_cqb_loop.ll75.pc.all.snd`, `fly/weapon/reload/sniper_cannon/fly_sniper_cannon_inspect`
-- and the repeated word is the asset's subject: a weapon, a vehicle, a creature.

Every token that appears both in a folder and in the basename becomes a placeholder (all its
occurrences), names group by template, and each template is filled with every value seen in the
placeholder of any template of its *family* (the first two path components) -- so a weapon's whole
file set is offered to every weapon its family knows.

`--two N` does the same for templates with two repeated words at once (`<move>` and `<surface>` in a
footstep path), each slot taking its family's N commonest values, crossed.

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
SLOT_A = chr(1)
SLOT_B = chr(2)


def repeated(name):
    folder, _, base = name.rpartition("/")
    if not folder:
        return []
    return sorted(t for t in set(folder.split("/")) & set(re.split(r"[_.]", base)) if TOKEN.match(t))


def family(tpl):
    return "/".join(tpl.split("/")[:2])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--game", required=True)
    ap.add_argument("--cap", type=int, default=400, help="most values offered per template")
    ap.add_argument("--two", type=int, default=0,
                    help="instead: templates with TWO repeated words, each slot filled with its family's N"
                         " commonest values, crossed")
    ap.add_argument("--dictionary", type=int, default=0,
                    help="instead: open templates (>= 3 values) x the N commonest English words")
    ap.add_argument("--count", action="store_true")
    args = ap.parse_args()

    backslash = args.game == "BLKOPS04"
    names = present_unfolded(args.game, "sound_asset") if backslash else token_markov.present(args.game, "sound_asset")[0]
    out = set()
    if args.two:
        two = collections.defaultdict(lambda: (set(), set()))
        for name in names:
            rep = repeated(name)
            parts = re.split(r"([/_.])", name)
            for i in range(len(rep)):
                for j in range(i + 1, len(rep)):
                    a, b = rep[i], rep[j]
                    tpl = "".join(SLOT_A if p == a else SLOT_B if p == b else p for p in parts)
                    two[tpl][0].add(a)
                    two[tpl][1].add(b)
        fam = collections.defaultdict(lambda: (collections.Counter(), collections.Counter()))
        for tpl, (va, vb) in two.items():
            fam[family(tpl)][0].update(va)
            fam[family(tpl)][1].update(vb)
        for tpl in two:
            fa, fb = fam[family(tpl)]
            for a, _ in fa.most_common(args.two):
                for b, _ in fb.most_common(args.two):
                    out.add(tpl.replace(SLOT_A, a).replace(SLOT_B, b))
        label = "%d two-slot templates" % len(two)
    elif args.dictionary:
        # templates whose repeated word already takes >= 3 values are an open class: offer the
        # dictionary, writing the word into both places at once (the frame sweeps cannot)
        from wordfreq import top_n_list
        words = [w for w in top_n_list("en", args.dictionary * 2) if re.match(r"^[a-z]{3,}$", w)][: args.dictionary]
        templates = collections.defaultdict(set)
        for name in names:
            parts = re.split(r"([/_.])", name)
            for tok in repeated(name):
                templates["".join(SLOT_A if p == tok else p for p in parts)].add(tok)
        open_tpl = [t for t, v in templates.items() if len(v) >= 3]
        total = 0
        for tpl in open_tpl:
            block = [tpl.replace(SLOT_A, w) for w in words if w not in templates[tpl]]
            total += len(block)
            if not args.count:
                sys.stdout.write("".join((b.replace("/", chr(92)) if backslash else b) + "\n" for b in block))
        print("%s: %d open templates x %d words, %d candidates" % (args.game, len(open_tpl), len(words), total),
              file=sys.stderr)
        return
    else:
        templates = collections.defaultdict(set)
        for name in names:
            parts = re.split(r"([/_.])", name)
            for tok in repeated(name):
                templates["".join(SLOT_A if p == tok else p for p in parts)].add(tok)
        fam = collections.defaultdict(collections.Counter)
        for tpl, vals in templates.items():
            fam[family(tpl)].update(vals)
        for tpl in templates:
            values = fam[family(tpl)]
            if len(values) < 2:
                continue
            for v, _ in values.most_common(args.cap):
                out.add(tpl.replace(SLOT_A, v))
        label = "%d templates" % len(templates)
    out -= names
    print("%s: %s, %d candidates" % (args.game, label, len(out)), file=sys.stderr)
    if not args.count:
        sys.stdout.write("".join((o.replace("/", chr(92)) if backslash else o) + "\n" for o in out))


if __name__ == "__main__":
    main()
