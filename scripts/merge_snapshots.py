"""Combine complete mode captures by asset type, including injected pools.

Usage: python scripts/merge_snapshots.py --game MODWAR22 --out local-captures/modwar22.ids mp.ids sp.ids
Inputs and their .pools.txt maps are never changed. Output indexes are canonical, not a live enum.
"""
import argparse
import collections
import hashlib
import json
from pathlib import Path
import re
import struct


def load(path):
    data = path.read_bytes()
    if data[:6] != b"CODIDS" or len(data) < 18:
        raise ValueError(f"{path}: invalid snapshot")
    version, length = struct.unpack_from("<HH", data, 6)
    tag = data[10:10+length].decode()
    count = struct.unpack_from("<Q", data, 10+length)[0]
    start = 18+length
    if version != 1 or len(data) != start+count*10:
        raise ValueError(f"{path}: invalid snapshot length/version")
    pools = {}
    for line in path.with_suffix(".pools.txt").read_text().splitlines():
        match = re.fullmatch(r"\s*(\d+)[,\s]+(\S+?)[,\s]+(\d+)\s*", line)
        if match:
            index, name, size = int(match[1]), match[2], int(match[3])
            if index in pools or name.startswith("pool_"):
                raise ValueError(f"{path}: invalid/unknown pool mapping")
            pools[index] = (name, size)
    if len({name for name, _ in pools.values()}) != len(pools):
        raise ValueError(f"{path}: duplicate type names")
    records = list(struct.iter_unpack("<QH", data[start:]))
    if any(a >= b for a, b in zip(records, records[1:])) or any(key >= 1<<63 for key, _ in records):
        raise ValueError(f"{path}: unsorted, duplicate, or unmasked records")
    counts = collections.Counter(pool for _, pool in records)
    if counts != {pool: size for pool, (_, size) in pools.items() if size}:
        raise ValueError(f"{path}: census does not match records")
    return tag, records, pools, hashlib.sha256(data).hexdigest()


def merge(game, inputs, output):
    if output.exists() or output.with_suffix(".pools.txt").exists():
        raise ValueError(f"{output}: existing output preserved; choose a fresh destination")
    combined, labels, by_name, sources = set(), {}, {}, []
    for n, path in enumerate(inputs):
        tag, records, pools, digest = load(path)
        if tag not in {game, game+"_SP", game+"_MP"}:
            raise ValueError(f"{path}: {tag} does not belong to {game}")
        if not n:
            labels = {i: name for i, (name, _) in pools.items()}
            by_name = {name: i for i, name in labels.items()}
        for name in sorted({name for name, _ in pools.values()} - by_name.keys()):
            index = max(labels, default=-1)+1
            if index > 65535:
                raise ValueError("too many canonical pools")
            labels[index], by_name[name] = name, index
        mapping = {i: by_name[name] for i, (name, _) in pools.items()}
        mapped = {(key, mapping[pool]) for key, pool in records}
        before = len(combined)
        combined.update(mapped)
        sources.append({"file": path.name, "tag": tag, "sha256": digest,
                        "records": len(records), "added": len(combined)-before,
                        "pool_mapping": mapping})
        assert mapped <= combined
    records = sorted(combined)
    counts = collections.Counter(pool for _, pool in records)
    tag = game.encode()
    encoded = bytearray(b"CODIDS"+struct.pack("<HH", 1, len(tag))+tag+struct.pack("<Q", len(records)))
    for record in records:
        encoded.extend(struct.pack("<QH", *record))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(encoded)
    census = f"{game} -- {len(records)} assets in {len(counts)} filled pools\n\nindex asset_type assets\n"
    census += "".join(f"{i:<6} {labels[i]:<34} {size:>10}\n" for i, size in sorted(counts.items()))
    output.with_suffix(".pools.txt").write_text(census, newline="\n")
    report = {"game": game, "records": len(records), "sources": sources,
              "shared_records_removed": sum(s["records"] for s in sources)-len(records),
              "sha256": hashlib.sha256(encoded).hexdigest(),
              "counts_by_type": {labels[i]: size for i, size in sorted(counts.items())}}
    output.with_suffix(".merge.json").write_text(json.dumps(report, indent=2)+"\n")
    load(output)
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--game", required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("inputs", nargs="+", type=Path)
    args = parser.parse_args()
    report = merge(args.game, args.inputs, args.out)
    print(json.dumps({k: report[k] for k in ("game", "records", "shared_records_removed")}))
