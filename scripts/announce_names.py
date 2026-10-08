"""Post the recovered-name figures to a Discord webhook, when they have moved.

    python scripts/announce_names.py            post, using $DISCORD_WEBHOOK
    python scripts/announce_names.py --dry-run  print the payload, send nothing

Reads `all_names/summary.json`, which `collect_names.py` writes beside the README. The README is
HTML so it can put game tables side by side, which is right for a reader and wrong for a program:
scraping it would break the next time anybody touches the layout. This reads the JSON instead, so
the page and the announcement can each change without the other noticing.

## Why a webhook rather than a bot

A bot needs an application, a token, a process running somewhere and hosting for it. All this has
to do is speak when the numbers change, which a webhook does for nothing: Discord makes the URL,
Actions does the sending, and there is no service to keep alive. A bot would only be worth it to
*answer* things -- a slash command that reports live figures on demand.

## It says nothing when it has nothing to say

No `DISCORD_WEBHOOK` in the environment and this exits quietly and successfully. A fork running
the workflow, or anybody running it locally, should not fail a build over a secret it was never
meant to have.
"""

import argparse
import json
import os
import pathlib
import sys
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent
while not (ROOT / "scripts" / "snapshot.py").exists() and ROOT != ROOT.parent:
    ROOT = ROOT.parent

SUMMARY = ROOT / "all_names" / "summary.json"
REPO = "https://github.com/KingslayerKyle/hash-slinging-slasher"

# The folder names are how the files are filed; these are what people call them.
#
# Kept short on purpose. These become the heading of an inline embed field, which is about half
# the card's width, and a heading that wraps to a second line pushes that column's rows down --
# so game columns stay easy to compare. "Black Ops Cold War" wrapped; "Cold War" does
# not. Check the card after changing one.
NICE = {"blkops04": "Black Ops 4", "blkopscw": "Cold War",
        "modwar22": "Modern Warfare II", "yamyamok": "Modern Warfare III",
        "blackop6": "Black Ops 6", "blackop7": "Black Ops 7", "modwar7": "Modern Warfare 4"}

# GitHub green, so the card reads as a repository update rather than an alert.
COLOUR = 0x2EA043


def embed(summary):
    """One card: a column per game, a row per asset type, the total in the footer."""
    # The order comes from the file rather than from here, so the card and the README always
    # list the types the same way. `collect_names.py` writes it; anything missing sorts after.
    order = summary.get("order") or []
    rank = {kind: index for index, kind in enumerate(order)}

    fields = []
    # Follow the display-name mapping: older games first, then the modern releases.
    game_rank = {game: index for index, game in enumerate(NICE)}
    for game, data in sorted(summary["games"].items(),
                             key=lambda item: (game_rank.get(item[0], len(game_rank)), item[0])):
        rows = sorted(
            data["types"].items(),
            key=lambda pair: (rank.get(pair[0], len(rank)), pair[0]),
        )
        lines = []
        for kind, counts in rows:
            found = counts.get("found_pct")
            # Two unrelated numbers, so they are labelled rather than left adjacent: the first is
            # what this project found, the second is how much of that pool everybody together has
            # named. Printed side by side and unlabelled, the first reads as the percentage's
            # numerator, which it is not.
            lines.append(
                "`%-12s %7s` %5s named"
                % (
                    kind,
                    "+" + format(counts["names"], ","),
                    "%.1f%%" % found if found is not None else "--",
                )
            )
        fields.append(
            {
                "name": "%s — %s found here" % (NICE.get(game, game), format(data["names"], ",")),
                "value": "\n".join(lines),
                "inline": True,
            }
        )

    totals = summary["totals"]
    return {
        "title": "GitHub repository",
        "url": REPO + "/tree/main/all_names",
        "color": COLOUR,
        "fields": fields,
        "footer": {
            "text": "%s names found by this project - \"named\" is how much of that pool "
            "has been named in total (including cod-name-db too)" % format(totals["names"], ",")
        },
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dry-run", action="store_true", help="print the payload, send nothing")
    args = parser.parse_args()

    if not SUMMARY.exists():
        print("no all_names/summary.json -- run collect_names.py first", file=sys.stderr)
        return 1

    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
    payload = {"embeds": [embed(summary)]}

    if args.dry_run:
        # Written as UTF-8 bytes rather than printed. A Windows console is cp1252, and printing
        # an em-dash to it produces a byte nothing downstream can decode -- which matters because
        # --dry-run exists to be piped into something else.
        out = json.dumps(payload, indent=2, ensure_ascii=False).encode("utf-8")
        sys.stdout.buffer.write(out + bytes([10]))
        return 0

    url = os.environ.get("DISCORD_WEBHOOK", "").strip()
    if not url:
        # Not an error. See the module docstring.
        print("no DISCORD_WEBHOOK set, so nothing was announced")
        return 0

    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "User-Agent": "hash-slinging-slasher"},
    )

    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            print("announced (%s)" % response.status)
    except urllib.error.HTTPError as error:
        # A failed announcement must not fail the build: the names are already committed and the
        # figures are already on the page. Say so and move on.
        print("Discord refused the post (%s): %s" % (error.code, error.reason), file=sys.stderr)
    except Exception as error:
        print("could not reach Discord: %s" % error, file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
