"""Sound-file grids keyed on a token that appears in both the folder and the basename.

`rex/wpn/lm_recho/weap_rex_recho_fire_plr_atmo_06.qnn.85.48000.all` names its weapon twice, once in
the folder and once in the file. Replacing both with a hole gives a template; templates sharing the
same holed folder form a family, and every template of a family is offered with every value the
family has used. Measured 2026-10-16 on MW7's `rex/wpn/<cls>_<weapon>/weap_rex_<weapon>_*` family
alone: 24 weapons x 763 suffixes = 18,312 cells, 4,281 resolved.

    python contrib/both_ends_slot_grid.py <GAME> | confirm_list - --game <GAME>

Seeds: state/an/<GAME>_sound_asset.named (resolved in the target, in its own spelling).
"""
from collections import defaultdict
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent
while not (ROOT / "scripts" / "snapshot.py").is_file() and ROOT != ROOT.parent:
    ROOT = ROOT.parent

TAIL = re.compile(r"\.[a-z]{1,4}\.\d{1,3}\.\d{4,6}\.[a-z_]+$")
MAX_VALUES = 400          # a 'slot' with more values than this is not a slot, it is free text
MAX_TEMPLATES = 5000


def main():
    game = sys.argv[1].upper()
    dotted = game in ("MODWAR22", "YAMYAMOK")
    templates = defaultdict(set)    # holed folder -> holed file templates
    values = defaultdict(set)       # holed folder -> slot values
    for line in (ROOT / "state" / "an" / f"{game}_sound_asset.named").open(encoding="utf-8"):
        n = line.strip()
        m = TAIL.search(n)
        if not m:
            continue
        head, tail = n[:m.start()], n[m.start():]
        sep = "." if dotted else "/"
        folder, _, base = head.rpartition(sep)
        if not folder:
            continue
        segs = folder.split(sep)
        btoks = base.split("_")
        for i, seg in enumerate(segs):
            for tok in {seg, *seg.split("_")[1:]}:
                if len(tok) < 3 or tok not in btoks:
                    continue
                hf = sep.join(segs[:i] + [seg.replace(tok, "{}")] + segs[i + 1:])
                hb = "_".join("{}" if t == tok else t for t in btoks) + tail
                templates[hf].add(hb)
                values[hf].add(tok)
    out = sys.stdout
    emitted = 0
    for hf, vals in values.items():
        temps = templates[hf]
        if len(vals) < 2 or len(vals) > MAX_VALUES or len(temps) > MAX_TEMPLATES:
            continue
        for v in vals:
            folder = hf.replace("{}", v)
            sep = "." if dotted else "/"
            for t in temps:
                out.write(f"{folder}{sep}{t.replace('{}', v)}\n")
                emitted += 1
    print(f"{game}: {len(values):,} slot families, {emitted:,} candidates", file=sys.stderr)


if __name__ == "__main__":
    main()
