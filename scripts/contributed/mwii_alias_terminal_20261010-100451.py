"""Alias terminal-byte plans for a modern game, without a Rust toolchain.

The reviewed terminal solvers invert the alias hash for a name's final bytes
against prefixes witnessed by the target's own alias pool. They embed a Rust
solver, which this machine cannot build. The same search is expressible as an
engine plan: begin = witnessed prefixes, stem = one byte, end = the remaining
trailing bytes, and run_best peels the endings off each wanted id once instead
of multiplying the product out.

Run: python contrib/mwii_alias_terminal.py --game MODWAR22 --bytes 4
Then: bin/windows/confirm_plan.exe plans/mwii_term4.txt --size
      bin/windows/confirm_plan.exe plans/mwii_term4.txt --game MODWAR22
Old two/three-byte domains, published keys and current claims are left to the
engine's own exclusion; normal submission is required.
"""
import argparse
import itertools
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
while ROOT != ROOT.parent and not (ROOT / 'scripts/snapshot.py').is_file():
    ROOT = ROOT.parent
if not (ROOT / 'scripts/snapshot.py').is_file():
    ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / 'scripts'))
import snapshot

ALPHABET = 'abcdefghijklmnopqrstuvwxyz0123456789_-'


def corpus(game):
    names = set(snapshot.table_names('fnv1a_soundbanks_aliases_v2'))
    for top in ['all_names', 'findings']:
        for path in (ROOT / top).glob('*/sound_alias.txt'):
            for row in path.read_text(encoding='utf-8').splitlines():
                raw, sep, name = row.partition(',')
                if not sep or not name.isascii():
                    continue
                try:
                    key = int(raw, 16) & snapshot.ID_MASK
                except ValueError:
                    continue
                name = name.strip().lower().replace(chr(92), '/')
                if snapshot.fnv1a(name, game, 'sound_alias') & snapshot.ID_MASK == key:
                    names.add(name)
    return {n for n in names if n.isascii() and n.strip() == n}


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument('--game', required=True, choices=sorted(snapshot.MODERN))
    p.add_argument('--bytes', type=int, choices=[3, 4], default=4,
                   help='terminal bytes to solve; end holds all but the first')
    a = p.parse_args()
    shot = snapshot.read(ROOT / 'snapshots' / (a.game.lower() + '.ids'))
    assert shot.game == a.game
    held = set(shot.by_pool()['sound_alias'])
    names = corpus(a.game)
    target = {n for n in names
              if len(n) >= 8 + a.bytes
              and snapshot.fnv1a(n, a.game, 'sound_alias') & snapshot.ID_MASK in held}
    prefixes = sorted({n[:-a.bytes] for n in target})
    plans = ROOT / 'plans'
    tag = a.game.lower()
    begins_path = plans / f'{tag}_term{a.bytes}.begins.txt'
    begins_path.write_text(''.join(b + '\n' for b in prefixes), encoding='utf-8')
    stem_path = plans / 'byte38.stems.txt'
    if not stem_path.exists():
        stem_path.write_text(''.join(c + '\n' for c in ALPHABET), encoding='utf-8')
    ends_path = plans / f'{tag}_term{a.bytes}.ends.txt'
    tails = [''.join(t) for t in itertools.product(ALPHABET, repeat=a.bytes - 1)]
    ends_path.write_text(''.join(t + '\n' for t in tails), encoding='utf-8')
    plan_path = plans / f'{tag}_term{a.bytes}.txt'
    plan_path.write_text(
        f'# Written by contrib/mwii_alias_terminal.py --game {a.game} --bytes {a.bytes}. '
        f'Regenerate rather than editing.\n'
        f'#\n'
        f'# {len(prefixes)} prefixes witnessed by {a.game} target-held aliases, crossed\n'
        f'# with every {a.bytes}-byte terminal over the alias alphabet, solved by the\n'
        f'# engine peeling {len(tails)} endings off each wanted alias id.\n'
        f'label: {a.game} alias terminal-{a.bytes} from witnessed prefixes\n'
        f'describe: target-held alias prefixes crossed with every trailing '
        f'{a.bytes}-byte string; engine peels endings off wanted ids\n'
        f'game: {a.game}\n'
        f'begin: @plans/{begins_path.name}\n'
        f'stem: @plans/{stem_path.name}\n'
        f'end: @plans/{ends_path.name}\n'
        f'bare: no\n'
        f'fold: yes\n',
        encoding='utf-8')
    print(f'{len(prefixes)} prefixes from {len(target)} target-held names; '
          f'{len(tails)} endings; plan {plan_path}', file=sys.stderr)
    print(str(plan_path))


if __name__ == '__main__':
    main()
