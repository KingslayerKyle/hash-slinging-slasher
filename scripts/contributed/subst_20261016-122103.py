"""One token of a known name replaced by (or a word inserted beside it from) the type's vocabulary.

Every known name of the kind in the given games is a skeleton. The vocabulary is the kind's own
tokens (seen `min_count` times), then the other kinds' tokens (seen `other_min` times), or the
words of a file the names do not already use (a wiki, a glossary). Each round's hits are the next
round's skeletons, which fills families that vary in several places.
Measured 2026-10-11 on BO6/MWIII/BO7/MWII: 117k names (87k aliases) at 20k words, then 42k more
with 50k words and insertion; the Call of Duty wiki's page titles as the word file: 1.5k.
"""
import collections
import re

from core import config, engines, games, names

CUT = re.compile('[_/.]')


def vocabulary(tags, kind, min_count, other_min, max_words):
    """The kind's own tokens first, then the other kinds'. Counted from the tables in one pass each,
    without holding the names (tags may also be the old list of loaded tables: then it is used as is)."""
    own, other = collections.Counter(), collections.Counter()
    for t in tags:
        if isinstance(t, dict):                       # already loaded tables
            for k, table in t.items():
                for name in table.values():
                    if names.usable(name):
                        (own if k == kind else other).update(set(CUT.split(name)))
        else:
            for k, c in names.tokens(t).items():
                (own if k == kind else other).update(c)
    chosen = [w for w, c in own.most_common(max_words) if c >= min_count and w]
    have = set(chosen)
    chosen += [w for w, c in other.most_common() if c >= other_min and w and w not in have][:max(0, max_words - len(chosen))]
    return chosen, set(own) | set(other)


def run(tags, kind, words_file=None, insert=False, max_words=20000, min_count=2, other_min=5, rounds=6, log=print,
        skeletons_file=None, gpu=False):
    assert games.same_family(tags, kind), 'these games do not hash this kind alike: run them apart'
    known_by_game = [names.known(t, [kind]) for t in tags]
    skeletons = {n for k in known_by_game for n in k[kind].values() if names.usable(n)}
    if skeletons_file:      # names derived elsewhere (a linked asset's name) stand in for the known ones
        skeletons = {l.strip() for l in open(skeletons_file, encoding='utf-8') if l.strip()}
    targets = names.targets(tags, kind)
    words, used = vocabulary(tags, kind, min_count, other_min, max_words)
    if words_file:
        listed = dict.fromkeys(l.strip().lower() for l in open(words_file, encoding='utf-8'))
        words = [w for w in listed if w and w not in used]
    f = [config.work('subst', '%s_%s.txt' % (kind, x)) for x in ('targets', 'skeletons', 'words')]
    found, seen, new = {}, set(skeletons), sorted(skeletons)
    if skeletons_file:
        seen |= {n for k in known_by_game for n in k[kind].values()}
    for r in range(rounds):
        engines.write(f[0], ('%016x' % t for t in targets))
        engines.write(f[1], new)
        engines.write(f[2], words)
        log('subst %s round %d: %d targets, %d skeletons, %d words' % (kind, r + 1, len(targets), len(new), len(words)))
        ops = 'both' if insert else 'replace'
        if gpu:        # same candidates on the GPU box (tools/gpu/subst_gpu.cu)
            from core import box
            hits = box.gpu_engine('subst_gpu', tags[0], kind, f, SUBST_OPS=ops)
        else:
            hits = engines.run('subst', tags[0], kind, f, SUBST_OPS=ops)
        new = []
        for i, name in hits:
            if name not in seen:
                seen.add(name)
                new.append(name)
                found[name] = i
                targets.discard(i)
        log('  %d new names' % len(new))
        if not new or not targets:
            break
    return found
