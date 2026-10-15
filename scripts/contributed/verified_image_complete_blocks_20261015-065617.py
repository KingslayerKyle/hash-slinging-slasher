"""Generate source-witnessed BO7 complete six-byte image-block plan factors.

Each middle factor is a complete observed six-byte block, possibly crossing an
underscore, never a product of character alphabets. Blocks require three distinct
independent target-held source cores. Endings contain one or two underscore tokens
and require three distinct cores with two different sibling endings at the SAME
cut depth. Verified public/history names supply application beginnings; generated
local names are excluded from rule training. All inputs are image-specific.

Generation works without the original private factor files:
  python contrib/verified_image_complete_blocks_20261015.py --size
  python contrib/verified_image_complete_blocks_20261015.py --output-dir logs/image-blocks
  bin/windows/confirm_plan.exe logs/image-blocks/plan.txt --size

Select ONLY image in the confirmer configuration before running the plan. The
plan runner has no --script option: submit automatically carries this generator
from contrib/ into scripts/contributed/. This generator never runs a search or
changes settings, findings or claims. Run start before any subsequent confirmation.

By default, use the pinned public image table revision, the installed BO7 capture,
and hash-verified local image history. --source-table accepts an explicit public
fnv1a_ximages_v2 CSV instead. --application-keyed and --exclude-training-keyed
accept explicit hexhash,name files; only the first comma separates columns.
--no-local-history disables history discovery for portable explicit-input replay.
--exclude-keyed removes verified names globally before deriving factors (e.g. a
new run whose descendants must not enter a replay). --save-inputs exports keyed
application/exclusion files. --size derives and validates but writes nothing.

Optional --frozen-dir compares regenerated factor sets, training and controls
with a previous measurement.json plus begin/stem/end.txt. It is not required for
generation. When comparing, factor output preserves the exact frozen file bytes
only AFTER independently regenerating and verifying all sets and source witnesses.

The original Oct15 BO7 run had 72,789 beginnings x 3,506 complete blocks x 6,193
endings including the engine's empty ending: 1,580,442,663,162 cells. Its 45,527
controls are independent source-known names, NOT a held-out split. Recorded aligned
overlap with seven earlier pair products was 644,876,782 cells; alternate ending
decompositions and missing historical methods were not proved disjoint. Expected
chance matches then: 0.12723. Actual hits require typed hash validation, current
exclusions and source-specific provenance review. Spent by the exact input factors;
do not rerun unchanged inputs or treat new matches as independent rule evidence.
"""
import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import time

ROOT = next((p for p in [Path.cwd(), *Path(__file__).resolve().parents]
             if (p / 'scripts/snapshot.py').is_file()), None)
if ROOT is None:
    raise SystemExit('Run inside a solver checkout')
sys.path.insert(0, str(ROOT / 'scripts'))
import snapshot


def table_checkout():
    """Use the configured table checkout when pinned Git history is required."""
    folder = Path(snapshot.settings.tables_csv()).resolve()
    for candidate in (folder, folder.parent, ROOT / 'cod-name-db'):
        if (candidate / '.git').exists() and (candidate / 'csv').is_dir():
            return candidate
    raise ValueError('Pinned source revisions require a cod-name-db Git checkout; '
                     'configure tables in config.toml and fetch its history first')

SOURCE_COMMIT = '3d42c005d5405af8b225958bef09a041e9ada0be'
TABLE = 'fnv1a_ximages_v2'
GAME = 'BLACKOP7'
WIDTH = 6
MASK = snapshot.ID_MASK
TOKEN = re.compile('[a-z0-9]{1,16}')
BLOCK = re.compile('[a-z0-9_]{6}')


def digest(values):
    return hashlib.sha256(('\n'.join(sorted(values))+'\n').encode()).hexdigest()


def read_factors(path):
    """Explicit count/name rows preserve all commas in the factor spelling."""
    result = set()
    for number, row in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
        if not row or row.startswith('#'):
            continue
        raw, sep, name = row.partition(',')
        if not sep or raw != '0' or not name or not name.isascii() or name != name.strip().lower():
            raise ValueError(f'{path}:{number}: expected canonical explicit 0,name factor')
        result.add(name)
    return result


def verified_row(row):
    """Hash exact supplied spelling and returned normalization separately.

    >>> name = 'sample,part_image_color'
    >>> key = snapshot.fnv1a(name, GAME, 'image')
    >>> verified_row(f'{key:x},{name}') == name
    True
    >>> verified_row(f'{key:x},{name.upper()}') == name
    True
    >>> verified_row(f'{key:x}, {name}') is None
    True
    >>> verified_row(f'{key:x},{name}_wrong') is None
    True
    >>> verified_row('0,not_a_verified_source') is None
    True
    """
    raw, sep, name = row.partition(',')
    if not sep or not name or not name.isascii() or name != name.strip():
        return None
    try:
        key = int(raw, 16) & MASK
    except ValueError:
        return None
    if snapshot.fnv1a(name, GAME, 'image') & MASK != key:
        return None
    normalized = name.lower()
    if snapshot.fnv1a(normalized, GAME, 'image') & MASK != key:
        return None
    return normalized


