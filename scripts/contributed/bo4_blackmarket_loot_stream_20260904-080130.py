"""Black Market loot stream, itemshop, and contract icons for BO4."""
import sys

def main():
    characters = [
        "marlton", "misty", "russman", "stuhlinger", "tedd", "sergei", "weaver",
        "richtofen", "takeo", "dempsey", "nikolai", "brutus", "hudson", "mason",
        "woods", "menendez", "reznov", "seraph", "ruin", "outrider", "spectre",
        "reaper", "prophet", "battery", "firebreak", "nomad", "torque", "ajax",
        "crash", "zero", "corvus", "sarah_hall", "john_taylor", "diaz", "maretti",
        "hendricks", "shaw", "bruno", "diego", "scarlett", "replacer", "secretsanta"
    ]

    bundles = [
        "action_figure", "rising_tide", "zombiearm", "full_stop", "replacer",
        "tedd", "sergei", "deep_voyage", "water_zero", "afterburner", "afterglow",
        "incandescent", "tactical_unicorn", "gigaswat", "hellscream", "valkyrie",
        "vampire_hunter", "great_lion", "wundergewehr", "triple_play", "party_rock",
        "space_race", "nebula", "street_race", "divinity", "sentinel", "homunculus",
        "death_card", "black_market", "spectral", "cosmic", "solar"
    ]

    weapons = [
        "icr7", "rampart17", "vapr", "kn57", "maddox", "swat", "peacekeeper", "grav",
        "kap45", "daemon3xb", "switchblade", "spitfire", "saug9mm", "cordite", "gks",
        "auger", "abr223", "swordfish", "titan", "hades", "vkm750", "paladin", "outlaw",
        "koshka", "sdm", "locus", "haveloc", "mozu", "strife", "rk7", "sg12", "mog12",
        "stingray", "crossbow", "ballistic_knife", "tigershark", "echohawk", "an94", "vmp",
        "microimg", "reaver", "argus"
    ]

    seasons = []
    for i in range(1, 9):
        seasons.append(f"loot{i:02d}")
        seasons.append(f"loot_{i:02d}")
        seasons.append(f"loot{i}")
        seasons.append(f"loot_{i}")

    cands = set()

    for s in seasons:
        for c in characters:
            cands.add(f"{s}_ui_icon_blackmarket_itemdetail_{c}")
            cands.add(f"{s}_ui_icon_blackmarket_itemshop_{c}")
            cands.add(f"{s}_ui_icon_blackmarket_contracts_{c}")
            cands.add(f"{s}_ui_icon_blackmarket_contracts_{c}_tall")
            cands.add(f"{s}_ui_icon_blackmarket_contracts_{c}_itemdetail")
            cands.add(f"{s}_ui_icon_blackmarket_itemdetail_bundle_{c}")
            cands.add(f"{s}_ui_icon_blackmarket_itemshop_bundle_{c}")
            cands.add(f"{s}_ui_icon_blackmarket_stream_{c}")

        for b in bundles:
            cands.add(f"{s}_ui_icon_blackmarket_itemdetail_{b}")
            cands.add(f"{s}_ui_icon_blackmarket_itemshop_{b}")
            cands.add(f"{s}_ui_icon_blackmarket_contracts_{b}")
            cands.add(f"{s}_ui_icon_blackmarket_contracts_{b}_tall")
            cands.add(f"{s}_ui_icon_blackmarket_contracts_{b}_itemdetail")
            cands.add(f"{s}_ui_icon_blackmarket_itemdetail_bundle_{b}")
            cands.add(f"{s}_ui_icon_blackmarket_itemshop_bundle_{b}")
            cands.add(f"{s}_ui_icon_blackmarket_stream_{b}")

        for w in weapons:
            cands.add(f"{s}_ui_icon_blackmarket_stream_{w}_mastercraft")
            cands.add(f"{s}_ui_icon_blackmarket_stream_mastercraft_{w}")
            cands.add(f"{s}_ui_icon_blackmarket_itemshop_{w}_mastercraft")
            cands.add(f"{s}_ui_icon_blackmarket_itemshop_mastercraft_{w}")
            cands.add(f"{s}_ui_icon_blackmarket_itemdetail_{w}_mastercraft")
            cands.add(f"{s}_ui_icon_blackmarket_itemdetail_mastercraft_{w}")
            cands.add(f"{s}_ui_icon_blackmarket_contracts_{w}_mastercraft")
            cands.add(f"{s}_ui_icon_blackmarket_contracts_{w}_mastercraft_tall")
            cands.add(f"{s}_ui_icon_blackmarket_contracts_{w}_mastercraft_itemdetail")
            cands.add(f"{s}_ui_icon_blackmarket_contracts_mastercraft_{w}")
            cands.add(f"{s}_ui_icon_blackmarket_contracts_mastercraft_{w}_tall")
            cands.add(f"{s}_ui_icon_blackmarket_contracts_mastercraft_{w}_itemdetail")
            cands.add(f"{s}_ui_icon_blackmarket_stream_{w}_mk2")
            cands.add(f"{s}_ui_icon_blackmarket_stream_mk2_{w}")
            cands.add(f"{s}_ui_icon_blackmarket_itemshop_{w}_mk2")
            cands.add(f"{s}_ui_icon_blackmarket_itemdetail_{w}_mk2")
            cands.add(f"{s}_ui_icon_blackmarket_contracts_{w}_mk2")
            cands.add(f"{s}_ui_icon_blackmarket_contracts_{w}_mk2_tall")
            cands.add(f"{s}_ui_icon_blackmarket_contracts_{w}_mk2_itemdetail")

    for cand in sorted(cands):
        sys.stdout.write(cand + "\n")

if __name__ == "__main__":
    main()
