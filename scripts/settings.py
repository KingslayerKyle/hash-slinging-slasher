"""Reads config.toml, so no script has to hardcode one person's folders.

Understands only the subset the file uses -- comments, `key = value`, and arrays of strings --
rather than needing a TOML library for thirty lines.
"""
import glob
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG = os.path.join(ROOT, "config.toml")


def _values():
    out = {}
    try:
        with open(CONFIG, encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line or line.startswith("#") or line.startswith("["):
                    continue
                if "=" not in line:
                    continue
                key, _, value = line.partition("=")
                if "#" in value and value.count('"') % 2 == 0:
                    value = value.split("#")[0]
                out[key.strip()] = value.strip().strip('"').strip("'")
    except FileNotFoundError:
        pass
    return out


def path(key, default=None):
    """A configured path, or a default that sits inside the repository."""
    value = _values().get(key)
    if value:
        return value
    if default is None:
        return None
    return os.path.join(ROOT, default)


def tables_csv():
    """The folder actually holding the table csv.

    Mirrors src/tables.rs::csv_folder: a folder already full of csv is taken as it is, and an
    empty or missing one resolves to the `cod-name-db` checkout the fetch leaves beside it.
    Without this, a fresh clone reads zero tables from the default `tables/` and measures
    nothing.
    """
    folder = path("tables", "tables")
    if glob.glob(os.path.join(folder, "*.csv")):
        return folder

    # Rust accepts a configured Git checkout regardless of its directory name.
    # Keep Python reporting on the same database as the Rust search tools.
    checkout_root = folder if os.path.exists(os.path.join(folder, ".git")) else os.path.join(os.path.dirname(folder) or ROOT, "cod-name-db")
    checkout = os.path.join(checkout_root, "csv")
    if glob.glob(os.path.join(checkout, "*.csv")):
        return checkout

    return folder


def require(key):
    """A path that only makes sense on a machine that has the thing it names."""
    value = _values().get(key)
    if not value:
        raise SystemExit(
            "`%s` is not set in config.toml.\n"
            "This script needs it; see config.example.toml for what it means." % key
        )
    return value

def search_modern_models():
    """Deliberate opt-in; listing xmodel or all_pools is insufficient."""
    return _values().get("search_modern_models") == "true"


def game():
    """Same CLI pin and per-clone choice used by the Rust searches."""
    import sys
    if "--game" in sys.argv:
        return sys.argv[sys.argv.index("--game") + 1].upper()
    values = _values()
    if values.get("alternate_games") != "false":
        try:
            return open(os.path.join(ROOT, "state", "game.txt"), encoding="utf-8").read().strip()
        except OSError:
            pass
    return values.get("game", "BLKOPSCW").upper()
