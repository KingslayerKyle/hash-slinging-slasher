#!/usr/bin/env python3
"""Generator for Black Ops 4 Black Market MK2 weapon itemshop and itemdetail icons."""

WEAPONS = [
    "ar_standard", "ar_damage", "ar_fastfire", "ar_accurate", "ar_modular",
    "ar_peacekeeper", "ar_an94", "ar_doublebarrel", "smg_standard", "smg_handling",
    "smg_fastfire", "smg_capacity", "smg_accurate", "smg_burst", "smg_folding",
    "smg_vmp", "tr_midburst", "tr_longburst", "tr_powersemi", "tr_flechette",
    "tr_m16", "sn_fastbolt", "sn_powerbolt", "sn_quickscope", "sn_heavy",
    "sn_locus", "sn_semiauto", "lmg_heavy", "lmg_standard", "lmg_spray",
    "lmg_stealth", "shotgun_pump", "shotgun_semiauto", "shotgun_precision",
    "shotgun_trenchgun", "pistol_standard", "pistol_revolver", "pistol_burst",
    "pistol_fullauto"
]

SEASONS = [f"loot{s:02d}" for s in range(1, 13)]

def generate():
    seen = set()
    def emit(s):
        s = s.strip()
        if s and s not in seen:
            seen.add(s)
            print(s)

    for w in WEAPONS:
        emit(f"reserves_weapon_{w}_mk2")
        emit(f"reserves_weapon_{w}_mastercraft")
        for s in SEASONS:
            emit(f"{s}_ui_icon_blackmarket_itemdetail_{w}_mk2")
            emit(f"{s}_ui_icon_blackmarket_itemshop_{w}_mk2")
            emit(f"{s}_ui_icon_blackmarket_contracts_{w}_mk2")
            emit(f"{s}_ui_icon_blackmarket_contracts_{w}_mk2_tall")
            emit(f"{s}_ui_icon_blackmarket_contracts_{w}_mastercraft")
            emit(f"{s}_ui_icon_blackmarket_contracts_{w}_mastercraft_tall")
            emit(f"{s}_ui_icon_blackmarket_itemdetail_{w}_mastercraft")
            emit(f"{s}_ui_icon_blackmarket_itemshop_{w}_mastercraft")
            for x in ["x3", "x5", "x8"]:
                emit(f"{s}_ui_icon_blackmarket_itemshop_bundle_{w}_{x}")
                emit(f"{s}_ui_icon_blackmarket_itemdetail_bundle_{w}_{x}")

if __name__ == "__main__":
    generate()
