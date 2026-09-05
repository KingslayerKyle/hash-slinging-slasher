"""Fill two-token sound-alias cells under heads absent from the carried prefix ceiling."""
import collections
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import snapshot


def main():
    names = set(snapshot.table_names("fnv1a_soundbanks_aliases"))
    names.update(snapshot.confirmed_names("sound_alias"))
    known = {n.strip().lower().replace("\\", "/") for n in names if n.strip()}
    carried = {
        line.strip().lower()
        for line in (ROOT / "data" / "sound.prefixes.txt").read_text(
            encoding="utf-8", errors="replace").splitlines()
        if line.strip()
    }
    families = collections.defaultdict(list)
    for name in known:
        if "/" in name or "." in name:
            continue
        head, sep, rest = name.partition("_")
        if sep and rest.count("_") >= 2:
            families[head + "_"].append(rest.split("_"))
    out = set()
    selected = 0
    for head, rows in families.items():
        if any(head[:cut] in carried for cut in range(1, len(head) + 1)):
            continue
        axes = set()
        tails = collections.Counter()
        for row in rows:
            axes.add((row[0], row[1]))
            tails["_".join(row[2:])] += 1
        shared = {tail for tail, count in tails.items() if count > 1}
        if len(axes) < 2 or not shared:
            continue
        selected += 1
        for first, second in axes:
            for tail in shared:
                candidate = head + first + "_" + second + "_" + tail
                if candidate not in known:
                    out.add(candidate)
    print(f"{selected:,} uncarried families, {len(out):,} two-token grid cells", file=sys.stderr)
    for candidate in sorted(out):
        print(candidate)


if __name__ == "__main__":
    main()
