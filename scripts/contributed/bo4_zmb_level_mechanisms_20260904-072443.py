"""
Targeted generator for BO4 Zombies level-specific sound assets:
- zm_escape (Alcatraz/Blood of the Dead): gondola, catwalk, cellblock, warden, docks, citadel, etc.
- zm_office (Pentagon/Classified): ee reels, crates, phones, elevators, teleporters, etc.
- other maps: zm_mansion, zm_towers, zm_zodt8, zm_white, zm_orange, zm_red
"""
import sys

def main():
    out = set()
    encs = [".ln100.pc.snd", ".ll100.pc.snd", ".sn100.pc.snd", ".sl100.pc.snd", ".mn100.pc.snd", ".ml100.pc.snd", ".rn75.pc.snd"]
    
    # 1. zm_escape gondola
    gondola_verbs = [
        "start", "stop", "lp", "loop", "run", "run_lp", "move", "move_lp", "arrive",
        "depart", "travel", "travel_lp", "slow", "fast", "bell", "lever", "switch",
        "gate_open", "gate_close", "door_open", "door_close", "gate", "door", "chain",
        "cable", "motor_start", "motor_stop", "motor_lp", "motor_run", "brake",
        "creak", "creak_lp", "rattle", "hit", "dock", "undock", "click", "ding",
        "buzzer", "alarm", "horn", "power_on", "power_off"
    ]
    for v in gondola_verbs:
        for enc in encs:
            out.add(f"zmb\\level\\zm_escape\\gondola\\gondola_{v}{enc}")
            out.add(f"zmb\\level\\zm_escape\\gondola\\{v}{enc}")
            out.add(f"zmb\\level\\zm_escape\\{v}{enc}")

    # 2. zm_office ee / mechanisms
    ee_items = [
        "reel", "tape_reel", "tape", "film", "slide", "bottle", "crate", "phone",
        "telephone", "punch_card", "card", "key", "keycard", "code", "paper",
        "picture", "photo", "clock", "knob", "dial", "switch", "lever", "button",
        "fuse", "valve", "trap", "defcon", "teleporter", "elevator", "door", "gate",
        "cabinet", "desk", "drawer", "safe", "lock", "padlock", "breaker", "box"
    ]
    ee_actions = [
        "place", "pickup", "insert", "remove", "take", "drop", "put", "use",
        "activate", "deactivate", "open", "close", "start", "stop", "lp", "loop",
        "play", "rewind", "fastforward", "press", "push", "pull", "turn", "spin",
        "crank", "click", "clunk", "hit", "shatter", "break", "hum", "hum_lp",
        "buzz", "ring", "ring_lp", "dial", "hangup", "pickup_phone", "beep"
    ]
    for item in ee_items:
        for act in ee_actions:
            for enc in encs:
                out.add(f"zmb\\level\\zm_office\\ee\\{item}_{act}{enc}")
                out.add(f"zmb\\level\\zm_office\\ee\\{act}_{item}{enc}")
                out.add(f"zmb\\level\\zm_office\\{item}_{act}{enc}")

    # 3. Across other maps
    maps = ["zm_escape", "zm_office", "zm_mansion", "zm_towers", "zm_zodt8", "zm_white", "zm_orange", "zm_red"]
    cats = ["ee", "gondola", "elevator", "teleporter", "portal", "trap", "power", "pap", "box"]
    for m in maps:
        for cat in cats:
            for item in ["generator", "lever", "switch", "door", "gate", "valve", "trap", "box"]:
                for act in ["start", "stop", "lp", "loop", "open", "close", "activate", "deactivate"]:
                    for enc in encs:
                        out.add(f"zmb\\level\\{m}\\{cat}\\{item}_{act}{enc}")
                        out.add(f"zmb\\level\\{m}\\{item}_{act}{enc}")

    for name in sorted(out):
        print(name)

if __name__ == "__main__":
    main()
