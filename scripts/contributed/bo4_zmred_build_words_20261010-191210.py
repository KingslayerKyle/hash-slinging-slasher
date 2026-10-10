"""wordnet.txt (object nouns), detect.txt (LVIS/Open Images classes), zmred_text.txt (the map's own strings)."""
import json, re, os
from nltk.corpus import wordnet as wn
D = r'C:\tmp\bo4\glossary'


def norm(s):
    s = re.sub(r"[^a-z0-9 _-]", '', s.lower()).replace('-', ' ').replace(' ', '_')
    return re.sub('_+', '_', s).strip('_')


def emit(out, s):
    s = norm(s)
    if 3 <= len(s) <= 30:
        out.add(s)
        out.add(s.replace('_', ''))
        out.update(t for t in s.split('_') if len(t) >= 3)


wnw = set()
roots = ['artifact.n.01', 'structure.n.01', 'plant.n.02', 'natural_object.n.01', 'substance.n.01',
         'geological_formation.n.01', 'animal.n.01', 'body_part.n.01', 'material.n.01', 'food.n.01']
for r in roots:
    for s in wn.synset(r).closure(lambda x: x.hyponyms()):
        for l in s.lemma_names():
            if '_' not in l or l.count('_') <= 2:
                emit(wnw, l)
open(os.path.join(D, 'wordnet.txt'), 'w').write('\n'.join(sorted(wnw)) + '\n')

det = set()
for f in ('lvis.yaml', 'open-images-v7.yaml'):
    for line in open(os.path.join(D, 'out', f), encoding='utf-8'):
        m = re.match(r'\s+\d+:\s*(.+)$', line)
        if m:
            emit(det, m.group(1).strip().strip("'\""))
open(os.path.join(D, 'detect.txt'), 'w').write('\n'.join(sorted(det)) + '\n')

txt = set()
for f in ('en_zm_red.raw.jsonl', 'zm_red.loc.jsonl'):
    for line in open(os.path.join(D, 'out', f), encoding='utf-8', errors='replace'):
        try:
            t = json.loads(line, strict=False)['text']
        except ValueError:
            continue
        t = re.sub(r'\^\d|\[\{.*?\}\]', ' ', t)
        words = re.findall(r"[A-Za-z]+", t)
        for w in words:
            if len(w) >= 3:
                txt.add(w.lower())
        for a, b in zip(words, words[1:]):
            txt.add((a + '_' + b).lower())
open(os.path.join(D, 'zmred_text.txt'), 'w').write('\n'.join(sorted(txt)) + '\n')
print('wordnet', len(wnw), 'detect', len(det), 'zm_red text', len(txt))
