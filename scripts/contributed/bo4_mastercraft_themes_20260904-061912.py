#!/usr/bin/env python3
"""Targeted Black Market generator using specific BO4 weapon/mastercraft skin themes.

Discovered confirmed:
  loot07_ui_icon_blackmarket_contracts_icr7_mastercraft
  loot_ui_icon_stickers_gks_mastercraft
  loot07_ui_icon_blackmarket_itemdetail_tactical_unicorn
  loot07_ui_icon_blackmarket_itemdetail_dempsey
  loot07_ui_icon_blackmarket_itemdetail_nikolai
  loot07_ui_icon_blackmarket_itemdetail_marlton
  loot07_ui_icon_blackmarket_itemdetail_russman
  loot07_ui_icon_blackmarket_itemdetail_stuhlinger
"""

THEMES = [
    # Named Mastercraft themes in BO4
    "tactical_unicorn", "black_knight", "summon", "valkyrie", "carbon_cobra",
    "great_lion", "divinity", "replicant", "boombox", "apex_predator",
    "high_noon", "wundergewehr", "valhalla", "imaginator", "epic_hare",
    "bunnymania", "vampire_hunter", "shogun", "kuromaku", "hades_mastercraft",
    "megashark", "kn57_mastercraft", "icr7_mastercraft", "gks_mastercraft",
    "titan_mastercraft", "maddox_mastercraft", "saug_mastercraft", "strife_mastercraft",
    "mozu_mastercraft", "sg12_mastercraft", "abr_mastercraft", "outlaw_mastercraft",
    "koshka_mastercraft", "paladin_mastercraft", "daemon_mastercraft", "switchblade_mastercraft",
    "rampart_mastercraft", "vapr_mastercraft", "tigershark_mastercraft", "peacekeeper_mastercraft",
    "locus_mastercraft", "stingray_mastercraft", "m16_mastercraft", "an94_mastercraft",
    "vmp_mastercraft", "argus_mastercraft", "echohawk_mastercraft", "havelina_mastercraft",
    "afterburner", "afterglow", "incandescent", "deep_voyage", "rising_tide",
    "water_zero", "secretsanta", "melee_club", "melee_coinbag", "melee_slaybell",
    "melee_secretsanta", "melee_stop_sign", "melee_action_figure", "melee_nunchucks",
    "melee_cane", "melee_pickaxe", "bundle_action_figure", "bundle_full_stop",
    "bundle_replacer", "bundle_tedd", "bundle_zombiearm", "bundle_misty",
    "bundle_stuhlinger", "bundle_russman", "bundle_marlton", "bundle_sergei",
    "bundle_weaver", "bundle_brutus",
    # Characters in Black Market
    "brutus", "dempsey", "nikolai", "takeo", "richtofen", "marlton", "russman",
    "stuhlinger", "misty", "tedd", "sergei", "weaver", "hudson", "woods", "mason",
    "reznov", "menendez", "price", "bowman", "kravchenko", "dragovich", "steiner",
    "shaw", "bruno", "diego", "scarlett"
]

SEASONS = [f"loot{s:02d}" for s in range(1, 13)]

VIEWS = [
    "contracts", "contracts_{theme}_itemdetail", "contracts_{theme}_tall",
    "itemdetail", "itemshop", "featured", "tier", "reserve", "case"
]

def generate():
    seen = set()
    def emit(s):
        s = s.strip()
        if s and s not in seen:
            seen.add(s)
            print(s)

    for theme in THEMES:
        # 1. Stickers, calling cards, tags
        emit(f"loot_ui_icon_stickers_{theme}")
        emit(f"loot_ui_icon_callingcards_{theme}")
        emit(f"loot_ui_icon_tags_{theme}")
        emit(f"ui_icon_stickers_{theme}")
        emit(f"ui_icon_callingcards_{theme}")
        emit(f"ui_icon_tags_{theme}")

        # 2. Black Market icons
        for s in SEASONS:
            emit(f"{s}_ui_icon_blackmarket_contracts_{theme}")
            emit(f"{s}_ui_icon_blackmarket_contracts_{theme}_itemdetail")
            emit(f"{s}_ui_icon_blackmarket_contracts_{theme}_tall")
            emit(f"{s}_ui_icon_blackmarket_itemdetail_{theme}")
            emit(f"{s}_ui_icon_blackmarket_itemshop_{theme}")
            emit(f"{s}_ui_icon_blackmarket_featured_{theme}")
            emit(f"{s}_ui_icon_blackmarket_tier_{theme}")
            emit(f"{s}_ui_icon_blackmarket_reserve_{theme}")
            emit(f"{s}_ui_icon_blackmarket_case_{theme}")

if __name__ == "__main__":
    generate()
