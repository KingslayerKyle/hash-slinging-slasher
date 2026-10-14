"""Read asset names out of an installed Modern Warfare III build.

    python contrib/harvest_mwiii.py --folder "<install>/cod23" --oodle "<install>/oo2core_8_win64.dll" --limit 20 > names.txt

Reads:  <install>/cod23/*.ff   -- the shipped fast files.
Writes: candidate names on standard output, one per line; progress on standard error.

Nothing decompressed is written down: each block is expanded into memory, scanned, and
dropped, which is the rule `scripts/harvest_bo4.py` states for the same reason.

## Why this is not the same as walking the containers by hand

The `.ff` payload is packed, so a strings scan of the file finds noise (`__g5wiy6`) and
nothing else -- 7.98 bits/byte, no zlib at any header offset, four ASCII runs >= 8 across
the first 8 MB of six sampled files, two of which are the filename repeated. What makes it
readable is the block chain, and the layout below is read off ATIAN's own MWIII
implementation (`decompressor_iw.cpp`, `fastfile_handlers.hpp`):

    byte   magic[8]         "IWff" + platform + "100"
    +0x08  headerVersion    0x17 MWII, 0x18 MWIII, 0x19 BO6
    +0x0c  xfileVersion
    +0x38  size / preloadWalkSize / blockSize[16] / encryption header   (0xe0 total)

Then a byte-by-byte scan for the 4-byte marker 02 49 57 43 ("\\x02IWC"); if the four bytes
after it are "IWff" the file is signed, and 0x8000 of RSA header follows. After that an
8-byte compress header whose last byte is the algorithm:

    1 none, 2-3 zlib, 4-5 lz4, 6-7 Oodle Kraken, 0xc-0xd Leviathan,
    0xe-0xf Mermaid, 0x10-0x11 Selkie, 0x12-0x13 zstd

and then a chain of 12-byte block headers -- compressedSize, uncompressedSize,
encryptionCTR -- each followed by that block's bytes, 4-byte aligned. For signed MWII/MWIII/BO6 files a 0x4000 RSA chunk precedes zero-based
block indices 0x1ff, 0x3ff, etc.; the counter counts parsed blocks, not decoder successes.
This follows the ST_MW22 branch of the referenced parser.

Oodle is decoded by the copy the install ships (`oo2core_8_win64.dll`), the same way
`scripts/harvest_bo4.py` uses Black Ops 4's.
"""
import argparse
import ctypes
import glob
import os
import re
import struct
import sys
import zlib

IWC = b"\x02IWC"
IWFF = b"IWff"
SIGNED_SKIP = 0x4000 + 0x4000
RSA_CHUNK = 0x4000
RSA_EVERY = 0x200

NAME = re.compile(rb"[A-Za-z0-9][A-Za-z0-9_/.\-]{5,159}")
SEPARATORS = set(b"_/")
LETTERS = re.compile(rb"[A-Za-z]")
NOISE = re.compile(rb"([A-Za-z0-9])\1{3,}")
RUN = re.compile(rb"[\x20-\x7e]{4,}")

names = set()


def keep(text):
    if len(text) < 6 or len(text) > 160:
        return False
    if not any(byte in SEPARATORS for byte in text):
        return False
    if len(LETTERS.findall(text)) < 3:
        return False
    if NOISE.search(text):
        return False
    return True


def take(data):
    for run in RUN.finditer(data):
        for part in run.group().split(b":"):
            for found in NAME.finditer(part):
                text = found.group()
                if keep(text):
                    names.add(text.decode("ascii").lower())


def oodle(path):
    """Load only the caller's explicitly selected, trusted game decoder."""
    if not os.path.isfile(path):
        raise SystemExit("--oodle must name the trusted decoder shipped by your install")
    library = ctypes.WinDLL(os.path.abspath(path))
    call = library.OodleLZ_Decompress
    call.restype = ctypes.c_int64
    call.argtypes = [
        ctypes.c_char_p, ctypes.c_int64, ctypes.c_char_p, ctypes.c_int64,
        ctypes.c_int32, ctypes.c_int32, ctypes.c_int64,
        ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p,
        ctypes.c_void_p, ctypes.c_int64, ctypes.c_int32,
    ]
    print("oodle: %s" % os.path.abspath(path), file=sys.stderr)
    return call


