"""Translate material directories and complete endings as correlated pairs.

Two original BO7-held material names may share an intact basename body but use
different literal directories AND different complete endings. Learn that joint
translation only from three disjoint original name pairs. Preserve zero, one or
two leading basename tokens, one to three ending tokens, and at least three body
tokens. Do not independently cross directory and ending alphabets. Descendants
are application vocabulary only: the explicit baseline must remain a subset of
verified public table spellings and cannot include local findings.

BO7 2026-10-15: 161,718 independent source names, 181,651 application names,
12,908 directed translations, 14,052 independent held-out controls and 2,328,253
unseen candidates. A separate read-only probe found 11 provisional material keys;
official material-only confirmation and submission remain authoritative. This
small irregular relation belongs in confirm_list rather than enlarged products.

  python contrib/verified_material_directory_tail.py --game BLACKOP7 \
    --baseline logs/material-baseline.csv --application logs/material-application.csv \
    --output logs/material-candidates.txt --report logs/material-report.json
  confirm_list logs/material-candidates.txt --game BLACKOP7 \
    --script contrib/verified_material_directory_tail.py

Both baseline and application are explicitly keyed CSV: hash,complete raw name.
Only the FIRST comma separates the key; commas inside names are preserved.
--exclude-file inputs are explicitly RAW name lists and are never comma-split.
--size computes the candidate count without writing candidate names. Reads the
selected capture, current verified material table and local findings to validate
inputs. Writes only requested diagnostics/candidates; never settings or findings.
Reusable with genuinely new independent sources/application names. Spent by its
frozen baseline, application and prior candidate spaces; no autonomous repetition.
"""
import argparse
from collections import defaultdict
from itertools import combinations
import hashlib
import json
from pathlib import Path
import re
import sys
import time

ROOT = next((p for p in [Path.cwd(), *Path(__file__).resolve().parents]
             if (p / 'scripts/snapshot.py').is_file()), None)
if ROOT is None:
    raise SystemExit('Run inside a solver checkout')
sys.path.insert(0, str(ROOT / 'scripts'))
import snapshot


def parse_keyed_row(row, game):
    """Verify exact input bytes, then separately verify returned normalization.

    >>> name = 'mc/mtl_sample,layer_color'
    >>> key = snapshot.fnv1a(name, 'BLACKOP7', 'material')
    >>> parse_keyed_row(f'{key:x},{name}', 'BLACKOP7')[1] == name
    True
    >>> parse_keyed_row(f'{key:x},{name.upper()}', 'BLACKOP7')[1] == name
    True
    >>> parse_keyed_row(f'{key:x}, {name}', 'BLACKOP7') is None
    True
    >>> parse_keyed_row(f'{key:x},{name}_wrong', 'BLACKOP7') is None
    True
    >>> raw_names(['mc/mtl_sample,layer_color']) == {name}
    True
    """
    raw, sep, name = row.partition(',')
    if not sep or not re.fullmatch(r'(?:0x)?[0-9a-fA-F]{1,16}', raw):
        return None
    if not name or name != name.strip() or not name.isascii():
        return None
    key = int(raw, 16) & snapshot.ID_MASK
    if snapshot.fnv1a(name, game, 'material') & snapshot.ID_MASK != key:
        return None
    normalized = name.lower()
    if snapshot.fnv1a(normalized, game, 'material') & snapshot.ID_MASK != key:
        return None
    return key, normalized


def read_keyed(path, held, game):
    names = set()
    for index, row in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
        if not row:
            continue
        parsed = parse_keyed_row(row, game)
        if parsed is None or parsed[0] not in held:
            raise ValueError(f'{path}:{index}: invalid source key, spelling or material capture membership')
        names.add(parsed[1])
    return names


def raw_names(rows):
    """Explicit raw-name lists preserve every literal comma."""
    names = set()
    for row in rows:
        if not row:
            continue
        if row != row.strip() or not row.isascii():
            raise ValueError('Raw exclusion names must be canonical ASCII without outer whitespace')
        names.add(row.lower())
    return names


def independent(pairs, exclude=()):
    """Copies of one source pair never count as independent evidence.

    >>> len(independent([('a', 'b'), ('a', 'c'), ('d', 'e'), ('f', 'g')]))
    3
    >>> len(independent([('a', 'b'), ('d', 'e'), ('f', 'g')], ('a', 'b')))
    2
    """
    used, out = set(exclude), []
    for pair in sorted(pairs):
        if not used.intersection(pair):
            out.append(pair)
            used.update(pair)
    return out


def split_name(name):
    directory, slash, base = name.rpartition('/')
    tokens = tuple(base.split('_'))
    if not slash or not all(t.isascii() and t.isalnum() for t in tokens):
        return None
    return directory + slash, tokens


def cuts(name):
    parsed = split_name(name)
    if parsed is None:
        return
    directory, tokens = parsed
    for left in (0, 1, 2):
        for right in (1, 2, 3):
            if len(tokens) - left - right >= 3:
                yield (directory, tokens[:left], tokens[-right:]), tokens[left:-right]


