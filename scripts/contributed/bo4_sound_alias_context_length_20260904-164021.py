"""Context-evidenced token deletion/reinsertion for native BO4 sound aliases."""
import collections, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import snapshot

known = {n.strip().lower() for n in snapshot.table_names("fnv1a_soundbanks_aliases", "fnv1a_soundbanks_aliases_v2") if n.strip()}
known.update(n.strip().lower() for n in snapshot.confirmed_names("sound_alias") if n.strip())
parsed = [(n, n.split("_")) for n in known if 2 <= len(n.split("_")) <= 14 and all(n.split("_"))]
between = collections.defaultdict(set)
for _, tokens in parsed:
    for pos, token in enumerate(tokens):
        between[(tuple(tokens[:pos]), tuple(tokens[pos+1:]))].add(token)
out = set()
for name, tokens in parsed:
    for pos in range(len(tokens)):
        candidate = "_".join(tokens[:pos] + tokens[pos+1:])
        if candidate and candidate not in known:
            out.add(candidate)
    for pos in range(1, len(tokens)):
        context = (tuple(tokens[:pos]), tuple(tokens[pos:]))
        for token in between.get(context, ()):
            candidate = "_".join(tokens[:pos] + [token] + tokens[pos:])
            if candidate not in known:
                out.add(candidate)
print(f"{len(known):,} native BO4 aliases -> {len(out):,} context-length candidates", file=sys.stderr)
for candidate in sorted(out):
    print(candidate)
