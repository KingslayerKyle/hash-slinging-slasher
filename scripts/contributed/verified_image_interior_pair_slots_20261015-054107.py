"""Offer complete verified image word-pairs to independently witnessed interior slots.

The selected modern capture supplies exact image prefix/suffix frames containing
at least five different complete two-token fillers. Retain at least two prefix
tokens and three suffix tokens, which reaches interior changes beyond the short
terminal byte plans. Each offered pair occurs intact in at least three verified
image names. Tokens are never multiplied independently; frame endpoints stay
correlated. All source spellings must reproduce their database or stored keys.

BO7 2026-10-15: 296,505 verified image names, 96,685 target-held image names,
262 frames and 33,006 complete pairs gave 8,647,572 candidate cells. A read-only
probe reconstructed 2,494 known cells and found three provisionally unclaimed
image keys. All three require two token changes and lie outside the earlier
byte/pair/numeric products. Official image-only confirmation is still required.
Expected chance matches: 0.000000696. Held-out controls exclude their own name
from pair evidence and require five other frame fillers (1,954 controls).

This space consists of 193 tiny exact suffix groups; emitting names or using
the diagnostic probe is cheaper than starting 193 compiled plans. Do not inflate
it into a global prefix x suffix product for GPU utilization.

  python contrib/verified_image_interior_pair_slots_20261015.py --game BLACKOP7 --size
  python contrib/verified_image_interior_pair_slots_20261015.py --game BLACKOP7 \
      --probe --output logs/image-interior-pairs.txt --report logs/image-interior-pairs.json
  confirm_list logs/image-interior-pairs.txt --game BLACKOP7 \
      --script contrib/verified_image_interior_pair_slots_20261015.py \
      --label "verified complete image pairs in witnessed interior frames"

Select only image in the confirmer. --probe rehashes candidates and writes only
unclaimed capture matches for subsequent standard confirmation; its report keeps
the full attempted cell count. This tool never writes findings, config or claims.
Without --probe it emits the complete candidate space. Spent by unchanged source
vocabulary, exact frames and selected capture. No autonomous repetition.
"""
import argparse
from collections import defaultdict
import hashlib
import json
import multiprocessing
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

WORD = re.compile(r'[a-z]{3,}')
MASK = snapshot.ID_MASK
PRIME = snapshot.PRIME


def verified_stored_name(name, key, game):
    """Keep canonical source bytes and recheck exactly the spelling returned.

    >>> key = snapshot.fnv1a('img_brown_wood', 'BLACKOP7', 'image') & MASK
    >>> verified_stored_name(' img_brown_wood', key, 'BLACKOP7') is None
    True
    >>> verified_stored_name('IMG_BROWN_WOOD', key, 'BLACKOP7')
    'img_brown_wood'
    >>> verified_stored_name('img_brown_rock', key, 'BLACKOP7') is None
    True
    """
    if not name or not name.isascii() or name != name.strip():
        return None
    normalized = name.lower()
    if snapshot.fnv1a(normalized, game, 'image') & MASK != key:
        return None
    return normalized


def corpus(game):
    names = set(snapshot.table_names('fnv1a_ximages_v2'))
    stored = set()
    for top in ('all_names', 'submissions', 'findings'):
        for path in (ROOT / top).rglob('image*.txt'):
            for row in path.read_text(encoding='utf-8').splitlines():
                raw, sep, name = row.partition(',')
                if not sep or not name:
                    continue
                try:
                    key = int(raw, 16) & MASK
                except ValueError:
                    continue
                stored.add(key)
                verified = verified_stored_name(name, key, game)
                if verified is not None:
                    names.add(verified)
    return {n for n in names if n and n.isascii() and n == n.strip()
            and '\n' not in n and '\r' not in n}, stored


def learn(names, target):
    """Learn correlated frames and complete vocabulary with explicit controls.

    >>> names = {'img_fam_' + pair + '_part_layer_color' for pair in
    ...          ('brown_wood', 'green_moss', 'white_rock', 'black_steel', 'clear_glass')}
    >>> frames, vocabulary, controls = learn(names, names)
    >>> len(frames), 'brown_wood' in vocabulary, len(controls)
    (1, False, 0)
    >>> extra = {'src_' + str(i) + '_' + pair for i in range(3) for pair in
    ...          ('brown_wood', 'green_moss', 'white_rock', 'black_steel', 'clear_glass')}
    >>> frames, vocabulary, controls = learn(names | extra, names)
    >>> ('img_fam_', '_part_layer_color') in frames
    True
    >>> 'brown_wood' in vocabulary and 'brown_moss' not in vocabulary
    True
    >>> len(controls)  # A five-filler frame cannot reconstruct its own held-out fifth.
    0
    >>> names.add('img_fam_red_clay_part_layer_color')
    >>> len(learn(names | extra, names)[2])
    5
    """
    pair_sources = defaultdict(set)
    for name in names:
        tokens = name.split('_')
        for i in range(len(tokens) - 1):
            if WORD.fullmatch(tokens[i]) and WORD.fullmatch(tokens[i + 1]):
                pair_sources['_'.join(tokens[i:i + 2])].add(name)
    vocabulary = {pair for pair, sources in pair_sources.items() if len(sources) >= 3}
    frames = defaultdict(set)
    for name in target:
        tokens = name.split('_')
        if not all(t and t.isascii() and t.isalnum() for t in tokens):
            continue
        for i in range(2, len(tokens) - 4):
            if WORD.fullmatch(tokens[i]) and WORD.fullmatch(tokens[i + 1]):
                frames['_'.join(tokens[:i]) + '_', '_' + '_'.join(tokens[i + 2:])].add(
                    '_'.join(tokens[i:i + 2]))
    frames = {frame: pairs for frame, pairs in frames.items() if len(pairs) >= 5}
    controls = set()
    for (prefix, suffix), pairs in frames.items():
        if len(pairs) >= 6:
            for pair in pairs & vocabulary:
                name = prefix + pair + suffix
                if len(pair_sources[pair] - {name}) >= 3:
                    controls.add(name)
    return frames, vocabulary, controls


