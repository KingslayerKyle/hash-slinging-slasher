"""Every string of ate47/HashIndex and shiversoftdev/t8-src hashed as a BO4 asset name; hits on unnamed ids."""
import os, re, sys
D = r'C:\tmp\bo4\glossary'
M63 = 0x7FFFFFFFFFFFFFFF
targets = {int(l, 16) for l in open(os.path.join(D, 'targets.txt'))}


def fnv63(s):
    h = 0xCBF29CE484222325
    for b in s.encode('utf-8', 'replace'):
        h = ((h ^ b) * 0x100000001B3) & 0xFFFFFFFFFFFFFFFF
    return h & M63


cands = {}
TOK = re.compile(r'[A-Za-z0-9_$/\\.\-#]{3,160}')
for src in ('hashindex', 't8src'):
    seen = set()
    for root, _, files in os.walk(os.path.join(D, 'out', src)):
        if '.git' in root:
            continue
        for f in files:
            try:
                txt = open(os.path.join(root, f), encoding='utf-8', errors='replace').read()
            except OSError:
                continue
            for m in TOK.findall(txt):
                s = m.lower().replace('\\', '/').strip('#"')
                seen.add(s)
                if '.' in s:
                    seen.add(s.rsplit('.', 1)[0])
    print(src, len(seen), flush=True)
    for s in seen:
        h = fnv63(s)
        if h in targets:
            cands[h] = (s, src)
with open(os.path.join(D, 'sources_hits.txt'), 'w') as f:
    for h, (s, src) in sorted(cands.items()):
        f.write('%016x,%s,%s\n' % (h, s, src))
print('hits', len(cands))
