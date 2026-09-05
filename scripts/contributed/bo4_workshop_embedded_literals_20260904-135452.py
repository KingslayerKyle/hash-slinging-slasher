"""Extract literal BO4-looking asset labels embedded in the downloaded Workshop mirror."""
from pathlib import Path
import re

ROOT = Path('.tmp-steamcmd/steamapps/workshop/content/311210')
PATTERN = re.compile(rb'(?<![A-Za-z0-9_])((?:i|mtl|xmodel|xanim)_t8_[A-Za-z0-9_./\\-]{2,})')

def main():
    seen = set()
    for path in ROOT.rglob('*'):
        if not path.is_file():
            continue
        try:
            data = path.read_bytes()
        except OSError:
            continue
        for match in PATTERN.finditer(data):
            raw = match.group(1).decode('ascii', 'ignore').replace('\\', '/')
            if raw.count('/') > 8 or len(raw) > 180:
                continue
            seen.add(raw)
    for name in sorted(seen):
        print(name)

if __name__ == '__main__':
    main()
