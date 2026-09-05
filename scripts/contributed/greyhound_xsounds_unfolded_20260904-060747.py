#!/usr/bin/env python3
"""Emit Greyhound's exact historical ``xsounds`` labels for BO4 SAB confirmation.

The package index is independent of cod-name-db.  This deliberately selects
only its sound-file table: the other four wanted type tables are already fully
represented upstream, whereas xsounds retains names absent from the current
tables.  Preserve backslashes; BO4 hashes SAB paths unfolded.
"""
from pathlib import Path


PATH = (Path(__file__).resolve().parents[1] / 'borrowed' / 'GreyhoundPackageIndex'
        / 'PackageIndexSources' / 'FNV1A' / 'fnv1a_xsounds.csv')


def main() -> None:
    seen: set[str] = set()
    with PATH.open(encoding='utf-8', errors='surrogateescape') as source:
        for row in source:
            _, comma, name = row.rstrip('\r\n').partition(',')
            if comma and name and name not in seen:
                seen.add(name)
                print(name)


if __name__ == '__main__':
    main()
