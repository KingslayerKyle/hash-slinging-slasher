"""
Targeted generator for BO4 Zombie AI Spartoi sounds (vox, foley, movement, fake_death)
and missing pain/death/ambient numbers.
"""
import sys

def main():
    actions = [
        "pain", "death", "ambient", "attack", "attack_swipe", "attack_bite",
        "spawn", "fake_death", "scream", "leap", "taunt", "growl", "snarl",
        "roar", "charge", "alert", "emerge", "hit", "melee"
    ]
    
    foley_actions = [
        "step_2", "step", "step_walk", "step_run", "fs", "fs_walk", "fs_run",
        "mvmt", "movement", "land", "jump", "fall", "emerge", "rattle", "bone",
        "bones", "cloth", "armor", "sword", "shield"
    ]
    
    encodings = [
        ".ln100.pc.snd", ".sl100.pc.snd", ".ll100.pc.snd", ".sn100.pc.snd",
        ".rn75.pc.snd", ".mn100.pc.snd", ".pc.snd"
    ]
    
    out = set()
    
    # 1. zmb\ai\spartoi\vox\<action>\<action>_<num><enc>
    for act in actions:
        # with vox subfolder
        for num in range(30):
            for enc in encodings:
                out.add(f"zmb\\ai\\spartoi\\vox\\{act}\\{act}_{num:02d}{enc}")
                out.add(f"zmb\\ai\\spartoi\\vox\\{act}\\{act}_{num}{enc}")
                out.add(f"zmb\\ai\\spartoi\\vox\\{act}_2.0\\spartoi_{act}_{num:02d}{enc}")
                out.add(f"zmb\\ai\\spartoi\\vox\\{act}_2.0\\{act}_{num:02d}{enc}")
                out.add(f"zmb\\ai\\spartoi\\vox_2.0\\{act}\\{act}_{num:02d}{enc}")
                out.add(f"zmb\\ai\\spartoi\\{act}\\{act}_{num:02d}{enc}")
                
    # 2. zmb\ai\spartoi\fake_death_move and other movement
    moves = ["fakedeath_move", "fake_death_move", "emerge", "spawn", "death_move", "rise", "crawl"]
    suffixes = ["_lp", "_start", "_end", "_00", "_01", "_02", "_03", "_04", ""]
    for m in moves:
        for s in suffixes:
            for enc in encodings:
                out.add(f"zmb\\ai\\spartoi\\fake_death_move\\{m}{s}{enc}")
                out.add(f"zmb\\ai\\spartoi\\movement\\{m}{s}{enc}")
                out.add(f"zmb\\ai\\spartoi\\spawn\\{m}{s}{enc}")

    # 3. Foley: zmb\ai\spartoi\foley\...
    for f in foley_actions:
        for num in range(20):
            for enc in encodings:
                out.add(f"zmb\\ai\\spartoi\\foley\\{f}\\{f}_{num:02d}{enc}")
                out.add(f"zmb\\ai\\spartoi\\foley\\{f}\\{f}_{num}{enc}")
                out.add(f"zmb\\ai\\spartoi\\foley\\{f}_{num:02d}{enc}")
                out.add(f"zmb\\ai\\spartoi\\foley\\step_2\\step_{num:02d}{enc}")
                out.add(f"zmb\\ai\\spartoi\\foley\\step_2\\step_2_{num:02d}{enc}")

    for name in sorted(out):
        print(name)

if __name__ == "__main__":
    main()
