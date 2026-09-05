"""Recovers Black Market character spray tag images across sets and characters in BO4."""
import sys

def main():
    characters = [
        "ajax", "battery", "crash", "firebreak", "nomad", "prophet", "reaper",
        "ruin", "seraph", "spectre", "torque", "zero", "outrider", "dempsey",
        "nikolai", "richtofen", "takeo", "brutus", "scarlett", "diego", "bruno",
        "shaw", "misty", "marlton", "russman", "stuhlinger", "tedd", "weaver",
        "woods", "mason", "menendez", "reznov", "hudson"
    ]

    cands = set()
    for s in range(1, 10):
        for n in range(1, 20):
            for c in characters:
                cands.add(f"loot_ui_icon_tags_random_set_{s}_{n}_{c}")
                cands.add(f"loot_ui_icon_tags_random_set_{s}_{n:02d}_{c}")

    for cand in sorted(cands):
        sys.stdout.write(cand + "\n")

if __name__ == "__main__":
    main()
