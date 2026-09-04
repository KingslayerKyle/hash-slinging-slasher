"""
Targeted generator for BO4 Zombies level/map interactive sound assets:
- zm_escape (Alcatraz): crane, catwalk, gondola
- zm_office (Classified): defcon alarms and switches, easter egg interactives
- zm_zodt8 (Voyage of Despair): gate mechanisms, sentinel artifact
- zm_orange (Tag der Toten): ziplines, dynamite placement, fuses, and explosions
"""
import sys

def main():
    out = set()
    encs = [".ln100.pc.snd", ".ll100.pc.snd", ".sn100.pc.snd", ".sl100.pc.snd", ".mn100.pc.snd", ".ml100.pc.snd", ".rn75.pc.snd"]
    
    # 1. zm_escape: crane & catwalk
    crane_actions = ["dock", "undock", "start", "stop", "lp", "move", "move_lp", "swing", "drop", "lift", "chain", "cable", "motor_start", "motor_stop", "creak", "alarm"]
    catwalk_actions = ["door_open", "door_close", "gate_open", "gate_close", "alarm", "siren", "sparks", "collapse", "creak", "light"]
    for a in crane_actions:
        for enc in encs:
            out.add(f"zmb\\level\\zm_escape\\crane\\crane_{a}{enc}")
    for a in catwalk_actions:
        for enc in encs:
            out.add(f"zmb\\level\\zm_escape\\catwalk\\catwalk_{a}{enc}")
            
    # 2. zm_office: defcon
    defcon_actions = ["alarm", "alarm_lp", "switch", "switch_flip", "lever", "press", "activate", "light", "success", "fail", "siren"]
    for a in defcon_actions:
        for enc in encs:
            out.add(f"zmb\\level\\zm_office\\defcon\\defcon_{a}{enc}")
            for i in range(1, 6):
                out.add(f"zmb\\level\\zm_office\\defcon\\defcon_{i}_{a}{enc}")

    # 3. zm_zodt8: gate & artifact
    gate_actions = ["open", "close", "start", "stop", "creak", "rattle", "hit", "lock", "unlock"]
    artifact_actions = ["lp", "start", "stop", "activate", "deactivate", "pickup", "place", "glow", "hum", "pulse", "charge", "beam"]
    for a in gate_actions:
        for enc in encs:
            out.add(f"zmb\\level\\zm_zodt8\\gate\\gate_{a}{enc}")
    for a in artifact_actions:
        for enc in encs:
            out.add(f"zmb\\level\\zm_zodt8\\artifact\\artifact_{a}{enc}")

    # 4. zm_orange: zipline & dynamite
    zipline_actions = ["lp", "start", "stop", "attach", "detach", "ride", "ride_lp", "travel", "travel_lp", "arrive", "depart", "cable", "handle"]
    dynamite_actions = ["explode", "place", "plant", "pickup", "fuse_lp", "fuse", "fuse_burn", "fuse_burn_lp", "ignite", "throw", "hit", "craft"]
    for a in zipline_actions:
        for enc in encs:
            out.add(f"zmb\\level\\zm_orange\\zipline\\zipline_{a}{enc}")
    for a in dynamite_actions:
        for enc in encs:
            out.add(f"zmb\\level\\zm_orange\\dynamite\\dynamite_{a}{enc}")

    for name in sorted(out):
        print(name)

if __name__ == "__main__":
    main()
