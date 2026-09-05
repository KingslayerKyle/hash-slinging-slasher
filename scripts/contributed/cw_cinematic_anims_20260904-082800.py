"""Generate Cold War MP and Zombies cinematic infiltration and story cutscene animations.

Recovers hundreds of character and prop animations across MP maps (blacksea, cartel, cliffhanger,
gas, kgb, mall, miami, moscow, satellite, tank, tundra) and Zombies maps (tungsten, gold, berlin, amerika).
"""
import sys
import os

def main():
    cands = set()

    # 1. MP Infiltration & Frozen Moment Cinematics
    # Structure: ch_cin_mp_{map}_{faction}_{style}_{shot}_{actor}{weapon}
    mp_maps = [
        'blacksea', 'cartel', 'cliffhanger', 'gas', 'kgb', 'mall', 'miami', 
        'moscow', 'satellite', 'tank', 'tundra', 'armada', 'checkmate', 
        'crossroads', 'pines', 'raid', 'express', 'apocalypse', 'yamantau', 
        'diesel', 'standoff', 'collateral', 'amsterdam', 'rush', 'echelon', 
        'slums', 'zoo', 'drivein'
    ]
    factions = ['cia', 'kgb', 'dgi', 'mi6', 'bnd', 'stasi']
    mp_shots = [f'sh{i:03d}' for i in range(10, 150, 10)] + [f'shot{i:03d}' for i in range(10, 150, 10)]
    mp_chars = [f'ch{i}' for i in range(1, 12)] + [f'pilot{i:02d}' for i in range(1, 5)] + ['player', 'guard']
    mp_weapons = [
        '', '_knife', '_knife_fem', '_pistol', '_pistol_fem', 
        '_barehands', '_barehand', '_launcher', '_launcher_fem', 
        '_rifle', '_fem'
    ]
    styles = ['intro', 'frozen', 'frozen_moment']

    for m in mp_maps:
        for fac in factions:
            for sty in styles:
                pfx = f'ch_cin_mp_{m}_{fac}_{sty}_'
                for s in mp_shots:
                    for c in mp_chars:
                        for w in mp_weapons:
                            cands.add(f'{pfx}{s}_{c}{w}')

    # 2. Zombies Map Intro/Mid/Outro Cinematics
    # Maps: tungsten, gold, berlin, amerika, silver
    zm_maps = ['tungsten', 'gold', 'berlin', 'amerika', 'silver']
    zm_phases = ['intro', 'mid', 'outro', 'mid_pt1', 'mid_pt2', 'outro_pt1', 'outro_pt2']
    zm_shots = [f'sh{i:03d}' for i in range(10, 260, 10)] + [f'shot{i:03d}' for i in range(10, 260, 10)] + [f'shot{i:03d}' for i in range(1, 40)]
    zm_actors = [
        'player1', 'player2', 'player3', 'player4', 'player',
        'krav', 'kravchenko', 'peck', 'raptor1', 'weaver', 'maxis', 'sam', 'sam_maxis', 'ravenov', 
        'grey', 'strauss', 'carver', 'gorev', 'klaus', 'valentina', 'zykov', 'forsaken', 'director',
        'orda', 'soldier', 'guard', 'worker', 'placeholder', 'ch1', 'ch2', 'ch3', 'ch4', 'ch5', 'ch6', 'ch7', 'ch8'
    ] + [f'soldier{i}' for i in range(1, 15)] + [f'worker{i}' for i in range(1, 5)]

    zm_weapons = ['', '_knife', '_knife_fem', '_pistol', '_pistol_fem', '_barehands', '_launcher', '_fem']

    for zm_pfx in ['ch_cin_zm_', 'ch_cin_t9_zm_', 'ch_t9_cin_zm_']:
        for m in zm_maps:
            for ph in zm_phases:
                pfx = f'{zm_pfx}{m}_{ph}_'
                for s in zm_shots:
                    for a in zm_actors:
                        for w in zm_weapons:
                            cands.add(f'{pfx}{s}_{a}{w}')

    # 3. Vehicle & Prop cutscene animations
    for m in zm_maps:
        for ph in zm_phases:
            for s in zm_shots:
                for v in ['heli', 'chinook', 'exfil_heli', 'jeep', 'truck']:
                    cands.add(f'v_t9_cin_zm_{m}_{ph}_{s}_{v}')
                    cands.add(f'v_cin_t9_zm_{m}_{ph}_{s}_{v}')
                for prop in ['cage_eye', 'cage_eye_wire', 'ziptie', 'chair', 'briefcase']:
                    cands.add(f'o_t9_cin_zm_{m}_{ph}_{s}_{prop}')

    out_path = 'candidates_cw_cinematic_anims.txt'
    print(f'Writing {len(cands)} candidates to {out_path}...')
    with open(out_path, 'w', encoding='utf-8') as f:
        for c in sorted(cands):
            f.write(c + '\n')
    print('Done.')

if __name__ == '__main__':
    main()
