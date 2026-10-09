"""Solve a modern image byte before a witnessed channel/decorative suffix.

An image ending in _lbm1 or _lbm1_dmg hides version or part bytes before that
suffix from ordinary final-byte searches. Learn suffixes from target-held
images: at least three distinct cores must witness a suffix, and each core
must have sibling endings at that same cut. Retain one- and two-token suffixes.
Peel those suffixes, solve one prefix byte, and verify the complete normalized
modern image hash against unresolved unclaimed image IDs. No models searched.
Suffixes share a reversed trie. Arithmetic modulo 2^63 covers both possible
full-hash top bits once; every complete name is still rehashed at full width.
"""
import argparse
from collections import defaultdict
import json
import multiprocessing
import os
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent
while ROOT != ROOT.parent and not (ROOT / 'scripts/snapshot.py').is_file():
    ROOT = ROOT.parent
if not (ROOT / 'scripts/snapshot.py').is_file():
    ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / 'scripts'))
import snapshot

MASK = (1 << 64) - 1
TOP = 1 << 63
INVERSE = pow(snapshot.PRIME, -1, 1 << 64)
TOKEN = re.compile(r'[a-z0-9]{1,16}')


def corpus(kind, game):
    assert kind == 'image'
    names = set(snapshot.table_names('fnv1a_ximages_v2'))
    for top in ['all_names', 'submissions', 'findings']:
        for path in (ROOT / top).rglob('image*.txt'):
            for row in path.read_text(encoding='utf-8').splitlines():
                raw, sep, name = row.partition(',')
                if not sep or not name:
                    continue
                try:
                    key = int(raw, 16) & snapshot.ID_MASK
                except ValueError:
                    continue
                if snapshot.fnv1a(name, game, 'image') & snapshot.ID_MASK == key:
                    names.add(name.strip().lower())
    return {n for n in names if n.isascii() and n == n.strip() and '\n' not in n and '\r' not in n}


def cuts(name):
    parts = name.split('_')
    for depth in [1, 2]:
        if len(parts) <= depth or not all(TOKEN.fullmatch(t) for t in parts[-depth:]):
            continue
        tail = '_' + '_'.join(parts[-depth:])
        stem = name[:-len(tail)]
        if len(stem) > 1 and stem[-1].isalnum():
            yield depth, stem, tail


def target_tails(names, held, game):
    siblings = defaultdict(set)
    for name in names:
        if snapshot.fnv1a(name, game, 'image') & snapshot.ID_MASK in held:
            for depth, stem, tail in cuts(name):
                siblings[depth, stem].add(tail)
    witnesses = defaultdict(set)
    for (depth, stem), tails in siblings.items():
        if len(tails) >= 2:
            for tail in tails:
                witnesses[tail].add(stem)
    return {tail for tail, stems in witnesses.items() if len(stems) >= 3}


def wanted(held, names, known, game, kind):
    assert kind == 'image'
    excluded = {key & snapshot.ID_MASK for key in known}
    excluded.update(snapshot.fnv1a(n, game, kind) & snapshot.ID_MASK for n in names)
    return {key & snapshot.ID_MASK for key in held} - excluded


def prefixes(names, tails):
    return {stem[:-1] for name in names for _, stem, tail in cuts(name) if tail in tails}


def suffix_trie(tails):
    nodes = [(0, 0, None)]
    edges = {}
    for tail in sorted(tails):
        parent = 0
        for byte in reversed(tail.lower().encode('ascii')):
            edge = parent, byte
            if edge not in edges:
                edges[edge] = len(nodes)
                nodes.append((parent, byte, None))
            parent = edges[edge]
        before, byte, _ = nodes[parent]
        nodes[parent] = before, byte, tail
    return nodes


def solve_chunk(ids, buckets, steps, names, game, node_count):
    found = {}
    id_mask = snapshot.ID_MASK
    values = [0] * node_count
    for key in ids:
        key &= id_mask
        values[0] = key
        for index, (parent, byte, tail) in steps:
            value = ((values[parent] * INVERSE) & id_mask) ^ byte
            values[index] = value
            if tail is None:
                continue
            scaled = (value * INVERSE) & id_mask
            for prefix_hash, beginning in buckets.get(scaled >> 8, ()):
                unknown = scaled ^ prefix_hash
                if not 33 <= unknown <= 126:
                    continue
                name = beginning + chr(unknown) + tail
                if name in names:
                    continue
                full = snapshot.fnv1a(name, game, 'image')
                if full & snapshot.ID_MASK == key:
                    found[name] = full
    return found


def worker_init(buckets, steps, names, game, node_count):
    global WORKER_INPUT
    WORKER_INPUT = buckets, steps, names, game, node_count


def worker_chunk(ids):
    return solve_chunk(ids, *WORKER_INPUT)


def solve(names, ids, tails, game, workers=1):
    buckets = defaultdict(list)
    for beginning in prefixes(names, tails):
        value = snapshot.fnv1a(beginning, game, 'image') & snapshot.ID_MASK
        buckets[value >> 8].append((value, beginning))
    nodes = suffix_trie(tails)
    steps = list(enumerate(nodes[1:], 1))
    if workers == 1 or not ids:
        return solve_chunk(ids, buckets, steps, names, game, len(nodes))
    keys = sorted(ids)
    chunks = [keys[i::workers] for i in range(workers)]
    found = {}
    with multiprocessing.get_context('spawn').Pool(
            workers, initializer=worker_init,
            initargs=(buckets, steps, names, game, len(nodes))) as pool:
        for batch in pool.imap_unordered(worker_chunk, chunks):
            found.update(batch)
    return found


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--game', required=True, choices=sorted(snapshot.MODERN))
    parser.add_argument('--kind', choices=['image'], default='image')
    parser.add_argument('--profile', action='store_true')
    parser.add_argument('--workers', type=int, default=min(8, os.cpu_count() or 1))
    args = parser.parse_args()
    if not 1 <= args.workers <= 16:
        parser.error('--workers must be between 1 and 16')
    shot = snapshot.read(ROOT / 'snapshots' / (args.game.lower() + '.ids'))
    assert shot.game == args.game
    names = corpus('image', args.game)
    held = set(shot.by_pool()['image'])
    tails = target_tails(names, held, args.game)
    known = snapshot.known_hashes(game=args.game)
    path = ROOT / 'state/claimed.txt'
    if path.is_file():
        for raw in path.read_text(encoding='utf-8').splitlines():
            try:
                known.add(int(raw, 16) & snapshot.ID_MASK)
            except ValueError:
                continue
    ids = wanted(held, names, known, args.game, 'image')
    report = {'game': args.game, 'kind': 'image', 'verified_seed_names': len(names),
              'workers': args.workers,
              'witnessed_target_suffixes': len(tails), 'original_prefixes': len(prefixes(names, tails)),
              'unresolved_unclaimed_image_ids': len(ids),
              'reverse_hash_queries': len(tails) * len(ids),
              'shared_reverse_byte_operations': (len(suffix_trie(tails)) - 1) * len(ids)}
    if args.profile:
        print(json.dumps(report), file=sys.stderr)
        return
    print(json.dumps(report), file=sys.stderr)
    found = solve(names, ids, tails, args.game, args.workers)
    report['solved'] = len(found)
    print(json.dumps(report), file=sys.stderr)
    for name in sorted(found):
        print(name)


if __name__ == '__main__':
    main()
