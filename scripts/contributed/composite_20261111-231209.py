"""Composite world materials of the modern titles, enumerated whole on the GPU box.

Half of the known materials of BO6 are named by a grammar with no words in it: a technique (`twc`,
`tw`, `twcj`, `twck`, `wc`, `twj`, `twk`, `w`), a slash and a star, then two to four layers joined
by `_`, each a number followed by `n`, `dn` or nothing. Two layers (numbers to 20,000) take a second
and are exhausted; three layers (numbers to 8,000) take about an hour per technique on a 3090
and carry about three chance matches each. Four layers: extend the three-layer names by one layer
(methods/subst with insertion), not by enumeration.
"""
from core import box, config, engines, names

TECHNIQUES = ('twc', 'tw', 'twcj', 'twck', 'wc', 'twj', 'twk', 'w')
STAR = '/' + chr(42)


def start(tags, layers, top=None, techniques=TECHNIQUES):
    top = top or (20000 if layers == 2 else 8000)
    job = 'composite%d' % layers
    t = engines.write(config.work('box', job + '_targets.txt'), ('%016x' % x for x in sorted(names.targets(tags, 'material'))))
    d = engines.write(config.work('box', job + '_dict.txt'), ('%d%s' % (i, s) for s in ('n', 'dn', '') for i in range(top + 1)))
    p = engines.write(config.work('box', job + '_prefixes.txt'), (x + STAR for x in techniques))
    return box.sweep(job, tags[0], 'material', t, [d], p, layers)
