r"""Every short code, dropped into the middle slots the game fills with short codes.

Measured 2026-10-01 with `token_markov.py --holdout`: a token trigram model regenerates 56% of a
random held-out sample of Cold War's known anims inside 2M candidates -- and 0 of the unnamed ones
from the same budget. The unnamed remainder is therefore not shaped like the named set: almost every
unnamed name contains a token, or a junction, that no known name holds. Recombination of any kind
cannot produce a token nobody has seen. Brute force can, if the token is short and the place it
goes is known exactly.

So this finds *frames*: an exact known prefix and an exact known suffix around one slot, where the
slot is filled by at least --min different short codes (1-4 characters, not all digits) across the
names the game is known to hold -- `ai_zombie_base_walk_au_<v>_pain_chest_f`, `vox_<spk>_<line>`.
A slot that takes many short codes is an open class, and its unseen members are exactly the tokens
recombination cannot make. Every code of 1 to --length characters from [a-z0-9] is offered to each
frame on its own -- never one frame's prefix with another's suffix -- which keeps the candidate count
the frames times the code space and the collision expectation at zero.

Final slots are skipped: `affix_sweep.py` already sweeps short endings exhaustively.

    python contrib/open_slot_codes.py --game BLKOPSCW | bin\windows\confirm_list.exe - \
        --game BLKOPSCW --label "open-slot short codes" --script contrib/open_slot_codes.py
"""
import argparse
import collections
import itertools
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import token_markov  # noqa: E402

CODE = re.compile(r"^[a-z0-9]{1,4}$")
ALPHABET = "abcdefghijklmnopqrstuvwxyz0123456789"
POOLS = ("xmodel", "image", "material", "xanim", "sound_alias")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--game", required=True)
    ap.add_argument("--min", type=int, default=4)
    ap.add_argument("--length", type=int, default=3)
    ap.add_argument("--count", action="store_true")
    args = ap.parse_args()

    codes = ["".join(c) for n in range(1, args.length + 1) for c in itertools.product(ALPHABET, repeat=n)]
    frames = collections.defaultdict(set)
    known = set()
    for pool in POOLS:
        names, _ = token_markov.present(args.game, pool)
        known |= names
        for name in names:
            toks = name.split("_")
            for i in range(1, len(toks) - 1):
                if CODE.match(toks[i]) and not toks[i].isdigit():
                    frames[("_".join(toks[:i]) + "_", "_" + "_".join(toks[i + 1:]))].add(toks[i])
    kept = [k for k, v in frames.items() if len(v) >= args.min]
    print("%s: %d frames with >= %d short fillers, %d codes, %d candidates"
          % (args.game, len(kept), args.min, len(codes), len(kept) * len(codes)), file=sys.stderr)
    if args.count:
        return
    out = sys.stdout
    for head, tail in sorted(kept):
        seen = frames[(head, tail)]
        out.write("".join(head + c + tail + "\n" for c in codes if c not in seen))


if __name__ == "__main__":
    main()
