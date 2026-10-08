"""Measure the beginnings and endings Cold War names carry, and write the lists the search reads.

The endings and beginnings a name actually carries are measured rather than guessed, because a
hand written list gets the rare ones right and misses the common ones. A hand list of 33 image
suffixes held five that appear zero times in 752,744 real image names while missing `_cm`, which
appears 12,727 times.

Two sources are measured, and the second is the one nothing else has:

  the Cold War tables      what is already published, which is most of the vocabulary
  the confirmed names      what this work has proved and no table holds

The confirmed names matter out of proportion to their number. The tables show no xmodel with a
directory on it; the confirmed xmodels are full of them -- `clt/`, `cltp/`, `splm/` -- so the
beginnings that reach a whole class of models exist only in what has already been found. A list
measured from the tables alone cannot see them.

Only Cold War is measured. The `_v2` tables are MW2022 and BO6 and teach the wrong conventions,
though every table is still read for exclusion elsewhere.

Writes data/prefixes.txt and data/suffixes.txt, one item per line. What a previous measurement
found is carried forward, so a pass can be a superset of the pass before it -- but only as far as
this group's own corpus still supports it. A capped list has a fixed number of slots, and an entry
no sound table and no confirmed sound name has ever contained is not vocabulary for a sound
search, however long it has been in the file.

There are two groups, and they do not share a budget or a corpus: a general search hunts models,
materials, images and anims, and a sound search hunts `sound_asset` and `sound_alias`. Each
measures its own tables and its own half of the confirmed names.
"""
import settings
import snapshot
import collections, os, sys, glob

# A sound name's encoding tail. One confirmed xmodel genuinely carries one -- somebody at Treyarch
# pasted a sound path onto a model, verified in Saluki -- and it is kept and submitted as the fact
# it is. It must not reach *these* lists, though: they are the committed vocabulary every future
# pass builds candidates from, so learning an ending off one developer's slip would aim the whole
# search wrongly for as long as the file survives. Kept as a name, declined as a lesson.
SOUND_TAILS = (".rn75.", ".ln75.")


def teaches_the_wrong_shape(kind, name):
    return not kind.startswith("sound") and any(tail in name for tail in SOUND_TAILS)

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TABLES = settings.tables_csv()
# One folder, and it used to be named twice. `CONFIRMED` and `FROM_MATERIALS` resolved to the
# same path and `found_names` walked both, so every confirmed name was measured twice: 136,029
# lines on disk reported as 272,034. That halves every threshold the confirmed takes are held to
# -- `FOUND_PREFIX_MIN` of 40 was really a bar of 20 -- and the entries it waved through are a
# good part of what displaced the published vocabulary out of these capped lists.
CONFIRMED = settings.path("findings", "findings")
DATA = os.path.join(HERE, "data")

# The tables that are Cold War rather than a newer game, by their marker density.
# **Order matters.** Each table gets a capped share below, but the shares are taken in this order
# and the ceiling binds long before the list ends -- so a table placed last gets whatever is left,
# which on the first attempt at this was nothing at all: adding the sound tables at the end
# contributed 313 beginnings and **zero** endings. Smallest and least-represented first.
COLD_WAR = [
    # Sound, which these lists were blind to until the sound pools became something we grind.
    # `sound_asset` and `sound_alias` are now ~138,000 of the wanted ids across the two games, and
    # not one beginning or ending had ever been measured from a sound name. Each table gets its
    # own guaranteed places below before global popularity fills the rest, so adding them widens
    # the vocabulary rather than letting the biggest pool crowd the others out.
    "fnv1a_soundbanks_aliases",
    "fnv1a_english_xsounds",
    "fnv1a_xsounds",
    "fnv1a_xanims",
    "fnv1a_xmodels",
    "fnv1a_xmaterials",
    "fnv1a_ximages",
]

# `fnv1a_xsounds` is the Black Ops 4 SAB table and is **mixed**: 8,403 of its names use
# backslashes and 49,189 use forward slashes, none use both. The backslash rows are the SAB
# entries, whose ids are the hash of the unfolded string.
#
# They are measured anyway, with the separator normalised to `/` below, because the *shape* of a
# sound path is the same either way and only the separator differs. Keeping one canonical list
# costs no slots and loses nothing: a `--no-fold` run translates `/` back to `\` as it loads, so
# the same measured vocabulary serves both normalisations. Measuring them twice, once per
# separator, would have spent half the ceiling saying the same thing.

# Since the search peels its endings off the wanted ids rather than appending them to every
# stem, an ending costs a share of one pass over those ids instead of a whole pass over the
# stems. That is what pays for these thresholds being an order of magnitude below the old ones.
ONE_MIN = 30        # a single trailing segment
TWO_MIN = 200       # two trailing segments, which multiply out much faster
THREE_MIN = 200     # three trailing segments, which the old lists never measured at all
PREFIX_MIN = 200    # a beginning, which still multiplies the forward work directly
ROOTED_MIN = 100    # a directory carrying a leading token

