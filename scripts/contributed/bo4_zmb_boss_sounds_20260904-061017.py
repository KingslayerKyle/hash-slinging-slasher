#!/usr/bin/env python3
"""Targeted sound asset generator for Black Ops 4 Zombies AI bosses.

Targeted bosses:
  - Werewolf (Dead of the Night)
  - Nosferatu & Crimson Nosferatu (Dead of the Night)
  - Spartoi (Ancient Evil)
  - Tiger (IX)
  - Blightfather (IX / Voyage)
  - Geglenees (Ancient Evil)
  - Brutus / Warden (Blood of the Dead)

All BO4 sound asset names use raw backslashes and --no-fold hashing.
"""

TAILS = [
    ".ln100.pc.snd", ".ll100.pc.snd", ".sn100.pc.snd", ".sl100.pc.snd",
    ".rn100.pc.snd", ".rr100.pc.snd", ".ln100.pc.all.snd"
]

def generate():
    seen = set()
    def emit(s):
        s = s.strip()
        if s and s not in seen:
            seen.add(s)
            print(s)

    # 1. Werewolf
    ww_acts = [
        "howl", "pain", "death", "attack", "ambient", "growl", "leap", "pounce",
        "roar", "spawn", "snarl", "bite", "breath", "idle", "charge", "swipe", "stun"
    ]
    for act in ww_acts:
        for idx in range(25):
            for t in TAILS:
                emit(f"zmb\\ai\\werewolf\\vox\\{act}_2.0\\wwolf_{act}_{idx:02d}{t}")
                emit(f"zmb\\ai\\werewolf\\vox\\{act}_2.0\\ww_{act}_{idx:02d}{t}")
                emit(f"zmb\\ai\\werewolf\\vox\\{act}_2.0\\{act}_{idx:02d}{t}")
                emit(f"zmb\\ai\\werewolf\\vox_{act}_2.0\\wwolf_{act}_{idx:02d}{t}")
                emit(f"zmb\\ai\\werewolf\\vox\\{act}\\wwolf_{act}_{idx:02d}{t}")
                emit(f"zmb\\ai\\werewolf\\vox\\{act}\\{act}_{idx:02d}{t}")

    # 2. Nosferatu & Crimson
    nos_acts = [
        "ambient", "attack_swipe", "death", "leap", "pain", "scream",
        "attack_bite", "bite", "hiss", "spawn", "idle", "feeding", "stun", "charge"
    ]
    for ai in ["nosferatu", "crimson_nosferatu", "nosferatu_crimson", "crimson"]:
        for act in nos_acts:
            for idx in range(25):
                for t in TAILS:
                    emit(f"zmb\\ai\\{ai}\\vox_2.0\\{act}\\{act}_{idx:02d}{t}")
                    emit(f"zmb\\ai\\{ai}\\vox\\{act}\\{act}_{idx:02d}{t}")
                    emit(f"zmb\\ai\\{ai}\\vox_2.0\\{act}\\{ai}_{act}_{idx:02d}{t}")
            for t in TAILS:
                emit(f"zmb\\ai\\{ai}\\vox_2.0\\{act}_lfe{t}")
                emit(f"zmb\\ai\\{ai}\\vox\\{act}_lfe{t}")

    # 3. Spartoi
    spar_acts = ["pain", "death", "attack", "ambient", "spawn", "idle", "scream", "roar", "hit", "bite", "fakedeath", "fall", "rise"]
    for act in spar_acts:
        for idx in range(25):
            for t in TAILS:
                emit(f"zmb\\ai\\spartoi\\vox\\{act}\\{act}_{idx:02d}{t}")
                emit(f"zmb\\ai\\spartoi\\vox_2.0\\{act}\\{act}_{idx:02d}{t}")
                emit(f"zmb\\ai\\spartoi\\vox\\{act}\\spartoi_{act}_{idx:02d}{t}")

    for step_sub in ["step_1", "step_2", "step_3", "step_l", "step_r", "step"]:
        for idx in range(25):
            for t in TAILS:
                emit(f"zmb\\ai\\spartoi\\foley\\{step_sub}\\step_{idx:02d}{t}")
                emit(f"zmb\\ai\\spartoi\\foley\\{step_sub}\\step_{idx}{t}")

    # 4. Tiger
    tiger_acts = ["exp", "roar", "growl", "attack", "death", "pounce", "pain", "bite", "ambient", "idle", "spawn", "leap"]
    for act in tiger_acts:
        for idx in range(20):
            for t in TAILS:
                emit(f"zmb\\ai\\tiger\\{act}\\{act}_tiger_{idx:02d}{t}")
                emit(f"zmb\\ai\\tiger\\{act}\\tiger_{act}_{idx:02d}{t}")
                emit(f"zmb\\ai\\tiger\\vox\\{act}\\{act}_{idx:02d}{t}")
                emit(f"zmb\\ai\\tiger\\vox\\{act}\\tiger_{act}_{idx:02d}{t}")
                emit(f"zmb\\ai\\tiger\\exp\\exp_tiger_{idx:02d}{t}")

    # 5. Blightfather
    bf_acts = ["vomit", "tongue", "spawn", "egg", "attack", "death", "pain", "roar", "ambient", "leap", "idle", "stomp"]
    for act in bf_acts:
        for idx in range(20):
            for t in TAILS:
                emit(f"zmb\\ai\\blightfather\\vox\\{act}\\blight_{act}_{idx:02d}{t}")
                emit(f"zmb\\ai\\blightfather\\vox\\{act}\\bfather_{act}_{idx:02d}{t}")
                emit(f"zmb\\ai\\blightfather\\vox\\{act}\\{act}_{idx:02d}{t}")
                emit(f"zmb\\ai\\blightfather\\{act}\\{act}_{idx:02d}{t}")

    # 6. Geglenees
    geg_acts = ["shield", "blast", "stun", "attack", "death", "pain", "roar", "ambient", "stomp", "eye", "spawn", "idle"]
    for act in geg_acts:
        for idx in range(20):
            for t in TAILS:
                emit(f"zmb\\ai\\geglenees\\vox\\{act}\\geg_{act}_{idx:02d}{t}")
                emit(f"zmb\\ai\\geglenees\\vox\\{act}\\{act}_{idx:02d}{t}")
                emit(f"zmb\\ai\\geglenees\\{act}\\{act}_{idx:02d}{t}")

    # 7. Brutus / Warden
    warden_acts = ["yell", "attack", "slam", "death", "pain", "roar", "ambient", "lock", "spawn", "laugh", "idle"]
    for act in warden_acts:
        for idx in range(20):
            for t in TAILS:
                emit(f"zmb\\ai\\brutus\\vox\\{act}\\brutus_{act}_{idx:02d}{t}")
                emit(f"zmb\\ai\\warden\\vox\\{act}\\warden_{act}_{idx:02d}{t}")
                emit(f"zmb\\ai\\brutus\\vox\\{act}\\{act}_{idx:02d}{t}")
                emit(f"zmb\\ai\\warden\\vox\\{act}\\{act}_{idx:02d}{t}")

if __name__ == "__main__":
    generate()
