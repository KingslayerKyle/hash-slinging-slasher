"""coordinated_identifiers, pooled across every asset type instead of run per-type.

The original method (scripts/contributed/coordinated_identifiers_20260922-122153.py) finds tokens
that repeat within a name, groups names into templates with that token masked, and learns a
substitution rule when two different tokens are seen filling the *same* template shape at least
twice -- but it does this once per asset type, with each type's names as a separate closed world.

The tokens these rules capture (operator codes, faction names, camo colors, weapon variants) are
game vocabulary, not naming-convention vocabulary -- there is no reason a rule like usa<->rus
should only be learnable from xmodel siblings when material or image names might carry the same
two tokens in a template xmodel never happened to repeat. This pools every type's known names into
one flat set before looking for repeated-token evidence, so a rule can be supported by sibling
frames from *any* type, then applies the resulting rules back across every type's names. Output is
split into visual/sound candidate files the way the original does, since sound still needs its own
confirm pass.
"""
from pathlib import Path
from collections import Counter, defaultdict
import argparse
import itertools
import json
import re
import sys

ROOT = Path(__file__).resolve().parent
while not (ROOT / 'scripts' / 'snapshot.py').is_file() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
sys.path.insert(0, str(ROOT / 'scripts'))
import snapshot

TABLES = {'xmodel': 'fnv1a_xmodels', 'material': 'fnv1a_xmaterials',
          'image': 'fnv1a_ximages', 'xanim': 'fnv1a_xanims',
          'sound_asset': 'fnv1a_xsounds', 'sound_alias': 'fnv1a_soundbanks_aliases'}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    prefix = Path(args.out)
    prefix.parent.mkdir(parents=True, exist_ok=True)

    known = set()
    kind_of = {}
    for kind, table in TABLES.items():
        for n in itertools.chain(snapshot.table_names(table), snapshot.confirmed_names(kind)):
            n = n.strip().lower()
            if n:
                known.add(n)
                kind_of.setdefault(n, kind)

    # template -> {token: set(kinds it was seen wearing)}
    groups = defaultdict(lambda: defaultdict(set))
    rows = []
    for name in sorted(known):
        parts = re.split(r'([^a-z0-9]+)', name)
        repeated = [t for t, count in Counter(parts[::2]).items()
                    if count >= 2 and len(t) >= 2 and not t.isdigit()]
        kind = kind_of.get(name, '?')
        for token in repeated:
            template = tuple('' if i % 2 == 0 and p == token else p
                             for i, p in enumerate(parts))
            groups[template][token].add(kind)
            rows.append((name, parts, token))

    support = Counter()
    cross_kind_pairs = set()
    for template, values in groups.items():
        if 2 <= len(values) <= 100:
            for a, b in itertools.combinations(sorted(values), 2):
                support[a, b] += 1
                if len(values[a] | values[b]) > 1:
                    cross_kind_pairs.add((a, b))

    rules = defaultdict(set)
    for (a, b), count in support.items():
        if count >= 2:
            rules[a].add(b)
            rules[b].add(a)

    outputs = {k: open(str(prefix) + '.' + k + '.txt', 'w', encoding='utf-8', newline='\n')
               for k in ('visual', 'sound')}
    emitted = set()
    rebuilt = 0
    for name, parts, token in rows:
        for other in sorted(rules.get(token, ())):
            candidate = ''.join(other if i % 2 == 0 and p == token else p
                                for i, p in enumerate(parts))
            if candidate in known:
                rebuilt += 1
            else:
                emitted.add((candidate, kind_of.get(name, 'material')))

    for candidate, kind in sorted(emitted):
        target = outputs['sound' if kind.startswith('sound') else 'visual']
        target.write(candidate + '\n')
    for handle in outputs.values():
        handle.close()

    cross_kind_supported = sum(1 for pair in cross_kind_pairs if support[pair] >= 2)
    report = dict(known=len(known), repeated_rows=len(rows),
                  supported_rules=sum(map(len, rules.values())),
                  cross_kind_supported_pairs=cross_kind_supported,
                  rebuilt_known=rebuilt, candidates=len(emitted))
    print(json.dumps(report, indent=2), file=sys.stderr)
    Path(str(prefix) + '.json').write_text(json.dumps(report, indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()
