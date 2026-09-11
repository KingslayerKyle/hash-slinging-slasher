"""BO4 music files. The convention, recovered from the two published examples plus these hits, is
mus\<mode>\<map>\<category>\<stem>[_N].<ending> with the stem taken from the music alias
(mus_boss_loop_1 -> mus\zm\zodt8\boss\mus_boss_loop_1.sl100.pc.snd). Probe: every music alias that
the w28447 dump links to a still-unnamed file id, spans of its tokens as stems, against a grid of
mode x map x category directories. Generators: C:/tmp/bo4_vox/music_probe.py, music_dirs2.py."""
import os
here = os.path.dirname(os.path.abspath(__file__))
for l in open(os.path.join(here, "bo4_music_probe.txt"), encoding="utf-8"):
    if l.strip(): print(l.strip())
