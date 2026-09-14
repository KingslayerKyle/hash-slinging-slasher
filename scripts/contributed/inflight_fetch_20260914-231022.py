"""Materialise the names in open pull requests as local seed folders.

Every derivation reads `submissions/` for its seed corpus, and an open pull request's names are
not there until it merges -- so nothing on this machine has ever derived from them. Written under
`submissions/_inflight_<original folder>/` so the path can never collide with the real folder when
the pull request merges. Remove the folders before the next `start`.
"""
import collections
import glob
import os
import sys

prs, root = sys.argv[1], sys.argv[2]
out = collections.defaultdict(list)
for path in sorted(glob.glob(os.path.join(prs, "pr_*.diff"))):
    current = None
    with open(path, encoding="utf-8-sig", errors="replace") as handle:
        for line in handle:
            line = line.rstrip("\r\n")
            if line.startswith("+++ "):
                target = line[4:].strip()
                current = target[2:] if target.startswith("b/") else None
                if current and not (current.startswith("submissions/") and current.endswith(".txt")):
                    current = None
                continue
            if line.startswith("diff --git"):
                current = None
                continue
            if current and line.startswith("+") and len(line) > 1:
                out[current].append(line[1:])

games = collections.Counter()
for rel, names in out.items():
    parts = rel.split("/")
    folder, base = parts[1], parts[-1]
    dest = os.path.join(root, "submissions", "_inflight_" + folder)
    os.makedirs(dest, exist_ok=True)
    with open(os.path.join(dest, base), "w", encoding="utf-8", newline="\n") as handle:
        handle.write("\n".join(names) + "\n")
    games["BLKOPS04" if "_BLKOPS04_" in folder else "BLKOPSCW"] += len(names)
print(len(out), "files;", dict(games))
