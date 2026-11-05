"""Fill missing wfoly_plr_<class>_<weapon>_<event> cells from verified modern names.

Unnamed MW7 profile is heavy on wfoly_. Measure every verified wfoly_plr name, keep
weapons with >=3 events and events seen on >=2 weapons, and cross every frequent
prefix with every such weapon x every shared event (skipping cells already held).

    python contrib/wfoly_event_grid.py          # writes plan lists
    bin/windows/confirm_plan plans/wfoly_MODWAR7.txt --script contrib/wfoly_event_grid.py
"""
from collections import Counter, defaultdict
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent
while not (ROOT / "scripts" / "snapshot.py").is_file() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
sys.path.insert(0, str(ROOT / "scripts"))
import snapshot

RX = re.compile(
    r"(?P<pre>.*?wfoly_plr_)(?P<cls>[a-z0-9]+)_(?P<wep>[a-z0-9]+)_(?P<evt>.+)$"
)


def names():
    out = set()
    for table in ("fnv1a_xsounds_v2", "fnv1a_soundbanks_aliases_v2"):
        for n in snapshot.table_names(table):
            if "wfoly_" in n.lower():
                out.add(n.lower())
    for top in ("findings", "submissions", "all_names"):
        base = ROOT / top
        if not base.exists():
            continue
        for kind in ("sound_asset", "sound_alias"):
            for path in base.rglob(kind + "*.txt"):
                for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
                    _, sep, name = line.partition(",")
                    if sep and "wfoly_" in name.lower():
                        out.add(name.lower())
    return out


def main():
    by_wep = defaultdict(set)
    events = Counter()
    prefixes = Counter()
    for n in names():
        m = RX.search(n)
        if not m:
            continue
        by_wep[(m["cls"], m["wep"])].add(m["evt"])
        events[m["evt"]] += 1
        prefixes[m["pre"]] += 1

    weps = sorted(f"{c}_{w}" for (c, w), ev in by_wep.items() if len(ev) >= 3)
    evs = sorted(e for e, c in events.items() if c >= 2)
    pres = sorted(p for p, c in prefixes.items() if c >= 5)
    out = ROOT / "contrib" / "out"
    out.mkdir(parents=True, exist_ok=True)
    (ROOT / "plans").mkdir(parents=True, exist_ok=True)
    (out / "wfoly_MODWAR7.begins.txt").write_text("\n".join(pres) + "\n", encoding="utf-8")
    (out / "wfoly_MODWAR7.stems.txt").write_text("\n".join(w + "_" for w in weps) + "\n", encoding="utf-8")
    (out / "wfoly_MODWAR7.ends.txt").write_text("\n".join(evs) + "\n", encoding="utf-8")
    plan = ROOT / "plans" / "wfoly_MODWAR7.txt"
    plan.write_text(
        "label: wfoly_plr class/weapon x shared event grid\n"
        "describe: frequent wfoly_plr_ prefixes x weapons with >=3 events x events "
        "seen on >=2 weapons (contrib/wfoly_event_grid.py)\n"
        "game: modwar7\n"
        "begin: @contrib/out/wfoly_MODWAR7.begins.txt\n"
        "stem: @contrib/out/wfoly_MODWAR7.stems.txt\n"
        "end: @contrib/out/wfoly_MODWAR7.ends.txt\n"
        "bare: yes\n",
        encoding="utf-8",
    )
    n = len(pres) * len(weps) * len(evs)
    print(f"wfoly grid: {len(pres)} prefixes x {len(weps)} weapons x {len(evs)} events = {n:,}", file=sys.stderr)
    print(plan)


if __name__ == "__main__":
    main()
