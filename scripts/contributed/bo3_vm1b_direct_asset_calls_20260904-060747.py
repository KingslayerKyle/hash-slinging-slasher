#!/usr/bin/env python3
"""Exact literals passed directly to BO3 VM1B model/sound asset consumers."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / 'borrowed' / 'oldcod-source' / 'bo3_vm1b'
CALL = re.compile(
    r'\b(?:forcestreamxmodel|play(?:local|loop|ambient)?sound(?:atposition|toplayer|ontag|withnotify)?)'
    r'\s*\([^\n"\']*["\']([A-Za-z0-9_./-]{3,160})["\']', re.I)


def main() -> None:
    found: set[str] = set()
    for path in ROOT.rglob('*'):
        if path.suffix.lower() not in {'.gsc', '.csc'}:
            continue
        try:
            found.update(value.lower() for value in CALL.findall(
                path.read_text(encoding='utf-8', errors='ignore')))
        except OSError:
            pass
    print('\n'.join(sorted(found)))


if __name__ == '__main__':
    main()
