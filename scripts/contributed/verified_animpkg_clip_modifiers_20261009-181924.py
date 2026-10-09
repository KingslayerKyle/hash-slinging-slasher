"""Recover animation names using the target's per-weapon animation-package modifiers.

Run: python contrib/verified_animpkg_clip_modifiers.py --game BLACKOP7 --out logs/bo7_pkg_clips.txt
Then: bin/windows/confirm_list.exe logs/bo7_pkg_clips.txt --game BLACKOP7 --label "BO7 package-witnessed animation modifier insertions" --script contrib/verified_animpkg_clip_modifiers.py
Reads source-verified package/animation names and the selected modern capture,
with shared game/hash policies, typed history, findings, and open-PR exclusions.
Learns insertion boundary token contexts only when a package modifier occurs in
a target-held clip and removing it reconstructs a known same-weapon clip.
Applies learned contexts to target-held base clips using only modifiers whose
package is also held on target for that weapon. A boundary needs at least three
distinct witnessed clip/base/modifier relations. Writes all candidates, a JSON
diagnostic, and a separate probe-hit list; never writes findings or submits.
Reusable across modern captures. Spent by unchanged verified package/clip names
and target-held insertion evidence; ordinary dictionary widening is not evidence.
Initial 2026-10-09 BO7 measurement: 2,985 held packages, 245 weapon families,
15,159 clip/modifier relations, 1,228,983 candidates, 89 unresolved/unclaimed
probe matches. Normal confirmer and submit determine final findings.
"""
from pathlib import Path
from collections import defaultdict
import argparse
import json
import re
import sys

ROOT = Path(__file__).resolve().parent
while ROOT != ROOT.parent and not (ROOT / 'scripts/snapshot.py').is_file():
    ROOT = ROOT.parent
sys.path.insert(0, str(ROOT / 'scripts'))
import snapshot

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--game', required=True, choices=sorted(snapshot.MODERN))
parser.add_argument('--out', required=True)
args = parser.parse_args()
GAME = args.game
WEAPON = re.compile(r'(?:^|_)(ar|sm|pi|sh|lm|br|dm|sn|me|la|ww|smg|pistol|lmg|dmr|shotgun|sniper|rifle|launcher|melee|special)_(?:p\d+_)?([a-z][a-z0-9]*)_')


def corpus(game):
    names = set(snapshot.table_names('fnv1a_xanims_v2'))
    keys = set()
    for top in ['all_names', 'submissions', 'findings']:
        for path in (ROOT / top).rglob('xanim*.txt'):
            for row in path.read_text(encoding='utf-8').splitlines():
                raw, sep, name = row.partition(',')
                if not sep or not name:
                    continue
                try:
                    key = int(raw, 16) & snapshot.ID_MASK
                except ValueError:
                    continue
                if snapshot.fnv1a(name, game, 'xanim') & snapshot.ID_MASK == key:
                    names.add(name.strip().lower().replace(chr(92), '/'))
                    keys.add(key)
    return {n for n in names if n.isascii() and n == n.strip() and '\n' not in n and '\r' not in n}, keys


def parse(name):
    match = WEAPON.search(name)
    if match is None:
        return None
    return match.group(1, 2), name[:match.end()], tuple(name[match.end():].split('_'))


def context(tokens, at):
    return (tokens[at - 1] if at else '^', tokens[at] if at < len(tokens) else '$')


shot = snapshot.read(ROOT / 'snapshots' / (GAME.lower() + '.ids'))
assert shot.game == GAME
held = {k: set(v) for k, v in shot.by_pool().items() if k in {'xanim', 'animpkg'}}
if 'animpkg' not in held or 'xanim' not in held:
    raise SystemExit('Selected capture has no animation-package/animation census pair')
names, known = corpus(GAME)
known.update(snapshot.known_hashes(game=GAME))
known.update(snapshot.fnv1a(n, GAME, 'xanim') & snapshot.ID_MASK for n in names)
for row in (ROOT / 'state/claimed.txt').read_text().splitlines():
    try:
        known.add(int(row, 16) & snapshot.ID_MASK)
    except ValueError:
        pass
wanted = held['xanim'] - known
modifiers = defaultdict(set)
pkg_held = 0
for name in snapshot.table_names('fnv1a_animpkgs_v2'):
    if snapshot.fnv1a(name, GAME, 'animpkg') & snapshot.ID_MASK not in held['animpkg']:
        continue
    pkg_held += 1
    parsed = parse(name)
    if parsed is None:
        continue
    weapon, head, tokens = parsed
    # Remove only the package type/default markers; preserve every modifier token.
    tokens = tuple(t for t in tokens if t not in {'animpackage', 'default'})
    if tokens:
        modifiers[weapon].add(tokens)
target_clips = []
for name in names:
    parsed = parse(name)
    if parsed and snapshot.fnv1a(name, GAME, 'xanim') & snapshot.ID_MASK in held['xanim']:
        weapon, head, tokens = parsed
        if weapon in modifiers:
            target_clips.append((name, weapon, head, tokens))
contexts = defaultdict(set)
controls = set()
for name, weapon, head, tokens in target_clips:
    for mod in modifiers[weapon]:
        for at in range(len(tokens) - len(mod) + 1):
            if tokens[at:at + len(mod)] != mod:
                continue
            rest = tokens[:at] + tokens[at + len(mod):]
            base = head + '_'.join(rest)
            if base in names and rest:
                frame = context(rest, at)
                contexts[frame].add((name, base, mod))
                controls.add((name, base, mod))
allowed = {frame for frame, witnesses in contexts.items() if len(witnesses) >= 3}
candidates = set()
for name, weapon, head, tokens in target_clips:
    for mod in modifiers[weapon]:
        for at in range(len(tokens) + 1):
            if context(tokens, at) not in allowed:
                continue
            candidate = head + '_'.join(tokens[:at] + mod + tokens[at:])
            if candidate not in names:
                candidates.add(candidate)
hits = {n for n in candidates if snapshot.fnv1a(n, GAME, 'xanim') & snapshot.ID_MASK in wanted}
out = Path(args.out)
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(''.join(n + '\n' for n in sorted(candidates)), encoding='utf-8')
out.with_suffix('.probe_hits.txt').write_text(''.join(n + '\n' for n in sorted(hits)), encoding='utf-8')
report = {'game': GAME, 'known_xanim': len(names), 'wanted_xanim': len(wanted),
          'known_target_packages': pkg_held, 'weapons_with_package_modifiers': len(modifiers),
          'per_weapon_modifiers': sum(map(len, modifiers.values())),
          'distinct_modifier_blocks': len(set().union(*modifiers.values())),
          'target_weapon_clips': len(target_clips), 'known_clip_modifier_relations': len(controls),
          'witnessed_insertion_contexts_min3': len(allowed), 'candidates': len(candidates),
          'unresolved_unclaimed_probe_hits': len(hits)}
out.with_suffix('.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report), flush=True)
