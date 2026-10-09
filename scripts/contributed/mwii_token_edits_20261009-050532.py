"""Token insertion and deletion over MWII's sound names.

    python contrib/mwii_token_edits.py --pool sound_asset | bin\\windows\\confirm_list.exe - ^
        --game MODWAR22 --label "MWII sound token edits" --script contrib/mwii_token_edits.py
    python contrib/mwii_token_edits.py --pool sound_asset --count      # size it first

## The gap this fills, and why the shared-tail plan cannot

`scripts/token_edits.py` says it plainly: *"Every method in METHODS.md substitutes, and none of
them changes a name's length"*, and gives the unreachable case as

    p9_rus_apartment_tower_sign_01
    p9_rus_apartment_stone_tower_sign_01     <- an insertion, reachable by nothing

That is exactly the shape of my own method's blind spot, measured rather than assumed.
`mwii_shared_tail_plan.py` crosses every measured **head** with every measured **tail**, so it can
only ever build names whose prefix-before-a-cut *and* whose suffix-after-a-cut are both attested.
Inserting a token means the head gains a component it never had:

    iw9.wpn.ar_kar98k.ar_kar98k_fire_plr_shot_03.ln.75.48000.all     head, tail  -- found
    iw9.wpn.ar_kar98k.ar_kar98k_fire_plr_impact_shot_03.ln.75.48000.all   <- unreachable

Widening the vocabulary does not help: the token has to be measured *at that position*, under that
leading token, from names the game actually has. That is what this does, following
`scripts/token_edits.py`'s own design -- deletions need no vocabulary at all, and insertions are
offered only words observed at that position among names sharing a leading token.

## Why this is a new script and not a `--type` flag

Two reasons, both specific to MWII, and neither is a refactor:

* `token_edits.py`'s `TYPES` covers model/material/image/anim against the **legacy** tables
  (`fnv1a_xmodels`, not `fnv1a_xmodels_v2`). Every modern game needs the IW offset and the `_v2`
  tables, so no MWII pool is reachable from it as written.
* It splits a name with `rpartition("/")`. A MWII sound **file** is a dot-separated path carrying a
  four-component encoding tail -- `iw9.dst.iw9_dst_street_barricade_03.ln.75.48000.all` -- so
  `rpartition("/")` finds nothing, the whole thing becomes one basename, and every edit lands in the
  encoding instead of the name. **45,882 of 45,911 MWII sound names are dotted, so this is not an
  edge case, it is the pool.**

MWII sound **aliases** need the opposite treatment: they are flat, with no path and no tail. Both
are handled here, because getting that backwards is exactly how a sound method ends up matching
nothing while looking healthy.
"""
import argparse
import collections
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))

import settings
import snapshot

# Beyond this a name is a generated identifier rather than a composed one, and editing it produces
# vocabulary that means nothing. Same bound the library script uses.
MAX_TOKENS = 14

TAIL = re.compile(r"\.(?P<chan>[a-z]{1,4})\.(?P<qual>\d+)\.48000\.(?P<ext>[a-z_]+)$")

POOLS = {
    "sound_asset": ("fnv1a_xsounds_v2", True),
    "sound_alias": ("fnv1a_soundbanks_aliases_v2", False),
}


def corpus(game, pool):
    """Verified names the game's own capture holds, spelled the way they were hashed."""
    table, masked = POOLS[pool]
    path = [p for p in snapshot.snapshots() if snapshot.read(p).game == game][0]
    held = {k: set(v) for k, v in snapshot.read(path).by_pool().items()}
    ids = held.get(pool, set())
    out = set()
    with (Path(settings.tables_csv()) / (table + ".csv")).open(encoding="utf-8",
                                                               errors="replace") as handle:
        for line in handle:
            key, sep, display = line.strip().partition(",")
            if not sep:
                continue
            try:
                key = int(key, 16)
            except ValueError:
                continue
            # Alias keys are stored full 64-bit; sound-file keys are masked. Getting this wrong
            # reports a healthy pool as half missing, silently.
            if key not in ids and (key & snapshot.ID_MASK) not in ids:
                continue
            restored = snapshot.verified_database_row(table, key, display)
            if restored is None:
                continue
            _, name = restored
            hashed = snapshot.fnv1a(name, game, pool)
            if (hashed & snapshot.ID_MASK) != (key & snapshot.ID_MASK) if masked else hashed != key:
                continue
            out.add(name)
    return out


def split(name, dotted):
    """(prefix, tokens): prefix is everything outside the editable basename.

    For a sound file that is the dotted directory **and** the encoding tail, because the tail is
    not part of the name and must not be edited -- `_03.ln.75.48000.all` is one fixed string, and
    treating its dots as separators is how a variant index becomes an extra token.
    """
    if not dotted:
        return "", name.split("_")
    match = TAIL.search(name)
    if not match:
        return "", name.split("_")
    prefix = name[: match.start()]
    directory, _, base = prefix.rpartition(".")
    return (directory + "." if directory else "") + name[match.start():], base.split("_")


def vocabulary(parsed, cap, min_seen):
    """{(leading token, position): [words observed there]}.

    Keyed on the leading token so a name beginning `iw9_` is offered what follows `iw9_` elsewhere,
    not the corpus's globally common words. A global list would be the same handful everywhere and
    would reach almost nothing.
    """
    seen = collections.defaultdict(collections.Counter)
    for _, tokens in parsed:
        if len(tokens) > MAX_TOKENS:
            continue
        head = tokens[0]
        for position, token in enumerate(tokens):
            seen[(head, position)][token] += 1
    out = {}
    for key, counter in seen.items():
        words = [w for w, c in counter.most_common(cap) if c >= min_seen]
        if words:
            out[key] = words
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--game", default="MODWAR22")
    parser.add_argument("--pool", default="sound_asset", choices=sorted(POOLS))
    parser.add_argument("--cap", type=int, default=12)
    parser.add_argument("--min-seen", type=int, default=8)
    parser.add_argument("--count", action="store_true")
    parser.add_argument("--no-insert", action="store_true")
    args = parser.parse_args()

    game = args.game.upper()
    dotted = POOLS[args.pool][1]
    known = corpus(game, args.pool)
    parsed = [split(name, dotted) for name in known]
    words = {} if args.no_insert else vocabulary(parsed, args.cap, args.min_seen)

    seen = set()
    made = 0
    for prefix, tokens in parsed:
        if len(tokens) < 2 or len(tokens) > MAX_TOKENS:
            continue

        for position in range(len(tokens)):
            shorter = tokens[:position] + tokens[position + 1:]
            if not shorter:
                continue
            candidate = prefix + "_".join(shorter)
            if candidate not in known and candidate not in seen:
                seen.add(candidate)
                made += 1
                if not args.count:
                    print(candidate)

        if args.no_insert:
            continue

        head = tokens[0]
        for position in range(1, len(tokens) + 1):
            for word in words.get((head, min(position, len(tokens) - 1)), ()):
                longer = tokens[:position] + [word] + tokens[position:]
                candidate = prefix + "_".join(longer)
                if candidate not in known and candidate not in seen:
                    seen.add(candidate)
                    made += 1
                    if not args.count:
                        print(candidate)

    sys.stderr.write("%s %s: %d known names, %d candidates\n"
                     % (game, args.pool, len(known), made))
    if args.count:
        print("\n    python contrib/mwii_token_edits.py --pool %s | bin\\windows\\confirm_list.exe "
              "- ^ --game %s --label \"MWII %s token edits\" "
              "--script contrib/mwii_token_edits.py" % (args.pool, game, args.pool))


if __name__ == "__main__":
    main()