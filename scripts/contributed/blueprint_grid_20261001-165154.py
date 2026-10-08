r"""Weapon-blueprint attachment models, completed per weapon.

Cold War's single biggest model family is `attach_t9_<attachment>_<class>_<weapon>_<blueprint>_<view|world>`
-- 11,437 of the 68,354 named models: `attach_t9_mixstock_01_pro_ar_damage_halloween_world`,
`attach_t9_mixbarrel_01_sniper_quickscope_bwarrior_world_pc`. A blueprint reskins a whole weapon, so
every attachment that weapon offers can come in that blueprint, in both a view and a world model.

Per weapon (`<class>_<weapon>`), this collects every attachment part seen on it and every blueprint
seen on it, and offers attachment x blueprint x {view, world}, each with no suffix and with the
suffixes (`_pc`, `_sy`, ...) seen on that weapon. With --across-classes the attachment parts of every
weapon of the same class are pooled (a blueprint's barrel may only be known from a sibling weapon).

    python contrib/blueprint_grid.py --game BLKOPSCW | bin\windows\confirm_list.exe - \
        --game BLKOPSCW --label "weapon blueprint attachment grid" --script contrib/blueprint_grid.py
"""
import argparse
import collections
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import token_markov  # noqa: E402

CLASSES = "ar|smg|sniper|shotgun|pistol|lmg|tr|launcher|melee|special"
PATTERN = re.compile(r"^attach_(t\d)_(.+?)_(%s)_([a-z0-9]+)_(?:(.+?)_)?(view|world)(_[a-z0-9]+)?$" % CLASSES)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--game", default="BLKOPSCW")
    ap.add_argument("--across-classes", action="store_true")
    ap.add_argument("--probe", nargs="*", help="instead: offer these word lists (files, one word per line;"
                    " 'wordfreq' for its top 100k) as new blueprint names on each weapon's 3 most"
                    " blueprinted attachment parts")
    ap.add_argument("--count", action="store_true")
    args = ap.parse_args()

    names, _ = token_markov.present(args.game, "xmodel")
    parts = collections.defaultdict(set)
    prints = collections.defaultdict(set)
    suffixes = collections.defaultdict(set)
    era = {}
    for name in names:
        m = PATTERN.match(name)
        if not m:
            continue
        tag, part, cls, wpn, bp, _, sfx = m.groups()
        weapon = (cls, wpn)
        era[weapon] = tag
        parts[cls if args.across_classes else weapon].add(part)
        if bp:
            prints[weapon].add(bp)
        suffixes[weapon].add(sfx or "")
    if args.probe is not None:
        vocab = set()
        for src in args.probe:
            if src == "wordfreq":
                from wordfreq import top_n_list
                vocab |= {w for w in top_n_list("en", 200000) if re.match(r"^[a-z]{3,}$", w)}
            else:
                with open(src, encoding="utf-8") as handle:
                    vocab |= {w.strip() for w in handle if re.match(r"^[a-z0-9]{3,}$", w.strip())}
        per_part = collections.defaultdict(collections.Counter)
        for name in names:
            m = PATTERN.match(name)
            if m and m.group(5):
                per_part[(m.group(3), m.group(4))][m.group(2)] += 1
        out = sys.stdout
        total = 0
        for weapon, counter in per_part.items():
            cls, wpn = weapon
            for part, _ in counter.most_common(3):
                for vw in ("view", "world"):
                    block = ["attach_%s_%s_%s_%s_%s_%s" % (era[weapon], part, cls, wpn, w, vw)
                             for w in vocab if w not in prints[weapon]]
                    total += len(block)
                    if not args.count:
                        out.write("".join(c + "\n" for c in block))
        print("%s: probing %d weapons with %d words, %d candidates" % (args.game, len(per_part), len(vocab),
              total), file=sys.stderr)
        return
    cands = set()
    for weapon, bps in prints.items():
        cls, wpn = weapon
        pool = parts[cls if args.across_classes else weapon]
        for part in pool:
            for bp in bps:
                for vw in ("view", "world"):
                    for sfx in suffixes[weapon] | {""}:
                        cands.add("attach_%s_%s_%s_%s_%s_%s%s" % (era[weapon], part, cls, wpn, bp, vw, sfx))
    cands -= names
    print("%s: %d weapons with blueprints, %d candidates" % (args.game, len(prints), len(cands)), file=sys.stderr)
    if not args.count:
        sys.stdout.write("".join(c + "\n" for c in sorted(cands)))


if __name__ == "__main__":
    main()
