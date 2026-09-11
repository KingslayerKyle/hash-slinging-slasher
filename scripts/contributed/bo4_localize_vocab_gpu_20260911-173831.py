"""BO4: GPU 1-2 token gap fill with a vocabulary built from the game's own English subtitles.
The w28447 dump ships localize/en/*.json (38 files, 12 MB); 20,749 distinct words, 9,989 of them
capitalised, and 16,306 absent from every vocabulary built out of already-published asset names.
2,500 of those mixed with 2,000 known tokens, then swept over the image, material, sound_alias and
xmodel prefixes. Generators: C:/tmp/bo4_vox/localize_vocab.py, gen_alias_gpu_inputs.py."""
import os
here = os.path.dirname(os.path.abspath(__file__))
for l in open(os.path.join(here, "bo4_localize_vocab_gpu.txt"), encoding="utf-8"):
    if l.strip(): print(l.strip())
