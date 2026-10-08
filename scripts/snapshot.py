"""Reads a captured snapshot and the hash tables, so a script can ask what is still unnamed.

Every analysis script here needs the same three things: the ids a game holds, which pool each one
sits in, and which of them the community can already name. This is that, once.

The pool names are parsed out of `src/lib.rs` rather than copied into this file. Copying them
would work today and be wrong within a month -- there are two lists of two hundred entries, the
games number their asset types differently, and a stale copy does not fail loudly. It mislabels
findings, which is worse.

Usage as a library:

    import snapshot
    snap = snapshot.read("snapshots/blkopscw.ids")     # -> Snapshot
    known = snapshot.known_hashes()                    # -> set of ints
    snap.unnamed(known)                                # -> {id: pool index}

Run it directly for a one-line summary of every snapshot in the repository.
"""
import glob
import os
import re
import struct
from pathlib import Path
import sys

import settings

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MAGIC = b"CODIDS"
RECORD = 10

BASIS = 0xCBF29CE484222325
PRIME = 0x100000001B3
ID_MASK = 0x7FFFFFFFFFFFFFFF

# Pools no rule can reach or that are known to be worth nothing. Kept in step with
# LOW_VALUE_POOLS and UNREACHABLE on the Rust side; `check_docs.py` fails if they drift.
SKIP = {"xmodelmesh", "streamkey", "localizeentry", "localize_entry"}

# The asset types this project is actually for. `sound` is Black Ops 4's *bank* pool and is not
# one of them -- the files are `sound_asset` and the alias names are `sound_alias`.
IMPORTANT = {"xmodel", "xanim", "image", "material", "sound_asset", "sound_alias"}


MODERN = {"MODWAR22", "YAMYAMOK", "BLACKOP6", "BLACKOP7", "MODWAR7"}
MODERN_TABLES = {"fnv1a_ximages_v2", "fnv1a_xmaterials_v2", "fnv1a_xanims_v2",
                "fnv1a_xsounds_v2", "fnv1a_soundbanks_aliases_v2",
                "fnv1a_soundbanks_v2", "fnv1a_animpkgs_v2"}


def searchable(game, kind, search_modern_models=False):
    """Shared model policy: reports always use the default; searches may opt in."""
    return game.upper() not in MODERN or kind != "xmodel" or search_modern_models


def database_policy(table):
    table=table.removesuffix('.csv')
    if not table.startswith("fnv1a_"):
        return None
    mask = {"fnv1a_bones":0xffffffff, "fnv1a_strings":0x0fffffffffffffff,
            "fnv1a_bones_v2":0xffffffffffffffff,
            "fnv1a_soundbanks_aliases_v2":0xffffffffffffffff}.get(table,ID_MASK)
    basis = 0x47F5817A5EF961BA if table.endswith("_v2") and table not in {"fnv1a_bones_v2","fnv1a_soundbanks_aliases_v2"} else BASIS
    return basis, mask, "xsounds" in table and not table.endswith("_v2")


def database_source_hash(table,name):
    table=table.removesuffix('.csv')
    policy=database_policy(table)
    if policy is None:
        return None
    value=0x811c9dc5 if table=="fnv1a_bones" else policy[0]
    prime=0x01000193 if table=="fnv1a_bones" else PRIME
    mask=0xffffffff if table=="fnv1a_bones" else 0xffffffffffffffff
    for byte in name.encode("utf-8"):
        value=((value^byte)*prime)&mask
    return value


def verified_database_row(table,key,display):
    table=table.removesuffix('.csv')
    policy=database_policy(table)
    if policy is None:
        return None
    display=display.strip()
    lowered=display.translate(str.maketrans('ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'))
    older_mask=not table.endswith('_v2') and policy[1]==ID_MASK
    for spelling in dict.fromkeys((display,lowered)):
        candidates=(spelling.replace(chr(92),"/"),spelling.replace("/",".").replace(chr(92),"."),spelling.replace("/",chr(92)))
        for index,name in enumerate(candidates):
            if index==2 and not policy[2]:
                continue
            full=database_source_hash(table,name)
            if full & policy[1] == key or (older_mask and full & 0x0fffffffffffffff == key):
                return full,name
    return None


