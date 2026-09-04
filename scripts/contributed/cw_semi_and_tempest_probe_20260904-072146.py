"""
Targeted probe expanding around recent Cold War material discoveries:
- tempest crystals variations (singular/plural and body parts/slots, plus image maps)
- civ_truck_semi_80s components, color variations, part letters (a-h), and snow/rust variants
"""
import sys

def main():
    out = set()
    
    # 1. Tempest crystal / crystals
    tempest_stems = [
        "mtl_t9_zmb_tempest_crystal",
        "mtl_t9_zmb_tempest_crystals",
        "mtl_t9_zmb_tempest",
        "mtl_t9_zmb_tempest_elite",
        "mtl_t9_zmb_tempest_disc",
        "mtl_t9_zmb_tempest_core",
    ]
    parts = [
        "", "_chest", "_head", "_arm", "_leg", "_torso", "_back", "_hand", "_foot",
        "_pelvis", "_spine", "_shoulder", "_knee", "_elbow", "_eye", "_eyes", "_face",
        "_mouth", "_heart", "_core", "_glow", "_fx", "_shard", "_shards", "_cluster",
        "_clusters", "_ribs", "_horn", "_horns", "_crystal", "_crystals", "_weakpoint",
        "_armor", "_body", "_limbs", "_rock", "_rocks"
    ]
    variants = ["", "_red", "_blue", "_purple", "_orange", "_green", "_yellow", "_dark", "_glow", "_snow"]
    
    img_suffixes = ["_c", "_n", "_g", "_m", "_s", "_o", "_ao", "_e", "_emissive", "_mask", "_col", "_clr", "_c_alpha", "_s_alpha", "_rough", "_glw"]
    
    for stem in tempest_stems:
        for p in parts:
            for v in variants:
                base = f"{stem}{p}{v}"
                out.add(f"mc/{base}")
                out.add(f"wc/{base}")
                out.add(f"clt/{base}")
                out.add(base)
                for sfx in img_suffixes:
                    out.add(f"i_{base}{sfx}")
                    out.add(f"{base}{sfx}")

    # 2. civ_truck_semi_80s variations
    # Observed:
    # mc/mtl_veh_t9_civ_truck_semi_80s_door_metal_paint_a_beig_snow
    # mc/mtl_veh_t9_civ_truck_semi_80s_wheel_back_metal_paint_c_snow
    # mc/mtl_veh_t9_civ_truck_semi_80s_base_bumper_metal_paint_[d,e,f]
    # mc/mtl_veh_t9_civ_truck_semi_80s_base_chassis_b_metal_paint_[c,d]
    # mc/mtl_veh_t9_civ_truck_semi_80s_base_body_front_d_plastic_orange_snow
    # mc/mtl_veh_t9_civ_truck_semi_80s_base_body_roof_reflector_snow
    
    parts_truck = [
        "base_body", "base_body_front", "base_body_rear", "base_body_side", "base_body_roof",
        "base_bumper", "base_chassis", "base_chassis_a", "base_chassis_b",
        "door", "door_front", "door_rear", "door_left", "door_right",
        "wheel", "wheel_front", "wheel_back", "wheel_rear",
        "roof", "roof_reflector", "roof_light", "roof_lights",
        "front", "rear", "grille", "hood", "cab", "fender", "exhaust", "tank", "step",
        "interior", "glass", "window", "windows", "windshield", "mirror", "mirrors",
        "headlight", "headlights", "taillight", "taillights"
    ]
    
    letters = ["", "_a", "_b", "_c", "_d", "_e", "_f", "_g", "_h", "_01", "_02", "_03", "_04"]
    
    mat_types = [
        "", "_plastic", "_metal", "_metal_paint", "_paint", "_chrome", "_rubber", "_glass",
        "_reflector", "_plastic_black", "_plastic_grey", "_plastic_orange"
    ]
    
    colors = [
        "", "_orange", "_blue", "_red", "_green", "_yellow", "_white", "_black",
        "_grey", "_gray", "_silver", "_brown", "_beig", "_beige", "_rust"
    ]
    
    states = ["", "_snow", "_mud", "_dirt", "_wet", "_damage", "_dmg", "_dest", "_burnt"]
    
    for pt in parts_truck:
        for let in letters:
            for mt in mat_types:
                for col in colors:
                    for st in states:
                        base = f"mtl_veh_t9_civ_truck_semi_80s_{pt}{let}{mt}{col}{st}"
                        out.add(f"mc/{base}")
                        out.add(f"wc/{base}")
                        out.add(base)
                        for sfx in img_suffixes:
                            out.add(f"i_{base}{sfx}")

    for name in sorted(out):
        print(name)

if __name__ == "__main__":
    main()
