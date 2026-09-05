#!/usr/bin/env python3
"""Fill supported terminal-role variants within real ``fly_`` sound-alias bases."""
from collections import defaultdict
from pathlib import Path
import sys

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / "scripts"))
import snapshot

ROLES = (
    "npc", "plr", "hv", "lt_npc", "lt_plr", "npc_hv", "igc_lt_plr",
    "medium_lt_plr", "rapid_lt_plr", "soft_lt_plr", "soft_lt_npc",
)


def split_role(name: str):
    for role in ROLES:
        marker = "_" + role
        if name.endswith(marker) and len(name) > len(marker) + 4:
            return name[:-len(marker)], role
    return None


def main() -> None:
    known = {
        name.strip().lower().replace("\\", "/")
        for name in snapshot.table_names("fnv1a_soundbanks_aliases")
        if name.strip()
    }
    known.update(
        name.strip().lower().replace("\\", "/")
        for name in snapshot.confirmed_names("sound_alias")
        if name.strip()
    )
    base_roles = defaultdict(set)
    role_bases = defaultdict(set)
    for name in known:
        if name.startswith("fly_"):
            pair = split_role(name)
            if pair:
                base, role = pair
                base_roles[base].add(role)
                role_bases[role].add(base)
    supported_roles = {role for role, bases in role_bases.items() if len(bases) >= 3}
    candidates = {
        f"{base}_{role}"
        for base, roles in base_roles.items()
        if len(roles) >= 2
        for role in supported_roles
        if f"{base}_{role}" not in known
    }
    print("\n".join(sorted(candidates)))


if __name__ == "__main__":
    main()