def initialize(game, held, excluded, vocabulary):
    global GAME, HELD, EXCLUDED, VOCABULARY
    GAME, HELD, EXCLUDED, VOCABULARY = game, held, excluded, vocabulary


def probe_frame(frame):
    prefix, suffix = frame
    start = snapshot.fnv1a(prefix, GAME, 'image') & MASK
    suffix_bytes = suffix.encode('ascii')
    found, known = {}, 0
    for pair in VOCABULARY:
        value = start
        for byte in pair.encode('ascii'):
            value = ((value ^ byte) * PRIME) & MASK
        for byte in suffix_bytes:
            value = ((value ^ byte) * PRIME) & MASK
        if value not in HELD:
            continue
        if value in EXCLUDED:
            known += 1
            continue
        name = prefix + pair + suffix
        full = snapshot.fnv1a(name, GAME, 'image')
        if full & MASK != value:
            raise ValueError('Complete name rehash disagrees with incremental candidate hash')
        found[name] = full
    return found, known


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--game', required=True, choices=sorted(snapshot.MODERN))
    ap.add_argument('--size', action='store_true')
    ap.add_argument('--probe', action='store_true')
    ap.add_argument('--workers', type=int, default=4)
    ap.add_argument('--output', type=Path)
    ap.add_argument('--report', type=Path)
    args = ap.parse_args()
    if not 1 <= args.workers <= 16:
        ap.error('--workers must be between 1 and 16')
    started = time.monotonic()
    capture_path = ROOT / 'snapshots' / (args.game.lower() + '.ids')
    capture = snapshot.read(capture_path)
    if capture.game != args.game:
        raise ValueError('Capture game differs from selected game')
    held = set(capture.by_pool()['image'])
    names, stored = corpus(args.game)
    target = {n for n in names if snapshot.fnv1a(n, args.game, 'image') & MASK in held}
    frames, vocabulary, controls = learn(names, target)
    count = len(frames) * len(vocabulary)
    digest = lambda values: hashlib.sha256(('\n'.join(sorted(values)) + '\n').encode()).hexdigest()
    report = {'game': args.game, 'kind': 'image', 'verified_image_names': len(names),
              'target_held_image_names': len(target), 'complete_pair_vocabulary': len(vocabulary),
              'eligible_frames': len(frames), 'candidate_cells': count,
              'independent_controls': len(controls), 'capture_sha256': hashlib.sha256(capture_path.read_bytes()).hexdigest(),
              'verified_corpus_sha256': digest(names), 'vocabulary_sha256': digest(vocabulary),
              'frames_sha256': digest(a + '\t' + b for a, b in frames)}
    if args.size:
        print(json.dumps(report, sort_keys=True))
        return
    if args.probe:
        excluded = stored | {k & MASK for k in snapshot.known_hashes(game=args.game)}
        claims = ROOT / 'state/claimed.txt'
        if claims.is_file():
            for row in claims.read_text(encoding='utf-8').splitlines():
                try:
                    excluded.add(int(row, 16) & MASK)
                except ValueError:
                    pass
        found, known = {}, 0
        with multiprocessing.get_context('spawn').Pool(args.workers, initializer=initialize,
                initargs=(args.game, held, excluded, sorted(vocabulary))) as pool:
            for batch, seen in pool.imap_unordered(probe_frame, sorted(frames)):
                found.update(batch)
                known += seen
        report.update({'known_match_cells': known, 'fresh_names': len(found),
                       'unclaimed_target_keys': len(held - excluded),
                       'chance_hit_expectation': count * len(held - excluded) / (1 << 63)})
        candidates = iter(sorted(found))
    else:
        candidates = (a + pair + b for a, b in sorted(frames) for pair in sorted(vocabulary))
    output = args.output.open('w', encoding='utf-8', newline='\n') if args.output else sys.stdout
    try:
        for name in candidates:
            output.write(name + '\n')
    finally:
        if args.output:
            output.close()
    report['seconds'] = round(time.monotonic() - started, 3)
    if args.report:
        args.report.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, sort_keys=True), file=sys.stderr)


if __name__ == '__main__':
    main()
