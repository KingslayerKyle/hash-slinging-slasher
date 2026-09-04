#!/usr/bin/env python3
"""Targeted Black Market & Gauntlet cosmetic image generator for Black Ops 4.

Discovered patterns:
  loot06_ui_icon_blackmarket_contracts_kn57_mastercraft
  loot06_ui_icon_blackmarket_itemdetail_kn57_mastercraft
  loot06_ui_icon_blackmarket_itemshop_kn57_mastercraft
  loot_ui_icon_callingcards_hades_mastercraft
  loot_ui_icon_stickers_kn57_mastercraft
  ui_icon_callingcards_zm_gauntlet_orange_gold
  ui_icon_callingcards_zm_gauntlet_white_silver
"""
import sys

WEAPONS = [
    "kn57", "hades", "icr", "icr7", "gks", "titan", "maddox", "spitfire",
    "paladin", "auger", "auger_dmr", "saug", "saug_9mm", "vapr", "vapr_xkg",
    "rampart", "rampart_17", "cordite", "swat", "swat_rft", "daemon", "daemon_3xb",
    "kap45", "kap_45", "switchblade", "stingray", "peacekeeper", "locus", "havelina",
    "an94", "vmp", "echohawk", "argus", "m16", "tigershark", "mozu", "strife",
    "sg12", "mog12", "koshka", "outlaw", "sdm", "vendetta", "vkm", "abr", "abr_223",
    "swordfish", "rk7"
]

SPECIALISTS = [
    "ajax", "battery", "crash", "firebreak", "nomad", "prophet", "recon",
    "ruin", "seraph", "torque", "zero", "reaper", "spectre", "outrider"
]

GAUNTLET_MAPS = [
    "voyage", "titanic", "ix", "towers", "escape", "botd", "mansion", "dotn",
    "ancient_evil", "red", "office", "classified", "white", "orange"
]

MEDALS = ["bronze", "silver", "gold", "master", "platinum", "complete", "flawless"]

def generate():
    seen = set()
    def emit(s):
        s = s.strip()
        if s and s not in seen:
            seen.add(s)
            print(s)

    # 1. Gauntlet calling cards
    for m in GAUNTLET_MAPS:
        for medal in MEDALS:
            emit(f"ui_icon_callingcards_zm_gauntlet_{m}_{medal}")
            emit(f"loot_ui_icon_callingcards_zm_gauntlet_{m}_{medal}")
            emit(f"ui_icon_callingcards_zm_{m}_{medal}")
            emit(f"ui_icon_callingcards_gauntlet_{m}_{medal}")

    # 2. Mastercraft calling cards, stickers, tags
    for w in WEAPONS:
        for suffix in ["mastercraft", "signature", "mk2", "reactive", "camo"]:
            emit(f"loot_ui_icon_callingcards_{w}_{suffix}")
            emit(f"loot_ui_icon_stickers_{w}_{suffix}")
            emit(f"loot_ui_icon_tags_{w}_{suffix}")
            emit(f"ui_icon_callingcards_{w}_{suffix}")
            emit(f"ui_icon_stickers_{w}_{suffix}")
            emit(f"ui_icon_tags_{w}_{suffix}")

            # Black market views across seasons loot01..loot12
            for s in range(1, 13):
                loot_pfx = f"loot{s:02d}"
                for view in ["contracts", "itemdetail", "itemshop", "tier", "reserve", "case", "featured"]:
                    emit(f"{loot_pfx}_ui_icon_blackmarket_{view}_{w}_{suffix}")

    # 3. Specialist outfits
    for sp in SPECIALISTS:
        for theme in ["dotd", "cop", "cyber", "gladiator", "barbarian", "knight", "valkyrie", "vampire"]:
            for com in ["com1", "com2", "com3", "com4", "com5"]:
                emit(f"loot_ui_icon_outfit_{theme}_base_decal_{com}_{sp}")
                emit(f"loot_ui_icon_outfit_{theme}_{com}_{sp}")
                emit(f"loot_ui_icon_outfit_{theme}_{sp}")

if __name__ == "__main__":
    generate()
