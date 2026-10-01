r"""Sound alias names read off the sound files they play.

`alias_to_file.py` went alias -> file. This goes the other way: a sound file's basename (the text
before the first `.`) is very often its alias's name, and an alias that plays one of several takes
is that basename minus the trailing take number (`vox_x_congrat_sml_03` -> `vox_x_congrat_sml`).
Every published or confirmed `sound_asset` name in either game is reduced both ways and printed.

    python contrib/aliases_from_files.py | bin\windows\confirm_list.exe - --game BLKOPSCW \
        --label "aliases from sound files" --script contrib/aliases_from_files.py
"""
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
while not os.path.isfile(os.path.join(ROOT, "scripts", "snapshot.py")) and ROOT != os.path.dirname(ROOT):
    ROOT = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import snapshot  # noqa: E402

TAKE = re.compile(r"(?:[_ ]?(?:\d+|[a-z]))$")


def sound_files():
    names = set(snapshot.table_names("fnv1a_xsounds", "fnv1a_xsounds_v2"))
    names.update(snapshot.confirmed_names("sound_asset"))
    return names


def main():
    out = set()
    for name in sound_files():
        base = name.strip().lower().replace(chr(92), "/").rsplit("/", 1)[-1].split(".", 1)[0]
        if not base:
            continue
        out.add(base)
        stripped = re.sub(r"_\d+$", "", base)
        out.add(stripped)
        out.add(re.sub(r"_\d+$", "", stripped))
        # takes are sometimes letters, or a number glued on without the underscore
        out.add(re.sub(r"\d+$", "", base).rstrip("_"))
    for name in sorted(out):
        if name:
            sys.stdout.write(name + "\n")
    print("%d candidates" % len(out), file=sys.stderr)


if __name__ == "__main__":
    main()
