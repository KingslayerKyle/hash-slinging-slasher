"""
Targeted generator for Cold War operator MTX execution voice assets and sound aliases:
vox_{op}_mtx_execute_{name} (sound_alias)
vox/scripted/operators/{op}/vox_{op}_mtx_execute_{name}.rn75.pc.en.snd (sound_asset)
"""
import sys

def main():
    operators = [
        'adlr', 'antv', 'bakr', 'bdzr', 'beck', 'frs1', 'frs2', 'fuze', 'grca', 'gstf',
        'hdsn', 'jckl', 'kngs', 'kngt', 'ktsn', 'lazr', 'masn', 'maxi', 'mcln', 'mrs1',
        'mrs2', 'mrs3', 'naga', 'park', 'prce', 'ptnv', 'rmbo', 'rvas', 'sala', 'sims',
        'stch', 'stry', 'weav', 'wolf', 'wood', 'wrth', 'zyna'
    ]

    exec_names = [
        'blitz', 'blitz_00', 'close_eyes_00', 'dead_00', 'dismember_00', 'electric_shock',
        'electric_shock_00', 'esad', 'esad_00', 'fire_00', 'fire_chill', 'fire_chill_00',
        'fire_flamethrower_00', 'fire_match', 'fire_match_00', 'hunt_00', 'kill_machine_00',
        'knife_fight', 'newb', 'newb_00', 'next_00', 'nice_try', 'nice_try_00', 'overkill_00',
        'payback_00', 'point_blank', 'point_blank_00', 'rare', 'rare_00', 'rare_01',
        'rare_02', 'rare_03', 'rare_04', 'rare_05', 'rare_06', 'rare_07', 'rare_08',
        'rare_09', 'rare_10', 'rare_11', 'rare_12', 'rare_13', 'rare_14', 'rare_15',
        'see_hell_00', 'sit_down_00', 'sniper_rifle', 'sniper_rifle_00', 'target_down',
        'worst_nightmare_00'
    ]

    tails = ['.rn75.pc.all.snd', '.rn75.pc.en.snd', '.ln75.pc.all.snd', '.sn75.pc.all.snd']

    out = set()
    for op in operators:
        for en in exec_names:
            # Sound alias
            out.add(f'vox_{op}_mtx_execute_{en}')
            # Sound assets
            for t in tails:
                out.add(f'vox/scripted/operators/{op}/vox_{op}_mtx_execute_{en}{t}')
                out.add(f'vox/scripted/zm_operators/{op}/vox_{op}_mtx_execute_{en}{t}')
                out.add(f'vox/scripted/{op}/vox_{op}_mtx_execute_{en}{t}')

    for name in sorted(out):
        print(name)

if __name__ == "__main__":
    main()
