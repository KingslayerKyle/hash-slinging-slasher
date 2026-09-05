#!/usr/bin/env python3
"""Cores harvested from the pools this project never files, offered to the pools it does.

Every method here seeds from names known to be real, and the usual sources are the published
tables and this project's own findings -- both of which describe the *targeted* asset types.
But a game holds a great many assets in types nobody submits: script bundles, fx, lua files,
ai types, rumbles, cameras. Those names are recovered a different way (they are read out of the
build rather than cracked), they are verifiably real in these exact two titles, and their
vocabulary has never been fed back into the search.

That matters because the cross-era negatives are total -- a newer title's published names return
zero against these games, because the newer engines renamed rather than inherited. This corpus
has the opposite property: it is game-native. A spawner called `spawner_zm_gegenees` and a script
bundle called `aib_t9_vign_cust_zm_silver_steiner_left_levitate` are Black Ops 4 and Cold War
strings, so the characters, locations and systems they name are the ones these games' models and
materials are named after too.

What this prints is the part of that vocabulary the search cannot currently express: every
contiguous run of one to four underscore-separated tokens that carries at least one token no
name we already hold has ever used. Those are stems for a plan -- `confirm_plan` multiplies them
by the measured beginnings and endings, which is three orders of magnitude faster than printing
the cross product from here.

    python untargeted_pool_cores.py <names.txt>... > cores.txt

Input is one name per line, or `hash,name`. Held names are read from `all_names/` and the
published tables, so "novel" means novel against everything, not against one game.
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAX_TOKENS = 4
MIN_LEN = 4

# Decorations that say which mode or title a name belongs to rather than what the asset is.
# Stripping them exposes the core, which is the part that carries across into a model name.
LEADING = re.compile(r"^(spawner|archetype|aib|aibh|ai|vign|cust)_")
TITLE = re.compile(r"^(bo3|bo4|bo5|boct|t7|t8|t9|p7|p8|p9|zm|mp|wz|sr|cp|zmb)_")


# Pools whose names are code and data rather than content. A lua file, a script parse tree or a
# ui model struct is named after a source file or a widget, so its vocabulary (`_lua`, `uieditor_`,
# `lobbyprocessnavzm`) describes the program, not the game -- and no model, material or image is
# ever named after it. Everything not listed here is kept: fx, cameras, vehicles, characters,
# ai types, destructibles, attachments and the rest are named after the things they depict.
CODE_POOLS = {
    "luafile", "scriptparsetree", "scriptparsetreeforced", "script_using", "script_using_mp",
    "script_using_wz", "script_using_zm", "keyvaluepairs", "ddl", "stringtable",
    "structured_table", "structuredtable", "localizeentry", "localize_entry", "rawstring",
    "rawfile", "rawfilepreproc", "rawtextfile", "dlogevent", "uimodeldatastruct", "leaderboard",
    "leaderboarddef", "objective", "objectivelist", "objective_list", "bitfield", "storagefile",
    "playlists", "rank", "storecategory", "storeproduct", "milestone", "gametypetableentry",
    "aimtable", "tacticalquery", "hierarchical_task_network", "behaviortree",
    "behaviorstatemachine", "animmappingtable", "animstatemachine", "animselectortable",
    "animselectortableset", "animtree", "xanim_tree", "motion_matching_input",
    "motionmatchinginput", "bulletpenetration", "locdmgtable", "weapontunables",
    "weaponsecondarymovement", "ttf", "fonticon", "customization_table", "customizationtable",
    "customizationtablefrontend", "customization_table_fe_images", "player_role_template",
    "playerroletemplate", "playerroletemplatefrontend", "player_role_category",
    "playerrolecategory", "snddriver_globals", "snddriverglobals", "streamkey", "xmodelmesh",
    "scriptbundlelist", "maptableentry", "maptableentry_level_assets", "cgmedia", "cgmediatable",
    "physconstraints", "ballisticdesc", "triggereffectdesc", "execution", "talent",
}

SECTION = re.compile(r"^===\s+(\S+)\s+(\S+)\s+\((\d+)\)\s+===")


def name_of(line):
    line = line.strip()
    if not line or line.startswith("="):
        return None
    return line.split(",", 1)[1].strip() if "," in line else line


def cores(name):
    """Every contiguous 1..4 token run, after the mode and title decorations are peeled off."""
    n = name.lower()
    for _ in range(3):
        n = LEADING.sub("", n)
    for _ in range(3):
        n = TITLE.sub("", n)
    toks = [t for t in re.split(r"[^a-z0-9]+", n) if t]
    for i in range(len(toks)):
        for j in range(i + 1, min(i + MAX_TOKENS, len(toks)) + 1):
            c = "_".join(toks[i:j])
            if len(c) >= MIN_LEN and not c.isdigit():
                yield c


def held_tokens():
    """Every token any name we already hold uses, as a set.

    Set membership rather than substring search: the corpus is millions of names and tens of
    millions of tokens, and a core is a run of whole tokens, so the two tests agree while this
    one finishes.
    """
    toks = set()
    split = re.compile(r"[^a-z0-9]+")
    for base in ("all_names", os.path.join("cod-name-db", "csv")):
        d = os.path.join(ROOT, base)
        if not os.path.isdir(d):
            continue
        for root, _, files in os.walk(d):
            for f in files:
                if not f.endswith((".txt", ".csv")) or f.startswith("README"):
                    continue
                with open(os.path.join(root, f), encoding="utf-8", errors="replace") as fh:
                    for line in fh:
                        nm = line.strip().split(",", 1)[-1].lower()
                        toks.update(t for t in split.split(nm) if t)
    return toks


def main():
    runs = set()
    kept = dropped = 0
    for path in sys.argv[1:]:
        pool = None
        with open(path, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                m = SECTION.match(line)
                if m:
                    pool = m.group(2)
                    continue
                nm = name_of(line)
                if not nm:
                    continue
                if pool in CODE_POOLS:
                    dropped += 1
                    continue
                kept += 1
                runs.update(cores(nm))
    print("names kept: %d, dropped as code/data pools: %d" % (kept, dropped), file=sys.stderr)
    print("cores harvested: %d" % len(runs), file=sys.stderr)
    held = held_tokens()
    print("tokens in the held corpus: %d" % len(held), file=sys.stderr)

    # A core earns its place only if some token in it is one nothing we hold has ever used.
    # A core of entirely familiar tokens is reachable already and would only re-grind the corpus.
    novel = {c for c in runs if any(t not in held for t in c.split("_"))}
    print("novel (carrying a token no held name uses): %d" % len(novel), file=sys.stderr)
    for c in sorted(novel):
        print(c)


if __name__ == "__main__":
    main()