def read_keyed(path, inputs, strict=True):
    data = path.read_bytes()
    inputs[str(path.resolve())] = hashlib.sha256(data).hexdigest()
    names = set()
    for number, row in enumerate(data.decode('utf-8').splitlines(), 1):
        if not row:
            continue
        name = verified_row(row)
        if name is not None:
            names.add(name)
        elif strict:
            raise ValueError(f'{path}:{number}: invalid image hash/name row')
    return names


def cuts(name):
    """Return literal endings and preserve their one/two-token cut depth.

    >>> list(cuts('prefix_core_red_01'))
    [(1, 'prefix_core_red', '_01'), (2, 'prefix_core', '_red_01')]
    """
    words = name.split('_')
    for depth in (1, 2):
        if len(words) <= depth or not all(TOKEN.fullmatch(t) for t in words[-depth:]):
            continue
        tail = '_' + '_'.join(words[-depth:])
        yield depth, name[:-len(tail)], tail


def eligible(core):
    """Whole observed blocks can span a real underscore boundary.

    >>> eligible('texture_body01')
    True
    >>> eligible('texture_red_01')
    True
    >>> eligible('red_01')  # A nonempty source beginning is required.
    False
    >>> eligible('texture_red_0_')
    False
    """
    return len(core) > WIDTH and core[-1].isalnum() and BLOCK.fullmatch(core[-WIDTH:]) is not None