def database_names(table,lines):
    for line in lines:
        key,sep,display=line.partition(",")
        if not sep:
            continue
        try:
            key=int(key.strip(),16)
        except ValueError:
            continue
        if database_policy(table) is None:
            name=display.strip()
        else:
            restored=verified_database_row(table,key,display)
            if restored is None:
                continue
            _,name=restored
        if name:
            yield name


def sound_spelling(game, key, display):
    table='fnv1a_xsounds_v2' if game in MODERN else 'fnv1a_xsounds'
    restored=verified_database_row(table,key,display)
    if restored is not None:
        _,name=restored
        value=fnv1a_nofold(name) if game=='BLKOPS04' else fnv1a(name,game,'sound_asset')
        if value & ID_MASK == key & ID_MASK:
            return name
    return None


def fnv1a(name, game=None, kind="image"):
    """The game's hash: FNV-1a 64, lowercased, backslashes folded to forward slashes.

    Both games use it and so do all the non-`_v2` tables. See docs/HASHES.md for which files use
    which offset and which mask -- getting the mask wrong is the commonest reason a correct name
    fails to resolve.
    """
    h = 0x47F5817A5EF961BA if game in MODERN and kind != "sound_alias" else BASIS
    for byte in name.strip().lower().replace("\\", "/").encode("utf-8", "replace"):
        h = ((h ^ byte) * PRIME) & 0xFFFFFFFFFFFFFFFF
    return h


def fnv1a_nofold(name):
    """The same hash, leaving backslashes alone.

    Black Ops 4's SAB sound names are stored with literal backslashes and their ids are the hash
    of exactly that. Measured against the 8,385 of them cod-name-db already names: 8,385 reproduce
    this way, 0 with the usual fold. Every other table folds harmlessly, because its names already
    use forward slashes.
    """
    h = BASIS
    for byte in name.strip().lower().encode("utf-8", "replace"):
        h = ((h ^ byte) * PRIME) & 0xFFFFFFFFFFFFFFFF
    return h


def _pool_lists():
    """The two asset-type enums, read out of src/lib.rs so there is one copy of them anywhere."""
    source = open(os.path.join(ROOT, "src", "lib.rs"), encoding="utf-8").read()
    out = {}

    for constant, game in (("POOLS", "BLKOPSCW"), ("BO4_POOLS", "BLKOPS04")):
        match = re.search(
            r"pub const %s: &\[&str\] = &\[(.*?)\];" % constant, source, re.S
        )
        if not match:
            raise SystemExit("src/lib.rs no longer declares %s in the expected shape" % constant)
        out[game] = re.findall(r'"([^"]+)"', match.group(1))

    return out


POOLS = _pool_lists()


class Snapshot:
    def __init__(self, game, records, pools=None):
        self.game = game
        self.records = records          # list of (id, pool index)
        self.pools = POOLS.get(game, []) if pools is None else pools

    def pool_name(self, index):
        name = self.pools[index] if index < len(self.pools) else "pool_%d" % index
        return "sound_asset" if name == "sndasset" else name

    def by_pool(self):
        """{pool name: [ids]}, in pool order."""
        out = {}
        for asset_id, pool in self.records:
            out.setdefault(self.pool_name(pool), []).append(asset_id)
        return out

    def unnamed(self, known, skip=SKIP, search_modern_models=None):
        """{id: pool name} for everything the tables cannot name."""
        if search_modern_models is None:
            search_modern_models = settings.search_modern_models()
        out = {}
        for asset_id, pool in self.records:
            name = self.pool_name(pool)
            if name in skip or not searchable(self.game, name, search_modern_models):
                continue
            if asset_id in known:
                continue
            out[asset_id] = name
        return out

    def __len__(self):
        return len(self.records)


