"""Test every literal in every local corpus file against the snapshot, all pools.

Not a generator in the usual sense: it emits the project's own accumulated corpora
verbatim -- borrowed/, logs/, plans/, data/, scripts/contributed/ -- so that every
string anybody has ever harvested is checked against the loaded asset ids at least
once, in every pool rather than only the five gated types.

The motivating case: `spawner_*` aitype names had been sitting in borrowed/ for
weeks. They were never found because aitype is not one of the five types the
searches target, so nothing had ever hashed them. 197 of them landed the first
time anybody tried.

Run:
    python contrib/corpus_total_sweep.py | confirm_list - --game BLKOPS04 \
        --label "total corpus sweep, all pools" --script contrib/corpus_total_sweep.py
"""
import pathlib
import sys

ROOTS = ("borrowed", "logs", "plans", "data", "scripts/contributed")


def main() -> None:
    seen = 0
    for root in ROOTS:
        for path in sorted(pathlib.Path(root).rglob("*.txt")):
            try:
                with path.open(encoding="utf-8", errors="replace") as handle:
                    for line in handle:
                        line = line.strip()
                        if line:
                            sys.stdout.write(line + "\n")
                            seen += 1
            except OSError:
                continue
    print(f"corpus total sweep: {seen:,} candidate lines", file=sys.stderr)


if __name__ == "__main__":
    main()
