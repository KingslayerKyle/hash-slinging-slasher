"""Emit exact material cores observed under clt/ but absent under cltp/.

The directional relation is admitted only because 2,531 complete full-core
clt/cltp controls establish cltp as a strict subset.  It changes no basename
byte and is intentionally not a general material-directory sweep.
"""

from pathlib import Path
import sys


ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / "scripts"))
import snapshot


SOURCE = "clt/"
TARGET = "cltp/"


def main() -> None:
    known = {
        name.strip().lower().replace("\\", "/")
        for name in snapshot.table_names("fnv1a_xmaterials")
        if name.strip()
    }
    known.update(
        name.strip().lower().replace("\\", "/")
        for name in snapshot.confirmed_names("material")
        if name.strip()
    )
    source_cores = {name[len(SOURCE) :] for name in known if name.startswith(SOURCE)}
    target_cores = {name[len(TARGET) :] for name in known if name.startswith(TARGET)}
    controls = len(source_cores & target_cores)
    candidates = {TARGET + core for core in source_cores - target_cores}
    print(
        f"{controls:,} clt/cltp exact-core controls; {len(candidates):,} clt-only candidates",
        file=sys.stderr,
    )
    print("\n".join(sorted(candidates)))


if __name__ == "__main__":
    main()
