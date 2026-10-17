"""Unnamed aliases rebuilt from the named file they play and the wrappers their bank uses.

A link table (bank, alias, sound) pairs each alias with the files it plays. Where both are named,
the alias is a *wrapper* around the file's core: `amb_emt_sat_barrel_` + `light_buzz_soft_06_lp`
for `emt_iw9_light_buzz_soft_06_lp`, `rtl_sat_roji_` + `ceramic_potted_plant_large` for
`dst_ceramic_potted_plant_large_01`. Wrappers are learned per bank (alias minus the longest token
suffix it shares with the file core, file core = basename minus leading 1-2 tokens and trailing
take), and every unnamed alias linked to a named file in that bank is offered as
wrapper + core variants.

    python contrib/bank_wrapper_aliases.py <GAME> <links.tsv.gz> [--measure] | confirm_list - --game <GAME>
"""
from collections import defaultdict
import gzip
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent
while not (ROOT / "scripts" / "snapshot.py").is_file() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
sys.path.insert(0, str(ROOT / "scripts"))
import snapshot  # noqa: E402

M = snapshot.ID_MASK
TAIL = re.compile(r"\.[a-z]{1,4}\.\d{1,3}\.\d{4,6}\.[a-z_]+$")
MAX_WRAPPERS = 60


def cores(base):
    t = base.split("_")
    out = set()
    for drop_head in (0, 1, 2):
        for drop_take in (False, True):
            u = t[drop_head:]
            if drop_take and u and u[-1].isdigit():
                u = u[:-1]
            if len(u) >= 2:
                out.add("_".join(u))
    return out


def main():
    game, links = sys.argv[1].upper(), sys.argv[2]
    measure = "--measure" in sys.argv
    an = ROOT / "state" / "an"
    files = {}
    for line in (an / f"{game}_sound_asset.named").open(encoding="utf-8"):
        n = line.strip()
        m = TAIL.search(n)
        if m:
            files[snapshot.fnv1a(n, game, "sound_asset") & M] = n[:m.start()].replace("/", ".").rsplit(".", 1)[-1]
    aliases = {}
    for line in (an / f"{game}_sound_alias.named").open(encoding="utf-8"):
        n = line.strip()
        aliases[snapshot.fnv1a(n, game, "sound_alias") & M] = n
    wrappers = defaultdict(set)
    pairs, open_links = [], []
    for line in gzip.open(links, "rt"):
        b, a, s = (int(x, 16) & M for x in line.split("\t")[:3])
        if s not in files:
            continue
        if a in aliases:
            pairs.append((b, aliases[a], files[s]))
        else:
            open_links.append((b, files[s]))
    for b, al, base in pairs:
        for c in cores(base):
            if al.endswith("_" + c):
                wrappers[b].add(al[: -len(c)])
            elif ("_" + c + "_") in al:
                i = al.index("_" + c + "_")
                wrappers[b].add(al[: i + 1] + "{}" + al[i + 1 + len(c):])
    def build(b, base):
        ws = wrappers.get(b, ())
        if len(ws) > MAX_WRAPPERS:
            return set()
        out = set()
        for w in ws:
            for c in cores(base):
                out.add(w.replace("{}", c) if "{}" in w else w + c)
        return out
    if measure:
        hit = sum(1 for b, al, base in pairs if al in build(b, base))
        print(f"{game}: {len(pairs):,} named pairs, {hit:,} rebuilt by their bank's wrappers "
              f"({hit / max(1, len(pairs)):.1%}); {len(open_links):,} open links", file=sys.stderr)
        return
    seen = set()
    for b, base in open_links:
        for c in build(b, base):
            if c not in seen:
                seen.add(c)
                sys.stdout.write(c + "\n")
    print(f"{game}: {len(open_links):,} open links -> {len(seen):,} candidates", file=sys.stderr)


if __name__ == "__main__":
    main()
