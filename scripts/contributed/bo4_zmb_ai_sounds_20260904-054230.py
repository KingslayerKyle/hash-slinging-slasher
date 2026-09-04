"""Systematic generator for Black Ops 4 Zombie AI sound assets.

Uses exact directory structures from bo4_snd_dirs for all zombie enemy types
(werewolf, spartoi, hellephant, gladiator, nosferatu, blightfather, catalyst,
hellhounds, tiger, quads, nos_bat, standard zombie).
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import snapshot

TAILS = (
    ".ln100.pc.snd",
    ".ll100.pc.snd",
    ".sn100.pc.snd",
    ".sl100.pc.snd",
    ".pn100.pc.snd",
    ".pl100.pc.snd",
)

def generate():
    candidates = set()
    
    # Read bo4 sound dirs
    snd_dirs_file = ROOT / "scripts" / "contributed" / "bo4_snd_dirs_20260823-030223.txt"
    all_dirs = [l.strip() for l in snd_dirs_file.read_text().splitlines() if l.strip()]
    zmb_ai_dirs = [d for d in all_dirs if d.startswith("zmb\\ai\\")]
    
    # Enemy prefixes
    enemy_map = {
        "werewolf": ["wwolf_", "werewolf_", ""],
        "spartoi": ["spartoi_", ""],
        "hellephant": ["hellephant_", "elephant_", ""],
        "gladiator": ["gladiator_", "destroyer_", "marauder_", ""],
        "nosferatu": ["nosferatu_", "nos_", ""],
        "nos_bat": ["nos_bat_", "bat_", ""],
        "blightfather": ["blightfather_", "blight_", ""],
        "catalyst": ["catalyst_", ""],
        "hellhounds": ["fly_hellhound_", "hellhound_", ""],
        "tiger": ["tiger_", ""],
        "stoker": ["stoker_", ""],
        "quads": ["quad_", "quads_", ""],
        "standard": ["zmb_", "vox_zmb_", "vox_", ""],
    }

    for d in zmb_ai_dirs:
        # Determine enemy
        parts = d.rstrip("\\").split("\\")
        enemy = parts[1] if len(parts) > 1 else ""
        leaf = parts[-1]
        
        # Base names derived from leaf
        prefixes = enemy_map.get(enemy, [""])
        
        base_stems = set()
        # Leaf action directly
        base_stems.add(leaf)
        if leaf.endswith("_2.0"):
            base_stems.add(leaf[:-4])
        
        # Variations on leaf
        if leaf in ("atk", "attack", "swing", "sword_swipe", "axe_swing", "melee"):
            base_stems.update(["attack", "atk", "swing", "attack_swipe", "swipe", "melee"])
        elif leaf in ("amb", "ambient"):
            base_stems.update(["amb", "ambient", "growl", "idle"])
        elif leaf in ("death", "pain", "scream", "roar", "howl", "growl"):
            base_stems.update(["death", "pain", "scream", "roar", "howl", "growl"])
        elif leaf.startswith("series_"):
            # Inside series_1, series_2, etc. Parent is action (e.g. amb, attack, pain, sprint)
            parent_act = parts[-2] if len(parts) > 2 else "amb"
            base_stems.update([parent_act, f"{parent_act}_{leaf}"])
            
        for pfx in prefixes:
            for stem in base_stems:
                for i in range(25):
                    # Unnumbered and numbered
                    for tail in TAILS:
                        candidates.add(f"{d}{pfx}{stem}_{i:02d}{tail}")
                        candidates.add(f"{d}{pfx}{stem}_{i}{tail}")
                        if i == 0:
                            candidates.add(f"{d}{pfx}{stem}{tail}")
                            candidates.add(f"{d}{pfx}{stem}_lp{tail}")
                            candidates.add(f"{d}{pfx}{stem}_loop{tail}")

    return sorted(candidates)

def main():
    cands = generate()
    print(f"Generated {len(cands):,} candidate names", file=sys.stderr)
    for c in cands:
        print(c)

if __name__ == "__main__":
    main()