def learn(training):
    frames = defaultdict(dict)
    for name in sorted(training):
        for wrapper, body in cuts(name):
            frames[wrapper[1], body][wrapper] = name
    supports = defaultdict(set)
    for wrappers in frames.values():
        if not 2 <= len(wrappers) <= 32:
            continue
        for a, b in combinations(sorted(wrappers), 2):
            if a[0] != b[0] and a[2] != b[2]:
                supports[a, b].add(tuple(sorted((wrappers[a], wrappers[b]))))
    rules = defaultdict(dict)
    for (a, b), pairs in supports.items():
        if len(independent(pairs)) >= 3:
            rules[a][b] = pairs
            rules[b][a] = pairs
    return rules, len(frames), len(supports)


def generate(training, application):
    """Apply each whole joint translation; neither half alone is offered.

    >>> training = {d + 'head_' + core + '_' + tail for core in
    ...     ('birch_wood_plank', 'brown_stone_block', 'black_metal_panel', 'green_moss_floor')
    ...     for d, tail in (('mc/', 'color'), ('wc/', 'normal'))}
    >>> application = training | {'mc/head_clear_glass_window_color'}
    >>> candidates, report, rules = generate(training, application)
    >>> 'wc/head_clear_glass_window_normal' in candidates
    True
    >>> 'wc/head_clear_glass_window_color' in candidates
    False
    >>> 'mc/head_clear_glass_window_normal' in candidates
    False
    >>> report['independent_controls'] > 0
    True
    >>> reduced = {n for n in training if not 'green_moss_floor' in n}
    >>> generate(reduced, reduced)[1]['independent_controls']
    0
    """
    rules, frame_count, observed = learn(training)
    candidates, controls = set(), set()
    for name in sorted(application):
        for a, body in cuts(name):
            for b, pairs in rules.get(a, {}).items():
                candidate = b[0] + '_'.join(b[1] + body + b[2])
                if candidate in application:
                    if candidate in training and len(independent(pairs, (name, candidate))) >= 3:
                        controls.add(candidate)
                else:
                    candidates.add(candidate)
    return candidates, {'frames': frame_count, 'observed_rules': observed,
        'eligible_directed_rules': sum(map(len, rules.values())),
        'independent_controls': len(controls)}, rules


def digest_names(names):
    return hashlib.sha256(('\n'.join(sorted(names)) + '\n').encode()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--game', required=True, choices=sorted(snapshot.MODERN))
    parser.add_argument('--baseline', type=Path, required=True)
    parser.add_argument('--application', type=Path, required=True)
    parser.add_argument('--exclude-file', type=Path, action='append', default=[])
    parser.add_argument('--output', type=Path)
    parser.add_argument('--report', type=Path)
    parser.add_argument('--provenance', type=Path)
    parser.add_argument('--size', action='store_true')
    args = parser.parse_args()
    started = time.monotonic()
    capture_path = ROOT / 'snapshots' / (args.game.lower() + '.ids')
    capture = snapshot.read(capture_path)
    if capture.game != args.game:
        raise ValueError('Capture game differs from requested game')
    held = set(capture.by_pool()['material'])
    training = read_keyed(args.baseline, held, args.game)
    application = read_keyed(args.application, held, args.game)
    public = {n.lower() for n in snapshot.table_names('fnv1a_xmaterials_v2')
              if n and n.isascii() and n == n.strip()}
    if training - public:
        raise ValueError('Baseline contains names not independently verified by the public material table')
    local = set()
    for path in (ROOT / 'findings').rglob('material*.txt'):
        for row in path.read_text(encoding='utf-8').splitlines():
            parsed = parse_keyed_row(row, args.game)
            if parsed:
                local.add(parsed[1])
    if training & local:
        raise ValueError('Baseline contains local descendants; keep them application-only')
    if not training <= application:
        raise ValueError('Application must include the frozen baseline')
    candidates, report, rules = generate(training, application)
    report.update(game=args.game, kind='material', independent_training_names=len(training),
        held_application_names=len(application), training_sha256=digest_names(training),
        application_sha256=digest_names(application), candidates_before_prior_exclusion=len(candidates),
        capture_sha256=hashlib.sha256(capture_path.read_bytes()).hexdigest())
    overlap = {}
    for path in args.exclude_file:
        earlier = raw_names(path.read_text(encoding='utf-8').splitlines())
        overlap[str(path)] = len(candidates & earlier)
        candidates.difference_update(earlier)
    report.update(prior_candidate_overlap=overlap, candidates=len(candidates),
        candidate_sha256=digest_names(candidates), seconds=round(time.monotonic()-started, 3),
        input_sha256={str(p): hashlib.sha256(p.read_bytes()).hexdigest()
                      for p in [args.baseline, args.application, *args.exclude_file]})
    if args.provenance:
        evidence = [{'from': a, 'to': b, 'independent_witnesses': independent(pairs)[:3]}
                    for a in sorted(rules) for b, pairs in sorted(rules[a].items())]
        args.provenance.write_text(json.dumps(evidence, indent=2)+'\n', encoding='utf-8')
    if args.report:
        args.report.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    if not args.size:
        handle = args.output.open('w', encoding='utf-8', newline='\n') if args.output else sys.stdout
        try:
            for name in sorted(candidates):
                handle.write(name + '\n')
        finally:
            if args.output:
                handle.close()
    print(json.dumps(report, sort_keys=True), file=sys.stderr)


if __name__ == '__main__':
    main()