def run_blocks(path, decompress):
    """Decompress every block in one fast file, scanning as it goes. Returns blocks read."""
    with open(path, "rb") as handle:
        raw = handle.read()

    if len(raw) < 0xE0 or raw[:4] != b"IWff" or raw[5:8] != b"100":
        return 0
    version = struct.unpack_from("<I", raw, 0x08)[0]
    if version not in (0x17, 0x18, 0x19):
        return 0

    at = raw.find(IWC, 0xE0)
    if at < 0:
        return 0
    at += 4
    signed = raw[at:at + 4] == IWFF
    if signed:
        at += SIGNED_SKIP
    if at + 8 > len(raw):
        return 0
    algorithm = raw[at + 7]
    at += 8

    if algorithm not in (1, 2, 3, 6, 7, 12, 13, 14, 15, 16, 17):
        print("Unsupported compression algorithm %d: %s" % (algorithm, path), file=sys.stderr)
        return 0
    blocks = 0
    parsed = 0
    while at + 12 <= len(raw):
        if signed and parsed % RSA_EVERY == RSA_EVERY - 1:
            at += RSA_CHUNK
            if at + 12 > len(raw):
                break
        compressed, uncompressed, _ctr = struct.unpack_from("<III", raw, at)
        at += 12
        parsed += 1
        if compressed == 0:
            break
        aligned = (compressed + 3) & ~3
        if at + aligned > len(raw) or not 0 < uncompressed <= 0x4000000 or compressed > 0x4000000:
            break
        payload = raw[at:at + compressed]
        at += aligned

        if algorithm == 1:
            if len(payload) == uncompressed:
                take(payload)
                blocks += 1
            continue
        if algorithm in (2, 3):
            try:
                decoder = zlib.decompressobj()
                output = decoder.decompress(payload, uncompressed + 1)
                if (len(output) == uncompressed and decoder.eof
                        and not decoder.unconsumed_tail and not decoder.unused_data):
                    take(output)
                    blocks += 1
            except zlib.error:
                pass
            continue
        if algorithm in (4, 5, 0x12, 0x13):
            continue  # lz4/zstd: not needed, the modern titles use Oodle

        out = ctypes.create_string_buffer(uncompressed)
        produced = decompress(payload, compressed, out, uncompressed,
                              0, 0, 0, None, None, None, None, None, 0, 0)
        if produced == uncompressed:
            take(out.raw[:produced])
            blocks += 1
        del out
    return blocks


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--limit", type=int, default=0, help="stop after this many files")
    parser.add_argument("--folder", required=True, help="explicit cod23 fast-file directory")
    parser.add_argument("--oodle", help="explicit trusted game decoder DLL, required for Oodle blocks")
    parser.add_argument("--output", help="write the names here instead of standard output")
    parser.add_argument("--sample", type=int, default=0,
                        help="take every Nth file across the whole list instead of the head")
    parser.add_argument("--start", type=int, default=0, help="skip this many files first")
    options = parser.parse_args(argv)

    if not os.path.isdir(options.folder):
        parser.error("--folder must be an existing directory")
    if min(options.limit, options.sample, options.start) < 0:
        parser.error("--limit, --sample and --start must be nonnegative")
    files = sorted(glob.glob(os.path.join(options.folder, "*.ff")))
    if options.sample:
        files = files[::options.sample]
    if options.start:
        files = files[options.start:]
    if options.limit:
        files = files[:options.limit]
    print("fast files: %d" % len(files), file=sys.stderr)

    decoder = None
    def decompress(*args):
        nonlocal decoder
        if not options.oodle:
            raise SystemExit("Oodle block requires --oodle pointing to your trusted game DLL")
        if decoder is None:
            decoder = oodle(options.oodle)
        return decoder(*args)
    total = 0
    for index, path in enumerate(files):
        try:
            total += run_blocks(path, decompress)
        except Exception as error:  # a corrupt block must not stop the sweep
            print("  %s: %s" % (os.path.basename(path), error), file=sys.stderr)
        if (index + 1) % 250 == 0:
            print("  %d/%d files, %d blocks, %d names"
                  % (index + 1, len(files), total, len(names)), file=sys.stderr)

    if options.output:
        with open(options.output, "w", encoding="utf-8", newline="\n") as handle:
            handle.write("\n".join(sorted(names)) + "\n")
    else:
        for name in sorted(names):
            print(name)
    print("blocks: %d, names: %d" % (total, len(names)), file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
