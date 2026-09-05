"""Extract explicit Call of Duty asset-shaped ASCII literals from a local crash dump."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
PREFIX = re.compile(rb"(?:i_|mtl_|xmodel_|xanim_|snd_|sound_)[A-Za-z0-9_./\\-]{3,180}")

def main():
    dumps = sorted((ROOT / "dumps").glob("*.dmp"))
    found = set()
    for path in dumps:
        data = path.read_bytes()
        for match in PREFIX.finditer(data):
            value = match.group().decode("ascii", "ignore").lower().replace("\\", "/")
            if value.endswith(("/", "_")):
                continue
            found.add(value)
    print("\n".join(sorted(found)))
    print(f"{len(found):,} explicit dump literals", file=__import__("sys").stderr)

if __name__ == "__main__":
    main()
