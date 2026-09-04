#!/usr/bin/env python3
"""Expanded execution sound asset and sound alias generator for Cold War."""

POSTURES = [
    "laststand", "prone", "stand",
    "laststand_vox", "prone_vox", "stand_vox",
    "laststand_exert", "prone_exert", "stand_exert",
    "laststand_exerts", "prone_exerts", "stand_exerts",
    "attacker_laststand", "attacker_prone", "attacker_stand",
    "attacker_laststand_exert", "attacker_prone_exert", "attacker_stand_exert",
    "attacker_laststand_exerts", "attacker_prone_exerts", "attacker_stand_exerts",
    "victim_laststand", "victim_prone", "victim_stand",
    "victim_laststand_exert", "victim_prone_exert", "victim_stand_exert",
    "victim_laststand_exerts", "victim_prone_exerts", "victim_stand_exerts",
    "laststand_dog", "prone_dog", "stand_dog", "whistle",
    "dog_laststand", "dog_prone", "dog_stand",
    "laststand_pet", "prone_pet", "stand_pet",
    "pet_laststand", "pet_prone", "pet_stand",
    "laststand_bird", "prone_bird", "stand_bird",
    "crouch", "crouch_vox", "crouch_exert", "crouch_exerts",
    "kneel", "kneel_vox", "kneel_exert", "kneel_exerts",
]

TAILS = [
    ".ln75.pc.all.snd", ".rn75.pc.all.snd", ".sn75.pc.all.snd",
    ".ll75.pc.all.snd", ".sl75.pc.all.snd", ".rr75.pc.all.snd",
    ".ln75.pc.snd", ".sn75.pc.snd", ".rn75.pc.snd"
]

def generate():
    seen = set()
    def emit(s):
        s = s.strip()
        if s and s not in seen:
            seen.add(s)
            print(s)

    # Search executions from 1 to 400
    for i in range(1, 400):
        id3 = f"{i:03d}"
        id_raw = str(i)

        for post in POSTURES:
            # Sound alias candidates
            emit(f"evt_execution_{id3}_{post}")
            emit(f"evt_execution_{id_raw}_{post}")
            emit(f"evt_exec_{id3}_{post}")
            emit(f"evt_exec_{id_raw}_{post}")
            emit(f"bik_execution_{id3}_{post}")
            emit(f"bik_execution_{id_raw}_{post}")

            # Sound asset candidates
            for folder in [f"exec_{id3}", f"exec_{id_raw}"]:
                for file_prefix in [f"{folder}_{post}", post, f"evt_{folder}_{post}"]:
                    for t in TAILS:
                        emit(f"mpl/executions/{folder}/{file_prefix}{t}")

        # Also emit base bik files
        emit(f"bik_execution_{id3}")
        emit(f"bik_execution_{id_raw}")

if __name__ == "__main__":
    generate()
