"""BO4 sound files named in the third round, after the 3-token alias sweep added 192 aliases.

The w28447 acts dump links each sound file id to its alias (plaintext or "#hash_<id>"). Files whose
alias was only a hash were unreachable; once the alias itself is named by the GPU alias pass, the
file becomes a target again and the voice-over rule applies: the alias IS the file stem, under
en\\vox\\scripted\\<dir>\\<speaker>\\<alias>_<NN>.<ending>. Exact-id match only.
"""

NAMES = r"""
en\vox\scripted\mpl\batt\vox_batt_ae_seek_mini_game_win_00.sn100.pc.snd
en\vox\scripted\mpl\batt\vox_batt_ae_seek_mini_game_win_01.sn100.pc.snd
en\vox\scripted\mpl\batt\vox_batt_ae_seek_mini_game_win_02.sn100.pc.snd
en\vox\scripted\mpl\batt\vox_batt_ae_seek_mini_game_win_03.sn100.pc.snd
en\vox\scripted\mpl\cras\vox_cras_ae_seek_mini_game_win_00.sn100.pc.snd
en\vox\scripted\mpl\cras\vox_cras_ae_seek_mini_game_win_01.sn100.pc.snd
en\vox\scripted\mpl\cras\vox_cras_ae_seek_mini_game_win_02.sn100.pc.snd
en\vox\scripted\mpl\cras\vox_cras_ae_seek_mini_game_win_03.sn100.pc.snd
en\vox\scripted\mpl\engi\vox_engi_ae_seek_mini_game_win_00.sn100.pc.snd
en\vox\scripted\mpl\engi\vox_engi_ae_seek_mini_game_win_01.sn100.pc.snd
en\vox\scripted\mpl\engi\vox_engi_ae_seek_mini_game_win_02.sn100.pc.snd
en\vox\scripted\mpl\engi\vox_engi_ae_seek_mini_game_win_03.sn100.pc.snd
en\vox\scripted\mpl\fire\vox_fire_ae_seek_mini_game_win_00.sn100.pc.snd
en\vox\scripted\mpl\fire\vox_fire_ae_seek_mini_game_win_01.sn100.pc.snd
en\vox\scripted\mpl\fire\vox_fire_ae_seek_mini_game_win_02.sn100.pc.snd
en\vox\scripted\mpl\fire\vox_fire_ae_seek_mini_game_win_03.sn100.pc.snd
en\vox\scripted\mpl\noma\vox_noma_ae_seek_mini_game_win_00.sn100.pc.snd
en\vox\scripted\mpl\noma\vox_noma_ae_seek_mini_game_win_01.sn100.pc.snd
en\vox\scripted\mpl\noma\vox_noma_ae_seek_mini_game_win_02.sn100.pc.snd
en\vox\scripted\mpl\noma\vox_noma_ae_seek_mini_game_win_03.sn100.pc.snd
en\vox\scripted\mpl\outr\vox_outr_ae_seek_mini_game_win_00.sn100.pc.snd
en\vox\scripted\mpl\outr\vox_outr_ae_seek_mini_game_win_01.sn100.pc.snd
en\vox\scripted\mpl\outr\vox_outr_ae_seek_mini_game_win_02.sn100.pc.snd
en\vox\scripted\mpl\outr\vox_outr_ae_seek_mini_game_win_03.sn100.pc.snd
en\vox\scripted\mpl\prop\vox_prop_ae_seek_mini_game_win_00.sn100.pc.snd
en\vox\scripted\mpl\prop\vox_prop_ae_seek_mini_game_win_01.sn100.pc.snd
en\vox\scripted\mpl\prop\vox_prop_ae_seek_mini_game_win_02.sn100.pc.snd
en\vox\scripted\mpl\prop\vox_prop_ae_seek_mini_game_win_03.sn100.pc.snd
en\vox\scripted\mpl\reco\vox_reco_ae_seek_mini_game_win_00.sn100.pc.snd
en\vox\scripted\mpl\reco\vox_reco_ae_seek_mini_game_win_01.sn100.pc.snd
en\vox\scripted\mpl\reco\vox_reco_ae_seek_mini_game_win_02.sn100.pc.snd
en\vox\scripted\mpl\reco\vox_reco_ae_seek_mini_game_win_03.sn100.pc.snd
en\vox\scripted\mpl\ruin\vox_ruin_ae_seek_mini_game_win_00.sn100.pc.snd
en\vox\scripted\mpl\ruin\vox_ruin_ae_seek_mini_game_win_01.sn100.pc.snd
en\vox\scripted\mpl\ruin\vox_ruin_ae_seek_mini_game_win_02.sn100.pc.snd
en\vox\scripted\mpl\ruin\vox_ruin_ae_seek_mini_game_win_03.sn100.pc.snd
en\vox\scripted\mpl\sera\vox_sera_ae_seek_mini_game_win_00.sn100.pc.snd
en\vox\scripted\mpl\sera\vox_sera_ae_seek_mini_game_win_01.sn100.pc.snd
en\vox\scripted\mpl\sera\vox_sera_ae_seek_mini_game_win_02.sn100.pc.snd
en\vox\scripted\mpl\sera\vox_sera_ae_seek_mini_game_win_03.sn100.pc.snd
en\vox\scripted\mpl\spec\vox_spec_ae_seek_mini_game_win_00.sn100.pc.snd
en\vox\scripted\mpl\spec\vox_spec_ae_seek_mini_game_win_01.sn100.pc.snd
en\vox\scripted\mpl\spec\vox_spec_ae_seek_mini_game_win_02.sn100.pc.snd
en\vox\scripted\mpl\spec\vox_spec_ae_seek_mini_game_win_03.sn100.pc.snd
en\vox\scripted\mpl\swat\vox_swat_ae_seek_mini_game_win_00.sn100.pc.snd
en\vox\scripted\mpl\swat\vox_swat_ae_seek_mini_game_win_01.sn100.pc.snd
en\vox\scripted\mpl\swat\vox_swat_ae_seek_mini_game_win_02.sn100.pc.snd
en\vox\scripted\mpl\swat\vox_swat_ae_seek_mini_game_win_03.sn100.pc.snd
en\vox\scripted\mpl\zero\vox_zero_ae_seek_mini_game_win_00.sn100.pc.snd
en\vox\scripted\mpl\zero\vox_zero_ae_seek_mini_game_win_01.sn100.pc.snd
en\vox\scripted\mpl\zero\vox_zero_ae_seek_mini_game_win_02.sn100.pc.snd
en\vox\scripted\mpl\zero\vox_zero_ae_seek_mini_game_win_03.sn100.pc.snd
""".strip().splitlines()

for n in NAMES:
    n = n.strip()
    if n:
        print(n)
