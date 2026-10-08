"""Where the unnamed assets actually are, per pool, per game.

This answers the first question anybody arriving here should ask and mostly does not: *is the
thing I am about to search for even there?* Two nights have been lost to that. One went on
`streamkey`, the largest pool in both games, and returned ~290,000 genuine and useless names.
One went on Black Ops 4 animations on the strength of a figure that turned out to be
`xmodelmesh` mislabelled -- the pool has 21,968 anims, not 259,051.

A pool with three hundred unnamed ids cannot repay an hour, however clever the method. A pool
with a hundred thousand can repay a week. That is the whole content of this script.

    python scripts/coverage.py                 every pool, both games
    python scripts/coverage.py --five          only the types that matter
    python scripts/coverage.py --game BLKOPS04

Reads the committed snapshots and the fetched tables. Needs no game and no network.
"""
import sys

import snapshot


def main(argv):
    only_five = "--five" in argv
    wanted_game = None
    if "--game" in argv:
        wanted_game = argv[argv.index("--game") + 1].upper()

    print("reading the tables", file=sys.stderr)

    for path in snapshot.snapshots():
        snap = snapshot.read(path)
        if wanted_game and snap.game != wanted_game:
            continue

        known = snapshot.known_hashes(game=snap.game)
        rows = []
        for pool, ids in snap.by_pool().items():
            if only_five and pool not in snapshot.IMPORTANT:
                continue

            unnamed = sum(1 for asset_id in ids if asset_id not in known)
            rows.append((unnamed, len(ids), pool))

        rows.sort(reverse=True)

        print("\n%s -- %d assets in %d filled pools" % (snap.game, len(snap), len(rows)))
        print("%-28s %10s %10s %8s  %s" % ("pool", "unnamed", "total", "named", ""))

        for unnamed, total, pool in rows:
            if unnamed == 0:
                continue

            share = 100.0 * (total - unnamed) / total
            note = ""
            if pool in snapshot.SKIP:
                note = "<- not worth searching; see LOW_VALUE_POOLS"
            elif pool in snapshot.IMPORTANT:
                note = "<- one we want"

            print("%-28s %10d %10d %7.1f%%  %s" % (pool, unnamed, total, share, note))

        reachable = sum(u for u, _, p in rows if p not in snapshot.SKIP)
        five = sum(u for u, _, p in rows if p in snapshot.IMPORTANT)
        print(
            "\n%s: %d unnamed in pools worth searching, %d of them in the types we want"
            % (snap.game, reachable, five)
        )


if __name__ == "__main__":
    main(sys.argv[1:])
