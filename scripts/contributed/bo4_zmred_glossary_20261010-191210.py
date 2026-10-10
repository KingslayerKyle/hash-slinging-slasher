"""Antiquity / Greek mythology glossary from Wikipedia: link titles + article words."""
import json, re, urllib.request, urllib.parse, os
OUT = r'C:\tmp\bo4\glossary'
PAGES = '''List_of_Greek_mythological_figures
List_of_Greek_mythological_creatures
Twelve_Olympians
Titans
Greek_primordial_deities
List_of_Roman_deities
Glossary_of_ancient_Roman_religion
Greek_hero_cult
Labours_of_Hercules
Argonauts
Trojan_War
Perseus
Medusa
Pegasus
Delphi
Pythia
Amphictyonic_league
Ancient_Greek_architecture
Classical_order
Ancient_Greek_temple
Glossary_of_architecture
Pottery_of_ancient_Greece
Types_of_ancient_Greek_vases
List_of_ancient_Greek_cities
Ancient_Greek_warfare
Hoplite
Ancient_Greek_clothing
Ancient_Greek_religion
Ancient_Greek_funerary_practices
Greek_underworld
Ancient_Greek_musical_instruments
Ancient_Olympic_Games
Ancient_Greek_cuisine
Acropolis_of_Athens
Parthenon
Mount_Olympus
Oracle
Ancient_Greek_sculpture
Ancient_Rome
Gladiator
Roman_legion
Ancient_Egyptian_deities
Mesopotamian_mythology
Norse_mythology'''.split()
UA = {'User-Agent': 'graywolf-glossary/0.1 (offline research)'}


def api(**kw):
    kw.update(format='json', formatversion=2)
    url = 'https://en.wikipedia.org/w/api.php?' + urllib.parse.urlencode(kw)
    import time
    for k in range(6):
        time.sleep(1.5 * (k + 1))
        try:
            return json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60))
        except Exception as e:
            if '429' not in str(e):
                raise
    raise RuntimeError('429')


titles, words = set(), set()
for p in PAGES:
    try:
        cont = {}
        while True:
            r = api(action='query', titles=p, prop='links', pllimit='max', plnamespace=0, redirects=1, **cont)
            for pg in r['query']['pages']:
                for l in pg.get('links', []):
                    titles.add(l['title'])
            if 'continue' not in r:
                break
            cont = r['continue']
        r = api(action='query', titles=p, prop='extracts', explaintext=1, redirects=1)
        for pg in r['query']['pages']:
            words.update(re.findall(r'[a-z]{3,}', pg.get('extract', '').lower()))
        print(p, len(titles), len(words))
    except Exception as e:
        print('fail', p, e)

terms = set(words)
for t in titles:
    t = re.sub(r'\s*\(.*?\)', '', t).lower()
    t = re.sub(r"[^a-z0-9 ]", '', t).strip()
    if not t or len(t) > 30:
        continue
    toks = t.split()
    if len(toks) <= 3:
        terms.add('_'.join(toks))
        terms.add(''.join(toks))
    terms.update(x for x in toks if len(x) >= 3)
terms = sorted(x for x in terms if 3 <= len(x) <= 30)
open(os.path.join(OUT, 'glossary.txt'), 'w').write('\n'.join(terms) + '\n')
print('terms', len(terms))
