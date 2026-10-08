"""Known sound-file stems from every game, crossed with the encoding tails a modern game uses.

A modern sound file is `<stem>.<codec>.<quality>.<rate>.<lang>`, e.g.
`iw9/wpn/ar_mike4/weap_mike4_fire_npc_med_01.lnn.85.48000.all`. The tail is chosen per asset by
the audio pipeline, not by whoever named it, so a stem that is real in MWII under `.lnn.85` can be
real in BO6 under `.lnn.75` or `.snn.75.48000.english`. Cross-game transfer only finds the exact
spelling, and so misses every asset whose tail moved.

Stems come from every known sound name (database tables, all_names, submissions, findings), with
the modern tail stripped, or the legacy Treyarch tail (`.rr75.pc.all.snd`, `.ln75.pc.english.snd`)
stripped. Tails are the ones verified names in the target game actually carry, most frequent first.

    python contrib/sound_tail_swap.py --game BLACKOP6 --tails 120 | confirm_list - --game BLACKOP6 ...
"""
from pathlib import Path
import argparse
import collections
import re
import sys

ROOT = Path(__file__).resolve().parent
while not (ROOT / "scripts" / "snapshot.py").is_file() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
sys.path.insert(0, str(ROOT / "scripts"))

MODERN = re.compile(r"^(.+?)\.([a-z]{3})\.(\d+)\.(\d+)\.([a-z_]+)$")
TAKE = re.compile(r"^(.*[_a-z])(\d{1,3})$")
LEGACY = re.compile(r"^(.+?)\.([a-z]{2}\d+)\.pc\.([a-z_]+)\.snd$")


def all_names():
    for f in sorted((ROOT / "cod-name-db" / "csv").glob("*.csv")):
        for line in f.open(encoding="utf-8", errors="replace"):
            _, _, name = line.rstrip("\r\n").partition(",")
            yield name.lower()
    for top in ("all_names", "submissions", "findings"):
        for f in sorted((ROOT / top).rglob("*.txt")):
            for line in f.open(encoding="utf-8", errors="replace"):
                _, sep, name = line.rstrip("\r\n").partition(",")
                if sep:
                    yield name.lower()


def target_tails(game):
    """Tails carried by names verified in the target game's capture, most frequent first."""
    import snapshot
    import settings
    paths = [Path(p) for p in snapshot.snapshots() if snapshot.read(p).game == game]
    snap = snapshot.read(paths[0])
    held = set(snap.by_pool().get("sound_asset", ()))
    count = collections.Counter()
    table = Path(settings.tables_csv()) / "fnv1a_xsounds_v2.csv"
    for line in table.open(encoding="utf-8", errors="replace"):
        key, _, name = line.strip().partition(",")
        try:
            key = int(key, 16)
        except ValueError:
            continue
        if key & snapshot.ID_MASK not in held:
            continue
        restored = snapshot.verified_database_row("fnv1a_xsounds_v2", key, name)
        if restored is None:
            continue
        m = MODERN.match(restored[1].lower())
        if m:
            count[restored[1].lower()[len(m.group(1)):]] += 1
    return [t for t, _ in count.most_common()]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--game", required=True)
    ap.add_argument("--tails", type=int, default=120)
    ap.add_argument("--all-tails", action="store_true",
                    help="also every modern tail any known name carries, not only the target's")
    ap.add_argument("--numbers", type=int, default=0,
                    help="renumber a stem's trailing take number 1..N (keeping its padding)")
    a = ap.parse_args()
    tails = target_tails(a.game)[: a.tails]
    stems = set()
    extra = collections.Counter()
    for name in all_names():
        m = MODERN.match(name) or LEGACY.match(name)
        if m:
            stems.add(m.group(1))
            if a.all_tails and m.re is MODERN:
                extra[name[len(m.group(1)):]] += 1
    tails += [t for t, n in extra.most_common() if t not in tails and n > 1]
    if a.numbers:
        renumbered = set()
        for stem in stems:
            m = TAKE.match(stem)
            if m:
                width = len(m.group(2))
                renumbered.update(f"{m.group(1)}{i:0{width}d}" for i in range(1, a.numbers + 1))
        stems = renumbered - stems
    print(f"{len(stems)} stems x {len(tails)} tails", file=sys.stderr)
    out = sys.stdout
    for stem in sorted(stems):
        out.write("".join(stem + t + "\n" for t in tails))


if __name__ == "__main__":
    main()