# What the confirmed names show is rarer by construction -- there are forty thousand of them
# against a million table names -- so it is counted at a lower bar. Endings are cheaper than
# beginnings, since a beginning multiplies the forward work and an ending does not, so the bar
# for a beginning is higher.
FOUND_ENDING_MIN = 5
FOUND_PREFIX_MIN = 40

# What the published tables' own commonest entries are guaranteed, before the confirmed corpus
# competes for the ceiling.
#
# This is the fix for how the collapse-era lists lost their vocabulary. The confirmed take ran
# first and uncapped: it took 558 of the 700 beginning slots, so `published at >=200` and
# `published directory plus token` were measured, ranked and then truncated away in full. The
# shipped file carried 418 beginnings heading fewer than 200 published names, 225 heading none at
# all, and left out 51 of the 200 commonest published beginnings -- `volume0_state0_` (46,065
# names), `volume1_`, `mc/ui_`, `mc/p9_`. Each re-measure made it strictly worse, because the
# confirmed corpus only ever grows.
#
# Measured rather than hand-listed, so it protects a group nobody has written a `MUST_KEEP` for:
# the sound lists had `{}` for both guards while 289 of the 400 commonest published sound
# beginnings -- heading 173,255 names -- were absent from the file hunting the largest unnamed
# pool in the project.
PUBLISHED_FLOOR_PREFIXES = 150
PUBLISHED_FLOOR_ENDINGS = {"one": 600, "two": 250, "three": 100}

# Hard ceilings on what one measurement may add. Peeling makes an ending nearly free in time,
# but nothing makes it free in accuracy: a run of n candidates against w unnamed ids is expected
# to match n * w / 2^63 names by coincidence however the work is arranged. These keep a pass to
# roughly two or three such names as the searches feed each other and the lists grow.
MOST_ENDINGS = 4800
MOST_PREFIXES = 700

# The fewest names a table can hold and still be believed. The smallest of the seven measured here
# holds tens of thousands, so this only ever catches a read that went wrong rather than a table
# that is genuinely small.
LEAST_PER_TABLE = 5_000

# The most beginning slots one measurement of the confirmed corpus may take. See the note beside
# `PUBLISHED_FLOOR_PREFIXES` for what uncapped cost.
CONFIRMED_PREFIX_SHARE = 150

# What must survive every regeneration, whatever else is measured.
#
# These lists are capped, so measuring a new table does not grow them -- it *displaces* whatever
# ranked lowest. That failure is silent by construction: the file still has its 700 lines and
# still looks healthy, while the beginnings that reach most of the game have quietly gone. It has
# happened once already. Adding the sound tables made `published["directories"]` thousands of deep
# sound paths long, that take had no cap, and it consumed the whole ceiling: `p9_`, `i_`, `mtl_`,
# `attach_` and `vm_` all disappeared in one run.
#
# Nothing downstream would have complained. Every later pass would simply have found less, for as
# long as the file survived. So the list refuses to be written without them.
#
# The counts are how many published names each one heads, measured from the tables, and they are
# the argument for the entry being here. Anything added should carry the same justification.
MUST_KEEP_PREFIXES = {
    "p9_": 77248, "p8_": 66172, "p7_": 42516, "attach_": 27504,   # xmodel
    "mtl_": 343794, "i_": 403889, "c_": 16617,                    # material, image
    "vm_": 18088, "ai_": 11226, "sdr_": 6976,                     # xanim
    "ui_": 31742, "volume0_": 52256,                              # image
    # The twelve material directories. `mc/` heads 496,666 names and `ec/` heads 25, which is
    # exactly why they cannot be chosen by popularity.
    "mc/": 496666, "wc/": 7979, "clt/": 5762, "splm/": 3899, "vd/": 2340, "cltp/": 2278,
    "ei/": 1639, "mcs/": 1638, "vdd/": 110, "el/": 103, "mcp/": 40, "ec/": 25,
}

# The endings the game most depends on, and the same guard as the beginnings above.
#
# This list is capped too, and it displaces the same way. Measuring the sound tables pushed out
# endings covering 115,606 published names in one run -- `_proxy`, `_maps1`, `_maps2` and `_col`
# among them -- and nothing said so: the file still had its 4,800 lines. These forty are the
# most-used trailing segments across models, materials, images and anims, covering 748,684
# published names between them, and the run refuses to produce a list without them.
#
# The numbers are how many published names each ending closes, and they are the argument for the
# entry being here. Anything added should carry the same.
MUST_KEEP_ENDINGS = {
    '_c': 120466, '_01': 105373, '_n': 95007, '_g': 51864,
    '_02': 42455, '_o': 40176, '_m': 35669, '_s': 33768,
    '_03': 20182, '_r': 18651, '_view': 14575, '_world': 14229,
    '_04': 11420, '_metal': 9763, '_decal': 8879, '_dead': 7619,
    '_16': 7607, '_05': 7132, '_a': 6923, '_b': 6705,
    '_proxy': 6043, '_icon': 5754, '_maps1': 5748, '_on': 5660,
    '_maps2': 5262, '_red': 4909, '_e': 4627, '_06': 4625,
    '_white': 4474, '_wet': 4474, '_glass': 4399, '_black': 4214,
    '_1': 4141, '_wood': 3904, '_cst': 3846, '_2': 3773,
    '_base': 3704, '_large': 3625, '_blend': 3581, '_snow': 3458,
}

