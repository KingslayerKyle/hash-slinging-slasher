"""Sound aliases named from the sound files that play them -- alias_to_file run backwards.

A sound file is `<dir>/<stem>.<channel><rate>.pc.<mix>.snd`, and the alias that plays it is very
often the stem itself, or the stem without its take number (`_01`, `_00`), or the directory's last
part joined to the stem. alias_to_file goes alias -> file; this goes file -> alias, seeded only from
sound files already confirmed.

    python contrib/file_to_alias.py <named sound_asset list> | confirm_list - --label ...
"""
import re
import sys

TAKE = re.compile(r"(_\d{1,3}|_[a-z])$")

seen = set()


def emit(name):
    if name and name not in seen:
        seen.add(name)
        print(name)


for line in open(sys.argv[1], encoding="utf-8"):
    path = line.strip().replace("\\", "/")
    if "/" not in path:
        continue
    parts = path.split("/")
    base = parts[-1].split(".")[0]
    dirs = parts[:-1]
    stems = {base}
    s = base
    while TAKE.search(s):
        s = TAKE.sub("", s)
        stems.add(s)
    for stem in stems:
        emit(stem)
        # the directory's last one or two parts carried into the alias
        for k in (1, 2):
            if len(dirs) >= k:
                emit("_".join(dirs[-k:] + [stem]))
        # top-level category (vox, zmb, fly, amb ...) as a prefix
        if dirs and not stem.startswith(dirs[0] + "_"):
            emit(dirs[0] + "_" + stem)