def read(path):
    with open(path, "rb") as handle:
        blob = handle.read()

    if len(blob) < 16 or blob[:6] != MAGIC:
        raise SystemExit("%s is not a snapshot file" % path)

    version, name_length = struct.unpack_from("<HH", blob, 6)
    if version != 1:
        raise SystemExit("%s is snapshot version %d, and this reads version 1" % (path, version))

    at = 10
    game = blob[at:at + name_length].decode("utf-8")
    at += name_length

    (count,) = struct.unpack_from("<Q", blob, at)
    at += 8

    if len(blob) != at + count * RECORD:
        raise SystemExit("%s: invalid snapshot length" % path)
    records = []
    for index in range(count):
        offset = at + index * RECORD
        asset_id = int.from_bytes(blob[offset:offset + 8], "little")
        pool = int.from_bytes(blob[offset + 8:offset + 10], "little")
        records.append((asset_id, pool))

    pools = None
    if game in MODERN:
        rows = {}
        for line in Path(path).with_suffix(".pools.txt").read_text().splitlines():
            fields = re.split(r"[\s,]+", line.strip())
            if len(fields) == 3 and fields[0].isdigit() and fields[2].isdigit():
                i, name = int(fields[0]), fields[1]
                if i in rows or name in rows.values():
                    raise SystemExit("duplicate pool mapping")
                rows[i] = name
        if not rows or any(p not in rows for _, p in records):
            raise SystemExit("capture has unmapped pools")
        pools = [rows.get(i, "pool_%d" % i) for i in range(max(rows)+1)]
    return Snapshot(game, records, pools)


def snapshots():
    """Every snapshot in the repository, newest game first is not meaningful so: sorted."""
    folder = settings.path("snapshots", "snapshots")
    return sorted(glob.glob(os.path.join(folder, "*.ids")))


def known_hashes(tables=None, game=None):
    """Stored keys remain authoritative; name hashes use verified source-table spellings."""
    folder = tables or settings.tables_csv()
    game = game or settings.game()
    known = set()
    for path in sorted(glob.glob(os.path.join(folder, "*.csv"))):
        table = Path(path).stem
        if game in MODERN and table not in MODERN_TABLES:
            continue
        with open(path, encoding="utf-8", errors="replace") as handle:
            for line in handle:
                key, sep, display = line.partition(",")
                if not sep:
                    continue
                try:
                    key = int(key.strip(),16)
                except ValueError:
                    continue
                known.update((key,key & ID_MASK))
                restored = verified_database_row(table,key,display)
                if restored is not None:
                    full, _ = restored
                    known.update((full,full & ID_MASK))
    return known


def table_names(*tables):
    """Source-table-verified spellings; Saluki display paths are not asset-name seeds."""
    folder = settings.tables_csv()
    out = []
    for table in tables:
        path = os.path.join(folder, table + ".csv")
        if not os.path.exists(path):
            continue
        with open(path, encoding="utf-8", errors="replace") as handle:
            out.extend(database_names(table, handle))
    return out


def confirmed_names(kind=None):
    """Everything this machine has confirmed, plus every merged submission in the repository.

    Both, deliberately. What this machine found is the freshest seed material there is, and what
    everybody else submitted is the same thing from twenty other machines.

    `kind` narrows to one asset type, and any script measuring a *convention* must pass it. The
    files are named for the pool a name was filed under -- `material.txt` in a findings run,
    `material_20260819-041239.txt` in a submission -- so the type is recoverable, and mixing types
    silently destroys exactly the measurement being taken. Getting this wrong makes every asset
    type look like it wears every other type's decorations.
    """
    out = []

    for folder in (settings.path("findings", "findings"), os.path.join(ROOT, "submissions")):
        for path in glob.glob(os.path.join(folder, "**", "*.txt"), recursive=True):
            stem = os.path.splitext(os.path.basename(path))[0]

            if kind and stem != kind and not stem.startswith(kind + "_"):
                continue

            with open(path, encoding="utf-8", errors="replace") as handle:
                for line in handle:
                    key, _, name = line.partition(",")
                    name = (name or key).strip()
                    if name:
                        out.append(name)

    return out


if __name__ == "__main__":
    found = snapshots()
    if not found:
        raise SystemExit("no snapshots found; they ship with the repository")

    print("reading the tables (a few seconds)", file=sys.stderr)
    known = known_hashes()

    for path in found:
        snap = read(path)
        left = snap.unnamed(known)
        important = sum(1 for pool in left.values() if pool in IMPORTANT)
        print(
            "%-10s %8d assets  %8d unnamed and reachable  %8d of those in the five types"
            % (snap.game, len(snap), len(left), important)
        )