# Endings a family varies that no table can show, because a model's mesh entry hides them behind
# its own hash.
#
# **Seeded, never appended.** These are hand-written and no measurement can re-derive them, so
# adding them last put them first in line for the ceiling: `_cm` -- named in this file's own
# docstring as the ending a hand list missed, 12,727 occurrences -- along with `_gm`, `_jup`,
# `_lod2`..`_lod6`, `t9_` and `wm_` were all missing from the shipped lists.
EXTRA = ["_lod0", "_lod1", "_lod2", "_lod3", "_lod4", "_lod5", "_lod6", "_s1", "_s2", "_s3",
         "_000", "_bc", "_cm", "_dm", "_gm", "_jup", "_lg", "_m0", "_m1", "_v3", "_v4", "_v5",
         "_v6"]
EXTRA_PREFIX = ["mtl_", "t9_", "wm_", "i_", "c_", "i_mtl_", "i_c_"]


def table_names(table):
    path = os.path.join(TABLES, table + ".csv")
    with open(path, encoding="utf-8", errors="replace") as handle:
        for name in snapshot.database_names(table,handle):
            # Vocabulary is shared by legacy modes; --no-fold restores literal backslashes.
            yield name.replace(chr(92),"/")


def found_names(sound=None, seen=None):
    """The names this project has confirmed, optionally only the sound ones or only the rest.

    Split because the searches are split. A sound ending tried against a model id can only ever
    be a coincidence, and vice versa -- so measuring every confirmed name into both groups spent
    each list's ceiling on vocabulary that cannot match what it hunts. It showed: the general
    endings carried `_00.rn75.pc.en.snd` and six more encoding tails, and the sound beginnings
    carried `mc/`, `mc/mtl_`, `mc/mtl_p8_` and `i_mtl_`, none of which heads a single sound name
    in any of the three sound tables.
    """
    # Each name once, however many files hold it. The recursive glob below reads both the
    # per-game aggregate -- `findings/blkopscw/xmodel.txt` -- and every `run_*/xmodel.txt` whose
    # rows are a subset of it, so a name found last night is measured twice and a name found in
    # three runs four times. Measured on this clone: 78,096 lines for 38,242 distinct names, 2.04x.
    #
    # That is the same doubling that dropping `FROM_MATERIALS` was supposed to have ended, and it
    # has the same consequence: `FOUND_PREFIX_MIN` of 40 is really a bar of 20, `FOUND_ENDING_MIN`
    # of 5 a bar of 2.5, so the confirmed takes are waved through at half the threshold they are
    # written to -- and every confirmed-only entry in the ceiling-damage report reads at twice its
    # true size.
    seen = set() if seen is None else seen

    for folder in (CONFIRMED,):
        # Recursive, because findings are kept per game now -- findings/<game>/ and its run_*
        # folders. A flat glob of the root would quietly measure nothing at all.
        for path in glob.glob(os.path.join(folder, "**", "*.txt"), recursive=True):
            kind = os.path.basename(path).split(".")[0]

            # localizeentry is never measured: those names are CATEGORY/KEY pairs whose plain
            # text already ships in the build, and their conventions belong to no hunted pool.
            if kind.startswith("localizeentry"):
                continue

            if sound is not None and kind.startswith("sound") != sound:
                continue
            with open(path, encoding="utf-8", errors="replace") as handle:
                for line in handle:
                    if teaches_the_wrong_shape(kind, line):
                        continue
                    line = line.strip()
                    if "," in line:
                        # Folded to forward slashes exactly as `table_names` folds them. Black Ops
                        # 4's SAB sound names keep their backslashes, so without this a confirmed
                        # `vox\scripted\mpl\vox_thing` was measured as one enormous prefix with no
                        # directory in it, and two dead backslash entries reached
                        # data/prefixes.txt where nothing could ever match them.
                        name = line.split(",", 1)[1].lower().replace(chr(92), "/")
                        if name not in seen:
                            seen.add(name)
                            yield name


