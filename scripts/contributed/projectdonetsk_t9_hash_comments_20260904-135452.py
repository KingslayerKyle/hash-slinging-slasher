"""Exact label comments from ProjectDonetsk/T9's CW material registration code.

The source gives both literal spellings and the loader-hash constants, so this
does not infer names from opaque numbers.  Keep this deliberately tiny: other
strings in the project are UI, command, or engine vocabulary rather than asset
labels.
"""

from pathlib import Path

SOURCE = Path("borrowed/ProjectDonetsk-T9/hook_lib/console.cpp")
EXPECTED = {
    '0x4ED973885856E206': 'white',
    '0xB160909B712F8F9': 'lui_loader_no_offset',
}


def fnv1a(text: str) -> int:
    value = 0xCBF29CE484222325
    for byte in text.encode('utf-8'):
        value = ((value ^ byte) * 0x100000001B3) & 0xFFFFFFFFFFFFFFFF
    return value


def main() -> None:
    source = SOURCE.read_text(encoding='utf-8')
    for hashed, label in EXPECTED.items():
        marker = f'{hashed} = "{label}"'
        if marker not in source:
            raise SystemExit(f'missing verified source comment: {marker}')
        # T9 loader ids clear bit 63; the comment uses that loader form.
        if (fnv1a(label) & ((1 << 63) - 1)) != int(hashed, 16):
            raise SystemExit(f'hash mismatch for {label}')
        print(label)


if __name__ == '__main__':
    main()
