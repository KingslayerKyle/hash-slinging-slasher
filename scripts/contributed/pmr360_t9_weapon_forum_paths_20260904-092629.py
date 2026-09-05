"""Emit exact native T9 weapon sound paths posted on pmr360's ModMe export page.

Run:
    python contrib/pmr360_t9_weapon_forum_paths_20260904.py | target\\release\\confirm_list.exe - --game BLKOPSCW --sounds --label "pmr360 posted T9 weapon sound paths" --script contrib/pmr360_t9_weapon_forum_paths_20260904.py

Reads the public forum page's compiler-log text and writes only complete `t9_weapons\\...wav`
paths to stdout.  The linked full weapon archive is unavailable on Mega, but these paths are
explicit native source literals, not inferred spellings.  Reusable while the public page exists.
"""
import html
import re
import sys
import urllib.request


SOURCE = "https://forum.modme.co/wiki/threads/3540.html"
PATH = re.compile(r"t9_weapons\\(?:[a-z0-9_]+\\)*[a-z0-9_]+\.wav", re.I)


def main():
    request = urllib.request.Request(SOURCE, headers={"User-Agent": "Mozilla/5.0"})
    page = urllib.request.urlopen(request, timeout=60).read().decode("utf-8")
    names = {match.group(0).lower() for match in PATH.finditer(html.unescape(page))}
    if len(names) < 20:
        raise SystemExit("forum source did not expose the expected native path corpus")
    print("pmr360 forum page: {:,} exact T9 weapon sound paths".format(len(names)), file=sys.stderr)
    for name in sorted(names):
        print(name)


if __name__ == "__main__":
    main()
