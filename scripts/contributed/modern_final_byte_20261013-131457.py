"""Solves a modern capture's final character backwards -- method 16, applied to the five titles
whose hash basis it has never been run against.

    python contrib/modern_final_byte.py --game MODWAR22 | bin\\windows\\confirm_list.exe - ^
        --game MODWAR22 --label "modern final byte solved backwards" ^
        --script contrib/modern_final_byte.py

Reads:  snapshots/<game>.ids and .pools.txt, tables/*.csv (the `_v2` files for this game),
        all_names/<game>/<type>.txt, findings/<game>/<type>*.txt.
Writes: nothing. Candidate names on standard output, one per line; a summary on standard error.
Reusable: yes, one game per invocation. Re-run after any pass that confirms anything, for the
        same reason `scripts/final_byte.py` is re-run: every new name is a new prefix to solve
        against, and this costs seconds.

## Why this exists

`scripts/final_byte.py` is the best-measured method in this repository -- one name per 18
candidates, against the next best at one per 394. Every one of the ten scripts here that uses the
inverse solve, `final_byte.py` included, hashes with the Treyarch basis
(`0xCBF29CE484222325`). The five modern captures do not: `src/games.rs::basis` gives ordinary
modern assets the IW offset (`0x47F5817A5EF961BA`) and only `sound_alias`, `bone` and `bones`
keep Treyarch's. So on a modern capture the legacy solve computes a prefix hash the game never
computed, asks a question about ids that were never hashed that way, and returns nothing while
looking perfectly healthy. The largest entry in the registry for this shape of work --
`mwiii-typed-image-final-byte` -- tested **seven** hand-measured candidates and found seven; the
method itself has never been swept across a modern capture.

## What it does, exactly

Same arithmetic as `scripts/final_byte.py`:

    h(A) - h(B) = ((h_prefix ^ a) - (h_prefix ^ b)) * prime

so for two names differing only in their last character the two hashes differ by an exact small
multiple of the prime, and the relation inverts:

    u = (h(prefix) ^ byte) * prime   =>   byte = (u * prime_inverse) ^ h(prefix)

Nothing is hashed per candidate: for each unnamed id and each printable ASCII byte there is one dict
lookup against names already known to be real, with their last character removed.

Two things differ from the legacy script, and both are the whole point:

- **The basis is per pool**, read from the same policy the Rust side uses, so the lookup is
  against hashes the game actually produced. `sound_alias` keeps the Treyarch basis.
- **Lookup always uses 63 bits**, including sound aliases: captured IDs clear bit 63.
  The odd prime is invertible modulo 2^63. Confirmation restores all 64 bits for
  modern sound-alias output after hashing the solved name again.

Every solved name is hashed back and compared before it is printed, at the pool's own width.
That check is not belt and braces -- it is what separates a solved name from a plausible one, and
the legacy script's own comment records 11,003 solutions against 63 real ones without it.

## What it measured

See the run notes in the submission that carried it. Measured 2026-10-13 on this clone, one
invocation per game; `confirm_list` reports the confirmed and new counts.
"""
import argparse
import glob
import os
import sys

_root = os.path.dirname(os.path.abspath(__file__))
while _root != os.path.dirname(_root) and not os.path.isfile(
    os.path.join(_root, "scripts", "snapshot.py")
):
    _root = os.path.dirname(_root)
if not os.path.isfile(os.path.join(_root, "scripts", "snapshot.py")):
    raise SystemExit("Run inside a hash-slinging-slasher checkout")
sys.path.insert(0, os.path.join(_root, "scripts"))

import snapshot  # noqa: E402

PRIME = 0x100000001B3
PRIME_INVERSE = pow(PRIME, -1, 1 << 64)
M64 = 0xFFFFFFFFFFFFFFFF
ID_MASK = 0x7FFFFFFFFFFFFFFF

BASIS = 0xCBF29CE484222325
IW_BASIS = 0x47F5817A5EF961BA

MODERN = {"MODWAR22", "YAMYAMOK", "BLACKOP6", "BLACKOP7", "MODWAR7"}

