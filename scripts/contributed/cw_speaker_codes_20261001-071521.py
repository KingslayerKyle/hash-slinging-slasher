r"""Every 3-4 character speaker code, crossed with the voice lines Cold War speakers share.

Black Ops 4's exhaustive speaker-token search returned 176 names from 210 candidates' worth of
follow-up; Cold War never had one. A Cold War voice alias is `vox_<speaker>_<line>`, the speaker a
short code (`mcln`, `frs1`, `uao1`). A speaker whose code nobody knows has *every* line unnamed, and
no recombination of known names can produce the code -- but the code space is tiny. So: every code
of 3-4 characters from [a-z0-9] as stems, the lines at least --min known speakers share as endings,
and the engine peels the endings off the wanted ids. A hit names a new speaker; a script then fills
that speaker's grid (and its files) from the lines of its group.

    python contrib/cw_speaker_codes.py --write                 writes the stem/ending lists and plan
    bin\windows\confirm_plan.exe plans/cw_speaker_codes.txt --game BLKOPSCW
"""
import argparse
import collections
import itertools
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
while not os.path.isfile(os.path.join(ROOT, "scripts", "snapshot.py")) and ROOT != os.path.dirname(ROOT):
    ROOT = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import snapshot  # noqa: E402

ALPHABET = "abcdefghijklmnopqrstuvwxyz0123456789"
MASK = (1 << 63) - 1


def game_aliases(game):
    for path in snapshot.snapshots():
        snap = snapshot.read(path)
        if snap.game == game:
            ids = {i & MASK for i, p in snap.records if snap.pool_name(p) == "sound_alias"}
            break
    names = set(snapshot.table_names("fnv1a_soundbanks_aliases"))
    names.update(snapshot.confirmed_names("sound_alias"))
    return {n.strip().lower() for n in names if snapshot.fnv1a(n) & MASK in ids}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--game", default="BLKOPSCW")
    ap.add_argument("--min", type=int, default=3)
    ap.add_argument("--lengths", default="3,4")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()

    speakers = collections.defaultdict(set)
    for name in game_aliases(args.game):
        parts = name.split("_", 2)
        if len(parts) == 3 and parts[0] == "vox":
            speakers[parts[2]].add(parts[1])
    known = {s for v in speakers.values() for s in v}
    lines = sorted(line for line, who in speakers.items() if len(who) >= args.min)
    print("%d known speakers, %d lines shared by >= %d" % (len(known), len(lines), args.min), file=sys.stderr)

    tag = args.game.lower()
    stems = os.path.join(ROOT, "contrib", "cw_speaker_codes_stems.txt")
    ends = os.path.join(ROOT, "contrib", "cw_speaker_codes_ends_%s.txt" % tag)
    if args.write:
        with open(stems, "w") as handle:
            for n in map(int, args.lengths.split(",")):
                for combo in itertools.product(ALPHABET, repeat=n):
                    code = "".join(combo)
                    if code not in known:
                        handle.write(code + "\n")
        with open(ends, "w") as handle:
            for line in lines:
                handle.write("_" + line + "\n")
        with open(os.path.join(ROOT, "plans", "cw_speaker_codes_%s.txt" % tag), "w") as handle:
            handle.write(
                "label: exhaustive speaker codes x shared voice lines\n"
                "describe: vox_ + every unseen 3-4 char code + lines >= %d %s speakers share\n"
                "begin: vox_\n"
                "stem: @contrib/cw_speaker_codes_stems.txt\n"
                "end: @contrib/cw_speaker_codes_ends_%s.txt\n"
                "bare: no\n" % (args.min, args.game, tag))


if __name__ == "__main__":
    main()
