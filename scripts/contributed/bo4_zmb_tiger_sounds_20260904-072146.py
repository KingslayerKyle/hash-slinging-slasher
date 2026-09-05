"""
Targeted generator for BO4 Zombie Tiger sound assets (step, swipe, bite, roar, growl, attack, etc.)
"""
import sys

def main():
    actions = [
        "step", "swipe", "bite", "roar", "growl", "snarl", "pain", "death",
        "ambient", "attack", "leap", "spawn", "pounce", "hit", "run", "walk",
        "turn", "taunt", "alert", "fs", "movement", "land", "fall"
    ]
    
    encodings = [
        ".ln100.pc.snd", ".sl100.pc.snd", ".ll100.pc.snd", ".sn100.pc.snd",
        ".mn100.pc.snd", ".ml100.pc.snd", ".rn75.pc.snd", ".pc.snd"
    ]
    
    out = set()
    
    for act in actions:
        # direct: zmb\ai\tiger\<act>\tiger_<act>_<num><enc>
        # and: zmb\ai\tiger\vox\<act>\tiger_<act>_<num><enc>
        # and: zmb\ai\tiger\foley\<act>\tiger_<act>_<num><enc>
        paths = [
            f"zmb\\ai\\tiger\\{act}\\",
            f"zmb\\ai\\tiger\\vox\\{act}\\",
            f"zmb\\ai\\tiger\\vox_2.0\\{act}\\",
            f"zmb\\ai\\tiger\\foley\\{act}\\",
            f"zmb\\ai\\tiger\\",
        ]
        
        prefixes = [
            f"tiger_{act}_",
            f"tiger_",
            f"{act}_",
        ]
        
        for p in paths:
            for pfx in prefixes:
                for num in range(35):
                    for enc in encodings:
                        out.add(f"{p}{pfx}{num:02d}{enc}")
                        out.add(f"{p}{pfx}{num}{enc}")

    for name in sorted(out):
        print(name)

if __name__ == "__main__":
    main()