def write_keyed(path, names):
    with path.open('w', encoding='utf-8', newline='\n') as stream:
        for name in sorted(names):
            stream.write(f'{snapshot.fnv1a(name, GAME, "image") & MASK:016x},{name}\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--source-rev', default=SOURCE_COMMIT)
    parser.add_argument('--source-table', type=Path, help='explicit public fnv1a_ximages_v2 CSV')
    parser.add_argument('--capture', type=Path, default=ROOT / 'snapshots/blackop7.ids')
    parser.add_argument('--application-keyed', type=Path, action='append', default=[])
    parser.add_argument('--exclude-training-keyed', type=Path, action='append', default=[])
    parser.add_argument('--exclude-keyed', type=Path, action='append', default=[])
    parser.add_argument('--no-local-history', action='store_true')
    parser.add_argument('--save-inputs', action='store_true')
    parser.add_argument('--frozen-dir', type=Path, help='optional exact factor/training replay comparison')
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'logs/image-complete-blocks')
    parser.add_argument('--size', action='store_true')
    args = parser.parse_args()
    started = time.monotonic()
    if args.frozen_dir and args.output_dir.resolve() == args.frozen_dir.resolve():
        raise ValueError('Output must not overwrite frozen input')
    capture = snapshot.read(args.capture)
    if capture.game != GAME:
        raise ValueError('Expected a BLACKOP7 capture')
    held = set(capture.by_pool()['image'])
    if args.source_table:
        data = args.source_table.read_bytes()
    else:
        try:
            data = subprocess.check_output(['git', '-C', str(table_checkout()), 'show',
                                            args.source_rev + ':csv/' + TABLE + '.csv'])
        except subprocess.CalledProcessError as exc:
            raise SystemExit('Pinned table unavailable: fetch cod-name-db history or pass --source-table with a verified public image CSV') from exc
    public = {n for n in snapshot.database_names(TABLE, data.decode('utf-8').splitlines())
              if n.isascii() and n == n.strip().lower()}
    application, generated = set(public), set()
    source_inputs = {}
    if not args.no_local_history:
        for top in ('all_names', 'submissions', 'findings'):
            for path in (Path(snapshot.settings.path('findings', 'findings')) if top == 'findings' else ROOT / top).rglob('image*.txt'):
                names = read_keyed(path, source_inputs, strict=False)
                application.update(names)
                if top == 'findings':
                    generated.update(names)
    for path in args.application_keyed:
        application.update(read_keyed(path, source_inputs))
    for path in args.exclude_training_keyed:
        generated.update(read_keyed(path, source_inputs))
    excluded = set()
    for path in args.exclude_keyed:
        excluded.update(read_keyed(path, source_inputs))
    application.difference_update(excluded)
    generated.difference_update(excluded)
    training = {n for n in public if n not in generated and n not in excluded
                and snapshot.fnv1a(n, GAME, 'image') & MASK in held}

    families = defaultdict(set)
    for name in training:
        for depth, core, tail in cuts(name):
            families[depth, core].add(tail)
    tail_cores = defaultdict(set)
    for (depth, core), tails in families.items():
        if len(tails) >= 2:
            for tail in tails:
                tail_cores[tail].add(core)
    ends = {tail for tail, cores in tail_cores.items() if len(cores) >= 3}
    block_cores = defaultdict(set)
    for name in training:
        for depth, core, tail in cuts(name):
            if tail in ends and eligible(core):
                block_cores[core[-WIDTH:]].add(core)
    blocks = {b for b, cores in block_cores.items() if len(cores) >= 3}
    beginning_sources = {}
    for name in sorted(application):
        for depth, core, tail in cuts(name):
            if tail in ends and eligible(core):
                beginning_sources.setdefault(core[:-WIDTH], name)
    begins = set(beginning_sources)
    factors = {'begin': begins, 'stem': blocks, 'end': ends}
    cells = len(begins)*len(blocks)*(len(ends)+1)
    controls = set()
    for name in training:
        for depth, core, tail in cuts(name):
            if tail in ends and len(core)>WIDTH and core[:-WIDTH] in begins and core[-WIDTH:] in blocks:
                if len(block_cores[core[-WIDTH:]]-{core})>=3 and len(tail_cores[tail]-{core})>=3:
                    controls.add(name)
    hashes = {'training': digest(training), **{role: digest(values) for role, values in factors.items()}}
    frozen = None
    if args.frozen_dir:
        frozen = json.loads((args.frozen_dir/'measurement.json').read_text(encoding='utf-8'))
        if (frozen['game'], frozen['kind'], frozen['block_width']) != (GAME, 'image', WIDTH):
            raise ValueError('Frozen measurement uses another method/game/type')
        for role, values in factors.items():
            if read_factors(args.frozen_dir/(role+'.txt')) != values:
                raise ValueError('Regenerated factors differ from frozen ' + role)
        if frozen['sha256'] != hashes:
            raise ValueError('Regenerated factor/training digests differ')
        if frozen['candidate_cells'] != cells or frozen['independent_known_controls'] != len(controls):
            raise ValueError('Frozen cells or independent source-known controls differ')
        if frozen['source_application_names'] != len(application):
            raise ValueError('Frozen application corpus count differs')

    block_evidence = {}
    for block in sorted(blocks):
        examples = []
        for core in sorted(block_cores[block])[:3]:
            source = next(core+tail for depth in (1,2) for tail in sorted(families.get((depth,core),()))
                          if tail in ends and core+tail in training)
            examples.append({'core': core, 'source': source})
        block_evidence[block] = examples
    tail_evidence = {}
    for tail in sorted(ends):
        depth = tail.count('_')
        tail_evidence[tail] = [{'core': core, 'sources': [core+tail, core+next(t for t in sorted(families[depth,core]) if t != tail)]}
                               for core in sorted(tail_cores[tail])[:3]]
    report = {'game': GAME, 'kind': 'image', 'block_width': WIDTH,
        'source_names': len(public), 'source_application_names': len(application),
        'independent_target_training': len(training), 'generated_training_exclusions': len(generated),
        'globally_excluded_names': len(excluded), 'beginnings': len(begins), 'whole_blocks': len(blocks),
        'endings': len(ends), 'candidate_cells': cells, 'independent_known_controls': len(controls),
        'control_policy': 'source-known controls; own core removed from block/end witnesses; not a held-out split',
        'sha256': hashes, 'source_rev': None if args.source_table else args.source_rev,
        'source_table_path': str(args.source_table.resolve()) if args.source_table else None,
        'source_table_sha256': hashlib.sha256(data).hexdigest(),
        'capture_sha256': hashlib.sha256(args.capture.read_bytes()).hexdigest(),
        'source_input_sha256': source_inputs, 'exact_frozen_replay': frozen is not None,
        'application_sha256': digest(application), 'generated_exclusions_sha256': digest(generated),
        'globally_excluded_sha256': digest(excluded),
        'generator_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'searched_candidates': 0}
    if frozen:
        report['original_measurement'] = frozen
        report['frozen_input_file_sha256'] = {
            role: hashlib.sha256((args.frozen_dir/(role+'.txt')).read_bytes()).hexdigest() for role in factors}
    if not args.size:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        for role, values in factors.items():
            content = ((args.frozen_dir/(role+'.txt')).read_bytes() if frozen else
                       ''.join('0,'+name+'\n' for name in sorted(values)).encode())
            (args.output_dir/(role+'.txt')).write_bytes(content)
        for label, value in [('beginning_source_examples', beginning_sources),
                             ('block_source_examples', block_evidence), ('ending_source_examples', tail_evidence)]:
            (args.output_dir/(label+'.json')).write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8')
        if args.save_inputs:
            write_keyed(args.output_dir/'application.keyed.txt', application)
            write_keyed(args.output_dir/'generated_exclusions.keyed.txt', generated)
        paths = {role: (args.output_dir/(role+'.txt')).resolve().as_posix() for role in factors}
        plan = (f'label: BO7 independently witnessed complete six-byte image blocks\n'
                f'describe: Verified complete block factors; {cells} cells; image only; '
                f'generator contrib/{Path(__file__).name}; source evidence in measurement.json.\n'
                f'game: {GAME}\nbegin: @{paths["begin"]}\nstem: @{paths["stem"]}\n'
                f'end: @{paths["end"]}\nbare: no\nfold: yes\n')
        (args.output_dir/'plan.txt').write_text(plan,encoding='utf-8')
    report['seconds'] = round(time.monotonic()-started,3)
    if not args.size:
        (args.output_dir/'measurement.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k not in ('source_input_sha256', 'original_measurement')}))


if __name__ == '__main__':
    main()