def measure(names):
    """Count the beginnings and endings a set of names carries."""
    one, two, three = collections.Counter(), collections.Counter(), collections.Counter()
    prefixes, directories, rooted = collections.Counter(), collections.Counter(), collections.Counter()

    for name in names:
        head, separator, base = name.rpartition("/")
        directory = head + separator

        parts = base.split("_")
        if len(parts) < 2:
            continue

        one["_" + parts[-1]] += 1
        two["_" + "_".join(parts[-2:])] += 1
        if len(parts) >= 4:
            three["_" + "_".join(parts[-3:])] += 1

        # The directory belongs to the beginning: a material name is a path, and the path is
        # part of what the engine hashes.
        prefixes[directory + parts[0] + "_"] += 1
        prefixes[directory + "_".join(parts[:2]) + "_"] += 1

        if directory:
            prefixes[directory] += 1
            directories[directory] += 1
            rooted[directory + parts[0] + "_"] += 1

            # And every leading segment of it, not only the whole thing.
            #
            # A candidate is `beginning + stem + ending`, and the stem is any piece cut at a mark
            # -- so `fly/footsteps/stakeout/fs_asphalt_walk_01` is reachable from the beginning
            # `fly/` with a long stem just as well as from its entire directory. Counting only the
            # full directory meant deep paths contributed one very specific beginning each and no
            # short ones, and 700 slots cannot hold thousands of those. Measured: it left Black
            # Ops 4's sound names 19.2% reachable, on the largest unnamed pool in the project.
            #
            # The short ones are worth far more per slot: `fly/` heads thousands of names where
            # `fly/footsteps/stakeout_overrides/asphalt_walk/` heads 158.
            for index, character in enumerate(directory[:-1]):
                if character == "/":
                    directories[directory[: index + 1]] += 1

    return dict(one=one, two=two, three=three, prefixes=prefixes,
                directories=directories, rooted=rooted)


def seeded(must_keep, extra):
    """The head of a list: what must survive, then the hand-written entries no measurement can
    reach. Deduplicated, order preserved."""
    items = list(dict.fromkeys(list(must_keep) + list(extra)))
    return items, set(items)


