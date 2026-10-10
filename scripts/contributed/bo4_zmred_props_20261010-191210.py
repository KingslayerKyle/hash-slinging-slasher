"""Antiquity / Greek mythology glossary from Wikipedia: link titles + article words."""
import json, re, urllib.request, urllib.parse, os
OUT = r'C:\tmp\bo4\glossary'
PAGES = '''List_of_furniture_types
Furniture
Shelf_(storage)
Column
Glossary_of_architecture
List_of_building_materials
List_of_food_preparation_utensils
Cookware_and_bakeware
List_of_light_sources
Container
Barrel
Debris
Rubble
Statue
Fountain
Garden_furniture
Market_(place)
Ship
Galley
Chariot
Cart
Siege_engine
Agricultural_tool
List_of_hand_tools
Basket
Textile
Rope
Candle
Torch
Banner
Sarcophagus
Tomb
Altar
Brazier
Mosaic
Fresco
Scaffolding
Ruins
Cave
Rock_(geology)
Vegetation
List_of_trees_and_shrubs_by_taxonomic_family
Olive
Grape'''.split()
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
open(os.path.join(OUT, 'props.txt'), 'w').write('\n'.join(terms) + '\n')
print('terms', len(terms))