# Which published table feeds which pool. `fnv1a_animpkgs_v2` is a separate pool and is left out
# on purpose: an animpkg is not an xanim, and the two are not the same kind of asset.
TABLES = {
    "image": ("fnv1a_ximages_v2",),
    "material": ("fnv1a_xmaterials_v2",),
    "xanim": ("fnv1a_xanims_v2",),
    "sound_asset": ("fnv1a_xsounds_v2",),
    "sound_alias": ("fnv1a_soundbanks_aliases_v2",),
}


def basis_for(kind):
    """`src/games.rs::basis`, spelled for Python."""
    return BASIS if kind in ("sound_alias", "bone", "bones") else IW_BASIS


def width_for(kind):
    """Captured lookup width; output width is restored by confirm_list."""
    return ID_MASK


def fnv1a(name, basis):
    """The game's hash: lower cased, backslashes folded, run from the pool's own offset."""
    value = basis
    for byte in name.strip().translate(str.maketrans('ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')).replace("\\", "/").encode("utf-8", "replace"):
        value = ((value ^ byte) * PRIME) & M64
    return value


def seed_names(game, kind):
    """Names already known to be real for this pool: the published table, then what we hold.

    `all_names/<game>/<type>.txt` is every name in every merged submission, filed by the pool it
    was found under, and it is the game's own corpus rather than everybody's mixed together.
    """
    names = set(snapshot.table_names(*TABLES[kind]))
    names.update(snapshot.confirmed_names(kind))
    shot = snapshot.read(snapshot_path(game))
    ids = set(shot.by_pool().get(kind, []))
    return {name for name in names if len(name) >= 2
            and fnv1a(name, basis_for(kind)) & ID_MASK in ids}



def snapshot_path(game):
    for path in snapshot.snapshots():
        if snapshot.read(path).game.upper() == game:
            return path
    raise SystemExit("no snapshot for %s" % game)


def solve(prefixes, ids, basis, width):
    """{name: id} for every unnamed id a known seed with its final printable ASCII character replaced."""
    table = {}
    for seed in prefixes:
        name = seed[:-1]
        key = fnv1a(name, basis) & width
        table.setdefault(key, name)

    found = {}
    for value in ids:
        # (id * inverse) mod width is the masked prefix hash the id wants, and the byte only
        # touches the low eight bits, so one lookup per byte answers for the whole alphabet.
        scaled = (value * PRIME_INVERSE) & width
        for byte in range(33, 127):
            prefix = table.get(scaled ^ byte)
            if prefix is None:
                continue
            character = chr(byte)
            if not character.isprintable() or character.isspace():
                continue

            name = prefix + character
            if fnv1a(name, basis) & width == value:
                found[name] = value
    return found


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--game", required=True, help="one of " + ", ".join(sorted(MODERN)))
    options = parser.parse_args(argv)

    game = options.game.upper()
    if game not in MODERN:
        raise SystemExit(
            "%s is not a modern capture; use scripts/final_byte.py, which is correct for the "
            "legacy basis" % game
        )

    snap = snapshot.read(snapshot_path(game))
    known = snapshot.known_hashes(game=game)
    left = snap.unnamed(known)

    by_pool = {}
    for asset_id, pool in left.items():
        by_pool.setdefault(pool, []).append(asset_id)

    total = 0
    for kind in TABLES:
        ids = by_pool.get(kind, [])
        if not ids:
            print("%-12s %8d unnamed, none to solve" % (kind, 0), file=sys.stderr)
            continue

        names = seed_names(game, kind)
        basis = basis_for(kind)
        width = width_for(kind)
        found = solve(names, ids, basis, width)
        total += len(found)

        print(
            "%-12s %8d unnamed, %9d prefixes, %6d solved (%s)"
            % (
                kind,
                len(ids),
                len(names),
                len(found),
                "full 64-bit" if width == M64 else "63-bit",
            ),
            file=sys.stderr,
        )
        for name in sorted(found):
            sys.stdout.write(name + "\n")

    sys.stdout.flush()
    print("%s candidate(s)" % format(total, ","), file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