# Measured per table as well as all together. The tables differ in size by an order of
# magnitude, and a single global popularity ranking lets the biggest pool's conventions crowd
# every other pool's out of the ceiling -- the committed lists once carried 9 xanim-shaped
# endings out of 4,800 against 47,859 published xanim names. Each table's own commonest
# beginnings and endings are guaranteed a place first; global popularity fills the rest.
def derive(tables, suffix_file, prefix_file, keep_endings, keep_prefixes, extra_endings=(),
           extra_prefixes=(), sound_group=False, lean_sound=True):
    """Measure one group of tables into its own pair of lists.

    **One budget per search, not one budget shared.** The ceilings exist because coincidental
    matches scale with `stems x beginnings x endings`, and that is a real cost -- but a sound
    ending tried against a model id can only ever be a coincidence, never a match. Mixing every
    table into one capped list therefore made both halves worse: the sound vocabulary displaced
    endings covering 115,606 published names, and in exchange the model passes gained endings that
    could not match anything they were hunting.
    Measured separately, each search gets the whole ceiling for vocabulary that can actually reach
    what it is looking for. Nothing is sacrificed and the coincidence rate per pass goes *down*,
    because no pass carries the other's endings any more.
    """
    global suffixes, seen, prefixes, seen_prefix, per_table, published, confirmed, COLD_WAR
    COLD_WAR = tables

    per_table = {table: measure(table_names(table)) for table in COLD_WAR}

    # Refuse to measure at all against tables that read short, the way every Rust binary here
    # refuses (`tables_look_complete`, `src/lib.rs`).
    #
    # This became load-bearing when the carry started being *filtered*: an entry the previous list
    # held is now dropped when nothing in this run's corpus supports it, so a truncated
    # `cod-name-db` -- a `fetch-tables` killed halfway, a checkout that resolved to a
    # half-populated folder -- would silently delete vocabulary rather than merely fail to add
    # any. Nothing downstream could catch it: `MUST_KEEP` is seeded at the head so it survives by
    # construction, and the floor is recomputed from the very same truncated tables, so it agrees
    # with itself. Before the filter the carry was unconditional and a bad measurement could only
    # under-measure; after it, this check is what keeps AGENTS.md rule 1 true.
    short = [table for table in COLD_WAR if sum(per_table[table]["one"].values()) < LEAST_PER_TABLE]
    if short:
        print("", file=sys.stderr)
        print("REFUSING TO MEASURE: these tables read short, so this corpus is not the corpus:",
              file=sys.stderr)
        for table in short:
            print("    %-28s %d names" % (table, sum(per_table[table]["one"].values())),
                  file=sys.stderr)
        print("", file=sys.stderr)
        print("Refresh them (`bin/windows/fetch-tables.exe`, or `cargo run --release --bin",
              file=sys.stderr)
        print("fetch-tables`) and measure again. Writing from a partial read would drop carried",
              file=sys.stderr)
        print("vocabulary nothing in this run happens to support.", file=sys.stderr)
        raise SystemExit(1)

    published = {key: collections.Counter() for key in
                 ("one", "two", "three", "prefixes", "directories", "rooted")}
    for measured in per_table.values():
        for key in published:
            published[key].update(measured[key])

    confirmed = measure(found_names(sound=sound_group))

    # What this group's own corpus says a word exists at all. A carried entry outside it is
    # vocabulary from somebody else's search: `_00.rn75.pc.en.snd` in a list hunting models, or
    # `mc/` in a list hunting sound. Used on the carry only -- the hand-written extras are seeded,
    # and they are precisely the entries no measurement can support.
    supported = {}
    for name, keys in (("endings", ("one", "two", "three")),
                       ("beginnings", ("prefixes", "directories", "rooted"))):
        supported[name] = set()
        for key in keys:
            supported[name] |= set(published[key]) | set(confirmed[key])

    print(f"measured {sum(published['one'].values())} published names and "
          f"{sum(confirmed['one'].values())} confirmed ones", file=sys.stderr)

    def floor_of(counter, threshold, most):
        """The group's own commonest published entries, which no other take may displace."""
        return [key for key, count in counter.most_common()[:most] if count >= threshold]

    floor_endings = {key: floor_of(published[key], minimum, PUBLISHED_FLOOR_ENDINGS[key])
                     for key, minimum in (("one", ONE_MIN), ("two", TWO_MIN), ("three", THREE_MIN))}
    floor_prefixes = floor_of(published["prefixes"], PREFIX_MIN, PUBLISHED_FLOOR_PREFIXES)

    # Seeded with what must survive, before anything competes for the ceiling. A guard that only
    # *detects* the loss leaves somebody to fix it by hand every time a table is added; taking these
    # first means the loss cannot happen, and the guard below becomes the belt to this pair of braces.
    #
    # The hand-written extras are seeded with them, rather than appended after every take as they
    # used to be. Appending put the one part of these lists that no measurement can reproduce last
    # in the queue for a ceiling that binds every time.
    suffixes, seen = seeded(keep_endings, extra_endings)


    def take(counter, threshold, note, cap=None):
        added = 0
        for key, count in counter.most_common():
            if count < threshold or (cap is not None and added >= cap):
                break
            if key not in seen:
                seen.add(key)
                suffixes.append(key)
                added += 1
        print(f"  {note}: +{added}", file=sys.stderr)


    # What the confirmed names show comes first, because it is what no published table holds and so
    # what the ceiling must never be the thing that drops.
    # Held to a share, not given the whole budget.
    #
    # Confirmed names come first because they are what no published table holds. That was right
    # when there were a few thousand of them. After a night's grinding there were 253,120, which
    # produced 13,199 endings on their own -- nearly three times the entire 4,800 ceiling -- so
    # every published ending was measured, ranked, and then dropped by the cap before it could be
    # written. `_01.rn75.pc.en.snd` ends 30,786 published names and was not carried; sound-file
    # ending reach measured 27.8% with the names sitting in the table being measured.
    #
    # So confirmed keeps its priority but not the whole ceiling. The published tables are the only
    # source of vocabulary this project has not already found, and a list that cannot see them
    # stops learning anything new.
    confirmed_share = max(1, (MOST_ENDINGS * 2) // 5)
    print("endings", file=sys.stderr)

    # The published floor comes first, and it is a take rather than part of the seed on purpose:
    # if anything above it ever grows enough to eat the ceiling, these fall past it and the guard
    # below says so. Seeding them would make the guard unfirable, which is the exact shape of the
    # bug it replaces.
    for key in ("one", "two", "three"):
        take(collections.Counter({k: published[key][k] for k in floor_endings[key]}), 1,
             f"published floor, {key} segment")

    take(confirmed["one"], FOUND_ENDING_MIN, f"confirmed, one segment at >={FOUND_ENDING_MIN}",
         cap=confirmed_share // 3)
    take(confirmed["two"], FOUND_ENDING_MIN, f"confirmed, two segments at >={FOUND_ENDING_MIN}",
         cap=confirmed_share // 3)
    take(confirmed["three"], FOUND_ENDING_MIN, f"confirmed, three segments at >={FOUND_ENDING_MIN}",
         cap=confirmed_share // 3)

    # Each pool's own conventions next, held to a share each, so that what xanim names end in
    # cannot be crowded out of the ceiling by the long tail of a table five times its size.
    # Sound gets a much smaller share than the rest, and the reason is diversity rather than
    # importance. Its endings are hundreds of near-identical variants -- `_01.rn75.pc.en.snd`,
    # `_02.rn75.pc.en.snd`, on and on -- so each slot buys far less reach than a model ending does,
    # and the numbered part is what `confirm_variants` walks anyway. Given the full share they took
    # 418 slots and displaced endings covering 115,606 published names, `_proxy`, `_maps1`, `_maps2`
    # and `_col` among them.
    SOUND_TABLES = {"fnv1a_soundbanks_aliases", "fnv1a_english_xsounds", "fnv1a_xsounds"}

    for table in COLD_WAR:
        pool = table.replace("fnv1a_", "")
        # `lean` exists so that sound endings do not displace general ones -- a sound ending is
        # `_01.rn75.pc.en.snd`, `_02.rn75.pc.en.snd`, on and on, so each slot buys little reach in
        # a general pass.
        #
        # It must NOT apply when building the sound list itself. It did, and the sound list was
        # starved by a rule written to protect the general list *from* it: `_01.rn75.pc.en.snd`
        # alone ends 30,605 published names and was not carried, and only 9 of 4,800 sound endings
        # were dotted at all. Measured effect: sound-file ending reach of 27.8% where the names
        # were sitting right there in the table being measured.
        lean = lean_sound and table in SOUND_TABLES
        take(per_table[table]["one"], ONE_MIN, f"{pool}, one segment", cap=60 if lean else 400)
        take(per_table[table]["two"], TWO_MIN, f"{pool}, two segments", cap=30 if lean else 200)
        take(per_table[table]["three"], THREE_MIN, f"{pool}, three segments", cap=15 if lean else 100)

    take(published["one"], ONE_MIN, f"published, one segment at >={ONE_MIN}")
    take(published["two"], TWO_MIN, f"published, two segments at >={TWO_MIN}")
    take(published["three"], THREE_MIN, f"published, three segments at >={THREE_MIN}")
    prefixes, seen_prefix = seeded(keep_prefixes, extra_prefixes)


    def take_prefix(counter, threshold, note, cap=None):
        added = 0
        for key, count in counter.most_common():
            if count < threshold or (cap is not None and added >= cap):
                break
            if key not in seen_prefix:
                seen_prefix.add(key)
                prefixes.append(key)
                added += 1
        print(f"  {note}: +{added}", file=sys.stderr)


    print("beginnings", file=sys.stderr)
    # Every *shallow* directory first, however little used. Ranking these by popularity keeps `mc/`
    # and drops `ec/`, which heads only 25 names and is the whole of the naming for everything under
    # it -- the failure this take exists to prevent.
    #
    # Deep directories are capped, and that distinction is not cosmetic. Sound paths are directories
    # several segments long and there are thousands of them, so taking every one at threshold 1
    # consumed the entire 700-slot ceiling the moment the sound tables were measured: `p9_`, `i_`,
    # `mtl_`, `attach_` and `vm_` all vanished from the list, and `p9_` alone heads 45,879 xmodels.
    # Shallow ones are few enough to take whole; deep ones have to earn their place.
    def shallow(counter):
        return collections.Counter({k: v for k, v in counter.items() if k.count("/") <= 1})


    def deep(counter):
        return collections.Counter({k: v for k, v in counter.items() if k.count("/") > 1})


    take_prefix(shallow(confirmed["directories"]), 1, "every shallow confirmed directory")
    take_prefix(shallow(published["directories"]), 1, "every shallow published directory")
    take_prefix(collections.Counter({k: published["prefixes"][k] for k in floor_prefixes}), 1,
                "published floor")
    take_prefix(deep(confirmed["directories"]), 1, "deep confirmed directories", cap=40)
    take_prefix(deep(published["directories"]), 1, "deep published directories", cap=120)

    # Capped, and this is the take the collapse came out of. Uncapped it took 558 of 700 slots and
    # left nothing for the published beginnings measured after it.
    take_prefix(confirmed["prefixes"], FOUND_PREFIX_MIN, f"confirmed at >={FOUND_PREFIX_MIN}",
                cap=CONFIRMED_PREFIX_SHARE)

    # Each pool's own commonest beginnings, held to a share each, for the same reason as the
    # endings above.
    for table in COLD_WAR:
        pool = table.replace("fnv1a_", "")
        take_prefix(per_table[table]["prefixes"], PREFIX_MIN, f"{pool} beginnings", cap=60)

    take_prefix(published["prefixes"], PREFIX_MIN, f"published at >={PREFIX_MIN}")
    take_prefix(published["rooted"], ROOTED_MIN, f"published directory plus token at >={ROOTED_MIN}")




    def refuse_if_damaged(kept, dropped, must_keep, floor, counts, what, verb):
        """Refuse to write a list that lost vocabulary the game depends on.

        **It watches what the ceiling cut, which the guard it replaces could not.** That one
        seeded `MUST_KEEP` at the head of the list and truncation cuts the tail, so `missing` was
        empty by construction and "REFUSING TO WRITE" was dead code -- it checked the 24 entries
        that were the only ones incapable of being lost. `eace59b`'s commit message reports "no
        sign of the capped-list displacement" for a run that dropped 344 beginnings, and
        scripts/check_docs.py repeated the mistake, so CI stayed green through the whole collapse.

        The half that does the work is the measured floor, which is a *take* rather than a seed
        and can therefore genuinely fall off the end -- squeeze `MOST_PREFIXES` and it fires. The
        must-keep half is kept as the belt to that pair of braces, and it is honest to say it can
        only fire if the seed itself ever outgrows the ceiling: 31 seeded beginnings against 700,
        47 endings against 4,800. It costs nothing and it would catch exactly that.

        Whatever else the ceiling cuts is reported, not refused -- a capped list has to cut
        something, and the question is only ever whether it cut something that mattered.
        """
        have = set(kept)
        missing = sorted(k for k in must_keep if k not in have)
        lost = sorted((k for k in dropped if k in set(floor)),
                      key=lambda k: -counts.get(k, 0))

        # Counted across both sources. Built from the published tables alone, this said "the
        # ceiling cut 0" while dropping entries the confirmed corpus was the only thing to measure
        # -- 1,608 of the sound group's endings come from there and from nowhere else.
        cut = sorted(((k, counts.get(k, 0)) for k in dropped if counts.get(k, 0)),
                     key=lambda pair: -pair[1])
        report = None
        if cut:
            report = ("  the ceiling cut %d measured %s, the largest being %s (%d measured names)"
                      % (len(cut), what, cut[0][0], cut[0][1]))

        if not missing and not lost:
            return report

        print("", file=sys.stderr)
        print("REFUSING TO WRITE: the measurement dropped %s that must not be lost:" % what,
              file=sys.stderr)
        for key in missing:
            print("    %-16s %s %d published names" % (key, verb, must_keep[key]), file=sys.stderr)
        for key in lost:
            print("    %-16s %s %d measured names (the measured floor)"
                  % (key, verb, counts.get(key, 0)), file=sys.stderr)
        print("", file=sys.stderr)
        print("A capped list displaces rather than grows. Something measured before these has", file=sys.stderr)
        print("crowded them out -- cap that take, but do not ship this.", file=sys.stderr)
        raise SystemExit(1)


    def prepare(name, items, most, guard=None, supported=None):
        """Work out a list without writing it: what this measurement found, then whatever the
        previous list had that it did not reach and this group's corpus still supports, and the
        whole thing held to a ceiling.

        **Nothing reaches the disk here.** Every list this run produces is written together, at
        the very end, once all four have passed their guards -- see `main`. It used to write each
        file as it was worked out, which was harmless only while the guard was dead code: now that
        `refuse_if_damaged` genuinely fires, a refusal on the beginnings would abort having
        already replaced `suffixes.txt`, leaving a new endings list beside an old beginnings list.
        The next `confirm_cw` would then run, and fingerprint, a pair no measurement ever produced
        -- and it would look entirely healthy. The same holds across the two groups.

        The ceiling binds the total rather than only the new part. Carrying forward every item any
        past measurement ever produced is what a superset rule asks for, but the accuracy cost of a
        search is set by how big the lists are and nothing else, so an unbounded carry spends that
        budget on items too rare to have been measured twice. Measured items come first, so the
        carry is what gets cut.
        """
        path = os.path.join(DATA, name)
        kept = []
        stale = 0
        if os.path.exists(path):
            with open(path, encoding="utf-8") as handle:
                previous = [line.strip() for line in handle if line.strip()]
            have = set(items)
            kept = [item for item in previous if item not in have]

            # The carry is where a superset rule and a capped list meet, and it is how vocabulary
            # this group can never match lives for ever. The sound lists carried all 23 of the
            # general list's hand-written endings -- `_lod0`..`_lod6`, `_cm`, `_jup` -- measured
            # at **zero** occurrences across all three sound tables, while the file sat exactly on
            # its ceiling; the general list carried `_00.rn75.pc.en.snd` for the same reason.
            # Taking them out of a group's *seed* does nothing on its own, because the previous
            # file hands them straight back. So the carry is held to what this group's own corpus
            # supports at all, which the seeded entries are exempt from -- they are the ones no
            # measurement can reach.
            if supported is not None:
                before = len(kept)
                kept = [item for item in kept if item in supported]
                stale = before - len(kept)

        whole = (items + kept)[:most]
        cut = (items + kept)[most:]
        dropped = len(cut)

        # Checked against what will actually be written, and against what the ceiling cut to make
        # room. Guarding the input would pass happily while the file that lands is gutted.
        #
        # What it has to say is held back until after this file's own summary line below, because
        # printed here it landed under the *previous* file's summary and read as belonging to it.
        report = guard(whole, cut) if guard is not None else None

        if stale:
            print(f"  {stale} carried item(s) this group can never match, dropped", file=sys.stderr)

        note = f", {dropped} past the ceiling of {most} dropped" if dropped else ""
        print(f"{name}: {len(items)} measured, {len(kept)} carried{note}, {len(whole)} total",
              file=sys.stderr)
        if report:
            print(report, file=sys.stderr)
        return path, whole


    # Both sources, so the report cannot silently omit what only the confirmed corpus measured.
    #
    # Summed across the *keys* for endings, because one, two and three trailing segments are
    # disjoint key spaces -- `_c`, `_wpn_c` and `_ak_wpn_c` are three different endings. Taken as a
    # maximum across the keys for beginnings, because they are not: `measure` counts the same
    # beginning into `prefixes` and `rooted` in the same pass, and the same directory into
    # `prefixes` and `directories`, so adding them reports every pathed beginning at twice its
    # size. `mc/` came out as 1,081,203 where it heads 540,601 names -- and these numbers are the
    # whole evidence a contributor has for whether a ceiling cut mattered.
    ending_counts = collections.Counter()
    beginning_counts = collections.Counter()
    for key in ("one", "two", "three"):
        ending_counts.update(published[key])
        ending_counts.update(confirmed[key])
    for key in ("prefixes", "directories", "rooted"):
        beginning_counts |= published[key]
        beginning_counts |= confirmed[key]
    every_floor_ending = [key for group in floor_endings.values() for key in group]

    pending = [
        prepare(suffix_file, suffixes, MOST_ENDINGS,
                lambda got, cut: refuse_if_damaged(got, cut, keep_endings, every_floor_ending,
                                                   ending_counts, "endings", "closes"),
                supported=supported["endings"]),
        prepare(prefix_file, prefixes, MOST_PREFIXES,
                lambda got, cut: refuse_if_damaged(got, cut, keep_prefixes, floor_prefixes,
                                                   beginning_counts, "beginnings", "heads"),
                supported=supported["beginnings"]),
    ]

    return len(pending[0][1]), len(pending[1][1]), pending


# The two groups. Each is measured on its own and gets the whole ceiling, because each is used by
# a different search: an ordinary pass hunts models, materials, images and anims, and a sound pass
# hunts `sound_asset` and `sound_alias`. Neither carries vocabulary that cannot reach what it is
# looking for.
GROUPS = [
    (
        "the general lists",
        ["fnv1a_xanims", "fnv1a_xmodels", "fnv1a_xmaterials", "fnv1a_ximages"],
        "suffixes.txt",
        "prefixes.txt",
        MUST_KEEP_ENDINGS,
        MUST_KEEP_PREFIXES,
        EXTRA,
        EXTRA_PREFIX,
        False,
    ),
    (
        "the sound lists",
        ["fnv1a_soundbanks_aliases", "fnv1a_english_xsounds", "fnv1a_xsounds"],
        "sound.suffixes.txt",
        "sound.prefixes.txt",
        # No hand-written must-keeps: a sound ending is `_01.rn75.pc.en.snd` and a sound beginning
        # is a path, and neither is something anybody can write down forty of from memory. What
        # protects this pair is the measured floor, which is the whole reason it is measured.
        {},
        {},
        # And none of the general list's hand-written extras, which are model and material shaped
        # -- `_lod3` and `wm_` cannot end or head a sound name, and thirty slots of a capped list
        # is thirty sound beginnings not carried. Dropped from the carry as well as the seed, or
        # the previous file simply hands them back.
        (),
        (),
        # And only the confirmed *sound* names, for the same reason: this list is spent on
        # vocabulary that can reach sound ids or it is spent on nothing.
        True,
    ),
]

# Roughly what a general pass draws on, for reporting what the lists will cost it.
PIECES = 25_000_000
UNNAMED = 270_727

def commit(pending):
    """Write every list this run produced, once all of them have passed their guards.

    `newline=""` rather than the default, which on Windows turns every newline into a CRLF and
    leaves the working copy disagreeing with `.gitattributes` -- the file this project settled the
    question in, after a CRLF/LF mismatch produced a pull request that rewrote 95 lines of an
    unchanged file.
    """
    for path, whole in pending:
        with open(path, "w", encoding="utf-8", newline="") as handle:
            for item in whole:
                handle.write(item + "\n")

    print("", file=sys.stderr)
    print(f"wrote {len(pending)} lists", file=sys.stderr)


def main():
  pending = []

  for title, tables, suffix_file, prefix_file, keep_e, keep_p, extra_e, extra_p, is_sound in GROUPS:
    print("", file=sys.stderr)
    print(f"=== {title} ===", file=sys.stderr)
    # The sound group must not lean on itself -- see `lean` in `derive`.
    endings, beginnings, ready = derive(tables, suffix_file, prefix_file, keep_e, keep_p,
                                        extra_endings=extra_e, extra_prefixes=extra_p,
                                        sound_group=is_sound,
                                        lean_sound=(title != "the sound lists"))
    pending.extend(ready)

    per_stem = (beginnings + 1) * (endings + 1)
    print(f"a stem costs {beginnings + 1} forward hashes and reaches {per_stem} candidates",
          file=sys.stderr)
    print(f"against {PIECES:,} pieces that is "
          f"{PIECES * per_stem * UNNAMED / 9.223e18:.1f} names expected by coincidence",
          file=sys.stderr)

  commit(pending)


if __name__ == "__main__":
    main()
