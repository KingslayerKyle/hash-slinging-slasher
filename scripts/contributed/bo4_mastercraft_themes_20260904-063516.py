#!/usr/bin/env python3
"""Comprehensive Black Market themes and cosmetic images generator for Black Ops 4."""

THEMES = [
    # Mastercraft & Signature skin names
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
    "blinding_glory", "sandstorm", "patriot", "killcano", "plasma_drive", "soul_eater",
    "dday", "afterburner", "afterglow", "incandescent", "deep_voyage", "rising_tide",
    "water_zero", "secretsanta", "melee_club", "melee_coinbag", "melee_slaybell",
    "melee_secretsanta", "melee_stop_sign", "melee_action_figure", "melee_nunchucks",
    "melee_cane", "melee_pickaxe",

    # Characters
    "brutus", "warden", "shadowman", "dempsey", "nikolai", "takeo", "richtofen",
    "marlton", "russman", "stuhlinger", "misty", "tedd", "sergei", "weaver",
    "hudson", "woods", "mason", "reznov", "menendez", "price", "bowman",
    "kravchenko", "dragovich", "steiner", "shaw", "bruno", "diego", "scarlett",
    "replacer", "blackjack", "trejo", "billy", "sal", "finn", "al", "weasel",
    "ajax", "battery", "crash", "firebreak", "nomad", "prophet", "recon",
    "ruin", "seraph", "torque", "zero", "reaper", "spectre", "outrider",

    # Bundles
    "bundle_action_figure", "bundle_full_stop", "bundle_replacer", "bundle_tedd",
    "bundle_zombiearm", "bundle_misty", "bundle_stuhlinger", "bundle_russman",
    "bundle_marlton", "bundle_sergei", "bundle_weaver", "bundle_brutus",
    "bundle_dempsey", "bundle_nikolai", "bundle_takeo", "bundle_richtofen",
    "bundle_woods", "bundle_mason", "bundle_reznov", "bundle_menendez",
    "bundle_hudson", "bundle_price", "bundle_blackjack", "bundle_shadowman",

    # MK2 weapons
    "swat_mk2", "kap45_mk2", "rampart_mk2", "vapr_mk2", "spitfire_mk2", "cordite_mk2",
    "daemon_mk2", "switchblade_mk2", "koshka_mk2", "paladin_mk2", "peacekeeper_mk2",
    "stingray_mk2", "locus_mk2", "an94_mk2", "vmp_mk2", "m16_mk2", "argus_mk2",
    "havelina_mk2", "echohawk_mk2", "tigershark_mk2", "icr_mk2", "gks_mk2", "titan_mk2"
]

SEASONS = [f"loot{s:02d}" for s in range(1, 13)]

def generate():
    seen = set()
    def emit(s):
        s = s.strip()
        if s and s not in seen:
            seen.add(s)
            print(s)

    for theme in THEMES:
        # 1. Direct stickers, callingcards, tags
        emit(f"loot_ui_icon_stickers_{theme}")
        emit(f"loot_ui_icon_callingcards_{theme}")
        emit(f"loot_ui_icon_tags_{theme}")
        emit(f"ui_icon_stickers_{theme}")
        emit(f"ui_icon_callingcards_{theme}")
        emit(f"ui_icon_tags_{theme}")

        # 2. Black Market season icons
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
