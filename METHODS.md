# Methods

`AGENTS.md` says how to run. This says **what to run, what it reaches that nothing else does, and
how to tell when it is spent** — so that a fresh assistant with no memory of last night does not
run whichever method is listed first and re-sweep ground that is already bare.

Read this before choosing. Then check what has already been done:

```
python scripts/methods_report.py --by-method     what has been run here, and what it returned
python scripts/coverage.py --five                where the unnamed assets actually are
```

---

## The registry

| # | method | reaches | run it with | status |
|---|---|---|---|---|
| 1 | general search | anything as *beginning + stem + ending* | `confirm_cw` | **exhausted at the committed lists, and re-measuring them does not reopen it** — see below |
| 2 | per-prefix continuations | families the global lists cannot express | `scripts/continuations.py` → `confirm_list` | reaches 496 the general search misses, but only **5** were new to the community |
| 3 | materials → images | `image`, through the strongest measured cross-type seam | `images_from_materials` | productive after any material gain |
| 4 | numbers in place | family members whose number sits mid-name | `confirm_variants` | productive; widen with `swaps` |
| 5 | family gap filling | holes between confirmed family members | `scripts/families.py --gaps` → `confirm_list` | thin (1 new in 22,594) — mostly covered by 4 |
| 6 | cross-type spelling | one type's cores spelled as another's | `scripts/cross_type.py` → `confirm_list` | **measure the seam first.** Only 2 of 12 pairs are worth it |
| 7 | sound dotted tails | everything past the first dot | `confirm_sounds` | reopened — see the sound vocabulary note |
| 8 | reading the tables and extending | whatever the community half-finished | any generator → `confirm_list` | never exhausts; depends on noticing |
| 9 | cross-game techset pairs | `techset` / `technique_set` | `techset_probe`, `techset_pair` | BO4 productive; Cold War conclusively ruled out |
| 10 | sibling token substitution | one **non-numeric** token in the *middle*, both sides kept | `scripts/contributed/slotswap_20260819-225818.py` → `confirm_list` | productive: 2,789 names over four runs. Widen with `--cap`, `--context` |
| 11 | family column cross product | names differing in **two or more** places at once | `scripts/contributed/templates_20260819-220821.py` → `confirm_list` | 115 on top of a freshly-swept slotswap. Narrow ground, real ground |
| 12 | sound language and encoding variants | the same sound in the other eleven languages | `scripts/sound_languages.py` → `confirm_list` | Black Ops 4 only: 38. Cold War returns 0 — its language tables are already complete |
| 13 | image channel completion | the other channels of an image we hold one channel of | `scripts/image_channels.py` → `confirm_list` | 456 BO4, 59 CW. Compounds with method 3, which seeds from the other side |
| 14 | token insertion and deletion | names one token **longer or shorter** than a known name | `scripts/token_edits.py` → `confirm_list` | 700 BO4, 384 CW across all four types. The only method that changes a name's length |
| 15 | affix sweep | affixes used **once** in the game, which no measured list can hold | `scripts/affix_sweep.py` → `confirm_list` | **targeted only.** Blind: 1 name per 532 M candidates. Aimed at a family you suspect: the only thing that reaches it |
| 16 | final byte solved backwards | any name one **final character** from a known one, at any of 256 bytes | `scripts/final_byte.py` → `confirm_list` | **1 name per 18 candidates — the best measured here.** In `derive_closure`, so it re-runs free after any pass |
| 17 | tails of length k | any name that is a known one with its **last k characters** replaced | `scripts/tails.py` → `confirm_plan` | k=3: **1,151 in 21s a game.** Subsumes k=1 and 2; `--length 4` for more |
| 18 | heads of length k | any name that is a known one with its **first k characters** replaced | `scripts/tails.py --head` → `confirm_plan` | **692 on Cold War in one pass.** The mirror of 17, untried until 2026-08-22 |
| 19 | uncarried directories | material directories the twelve-directory list omits | `scripts/contributed/mcdp_cores_20260823-023310.py` -> `confirm_plan` | **2,846 on Cold War in one pass.** `mcdp/` is Cold War's second largest material directory and nothing here could emit it |
| 20 | black ops 3 sab sounds, black ops 4 spelling | Black Ops 4 `sound_asset`, the largest pool in either game | `scripts/contributed/bo3_sab_to_bo4_20260823-030223.py` -> `confirm_plan --no-fold` | Black Ops 3's SAB paths lower cased, language directory dropped, every Black Ops 4 tail put back on |
| 21 | recovering a pool's seed corpus | any pool whose ids were injected rather than loaded | `scripts/contributed/sound_takes_20260823-030223.py` | **not a search -- it is what every sound search should have been seeded from.** Cold War `sound_asset`: `all_names/` holds 148, the tables hold 39,199 |
| 22 | uncarried endings | any type, through the endings `data/suffixes.txt` structurally cannot express | `scripts/contributed/uncarried_endings_20260823-040620.py` -> `confirm_plan` | **6,674 names across both games on 2026-08-23, the largest method here.** Yield rises with the segment depth: 1 segment 1,191, 2 segments 2,065, 3 segments 1,800, 4 segments 1,054, 5 segments 564 |
| 23 | uncarried sound endings | `sound_alias` and `sound_asset`, the two largest pools | `scripts/contributed/uncarried_endings_20260823-040620.py --sound-pass` | **1,385 names.** 79% of published sound names end in something `data/sound.suffixes.txt` cannot express -- proportionally the larger of the two ending gaps |
| 24 | measured image channels | `image`, through the channels method 13's hand-written list omits | `scripts/contributed/image_channels_wide_20260823-043005.py` | 36 names, but it widens a derivation `derive_closure` re-runs every round: 231 of 250 real channels were uncarried, `_thermalmap` alone heads 16,000 |
| 25 | all-boundary cores | every method built as core x ending | `scripts/contributed/uncarried_endings_allboundary_20260823-134935.py` -> `confirm_plan` | **the most productive change measured on 2026-08-23.** Not a new method -- a fix to how every ending sweep builds its cores. Turned 2,065 names into 2,553 while using five times fewer endings, and 1,385 sound names into 1,746 in a single pass |
| 30 | family grid completion | `sound_alias` above all | `scripts/unnamed_profile.py --grid`, `contrib/family_grid.py` -> `confirm_list` | **23 on Black Ops 4, and `derive_closure` turned those into 102 more.** Rank families by tails shared across more than one axis value, not by raw product: `i_` looks like 158 M cells and collapses to 694 K under that, because it is not a grid, it is every name beginning `i_`. **10 more on Cold War, 2026-09-14, from families beyond the top 20 -- see below** |
| 31 | beginnings the ceiling drops | any type, through the beginnings `data/prefixes.txt` measures and then **discards for want of a slot** | `scripts/contributed/ceiling_dropped_begins_20260829-064955.py` -> `confirm_plan` | **9 on Cold War sound, and `derive_closure` turned them into 18 more; 1 more on the general half.** Distinct from 22/23: those are endings the list never measured, these are beginnings it *did* measure and the 700 ceiling threw away. Spent by nothing yet; re-run after any pass that grows the corpus, since the cut list changes |
| — | localize unfolding | `localizeentry` | `confirm_localize` | **off, and refuses to run.** Worthless — see dead ends |

### Every method that has actually been run

The table above is hand-written, and it holds fifteen methods. **One hundred and four have been
run.** The gap is not neglect — it is that keeping a registry by hand means keeping it by hand,
and nobody did, so the ninety methods missing from it were invisible to everybody who arrived
afterwards and several were invented twice.

So the rest of the registry is computed from the run record and written in below. Regenerate it
after pulling:

```
python scripts/methods_report.py --registry --write
```

Read it **before inventing anything**. A method already here under a name you would not have
guessed is the thing you are about to build again — `ways` counts how many labels one method has
already been run under, and the largest are five and six.

The two halves answer different questions and neither replaces the other. Above: what a method
*reaches*, which is judgement. Below: what it *returned*, which is arithmetic.

<!-- BEGIN GENERATED REGISTRY -->
<!-- generated by scripts/methods_report.py --registry --write; do not edit by hand -->

Every method ever run here, computed from the run record in `submissions/`. Ranked by
candidates per name, best first. `ways` is how many distinct labels this one method has
been run under -- check it before inventing anything, because a method already in this
table under a name you would not have guessed is the thing you are about to rebuild.

| method | ways | runs | names | candidates | 1 name per | best | latest | first | last | state |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|
| test | 1 | 1 | 5 | 5 | 1 | 1 | 1 | 2026-09-09 | 2026-09-09 | untried |
| voice-over from the per-language tables, language moved from the ending to the path | 1 | 1 | 257 | 257 | 1 | 1 | 1 | 2026-09-10 | 2026-09-10 | untried |
| sound asset meet-in-the-middle 1-2 token gap fill inside named sab-bank families | 1 | 1 | 794 | 794 | 1 | 1 | 1 | 2026-09-10 | 2026-09-10 | untried |
| sound files: exact-id targeted search from the w28447 sound tables alias->assetid link | 1 | 1 | 10,633 | 10,633 | 1 | 1 | 1 | 2026-09-11 | 2026-09-11 | untried |
| sound asset: exact-id probe of alias-linked unnamed files | 1 | 1 | 2,828 | 2,828 | 1 | 1 | 1 | 2026-09-11 | 2026-09-11 | untried |
| sound asset: index completion over every known stem | 1 | 1 | 237 | 237 | 1 | 1 | 1 | 2026-09-11 | 2026-09-11 | untried |
| sound asset: abbreviation-aware exact-id probe of alias-linked files | 1 | 1 | 46 | 46 | 1 | 1 | 1 | 2026-09-11 | 2026-09-11 | untried |
| sound alias: gpu 1-2 token gap fill, true open ids only, vocabulary pruned to the 4233 real sound tokens | 1 | 1 | 57 | 57 | 1 | 1 | 1 | 2026-09-11 | 2026-09-11 | untried |
| material: gpu 1-2 token gap fill over material prefixes x material tokens x material endings | 1 | 1 | 616 | 616 | 1 | 1 | 1 | 2026-09-11 | 2026-09-11 | untried |
| music: mus-mode-map-category directory grid x music alias stems | 1 | 1 | 6 | 6 | 1 | 1 | 1 | 2026-09-11 | 2026-09-11 | untried |
| image: gpu 1-2 token gap fill widened to all 20000 image prefixes | 1 | 1 | 216 | 216 | 1 | 1 | 1 | 2026-09-11 | 2026-09-11 | untried |
| xmodel+sound alias: gpu three-token meet-in-the-middle gap fill | 1 | 1 | 672 | 672 | 1 | 1 | 1 | 2026-09-11 | 2026-09-11 | untried |
| bo4: composition grids - attachment unique, weapon camo, player outfit from already-named weapons, attachments, specialists | 1 | 1 | 937 | 937 | 1 | 1 | 1 | 2026-09-13 | 2026-09-13 | untried |
| bo6 new fourth terminal alias byte with witnessed prefixes | 1 | 1 | 98 | 98 | 1 | 1 | 1 | 2026-10-10 | 2026-10-10 | untried |
| bo7 new third terminal alias byte with witnessed prefixes | 1 | 1 | 25 | 25 | 1 | 1 | 1 | 2026-10-10 | 2026-10-10 | untried |
| bo7 new fourth terminal alias byte with witnessed prefixes | 1 | 1 | 6,893 | 6,893 | 1 | 1 | 1 | 2026-10-10 | 2026-10-10 | untried |
| bo7 new fifth terminal alias byte with witnessed prefixes | 1 | 1 | 118 | 118 | 1 | 1 | 1 | 2026-10-10 | 2026-10-10 | untried |
| bo7 new alias four-byte domains opened by verified public vocabulary | 1 | 1 | 19 | 19 | 1 | 1 | 1 | 2026-10-10 | 2026-10-10 | untried |
| mwii new fourth terminal alias byte with witnessed prefixes | 1 | 1 | 155 | 155 | 1 | 1 | 1 | 2026-10-10 | 2026-10-10 | untried |
| mwii new alias four-byte domains opened by verified public vocabulary | 1 | 1 | 30 | 30 | 1 | 1 | 1 | 2026-10-10 | 2026-10-10 | untried |
| mw4-sound-byte-before-encoding | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 2026-10-09 | 2026-10-09 | untried |
| mw4-typed-image-final-byte | 1 | 1 | 9 | 9 | 1 | 1 | 1 | 2026-10-09 | 2026-10-09 | untried |
| mw4-image-byte-before-channels | 1 | 1 | 15 | 15 | 1 | 1 | 1 | 2026-10-09 | 2026-10-09 | untried |
| mw4-image-stem-pair | 1 | 1 | 18 | 18 | 1 | 1 | 1 | 2026-10-09 | 2026-10-09 | untried |
| mw4 new third terminal alias byte with witnessed prefixes | 1 | 1 | 390 | 390 | 1 | 1 | 1 | 2026-10-10 | 2026-10-10 | untried |
| mw4 new fourth terminal alias byte with witnessed prefixes | 1 | 1 | 580 | 580 | 1 | 1 | 1 | 2026-10-10 | 2026-10-10 | untried |
| mw4 new fifth terminal alias byte with witnessed prefixes | 1 | 1 | 46 | 46 | 1 | 1 | 1 | 2026-10-10 | 2026-10-10 | untried |
| mwiii-typed-image-final-byte | 1 | 1 | 7 | 7 | 1 | 1 | 1 | 2026-10-09 | 2026-10-09 | untried |
| mwiii-image-byte-before-channels | 1 | 1 | 416 | 416 | 1 | 1 | 1 | 2026-10-09 | 2026-10-09 | untried |
| mwiii-image-stem-pair | 1 | 1 | 149 | 149 | 1 | 1 | 1 | 2026-10-09 | 2026-10-09 | untried |
| mwiii new fourth terminal alias byte with witnessed prefixes | 1 | 1 | 30 | 30 | 1 | 1 | 1 | 2026-10-10 | 2026-10-10 | untried |
| mwii witnessed animation pairs probe hits | 1 | 1 | 28 | 28 | 1 | 1 | 1 | 2026-10-10 | 2026-10-10 | untried |
| sound final byte solved backwards | 1 | 1 | 7 | 7 | 1 | 1 | 1 | 2026-08-31 | 2026-08-31 | untried |
| unclaimed bo6 images from bo7 frozen suffix byte candidates | 1 | 1 | 3 | 3 | 1 | 1 | 1 | 2026-10-09 | 2026-10-09 | untried |
| shared verified animation deltas: bo6-only remaining names | 1 | 1 | 3 | 3 | 1 | 1 | 1 | 2026-10-09 | 2026-10-09 | untried |
| external csv raw aliases unique to bo6 | 1 | 1 | 8 | 8 | 1 | 1 | 1 | 2026-10-09 | 2026-10-09 | untried |
| external csv image unique after bo7-first validation | 1 | 2 | 2 | 2 | 1 | 1 | 1 | 2026-10-09 | 2026-10-09 | live |
| shared verified visual delta remaining in blackop6 image | 1 | 1 | 2 | 2 | 1 | 1 | 1 | 2026-10-09 | 2026-10-09 | untried |
| shared verified visual delta remaining in blackop6 material | 1 | 1 | 6 | 6 | 1 | 1 | 1 | 2026-10-09 | 2026-10-09 | untried |
| bo7 alias source-delta names in bo6 capture | 1 | 1 | 4 | 4 | 1 | 1 | 1 | 2026-10-09 | 2026-10-09 | untried |
| bo7 verified-frontier candidate in bo6 capture | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 2026-10-09 | 2026-10-09 | untried |
| bo7 sound basename byte after sound pool repair | 1 | 1 | 39 | 39 | 1 | 1 | 1 | 2026-10-09 | 2026-10-09 | untried |
| external csv raw-name capture check: animations | 1 | 1 | 643 | 643 | 1 | 1 | 1 | 2026-10-09 | 2026-10-09 | untried |
| external csv raw-name capture check: materials | 1 | 1 | 3,717 | 3,717 | 1 | 1 | 1 | 2026-10-09 | 2026-10-09 | untried |
| external csv raw-name capture check: images | 1 | 1 | 2,314 | 2,314 | 1 | 1 | 1 | 2026-10-09 | 2026-10-09 | untried |
| external csv raw-name capture check: sound aliases | 1 | 1 | 3,353 | 3,353 | 1 | 1 | 1 | 2026-10-09 | 2026-10-09 | untried |
| external csv raw-name capture check: sound files | 1 | 1 | 4 | 4 | 1 | 1 | 1 | 2026-10-09 | 2026-10-09 | untried |
| unclaimed mwii images from bo7 frozen suffix byte candidates | 1 | 1 | 7 | 7 | 1 | 1 | 1 | 2026-10-09 | 2026-10-09 | untried |
| external csv raw aliases unique after bo7-first validation | 1 | 3 | 83 | 83 | 1 | 1 | 1 | 2026-10-09 | 2026-10-09 | live |
| external csv material unique after bo7-first validation | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 2026-10-09 | 2026-10-09 | untried |
| shared verified visual delta remaining in modwar22 material | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 2026-10-09 | 2026-10-09 | untried |
| unclaimed mwiii images from bo7 frozen suffix byte candidates | 1 | 1 | 15 | 15 | 1 | 1 | 1 | 2026-10-09 | 2026-10-09 | untried |
| shared verified visual delta remaining in yamyamok image | 1 | 1 | 3 | 3 | 1 | 1 | 1 | 2026-10-09 | 2026-10-09 | untried |
| shared verified visual delta remaining in yamyamok material | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 2026-10-09 | 2026-10-09 | untried |
| bo7 alias source-delta names in mwiii capture | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 2026-10-09 | 2026-10-09 | untried |
| exact alias rule-delta vocabulary reused in mwiii | 1 | 1 | 78 | 78 | 1 | 1 | 1 | 2026-10-09 | 2026-10-09 | untried |
| xmodel: gpu 1-2 token gap fill over xmodel prefixes x xmodel tokens x xmodel endings | 1 | 1 | 451 | 452 | 1 | 1 | 1 | 2026-09-11 | 2026-09-11 | untried |
| xanim: gpu 1-2 token gap fill over animation prefixes x animation tokens x animation endings | 1 | 1 | 273 | 274 | 1 | 1 | 1 | 2026-09-11 | 2026-09-11 | untried |
| light description: editor default names new<31-bit int>, exhaustive digit sweep on gpu | 1 | 1 | 548 | 552 | 1 | 1 | 1 | 2026-09-13 | 2026-09-13 | untried |
| bo4: systematic token-slot template mining across every pocket, iterated to convergence | 1 | 1 | 1,473 | 1,492 | 1 | 1 | 1 | 2026-09-13 | 2026-09-13 | untried |
| scriptparsetree/luafile/ddl/stringtable: the dump's own file paths, pockets nobody searches | 1 | 1 | 7,038 | 7,195 | 1 | 1 | 1 | 2026-09-11 | 2026-09-11 | untried |
| bo4: gpu gap fill re-run on rebuilt vocabularies and targets | 1 | 1 | 287 | 294 | 1 | 1 | 1 | 2026-09-14 | 2026-09-14 | untried |
| image+material: gpu three-token meet-in-the-middle gap fill | 1 | 1 | 591 | 617 | 1 | 1 | 1 | 2026-09-11 | 2026-09-11 | untried |
| bo4: material/image mirror | 1 | 1 | 241 | 252 | 1 | 1 | 1 | 2026-09-12 | 2026-09-12 | untried |
| bo4: the dump's own file tree hashed against every pocket | 1 | 1 | 7,362 | 7,827 | 1 | 1 | 1 | 2026-09-11 | 2026-09-11 | untried |
| community-provided mw4 hash package | 1 | 1 | 33,593 | 36,949 | 1 | 1 | 1 | 2026-10-08 | 2026-10-08 | untried |
| bo4: three-way model/material/image core mirror | 1 | 1 | 101 | 112 | 1 | 1 | 1 | 2026-09-14 | 2026-09-14 | untried |
| bo4: identifier strings read from the retail install's raw 179.8 gb casc packages | 1 | 1 | 401 | 448 | 1 | 1 | 1 | 2026-09-12 | 2026-09-12 | untried |
| bo4: consonant-skeleton and truncation variants of proper nouns in creature-bearing templates | 1 | 1 | 1,185 | 1,355 | 1 | 1 | 1 | 2026-09-13 | 2026-09-13 | untried |
| bo4: merged token-slot categories cross-producted over every template in the corpus | 1 | 1 | 579 | 688 | 1 | 1 | 1 | 2026-09-12 | 2026-09-12 | untried |
| bo4: exhaustive 3-5 char speaker-token search on the alias side and the vo path shape | 1 | 1 | 176 | 210 | 1 | 1 | 1 | 2026-09-11 | 2026-09-11 | untried |
| sound asset: gpu 1-2 token gap fill inside every known sound directory | 1 | 1 | 8 | 10 | 1 | 1 | 1 | 2026-09-11 | 2026-09-11 | untried |
| bo4: per-pocket template mining, second pass on the enlarged corpus | 1 | 1 | 160 | 203 | 1 | 1 | 1 | 2026-09-14 | 2026-09-14 | untried |
| music: multiplayer sets 06/07 grid (mpn <cue> v<ver> <mix>) + editor-default light names | 1 | 1 | 21 | 27 | 1 | 1 | 1 | 2026-09-13 | 2026-09-13 | untried |
| beam names recovered live via saluki | 1 | 1 | 26 | 34 | 1 | 1 | 1 | 2026-09-14 | 2026-09-14 | untried |
| sweep of other pools: in-scope sound alias | 1 | 1 | 3 | 4 | 1 | 1 | 1 | 2026-09-05 | 2026-09-05 | untried |
| bo4: gpu gap fill over prefixes built from the 102 enemy spawner names of the aitype tables | 1 | 1 | 10 | 14 | 1 | 1 | 1 | 2026-09-11 | 2026-09-11 | untried |
| zombies vo: mitm round 4 (white/orange, npc seeds) + gpu 3-token gap fill, first 22 prefixes | 1 | 1 | 419 | 619 | 1 | 1 | 1 | 2026-09-10 | 2026-09-10 | untried |
| bo4: numeric-sibling completion across every non-sound pocket | 1 | 1 | 29 | 51 | 1 | 1 | 1 | 2026-09-14 | 2026-09-14 | untried |
| image: gpu 1-2 token gap fill over image prefixes x image tokens x channel endings | 2 | 2 | 348 | 642 | 1 | 1 | 6 | 2026-09-11 | 2026-09-11 | cooling |
| zombies player-line files read back as aliases | 1 | 1 | 40 | 80 | 2 | 2 | 2 | 2026-10-05 | 2026-10-05 | untried |
| bo4: truncation and skeleton variants of every vocabulary word in every single-slot template | 1 | 1 | 87 | 187 | 2 | 2 | 2 | 2026-09-13 | 2026-09-13 | untried |
| bo4: merged token-slot categories, second pass on the enlarged corpus | 1 | 1 | 78 | 194 | 2 | 2 | 2 | 2026-09-14 | 2026-09-14 | untried |
| bo4: every string in the dump hashed against every pocket | 1 | 1 | 6,240 | 15,741 | 2 | 2 | 2 | 2026-09-11 | 2026-09-11 | untried |
| richkiller bo4 decoded texture ledger | 1 | 1 | 7,488 | 22,210 | 2 | 2 | 2 | 2026-09-04 | 2026-09-04 | untried |
| xanim: gpu three-token meet-in-the-middle gap fill over 1500 animation prefixes | 1 | 1 | 68 | 273 | 4 | 4 | 4 | 2026-09-11 | 2026-09-11 | untried |
| sound files from the bo2/bo3 published folder trees | 1 | 1 | 2,603 | 11,036 | 4 | 4 | 4 | 2026-09-09 | 2026-09-09 | untried |
| operator voice-line grid dx op <category> <event> <speaker> | 3 | 3 | 7,657 | 37,260 | 4 | 3 | 3 | 2026-10-09 | 2026-10-09 | live |
| sound files: exact-id search, zombies player exertions under scripted/exerts/plr n | 1 | 1 | 2,442 | 14,723 | 6 | 6 | 6 | 2026-09-11 | 2026-09-11 | untried |
| music: tag der toten round cues mus round start nn mas under mus/zm/orange/round start | 1 | 1 | 5 | 32 | 6 | 6 | 6 | 2026-09-13 | 2026-09-13 | untried |
| sound files: exact-id search, full aliases <suffix> plr <n> <v> -> vox <map> plr <n> <suffix> <v>[ s] | 1 | 1 | 1,550 | 12,281 | 7 | 7 | 7 | 2026-09-11 | 2026-09-11 | untried |
| mw7 native full-corpus visual numeric siblings 0-999 | 1 | 1 | 15 | 137 | 9 | 9 | 9 | 2026-10-08 | 2026-10-08 | untried |
| sound alias: gpu gap fill re-run on rebuilt vocabularies and targets | 1 | 1 | 36 | 338 | 9 | 9 | 9 | 2026-09-14 | 2026-09-14 | untried |
| bo4: closed-category completion | 1 | 1 | 7 | 71 | 10 | 10 | 10 | 2026-09-13 | 2026-09-13 | untried |
| jointly witnessed alias pair rules on verified new source names | 1 | 1 | 2,677 | 29,352 | 10 | 10 | 10 | 2026-10-09 | 2026-10-09 | untried |
| zombies map lines, file parts reordered as aliases | 1 | 1 | 412 | 4,759 | 11 | 11 | 11 | 2026-10-05 | 2026-10-05 | untried |
| bo4: gpu gap fill with a vocabulary taken from the game's own english subtitles | 1 | 1 | 77 | 1,056 | 13 | 13 | 13 | 2026-09-11 | 2026-09-11 | untried |
| bo4: exhaustive 1-9 character enumeration over [a-z0-9 ] against every pocket | 1 | 1 | 3 | 49 | 16 | 16 | 16 | 2026-09-13 | 2026-09-13 | untried |
| bo4: exhaustive 9-character enumeration, decode fixed | 1 | 1 | 4 | 71 | 17 | 17 | 17 | 2026-09-13 | 2026-09-13 | untried |
| sound alias: mp/blackout dialog aliases cracked from the mpdialog player script bundles | 1 | 1 | 30 | 570 | 19 | 19 | 19 | 2026-09-11 | 2026-09-11 | untried |
| bo4: player outfit grid with outfit tokens harvested from loot tables, unlockable items and subtitles | 1 | 1 | 52 | 1,020 | 19 | 19 | 19 | 2026-09-13 | 2026-09-13 | untried |
| final byte solved backwards | 1 | 232 | 234,567 | 5,130,003 | 21 | 2 | 8 | 2026-08-22 | 2026-10-09 | cooling |
| aliases from sound-file basenames, two-letter-codec files included | 1 | 2 | 61,096 | 1,482,617 | 24 | 20 | 20 | 2026-10-08 | 2026-10-08 | live |
| zombies vo: gpu 1-2 token gap fill over all crew/npc speaker prefixes | 1 | 1 | 1,507 | 38,338 | 25 | 25 | 25 | 2026-09-10 | 2026-09-10 | untried |
| sound alias: gpu 1-2 token gap fill over 4500 alias prefixes x 10k alias-token vocabulary x the real alias endings | 1 | 1 | 325 | 9,655 | 29 | 29 | 29 | 2026-09-11 | 2026-09-11 | untried |
| independently sourced alias paired-rule support delta | 1 | 1 | 787 | 24,289 | 30 | 30 | 30 | 2026-10-09 | 2026-10-09 | untried |
| bo4: composition grids round 2 - attachment unique with expanded weapon bases and attachment tokens | 1 | 1 | 31 | 968 | 31 | 31 | 31 | 2026-09-13 | 2026-09-13 | untried |
| music: dead of the night the ride v1 mas under mus/zm/red/the ride | 1 | 1 | 1 | 33 | 33 | 33 | 33 | 2026-09-13 | 2026-09-13 | untried |
| music: voyage of despair easter-egg song drowning mix 16 | 1 | 1 | 1 | 34 | 34 | 34 | 34 | 2026-09-13 | 2026-09-13 | untried |
| frozen witnessed alias rules on verified descendant names | 1 | 1 | 1,180 | 41,811 | 35 | 35 | 35 | 2026-10-09 | 2026-10-09 | untried |
| verified alias frontier after independent rule-support delta | 1 | 1 | 742 | 26,714 | 36 | 36 | 36 | 2026-10-09 | 2026-10-09 | untried |
| aliases from sound-file basenames, round 2 | 1 | 2 | 34,343 | 1,249,514 | 36 | 29 | 29 | 2026-10-08 | 2026-10-08 | live |
| zombies chaos-story player vo grid: vox <map> plr <n> <event> <v> for zod/red/tow, events from mitm gap fill | 1 | 1 | 3,365 | 123,139 | 36 | 36 | 36 | 2026-09-10 | 2026-09-10 | untried |
| blackout banter aliases + files cracked from the hashed banter stringtable | 1 | 1 | 34 | 1,339 | 39 | 39 | 39 | 2026-09-11 | 2026-09-11 | untried |
| black ops 4 source literals | 1 | 1 | 546 | 23,249 | 42 | 42 | 42 | 2026-08-26 | 2026-08-26 | untried |
| sound alias: weapon sound aliases from tables/weapon hashed fields | 1 | 1 | 12 | 543 | 45 | 45 | 45 | 2026-09-11 | 2026-09-11 | untried |
| voice phrase grids, fill after topic x common quips | 1 | 1 | 374 | 19,340 | 51 | 51 | 51 | 2026-10-06 | 2026-10-06 | untried |
| sound alias: plaintext alias names from the w28447 dump sound tables + aliases derived from the stems of already-named linked files | 1 | 1 | 254 | 14,836 | 58 | 58 | 58 | 2026-09-11 | 2026-09-11 | untried |
| voice phrase grids, fill after quip triples | 1 | 1 | 306 | 19,326 | 63 | 63 | 63 | 2026-10-06 | 2026-10-06 | untried |
| channel and material derivations from paired image discoveries | 1 | 1 | 11 | 738 | 67 | 67 | 67 | 2026-09-22 | 2026-09-22 | untried |
| zombies aether-story vo grid, blood of the dead (bod, plr 0-16), events from cracked vox csv + common table | 1 | 1 | 1,143 | 88,672 | 77 | 77 | 77 | 2026-09-10 | 2026-09-10 | untried |
| new image prefix delta to material wrappers | 1 | 1 | 25 | 2,064 | 82 | 82 | 82 | 2026-10-09 | 2026-10-09 | untried |
| verified embedded-model source vocabulary to image wrappers | 1 | 1 | 97 | 8,313 | 85 | 85 | 85 | 2026-10-09 | 2026-10-09 | untried |
| final byte current 20260907 | 1 | 1 | 15 | 1,316 | 87 | 87 | 87 | 2026-09-07 | 2026-09-07 | untried |
| mp/blackout specialist vo: gpu 1-2 token gap fill over en\vox\scripted\{mpl,wz}\<spec>\vox <spec> | 1 | 1 | 463 | 41,415 | 89 | 89 | 89 | 2026-09-10 | 2026-09-10 | untried |
| bo7 directory-witnessed encoding closure of 44 fresh sound files | 1 | 1 | 1 | 95 | 95 | 95 | 95 | 2026-10-09 | 2026-10-09 | untried |
| sound alias two byte solve | 1 | 1 | 5 | 521 | 104 | 104 | 104 | 2026-09-02 | 2026-09-02 | untried |
| sound files: directory probe | 1 | 1 | 98 | 10,731 | 109 | 109 | 109 | 2026-09-11 | 2026-09-11 | untried |
| voice phrase grids, fill after long-phrase probe | 1 | 1 | 165 | 18,751 | 113 | 113 | 113 | 2026-10-05 | 2026-10-05 | untried |
| cross-game transfer, round 3 | 1 | 2 | 60,755 | 8,002,517 | 131 | 110 | 110 | 2026-10-08 | 2026-10-08 | live |
| zombies vo grid: man = dead of the night | 1 | 1 | 1,549 | 207,751 | 134 | 134 | 134 | 2026-09-10 | 2026-09-10 | untried |
| cold war source literals | 1 | 1 | 251 | 35,278 | 140 | 140 | 140 | 2026-08-26 | 2026-08-26 | untried |
| cross-game transfer incl. open-pr names and refreshed tables | 1 | 2 | 47,942 | 7,780,781 | 162 | 137 | 137 | 2026-10-08 | 2026-10-08 | live |
| zombies vo grid: fiv = classified, whi | 1 | 1 | 3,505 | 575,687 | 164 | 164 | 164 | 2026-09-10 | 2026-09-10 | untried |
| verified union frontier of frozen alias pair and block rules | 1 | 1 | 89 | 14,824 | 166 | 166 | 166 | 2026-10-09 | 2026-10-09 | untried |
| mw7 confirmed visual numeric sibling closure 0-999 | 1 | 3 | 27 | 4,940 | 182 | 4 | 4 | 2026-10-08 | 2026-10-08 | live |
| voice phrase grids, fill after deep quips | 1 | 1 | 102 | 18,802 | 184 | 184 | 184 | 2026-10-05 | 2026-10-05 | untried |
| zombies aether vo grid round 2: bod plr 0-16 x (csv + common + mitm-found events), plus mitm round-3 hits | 1 | 1 | 487 | 101,127 | 207 | 207 | 207 | 2026-09-10 | 2026-09-10 | untried |
| aliases from sound-file basenames, take numbers stripped, segment-trimmed | 1 | 2 | 4,895 | 1,144,673 | 233 | 208 | 208 | 2026-10-08 | 2026-10-08 | live |
| vo: gpu gap fill rerun with  n s variants (zm + mp prefixes) + cpu variant probe | 1 | 1 | 357 | 84,856 | 237 | 237 | 237 | 2026-09-10 | 2026-09-10 | untried |
| vo sound files derived from known vox  sound aliases: en\vox\scripted\<mode>\<map>\<alias> <n> | 1 | 1 | 12,846 | 3,180,688 | 247 | 247 | 247 | 2026-09-10 | 2026-09-10 | untried |
| frozen alias rules through verified frontier | 1 | 1 | 79 | 20,991 | 265 | 265 | 265 | 2026-10-09 | 2026-10-09 | untried |
| mwiii-terrain-overlap | 1 | 1 | 54 | 14,881 | 275 | 275 | 275 | 2026-10-09 | 2026-10-09 | untried |
| voice phrase grids, fill after probe | 1 | 1 | 66 | 18,604 | 281 | 281 | 281 | 2026-10-05 | 2026-10-05 | untried |
| verified image vocabulary delta to witnessed material directories | 1 | 1 | 57 | 16,107 | 282 | 282 | 282 | 2026-10-09 | 2026-10-09 | untried |
| material-witnessed complete interior image blocks | 1 | 1 | 23 | 6,801 | 295 | 295 | 295 | 2026-10-09 | 2026-10-09 | untried |
| build strings, lpc fast files | 1 | 1 | 7 | 2,135 | 305 | 305 | 305 | 2026-08-24 | 2026-08-24 | untried |
| mwiii-alias-codename | 1 | 1 | 40 | 13,642 | 341 | 341 | 341 | 2026-10-09 | 2026-10-09 | untried |
| build strings, casc blte 0.5gb probe | 1 | 1 | 10 | 3,637 | 363 | 363 | 363 | 2026-08-24 | 2026-08-24 | untried |
| mwiii-file-derived-aliases | 1 | 1 | 2,667 | 1,192,154 | 447 | 447 | 447 | 2026-10-09 | 2026-10-09 | untried |
| alias family grid snowball r3 h3 | 5 | 5 | 7,083 | 3,614,180 | 510 | 271 | 6,755 | 2026-10-09 | 2026-10-09 | spent |
| zombies vo grid: oran (dir orange) = tag der toten, plr 0-24 | 1 | 1 | 1,394 | 747,687 | 536 | 536 | 536 | 2026-09-10 | 2026-09-10 | untried |
| old witnessed animation rules on verified new source clips | 1 | 1 | 10 | 5,539 | 553 | 553 | 553 | 2026-10-09 | 2026-10-09 | untried |
| voice phrase grids, fill after wide triples | 1 | 1 | 34 | 19,056 | 560 | 560 | 560 | 2026-10-06 | 2026-10-06 | untried |
| voice phrase grids, fill after wiki probe | 1 | 1 | 33 | 19,057 | 577 | 577 | 577 | 2026-10-07 | 2026-10-07 | untried |
| weapon anim grid | 1 | 2 | 77 | 46,426 | 602 | 446 | 927 | 2026-09-03 | 2026-09-03 | live |
| alias family grid snowball r2 h3 | 5 | 18 | 21,139 | 13,570,940 | 641 | 271 | 1,734 | 2026-10-09 | 2026-10-09 | cooling |
| alias family grid round 4, head 3 | 5 | 5 | 5,434 | 3,578,855 | 658 | 342 | 7,303 | 2026-10-09 | 2026-10-09 | spent |
| cinematic shot grid, round 3 | 1 | 1 | 70 | 46,414 | 663 | 663 | 663 | 2026-10-01 | 2026-10-01 | untried |
| alias family grid round 3, head 3 | 5 | 5 | 5,365 | 3,574,295 | 666 | 342 | 24,650 | 2026-10-09 | 2026-10-09 | spent |
| alias family grid round 2, head 3 | 5 | 5 | 5,339 | 3,574,040 | 669 | 342 | 357,404 | 2026-10-09 | 2026-10-09 | spent |
| alias family grid round 1, head 3 | 5 | 5 | 5,337 | 3,574,020 | 669 | 342 | 357,402 | 2026-10-09 | 2026-10-09 | spent |
| mw4-file-to-alias-prefixes | 1 | 1 | 4 | 2,845 | 711 | 711 | 711 | 2026-10-09 | 2026-10-09 | untried |
| mwiii sound variants opened by verified public seed batch | 1 | 1 | 2 | 1,466 | 733 | 733 | 733 | 2026-10-10 | 2026-10-10 | untried |
| zombies vo grid round 3: all 5 aether/dotn maps x plr 0-24 x events (csv + common + mitm rounds 1-3), plus mitm round-3 hits | 1 | 1 | 1,678 | 1,258,928 | 750 | 750 | 750 | 2026-09-10 | 2026-09-10 | untried |
| alias family grid snowball r1 h3 | 5 | 28 | 25,331 | 20,843,630 | 822 | 271 | 1,734 | 2026-10-09 | 2026-10-09 | cooling |
| black market character spray tag images | 1 | 1 | 10 | 8,316 | 831 | 831 | 831 | 2026-09-04 | 2026-09-04 | untried |
| gaps | 2 | 5 | 376 | 346,722 | 922 | 190 | 50,180 | 2026-08-20 | 2026-08-27 | spent |
| other types' stems as material bases under every material directory | 1 | 2 | 63,792 | 62,144,250 | 974 | 810 | 810 | 2026-10-08 | 2026-10-08 | live |
| verified material vocabulary delta to witnessed image wrappers | 1 | 1 | 692 | 688,373 | 994 | 994 | 994 | 2026-10-09 | 2026-10-09 | untried |
| aliases from sound-file basenames | 3 | 3 | 1,023 | 1,067,589 | 1,043 | 621 | 177,931 | 2026-10-08 | 2026-10-08 | spent |
| bo4: bo4-source decompiles, acts hash databases and the dump re-read as raw bytes, hashed against every pocket | 1 | 1 | 9 | 9,510 | 1,056 | 1,056 | 1,056 | 2026-09-12 | 2026-09-12 | untried |
| independently witnessed atomic alias interior blocks | 1 | 1 | 514 | 557,984 | 1,085 | 1,085 | 1,085 | 2026-10-09 | 2026-10-09 | untried |
| mw4 fresh material vocabulary to witnessed image wrappers | 1 | 1 | 1 | 1,100 | 1,100 | 1,100 | 1,100 | 2026-10-10 | 2026-10-10 | untried |
| uncarried sound grid two | 1 | 1 | 1 | 1,114 | 1,114 | 1,114 | 1,114 | 2026-09-07 | 2026-09-07 | untried |
| figglefx bo4 verified general exports | 1 | 1 | 134 | 159,569 | 1,190 | 1,190 | 1,190 | 2026-09-04 | 2026-09-04 | untried |
| mw4 material wrappers from verified embedded model vocabulary | 1 | 1 | 22 | 28,655 | 1,302 | 1,302 | 1,302 | 2026-10-10 | 2026-10-10 | untried |
| modern slotswap: method 10 over every modern name, first run on the modern games | 1 | 2 | 62,350 | 84,017,186 | 1,347 | 1,113 | 1,113 | 2026-10-08 | 2026-10-08 | live |
| reverse final-byte solve after source refresh | 1 | 1 | 3 | 4,051 | 1,350 | 1,350 | 1,350 | 2026-09-03 | 2026-09-03 | untried |
| numbered sound templates, every number | 1 | 1 | 772 | 1,055,896 | 1,367 | 1,367 | 1,367 | 2026-10-05 | 2026-10-05 | untried |
| modern slotswap round 3 | 1 | 2 | 62,211 | 86,904,042 | 1,396 | 1,178 | 1,178 | 2026-10-08 | 2026-10-08 | live |
| blackout vo: all named speakers x all known blackout events x variants | 1 | 1 | 112 | 159,536 | 1,424 | 1,424 | 1,424 | 2026-09-11 | 2026-09-11 | untried |
| modern slotswap round 2: seeds include this session's finds | 1 | 2 | 58,341 | 85,020,075 | 1,457 | 1,225 | 1,225 | 2026-10-08 | 2026-10-08 | live |
| voice phrase grids, cross fill inside categories | 1 | 1 | 442 | 650,084 | 1,470 | 1,470 | 1,470 | 2026-10-05 | 2026-10-05 | untried |
| two byte pool solve | 1 | 1 | 2 | 3,124 | 1,562 | 1,562 | 1,562 | 2026-09-04 | 2026-09-04 | untried |
| alias family grid snowball r3 h2 | 5 | 5 | 7,287 | 11,440,235 | 1,569 | 830 | 15,052 | 2026-10-09 | 2026-10-09 | spent |
| alias family grid snowball r3 h1 | 5 | 5 | 7,353 | 11,948,635 | 1,625 | 837 | 13,501 | 2026-10-09 | 2026-10-09 | spent |
| alias family grid round 2, head 1 | 4 | 4 | 5,645 | 9,507,740 | 1,684 | 1,042 | 11,944 | 2026-10-09 | 2026-10-09 | spent |
| sound tail swap: known stems x bo6 encoding tails | 1 | 1 | 4,049 | 7,657,578 | 1,891 | 1,891 | 1,891 | 2026-10-08 | 2026-10-08 | untried |
| sound tail swap: known stems x bo7 encoding tails | 1 | 1 | 4,002 | 7,657,578 | 1,913 | 1,913 | 1,913 | 2026-10-08 | 2026-10-08 | untried |
| zombies vo: english-dictionary mitm on the last csv/script suffixes (bo4 mitm dict english.cpp) + mitm round 4 mansion/common + gpu 3-token progress | 1 | 1 | 1,657 | 3,173,167 | 1,915 | 1,915 | 1,915 | 2026-09-10 | 2026-09-10 | untried |
| newly witnessed animation contexts from verified source clips | 1 | 1 | 16 | 30,802 | 1,925 | 1,925 | 1,925 | 2026-10-09 | 2026-10-09 | untried |
| alias family grid: middle x final token, head 2 | 5 | 5 | 5,887 | 11,404,715 | 1,937 | 1,033 | 126,719 | 2026-10-09 | 2026-10-09 | spent |
| alias family grid round 4, head 2 | 5 | 5 | 5,567 | 11,410,880 | 2,049 | 1,045 | 41,494 | 2026-10-09 | 2026-10-09 | spent |
| zombies player-line aliases placed into every map's voice folder | 1 | 1 | 370 | 763,091 | 2,062 | 2,062 | 2,062 | 2026-10-05 | 2026-10-05 | untried |
| alias family grid round 3, head 2 | 5 | 5 | 5,531 | 11,410,335 | 2,062 | 1,045 | 120,108 | 2026-10-09 | 2026-10-09 | spent |
| alias family grid round 1, head 1 | 5 | 5 | 5,760 | 11,884,405 | 2,063 | 1,042 | 38,336 | 2026-10-09 | 2026-10-09 | spent |
| alias family grid round 2, head 2 | 5 | 5 | 5,530 | 11,410,315 | 2,063 | 1,045 | 120,108 | 2026-10-09 | 2026-10-09 | spent |
| alias family grid round 1, head 2 | 5 | 5 | 5,497 | 11,404,715 | 2,074 | 1,050 | 325,849 | 2026-10-09 | 2026-10-09 | spent |
| alias family grid round 4, head 1 | 5 | 5 | 5,721 | 11,888,980 | 2,078 | 1,043 | 31,703 | 2026-10-09 | 2026-10-09 | spent |
| alias family grid round 3, head 1 | 5 | 5 | 5,693 | 11,887,885 | 2,088 | 1,043 | 51,686 | 2026-10-09 | 2026-10-09 | spent |
| bo7 witnessed file-to-alias prefix rules | 1 | 1 | 18 | 38,612 | 2,145 | 2,145 | 2,145 | 2026-10-09 | 2026-10-09 | untried |
| alias family grid snowball r2 h1 | 5 | 18 | 21,054 | 45,966,563 | 2,183 | 837 | 5,902 | 2026-10-09 | 2026-10-09 | cooling |
| hashindex bo4 bocw global and script labels | 1 | 1 | 160 | 352,925 | 2,205 | 2,205 | 2,205 | 2026-09-04 | 2026-09-04 | untried |
| alias family grid snowball r1 h2 | 5 | 28 | 29,739 | 65,930,160 | 2,216 | 623 | 4,287 | 2026-10-09 | 2026-10-09 | cooling |
| final-byte-after-xanim-seed | 1 | 1 | 16 | 35,919 | 2,244 | 2,244 | 2,244 | 2026-08-29 | 2026-08-29 | untried |
| black ops 4 final byte after upstream corpus refresh | 1 | 1 | 1 | 2,267 | 2,267 | 2,267 | 2,267 | 2026-09-01 | 2026-09-01 | untried |
| alias family grid snowball r2 h2 | 5 | 25 | 25,128 | 59,074,809 | 2,350 | 830 | 5,459 | 2026-10-09 | 2026-10-09 | cooling |
| final-byte after current findings | 1 | 1 | 5 | 11,775 | 2,355 | 2,355 | 2,355 | 2026-09-01 | 2026-09-01 | untried |
| black ops 1 build names, verbatim | 1 | 2 | 271 | 651,912 | 2,405 | 1,940 | 3,164 | 2026-08-22 | 2026-08-22 | live |
| mwiii-terrain-qualifiers | 1 | 1 | 2 | 5,496 | 2,748 | 2,748 | 2,748 | 2026-10-09 | 2026-10-09 | untried |
| alias family grid snowball r1 h1 | 5 | 28 | 25,313 | 69,912,173 | 2,761 | 834 | 5,902 | 2026-10-09 | 2026-10-09 | cooling |
| cinematic shot grid | 1 | 2 | 50 | 143,956 | 2,879 | 867 | 34,387 | 2026-10-01 | 2026-10-01 | spent |
| bo7 terrain layer order permutations | 1 | 1 | 129 | 376,350 | 2,917 | 2,917 | 2,917 | 2026-10-09 | 2026-10-09 | untried |
| black ops 3 build names, respelled, full harvest | 1 | 2 | 148 | 473,642 | 3,200 | 1,691 | 29,602 | 2026-08-22 | 2026-08-22 | spent |
| numbered family gaps after pr2011 | 1 | 1 | 36 | 119,028 | 3,306 | 3,306 | 3,306 | 2026-09-09 | 2026-09-09 | untried |
| zombies vo grids, all 8 maps, with 176 more csv suffixes cracked by 3-token mitm | 1 | 1 | 593 | 1,964,627 | 3,313 | 3,313 | 3,313 | 2026-09-10 | 2026-09-10 | untried |
| bo4: plaintext names harvested from the w28447/-8 dump (all pools) + mitm character xmodels | 1 | 1 | 98 | 340,813 | 3,477 | 3,477 | 3,477 | 2026-09-11 | 2026-09-11 | untried |
| cross-game transfer: every known name from every game, rehashed under bo6 policy | 1 | 1 | 1,052 | 3,817,006 | 3,628 | 3,628 | 3,628 | 2026-10-08 | 2026-10-08 | untried |
| cross-game transfer: every known name from every game, rehashed under bo7 policy | 1 | 1 | 1,045 | 3,817,005 | 3,652 | 3,652 | 3,652 | 2026-10-08 | 2026-10-08 | untried |
| anim symmetry | 2 | 2 | 5 | 18,464 | 3,692 | 3,098 | 3,098 | 2026-09-03 | 2026-09-04 | live |
| vo: gpu gap fill with the cod-wiki-enriched 16k vocabulary (all zm/mp prefixes) + grids with 16 more csv suffixes | 1 | 1 | 803 | 3,062,529 | 3,813 | 3,813 | 3,813 | 2026-09-10 | 2026-09-10 | untried |
| zombies player and npc lines placed into every map's voice folder | 1 | 1 | 248 | 946,142 | 3,815 | 3,815 | 3,815 | 2026-10-05 | 2026-10-05 | untried |
| zombies npc/announcer speakers (gpu-found tokens) x known events x variants | 1 | 1 | 120 | 460,800 | 3,840 | 3,840 | 3,840 | 2026-09-10 | 2026-09-10 | untried |
| modern material <-> image cores | 5 | 5 | 8,811 | 34,102,700 | 3,870 | 1,492 | 6,820,540 | 2026-10-09 | 2026-10-09 | spent |
| early black ops 4 source literals | 1 | 1 | 4 | 16,198 | 4,049 | 4,049 | 4,049 | 2026-08-26 | 2026-08-26 | untried |
| sound aliases = recovered sound file stems minus  n | 1 | 1 | 4 | 18,353 | 4,588 | 4,588 | 4,588 | 2026-09-10 | 2026-09-10 | untried |
| animation symmetry | 1 | 1 | 2 | 9,297 | 4,648 | 4,648 | 4,648 | 2026-09-04 | 2026-09-04 | untried |
| build strings, casc archives | 1 | 4 | 139 | 659,480 | 4,744 | 1,316 | 273,138 | 2026-08-24 | 2026-08-24 | spent |
| sound files: exact-id search, stoker vocals | 1 | 1 | 3 | 14,726 | 4,908 | 4,908 | 4,908 | 2026-09-11 | 2026-09-11 | untried |
| bo7 witnessed animation pairs shared with mwii | 1 | 1 | 225 | 1,137,241 | 5,054 | 5,054 | 5,054 | 2026-10-09 | 2026-10-09 | untried |
| modern material-image delta closure | 1 | 1 | 2 | 10,535 | 5,267 | 5,267 | 5,267 | 2026-10-08 | 2026-10-08 | untried |
| zombies vo grids (all maps, players + npc speakers) with 72 more csv suffixes cracked via the guide vocabulary | 1 | 1 | 521 | 2,840,147 | 5,451 | 5,451 | 5,451 | 2026-09-10 | 2026-09-10 | untried |
| mwiii-alias-context | 1 | 1 | 873 | 4,906,681 | 5,620 | 5,620 | 5,620 | 2026-10-09 | 2026-10-09 | untried |
| image family grid round 2, head 2 | 4 | 4 | 3,689 | 20,825,392 | 5,645 | 1,784 | 1,784 | 2026-10-09 | 2026-10-09 | live |
| an unnamed method | 1 | 38 | 19,908 | 117,577,360 | 5,906 | 1 | 1 | 2026-09-02 | 2026-09-24 | live |
| black market loot stream, itemshop, and contract icons | 1 | 1 | 7 | 43,712 | 6,244 | 6,244 | 6,244 | 2026-09-04 | 2026-09-04 | untried |
| anim game cross | 1 | 1 | 4 | 26,532 | 6,633 | 6,633 | 6,633 | 2026-09-03 | 2026-09-03 | untried |
| twc terrain-blend grid, pairs | 1 | 4 | 35,796 | 241,076,880 | 6,734 | 4,148 | 4,148 | 2026-10-08 | 2026-10-09 | live |
| verified embedded-model source vocabulary to material wrappers | 1 | 1 | 7 | 47,590 | 6,798 | 6,798 | 6,798 | 2026-10-09 | 2026-10-09 | untried |
| mw4-target-image-gaps | 1 | 1 | 2 | 13,945 | 6,972 | 6,972 | 6,972 | 2026-10-09 | 2026-10-09 | untried |
| final byte closure, guard cleared | 1 | 1 | 2 | 15,218 | 7,609 | 7,609 | 7,609 | 2026-08-25 | 2026-08-25 | untried |
| mp/blackout: aliases cracked from mpdialog bundles | 1 | 1 | 28 | 223,097 | 7,967 | 7,967 | 7,967 | 2026-09-11 | 2026-09-11 | untried |
| bo7 target-witnessed nonadjacent animation pairs gap 2-6 | 1 | 1 | 140 | 1,137,241 | 8,123 | 8,123 | 8,123 | 2026-10-09 | 2026-10-09 | untried |
| image siblings | 3 | 5 | 529 | 4,621,863 | 8,736 | 1,734 | 68,329 | 2026-08-20 | 2026-08-21 | spent |
| early cold war source literals | 1 | 1 | 3 | 26,471 | 8,823 | 8,823 | 8,823 | 2026-08-26 | 2026-08-26 | untried |
| blackout character banter grid: vox <spk> <idx> banter <c1> <c2> <line> <nn> over the ~60 named blackout speakers | 1 | 1 | 276 | 2,628,096 | 9,522 | 9,522 | 9,522 | 2026-09-10 | 2026-09-10 | untried |
| independently witnessed joint image prefix and suffix translations | 1 | 1 | 3 | 29,216 | 9,738 | 9,738 | 9,738 | 2026-10-09 | 2026-10-09 | untried |
| operator voice-line grid: every known phrase x every known operator | 1 | 1 | 253 | 2,606,300 | 10,301 | 10,301 | 10,301 | 2026-10-08 | 2026-10-08 | untried |
| channels | 2 | 4 | 916 | 9,598,953 | 10,479 | 2,732 | 602,442 | 2026-08-20 | 2026-08-20 | spent |
| cross-game transfer: every known name, rehashed under modwar22 policy | 1 | 1 | 313 | 3,494,661 | 11,165 | 11,165 | 11,165 | 2026-10-08 | 2026-10-08 | untried |
| alias family grid h3 r1 | 3 | 5 | 392 | 4,519,246 | 11,528 | 5,886 | 5,886 | 2026-10-09 | 2026-10-09 | live |
| cross-game transfer incl. dotted sound paths | 3 | 3 | 1,402 | 16,963,914 | 12,099 | 7,842 | 7,842 | 2026-10-08 | 2026-10-08 | live |
| paired-token-blocks-anim | 1 | 1 | 33 | 410,321 | 12,433 | 12,433 | 12,433 | 2026-08-20 | 2026-08-20 | untried |
| sound aliases named from the aliases they point at | 1 | 1 | 3 | 38,993 | 12,997 | 12,997 | 12,997 | 2026-09-05 | 2026-09-05 | untried |
| operator voice-line grid r1 | 2 | 2 | 6 | 78,008 | 13,001 | 13,001 | 13,001 | 2026-10-09 | 2026-10-09 | live |
| operator voice-line grid r2 | 1 | 1 | 3 | 39,004 | 13,001 | 13,001 | 13,001 | 2026-10-09 | 2026-10-09 | untried |
| image family grid round 2, head 1 | 5 | 5 | 1,401 | 18,515,770 | 13,216 | 2,728 | 3,703,154 | 2026-10-09 | 2026-10-09 | spent |
| cross-game transfer r1 | 3 | 6 | 1,679 | 22,848,995 | 13,608 | 3,737 | 3,737 | 2026-10-09 | 2026-10-09 | live |
| bo7 animation package modifiers at witnessed clip boundaries | 1 | 1 | 89 | 1,228,982 | 13,808 | 13,808 | 13,808 | 2026-10-09 | 2026-10-09 | untried |
| black ops 3 build names, verbatim, full harvest | 1 | 2 | 177 | 2,462,622 | 13,913 | 8,858 | 32,402 | 2026-08-22 | 2026-08-22 | cooling |
| cold war source filenames and text | 1 | 1 | 151 | 2,102,012 | 13,920 | 13,920 | 13,920 | 2026-08-27 | 2026-08-27 | untried |
| xanim family grid round 2, head 2 | 3 | 3 | 628 | 8,869,731 | 14,123 | 9,693 | 10,712 | 2026-10-09 | 2026-10-09 | live |
| every-game transfer after worker finds | 1 | 1 | 429 | 6,221,800 | 14,503 | 14,503 | 14,503 | 2026-10-09 | 2026-10-09 | untried |
| family gap filling | 1 | 103 | 1,258 | 19,646,089 | 15,616 | 654 | 1,115,535 | 2026-08-19 | 2026-10-09 | spent |
| \ bo4 image siblings from confirmed materials 20260830\ | 1 | 1 | 135 | 2,163,297 | 16,024 | 16,024 | 16,024 | 2026-08-30 | 2026-08-30 | untried |
| material family grid: middle x final token | 3 | 3 | 1,476 | 23,740,011 | 16,084 | 9,244 | 282,619 | 2026-10-09 | 2026-10-09 | spent |
| alias slot substitution | 4 | 9 | 1,354 | 21,780,323 | 16,085 | 6,535 | 2,047,927 | 2026-08-20 | 2026-08-21 | spent |
| zombies vo: gpu 3-token gap fill complete (112 prefixes) + 67 four-token suffixes (gapfill4 on the 3090) -> grids + aliases | 1 | 1 | 355 | 6,030,376 | 16,986 | 16,986 | 16,986 | 2026-09-11 | 2026-09-11 | untried |
| mw7 verified numeric and texture siblings | 1 | 1 | 114 | 1,963,655 | 17,225 | 17,225 | 17,225 | 2026-10-08 | 2026-10-08 | untried |
| rare-token-compound-splice-anim | 1 | 3 | 30 | 521,194 | 17,373 | 10,849 | 17,385 | 2026-08-20 | 2026-08-20 | live |
| two-slot alias slotswap, alias-only slot alphabet | 1 | 2 | 3,412 | 59,554,709 | 17,454 | 13,521 | 24,240 | 2026-10-08 | 2026-10-08 | live |
| black ops 4 final-byte solve after refreshed tables | 1 | 2 | 2 | 35,304 | 17,652 | 17,652 | 17,652 | 2026-08-27 | 2026-08-27 | live |
| black ops 3 build names, verbatim | 1 | 1 | 4 | 73,303 | 18,325 | 18,325 | 18,325 | 2026-08-22 | 2026-08-22 | untried |
| \ bo4 final-byte after upstream corpus refresh\ | 1 | 1 | 1 | 19,466 | 19,466 | 19,466 | 19,466 | 2026-08-29 | 2026-08-29 | untried |
| slot swap xanim | 3 | 3 | 566 | 12,168,903 | 21,499 | 7,962 | 812,953 | 2026-10-09 | 2026-10-09 | spent |
| sound alias: zombies dialogue aliases <suffix> plr <n> <v> from the cracked vox csv/script suffixes + banter aliases | 1 | 1 | 99 | 2,134,096 | 21,556 | 21,556 | 21,556 | 2026-09-10 | 2026-09-10 | untried |
| bo3 mod tools asset file list | 1 | 1 | 3 | 65,355 | 21,785 | 21,785 | 21,785 | 2026-08-22 | 2026-08-22 | untried |
| blackout vo: 5 more speaker tokens found by brute force (dmas sman repl cgor bza) x events + banter | 1 | 1 | 147 | 3,269,632 | 22,242 | 22,242 | 22,242 | 2026-09-11 | 2026-09-11 | untried |
| material directory swap: known bases and image stems x every modern material dir | 1 | 2 | 4,193 | 94,243,709 | 22,476 | 16,757 | 16,757 | 2026-10-08 | 2026-10-08 | live |
| rare shared-token splices | 1 | 2 | 7 | 158,622 | 22,660 | 13,212 | 79,348 | 2026-08-28 | 2026-08-29 | cooling |
| external sound paths with one directory dropped | 1 | 1 | 1 | 23,776 | 23,776 | 23,776 | 23,776 | 2026-09-04 | 2026-09-04 | untried |
| material family grid round 2, head 3 | 4 | 4 | 1,492 | 36,055,248 | 24,165 | 14,948 | 15,023 | 2026-10-09 | 2026-10-09 | live |
| material family grid round 3, head 1 | 4 | 4 | 2,444 | 60,419,232 | 24,721 | 14,129 | 16,137 | 2026-10-09 | 2026-10-09 | live |
| reversible endpoint token swaps | 1 | 1 | 2 | 49,872 | 24,936 | 24,936 | 24,936 | 2026-09-04 | 2026-09-04 | untried |
| sound files from aliases, after cross fill | 1 | 1 | 460 | 11,480,155 | 24,956 | 24,956 | 24,956 | 2026-10-05 | 2026-10-05 | untried |
| material family grid round 3, head 2 | 4 | 4 | 1,263 | 31,684,648 | 25,086 | 14,272 | 15,440 | 2026-10-09 | 2026-10-09 | live |
| sound files re-spelled with dotted dirs for mwiii | 1 | 1 | 19 | 488,448 | 25,707 | 25,707 | 25,707 | 2026-10-09 | 2026-10-09 | untried |
| codename swap: iw8/iw9/jup/t9/t10/sat/s4... and veh8/veh9 tokens exchanged in every known name | 1 | 2 | 969 | 24,930,732 | 25,728 | 23,351 | 23,351 | 2026-10-08 | 2026-10-08 | live |
| bo3 mod tools gdt asset names | 1 | 2 | 3 | 84,078 | 28,026 | 21,019 | 42,039 | 2026-08-22 | 2026-08-22 | live |
| alias family grid h1 r1 | 3 | 5 | 503 | 14,369,670 | 28,567 | 14,365 | 14,365 | 2026-10-09 | 2026-10-09 | live |
| packed twc/tw codes delta, new numbers | 2 | 4 | 165 | 4,731,660 | 28,676 | 9,260 | 42,159 | 2026-10-09 | 2026-10-09 | cooling |
| numbered families extended past their highest published member, every digit slot | 1 | 2 | 3,501 | 101,082,018 | 28,872 | 20,105 | 51,170 | 2026-10-08 | 2026-10-08 | live |
| mw4-sound-directory-spellings | 1 | 1 | 265 | 7,895,961 | 29,796 | 29,796 | 29,796 | 2026-10-09 | 2026-10-09 | untried |
| sound files from aliases, after topic x common quips | 1 | 1 | 386 | 11,662,505 | 30,213 | 30,213 | 30,213 | 2026-10-06 | 2026-10-06 | untried |
| alias family grid h2 r1 | 3 | 5 | 464 | 14,030,499 | 30,238 | 15,005 | 15,005 | 2026-10-09 | 2026-10-09 | live |
| sound files from aliases, after web-bigram aliases | 1 | 1 | 357 | 11,024,773 | 30,881 | 30,881 | 30,881 | 2026-10-05 | 2026-10-05 | untried |
| rare shared-token splices family size 13-30 | 1 | 1 | 10 | 325,039 | 32,503 | 32,503 | 32,503 | 2026-08-28 | 2026-08-28 | untried |
| black ops 4 family gap filling after refreshed corpus | 1 | 2 | 6 | 200,472 | 33,412 | 33,412 | 33,412 | 2026-08-27 | 2026-08-27 | live |
| aliases from sound files, after sound pair slots | 1 | 1 | 14 | 477,105 | 34,078 | 34,078 | 34,078 | 2026-10-01 | 2026-10-01 | untried |
| paired-token-blocks-alias-deterministic | 1 | 2 | 14 | 481,544 | 34,396 | 24,067 | 60,216 | 2026-08-20 | 2026-08-20 | live |
| paired-token-blocks-anim-deterministic | 1 | 9 | 104 | 3,708,652 | 35,660 | 15,884 | 206,784 | 2026-08-20 | 2026-08-20 | spent |
| final-byte-after-image-channel-seed | 1 | 1 | 1 | 36,014 | 36,014 | 36,014 | 36,014 | 2026-08-29 | 2026-08-29 | untried |
| sound alias all-boundary segment plan | 1 | 6 | 128,951 | 4,682,258,826 | 36,310 | 13,018 | 4,016,543 | 2026-10-08 | 2026-10-09 | spent |
| bo7 frozen image suffix witnessed preceding byte | 1 | 1 | 47 | 1,715,197 | 36,493 | 36,493 | 36,493 | 2026-10-09 | 2026-10-09 | untried |
| \ cw final-byte after upstream corpus refresh\ | 1 | 1 | 1 | 37,273 | 37,273 | 37,273 | 37,273 | 2026-08-29 | 2026-08-29 | untried |
| sound files from aliases, after quip triples | 1 | 1 | 316 | 11,798,006 | 37,335 | 37,335 | 37,335 | 2026-10-06 | 2026-10-06 | untried |
| numbered families on two axes | 1 | 2 | 7 | 265,407 | 37,915 | 22,119 | 22,119 | 2026-08-27 | 2026-08-27 | live |
| context swap sound alias r1 | 2 | 2 | 609 | 23,330,040 | 38,308 | 33,943 | 52,534 | 2026-10-09 | 2026-10-09 | live |
| slot swap sound alias r2 | 2 | 2 | 218 | 8,461,545 | 38,814 | 20,161 | 20,161 | 2026-10-09 | 2026-10-09 | live |
| sound files from aliases, after phrase grids | 1 | 1 | 284 | 11,146,413 | 39,247 | 39,247 | 39,247 | 2026-10-05 | 2026-10-05 | untried |
| learned coordinated repeated identifiers sound | 1 | 2 | 34 | 1,366,822 | 40,200 | 21,356 | 341,705 | 2026-09-22 | 2026-09-22 | spent |
| bo7 witnessed animation pairs shared with mw7 | 1 | 1 | 28 | 1,137,241 | 40,615 | 40,615 | 40,615 | 2026-10-09 | 2026-10-09 | untried |
| material family grid round 1, head 1 | 5 | 5 | 1,794 | 75,511,245 | 42,090 | 13,436 | 5,034,083 | 2026-10-09 | 2026-10-09 | spent |
| sound alias head swap | 1 | 10 | 240,859 | 10,323,473,232 | 42,861 | 21,799 | 17,981,430 | 2026-10-08 | 2026-10-09 | spent |
| external source filenames | 1 | 1 | 28 | 1,226,186 | 43,792 | 43,792 | 43,792 | 2026-08-27 | 2026-08-27 | untried |
| mw4-target-alias-file-paths | 1 | 1 | 5 | 221,329 | 44,265 | 44,265 | 44,265 | 2026-10-09 | 2026-10-09 | untried |
| bo7 witnessed animation pairs shared with mwiii | 1 | 1 | 25 | 1,137,241 | 45,489 | 45,489 | 45,489 | 2026-10-09 | 2026-10-09 | untried |
| zombies vo grids with suffixes cracked from the zm scripts' hashed vo say/function a2bd5a0c arguments | 1 | 1 | 67 | 3,073,427 | 45,872 | 45,872 | 45,872 | 2026-09-10 | 2026-09-10 | untried |
| weapon foley aliases from weapon animation events x take numbers | 1 | 15 | 52,487 | 2,529,126,540 | 48,185 | 6,551 | 49,703 | 2026-10-09 | 2026-10-09 | cooling |
| image interior counterparts after richkiller | 1 | 1 | 18 | 904,787 | 50,265 | 50,265 | 50,265 | 2026-09-04 | 2026-09-04 | untried |
| \ cold war rare shared-token splice family 2401-2700 xanim\ | 1 | 1 | 8 | 409,075 | 51,134 | 51,134 | 51,134 | 2026-08-28 | 2026-08-28 | untried |
| continuations | 1 | 1 | 776 | 39,892,300 | 51,407 | 51,407 | 51,407 | 2026-08-20 | 2026-08-20 | untried |
| zombies vo: 165 more suffixes from the 13 hashed player-voice-category stringtables (hashed/stringtable in bo4-source: common + crew + map tables) -> files + aliases | 1 | 1 | 111 | 5,745,628 | 51,762 | 51,762 | 51,762 | 2026-09-11 | 2026-09-11 | untried |
| positional grids: same-length name families, every position crossed | 1 | 2 | 1,062 | 56,112,944 | 52,837 | 48,878 | 57,492 | 2026-10-09 | 2026-10-09 | live |
| older-title vocabulary | 1 | 2 | 59 | 3,144,542 | 53,297 | 34,939 | 112,305 | 2026-08-21 | 2026-08-21 | cooling |
| image siblings from confirmed materials current | 1 | 1 | 43 | 2,307,057 | 53,652 | 53,652 | 53,652 | 2026-09-01 | 2026-09-01 | untried |
| black ops 3 build names, respelled | 1 | 1 | 1 | 54,358 | 54,358 | 54,358 | 54,358 | 2026-08-22 | 2026-08-22 | untried |
| aliases from sound-file basenames, dotted names included | 4 | 4 | 26 | 1,425,264 | 54,817 | 27,408 | 178,158 | 2026-10-08 | 2026-10-08 | cooling |
| material dirs on every image/material core | 1 | 1 | 394 | 21,614,499 | 54,859 | 54,859 | 54,859 | 2026-10-09 | 2026-10-09 | untried |
| alias slot substitution, left context only | 3 | 6 | 1,934 | 109,332,515 | 56,531 | 8,885 | 2,932,361 | 2026-08-20 | 2026-08-20 | spent |
| xanim family grid: middle x final token | 4 | 4 | 209 | 11,825,864 | 56,583 | 22,397 | 739,116 | 2026-10-09 | 2026-10-09 | spent |
| image siblings from confirmed materials | 1 | 1 | 35 | 2,001,561 | 57,187 | 57,187 | 57,187 | 2026-08-26 | 2026-08-26 | untried |
| cod-ultimate source literals | 1 | 2 | 12 | 686,330 | 57,194 | 49,023 | 49,023 | 2026-08-31 | 2026-08-31 | live |
| image siblings of richkiller-derived materials | 1 | 1 | 39 | 2,396,589 | 61,451 | 61,451 | 61,451 | 2026-09-04 | 2026-09-04 | untried |
| edits anim | 2 | 5 | 208 | 12,868,629 | 61,868 | 15,318 | 15,318 | 2026-08-20 | 2026-08-20 | live |
| mwiii-material-context | 1 | 1 | 348 | 21,755,781 | 62,516 | 62,516 | 62,516 | 2026-10-09 | 2026-10-09 | untried |
| sound files from aliases, after long-phrase quips | 1 | 1 | 176 | 11,236,875 | 63,845 | 63,845 | 63,845 | 2026-10-05 | 2026-10-05 | untried |
| image siblings of confirmed materials | 1 | 211 | 7,524 | 484,091,736 | 64,339 | 393 | 80,965 | 2026-08-19 | 2026-10-09 | spent |
| cold war animation token edits after new findings | 2 | 2 | 93 | 5,989,742 | 64,405 | 32,080 | 3,038,360 | 2026-08-26 | 2026-08-31 | spent |
| image family grid: middle x final token | 5 | 5 | 396 | 26,031,120 | 65,735 | 22,060 | 1,735,408 | 2026-10-09 | 2026-10-09 | spent |
| image family grid snowball r2 h2 | 3 | 3 | 236 | 15,640,395 | 66,272 | 27,439 | 27,439 | 2026-10-09 | 2026-10-09 | live |
| viewmodel anim <-> player foley alias seam | 1 | 1 | 2 | 134,846 | 67,423 | 67,423 | 67,423 | 2026-10-09 | 2026-10-09 | untried |
| adjacent-token-order-anim | 1 | 1 | 2 | 136,243 | 68,121 | 68,121 | 68,121 | 2026-08-20 | 2026-08-20 | untried |
| mwiii-image-context | 1 | 1 | 252 | 17,405,181 | 69,068 | 69,068 | 69,068 | 2026-10-09 | 2026-10-09 | untried |
| rare compound material splice | 1 | 1 | 3 | 208,316 | 69,438 | 69,438 | 69,438 | 2026-09-04 | 2026-09-04 | untried |
| witnessed nonadjacent paired animation changes | 1 | 1 | 3 | 214,702 | 71,567 | 71,567 | 71,567 | 2026-09-22 | 2026-09-22 | untried |
| cross-game transfer incl. all modern finds | 2 | 2 | 97 | 7,070,062 | 72,887 | 36,823 | 3,535,031 | 2026-10-09 | 2026-10-09 | spent |
| rare shared-token splices family size 31-60 | 1 | 2 | 23 | 1,691,810 | 73,556 | 42,295 | 42,295 | 2026-08-28 | 2026-08-28 | live |
| cross-game transfer round 2 | 1 | 2 | 101 | 7,634,010 | 75,584 | 50,223 | 50,223 | 2026-10-08 | 2026-10-08 | live |
| paired-token-blocks-anim-lengths2-5-rare | 1 | 5 | 72 | 5,466,329 | 75,921 | 34,115 | 547,307 | 2026-08-20 | 2026-08-20 | spent |
| vo sound files derived from known vox  sound aliases: en\vox\scripted\<mode>\<map>\<alias> <n>.sn100 | 1 | 1 | 10,388 | 797,443,920 | 76,765 | 76,765 | 76,765 | 2026-09-10 | 2026-09-10 | untried |
| sound tail swap: known stems x every modern tail | 1 | 2 | 286 | 22,124,427 | 77,358 | 46,670 | 225,785 | 2026-10-08 | 2026-10-08 | cooling |
| bo3 mod tools asset names | 1 | 2 | 22 | 1,735,532 | 78,887 | 78,887 | 78,887 | 2026-08-24 | 2026-08-24 | live |
| witnessed nonadjacent paired image changes | 1 | 1 | 57 | 4,674,651 | 82,011 | 82,011 | 82,011 | 2026-09-22 | 2026-09-22 | untried |
| sound files from aliases with takes, after pooled grid rows | 1 | 1 | 35 | 2,904,447 | 82,984 | 82,984 | 82,984 | 2026-10-01 | 2026-10-01 | untried |
| other types' stems as image stems x measured image endings | 1 | 2 | 64,177 | 5,328,425,550 | 83,027 | 68,871 | 68,871 | 2026-10-08 | 2026-10-08 | live |
| mw4-alias-context | 1 | 1 | 58 | 4,918,981 | 84,810 | 84,810 | 84,810 | 2026-10-09 | 2026-10-09 | untried |
| sound paths with a repeated word, filled from the family | 1 | 4 | 84 | 7,545,486 | 89,827 | 47,768 | 47,768 | 2026-10-05 | 2026-10-05 | live |
| rare-token-compound-splice-model | 1 | 2 | 60 | 5,611,060 | 93,517 | 80,164 | 80,164 | 2026-08-20 | 2026-08-20 | live |
| mwii-sound-directory-spellings | 1 | 1 | 29 | 2,790,571 | 96,226 | 96,226 | 96,226 | 2026-10-09 | 2026-10-09 | untried |
| zombies character conversations: vox <map> plr <n> <idx> banter <chr1> <chr2> <v> from zm vo.gsc + zm characters.gsc chrnames | 1 | 1 | 625 | 61,424,640 | 98,279 | 98,279 | 98,279 | 2026-09-10 | 2026-09-10 | untried |
| family grid current | 1 | 1 | 38 | 3,786,603 | 99,647 | 99,647 | 99,647 | 2026-08-31 | 2026-08-31 | untried |
| alias family grid h2 r2 | 1 | 1 | 28 | 2,799,785 | 99,992 | 99,992 | 99,992 | 2026-10-09 | 2026-10-09 | untried |
| sound files from aliases, after deep quips | 1 | 1 | 108 | 11,283,066 | 104,472 | 104,472 | 104,472 | 2026-10-05 | 2026-10-05 | untried |
| twck 3-token names: known 2-token name + appended token | 1 | 2 | 326 | 34,205,130 | 104,923 | 72,776 | 187,940 | 2026-10-09 | 2026-10-09 | live |
| mwiii-image-codename | 1 | 1 | 2 | 211,406 | 105,703 | 105,703 | 105,703 | 2026-10-09 | 2026-10-09 | untried |
| alias family grid h1 r2 | 1 | 1 | 27 | 2,860,931 | 105,960 | 105,960 | 105,960 | 2026-10-09 | 2026-10-09 | untried |
| cross-game transfer r2 | 1 | 1 | 35 | 3,806,669 | 108,761 | 108,761 | 108,761 | 2026-10-09 | 2026-10-09 | untried |
| \ cw sound-alias token insertion and deletion 20260830\ | 1 | 1 | 70 | 7,641,905 | 109,170 | 109,170 | 109,170 | 2026-08-30 | 2026-08-30 | untried |
| xanim family grid round 2, head 1 | 2 | 2 | 55 | 6,005,858 | 109,197 | 107,247 | 107,247 | 2026-10-09 | 2026-10-09 | live |
| pooled insert-delete sound alias r1 | 1 | 1 | 216 | 23,825,866 | 110,304 | 110,304 | 110,304 | 2026-10-10 | 2026-10-10 | untried |
| rare shared token splice 13 30 current | 1 | 1 | 3 | 331,149 | 110,383 | 110,383 | 110,383 | 2026-09-02 | 2026-09-02 | untried |
| rare-token-compound-splice-batch | 1 | 4 | 236 | 26,219,346 | 111,098 | 48,548 | 3,278,056 | 2026-08-20 | 2026-08-20 | spent |
| material directory swap, image names stripped of their last 1-2 segments as bases | 1 | 2 | 998 | 111,799,600 | 112,023 | 109,178 | 115,021 | 2026-10-08 | 2026-10-08 | live |
| material family grid round 1, head 3 | 2 | 2 | 160 | 18,025,710 | 112,660 | 57,774 | 2,253,213 | 2026-10-09 | 2026-10-09 | spent |
| slot swap image | 3 | 4 | 563 | 63,797,145 | 113,316 | 50,663 | 331,460 | 2026-10-09 | 2026-10-09 | cooling |
| twcj 3-token names: known 2-token name + appended token | 1 | 2 | 365 | 41,926,288 | 114,866 | 76,788 | 227,860 | 2026-10-09 | 2026-10-09 | live |
| coordinated identifiers, sound | 1 | 1 | 6 | 699,191 | 116,531 | 116,531 | 116,531 | 2026-09-25 | 2026-09-25 | untried |
| slot swap, all kinds | 1 | 1 | 832 | 96,955,680 | 116,533 | 116,533 | 116,533 | 2026-10-09 | 2026-10-09 | untried |
| context indel xanim r1 | 1 | 1 | 36 | 4,261,400 | 118,372 | 118,372 | 118,372 | 2026-10-09 | 2026-10-09 | untried |
| packed twc/tw material codes, two slots, every observed number | 1 | 4 | 2,288 | 272,754,104 | 119,210 | 72,801 | 240,439 | 2026-10-09 | 2026-10-09 | cooling |
| slot swap sound alias | 3 | 3 | 102 | 12,684,083 | 124,353 | 70,442 | 1,410,202 | 2026-10-09 | 2026-10-09 | spent |
| cold war two-token suffix precedents current | 1 | 1 | 1 | 124,990 | 124,990 | 124,990 | 124,990 | 2026-09-03 | 2026-09-03 | untried |
| sound files from aliases placed among siblings | 2 | 2 | 188 | 24,379,882 | 129,680 | 87,071 | 87,071 | 2026-10-08 | 2026-10-08 | live |
| rare shared-token splices family size 61-120 | 1 | 1 | 18 | 2,355,489 | 130,860 | 130,860 | 130,860 | 2026-08-28 | 2026-08-28 | untried |
| figglefx cold war community export | 1 | 1 | 1 | 132,659 | 132,659 | 132,659 | 132,659 | 2026-09-04 | 2026-09-04 | untried |
| context swap w2 sound alias r1 | 1 | 1 | 161 | 21,435,293 | 133,138 | 133,138 | 133,138 | 2026-10-09 | 2026-10-09 | untried |
| sound aliases built from file paths | 1 | 1 | 8 | 1,089,910 | 136,238 | 136,238 | 136,238 | 2026-10-05 | 2026-10-05 | untried |
| context indel material r1 | 1 | 1 | 149 | 20,647,967 | 138,576 | 138,576 | 138,576 | 2026-10-09 | 2026-10-09 | untried |
| context insert-delete material r1 | 1 | 1 | 496 | 68,890,611 | 138,892 | 138,892 | 138,892 | 2026-10-09 | 2026-10-09 | untried |
| slot swap from the ending, width 1 | 1 | 1 | 1,017 | 144,045,794 | 141,637 | 141,637 | 141,637 | 2026-10-09 | 2026-10-09 | untried |
| material family grid h2 r1 | 3 | 5 | 297 | 42,632,800 | 143,544 | 52,284 | 776,453 | 2026-10-09 | 2026-10-09 | spent |
| cross-game transfer: every known name, rehashed under mwiii policy | 1 | 1 | 24 | 3,494,661 | 145,610 | 145,610 | 145,610 | 2026-10-08 | 2026-10-08 | untried |
| context indel sound asset r1 | 1 | 1 | 27 | 4,070,439 | 150,757 | 150,757 | 150,757 | 2026-10-09 | 2026-10-09 | untried |
| alias slot substitution, right context only | 1 | 2 | 146 | 22,349,656 | 153,079 | 121,544 | 121,544 | 2026-08-20 | 2026-08-20 | live |
| sibling directory swap: a dir name the basename repeats, replaced in both places by its siblings | 1 | 2 | 49 | 7,764,854 | 158,466 | 129,416 | 129,416 | 2026-10-08 | 2026-10-08 | live |
| material family grid snowball r2 h3 | 4 | 4 | 226 | 36,325,836 | 160,733 | 44,736 | 4,540,729 | 2026-10-09 | 2026-10-09 | spent |
| rare shared-token splices families 18901-19200 | 1 | 1 | 20 | 3,237,958 | 161,897 | 161,897 | 161,897 | 2026-08-29 | 2026-08-29 | untried |
| material family grid h1 r1 | 3 | 5 | 688 | 111,899,645 | 162,644 | 60,452 | 641,480 | 2026-10-09 | 2026-10-09 | spent |
| vox speaker x line grid, unseen cells | 1 | 1 | 34 | 5,564,535 | 163,662 | 163,662 | 163,662 | 2026-08-23 | 2026-08-23 | untried |
| bo7 sound files from witnessed alias prefix rewrites | 1 | 1 | 3 | 493,482 | 164,494 | 164,494 | 164,494 | 2026-10-09 | 2026-10-09 | untried |
| image siblings after suffix | 1 | 1 | 14 | 2,307,537 | 164,824 | 164,824 | 164,824 | 2026-09-02 | 2026-09-02 | untried |
| correlated-token-blocks-alias-wide | 1 | 2 | 7 | 1,175,308 | 167,901 | 146,934 | 146,934 | 2026-08-20 | 2026-08-20 | live |
| slot swap material | 3 | 3 | 690 | 120,468,912 | 174,592 | 137,687 | 360,082 | 2026-10-09 | 2026-10-09 | live |
| cold war image siblings from current confirmed materials | 1 | 1 | 13 | 2,281,761 | 175,520 | 175,520 | 175,520 | 2026-09-01 | 2026-09-01 | untried |
| adjacent-token-order-model | 1 | 2 | 10 | 1,765,338 | 176,533 | 110,332 | 441,340 | 2026-08-20 | 2026-08-20 | cooling |
| family grid completion, shared tails only | 1 | 1 | 23 | 4,076,970 | 177,259 | 177,259 | 177,259 | 2026-08-24 | 2026-08-24 | untried |
| image siblings closure followup | 1 | 1 | 13 | 2,309,889 | 177,683 | 177,683 | 177,683 | 2026-09-02 | 2026-09-02 | untried |
| sound language and encoding variants | 1 | 2 | 53 | 9,914,264 | 187,061 | 113,060 | 374,530 | 2026-08-20 | 2026-09-11 | cooling |
| slot swap wide, images+materials | 1 | 1 | 820 | 154,118,861 | 187,949 | 187,949 | 187,949 | 2026-10-09 | 2026-10-09 | untried |
| rare shared-token splices family sizes 10201-10500 | 1 | 1 | 14 | 2,725,854 | 194,703 | 194,703 | 194,703 | 2026-08-28 | 2026-08-28 | untried |
| mwii sound alias heads x shared tails | 1 | 3 | 5,889 | 1,165,843,231 | 197,969 | 14,786 | 608,692 | 2026-10-08 | 2026-10-08 | spent |
| alias segment plan | 1 | 14 | 343,205 | 70,861,267,102 | 206,469 | 58,451 | 20,699,120 | 2026-10-08 | 2026-10-09 | spent |
| numbered designation slots | 1 | 1 | 16 | 3,352,846 | 209,552 | 209,552 | 209,552 | 2026-10-01 | 2026-10-01 | untried |
| modern warfare 2 build names, verbatim | 1 | 1 | 1 | 209,784 | 209,784 | 209,784 | 209,784 | 2026-08-22 | 2026-08-22 | untried |
| yamyamok verified material-to-image channel seam | 1 | 1 | 266 | 57,678,684 | 216,837 | 216,837 | 216,837 | 2026-10-09 | 2026-10-09 | untried |
| context swap material r1 | 2 | 2 | 452 | 98,157,571 | 217,162 | 172,847 | 172,847 | 2026-10-09 | 2026-10-09 | live |
| slot swap from end w2 sound alias r1 | 2 | 2 | 77 | 16,896,804 | 219,439 | 141,111 | 141,111 | 2026-10-09 | 2026-10-09 | live |
| sound files from aliases r1 | 1 | 1 | 88 | 19,484,278 | 221,412 | 221,412 | 221,412 | 2026-10-09 | 2026-10-09 | untried |
| rare compound image splice | 1 | 1 | 1 | 223,738 | 223,738 | 223,738 | 223,738 | 2026-09-04 | 2026-09-04 | untried |
| modwar7 verified sound takes width 2 | 1 | 1 | 101 | 23,305,893 | 230,751 | 230,751 | 230,751 | 2026-10-09 | 2026-10-09 | untried |
| sound tail swap, two-letter-codec stems included | 1 | 2 | 244 | 56,537,832 | 231,712 | 200,488 | 200,488 | 2026-10-08 | 2026-10-08 | live |
| mwii sound directory spellings | 1 | 1 | 12 | 2,800,349 | 233,362 | 233,362 | 233,362 | 2026-10-10 | 2026-10-10 | untried |
| cross-game verbatim transfer | 1 | 1 | 3 | 702,081 | 234,027 | 234,027 | 234,027 | 2026-08-25 | 2026-08-25 | untried |
| slot swap from end w1 sound alias r1 | 2 | 3 | 131 | 30,784,079 | 234,992 | 119,669 | 119,669 | 2026-10-09 | 2026-10-09 | live |
| token edits anim | 1 | 1 | 13 | 3,067,026 | 235,925 | 235,925 | 235,925 | 2026-09-03 | 2026-09-03 | untried |
| sound files from aliases | 1 | 4 | 188 | 44,736,077 | 237,957 | 159,878 | 194,856 | 2026-10-01 | 2026-10-05 | live |
| image channel completion | 1 | 165 | 1,775 | 423,035,488 | 238,329 | 5,159 | 2,824,231 | 2026-08-20 | 2026-10-09 | spent |
| mcdp material redecorations after pr971 | 1 | 1 | 5 | 1,198,438 | 239,687 | 239,687 | 239,687 | 2026-08-27 | 2026-08-27 | untried |
| refreshed mcdp material core redecorations | 1 | 1 | 5 | 1,198,717 | 239,743 | 239,743 | 239,743 | 2026-08-28 | 2026-08-28 | untried |
| xanim family grid h2 r1 | 3 | 3 | 39 | 9,501,074 | 243,617 | 122,290 | 122,290 | 2026-10-09 | 2026-10-09 | live |
| speaker grids re-run cw | 1 | 1 | 6 | 1,466,925 | 244,487 | 244,487 | 244,487 | 2026-08-24 | 2026-08-24 | untried |
| xanim family grid round 1, head 1 | 2 | 2 | 24 | 6,005,858 | 250,244 | 158,048 | 158,048 | 2026-10-09 | 2026-10-09 | live |
| token insertion and deletion anim | 1 | 1 | 12 | 3,115,854 | 259,654 | 259,654 | 259,654 | 2026-09-07 | 2026-09-07 | untried |
| bo7 package modifiers and terrain orders shared with mwii | 1 | 1 | 6 | 1,605,332 | 267,555 | 267,555 | 267,555 | 2026-10-09 | 2026-10-09 | untried |
| paired-token-blocks-model-deterministic | 1 | 6 | 148 | 39,959,454 | 269,996 | 96,527 | 475,923 | 2026-08-20 | 2026-08-20 | cooling |
| material directory swap, cross-type snowball round 1 | 1 | 2 | 413 | 113,116,650 | 273,890 | 246,968 | 307,395 | 2026-10-08 | 2026-10-08 | live |
| mined substitution equivalence classes | 1 | 2 | 211 | 58,068,971 | 275,208 | 151,043 | 1,529,932 | 2026-08-25 | 2026-08-25 | spent |
| aliases placed in their family's sound folders | 1 | 1 | 3 | 829,676 | 276,558 | 276,558 | 276,558 | 2026-09-30 | 2026-09-30 | untried |
| context swap, vocab pooled across five kinds | 1 | 1 | 226 | 63,674,475 | 281,745 | 281,745 | 281,745 | 2026-10-09 | 2026-10-09 | untried |
| witnessed nonadjacent paired model changes | 1 | 1 | 4 | 1,127,177 | 281,794 | 281,794 | 281,794 | 2026-09-22 | 2026-09-22 | untried |
| token-insertion-deletion-alias | 1 | 2 | 28 | 7,924,449 | 283,016 | 233,070 | 233,070 | 2026-08-20 | 2026-08-20 | live |
| corpus-mined substitutions, top 1500 | 1 | 2 | 371 | 105,553,541 | 284,510 | 178,297 | 703,699 | 2026-08-25 | 2026-08-25 | cooling |
| adjacent-token-order-batch | 1 | 2 | 26 | 7,517,953 | 289,152 | 250,599 | 250,599 | 2026-08-20 | 2026-08-20 | live |
| per-prefix continuations | 3 | 4 | 538 | 159,447,283 | 296,370 | 79,618 | 1,430,530 | 2026-08-19 | 2026-08-21 | spent |
| sound encoding tail swap | 1 | 1 | 35 | 10,573,320 | 302,094 | 302,094 | 302,094 | 2026-10-09 | 2026-10-09 | untried |
| context swap w2 material r1 | 1 | 1 | 223 | 68,022,306 | 305,032 | 305,032 | 305,032 | 2026-10-09 | 2026-10-09 | untried |
| image siblings bo4 | 1 | 1 | 6 | 1,879,167 | 313,194 | 313,194 | 313,194 | 2026-08-26 | 2026-08-26 | untried |
| yamyamok verified material tails with target-held conventions | 1 | 1 | 4,646 | 1,459,350,288 | 314,108 | 314,108 | 314,108 | 2026-10-09 | 2026-10-09 | untried |
| token insertion deletion animation | 1 | 1 | 10 | 3,152,190 | 315,219 | 315,219 | 315,219 | 2026-09-09 | 2026-09-09 | untried |
| rare shared-token splices family size 241-480 | 1 | 2 | 89 | 28,268,386 | 317,622 | 224,352 | 543,622 | 2026-08-28 | 2026-08-28 | live |
| sound files from aliases, after web-bigram widening | 1 | 1 | 35 | 11,161,426 | 318,897 | 318,897 | 318,897 | 2026-10-05 | 2026-10-05 | untried |
| animation token insertion and deletion after pr983 | 1 | 1 | 9 | 2,961,267 | 329,029 | 329,029 | 329,029 | 2026-08-27 | 2026-08-27 | untried |
| numbered families extended past their highest published member | 1 | 2 | 325 | 106,997,756 | 329,223 | 286,090 | 387,673 | 2026-10-09 | 2026-10-09 | live |
| slot swap width 1 alternation r1 | 1 | 1 | 298 | 98,343,079 | 330,010 | 330,010 | 330,010 | 2026-10-09 | 2026-10-09 | untried |
| slot swap from end w1 material r1 | 2 | 3 | 507 | 167,863,543 | 331,091 | 202,425 | 202,425 | 2026-10-09 | 2026-10-09 | live |
| context swap image r1 | 2 | 2 | 185 | 62,174,275 | 336,077 | 323,596 | 358,057 | 2026-10-09 | 2026-10-09 | live |
| sound files from aliases, after wide triples | 1 | 1 | 35 | 11,813,019 | 337,514 | 337,514 | 337,514 | 2026-10-06 | 2026-10-06 | untried |
| sound files from aliases, after wiki probe | 1 | 1 | 35 | 11,833,282 | 338,093 | 338,093 | 338,093 | 2026-10-07 | 2026-10-07 | untried |
| token insertion and deletion | 5 | 21 | 1,164 | 394,291,167 | 338,738 | 34,598 | 3,459,022 | 2026-08-20 | 2026-09-08 | spent |
| mw7 expanded numeric siblings for materials animations images | 1 | 1 | 50 | 16,974,722 | 339,494 | 339,494 | 339,494 | 2026-10-08 | 2026-10-08 | untried |
| deep image channel completion after pr977 | 1 | 1 | 11 | 3,767,092 | 342,462 | 342,462 | 342,462 | 2026-08-27 | 2026-08-27 | untried |
| sound-alias context length completion | 1 | 1 | 1 | 353,063 | 353,063 | 353,063 | 353,063 | 2026-09-04 | 2026-09-04 | untried |
| external bo4-source core respelling | 1 | 2 | 9 | 3,192,200 | 354,688 | 319,220 | 319,220 | 2026-08-28 | 2026-08-28 | live |
| aliases from sound-file basenames r1 | 1 | 3 | 3 | 1,071,720 | 357,240 | 357,167 | 357,299 | 2026-10-09 | 2026-10-09 | live |
| sound tail swap | 1 | 1 | 22 | 8,009,936 | 364,088 | 364,088 | 364,088 | 2026-10-09 | 2026-10-09 | untried |
| context swap material r3 | 2 | 2 | 273 | 99,637,980 | 364,974 | 292,989 | 6,843,631 | 2026-10-09 | 2026-10-10 | spent |
| deep image channel completion after pr979 | 1 | 1 | 10 | 3,766,987 | 376,698 | 376,698 | 376,698 | 2026-08-27 | 2026-08-27 | untried |
| xanim family grid h1 r1 | 1 | 2 | 17 | 6,407,762 | 376,927 | 355,435 | 401,105 | 2026-10-09 | 2026-10-09 | live |
| images for every material prefix x measured channel endings | 1 | 2 | 105 | 41,331,480 | 393,633 | 251,442 | 1,399,903 | 2026-10-06 | 2026-10-06 | cooling |
| \ refreshed mcdp material core redecorations\ | 1 | 1 | 3 | 1,199,830 | 399,943 | 399,943 | 399,943 | 2026-08-29 | 2026-08-29 | untried |
| slot swap from end w1+w2 r1 | 2 | 4 | 2,409 | 973,843,944 | 404,252 | 306,625 | 306,625 | 2026-10-09 | 2026-10-09 | live |
| twck 4-token names: known 3-token name + appended token | 1 | 2 | 14 | 5,720,858 | 408,632 | 286,042 | 715,107 | 2026-10-09 | 2026-10-09 | live |
| slot swap from end w1 image r1 | 2 | 2 | 122 | 50,266,397 | 412,019 | 255,717 | 1,050,254 | 2026-10-09 | 2026-10-09 | cooling |
| rare shared-token splices family size 121-240 | 1 | 2 | 29 | 12,188,574 | 420,295 | 320,751 | 320,751 | 2026-08-28 | 2026-08-28 | live |
| yamyamok sound alias segments from the refreshed confirmed corpus | 1 | 1 | 734 | 309,075,991 | 421,084 | 421,084 | 421,084 | 2026-10-09 | 2026-10-09 | untried |
| xanim family grid round 1, head 2 | 1 | 1 | 7 | 2,956,483 | 422,354 | 422,354 | 422,354 | 2026-10-09 | 2026-10-09 | untried |
| xanim family grid round 3, head 2 | 1 | 1 | 7 | 2,957,106 | 422,443 | 422,443 | 422,443 | 2026-10-09 | 2026-10-09 | untried |
| xanim family grid snowball r2 h2 | 1 | 1 | 7 | 2,957,106 | 422,443 | 422,443 | 422,443 | 2026-10-09 | 2026-10-09 | untried |
| xanim family grid snowball r3 h2 | 1 | 1 | 7 | 2,957,106 | 422,443 | 422,443 | 422,443 | 2026-10-09 | 2026-10-09 | untried |
| context indel r1 | 3 | 4 | 622 | 263,401,526 | 423,475 | 187,977 | 3,005,644 | 2026-10-09 | 2026-10-10 | spent |
| cross-game sound stem transfer | 1 | 1 | 27 | 11,737,632 | 434,727 | 434,727 | 434,727 | 2026-08-20 | 2026-08-20 | untried |
| modwar7 target-held image whole-weapon identifier slots | 1 | 1 | 82 | 35,769,700 | 436,215 | 436,215 | 436,215 | 2026-10-09 | 2026-10-09 | untried |
| cross-game transfer: every known name, rehashed under yamyamok policy | 1 | 1 | 8 | 3,494,661 | 436,832 | 436,832 | 436,832 | 2026-10-08 | 2026-10-08 | untried |
| material family grid round 2, head 2 | 2 | 2 | 36 | 15,842,302 | 440,063 | 416,902 | 465,950 | 2026-10-09 | 2026-10-09 | live |
| incremented basename digits | 1 | 1 | 2 | 887,360 | 443,680 | 443,680 | 443,680 | 2026-09-04 | 2026-09-04 | untried |
| two-slot alias slotswap, round 2 | 1 | 2 | 162 | 72,051,094 | 444,759 | 223,603 | 36,050,857 | 2026-10-08 | 2026-10-08 | spent |
| shared-tail family grid follow-up | 1 | 1 | 8 | 3,578,096 | 447,262 | 447,262 | 447,262 | 2026-08-26 | 2026-08-26 | untried |
| title prefix swap material | 1 | 1 | 57 | 25,662,355 | 450,216 | 450,216 | 450,216 | 2026-10-09 | 2026-10-09 | untried |
| material family grid snowball r2 h1 | 4 | 4 | 135 | 61,331,044 | 454,304 | 235,888 | 1,703,640 | 2026-10-09 | 2026-10-09 | cooling |
| long image channel grid | 1 | 1 | 19 | 8,938,946 | 470,470 | 470,470 | 470,470 | 2026-10-09 | 2026-10-09 | untried |
| family grid top 30 | 1 | 1 | 10 | 4,709,171 | 470,917 | 470,917 | 470,917 | 2026-09-14 | 2026-09-14 | untried |
| context insert-delete image r1 | 1 | 1 | 94 | 44,638,509 | 474,877 | 474,877 | 474,877 | 2026-10-09 | 2026-10-09 | untried |
| twc quads: token inserted inside a known triple | 1 | 2 | 1,843 | 877,148,272 | 475,935 | 449,819 | 449,819 | 2026-10-09 | 2026-10-09 | live |
| decal volume mask atlas suffix on every known image | 1 | 2 | 2 | 964,188 | 482,094 | 482,088 | 482,100 | 2026-10-08 | 2026-10-08 | live |
| rare shared-token splices families 13801-14100 | 1 | 2 | 15 | 7,293,903 | 486,260 | 260,496 | 260,496 | 2026-08-28 | 2026-08-28 | live |
| slotswap | 3 | 6 | 1,903 | 928,681,787 | 488,009 | 183,556 | 5,712,231 | 2026-08-20 | 2026-09-03 | spent |
| context insert-delete sound alias r1 | 1 | 1 | 28 | 13,665,812 | 488,064 | 488,064 | 488,064 | 2026-10-09 | 2026-10-09 | untried |
| modern image channel completion incl. packed parts | 5 | 5 | 80 | 39,822,760 | 497,784 | 194,257 | 884,950 | 2026-10-09 | 2026-10-09 | cooling |
| sound-file family grid within folder and tail | 4 | 4 | 39 | 19,588,144 | 502,260 | 288,060 | 612,129 | 2026-10-09 | 2026-10-09 | live |
| pooled context swap xanim r1 | 1 | 1 | 46 | 23,463,013 | 510,065 | 510,065 | 510,065 | 2026-10-09 | 2026-10-09 | untried |
| context swap r1 | 2 | 4 | 1,246 | 638,542,263 | 512,473 | 198,035 | 198,035 | 2026-10-09 | 2026-10-09 | live |
| numbers in place over every table generation | 7 | 7 | 5,509 | 2,832,081,574 | 514,082 | 211,380 | 44,953,675 | 2026-10-09 | 2026-10-09 | spent |
| context swap xanim r1 | 2 | 2 | 49 | 25,221,259 | 514,719 | 493,677 | 587,410 | 2026-10-09 | 2026-10-09 | live |
| cold war xanim token insertions and deletions cap12 minseen8 | 1 | 1 | 6 | 3,142,235 | 523,705 | 523,705 | 523,705 | 2026-09-08 | 2026-09-08 | untried |
| wc 4-token names: known 3-token name + appended token | 1 | 2 | 10 | 5,280,792 | 528,079 | 293,377 | 2,640,396 | 2026-10-09 | 2026-10-09 | cooling |
| context indel image r1 | 1 | 1 | 37 | 19,735,055 | 533,379 | 533,379 | 533,379 | 2026-10-09 | 2026-10-09 | untried |
| black ops 4 materials from image cores current | 1 | 1 | 9 | 4,838,880 | 537,653 | 537,653 | 537,653 | 2026-09-01 | 2026-09-01 | untried |
| mined substitutions, ranking tail | 1 | 1 | 237 | 129,160,520 | 544,981 | 544,981 | 544,981 | 2026-08-25 | 2026-08-25 | untried |
| tw-family terrain grids, pairs | 1 | 2 | 882 | 482,153,760 | 546,659 | 492,999 | 613,427 | 2026-10-08 | 2026-10-08 | live |
| token edits material after pr828 | 1 | 1 | 4 | 2,186,916 | 546,729 | 546,729 | 546,729 | 2026-08-26 | 2026-08-26 | untried |
| cold war legacy multi-axis numbered grids | 1 | 1 | 7 | 3,858,203 | 551,171 | 551,171 | 551,171 | 2026-08-29 | 2026-08-29 | untried |
| slot swap from end w2 material r1 | 2 | 2 | 96 | 53,830,703 | 560,736 | 545,055 | 577,085 | 2026-10-09 | 2026-10-09 | live |
| materials from image cores | 1 | 171 | 1,486 | 840,697,368 | 565,745 | 9,045 | 163,223 | 2026-08-20 | 2026-10-08 | spent |
| twcj 4-token names: known 3-token name + appended token | 1 | 2 | 12 | 6,801,020 | 566,751 | 485,787 | 680,102 | 2026-10-09 | 2026-10-09 | live |
| material family grid snowball r1 h3 | 1 | 1 | 16 | 9,095,890 | 568,493 | 568,493 | 568,493 | 2026-10-09 | 2026-10-09 | untried |
| rare shared-token splices family size 481-960 | 1 | 2 | 128 | 73,051,283 | 570,713 | 314,886 | 314,886 | 2026-08-28 | 2026-08-28 | live |
| twj 3-token names: known 2-token name + appended token | 1 | 1 | 5 | 2,880,432 | 576,086 | 576,086 | 576,086 | 2026-10-09 | 2026-10-09 | untried |
| cold war same-directory outer-inner cross | 1 | 3 | 9 | 5,196,762 | 577,418 | 577,418 | 577,418 | 2026-08-27 | 2026-08-27 | live |
| final byte substitution | 1 | 2 | 121 | 70,135,764 | 579,634 | 467,581 | 467,581 | 2026-08-22 | 2026-08-22 | live |
| \ cw adjacent material token order 20260830\ | 1 | 1 | 4 | 2,374,577 | 593,644 | 593,644 | 593,644 | 2026-08-30 | 2026-08-30 | untried |
| rare shared token splice 61 120 current | 1 | 2 | 8 | 4,761,390 | 595,173 | 396,782 | 396,782 | 2026-09-02 | 2026-09-02 | live |
| locally evidenced adjacent token order | 1 | 1 | 2 | 1,205,866 | 602,933 | 602,933 | 602,933 | 2026-08-26 | 2026-08-26 | untried |
| cold war same-directory token graft | 1 | 2 | 10 | 6,114,860 | 611,486 | 611,486 | 611,486 | 2026-08-27 | 2026-08-27 | live |
| slot swap from end w1 xanim r1 | 2 | 3 | 99 | 61,312,725 | 619,320 | 283,472 | 890,689 | 2026-10-09 | 2026-10-09 | cooling |
| mw4-image-context | 1 | 1 | 28 | 17,426,028 | 622,358 | 622,358 | 622,358 | 2026-10-09 | 2026-10-09 | untried |
| material family grid snowball r1 h1 | 4 | 8 | 198 | 123,338,312 | 622,920 | 170,317 | 303,899 | 2026-10-09 | 2026-10-09 | live |
| rare shared token splice 481 960 current | 1 | 2 | 118 | 74,610,250 | 632,290 | 414,501 | 1,332,325 | 2026-09-02 | 2026-09-02 | cooling |
| slot swap from the ending, width 2 | 1 | 1 | 156 | 99,120,663 | 635,388 | 635,388 | 635,388 | 2026-10-09 | 2026-10-09 | untried |
| slot swap w2 material | 1 | 1 | 80 | 51,224,032 | 640,300 | 640,300 | 640,300 | 2026-10-09 | 2026-10-09 | untried |
| mw4-linked-sound-namespaces | 1 | 1 | 2 | 1,322,411 | 661,205 | 661,205 | 661,205 | 2026-10-09 | 2026-10-09 | untried |
| twc terrain-blend grid, full numeric token range, pairs | 1 | 2 | 1,243 | 827,195,120 | 665,482 | 409,908 | 409,908 | 2026-10-09 | 2026-10-09 | live |
| templates | 3 | 5 | 395 | 265,290,228 | 671,620 | 286,113 | 3,386,404 | 2026-08-20 | 2026-09-03 | spent |
| high-control terminal token counterparts | 1 | 2 | 6 | 4,130,040 | 688,340 | 516,254 | 516,254 | 2026-09-04 | 2026-09-04 | live |
| image interior2 | 1 | 1 | 3 | 2,121,927 | 707,309 | 707,309 | 707,309 | 2026-09-08 | 2026-09-08 | untried |
| material family grid snowball r1 h2 | 4 | 5 | 57 | 40,569,637 | 711,748 | 386,512 | 386,512 | 2026-10-09 | 2026-10-09 | live |
| execution quips, glove-topic word pairs on one speaker | 1 | 1 | 13 | 9,290,304 | 714,638 | 714,638 | 714,638 | 2026-10-05 | 2026-10-05 | untried |
| mwiii verified sound-name transfer after the modern submissions | 1 | 1 | 1 | 722,060 | 722,060 | 722,060 | 722,060 | 2026-10-09 | 2026-10-09 | untried |
| numbers in place, quick-wins r1 | 3 | 7 | 8,057 | 5,894,785,803 | 731,635 | 376,410 | 3,777,143 | 2026-10-09 | 2026-10-09 | spent |
| xanim family grid snowball r1 h2 | 2 | 2 | 8 | 5,914,900 | 739,362 | 422,443 | 2,957,794 | 2026-10-09 | 2026-10-09 | cooling |
| mined classes over indel-augmented pairs | 1 | 2 | 75 | 55,459,097 | 739,454 | 396,848 | 8,962,006 | 2026-08-25 | 2026-08-25 | spent |
| slot swap width 2, five types | 1 | 1 | 185 | 137,019,389 | 740,645 | 740,645 | 740,645 | 2026-10-09 | 2026-10-09 | untried |
| slot swap from end w2 image r1 | 1 | 1 | 22 | 16,450,994 | 747,772 | 747,772 | 747,772 | 2026-10-09 | 2026-10-09 | untried |
| correlated-token-blocks-material-image-wide | 1 | 6 | 563 | 425,162,272 | 755,172 | 270,359 | 5,907,185 | 2026-08-20 | 2026-08-20 | spent |
| corpus-mined substitutions | 7 | 38 | 1,354 | 1,042,097,492 | 769,643 | 25,953 | 1,289,462 | 2026-08-25 | 2026-09-02 | spent |
| image family grid round 1, head 1 | 4 | 4 | 19 | 14,812,616 | 779,611 | 411,461 | 3,703,154 | 2026-10-09 | 2026-10-09 | cooling |
| rare shared-token splices family sizes 9901-10200 | 1 | 1 | 9 | 7,174,482 | 797,164 | 797,164 | 797,164 | 2026-08-28 | 2026-08-28 | untried |
| length-sorted interior tokens | 1 | 1 | 1 | 816,286 | 816,286 | 816,286 | 816,286 | 2026-08-27 | 2026-08-27 | untried |
| image family grid snowball r2 h1 | 2 | 2 | 9 | 7,420,866 | 824,540 | 742,086 | 742,086 | 2026-10-09 | 2026-10-09 | live |
| xanim family grid round 1, head 3 | 1 | 1 | 2 | 1,651,884 | 825,942 | 825,942 | 825,942 | 2026-10-09 | 2026-10-09 | untried |
| token trigram walk, image | 1 | 1 | 6 | 5,000,000 | 833,333 | 833,333 | 833,333 | 2026-10-01 | 2026-10-01 | untried |
| \ bo4 sound-alias token insertion and deletion 20260830\ | 1 | 1 | 9 | 7,647,725 | 849,747 | 849,747 | 849,747 | 2026-08-30 | 2026-08-30 | untried |
| slot + title-prefix swap on cross-game corpus | 2 | 2 | 339 | 290,683,378 | 857,473 | 431,280 | 431,280 | 2026-10-09 | 2026-10-09 | live |
| rare shared token splice 31 60 current | 1 | 1 | 1 | 861,934 | 861,934 | 861,934 | 861,934 | 2026-09-02 | 2026-09-02 | untried |
| context indel sound alias r1 | 1 | 1 | 6 | 5,180,028 | 863,338 | 863,338 | 863,338 | 2026-10-09 | 2026-10-09 | untried |
| context indel material r2 | 1 | 1 | 24 | 20,785,844 | 866,076 | 866,076 | 866,076 | 2026-10-10 | 2026-10-10 | untried |
| paired-token-blocks-model-lengths2-4 | 1 | 2 | 21 | 18,272,811 | 870,133 | 702,844 | 702,844 | 2026-08-20 | 2026-08-20 | live |
| last-three token rotation | 1 | 2 | 2 | 1,746,976 | 873,488 | 873,488 | 873,488 | 2026-08-27 | 2026-08-27 | live |
| image channel completion restart | 1 | 1 | 3 | 2,624,441 | 874,813 | 874,813 | 874,813 | 2026-09-09 | 2026-09-09 | untried |
| yamyamok verified image segments with target-held endings | 1 | 1 | 1,292 | 1,132,181,268 | 876,301 | 876,301 | 876,301 | 2026-10-09 | 2026-10-09 | untried |
| complemented basename digits | 1 | 1 | 1 | 887,359 | 887,359 | 887,359 | 887,359 | 2026-09-04 | 2026-09-04 | untried |
| twcj 3-token names: prepended token + known 2-token name | 1 | 2 | 47 | 41,926,288 | 892,048 | 873,464 | 911,441 | 2026-10-09 | 2026-10-09 | live |
| family grid completion | 1 | 1 | 4 | 3,639,611 | 909,902 | 909,902 | 909,902 | 2026-08-27 | 2026-08-27 | untried |
| \ sound-alias positional token substitutions\ | 1 | 2 | 8 | 7,395,792 | 924,474 | 528,252 | 3,698,022 | 2026-08-30 | 2026-08-30 | cooling |
| slot swap width 3, five types | 1 | 1 | 104 | 97,470,830 | 937,219 | 937,219 | 937,219 | 2026-10-09 | 2026-10-09 | untried |
| zigzag basename token recombination | 1 | 1 | 1 | 939,211 | 939,211 | 939,211 | 939,211 | 2026-08-27 | 2026-08-27 | untried |
| zigzag basename tokens | 1 | 2 | 2 | 1,878,438 | 939,219 | 939,219 | 939,219 | 2026-08-27 | 2026-08-27 | live |
| image family grid h2 r1 | 2 | 2 | 11 | 10,423,504 | 947,591 | 579,098 | 579,098 | 2026-10-09 | 2026-10-09 | live |
| slot swap from end w2 xanim r4 | 1 | 1 | 16 | 15,213,091 | 950,818 | 950,818 | 950,818 | 2026-10-10 | 2026-10-10 | untried |
| numbers in place r1 | 3 | 6 | 5,180 | 5,011,728,697 | 967,515 | 282,385 | 748,392 | 2026-10-09 | 2026-10-09 | live |
| cold war material token edits after new findings | 2 | 3 | 101 | 98,466,866 | 974,919 | 360,669 | 5,500,996 | 2026-08-26 | 2026-08-31 | spent |
| context swap w2 material r2 | 1 | 1 | 70 | 69,045,226 | 986,360 | 986,360 | 986,360 | 2026-10-10 | 2026-10-10 | untried |
| animation token insertion and deletion after pr986 | 1 | 1 | 3 | 2,962,200 | 987,400 | 987,400 | 987,400 | 2026-08-27 | 2026-08-27 | untried |
| \ cold war animation token edits refreshed 20260830\ | 1 | 1 | 3 | 2,995,208 | 998,402 | 998,402 | 998,402 | 2026-08-29 | 2026-08-29 | untried |
| context swap material r2 | 2 | 2 | 98 | 98,811,827 | 1,008,283 | 759,783 | 759,783 | 2026-10-09 | 2026-10-10 | live |
| packed codes + one more slot | 1 | 5 | 18,513 | 19,134,643,296 | 1,033,578 | 301,459 | 480,045,646 | 2026-10-09 | 2026-10-09 | spent |
| context swap w2 + pooled r1 | 2 | 4 | 2,352 | 2,451,786,516 | 1,042,426 | 796,034 | 796,034 | 2026-10-09 | 2026-10-09 | live |
| slot swap w2 xanim | 1 | 1 | 10 | 10,505,282 | 1,050,528 | 1,050,528 | 1,050,528 | 2026-10-09 | 2026-10-09 | untried |
| rare shared-token splices family size 961-1200 | 1 | 2 | 33 | 34,762,466 | 1,053,408 | 1,022,406 | 1,086,347 | 2026-08-28 | 2026-08-28 | live |
| alphanumeric code slots | 1 | 2 | 134 | 141,267,947 | 1,054,238 | 316,339 | 316,339 | 2026-10-01 | 2026-10-01 | live |
| edits material | 2 | 5 | 139 | 150,302,473 | 1,081,312 | 439,383 | 1,589,712 | 2026-08-20 | 2026-08-20 | cooling |
| cold war corpus-mined substitutions rank 401-500 | 1 | 2 | 6 | 6,492,678 | 1,082,113 | 1,082,113 | 1,082,113 | 2026-08-27 | 2026-08-27 | live |
| sound files from aliases, slash spelling | 1 | 1 | 18 | 19,528,677 | 1,084,926 | 1,084,926 | 1,084,926 | 2026-10-09 | 2026-10-09 | untried |
| codename swap incl. rex (mw7) and s6 | 1 | 2 | 31 | 34,317,342 | 1,107,011 | 903,088 | 903,088 | 2026-10-08 | 2026-10-08 | live |
| title prefix swap image | 1 | 1 | 10 | 11,090,467 | 1,109,046 | 1,109,046 | 1,109,046 | 2026-10-09 | 2026-10-09 | untried |
| pooled insert-delete image r1 | 1 | 1 | 45 | 50,074,313 | 1,112,762 | 1,112,762 | 1,112,762 | 2026-10-10 | 2026-10-10 | untried |
| rare shared token splice 1921 3840 current | 1 | 2 | 261 | 290,452,894 | 1,112,846 | 580,905 | 13,202,404 | 2026-09-02 | 2026-09-02 | spent |
| material <-> image cores r1 | 3 | 3 | 19 | 21,219,124 | 1,116,796 | 415,776 | 7,083,296 | 2026-10-09 | 2026-10-09 | spent |
| pooled context swap material r1 | 1 | 1 | 75 | 84,233,278 | 1,123,110 | 1,123,110 | 1,123,110 | 2026-10-09 | 2026-10-09 | untried |
| context swap w2 xanim r1 | 1 | 1 | 17 | 19,288,826 | 1,134,636 | 1,134,636 | 1,134,636 | 2026-10-09 | 2026-10-09 | untried |
| yamyamok verified sound takes width 2 | 1 | 1 | 28 | 32,102,298 | 1,146,510 | 1,146,510 | 1,146,510 | 2026-10-09 | 2026-10-09 | untried |
| slot swap from end w1 image r2 | 1 | 1 | 22 | 25,258,770 | 1,148,125 | 1,148,125 | 1,148,125 | 2026-10-10 | 2026-10-10 | untried |
| quick wins combined | 18 | 22 | 6,145 | 7,325,270,766 | 1,192,070 | 227,721 | 434,677 | 2026-10-09 | 2026-10-09 | live |
| material bases as image stems x measured image endings | 1 | 5 | 5,470 | 6,522,349,392 | 1,192,385 | 378,202 | 652,333,372 | 2026-10-08 | 2026-10-08 | spent |
| xanim segment plan | 1 | 8 | 6,522 | 7,789,877,464 | 1,194,400 | 170,871 | 6,504,641 | 2026-10-08 | 2026-10-08 | spent |
| context swap w2 image r1 | 1 | 1 | 45 | 53,984,108 | 1,199,646 | 1,199,646 | 1,199,646 | 2026-10-09 | 2026-10-09 | untried |
| cold war adjacent material token order | 1 | 1 | 2 | 2,403,554 | 1,201,777 | 1,201,777 | 1,201,777 | 2026-09-03 | 2026-09-03 | untried |
| context swap w2 xanim r2 | 1 | 1 | 16 | 19,354,112 | 1,209,632 | 1,209,632 | 1,209,632 | 2026-10-10 | 2026-10-10 | untried |
| \ bo4 adjacent xmodel token order 20260830\ | 1 | 1 | 1 | 1,238,704 | 1,238,704 | 1,238,704 | 1,238,704 | 2026-08-30 | 2026-08-30 | untried |
| xanim family grid round 2, head 3 | 3 | 3 | 4 | 4,959,744 | 1,239,936 | 826,624 | 1,653,248 | 2026-10-09 | 2026-10-09 | live |
| sibling token substitution, right context only | 1 | 1 | 369 | 461,529,482 | 1,250,757 | 1,250,757 | 1,250,757 | 2026-08-19 | 2026-08-19 | untried |
| rare shared token splice 121 240 current | 1 | 1 | 5 | 6,312,219 | 1,262,443 | 1,262,443 | 1,262,443 | 2026-09-02 | 2026-09-02 | untried |
| positional grids | 2 | 4 | 554 | 708,200,620 | 1,278,340 | 881,956 | 1,506,919 | 2026-10-09 | 2026-10-09 | live |
| title prefix swap sound alias | 1 | 1 | 4 | 5,175,739 | 1,293,934 | 1,293,934 | 1,293,934 | 2026-10-09 | 2026-10-09 | untried |
| designation grids | 1 | 1 | 1 | 1,302,385 | 1,302,385 | 1,302,385 | 1,302,385 | 2026-10-01 | 2026-10-01 | untried |
| model component counterparts with measured integer offsets | 1 | 1 | 1 | 1,307,654 | 1,307,654 | 1,307,654 | 1,307,654 | 2026-09-22 | 2026-09-22 | untried |
| pooled insert-delete material r1 | 1 | 1 | 51 | 67,859,043 | 1,330,569 | 1,330,569 | 1,330,569 | 2026-10-10 | 2026-10-10 | untried |
| slot swap xanim r2 | 1 | 1 | 3 | 4,060,380 | 1,353,460 | 1,353,460 | 1,353,460 | 2026-10-09 | 2026-10-09 | untried |
| slot swap tail width 1 alternation r1 | 1 | 1 | 106 | 144,263,097 | 1,360,972 | 1,360,972 | 1,360,972 | 2026-10-09 | 2026-10-09 | untried |
| token edits material current | 1 | 2 | 48 | 65,328,704 | 1,361,014 | 759,636 | 759,636 | 2026-08-29 | 2026-08-29 | live |
| context insert-delete xanim r1 | 1 | 1 | 13 | 17,707,490 | 1,362,114 | 1,362,114 | 1,362,114 | 2026-10-09 | 2026-10-09 | untried |
| sound alias slot substitution | 1 | 2 | 3 | 4,119,600 | 1,373,200 | 1,028,660 | 2,062,280 | 2026-08-21 | 2026-08-22 | live |
| cod-name-finder-verified-export | 1 | 2 | 10 | 4,145,582 | 1,381,860 | 1,381,860 | 1,381,860 | 2026-10-09 | 2026-10-09 | untried |
| sound tail swap + take renumber 1..12 | 1 | 1 | 24 | 33,201,344 | 1,383,389 | 1,383,389 | 1,383,389 | 2026-10-09 | 2026-10-09 | untried |
| slot swap from end w1 material r2 | 1 | 1 | 41 | 56,810,968 | 1,385,633 | 1,385,633 | 1,385,633 | 2026-10-10 | 2026-10-10 | untried |
| sound files re-rooted under every codename | 3 | 3 | 18 | 25,497,642 | 1,416,535 | 653,785 | 8,499,214 | 2026-10-09 | 2026-10-09 | spent |
| mwiii-sound-directory-spellings | 1 | 1 | 5 | 7,103,293 | 1,420,658 | 1,420,658 | 1,420,658 | 2026-10-09 | 2026-10-09 | untried |
| sound files for known aliases: borrowed sibling directories x takes x game tails | 1 | 2 | 169 | 242,273,700 | 1,433,572 | 1,316,616 | 1,316,616 | 2026-10-08 | 2026-10-08 | live |
| slot swap image r2 | 2 | 2 | 22 | 31,879,685 | 1,449,076 | 1,228,344 | 1,767,911 | 2026-10-09 | 2026-10-09 | live |
| image family grid round 2, head 3 | 3 | 3 | 10 | 14,778,741 | 1,477,874 | 985,249 | 985,249 | 2026-10-09 | 2026-10-09 | live |
| image family grid snowball r1 h2 | 3 | 4 | 14 | 20,868,340 | 1,490,595 | 869,703 | 869,703 | 2026-10-09 | 2026-10-09 | live |
| token edits model cap30 | 1 | 1 | 21 | 31,607,140 | 1,505,101 | 1,505,101 | 1,505,101 | 2026-09-03 | 2026-09-03 | untried |
| modern material <-> image cores snowball r1 | 3 | 4 | 18 | 27,264,216 | 1,514,678 | 680,536 | 2,273,205 | 2026-10-09 | 2026-10-09 | cooling |
| refreshed token insertion/deletion | 1 | 1 | 9 | 13,694,727 | 1,521,636 | 1,521,636 | 1,521,636 | 2026-08-27 | 2026-08-27 | untried |
| material directories on every image and material core | 1 | 2 | 50 | 76,089,710 | 1,521,794 | 1,201,743 | 1,201,743 | 2026-10-09 | 2026-10-09 | live |
| animation token insertion and deletion | 1 | 1 | 2 | 3,043,656 | 1,521,828 | 1,521,828 | 1,521,828 | 2026-09-02 | 2026-09-02 | untried |
| token edits material after new findings | 1 | 1 | 21 | 32,170,813 | 1,531,943 | 1,531,943 | 1,531,943 | 2026-08-25 | 2026-08-25 | untried |
| multi-word slots, each frame's own words crossed | 1 | 1 | 1 | 1,534,736 | 1,534,736 | 1,534,736 | 1,534,736 | 2026-10-01 | 2026-10-01 | untried |
| precedents top50 | 1 | 1 | 40 | 61,822,767 | 1,545,569 | 1,545,569 | 1,545,569 | 2026-09-02 | 2026-09-02 | untried |
| material cores spelled as image | 5 | 13 | 1,006 | 1,578,450,625 | 1,569,036 | 289,958 | 42,125,208 | 2026-08-25 | 2026-09-03 | spent |
| sibling token substitution | 7 | 14 | 2,724 | 4,277,911,710 | 1,570,452 | 206,904 | 76,964,097 | 2026-08-19 | 2026-09-10 | spent |
| \ bo4 material token edits cap20 minseen4 20260830\ | 1 | 1 | 34 | 53,634,909 | 1,577,497 | 1,577,497 | 1,577,497 | 2026-08-29 | 2026-08-29 | untried |
| slot swap w1+w2 r1 | 2 | 2 | 296 | 467,870,042 | 1,580,642 | 850,672 | 850,672 | 2026-10-09 | 2026-10-09 | live |
| \ cold war rare shared-token splice family 3601-3900 material\ | 1 | 1 | 3 | 4,744,802 | 1,581,600 | 1,581,600 | 1,581,600 | 2026-08-28 | 2026-08-28 | untried |
| materials for every image base x measured material endings | 1 | 2 | 20 | 32,651,001 | 1,632,550 | 1,591,620 | 1,591,620 | 2026-10-06 | 2026-10-06 | live |
| precedents top10 | 2 | 2 | 19 | 31,423,294 | 1,653,857 | 1,122,260 | 1,122,260 | 2026-09-02 | 2026-09-02 | live |
| slot swap width 2 alternation r1 | 1 | 1 | 83 | 137,577,307 | 1,657,557 | 1,657,557 | 1,657,557 | 2026-10-09 | 2026-10-09 | untried |
| material segment plan | 1 | 8 | 17,293 | 28,910,453,924 | 1,671,800 | 210,527 | 13,206,582 | 2026-10-08 | 2026-10-08 | spent |
| sound path two-word slots | 1 | 2 | 131 | 221,173,229 | 1,688,345 | 1,676,775 | 1,676,775 | 2026-10-01 | 2026-10-01 | live |
| alias token substitutions | 1 | 3 | 7 | 11,834,165 | 1,690,595 | 1,314,899 | 1,314,911 | 2026-09-07 | 2026-09-07 | live |
| material token edits after new findings | 1 | 2 | 38 | 64,915,906 | 1,708,313 | 1,708,313 | 1,708,313 | 2026-08-26 | 2026-08-26 | live |
| \ bo4 rare shared-token splice family 2701-3000 material\ | 1 | 1 | 5 | 8,580,314 | 1,716,062 | 1,716,062 | 1,716,062 | 2026-08-28 | 2026-08-28 | untried |
| same-directory outer/interior cross 20260827 | 1 | 1 | 1 | 1,732,344 | 1,732,344 | 1,732,344 | 1,732,344 | 2026-08-27 | 2026-08-27 | untried |
| image family grid h2 r2 | 1 | 1 | 3 | 5,211,953 | 1,737,317 | 1,737,317 | 1,737,317 | 2026-10-09 | 2026-10-09 | untried |
| yamyamok verified sound alias heads with target-held conventions | 1 | 1 | 582 | 1,016,586,000 | 1,746,711 | 1,746,711 | 1,746,711 | 2026-10-09 | 2026-10-09 | untried |
| material <-> image cores r2 | 1 | 1 | 4 | 7,071,164 | 1,767,791 | 1,767,791 | 1,767,791 | 2026-10-09 | 2026-10-09 | untried |
| dotted sound files: slot swap both ends, family grid, codename swap r1 | 1 | 1 | 72 | 128,666,725 | 1,787,037 | 1,787,037 | 1,787,037 | 2026-10-09 | 2026-10-09 | untried |
| rare shared-token splices family sizes 7501-7800 | 1 | 1 | 2 | 3,574,174 | 1,787,087 | 1,787,087 | 1,787,087 | 2026-08-28 | 2026-08-28 | untried |
| slot swap image+material corpus | 1 | 1 | 20 | 37,060,338 | 1,853,016 | 1,853,016 | 1,853,016 | 2026-10-09 | 2026-10-09 | untried |
| material family grid snowball r3 h2 | 3 | 3 | 13 | 24,306,345 | 1,869,718 | 1,350,352 | 8,102,115 | 2026-10-09 | 2026-10-09 | cooling |
| deep image channel completion after pr980 | 1 | 1 | 2 | 3,767,176 | 1,883,588 | 1,883,588 | 1,883,588 | 2026-08-27 | 2026-08-27 | untried |
| deep image channel closure after new seed | 1 | 1 | 2 | 3,790,183 | 1,895,091 | 1,895,091 | 1,895,091 | 2026-08-29 | 2026-08-29 | untried |
| slot swap w2 image | 1 | 1 | 17 | 32,239,657 | 1,896,450 | 1,896,450 | 1,896,450 | 2026-10-09 | 2026-10-09 | untried |
| slot swap material r4 | 1 | 1 | 21 | 40,304,204 | 1,919,247 | 1,919,247 | 1,919,247 | 2026-10-09 | 2026-10-09 | untried |
| sound tail swap: renumbered takes 1..30 x every modern tail | 1 | 2 | 123 | 237,272,412 | 1,929,044 | 1,670,947 | 2,281,444 | 2026-10-08 | 2026-10-08 | live |
| twc 4-token names: known 3-token name + appended token | 1 | 4 | 6,278 | 12,226,355,372 | 1,947,492 | 922,340 | 54,778,735 | 2026-10-09 | 2026-10-09 | spent |
| mcdp | 1 | 1 | 2,846 | 5,545,804,740 | 1,948,631 | 1,948,631 | 1,948,631 | 2026-08-23 | 2026-08-23 | untried |
| material directory swap, cross-type snowball round 2 | 1 | 2 | 58 | 113,134,850 | 1,950,600 | 1,414,178 | 3,142,650 | 2026-10-08 | 2026-10-08 | live |
| deep image channel completion after richkiller ledger | 1 | 1 | 2 | 3,906,974 | 1,953,487 | 1,953,487 | 1,953,487 | 2026-09-04 | 2026-09-04 | untried |
| mined indels, anchored | 1 | 2 | 116 | 226,836,463 | 1,955,486 | 1,435,681 | 3,065,341 | 2026-08-25 | 2026-08-25 | live |
| rare shared-token splices family sizes 11101-11400 | 1 | 1 | 4 | 7,916,087 | 1,979,021 | 1,979,021 | 1,979,021 | 2026-08-28 | 2026-08-28 | untried |
| rare shared-token splices families 21601-21900 | 1 | 1 | 1 | 1,980,622 | 1,980,622 | 1,980,622 | 1,980,622 | 2026-08-29 | 2026-08-29 | untried |
| sound character substitution | 1 | 1 | 490 | 983,467,758 | 2,007,077 | 2,007,077 | 2,007,077 | 2026-08-24 | 2026-08-24 | untried |
| rare shared-token splices family sizes 6601-6900 | 1 | 2 | 13 | 26,110,812 | 2,008,524 | 1,450,600 | 1,450,600 | 2026-08-28 | 2026-08-28 | live |
| context indel sound asset r2 | 1 | 1 | 2 | 4,072,588 | 2,036,294 | 2,036,294 | 2,036,294 | 2026-10-10 | 2026-10-10 | untried |
| family grid, shared tails, cold war | 1 | 1 | 2 | 4,076,947 | 2,038,473 | 2,038,473 | 2,038,473 | 2026-08-24 | 2026-08-24 | untried |
| family column cross product | 3 | 9 | 349 | 711,519,426 | 2,038,737 | 456,163 | 54,076,619 | 2026-08-19 | 2026-09-02 | spent |
| slot swap from end w1 sound asset r1 | 2 | 2 | 32 | 66,155,388 | 2,067,355 | 1,383,440 | 1,383,440 | 2026-10-09 | 2026-10-09 | live |
| xanim all-boundary segment plan | 1 | 2 | 668 | 1,386,517,248 | 2,075,624 | 1,824,364 | 1,824,364 | 2026-10-08 | 2026-10-08 | live |
| sound path word slots | 1 | 2 | 109 | 226,556,874 | 2,078,503 | 1,187,257 | 49,760,166 | 2026-10-01 | 2026-10-01 | spent |
| slot swap from end w2 material r2 | 1 | 1 | 13 | 27,196,436 | 2,092,033 | 2,092,033 | 2,092,033 | 2026-10-10 | 2026-10-10 | untried |
| context swap xanim r3 | 1 | 1 | 9 | 18,856,985 | 2,095,220 | 2,095,220 | 2,095,220 | 2026-10-09 | 2026-10-09 | untried |
| rare shared splice 121 240 cw 20260903 | 1 | 1 | 3 | 6,315,365 | 2,105,121 | 2,105,121 | 2,105,121 | 2026-09-03 | 2026-09-03 | untried |
| corpus-mined substitutions, top 200 | 1 | 5 | 30 | 63,659,860 | 2,121,995 | 1,273,098 | 3,183,216 | 2026-08-27 | 2026-08-27 | live |
| rare shared-token splices family size 1501-1800 | 1 | 2 | 18 | 38,218,845 | 2,123,269 | 1,194,361 | 1,194,361 | 2026-08-28 | 2026-08-28 | live |
| family grid next families | 1 | 1 | 2 | 4,259,269 | 2,129,634 | 2,129,634 | 2,129,634 | 2026-08-31 | 2026-08-31 | untried |
| twck 3-token names: prepended token + known 2-token name | 1 | 2 | 16 | 34,205,130 | 2,137,820 | 1,900,285 | 2,443,223 | 2026-10-09 | 2026-10-09 | live |
| yamyamok terrain four-layer joins of target-held pairs | 1 | 1 | 543 | 1,163,969,689 | 2,143,590 | 2,143,590 | 2,143,590 | 2026-10-09 | 2026-10-09 | untried |
| \ cw image siblings after bo4 gain 20260830\ | 1 | 1 | 1 | 2,163,297 | 2,163,297 | 2,163,297 | 2,163,297 | 2026-08-30 | 2026-08-30 | untried |
| material token insertion and deletion after pr982 | 1 | 1 | 15 | 32,495,105 | 2,166,340 | 2,166,340 | 2,166,340 | 2026-08-27 | 2026-08-27 | untried |
| rare shared-token splices families 15001-15300 | 1 | 1 | 1 | 2,199,697 | 2,199,697 | 2,199,697 | 2,199,697 | 2026-08-28 | 2026-08-28 | untried |
| witnessed nonadjacent paired material changes | 1 | 1 | 3 | 6,629,438 | 2,209,812 | 2,209,812 | 2,209,812 | 2026-09-22 | 2026-09-22 | untried |
| \ cold war material token edits cap30 minseen3 20260830\ | 1 | 1 | 36 | 79,633,756 | 2,212,048 | 2,212,048 | 2,212,048 | 2026-08-29 | 2026-08-29 | untried |
| execution quips, probe with 12.3m chained phrases | 1 | 1 | 11 | 24,542,054 | 2,231,095 | 2,231,095 | 2,231,095 | 2026-10-05 | 2026-10-05 | untried |
| precedents top70 | 1 | 1 | 36 | 81,027,780 | 2,250,771 | 2,250,771 | 2,250,771 | 2026-09-02 | 2026-09-02 | untried |
| slot swap image r4 | 1 | 1 | 7 | 15,899,306 | 2,271,329 | 2,271,329 | 2,271,329 | 2026-10-09 | 2026-10-09 | untried |
| sibling token substitution, left context only | 2 | 3 | 1,401 | 3,216,420,428 | 2,295,803 | 769,926 | 3,368,815 | 2026-08-19 | 2026-08-20 | cooling |
| wc 3-token names: known 2-token name + appended token | 1 | 1 | 3 | 6,901,035 | 2,300,345 | 2,300,345 | 2,300,345 | 2026-10-09 | 2026-10-09 | untried |
| \ cold war material token edits cap20 minseen4 20260830\ | 1 | 1 | 23 | 53,630,368 | 2,331,755 | 2,331,755 | 2,331,755 | 2026-08-29 | 2026-08-29 | untried |
| \ bo4 adjacent material token order 20260830\ | 1 | 1 | 1 | 2,374,563 | 2,374,563 | 2,374,563 | 2,374,563 | 2026-08-30 | 2026-08-30 | untried |
| \ sound-alias two-token substitutions\ | 1 | 1 | 2 | 4,861,240 | 2,430,620 | 2,430,620 | 2,430,620 | 2026-08-30 | 2026-08-30 | untried |
| image channel completion, measured channel list | 1 | 2 | 36 | 88,257,624 | 2,451,600 | 2,451,600 | 2,451,600 | 2026-08-23 | 2026-08-23 | live |
| token abbreviation and expansion | 1 | 2 | 11 | 27,057,793 | 2,459,799 | 1,716,208 | 1,716,208 | 2026-10-01 | 2026-10-01 | live |
| \ cold war rare shared-token splice family 2401-2700 image\ | 1 | 1 | 1 | 2,507,207 | 2,507,207 | 2,507,207 | 2,507,207 | 2026-08-28 | 2026-08-28 | untried |
| \ cw adjacent image token order 20260830\ | 1 | 1 | 1 | 2,509,437 | 2,509,437 | 2,509,437 | 2,509,437 | 2026-08-30 | 2026-08-30 | untried |
| token insertion and deletion material | 1 | 1 | 13 | 32,998,295 | 2,538,330 | 2,538,330 | 2,538,330 | 2026-08-31 | 2026-08-31 | untried |
| sound uncarried two-segment endings top 500 | 1 | 1 | 10 | 25,397,193 | 2,539,719 | 2,539,719 | 2,539,719 | 2026-08-26 | 2026-08-26 | untried |
| slot swap from end w1 sound alias r2 | 1 | 1 | 4 | 10,350,481 | 2,587,620 | 2,587,620 | 2,587,620 | 2026-10-09 | 2026-10-09 | untried |
| high-control terminal token counterparts after bo4 texture ledger | 1 | 1 | 2 | 5,190,062 | 2,595,031 | 2,595,031 | 2,595,031 | 2026-09-04 | 2026-09-04 | untried |
| modern material-to-image uncapped measured channel siblings | 1 | 1 | 56 | 145,430,530 | 2,596,973 | 2,596,973 | 2,596,973 | 2026-10-08 | 2026-10-08 | untried |
| xhash external core respelling | 1 | 2 | 15 | 39,142,720 | 2,609,514 | 2,446,420 | 2,446,420 | 2026-08-28 | 2026-08-28 | live |
| seeded sound-alias token edits | 1 | 1 | 2 | 5,339,594 | 2,669,797 | 2,669,797 | 2,669,797 | 2026-09-05 | 2026-09-05 | untried |
| interior token duplication | 1 | 2 | 4 | 10,737,038 | 2,684,259 | 2,684,259 | 2,684,259 | 2026-08-27 | 2026-08-27 | live |
| yamyamok verified material heads with target-held conventions | 1 | 1 | 797 | 2,143,308,000 | 2,689,219 | 2,689,219 | 2,689,219 | 2026-10-09 | 2026-10-09 | untried |
| character deletion and transposition | 1 | 2 | 50 | 134,487,400 | 2,689,748 | 1,601,046 | 1,601,046 | 2026-08-24 | 2026-08-24 | live |
| model token insertion and deletion after pr987 | 1 | 1 | 5 | 13,695,779 | 2,739,155 | 2,739,155 | 2,739,155 | 2026-08-27 | 2026-08-27 | untried |
| context swap r2 | 2 | 2 | 100 | 284,726,994 | 2,847,269 | 2,072,345 | 2,072,345 | 2026-10-09 | 2026-10-09 | live |
| twck 4-token names: prepended token + known 3-token name | 1 | 1 | 1 | 2,860,429 | 2,860,429 | 2,860,429 | 2,860,429 | 2026-10-09 | 2026-10-09 | untried |
| \ cold war rare shared-token splice family 2401-2700 material\ | 1 | 1 | 3 | 8,787,217 | 2,929,072 | 2,929,072 | 2,929,072 | 2026-08-28 | 2026-08-28 | untried |
| title prefix swap + sound tail swap | 2 | 2 | 47 | 138,148,804 | 2,939,336 | 1,644,628 | 1,644,628 | 2026-10-09 | 2026-10-09 | live |
| image family grid round 1, head 3 | 3 | 3 | 5 | 14,753,982 | 2,950,796 | 2,458,997 | 2,458,997 | 2026-10-09 | 2026-10-09 | live |
| twc 3-token names: known 2-token name + appended token | 1 | 2 | 1,517 | 4,477,431,244 | 2,951,503 | 1,768,337 | 8,919,185 | 2026-10-09 | 2026-10-09 | cooling |
| \ cold war material token edits refreshed 20260830\ | 1 | 1 | 11 | 32,738,853 | 2,976,259 | 2,976,259 | 2,976,259 | 2026-08-29 | 2026-08-29 | untried |
| \ cold war rare shared-token splice family 3001-3300 material\ | 1 | 1 | 2 | 5,966,595 | 2,983,297 | 2,983,297 | 2,983,297 | 2026-08-28 | 2026-08-28 | untried |
| token order transpositions | 1 | 2 | 3 | 8,952,148 | 2,984,049 | 2,238,036 | 4,476,076 | 2026-08-24 | 2026-08-24 | live |
| token edits anim current | 1 | 2 | 2 | 6,031,597 | 3,015,798 | 2,980,123 | 3,051,474 | 2026-08-29 | 2026-09-02 | live |
| cold war animation token edits current | 1 | 1 | 1 | 3,041,844 | 3,041,844 | 3,041,844 | 3,041,844 | 2026-09-01 | 2026-09-01 | untried |
| rare shared-token splices family size 1201-1500 | 1 | 2 | 17 | 51,936,301 | 3,055,076 | 2,596,884 | 2,596,884 | 2026-08-28 | 2026-08-28 | live |
| \ cw same-directory sibling token graft\ | 1 | 1 | 1 | 3,063,893 | 3,063,893 | 3,063,893 | 3,063,893 | 2026-08-29 | 2026-08-29 | untried |
| family column cross product (community method 11) on the enlarged corpus | 1 | 1 | 18 | 56,352,518 | 3,130,695 | 3,130,695 | 3,130,695 | 2026-09-14 | 2026-09-14 | untried |
| image segment plan | 1 | 12 | 8,610 | 26,994,573,306 | 3,135,258 | 177,699 | 55,866,877 | 2026-10-08 | 2026-10-08 | spent |
| slot swap image wide | 1 | 1 | 19 | 61,138,470 | 3,217,814 | 3,217,814 | 3,217,814 | 2026-10-09 | 2026-10-09 | untried |
| pooled context swap image r1 | 1 | 1 | 16 | 51,939,109 | 3,246,194 | 3,246,194 | 3,246,194 | 2026-10-09 | 2026-10-09 | untried |
| material all-boundary segment plan | 1 | 2 | 1,672 | 5,440,267,836 | 3,253,748 | 3,137,409 | 3,137,409 | 2026-10-08 | 2026-10-08 | live |
| family grid completion: head x axis x tail, unseen cells | 1 | 1 | 15 | 50,326,771 | 3,355,118 | 3,355,118 | 3,355,118 | 2026-08-23 | 2026-08-23 | untried |
| pooled insert-delete xanim r1 | 1 | 1 | 6 | 20,272,459 | 3,378,743 | 3,378,743 | 3,378,743 | 2026-10-10 | 2026-10-10 | untried |
| token edits anim cap30 | 1 | 2 | 4 | 13,523,498 | 3,380,874 | 3,380,865 | 3,380,883 | 2026-09-03 | 2026-09-03 | live |
| material head swap | 1 | 4 | 2,459 | 8,343,111,990 | 3,392,888 | 1,718,907 | 10,562,770 | 2026-10-08 | 2026-10-08 | cooling |
| twcj 4-token names: prepended token + known 3-token name | 1 | 1 | 1 | 3,400,510 | 3,400,510 | 3,400,510 | 3,400,510 | 2026-10-09 | 2026-10-09 | untried |
| blackop7 evidence-family image numeric stem triples | 1 | 1 | 3 | 10,210,200 | 3,403,400 | 3,403,400 | 3,403,400 | 2026-10-09 | 2026-10-09 | untried |
| rare shared-token splices families 33901-34000 | 1 | 1 | 29 | 100,204,390 | 3,455,323 | 3,455,323 | 3,455,323 | 2026-08-29 | 2026-08-29 | untried |
| cold war amb sound family | 1 | 1 | 2 | 6,956,252 | 3,478,126 | 3,478,126 | 3,478,126 | 2026-08-30 | 2026-08-30 | untried |
| all-boundary refresh 2026-09-29, new cores x all endings | 1 | 2 | 200 | 696,002,320 | 3,480,011 | 2,161,497 | 8,923,106 | 2026-09-29 | 2026-09-29 | cooling |
| images for every material prefix x its family's measured endings | 1 | 2 | 6 | 21,021,375 | 3,503,562 | 3,037,059 | 3,037,059 | 2026-10-06 | 2026-10-06 | live |
| rare shared-token splices families 15901-16200 | 1 | 1 | 8 | 28,031,004 | 3,503,875 | 3,503,875 | 3,503,875 | 2026-08-28 | 2026-08-28 | untried |
| slot swap width 1 r1 | 1 | 1 | 28 | 98,475,858 | 3,516,994 | 3,516,994 | 3,516,994 | 2026-10-09 | 2026-10-09 | untried |
| slot swap from end w1+w2 r2 | 1 | 1 | 69 | 243,612,848 | 3,530,620 | 3,530,620 | 3,530,620 | 2026-10-09 | 2026-10-09 | untried |
| cold war image token edits | 2 | 2 | 18 | 64,416,665 | 3,578,703 | 2,662,730 | 5,410,649 | 2026-08-26 | 2026-08-31 | live |
| open-slot english words | 2 | 3 | 182 | 654,499,979 | 3,596,153 | 14,997 | 14,997 | 2026-10-01 | 2026-10-05 | live |
| context insert-delete material r2 | 1 | 1 | 19 | 68,961,085 | 3,629,530 | 3,629,530 | 3,629,530 | 2026-10-09 | 2026-10-09 | untried |
| asset adjacent transpose bo4 | 1 | 1 | 10 | 36,296,871 | 3,629,687 | 3,629,687 | 3,629,687 | 2026-09-09 | 2026-09-09 | untried |
| modwar7 source-verified sound-file tails | 1 | 1 | 235 | 857,634,355 | 3,649,507 | 3,649,507 | 3,649,507 | 2026-10-09 | 2026-10-09 | untried |
| bounded family column cross product | 1 | 1 | 3 | 10,956,657 | 3,652,219 | 3,652,219 | 3,652,219 | 2026-08-27 | 2026-08-27 | untried |
| modern image channel completion, quick-wins r1 | 4 | 4 | 9 | 32,941,124 | 3,660,124 | 2,058,820 | 2,745,093 | 2026-10-09 | 2026-10-09 | live |
| wide materials from images | 1 | 1 | 1 | 3,699,887 | 3,699,887 | 3,699,887 | 3,699,887 | 2026-09-02 | 2026-09-02 | untried |
| mined substitutions with left context | 1 | 1 | 29 | 108,352,260 | 3,736,284 | 3,736,284 | 3,736,284 | 2026-08-25 | 2026-08-25 | untried |
| token edits alias cap30 | 1 | 1 | 3 | 11,246,872 | 3,748,957 | 3,748,957 | 3,748,957 | 2026-09-03 | 2026-09-03 | untried |
| precedents top60 | 1 | 1 | 19 | 71,618,728 | 3,769,406 | 3,769,406 | 3,769,406 | 2026-09-02 | 2026-09-02 | untried |
| character substitution cw | 1 | 1 | 333 | 1,256,444,745 | 3,773,107 | 3,773,107 | 3,773,107 | 2026-08-24 | 2026-08-24 | untried |
| \ bo4 material token edits cap30 minseen3 20260830\ | 1 | 1 | 21 | 79,628,070 | 3,791,812 | 3,791,812 | 3,791,812 | 2026-08-29 | 2026-08-29 | untried |
| context indel r2 | 2 | 3 | 49 | 185,977,642 | 3,795,462 | 1,689,012 | 7,733,235 | 2026-10-09 | 2026-10-10 | cooling |
| black ops 4 per-suffix precedents, five-token mirror | 1 | 2 | 159 | 603,737,878 | 3,797,093 | 2,251,087 | 12,083,685 | 2026-08-26 | 2026-08-26 | cooling |
| rare shared-token splices family sizes 5101-5400 | 1 | 2 | 6 | 22,972,418 | 3,828,736 | 2,871,552 | 2,871,552 | 2026-08-28 | 2026-08-28 | live |
| slot swap material wide | 1 | 1 | 24 | 92,906,594 | 3,871,108 | 3,871,108 | 3,871,108 | 2026-10-09 | 2026-10-09 | untried |
| slot swap material r2 | 2 | 2 | 21 | 81,314,561 | 3,872,121 | 2,357,536 | 10,309,108 | 2026-10-09 | 2026-10-09 | cooling |
| alias one token current | 1 | 1 | 1 | 3,881,516 | 3,881,516 | 3,881,516 | 3,881,516 | 2026-09-02 | 2026-09-02 | untried |
| sound-alias token substitutions | 1 | 1 | 1 | 3,935,920 | 3,935,920 | 3,935,920 | 3,935,920 | 2026-09-05 | 2026-09-05 | untried |
| \ bo4 rare shared-token splice family 3301-3600 material\ | 1 | 1 | 2 | 7,888,925 | 3,944,462 | 3,944,462 | 3,944,462 | 2026-08-28 | 2026-08-28 | untried |
| sibling token substitution (community method 10) on the enlarged corpus | 1 | 1 | 44 | 175,553,749 | 3,989,857 | 3,989,857 | 3,989,857 | 2026-09-14 | 2026-09-14 | untried |
| weapon foley, every weapon x every animation/foley event x take numbers | 1 | 17 | 65,796 | 264,195,219,709 | 4,015,369 | 1,876,017 | 5,146,062 | 2026-10-09 | 2026-10-09 | live |
| material token insertion and deletion after pr983 | 1 | 1 | 8 | 32,496,827 | 4,062,103 | 4,062,103 | 4,062,103 | 2026-08-27 | 2026-08-27 | untried |
| slot swap xanim closure | 1 | 1 | 1 | 4,064,766 | 4,064,766 | 4,064,766 | 4,064,766 | 2026-10-09 | 2026-10-09 | untried |
| cold war sound stems, black ops 4 spelling | 1 | 1 | 3 | 12,257,370 | 4,085,790 | 4,085,790 | 4,085,790 | 2026-08-21 | 2026-08-21 | untried |
| per-suffix precedents, five-token mirror | 1 | 1 | 73 | 301,603,209 | 4,131,550 | 4,131,550 | 4,131,550 | 2026-08-26 | 2026-08-26 | untried |
| ab snowball r4 sound: new cores x all endings | 1 | 1 | 3 | 12,500,125 | 4,166,708 | 4,166,708 | 4,166,708 | 2026-10-01 | 2026-10-01 | untried |
| slot swap sound alias r3 | 1 | 1 | 1 | 4,235,721 | 4,235,721 | 4,235,721 | 4,235,721 | 2026-10-09 | 2026-10-09 | untried |
| total corpus sweep, all pools | 1 | 1 | 26 | 110,823,650 | 4,262,448 | 4,262,448 | 4,262,448 | 2026-09-05 | 2026-09-05 | untried |
| dotted sound files: slot swap both ends, family grid, codename swap r2 | 1 | 1 | 30 | 128,682,376 | 4,289,412 | 4,289,412 | 4,289,412 | 2026-10-09 | 2026-10-09 | untried |
| \ cold war rare shared-token splice family 2701-3000 material\ | 1 | 1 | 2 | 8,580,309 | 4,290,154 | 4,290,154 | 4,290,154 | 2026-08-28 | 2026-08-28 | untried |
| confirmed-only sound all-boundary cores, refreshed | 1 | 2 | 47 | 202,544,928 | 4,309,466 | 2,596,729 | 2,596,729 | 2026-08-29 | 2026-08-29 | live |
| context insert-delete sound asset r1 | 1 | 1 | 1 | 4,313,967 | 4,313,967 | 4,313,967 | 4,313,967 | 2026-10-09 | 2026-10-09 | untried |
| slot swap wide, aliases/anims/sounds | 2 | 2 | 49 | 215,202,976 | 4,391,897 | 2,339,162 | 2,339,162 | 2026-10-09 | 2026-10-09 | live |
| edits model | 2 | 4 | 12 | 52,757,566 | 4,396,463 | 1,876,636 | 6,607,769 | 2026-08-20 | 2026-08-20 | cooling |
| execution quips, deep chained phrases on one speaker | 1 | 1 | 6 | 26,713,251 | 4,452,208 | 4,452,208 | 4,452,208 | 2026-10-05 | 2026-10-05 | untried |
| packed twc/tw codes, first slot of every 4+ slot code swapped | 1 | 4 | 815 | 3,649,583,608 | 4,478,016 | 1,490,987 | 190,214,572 | 2026-10-09 | 2026-10-09 | spent |
| mw4-sound-file-context | 1 | 1 | 5 | 22,594,207 | 4,518,841 | 4,518,841 | 4,518,841 | 2026-10-09 | 2026-10-09 | untried |
| open-slot embedding neighbours | 1 | 2 | 44 | 199,716,612 | 4,539,013 | 3,633,293 | 3,633,293 | 2026-10-01 | 2026-10-01 | live |
| context swap w2 image r2 | 1 | 1 | 12 | 54,499,222 | 4,541,601 | 4,541,601 | 4,541,601 | 2026-10-10 | 2026-10-10 | untried |
| rare shared-token splices families 12901-13200 | 1 | 2 | 6 | 27,286,700 | 4,547,783 | 3,410,837 | 3,410,837 | 2026-08-28 | 2026-08-28 | live |
| slot swap from end w2 sound asset r1 | 1 | 1 | 7 | 32,377,016 | 4,625,288 | 4,625,288 | 4,625,288 | 2026-10-09 | 2026-10-09 | untried |
| material family grid h3 r1 | 1 | 1 | 2 | 9,252,725 | 4,626,362 | 4,626,362 | 4,626,362 | 2026-10-09 | 2026-10-09 | untried |
| context swap sound alias r2 | 2 | 2 | 5 | 23,432,376 | 4,686,475 | 3,976,078 | 7,528,062 | 2026-10-09 | 2026-10-10 | live |
| rare shared-token splices family sizes 6001-6300 | 1 | 2 | 3 | 14,089,319 | 4,696,439 | 3,522,329 | 3,522,329 | 2026-08-28 | 2026-08-28 | live |
| \ bo4 rare shared-token splice family 3601-3900 material\ | 1 | 1 | 1 | 4,744,803 | 4,744,803 | 4,744,803 | 4,744,803 | 2026-08-28 | 2026-08-28 | untried |
| token edits alias | 1 | 2 | 2 | 9,502,376 | 4,751,188 | 4,751,138 | 4,751,238 | 2026-09-03 | 2026-09-03 | live |
| wide image siblings of confirmed materials | 1 | 4 | 102 | 486,499,036 | 4,769,598 | 2,190,637 | 8,718,020 | 2026-09-02 | 2026-09-08 | cooling |
| rare shared-token splices family sizes 7201-7500 | 1 | 2 | 6 | 28,650,319 | 4,775,053 | 2,865,031 | 2,865,031 | 2026-08-28 | 2026-08-28 | live |
| context swap image r3 | 1 | 1 | 8 | 38,413,304 | 4,801,663 | 4,801,663 | 4,801,663 | 2026-10-09 | 2026-10-09 | untried |
| cold war materials from image cores current | 1 | 1 | 1 | 4,838,880 | 4,838,880 | 4,838,880 | 4,838,880 | 2026-09-01 | 2026-09-01 | untried |
| materials from images after gain | 1 | 1 | 1 | 4,846,608 | 4,846,608 | 4,846,608 | 4,846,608 | 2026-09-02 | 2026-09-02 | untried |
| black ops 4 material token insertions and deletions cap16 minseen5 | 1 | 1 | 9 | 44,036,727 | 4,892,969 | 4,892,969 | 4,892,969 | 2026-09-08 | 2026-09-08 | untried |
| sound-file family grid restart | 1 | 1 | 1 | 4,913,956 | 4,913,956 | 4,913,956 | 4,913,956 | 2026-10-09 | 2026-10-09 | untried |
| image family grid snowball r1 h3 | 1 | 1 | 1 | 4,930,209 | 4,930,209 | 4,930,209 | 4,930,209 | 2026-10-09 | 2026-10-09 | untried |
| alias heads x shared tails, every game's aliases | 1 | 24 | 22,569 | 112,940,852,051 | 5,004,247 | 613,483 | 23,754,470 | 2026-10-09 | 2026-10-09 | spent |
| xmodel cores spelled as material | 4 | 9 | 110 | 551,720,250 | 5,015,638 | 1,297,902 | 49,307,187 | 2026-08-28 | 2026-09-03 | spent |
| slot swap from end w2 xanim r1 | 1 | 1 | 3 | 15,090,249 | 5,030,083 | 5,030,083 | 5,030,083 | 2026-10-09 | 2026-10-09 | untried |
| word pairs into one-word slots | 1 | 3 | 114 | 574,760,000 | 5,041,754 | 4,713,809 | 4,713,809 | 2026-10-01 | 2026-10-01 | live |
| precedents top40 | 1 | 1 | 10 | 51,576,111 | 5,157,611 | 5,157,611 | 5,157,611 | 2026-09-02 | 2026-09-02 | untried |
| alias heads x single-attested short tails (support 1, <=2 tokens), every game | 1 | 10 | 7,104 | 36,824,508,840 | 5,183,630 | 1,158,049 | 162,612,810 | 2026-10-09 | 2026-10-09 | spent |
| context swap image r2 | 2 | 2 | 12 | 62,237,165 | 5,186,430 | 3,429,941 | 3,429,941 | 2026-10-09 | 2026-10-10 | live |
| rare shared-token splices family sizes 9001-9300 | 1 | 1 | 2 | 10,475,702 | 5,237,851 | 5,237,851 | 5,237,851 | 2026-08-28 | 2026-08-28 | untried |
| \ bo4 rare shared-token splice family 2401-2700 xmodel\ | 1 | 1 | 1 | 5,281,185 | 5,281,185 | 5,281,185 | 5,281,185 | 2026-08-28 | 2026-08-28 | untried |
| \ cold war material token edits cap40 minseen2 20260830\ | 1 | 1 | 20 | 105,800,678 | 5,290,033 | 5,290,033 | 5,290,033 | 2026-08-29 | 2026-08-29 | untried |
| token edits image after new findings | 1 | 1 | 6 | 31,740,887 | 5,290,147 | 5,290,147 | 5,290,147 | 2026-08-25 | 2026-08-25 | untried |
| context swap sound alias r3 | 1 | 1 | 3 | 15,978,913 | 5,326,304 | 5,326,304 | 5,326,304 | 2026-10-09 | 2026-10-09 | untried |
| packed twc/tw codes, every known code with one more slot appended | 1 | 5 | 10,014 | 54,959,715,740 | 5,488,287 | 1,275,190 | 487,681,299 | 2026-10-09 | 2026-10-09 | spent |
| rare shared-token splices family sizes 6901-7200 | 1 | 1 | 1 | 5,494,443 | 5,494,443 | 5,494,443 | 5,494,443 | 2026-08-28 | 2026-08-28 | untried |
| cold war material token edits current | 1 | 1 | 6 | 33,028,500 | 5,504,750 | 5,504,750 | 5,504,750 | 2026-09-01 | 2026-09-01 | untried |
| token edits material current bo4 20260903 | 1 | 1 | 6 | 33,095,322 | 5,515,887 | 5,515,887 | 5,515,887 | 2026-09-03 | 2026-09-03 | untried |
| ab snowball r2 visual: new cores x all endings | 1 | 13 | 100 | 564,001,880 | 5,640,018 | 496,155 | 496,155 | 2026-09-29 | 2026-10-05 | live |
| twc terrain-blend grid, triples | 1 | 4 | 117,204 | 661,756,035,600 | 5,646,189 | 2,882,664 | 2,882,664 | 2026-10-08 | 2026-10-09 | live |
| weapon animations | 1 | 6 | 808 | 4,618,528,502 | 5,716,000 | 2,066,124 | 23,460,025 | 2026-10-09 | 2026-10-09 | spent |
| black ops 4 image token insertions and deletions cap8 minseen12 | 1 | 1 | 4 | 22,877,526 | 5,719,381 | 5,719,381 | 5,719,381 | 2026-09-08 | 2026-09-08 | untried |
| corpus-mined substitutions, top 500 | 1 | 5 | 21 | 121,661,444 | 5,793,402 | 2,714,810 | 24,268,543 | 2026-08-27 | 2026-08-27 | cooling |
| rare shared-token splices family sizes 5401-5700 | 1 | 1 | 1 | 5,806,329 | 5,806,329 | 5,806,329 | 5,806,329 | 2026-08-28 | 2026-08-28 | untried |
| context swap w2 sound asset r2 | 1 | 1 | 8 | 46,549,572 | 5,818,696 | 5,818,696 | 5,818,696 | 2026-10-10 | 2026-10-10 | untried |
| \ bo4 rare shared-token splice family 3001-3300 material\ | 1 | 1 | 1 | 5,966,596 | 5,966,596 | 5,966,596 | 5,966,596 | 2026-08-28 | 2026-08-28 | untried |
| corpus-mined substitutions, top 1000 | 1 | 4 | 24 | 145,853,160 | 6,077,215 | 4,050,931 | 18,234,083 | 2026-08-27 | 2026-08-27 | cooling |
| two-word slots, web bigrams ranked 100k+ | 1 | 1 | 178 | 1,083,632,880 | 6,087,825 | 6,087,825 | 6,087,825 | 2026-10-05 | 2026-10-05 | untried |
| context swap xanim r2 | 2 | 2 | 4 | 25,283,313 | 6,320,828 | 6,265,634 | 6,486,409 | 2026-10-09 | 2026-10-10 | live |
| ab snowball r2 sound: new cores x all endings | 1 | 8 | 56 | 354,903,549 | 6,337,563 | 650,006 | 7,400,074 | 2026-09-29 | 2026-10-05 | spent |
| context insert-delete sound alias r2 | 1 | 1 | 2 | 13,667,974 | 6,833,987 | 6,833,987 | 6,833,987 | 2026-10-09 | 2026-10-09 | untried |
| token insertion and deletion model | 1 | 2 | 4 | 27,607,752 | 6,901,938 | 4,608,579 | 4,608,579 | 2026-08-31 | 2026-09-07 | live |
| black ops 4 amb sound family | 1 | 1 | 1 | 6,962,026 | 6,962,026 | 6,962,026 | 6,962,026 | 2026-08-30 | 2026-08-30 | untried |
| slot swap w2 sound alias | 1 | 1 | 1 | 6,963,462 | 6,963,462 | 6,963,462 | 6,963,462 | 2026-10-09 | 2026-10-09 | untried |
| packed codes, last slot swapped | 1 | 6 | 1,200 | 8,357,322,316 | 6,964,435 | 1,387,559 | 199,833,646 | 2026-10-09 | 2026-10-09 | spent |
| rare shared-token splices family sizes 4501-4800 | 1 | 1 | 5 | 34,844,158 | 6,968,831 | 6,968,831 | 6,968,831 | 2026-08-28 | 2026-08-28 | untried |
| slot swap sound asset | 3 | 3 | 14 | 97,707,129 | 6,979,080 | 3,256,913 | 3,256,913 | 2026-10-09 | 2026-10-09 | live |
| rare shared token splice 241 480 current | 1 | 2 | 4 | 28,939,012 | 7,234,753 | 4,823,168 | 14,469,506 | 2026-09-02 | 2026-09-02 | live |
| token inflection | 1 | 2 | 4 | 29,077,611 | 7,269,402 | 4,238,059 | 4,238,059 | 2026-10-01 | 2026-10-01 | live |
| sab directory and basename recombination | 1 | 1 | 5 | 36,351,762 | 7,270,352 | 7,270,352 | 7,270,352 | 2026-08-21 | 2026-08-21 | untried |
| two-word slots, corpus word pairs | 1 | 2 | 82 | 604,915,290 | 7,377,015 | 6,670,340 | 6,670,340 | 2026-10-01 | 2026-10-01 | live |
| precedents top30 | 2 | 2 | 11 | 81,245,056 | 7,385,914 | 4,062,252 | 40,622,528 | 2026-09-02 | 2026-09-02 | cooling |
| rare shared-token splice families 481-960 | 1 | 1 | 5 | 37,321,382 | 7,464,276 | 7,464,276 | 7,464,276 | 2026-09-03 | 2026-09-03 | untried |
| rare shared token splice 961 1920 current | 1 | 2 | 19 | 142,465,412 | 7,498,179 | 7,123,270 | 7,914,745 | 2026-09-02 | 2026-09-02 | live |
| edits image | 2 | 3 | 12 | 91,292,882 | 7,607,740 | 5,048,388 | 30,538,103 | 2026-08-20 | 2026-08-20 | cooling |
| \ seeded sound-alias token edits\ | 1 | 1 | 1 | 7,651,395 | 7,651,395 | 7,651,395 | 7,651,395 | 2026-08-30 | 2026-08-30 | untried |
| context insert-delete material r4 | 1 | 1 | 9 | 69,561,614 | 7,729,068 | 7,729,068 | 7,729,068 | 2026-10-10 | 2026-10-10 | untried |
| tails of length 2, every table generation | 1 | 1 | 354 | 2,757,086,640 | 7,788,380 | 7,788,380 | 7,788,380 | 2026-10-09 | 2026-10-09 | untried |
| sound character deletion and transposition | 1 | 2 | 13 | 101,307,572 | 7,792,890 | 4,221,125 | 50,654,061 | 2026-08-24 | 2026-08-24 | spent |
| \ cold war rare shared-token splice family 3301-3600 material\ | 1 | 1 | 1 | 7,888,923 | 7,888,923 | 7,888,923 | 7,888,923 | 2026-08-28 | 2026-08-28 | untried |
| slot swap tail width 1 r1 | 1 | 1 | 18 | 144,412,829 | 8,022,934 | 8,022,934 | 8,022,934 | 2026-10-09 | 2026-10-09 | untried |
| open-slot words from wiki transcripts | 1 | 1 | 4 | 32,236,750 | 8,059,187 | 8,059,187 | 8,059,187 | 2026-10-07 | 2026-10-07 | untried |
| ab snowball r5 sound: new cores x all endings | 1 | 1 | 3 | 24,300,243 | 8,100,081 | 8,100,081 | 8,100,081 | 2026-10-01 | 2026-10-01 | untried |
| black ops 4 image token edits | 1 | 1 | 4 | 32,464,572 | 8,116,143 | 8,116,143 | 8,116,143 | 2026-08-31 | 2026-08-31 | untried |
| \ bo4 material token edits cap40 minseen2 20260830\ | 1 | 1 | 13 | 105,807,354 | 8,139,027 | 8,139,027 | 8,139,027 | 2026-08-29 | 2026-08-29 | untried |
| two-word slots, english web bigrams (count 2w) not in the corpus | 1 | 2 | 372 | 3,032,500,000 | 8,151,881 | 4,182,739 | 4,182,739 | 2026-10-05 | 2026-10-05 | live |
| \ bo4 material token edits refreshed 20260830\ | 1 | 1 | 4 | 32,739,897 | 8,184,974 | 8,184,974 | 8,184,974 | 2026-08-29 | 2026-08-29 | untried |
| slot swap from end w2 image r2 | 1 | 1 | 2 | 16,509,433 | 8,254,716 | 8,254,716 | 8,254,716 | 2026-10-10 | 2026-10-10 | untried |
| black ops 4, uncarried two-segment endings | 1 | 1 | 1,468 | 12,179,260,896 | 8,296,499 | 8,296,499 | 8,296,499 | 2026-08-23 | 2026-08-23 | untried |
| token-edits-material-bo4 | 1 | 1 | 4 | 33,296,040 | 8,324,010 | 8,324,010 | 8,324,010 | 2026-09-07 | 2026-09-07 | untried |
| image all-boundary segment plan | 1 | 2 | 485 | 4,099,809,798 | 8,453,216 | 6,405,952 | 12,423,666 | 2026-10-08 | 2026-10-08 | live |
| cold war suffix precedents top5 20260907 | 1 | 1 | 1 | 8,513,726 | 8,513,726 | 8,513,726 | 8,513,726 | 2026-09-07 | 2026-09-07 | untried |
| rare shared-token splices family sizes 6301-6600 | 1 | 2 | 6 | 51,290,334 | 8,548,389 | 5,129,036 | 5,129,036 | 2026-08-28 | 2026-08-28 | live |
| \ cold war material token edits cap50 minseen2 20260830\ | 1 | 1 | 15 | 131,595,356 | 8,773,023 | 8,773,023 | 8,773,023 | 2026-08-30 | 2026-08-30 | untried |
| context insert-delete image r2 | 1 | 1 | 5 | 44,645,959 | 8,929,191 | 8,929,191 | 8,929,191 | 2026-10-09 | 2026-10-09 | untried |
| packed material codes, two tokens | 1 | 1 | 25 | 225,030,000 | 9,001,200 | 9,001,200 | 9,001,200 | 2026-10-09 | 2026-10-09 | untried |
| slot swap tail width 2 alternation r1 | 1 | 1 | 11 | 99,117,518 | 9,010,683 | 9,010,683 | 9,010,683 | 2026-10-09 | 2026-10-09 | untried |
| slot swap w2 sound asset | 1 | 1 | 4 | 36,196,819 | 9,049,204 | 9,049,204 | 9,049,204 | 2026-10-09 | 2026-10-09 | untried |
| slot swap from end w2 material r4 | 1 | 1 | 3 | 27,219,889 | 9,073,296 | 9,073,296 | 9,073,296 | 2026-10-10 | 2026-10-10 | untried |
| tw-family terrain grids (tw twcj twck wc twj twk w), pairs over the full 0..9999 n/dn range | 1 | 2 | 614 | 5,600,280,000 | 9,120,977 | 6,481,805 | 15,385,384 | 2026-10-09 | 2026-10-09 | live |
| repeated-word sound templates x dictionary words | 1 | 1 | 12 | 109,874,835 | 9,156,236 | 9,156,236 | 9,156,236 | 2026-10-06 | 2026-10-06 | untried |
| modwar7 source-verified sound-file heads | 1 | 1 | 266 | 2,451,578,082 | 9,216,458 | 9,216,458 | 9,216,458 | 2026-10-09 | 2026-10-09 | untried |
| heads of length 2, every table generation | 1 | 1 | 359 | 3,357,015,624 | 9,351,018 | 9,351,018 | 9,351,018 | 2026-10-09 | 2026-10-09 | untried |
| material token insertion and deletion | 1 | 2 | 7 | 66,040,581 | 9,434,368 | 8,255,060 | 11,006,779 | 2026-09-02 | 2026-09-02 | live |
| slot swap from end w1 material r3 | 1 | 1 | 6 | 56,833,765 | 9,472,294 | 9,472,294 | 9,472,294 | 2026-10-10 | 2026-10-10 | untried |
| sound alias heads x tails shared by >= 2 heads | 1 | 5 | 3,430 | 32,728,260,723 | 9,541,766 | 7,139,210 | 9,601,470 | 2026-10-09 | 2026-10-10 | live |
| context swap sound asset r3 | 1 | 1 | 8 | 77,095,740 | 9,636,967 | 9,636,967 | 9,636,967 | 2026-10-09 | 2026-10-09 | untried |
| xanim head swap | 1 | 4 | 265 | 2,590,243,188 | 9,774,502 | 4,012,142 | 41,074,433 | 2026-10-08 | 2026-10-08 | spent |
| context swap w2 + pooled r2 | 1 | 1 | 62 | 613,367,919 | 9,893,030 | 9,893,030 | 9,893,030 | 2026-10-09 | 2026-10-09 | untried |
| slot swap tail width 2 r1 | 1 | 1 | 10 | 99,161,861 | 9,916,186 | 9,916,186 | 9,916,186 | 2026-10-09 | 2026-10-09 | untried |
| per-prefix-continuations-depth2-cap24 | 1 | 1 | 4 | 39,983,007 | 9,995,751 | 9,995,751 | 9,995,751 | 2026-08-20 | 2026-08-20 | untried |
| token trigram walk to 20000000, image | 1 | 1 | 2 | 20,000,000 | 10,000,000 | 10,000,000 | 10,000,000 | 2026-10-01 | 2026-10-01 | untried |
| sound-file segment plan | 1 | 3 | 563 | 5,652,374,992 | 10,039,742 | 4,453,420 | 4,453,420 | 2026-10-09 | 2026-10-09 | live |
| rare shared-token splices family sizes 4201-4500 | 1 | 1 | 1 | 10,130,357 | 10,130,357 | 10,130,357 | 10,130,357 | 2026-08-28 | 2026-08-28 | untried |
| any english word in any known name -> its 40 glove neighbours | 1 | 2 | 13 | 133,284,028 | 10,252,617 | 4,899,895 | 4,899,895 | 2026-10-01 | 2026-10-01 | live |
| slot swap from end w1 xanim r2 | 1 | 1 | 2 | 20,606,619 | 10,303,309 | 10,303,309 | 10,303,309 | 2026-10-10 | 2026-10-10 | untried |
| redecoration batch 1 | 1 | 1 | 1 | 10,501,282 | 10,501,282 | 10,501,282 | 10,501,282 | 2026-09-20 | 2026-09-20 | untried |
| \ bo4 rare shared-token splice family 2101-2400\ | 1 | 1 | 2 | 21,030,543 | 10,515,271 | 10,515,271 | 10,515,271 | 2026-08-28 | 2026-08-28 | untried |
| image token insertion and deletion | 1 | 2 | 6 | 64,948,181 | 10,824,696 | 8,118,449 | 16,237,192 | 2026-09-02 | 2026-09-02 | live |
| context swap sound asset r1 | 1 | 1 | 7 | 77,003,327 | 11,000,475 | 11,000,475 | 11,000,475 | 2026-10-09 | 2026-10-09 | untried |
| cold war material token insertions and deletions cap16 minseen5 | 1 | 1 | 4 | 44,036,035 | 11,009,008 | 11,009,008 | 11,009,008 | 2026-09-08 | 2026-09-08 | untried |
| token edits material current cw 20260903 | 1 | 1 | 3 | 33,095,190 | 11,031,730 | 11,031,730 | 11,031,730 | 2026-09-03 | 2026-09-03 | untried |
| token edits material | 1 | 1 | 3 | 33,118,937 | 11,039,645 | 11,039,645 | 11,039,645 | 2026-09-03 | 2026-09-03 | untried |
| weapon-slot plan for newly found bo7 weapons | 1 | 1 | 6 | 68,337,384 | 11,389,564 | 11,389,564 | 11,389,564 | 2026-10-09 | 2026-10-09 | untried |
| precedents top20 | 2 | 2 | 5 | 57,508,152 | 11,501,630 | 7,188,519 | 7,188,519 | 2026-09-02 | 2026-09-02 | live |
| execution quips, topic + function word triples, one speaker | 1 | 1 | 9 | 107,850,176 | 11,983,352 | 11,983,352 | 11,983,352 | 2026-10-06 | 2026-10-06 | untried |
| pooled insert-delete sound alias r2 | 1 | 1 | 2 | 23,981,477 | 11,990,738 | 11,990,738 | 11,990,738 | 2026-10-10 | 2026-10-10 | untried |
| cold war uncarried four-segment endings current | 1 | 1 | 5 | 60,407,129 | 12,081,425 | 12,081,425 | 12,081,425 | 2026-08-31 | 2026-08-31 | untried |
| \ cold war material token edits cap60 minseen1 20260830\ | 1 | 1 | 13 | 158,177,067 | 12,167,466 | 12,167,466 | 12,167,466 | 2026-08-30 | 2026-08-30 | untried |
| operator voice-line grid, two-letter-codec lines included | 1 | 1 | 1 | 12,215,323 | 12,215,323 | 12,215,323 | 12,215,323 | 2026-10-08 | 2026-10-08 | untried |
| pooled insert-delete sound asset r1 | 1 | 1 | 2 | 25,236,476 | 12,618,238 | 12,618,238 | 12,618,238 | 2026-10-10 | 2026-10-10 | untried |
| execution quips, glove-topic word pairs (8000 words) on one speaker | 1 | 1 | 5 | 64,432,729 | 12,886,545 | 12,886,545 | 12,886,545 | 2026-10-05 | 2026-10-05 | untried |
| token insertion deletion material cap24 | 1 | 1 | 5 | 64,526,533 | 12,905,306 | 12,905,306 | 12,905,306 | 2026-09-09 | 2026-09-09 | untried |
| sibling token substitution right context current | 1 | 1 | 23 | 296,853,548 | 12,906,676 | 12,906,676 | 12,906,676 | 2026-08-25 | 2026-08-25 | untried |
| two-word slots, corpus pairs ranked 20k-120k | 1 | 2 | 232 | 3,025,489,975 | 13,040,905 | 11,815,842 | 11,815,842 | 2026-10-01 | 2026-10-01 | live |
| slot swap material closure | 1 | 1 | 3 | 40,111,997 | 13,370,665 | 13,370,665 | 13,370,665 | 2026-10-09 | 2026-10-09 | untried |
| ab snowball r3 sound: new cores x all endings | 1 | 6 | 45 | 606,906,069 | 13,486,801 | 140,001 | 28,644,036 | 2026-09-29 | 2026-10-05 | spent |
| sibling token substitution, re-run on grown corpus | 1 | 1 | 12 | 162,810,506 | 13,567,542 | 13,567,542 | 13,567,542 | 2026-09-08 | 2026-09-08 | untried |
| slot swap from end w2 material r3 | 1 | 1 | 2 | 27,210,358 | 13,605,179 | 13,605,179 | 13,605,179 | 2026-10-10 | 2026-10-10 | untried |
| token edits model current | 1 | 2 | 2 | 27,434,480 | 13,717,240 | 13,717,240 | 13,717,240 | 2026-08-29 | 2026-08-29 | live |
| token edits model | 1 | 1 | 1 | 13,801,977 | 13,801,977 | 13,801,977 | 13,801,977 | 2026-09-03 | 2026-09-03 | untried |
| long image channels on every material and image core | 1 | 4 | 362 | 5,029,969,973 | 13,894,944 | 704,827 | 534,375,054 | 2026-10-09 | 2026-10-09 | spent |
| \ bo4 material token edits cap70 minseen1 20260830\ | 1 | 1 | 13 | 184,040,349 | 14,156,949 | 14,156,949 | 14,156,949 | 2026-08-30 | 2026-08-30 | untried |
| packed codes, first slot swapped | 1 | 5 | 1,001 | 14,236,915,626 | 14,222,692 | 5,278,779 | 81,681,224 | 2026-10-09 | 2026-10-09 | spent |
| rare shared-token splice families 241-480 | 1 | 2 | 2 | 29,082,266 | 14,541,133 | 14,541,133 | 14,541,133 | 2026-09-03 | 2026-09-03 | live |
| \ bo4 material token edits cap50 minseen2 20260830\ | 1 | 1 | 9 | 131,591,450 | 14,621,272 | 14,621,272 | 14,621,272 | 2026-08-30 | 2026-08-30 | untried |
| sibling token substitution left context current | 1 | 1 | 23 | 337,560,590 | 14,676,547 | 14,676,547 | 14,676,547 | 2026-08-25 | 2026-08-25 | untried |
| open-slot words from the newer titles' vocabulary | 1 | 2 | 26 | 383,975,898 | 14,768,303 | 14,569,377 | 15,000,384 | 2026-10-01 | 2026-10-01 | live |
| hot word frames, whole vocabulary | 1 | 2 | 95 | 1,411,929,833 | 14,862,419 | 11,567,053 | 11,567,053 | 2026-10-01 | 2026-10-01 | live |
| open-slot words from the corpus's own non-dictionary vocabulary | 1 | 2 | 27 | 407,981,080 | 15,110,410 | 10,067,207 | 10,067,207 | 2026-10-01 | 2026-10-01 | live |
| execution quips, topic word x common word, one speaker | 1 | 1 | 12 | 183,360,000 | 15,280,000 | 15,280,000 | 15,280,000 | 2026-10-06 | 2026-10-06 | untried |
| ab snowball r1 sound: new cores x all endings | 1 | 9 | 100 | 1,548,115,481 | 15,481,154 | 900,009 | 31,083,644 | 2026-09-29 | 2026-10-06 | spent |
| character substitution | 1 | 1 | 81 | 1,256,307,739 | 15,509,972 | 15,509,972 | 15,509,972 | 2026-08-24 | 2026-08-24 | untried |
| any english word -> its 150 glove neighbours | 1 | 1 | 14 | 220,319,664 | 15,737,118 | 15,737,118 | 15,737,118 | 2026-10-01 | 2026-10-01 | untried |
| black ops 4 material token edits after new findings | 1 | 1 | 2 | 33,006,487 | 16,503,243 | 16,503,243 | 16,503,243 | 2026-08-31 | 2026-08-31 | untried |
| hot word frames, whole vocabulary, round 4 | 1 | 1 | 22 | 364,381,339 | 16,562,788 | 16,562,788 | 16,562,788 | 2026-10-01 | 2026-10-01 | untried |
| token insertion deletion material | 1 | 2 | 4 | 66,752,055 | 16,688,013 | 16,687,998 | 16,688,029 | 2026-09-09 | 2026-09-09 | live |
| tw 4-token names: known 3-token name + appended token | 1 | 1 | 2 | 34,165,124 | 17,082,562 | 17,082,562 | 17,082,562 | 2026-10-09 | 2026-10-09 | untried |
| tw 4-token names: prepended token + known 3-token name | 1 | 1 | 2 | 34,165,124 | 17,082,562 | 17,082,562 | 17,082,562 | 2026-10-09 | 2026-10-09 | untried |
| slot swap width 2 r1 | 1 | 1 | 8 | 137,658,008 | 17,207,251 | 17,207,251 | 17,207,251 | 2026-10-09 | 2026-10-09 | untried |
| material cores spelled as xmodel | 4 | 9 | 48 | 838,814,750 | 17,475,307 | 90,750 | 28,702,083 | 2026-08-28 | 2026-09-03 | spent |
| suffix precedents current | 2 | 2 | 35 | 622,623,642 | 17,789,246 | 10,042,077 | 77,829,809 | 2026-09-02 | 2026-09-02 | cooling |
| rare shared-token splices family sizes 11701-12000 | 1 | 1 | 1 | 17,801,434 | 17,801,434 | 17,801,434 | 17,801,434 | 2026-08-28 | 2026-08-28 | untried |
| ab snowball r2 sound: all cores x new endings | 1 | 1 | 1 | 17,844,687 | 17,844,687 | 17,844,687 | 17,844,687 | 2026-09-29 | 2026-09-29 | untried |
| numbers in place r2 | 1 | 1 | 46 | 836,944,623 | 18,194,448 | 18,194,448 | 18,194,448 | 2026-10-09 | 2026-10-09 | untried |
| sound directory swap | 1 | 2 | 2,952 | 53,787,854,680 | 18,220,817 | 14,891,432 | 14,891,432 | 2026-10-08 | 2026-10-08 | live |
| corpus-mined substitutions, top 300 | 1 | 4 | 6 | 109,732,535 | 18,288,755 | 13,715,940 | 27,434,695 | 2026-08-27 | 2026-08-27 | live |
| blackop7 fresh verified image beginnings under frozen complete pairs | 1 | 2 | 301 | 5,507,822,187 | 18,298,412 | 16,616,880 | 16,616,880 | 2026-10-09 | 2026-10-09 | live |
| suffix-chain completion | 2 | 2 | 10 | 187,289,550 | 18,728,955 | 10,404,975 | 10,404,975 | 2026-09-01 | 2026-09-01 | live |
| modern image-to-material uncapped measured directory siblings | 1 | 1 | 37 | 694,835,592 | 18,779,340 | 18,779,340 | 18,779,340 | 2026-10-08 | 2026-10-08 | untried |
| character insertion | 1 | 2 | 135 | 2,577,959,172 | 19,095,993 | 16,740,545 | 16,740,545 | 2026-08-24 | 2026-08-24 | live |
| ab snowball r1 visual: all cores x new endings | 1 | 9 | 46 | 901,101,864 | 19,589,170 | 6,619,910 | 95,017,300 | 2026-09-30 | 2026-10-06 | spent |
| voice phrase grids, probe with 3.07m phrases on two speakers per category | 1 | 1 | 18 | 355,930,140 | 19,773,896 | 19,773,896 | 19,773,896 | 2026-10-05 | 2026-10-05 | untried |
| token edits mat cap30 | 1 | 1 | 4 | 79,362,695 | 19,840,673 | 19,840,673 | 19,840,673 | 2026-09-03 | 2026-09-03 | untried |
| token trigram walk to 20000000, xmodel | 1 | 1 | 1 | 20,000,000 | 20,000,000 | 20,000,000 | 20,000,000 | 2026-10-01 | 2026-10-01 | untried |
| sound character substitution cw | 1 | 1 | 49 | 983,905,838 | 20,079,710 | 20,079,710 | 20,079,710 | 2026-08-24 | 2026-08-24 | untried |
| ab snowball r3 visual: new cores x all endings | 1 | 8 | 58 | 1,166,703,889 | 20,115,584 | 675,002 | 391,501,305 | 2026-09-29 | 2026-10-05 | spent |
| materials from image cores, image prefix and channel both stripped | 1 | 2 | 191 | 3,851,877,680 | 20,166,898 | 17,508,534 | 23,777,022 | 2026-10-09 | 2026-10-09 | live |
| weapon-slot plan | 1 | 4 | 1,764 | 35,624,312,292 | 20,195,188 | 13,620,660 | 31,691,799 | 2026-10-09 | 2026-10-09 | live |
| cold war, uncarried two-segment endings | 1 | 1 | 597 | 12,179,260,896 | 20,400,772 | 20,400,772 | 20,400,772 | 2026-08-23 | 2026-08-23 | untried |
| context swap material r4 | 1 | 1 | 1 | 20,534,631 | 20,534,631 | 20,534,631 | 20,534,631 | 2026-10-10 | 2026-10-10 | untried |
| context indel material r3 | 1 | 1 | 1 | 20,808,723 | 20,808,723 | 20,808,723 | 20,808,723 | 2026-10-10 | 2026-10-10 | untried |
| rare shared-token splices family size 1801-2100 | 1 | 2 | 2 | 43,513,608 | 21,756,804 | 21,756,771 | 21,756,837 | 2026-08-28 | 2026-08-28 | live |
| corpus-mined substitutions, deep cut | 1 | 1 | 2 | 43,582,606 | 21,791,303 | 21,791,303 | 21,791,303 | 2026-08-25 | 2026-08-25 | untried |
| \ per-suffix precedents bo4 20260830\ | 1 | 1 | 14 | 307,108,676 | 21,936,334 | 21,936,334 | 21,936,334 | 2026-08-30 | 2026-08-30 | untried |
| token edits img cap30 | 1 | 2 | 7 | 154,739,211 | 22,105,601 | 12,894,940 | 12,894,940 | 2026-09-03 | 2026-09-03 | live |
| black ops 4 sound, uncarried two-segment endings | 1 | 1 | 509 | 11,274,140,892 | 22,149,589 | 22,149,589 | 22,149,589 | 2026-08-23 | 2026-08-23 | untried |
| image cores spelled as material | 2 | 3 | 10 | 221,738,750 | 22,173,875 | 14,270,250 | 39,518,125 | 2026-08-28 | 2026-08-28 | live |
| compound word slots | 1 | 2 | 55 | 1,224,585,138 | 22,265,184 | 12,364,146 | 12,364,146 | 2026-10-01 | 2026-10-01 | live |
| char edits current | 1 | 1 | 3 | 68,250,824 | 22,750,274 | 22,750,274 | 22,750,274 | 2026-08-29 | 2026-08-29 | untried |
| confirmed-only all-boundary general cores x committed suffixes, 2026-09-20 | 1 | 2 | 36 | 819,098,610 | 22,752,739 | 11,701,408 | 11,701,408 | 2026-09-20 | 2026-09-20 | live |
| \\ cold war image token length stream\\ | 1 | 1 | 2 | 45,579,875 | 22,789,937 | 22,789,937 | 22,789,937 | 2026-08-29 | 2026-08-29 | untried |
| cold war image token insertions and deletions cap8 minseen12 | 1 | 1 | 1 | 22,877,777 | 22,877,777 | 22,877,777 | 22,877,777 | 2026-09-08 | 2026-09-08 | untried |
| yamyamok sound directories and tails with confirmed modern basenames | 1 | 1 | 1,106 | 26,529,272,280 | 23,986,683 | 23,986,683 | 23,986,683 | 2026-10-09 | 2026-10-09 | untried |
| image head swap | 1 | 4 | 456 | 11,005,506,000 | 24,134,881 | 12,495,151 | 89,639,032 | 2026-10-08 | 2026-10-08 | cooling |
| voice phrase grids, probed with wiki dialogue transcripts | 1 | 1 | 2 | 49,396,982 | 24,698,491 | 24,698,491 | 24,698,491 | 2026-10-07 | 2026-10-07 | untried |
| keyword sweep: zombie models | 1 | 1 | 4 | 100,074,665 | 25,018,666 | 25,018,666 | 25,018,666 | 2026-08-21 | 2026-08-21 | untried |
| ab snowball r1 visual: new cores x all endings | 1 | 14 | 79 | 1,983,006,610 | 25,101,349 | 2,662,508 | 154,200,514 | 2026-09-29 | 2026-10-06 | spent |
| sound uncarried five-segment endings top16000 | 1 | 1 | 7 | 178,731,170 | 25,533,024 | 25,533,024 | 25,533,024 | 2026-09-09 | 2026-09-09 | untried |
| ab snowball r6 sound: new cores x all endings | 1 | 2 | 3 | 77,000,770 | 25,666,923 | 19,250,192 | 19,250,192 | 2026-10-01 | 2026-10-01 | live |
| cold war, uncarried five-segment endings | 1 | 1 | 382 | 9,963,115,100 | 26,081,453 | 26,081,453 | 26,081,453 | 2026-08-23 | 2026-08-23 | untried |
| yamyamok verified image heads with target-held conventions | 1 | 1 | 106 | 2,787,447,000 | 26,296,669 | 26,296,669 | 26,296,669 | 2026-10-09 | 2026-10-09 | untried |
| \ bo4 material token edits cap60 minseen1 20260830\ | 1 | 1 | 6 | 158,173,101 | 26,362,183 | 26,362,183 | 26,362,183 | 2026-08-30 | 2026-08-30 | untried |
| sound uncarried three-segment endings top32000 | 2 | 2 | 88 | 2,360,521,764 | 26,824,110 | 20,004,421 | 40,698,651 | 2026-09-09 | 2026-09-09 | live |
| open-slot english words, deep | 1 | 2 | 97 | 2,618,852,272 | 26,998,477 | 26,254,828 | 27,894,235 | 2026-10-01 | 2026-10-01 | live |
| tails of length 1 | 1 | 1 | 1 | 27,486,426 | 27,486,426 | 27,486,426 | 27,486,426 | 2026-09-03 | 2026-09-03 | untried |
| family column cross product, re-run on grown corpus | 1 | 1 | 2 | 55,113,580 | 27,556,790 | 27,556,790 | 27,556,790 | 2026-09-08 | 2026-09-08 | untried |
| open-slot embedding neighbours, per-filler knn 200 | 1 | 1 | 1 | 27,781,645 | 27,781,645 | 27,781,645 | 27,781,645 | 2026-10-01 | 2026-10-01 | untried |
| \ per-suffix precedents cw 20260830\ | 1 | 1 | 11 | 307,102,800 | 27,918,436 | 27,918,436 | 27,918,436 | 2026-08-30 | 2026-08-30 | untried |
| pooled context swap sound alias r1 | 1 | 1 | 1 | 28,008,296 | 28,008,296 | 28,008,296 | 28,008,296 | 2026-10-09 | 2026-10-09 | untried |
| pooled context swap sound alias r2 | 1 | 1 | 1 | 28,217,204 | 28,217,204 | 28,217,204 | 28,217,204 | 2026-10-10 | 2026-10-10 | untried |
| tails of length 3 | 1 | 204 | 264,370 | 7,480,988,739,324 | 28,297,419 | 1,196,677 | 21,887,436 | 2026-08-22 | 2026-10-09 | spent |
| rare splice 961 1920 | 1 | 2 | 5 | 142,066,503 | 28,413,300 | 17,758,312 | 17,758,312 | 2026-09-03 | 2026-09-03 | live |
| context swap r3 | 2 | 2 | 10 | 284,741,161 | 28,474,116 | 19,664,339 | 107,762,107 | 2026-10-09 | 2026-10-09 | cooling |
| sibling token substitution with digits, re-run on grown corpus | 1 | 1 | 6 | 172,336,688 | 28,722,781 | 28,722,781 | 28,722,781 | 2026-09-09 | 2026-09-09 | untried |
| cold war, uncarried four-segment endings | 1 | 1 | 645 | 18,715,524,480 | 29,016,317 | 29,016,317 | 29,016,317 | 2026-08-23 | 2026-08-23 | untried |
| material interior character substitutions refreshed | 1 | 1 | 17 | 496,757,656 | 29,221,038 | 29,221,038 | 29,221,038 | 2026-08-27 | 2026-08-27 | untried |
| image siblings wide | 1 | 2 | 8 | 241,732,438 | 30,216,554 | 20,144,369 | 20,144,369 | 2026-09-03 | 2026-09-03 | live |
| sound uncarried two-segment endings top500 | 1 | 1 | 1 | 30,263,406 | 30,263,406 | 30,263,406 | 30,263,406 | 2026-09-09 | 2026-09-09 | untried |
| ab snowball r5 visual: all cores x new endings | 1 | 1 | 1 | 30,269,536 | 30,269,536 | 30,269,536 | 30,269,536 | 2026-10-01 | 2026-10-01 | untried |
| ab snowball r6 visual: new cores x all endings | 1 | 3 | 12 | 364,801,216 | 30,400,101 | 13,666,712 | 118,800,396 | 2026-10-01 | 2026-10-05 | cooling |
| ab snowball r5 visual: new cores x all endings | 1 | 3 | 18 | 548,101,827 | 30,450,101 | 4,000,013 | 476,101,587 | 2026-10-01 | 2026-10-05 | spent |
| rare shared-token splices families 21301-21600 | 1 | 2 | 3 | 91,884,529 | 30,628,176 | 22,971,132 | 22,971,132 | 2026-08-29 | 2026-08-29 | live |
| \ cold war material token edits cap70 minseen1 20260830\ | 1 | 1 | 6 | 184,036,838 | 30,672,806 | 30,672,806 | 30,672,806 | 2026-08-30 | 2026-08-30 | untried |
| blackop7 sound basename endings inside tokens, width 4 | 1 | 2 | 40 | 1,231,471,333 | 30,786,783 | 16,229,095 | 16,229,095 | 2026-10-09 | 2026-10-10 | live |
| xanim heads x tails shared by >= 2 heads | 1 | 6 | 1,289 | 40,529,097,611 | 31,442,278 | 12,196,226 | 3,400,655,625 | 2026-10-09 | 2026-10-10 | spent |
| image token edits after new findings | 1 | 1 | 1 | 31,952,764 | 31,952,764 | 31,952,764 | 31,952,764 | 2026-08-26 | 2026-08-26 | untried |
| image token insertion and deletion after pr984 | 1 | 1 | 1 | 31,982,799 | 31,982,799 | 31,982,799 | 31,982,799 | 2026-08-27 | 2026-08-27 | untried |
| rare shared token splice 3841 7680 current | 1 | 2 | 11 | 353,828,962 | 32,166,269 | 17,691,448 | 17,691,448 | 2026-09-02 | 2026-09-02 | live |
| token edits image | 1 | 1 | 1 | 32,542,333 | 32,542,333 | 32,542,333 | 32,542,333 | 2026-09-03 | 2026-09-03 | untried |
| three-word slots, corpus word triples | 1 | 2 | 16 | 531,362,461 | 33,210,153 | 29,162,329 | 29,162,329 | 2026-10-01 | 2026-10-01 | live |
| rare shared-token splices families 17101-17400 | 1 | 2 | 2 | 66,750,923 | 33,375,461 | 33,375,461 | 33,375,461 | 2026-08-28 | 2026-08-28 | live |
| slot swap w1+w2 r2 | 2 | 2 | 14 | 467,938,918 | 33,424,208 | 19,497,454 | 19,497,454 | 2026-10-09 | 2026-10-09 | live |
| sound uncarried two-segment endings top2000 | 2 | 2 | 7 | 241,744,812 | 34,534,973 | 20,145,401 | 120,872,406 | 2026-09-09 | 2026-09-09 | cooling |
| four-word slots, every corpus word 4-gram | 1 | 2 | 105 | 3,632,778,776 | 34,597,893 | 30,726,879 | 30,726,879 | 2026-10-01 | 2026-10-01 | live |
| open-slot english words, pooled across grid rows | 1 | 2 | 46 | 1,605,789,441 | 34,908,466 | 20,081,375 | 133,755,738 | 2026-10-01 | 2026-10-01 | cooling |
| yamyamok four-layer terrain blends from target-held tokens | 1 | 1 | 3,676 | 129,816,000,000 | 35,314,472 | 35,314,472 | 35,314,472 | 2026-10-09 | 2026-10-09 | untried |
| open-slot english words, thin | 1 | 2 | 43 | 1,521,610,010 | 35,386,279 | 31,482,049 | 31,482,049 | 2026-10-01 | 2026-10-01 | live |
| per-prefix-continuations-depth2-cap48 | 1 | 1 | 2 | 72,302,925 | 36,151,462 | 36,151,462 | 36,151,462 | 2026-08-20 | 2026-08-20 | untried |
| heads of length 1 | 1 | 1 | 1 | 36,707,544 | 36,707,544 | 36,707,544 | 36,707,544 | 2026-08-27 | 2026-08-27 | untried |
| cold war sound, uncarried 1-segment endings | 1 | 2 | 560 | 20,953,836,251 | 37,417,564 | 29,431,729 | 29,431,729 | 2026-08-23 | 2026-08-23 | live |
| two-word slots, corpus pairs ranked 120k+ | 1 | 2 | 116 | 4,412,385,691 | 38,037,807 | 37,680,211 | 37,680,211 | 2026-10-01 | 2026-10-01 | live |
| modwar7 verified material-to-image channel seam | 1 | 1 | 1 | 38,528,896 | 38,528,896 | 38,528,896 | 38,528,896 | 2026-10-09 | 2026-10-09 | untried |
| packed twc/tw codes, last slot of every 4+ slot code swapped | 1 | 4 | 85 | 3,299,340,016 | 38,815,764 | 18,980,903 | 145,520,260 | 2026-10-09 | 2026-10-09 | cooling |
| sound uncarried two-segment endings top1000 | 2 | 2 | 5 | 196,436,240 | 39,287,248 | 33,992,458 | 60,466,406 | 2026-09-09 | 2026-09-09 | live |
| ab snowball r4 visual: new cores x all endings | 1 | 4 | 27 | 1,071,603,572 | 39,689,021 | 1,931,256 | 484,051,613 | 2026-10-01 | 2026-10-05 | spent |
| black ops 4, uncarried three-segment endings | 1 | 2 | 1,058 | 42,578,054,890 | 40,243,908 | 16,329,961 | 157,676,083 | 2026-08-23 | 2026-08-23 | cooling |
| xmodel cores spelled as image | 2 | 2 | 4 | 162,828,125 | 40,707,031 | 33,660,000 | 33,660,000 | 2026-09-02 | 2026-09-04 | live |
| pooled context swap sound asset r1 | 1 | 1 | 2 | 81,538,991 | 40,769,495 | 40,769,495 | 40,769,495 | 2026-10-09 | 2026-10-09 | untried |
| cold war uncarried one-segment endings top 500 after pr969 | 1 | 1 | 1 | 41,080,998 | 41,080,998 | 41,080,998 | 41,080,998 | 2026-08-27 | 2026-08-27 | untried |
| slot swap material r3 | 1 | 1 | 1 | 41,303,515 | 41,303,515 | 41,303,515 | 41,303,515 | 2026-10-09 | 2026-10-09 | untried |
| sound character insertion | 1 | 2 | 49 | 2,032,746,695 | 41,484,626 | 22,585,574 | 254,098,957 | 2026-08-24 | 2026-08-24 | spent |
| per-prefix continuations depth2 cap24 | 1 | 1 | 1 | 41,529,671 | 41,529,671 | 41,529,671 | 41,529,671 | 2026-08-27 | 2026-08-27 | untried |
| three-word slots, corpus triples ranked 20k+ | 1 | 3 | 286 | 12,012,991,070 | 42,003,465 | 36,031,182 | 36,031,182 | 2026-10-01 | 2026-10-01 | live |
| compound word slots, glove-ranked halves | 1 | 1 | 5 | 212,515,946 | 42,503,189 | 42,503,189 | 42,503,189 | 2026-10-01 | 2026-10-01 | untried |
| sound files and aliases, confirmed seeds only | 1 | 1 | 149 | 6,478,589,425 | 43,480,465 | 43,480,465 | 43,480,465 | 2026-10-08 | 2026-10-08 | untried |
| twc terrain-blend grid, quads over the top 600 tokens | 1 | 2 | 5,891 | 259,632,721,200 | 44,072,775 | 24,089,137 | 258,598,327 | 2026-10-08 | 2026-10-08 | spent |
| \ cold war material token edits cap50 minseen1 20260830\ | 1 | 1 | 3 | 132,268,164 | 44,089,388 | 44,089,388 | 44,089,388 | 2026-08-30 | 2026-08-30 | untried |
| two mined substitutions composed | 1 | 1 | 1 | 45,000,000 | 45,000,000 | 45,000,000 | 45,000,000 | 2026-08-25 | 2026-08-25 | untried |
| measured image channels | 1 | 2 | 2 | 90,670,236 | 45,335,118 | 45,049,731 | 45,620,505 | 2026-08-27 | 2026-08-31 | live |
| black ops 4, uncarried four-segment endings | 1 | 1 | 409 | 18,715,524,480 | 45,759,228 | 45,759,228 | 45,759,228 | 2026-08-23 | 2026-08-23 | untried |
| anim substitutions bo4 | 1 | 1 | 1 | 46,101,284 | 46,101,284 | 46,101,284 | 46,101,284 | 2026-08-26 | 2026-08-26 | untried |
| corpus pairs ranked 20k+ into one-word slots | 1 | 2 | 65 | 3,016,410,520 | 46,406,315 | 40,651,004 | 40,651,004 | 2026-10-05 | 2026-10-05 | live |
| ab snowball r2 visual: all cores x new endings | 1 | 2 | 9 | 419,799,558 | 46,644,395 | 41,979,955 | 41,979,955 | 2026-10-01 | 2026-10-01 | live |
| per-prefix-continuations-depth3-cap24 | 1 | 2 | 10 | 472,580,559 | 47,258,055 | 26,254,247 | 236,292,329 | 2026-08-20 | 2026-08-20 | cooling |
| single words into two-word slots | 1 | 2 | 19 | 910,470,000 | 47,919,473 | 38,225,000 | 38,225,000 | 2026-10-05 | 2026-10-05 | live |
| rare shared-token splices family sizes 8401-8700 | 1 | 1 | 1 | 48,782,460 | 48,782,460 | 48,782,460 | 48,782,460 | 2026-08-28 | 2026-08-28 | untried |
| char substitutions bo4 sounds | 1 | 1 | 21 | 1,035,667,459 | 49,317,498 | 49,317,498 | 49,317,498 | 2026-08-24 | 2026-08-24 | untried |
| tails of length 3, every table generation | 1 | 20 | 32,564 | 1,760,646,219,044 | 54,067,258 | 11,674,181 | 17,366,338 | 2026-10-09 | 2026-10-09 | live |
| material substitutions cw | 1 | 1 | 9 | 492,105,760 | 54,678,417 | 54,678,417 | 54,678,417 | 2026-08-25 | 2026-08-25 | untried |
| black ops 4, uncarried five-segment endings | 1 | 1 | 182 | 9,963,115,100 | 54,742,390 | 54,742,390 | 54,742,390 | 2026-08-23 | 2026-08-23 | untried |
| all-boundary refresh 2026-09-29, all cores x new endings | 1 | 2 | 10 | 548,202,080 | 54,820,208 | 39,157,291 | 91,367,013 | 2026-09-29 | 2026-09-29 | live |
| prefixed material bases as images | 1 | 2 | 653 | 36,847,040,254 | 56,427,320 | 40,580,440 | 92,580,503 | 2026-10-09 | 2026-10-09 | live |
| ab snowball r5 sound: new cores x every known tail | 1 | 2 | 44 | 2,511,845,316 | 57,087,393 | 31,398,066 | 31,398,066 | 2026-10-01 | 2026-10-01 | live |
| cold war, uncarried three-segment endings | 1 | 2 | 742 | 42,578,054,890 | 57,382,823 | 23,804,371 | 203,050,496 | 2026-08-23 | 2026-08-23 | cooling |
| cold war sound, uncarried two-segment endings | 1 | 1 | 195 | 11,273,898,861 | 57,814,865 | 57,814,865 | 57,814,865 | 2026-08-23 | 2026-08-23 | untried |
| open-slot embedding neighbours, ranks 3000-15000, frames >= 5 fillers | 1 | 1 | 2 | 116,167,256 | 58,083,628 | 58,083,628 | 58,083,628 | 2026-10-01 | 2026-10-01 | untried |
| tw 3-token names: known 2-token name + appended token | 1 | 2 | 11 | 641,256,174 | 58,296,015 | 35,625,343 | 160,314,043 | 2026-10-09 | 2026-10-09 | cooling |
| hot word prefixes x their family tails x top 30k words | 1 | 2 | 5 | 298,140,000 | 59,628,000 | 46,450,000 | 46,450,000 | 2026-10-01 | 2026-10-01 | live |
| images for every material prefix x 200 measured channel endings | 1 | 2 | 2 | 138,431,017 | 69,215,508 | 60,958,159 | 60,958,159 | 2026-10-06 | 2026-10-06 | live |
| material heads x tails shared by >= 2 heads | 1 | 4 | 7,110 | 495,761,933,903 | 69,727,416 | 47,070,443 | 358,630,286 | 2026-10-09 | 2026-10-10 | cooling |
| slot swap tail width 1 r2 | 1 | 1 | 2 | 144,420,393 | 72,210,196 | 72,210,196 | 72,210,196 | 2026-10-09 | 2026-10-09 | untried |
| twc 4-token names: prepended token + known 3-token name | 1 | 2 | 78 | 6,091,136,964 | 78,091,499 | 63,449,343 | 63,449,343 | 2026-10-09 | 2026-10-09 | live |
| sibling token substitution, right context, re-run on grown corpus | 1 | 1 | 4 | 313,996,264 | 78,499,066 | 78,499,066 | 78,499,066 | 2026-09-08 | 2026-09-08 | untried |
| twc 3-token names: prepended token + known 2-token name | 1 | 2 | 57 | 4,477,431,244 | 78,551,425 | 50,879,900 | 172,208,894 | 2026-10-09 | 2026-10-09 | cooling |
| open-slot english words, 2-filler frames under word-class heads | 1 | 2 | 17 | 1,345,670,508 | 79,157,088 | 76,939,404 | 81,651,983 | 2026-10-01 | 2026-10-01 | live |
| uncarried two-segment endings over the full published core list | 1 | 2 | 264 | 20,951,727,534 | 79,362,604 | 72,749,053 | 87,298,864 | 2026-08-23 | 2026-08-23 | live |
| two-token slots, mixed code/word pairs | 1 | 1 | 3 | 242,531,605 | 80,843,868 | 80,843,868 | 80,843,868 | 2026-10-01 | 2026-10-01 | untried |
| modern weapon image heads x every weapon's parts x variant x channel | 1 | 1 | 1 | 81,091,395 | 81,091,395 | 81,091,395 | 81,091,395 | 2026-10-09 | 2026-10-09 | untried |
| open-slot short codes | 1 | 1 | 2 | 179,032,926 | 89,516,463 | 89,516,463 | 89,516,463 | 2026-10-01 | 2026-10-01 | untried |
| packed twc/tw material codes, three slots, every observed number | 1 | 1 | 5,449 | 495,188,562,960 | 90,876,961 | 90,876,961 | 90,876,961 | 2026-10-09 | 2026-10-09 | untried |
| hot word frames, whole vocabulary, round 2 | 1 | 1 | 2 | 182,765,431 | 91,382,715 | 91,382,715 | 91,382,715 | 2026-10-01 | 2026-10-01 | untried |
| hot word frames, whole vocabulary, round 5 | 1 | 2 | 17 | 1,559,444,957 | 91,732,056 | 62,032,954 | 134,159,345 | 2026-10-05 | 2026-10-05 | live |
| confirmed-only all-boundary cores x uncarried endings | 2 | 17 | 1,187 | 109,498,794,977 | 92,248,352 | 29,860,502 | 2,300,323,003 | 2026-08-26 | 2026-08-29 | spent |
| character substitution material current | 1 | 1 | 5 | 466,937,880 | 93,387,576 | 93,387,576 | 93,387,576 | 2026-08-25 | 2026-08-25 | untried |
| confirmed-only all-boundary uncarried endings bo4 | 1 | 1 | 44 | 4,110,141,101 | 93,412,297 | 93,412,297 | 93,412,297 | 2026-09-02 | 2026-09-02 | untried |
| ab snowball r6 visual: all cores x new endings | 1 | 2 | 11 | 1,040,062,582 | 94,551,143 | 71,327,118 | 326,791,400 | 2026-10-01 | 2026-10-05 | cooling |
| char substitutions cw | 1 | 3 | 41 | 3,975,824,680 | 96,971,333 | 66,239,055 | 265,122,255 | 2026-08-24 | 2026-08-25 | cooling |
| ab snowball r2 visual: new cores x every known tail | 1 | 10 | 91 | 9,063,493,348 | 99,598,828 | 17,964,497 | 458,733,730 | 2026-10-01 | 2026-10-06 | spent |
| confirmed-only all-boundary cores x uncarried two-segment endings | 1 | 2 | 79 | 7,918,179,181 | 100,230,116 | 59,160,293 | 59,160,293 | 2026-09-01 | 2026-09-01 | live |
| sound path three-word slots | 1 | 1 | 1 | 101,772,379 | 101,772,379 | 101,772,379 | 101,772,379 | 2026-10-05 | 2026-10-05 | untried |
| cold war suffix precedents resume | 1 | 1 | 3 | 310,645,123 | 103,548,374 | 103,548,374 | 103,548,374 | 2026-09-01 | 2026-09-01 | untried |
| ab snowball r1 sound: all cores x new endings | 1 | 1 | 2 | 209,071,300 | 104,535,650 | 104,535,650 | 104,535,650 | 2026-10-01 | 2026-10-01 | untried |
| blackop7 verified image stem bytes crossed with witnessed suffixes | 1 | 1 | 112 | 12,073,198,176 | 107,796,412 | 107,796,412 | 107,796,412 | 2026-10-09 | 2026-10-09 | untried |
| char substitutions bo4 | 1 | 2 | 23 | 2,650,269,779 | 115,229,120 | 94,629,420 | 147,273,098 | 2026-08-24 | 2026-08-24 | live |
| sound uncarried two-segment endings top8000 | 2 | 2 | 8 | 966,616,812 | 120,827,101 | 80,551,401 | 241,654,203 | 2026-09-09 | 2026-09-09 | live |
| slot swap from end w1+w2 r4 | 1 | 1 | 2 | 243,650,034 | 121,825,017 | 121,825,017 | 121,825,017 | 2026-10-09 | 2026-10-09 | untried |
| ab snowball r3 visual: new cores x every known tail | 1 | 7 | 155 | 19,456,178,062 | 125,523,729 | 5,003,103 | 818,255,227 | 2026-10-01 | 2026-10-05 | spent |
| confirmed-only sound all-boundary cores x uncarried endings | 2 | 7 | 717 | 91,609,516,086 | 127,767,804 | 42,055,113 | 79,082,077 | 2026-08-26 | 2026-08-26 | live |
| tw-family terrain grids, triples over the top 1500 tokens | 1 | 2 | 369 | 47,286,003,000 | 128,146,349 | 112,585,721 | 148,698,122 | 2026-10-08 | 2026-10-08 | live |
| sound path two-word slots, pairs ranked 30k+ | 1 | 2 | 4 | 516,815,180 | 129,203,795 | 79,600,424 | 79,600,424 | 2026-10-01 | 2026-10-01 | live |
| uncarried beginnings over the held vocabulary | 1 | 1 | 7 | 945,274,375 | 135,039,196 | 135,039,196 | 135,039,196 | 2026-08-23 | 2026-08-23 | untried |
| mw7 full-corpus visual numeric siblings 0-999 | 1 | 1 | 3 | 443,772,340 | 147,924,113 | 147,924,113 | 147,924,113 | 2026-10-08 | 2026-10-08 | untried |
| ab snowball r5 sound: all cores x new name tails | 1 | 1 | 32 | 4,756,607,392 | 148,643,981 | 148,643,981 | 148,643,981 | 2026-10-01 | 2026-10-01 | untried |
| packed twc/tw codes delta, three slots | 3 | 6 | 297 | 44,816,550,372 | 150,897,476 | 53,164,203 | 218,001,709 | 2026-10-09 | 2026-10-09 | cooling |
| hot cores x every tail of every known name | 1 | 2 | 202 | 30,561,666,356 | 151,295,378 | 132,876,810 | 132,876,810 | 2026-09-30 | 2026-09-30 | live |
| confirmed-only all-boundary cores x uncarried five-segment endings | 1 | 1 | 26 | 3,959,839,598 | 152,301,523 | 152,301,523 | 152,301,523 | 2026-09-01 | 2026-09-01 | untried |
| sound uncarried four-segment endings top32000 | 2 | 2 | 9 | 1,375,146,972 | 152,794,108 | 85,946,685 | 85,946,685 | 2026-09-09 | 2026-09-09 | live |
| ab snowball r3 sound: all cores x new name tails | 1 | 4 | 64 | 10,143,244,550 | 158,488,196 | 35,838,299 | 1,095,338,107 | 2026-10-01 | 2026-10-01 | spent |
| confirmed-only all-boundary cores x uncarried 2-segment endings, top 300000, blkops04 | 1 | 1 | 71 | 11,310,637,702 | 159,304,756 | 159,304,756 | 159,304,756 | 2026-09-01 | 2026-09-01 | untried |
| sound asset heads x tails shared by >= 2 heads | 1 | 2 | 318 | 51,674,403,336 | 162,498,123 | 109,159,015 | 109,159,015 | 2026-10-09 | 2026-10-09 | live |
| image heads x tails shared by >= 2 heads | 1 | 6 | 2,118 | 347,533,682,184 | 164,085,780 | 53,550,795 | 8,293,632,638 | 2026-10-09 | 2026-10-10 | spent |
| sound character substitution current | 1 | 1 | 6 | 985,045,956 | 164,174,326 | 164,174,326 | 164,174,326 | 2026-08-25 | 2026-08-25 | untried |
| confirmed-only all-boundary sound cores x fresh uncarried endings, 2026-09-20 | 1 | 2 | 14 | 2,334,809,970 | 166,772,140 | 145,925,623 | 145,925,623 | 2026-09-20 | 2026-09-20 | live |
| ab snowball r3 visual: all cores x new endings | 1 | 1 | 1 | 168,306,298 | 168,306,298 | 168,306,298 | 168,306,298 | 2026-10-01 | 2026-10-01 | untried |
| wrapper decorations, suffix side | 1 | 8 | 1,071 | 185,010,310,334 | 172,745,387 | 1,985,948 | 159,762,864 | 2026-08-23 | 2026-08-23 | spent |
| confirmed-only all-boundary cores x uncarried 3-segment endings, top 300000, blkops04 | 1 | 1 | 64 | 11,293,237,644 | 176,456,838 | 176,456,838 | 176,456,838 | 2026-09-01 | 2026-09-01 | untried |
| cold war sound, uncarried 3-segment endings | 1 | 2 | 121 | 22,865,684,520 | 188,972,599 | 181,473,686 | 181,473,686 | 2026-08-23 | 2026-08-23 | live |
| measured heads of length 6 | 2 | 2 | 92 | 17,483,482,820 | 190,037,856 | 135,677,462 | 135,677,462 | 2026-08-25 | 2026-08-25 | live |
| confirmed-only all-boundary cores x uncarried three-segment endings | 1 | 2 | 41 | 7,911,079,110 | 192,953,149 | 113,035,416 | 113,035,416 | 2026-09-01 | 2026-09-01 | live |
| confirmed-only all-boundary cold war cores x uncarried endings | 1 | 3 | 75 | 14,592,745,926 | 194,569,945 | 67,600,676 | 758,467,584 | 2026-08-29 | 2026-08-31 | spent |
| two-word slots, word pairs from wiki dialogue transcripts | 1 | 1 | 5 | 988,748,930 | 197,749,786 | 197,749,786 | 197,749,786 | 2026-10-07 | 2026-10-07 | untried |
| ab snowball r3 visual: all cores x new name tails | 1 | 7 | 113 | 22,449,734,850 | 198,670,219 | 13,083,628 | 2,111,181,504 | 2026-10-01 | 2026-10-05 | spent |
| sound-file head swap | 1 | 3 | 112 | 22,915,303,408 | 204,600,923 | 125,556,458 | 521,100,960 | 2026-10-09 | 2026-10-09 | cooling |
| scoped all-boundary cores x all uncarried 3-segment endings | 1 | 1 | 621 | 134,101,557,623 | 215,944,537 | 215,944,537 | 215,944,537 | 2026-09-03 | 2026-09-03 | untried |
| compound word slots, halves x words ranked 5k-30k | 1 | 1 | 12 | 2,662,775,000 | 221,897,916 | 221,897,916 | 221,897,916 | 2026-10-01 | 2026-10-01 | untried |
| voice phrase grids, small casts, probe | 1 | 1 | 2 | 447,982,774 | 223,991,387 | 223,991,387 | 223,991,387 | 2026-10-05 | 2026-10-05 | untried |
| sound uncarried three-segment endings top64000 | 2 | 2 | 21 | 4,720,969,764 | 224,808,084 | 214,589,534 | 214,589,534 | 2026-09-09 | 2026-09-09 | live |
| ab snowball r2 visual: all cores x new name tails | 1 | 10 | 79 | 18,727,983,378 | 237,063,080 | 29,493,796 | 789,727,527 | 2026-09-30 | 2026-10-05 | spent |
| sound uncarried two-segment endings top4000 | 1 | 1 | 1 | 241,684,406 | 241,684,406 | 241,684,406 | 241,684,406 | 2026-09-09 | 2026-09-09 | untried |
| uncarried endings over all-boundary truncation cores | 1 | 6 | 4,625 | 1,120,036,280,202 | 242,170,006 | 76,634,118 | 518,821,573 | 2026-08-23 | 2026-08-23 | cooling |
| uncarried three-segment endings over the full published core list | 1 | 2 | 56 | 13,564,678,200 | 242,226,396 | 165,422,904 | 165,422,904 | 2026-08-23 | 2026-08-23 | live |
| themed weapon codenames | 1 | 1 | 17 | 4,257,632,738 | 250,448,984 | 250,448,984 | 250,448,984 | 2026-10-09 | 2026-10-09 | untried |
| uncarried three-segment endings over all-boundary cores | 1 | 2 | 1,523 | 400,012,766,734 | 262,647,909 | 221,982,667 | 221,982,667 | 2026-08-23 | 2026-08-23 | live |
| confirmed-only all-boundary uncarried two-segment endings current | 1 | 1 | 28 | 7,610,476,104 | 271,802,718 | 271,802,718 | 271,802,718 | 2026-09-01 | 2026-09-01 | untried |
| sound uncarried two-segment endings top64000 | 1 | 1 | 14 | 3,866,044,406 | 276,146,029 | 276,146,029 | 276,146,029 | 2026-09-09 | 2026-09-09 | untried |
| heads of length 3, every table generation | 1 | 4 | 1,727 | 480,800,313,072 | 278,402,034 | 121,367,021 | 467,160,246 | 2026-10-09 | 2026-10-09 | cooling |
| ab snowball r2 sound: new cores x every known tail | 1 | 8 | 66 | 18,535,852,534 | 280,846,250 | 23,533,845 | 127,683,546 | 2026-10-01 | 2026-10-05 | cooling |
| execution quips, topic(500) + function word triples, one speaker | 1 | 1 | 1 | 283,593,393 | 283,593,393 | 283,593,393 | 283,593,393 | 2026-10-06 | 2026-10-06 | untried |
| model character substitutions refreshed | 1 | 1 | 1 | 286,924,916 | 286,924,916 | 286,924,916 | 286,924,916 | 2026-08-27 | 2026-08-27 | untried |
| all-boundary confirmed cores x uncarried endings | 1 | 8 | 243 | 70,412,103,724 | 289,761,743 | 22,567,795 | 2,875,461,397 | 2026-09-03 | 2026-09-03 | spent |
| ab snowball r1 visual: new cores x every known tail | 1 | 11 | 109 | 31,956,685,870 | 293,180,604 | 4,603,553 | 1,177,660,445 | 2026-09-30 | 2026-10-06 | spent |
| twc terrain-blend grid, triples over the full 0..4000 numeric range | 1 | 2 | 432 | 128,160,064,008 | 296,666,814 | 165,154,721 | 1,456,364,363 | 2026-10-09 | 2026-10-09 | cooling |
| measured heads of length 5 | 1 | 3 | 31 | 9,541,037,394 | 307,775,399 | 210,743,705 | 210,743,705 | 2026-08-25 | 2026-08-26 | live |
| tw 3-token names: prepended token + known 2-token name | 1 | 1 | 1 | 320,628,087 | 320,628,087 | 320,628,087 | 320,628,087 | 2026-10-09 | 2026-10-09 | untried |
| sound uncarried two-segment endings top16000 | 2 | 2 | 6 | 1,933,112,812 | 322,185,468 | 241,639,101 | 241,639,101 | 2026-09-09 | 2026-09-09 | live |
| uncarried endings over published cores | 1 | 6 | 1,191 | 385,019,657,854 | 323,274,271 | 17,624,983 | 4,062,515,784 | 2026-08-23 | 2026-08-23 | spent |
| black ops 4 confirmed-only all-boundary uncarried two-segment endings | 1 | 1 | 22 | 7,125,471,254 | 323,885,057 | 323,885,057 | 323,885,057 | 2026-08-30 | 2026-08-30 | untried |
| sound, uncarried endings over all-boundary cores | 1 | 8 | 3,397 | 1,105,024,531,644 | 325,294,239 | 92,280,373 | 902,952,472 | 2026-08-23 | 2026-08-23 | cooling |
| char insertions bo4 | 1 | 1 | 4 | 1,358,281,948 | 339,570,487 | 339,570,487 | 339,570,487 | 2026-08-24 | 2026-08-24 | untried |
| ab snowball r4 sound: all cores x new name tails | 1 | 1 | 3 | 1,023,185,585 | 341,061,861 | 341,061,861 | 341,061,861 | 2026-10-01 | 2026-10-01 | untried |
| confirmed-only all-boundary uncarried endings cw | 1 | 1 | 12 | 4,110,141,101 | 342,511,758 | 342,511,758 | 342,511,758 | 2026-09-02 | 2026-09-02 | untried |
| twc terrain-blend grid, quads over the full 0..800 numeric range | 1 | 1 | 1,177 | 412,166,408,004 | 350,183,864 | 350,183,864 | 350,183,864 | 2026-10-09 | 2026-10-09 | untried |
| confirmed-only cores over the full uncarried ending vocabulary | 1 | 8 | 1,576 | 555,022,909,612 | 352,171,896 | 141,523,942 | 3,319,756,536 | 2026-08-23 | 2026-08-23 | spent |
| sound dotted tails | 1 | 3 | 126 | 29,595,227,882 | 352,324,141 | 343,483,821 | 361,595,696 | 2026-08-19 | 2026-08-24 | live |
| confirmed-only all-boundary uncarried sound endings bo4 | 1 | 1 | 43 | 15,363,253,631 | 357,284,968 | 357,284,968 | 357,284,968 | 2026-09-02 | 2026-09-02 | untried |
| ab snowball r3 sound: new cores x every known tail | 1 | 5 | 84 | 31,383,093,074 | 373,608,250 | 60,273,336 | 641,509,388 | 2026-10-01 | 2026-10-05 | spent |
| ab snowball r4 visual: new cores x every known tail | 1 | 4 | 48 | 17,937,392,558 | 373,695,678 | 73,641,762 | 438,095,252 | 2026-10-01 | 2026-10-05 | cooling |
| ab snowball r1 sound: all cores x new name tails | 1 | 4 | 14 | 5,326,857,858 | 380,489,847 | 77,911,182 | 77,911,182 | 2026-10-01 | 2026-10-05 | live |
| ab snowball r5 sound: new slotswap cores x all endings | 1 | 1 | 1 | 394,303,943 | 394,303,943 | 394,303,943 | 394,303,943 | 2026-10-01 | 2026-10-01 | untried |
| yamyamok terrain numeric domain 0..1000, first untested layer 4 | 1 | 1 | 181 | 72,501,549,197 | 400,561,045 | 400,561,045 | 400,561,045 | 2026-10-09 | 2026-10-09 | untried |
| modwar22 alias terminal-3 from witnessed prefixes | 1 | 1 | 4 | 1,609,412,100 | 402,353,025 | 402,353,025 | 402,353,025 | 2026-10-10 | 2026-10-10 | untried |
| measured heads of length 4 | 2 | 3 | 15 | 6,149,861,538 | 409,990,769 | 115,289,728 | 3,152,328,598 | 2026-08-25 | 2026-08-25 | spent |
| sound uncarried three-segment endings top256000 | 2 | 2 | 46 | 18,883,657,764 | 410,514,299 | 393,409,536 | 393,409,536 | 2026-09-09 | 2026-09-09 | live |
| sound uncarried three-segment endings top128000 | 2 | 2 | 23 | 9,441,865,764 | 410,515,902 | 236,046,644 | 1,573,644,294 | 2026-09-09 | 2026-09-09 | cooling |
| slotswap-substituted all-boundary cores, visual, delta from the refreshed base 2026-09-29 | 1 | 2 | 41 | 17,316,057,720 | 422,342,871 | 346,321,154 | 346,321,154 | 2026-09-29 | 2026-09-29 | live |
| tails of names confirmed since 2026-09-25 x prefixes the all-boundary list does not carry | 1 | 1 | 2 | 850,397,911 | 425,198,955 | 425,198,955 | 425,198,955 | 2026-09-30 | 2026-09-30 | untried |
| dotted sound basenames, last 2 characters replaced, modwar22 tails | 1 | 1 | 27 | 11,529,794,664 | 427,029,432 | 427,029,432 | 427,029,432 | 2026-10-09 | 2026-10-09 | untried |
| sound uncarried two-segment endings top32000 | 2 | 2 | 9 | 3,866,104,812 | 429,567,201 | 386,610,481 | 483,263,101 | 2026-09-09 | 2026-09-09 | live |
| confirmed-only all-boundary black ops 4 cores x uncarried endings | 1 | 3 | 41 | 17,821,278,211 | 434,665,322 | 118,435,559 | 118,435,559 | 2026-08-29 | 2026-08-31 | live |
| ab snowball r5 visual: new cores x every known tail | 1 | 3 | 21 | 9,189,021,255 | 437,572,440 | 66,736,746 | 1,331,293,302 | 2026-10-01 | 2026-10-05 | spent |
| cold war confirmed-only all-boundary uncarried two-segment endings | 1 | 1 | 16 | 7,124,171,241 | 445,260,702 | 445,260,702 | 445,260,702 | 2026-08-30 | 2026-08-30 | untried |
| composed numeric endings | 1 | 2 | 14 | 6,497,838,750 | 464,131,339 | 406,114,921 | 406,114,921 | 2026-08-23 | 2026-08-23 | live |
| wrapper decorations, prefix side | 1 | 4 | 22 | 10,237,404,404 | 465,336,563 | 39,559,390 | 1,180,777,075 | 2026-08-23 | 2026-08-23 | spent |
| older-title decorations | 1 | 3 | 20 | 9,365,249,044 | 468,262,452 | 6,372,899 | 6,372,899 | 2026-08-23 | 2026-08-30 | live |
| ab snowball r6 visual: new cores x every known tail | 1 | 3 | 13 | 6,099,661,184 | 469,204,706 | 293,272,531 | 664,615,248 | 2026-10-01 | 2026-10-05 | live |
| ab snowball r3 sound: new slotswap cores x all endings | 1 | 1 | 4 | 1,908,319,083 | 477,079,770 | 477,079,770 | 477,079,770 | 2026-10-01 | 2026-10-01 | untried |
| confirmed-only all-boundary cores x uncarried six-segment endings | 1 | 1 | 8 | 3,962,339,623 | 495,292,452 | 495,292,452 | 495,292,452 | 2026-09-01 | 2026-09-01 | untried |
| measured tails of length 56 | 1 | 1 | 5 | 2,521,780,812 | 504,356,162 | 504,356,162 | 504,356,162 | 2026-08-25 | 2026-08-25 | untried |
| all-boundary sound cores x uncarried sound endings, 2 segments, top 200k | 1 | 1 | 634 | 320,548,256,700 | 505,596,619 | 505,596,619 | 505,596,619 | 2026-08-29 | 2026-08-29 | untried |
| yamyamok terrain numeric domain 0..1000, first untested layer 1 | 1 | 1 | 913 | 463,850,310,924 | 508,050,723 | 508,050,723 | 508,050,723 | 2026-10-09 | 2026-10-09 | untried |
| first twenty ceiling-dropped black ops 4 sound beginnings | 1 | 1 | 17 | 8,705,046,735 | 512,061,572 | 512,061,572 | 512,061,572 | 2026-08-29 | 2026-08-29 | untried |
| scoped all-boundary sound cores x all uncarried 2-segment sound endings (full vocabulary), re-run at grown corpus | 1 | 1 | 54 | 28,168,563,166 | 521,640,058 | 521,640,058 | 521,640,058 | 2026-09-03 | 2026-09-03 | untried |
| packed twc/tw material codes, three slots, slices 7-8 | 1 | 1 | 235 | 123,737,992,560 | 526,544,649 | 526,544,649 | 526,544,649 | 2026-10-09 | 2026-10-09 | untried |
| affix sweep | 1 | 1 | 1 | 532,497,168 | 532,497,168 | 532,497,168 | 532,497,168 | 2026-08-20 | 2026-08-20 | untried |
| yamyamok terrain numeric domain 0..1000, first untested layer 2 | 1 | 1 | 469 | 249,765,552,036 | 532,549,151 | 532,549,151 | 532,549,151 | 2026-10-09 | 2026-10-09 | untried |
| ab snowball r5 visual: all cores x new name tails | 1 | 3 | 36 | 19,893,304,174 | 552,591,782 | 84,935,759 | 3,784,225,412 | 2026-10-01 | 2026-10-05 | spent |
| confirmed-only all-boundary cores x uncarried 1-segment endings, blkops04 | 1 | 1 | 12 | 6,800,804,899 | 566,733,741 | 566,733,741 | 566,733,741 | 2026-09-01 | 2026-09-01 | untried |
| ab snowball r6 sound: new cores x every known tail | 1 | 2 | 7 | 3,981,074,790 | 568,724,970 | 331,756,232 | 331,756,232 | 2026-10-01 | 2026-10-01 | live |
| sound all-boundary uncarried endings current | 1 | 2 | 127 | 72,404,724,040 | 570,115,937 | 341,742,866 | 341,742,866 | 2026-09-01 | 2026-09-05 | live |
| yamyamok terrain numeric domain 0..1000, first untested layer 3 | 1 | 1 | 231 | 134,489,143,404 | 582,204,084 | 582,204,084 | 582,204,084 | 2026-10-09 | 2026-10-09 | untried |
| measured heads of length 48 | 1 | 2 | 51 | 30,025,694,930 | 588,739,116 | 428,938,499 | 938,302,966 | 2026-08-25 | 2026-08-25 | live |
| external bo4 xhash cores under uncarried endings | 1 | 1 | 2 | 1,196,624,742 | 598,312,371 | 598,312,371 | 598,312,371 | 2026-09-01 | 2026-09-01 | untried |
| all-boundary cores x uncarried endings, 1 segment(s), top 100000 | 1 | 1 | 6 | 3,777,037,770 | 629,506,295 | 629,506,295 | 629,506,295 | 2026-09-02 | 2026-09-02 | untried |
| all-boundary sound cores x uncarried sound endings, 3 segment(s), top 100000 | 1 | 3 | 83 | 52,864,928,644 | 636,926,851 | 317,511,508 | 317,511,508 | 2026-09-02 | 2026-09-09 | live |
| ab snowball r6 visual: all cores x new name tails | 1 | 2 | 8 | 5,143,477,968 | 642,934,746 | 514,347,796 | 857,246,328 | 2026-10-01 | 2026-10-01 | live |
| all-boundary confirmed sound cores x uncarried sound endings | 1 | 6 | 148 | 95,632,345,436 | 646,164,496 | 132,076,779 | 1,655,224,416 | 2026-09-03 | 2026-09-03 | spent |
| animation transition grid | 1 | 2 | 2 | 1,295,625,020 | 647,812,510 | 647,812,510 | 647,812,510 | 2026-08-23 | 2026-08-23 | live |
| ab snowball r2 visual: new slotswap cores x all endings | 1 | 6 | 20 | 12,971,143,237 | 648,557,161 | 176,400,588 | 176,400,588 | 2026-09-29 | 2026-10-05 | live |
| confirmed-only all-boundary cores x uncarried four-segment endings | 1 | 1 | 6 | 3,955,839,558 | 659,306,593 | 659,306,593 | 659,306,593 | 2026-09-01 | 2026-09-01 | untried |
| cold war sound harvested decorations | 1 | 1 | 105 | 71,392,088,600 | 679,924,653 | 679,924,653 | 679,924,653 | 2026-09-02 | 2026-09-02 | untried |
| heads of length 3 | 1 | 9 | 717 | 495,967,132,221 | 691,725,428 | 66,983,541 | 53,101,554,920 | 2026-08-22 | 2026-08-29 | spent |
| xanim cores borrowed wide, stripped shallow | 1 | 2 | 78 | 54,150,768,000 | 694,240,615 | 466,816,965 | 466,816,965 | 2026-08-24 | 2026-08-24 | live |
| double deletion | 1 | 1 | 1 | 712,525,298 | 712,525,298 | 712,525,298 | 712,525,298 | 2026-08-24 | 2026-08-24 | untried |
| measured heads of length 40 | 1 | 2 | 116 | 83,913,981,368 | 723,396,391 | 599,385,581 | 912,108,493 | 2026-08-25 | 2026-08-25 | live |
| confirmed-only all-boundary cores x uncarried 4-segment endings, top 300000, blkops04 | 1 | 1 | 15 | 11,319,937,733 | 754,662,515 | 754,662,515 | 754,662,515 | 2026-09-01 | 2026-09-01 | untried |
| mwii sound heads x shared tails | 1 | 4 | 443 | 343,045,627,067 | 774,369,361 | 428,872,158 | 11,954,781,124 | 2026-10-08 | 2026-10-08 | spent |
| char double deletions cw | 1 | 1 | 1 | 780,126,906 | 780,126,906 | 780,126,906 | 780,126,906 | 2026-08-24 | 2026-08-24 | untried |
| ab snowball r2 sound: all cores x new name tails | 1 | 3 | 17 | 13,449,786,945 | 791,163,937 | 703,145,554 | 2,199,458,079 | 2026-10-01 | 2026-10-05 | cooling |
| confirmed-only all-boundary cores x uncarried one-segment endings | 1 | 2 | 10 | 7,929,679,296 | 792,967,929 | 495,917,459 | 495,917,459 | 2026-09-01 | 2026-09-01 | live |
| confirmed-only all-boundary sound cores x uncarried 2-segment sound endings, blkops04 | 1 | 1 | 30 | 23,859,316,386 | 795,310,546 | 795,310,546 | 795,310,546 | 2026-09-01 | 2026-09-01 | untried |
| confirmed-only all-boundary cold war sound cores x uncarried sound endings | 1 | 1 | 17 | 14,337,543,374 | 843,384,904 | 843,384,904 | 843,384,904 | 2026-08-29 | 2026-08-29 | untried |
| confirmed-only all-boundary uncarried three-segment sound endings cw | 1 | 1 | 18 | 15,368,253,681 | 853,791,871 | 853,791,871 | 853,791,871 | 2026-09-02 | 2026-09-02 | untried |
| confirmed-only all-boundary uncarried five-segment sound endings bo4 | 1 | 1 | 18 | 15,379,053,789 | 854,391,877 | 854,391,877 | 854,391,877 | 2026-09-02 | 2026-09-02 | untried |
| packed twc/tw codes, third of four slots over every number | 1 | 4 | 1,977 | 1,717,192,039,160 | 868,584,744 | 266,269,590 | 63,164,340,051 | 2026-10-09 | 2026-10-09 | spent |
| cold war sound files, core tails of length 1 and 2 | 1 | 1 | 1 | 881,657,430 | 881,657,430 | 881,657,430 | 881,657,430 | 2026-08-23 | 2026-08-23 | untried |
| heads of length 2, head-measured alphabet | 1 | 2 | 3 | 2,730,823,702 | 910,274,567 | 682,705,925 | 1,365,411,851 | 2026-09-08 | 2026-09-08 | live |
| execution quips, topic word x 150k common words, one speaker | 1 | 1 | 1 | 919,500,000 | 919,500,000 | 919,500,000 | 919,500,000 | 2026-10-06 | 2026-10-06 | untried |
| all-boundary cores with uncarried three-segment endings | 2 | 3 | 58 | 53,493,592,404 | 922,303,317 | 446,051,682 | 1,943,570,114 | 2026-08-30 | 2026-08-31 | cooling |
| ab snowball r3 visual: new slotswap cores x all endings | 1 | 3 | 15 | 13,976,746,589 | 931,783,105 | 235,700,785 | 6,634,822,116 | 2026-10-01 | 2026-10-01 | spent |
| rule-substituted cores sound delta 2026-09-30 | 1 | 1 | 3 | 2,833,728,337 | 944,576,112 | 944,576,112 | 944,576,112 | 2026-09-30 | 2026-09-30 | untried |
| general ceiling-dropped beginnings cross-title | 1 | 1 | 44 | 43,531,074,800 | 989,342,609 | 989,342,609 | 989,342,609 | 2026-09-09 | 2026-09-09 | untried |
| family walking, numbers in place | 1 | 40 | 1,753 | 261,210,988,962 | 996,988,507 | 200,051,105 | 3,557,728,643 | 2026-08-19 | 2026-09-22 | spent |
| all-boundary general cores x top-100k uncarried endings, refreshed 2026-09-20 | 1 | 2 | 375 | 375,311,953,082 | 1,000,831,874 | 579,185,112 | 579,185,112 | 2026-09-20 | 2026-09-20 | live |
| all-boundary cores with uncarried four-segment endings | 1 | 1 | 16 | 16,060,860,607 | 1,003,803,787 | 1,003,803,787 | 1,003,803,787 | 2026-08-30 | 2026-08-30 | untried |
| confirmed-only all-boundary uncarried sound endings cw | 1 | 1 | 15 | 15,363,253,631 | 1,024,216,908 | 1,024,216,908 | 1,024,216,908 | 2026-09-02 | 2026-09-02 | untried |
| confirmed-only all-boundary uncarried three-segment sound endings bo4 | 1 | 1 | 15 | 15,368,253,681 | 1,024,550,245 | 1,024,550,245 | 1,024,550,245 | 2026-09-02 | 2026-09-02 | untried |
| all-boundary sound cores x uncarried sound endings, 2 segment(s), top 100000 | 1 | 5 | 265 | 271,741,317,386 | 1,025,438,933 | 247,119,354 | 247,119,354 | 2026-08-31 | 2026-09-09 | live |
| ab snowball r1 visual: all cores x new name tails | 1 | 9 | 31 | 31,790,314,044 | 1,025,494,001 | 107,819,718 | 5,534,631,186 | 2026-09-30 | 2026-10-06 | spent |
| confirmed-only all-boundary uncarried endings cw snowball | 1 | 1 | 4 | 4,115,041,150 | 1,028,760,287 | 1,028,760,287 | 1,028,760,287 | 2026-09-02 | 2026-09-02 | untried |
| every tail of names confirmed since 2026-09-25 x all-boundary cores | 1 | 2 | 27 | 28,017,699,060 | 1,037,692,557 | 737,307,870 | 1,751,106,191 | 2026-09-30 | 2026-09-30 | live |
| uncarried four-segment endings over all-boundary cores | 1 | 2 | 381 | 400,012,766,734 | 1,049,902,274 | 1,020,440,731 | 1,020,440,731 | 2026-08-23 | 2026-08-23 | live |
| char insertions bo4 sounds | 1 | 1 | 1 | 1,068,730,763 | 1,068,730,763 | 1,068,730,763 | 1,068,730,763 | 2026-08-24 | 2026-08-24 | untried |
| confirmed-only all-boundary sound cores x uncarried 1-segment sound endings, blkops04 | 1 | 1 | 4 | 4,300,971,681 | 1,075,242,920 | 1,075,242,920 | 1,075,242,920 | 2026-09-02 | 2026-09-02 | untried |
| all-boundary cores x uncarried endings, 2 segments | 1 | 1 | 163 | 177,157,271,555 | 1,086,854,426 | 1,086,854,426 | 1,086,854,426 | 2026-08-23 | 2026-08-23 | untried |
| all-boundary uncarried three-segment endings current | 1 | 1 | 30 | 33,669,536,692 | 1,122,317,889 | 1,122,317,889 | 1,122,317,889 | 2026-09-01 | 2026-09-01 | untried |
| v2 xanim borrowed endings, ranks 2001-3000 | 1 | 2 | 24 | 28,120,092,000 | 1,171,670,500 | 639,093,000 | 7,030,023,000 | 2026-08-28 | 2026-08-28 | spent |
| external bo4 xhash cores under uncarried endings ranks 3001-6000 | 1 | 2 | 2 | 2,393,249,484 | 1,196,624,742 | 1,196,624,742 | 1,196,624,742 | 2026-09-01 | 2026-09-04 | live |
| measured heads of length 32 | 1 | 2 | 162 | 196,053,608,608 | 1,210,207,460 | 1,113,940,958 | 1,324,686,544 | 2026-08-25 | 2026-08-25 | live |
| all-boundary sound cores x uncarried sound endings, 4 segment(s), top 100000 | 1 | 2 | 31 | 38,151,181,508 | 1,230,683,274 | 1,192,268,172 | 1,192,268,172 | 2026-09-09 | 2026-09-09 | live |
| black ops 4 confirmed-only all-boundary uncarried three-segment endings | 1 | 1 | 17 | 21,379,271,264 | 1,257,604,192 | 1,257,604,192 | 1,257,604,192 | 2026-08-30 | 2026-08-30 | untried |
| all-boundary sound cores x uncarried sound endings, 1 segment, top 300k | 1 | 1 | 46 | 58,151,913,260 | 1,264,172,027 | 1,264,172,027 | 1,264,172,027 | 2026-08-29 | 2026-08-29 | untried |
| measured heads of length 12 | 2 | 4 | 160 | 204,300,194,532 | 1,276,876,215 | 579,736,120 | 3,832,699,909 | 2026-08-25 | 2026-08-25 | cooling |
| ab snowball r1 visual: new slotswap cores x all endings | 1 | 9 | 43 | 55,237,984,126 | 1,284,604,282 | 259,200,864 | 3,490,061,633 | 2026-09-29 | 2026-10-06 | spent |
| ab snowball r1 visual: old slotswap cores x new endings | 1 | 3 | 3 | 3,929,287,822 | 1,309,762,607 | 455,192,348 | 2,351,501,010 | 2026-09-29 | 2026-10-01 | cooling |
| measured tails of length 64 | 1 | 1 | 1 | 1,336,663,110 | 1,336,663,110 | 1,336,663,110 | 1,336,663,110 | 2026-08-25 | 2026-08-25 | untried |
| v2 xanim borrowed endings, ranks 1001-2000 | 1 | 2 | 21 | 28,271,743,500 | 1,346,273,500 | 738,975,078 | 7,115,608,500 | 2026-08-28 | 2026-08-29 | cooling |
| uncarried five-segment endings over all-boundary cores | 1 | 2 | 597 | 804,758,082,518 | 1,348,003,488 | 906,259,101 | 906,259,101 | 2026-08-23 | 2026-08-23 | live |
| sound all-boundary cores with uncarried one-segment endings | 2 | 2 | 7 | 9,456,617,520 | 1,350,945,360 | 1,182,077,190 | 1,576,102,920 | 2026-08-30 | 2026-08-30 | live |
| confirmed-only endings x cores, after +18k merge, general, 2026-09-25 | 1 | 2 | 86 | 118,067,284,226 | 1,372,875,397 | 797,751,920 | 797,751,920 | 2026-09-25 | 2026-09-25 | live |
| modwar22 alias terminal-4 from witnessed prefixes | 1 | 1 | 37 | 52,135,605,522 | 1,409,070,419 | 1,409,070,419 | 1,409,070,419 | 2026-10-10 | 2026-10-10 | untried |
| heads of length 2 | 1 | 1 | 1 | 1,419,111,216 | 1,419,111,216 | 1,419,111,216 | 1,419,111,216 | 2026-09-03 | 2026-09-03 | untried |
| measured heads of length 10 | 2 | 4 | 94 | 134,357,271,610 | 1,429,332,676 | 965,246,055 | 1,093,886,252 | 2026-08-25 | 2026-08-25 | live |
| confirmed-only all-boundary sound cores x uncarried 3-segment sound endings, blkops04 | 1 | 1 | 30 | 44,393,847,979 | 1,479,794,932 | 1,479,794,932 | 1,479,794,932 | 2026-09-01 | 2026-09-01 | untried |
| tw-family terrain grids (tw twcj twck), triples over the full 0..3000 n range | 1 | 2 | 106 | 162,234,108,016 | 1,530,510,452 | 1,448,518,821 | 1,448,518,821 | 2026-10-09 | 2026-10-09 | live |
| cold war sound all-boundary uncarried two-segment endings current | 1 | 1 | 22 | 35,173,151,728 | 1,598,779,624 | 1,598,779,624 | 1,598,779,624 | 2026-09-01 | 2026-09-01 | untried |
| measured heads of length 8 | 2 | 3 | 30 | 48,116,742,888 | 1,603,891,429 | 1,199,252,869 | 1,199,252,869 | 2026-08-25 | 2026-08-25 | live |
| ab snowball r2 visual: old slotswap cores x new endings | 1 | 2 | 2 | 3,229,316,196 | 1,614,658,098 | 1,614,658,098 | 1,614,658,098 | 2026-10-01 | 2026-10-01 | live |
| uncarried one-segment endings over all-boundary cores | 1 | 2 | 316 | 522,511,859,758 | 1,653,518,543 | 1,326,172,232 | 2,195,427,982 | 2026-08-23 | 2026-08-23 | live |
| scoped all-boundary cores x all uncarried 3-segment endings, refreshed lists, 2026-09-04 | 1 | 1 | 82 | 139,188,724,500 | 1,697,423,469 | 1,697,423,469 | 1,697,423,469 | 2026-09-04 | 2026-09-04 | untried |
| sound uncarried two-segment endings top256000 | 1 | 1 | 6 | 10,185,055,660 | 1,697,509,276 | 1,697,509,276 | 1,697,509,276 | 2026-09-09 | 2026-09-09 | untried |
| confirmed-only all-boundary uncarried four-segment sound endings cw | 1 | 1 | 9 | 15,374,753,746 | 1,708,305,971 | 1,708,305,971 | 1,708,305,971 | 2026-09-02 | 2026-09-02 | untried |
| sound uncarried two-segment endings top128000 | 2 | 2 | 9 | 15,464,056,812 | 1,718,228,534 | 1,104,575,486 | 3,866,014,203 | 2026-09-09 | 2026-09-09 | cooling |
| scoped all-boundary cores x all uncarried 2-segment endings, refreshed lists, 2026-09-04 | 1 | 2 | 99 | 172,356,537,460 | 1,740,975,125 | 878,739,411 | 86,240,075,140 | 2026-09-04 | 2026-09-04 | spent |
| cold war sound all-boundary uncarried three-segment endings current | 1 | 1 | 20 | 35,176,151,758 | 1,758,807,587 | 1,758,807,587 | 1,758,807,587 | 2026-09-01 | 2026-09-01 | untried |
| general ceiling-dropped beginnings | 1 | 1 | 24 | 43,531,074,800 | 1,813,794,783 | 1,813,794,783 | 1,813,794,783 | 2026-09-09 | 2026-09-09 | untried |
| scoped all-boundary cores (published+confirmed) x uncarried 2-segment endings, top 300000 | 1 | 3 | 83 | 151,735,705,784 | 1,828,141,033 | 1,097,599,310 | 8,438,228,127 | 2026-09-02 | 2026-09-02 | cooling |
| family walking, whole words | 1 | 77 | 16,801 | 17,397,932,476,760 | 1,984,705,963 | 149,450,943 | 4,187,188,266 | 2026-08-19 | 2026-09-21 | spent |
| scoped all-boundary cores x all uncarried 2-segment endings | 1 | 1 | 41 | 83,095,021,328 | 2,026,707,837 | 2,026,707,837 | 2,026,707,837 | 2026-09-03 | 2026-09-03 | untried |
| ab snowball r1 sound: new cores x every known tail | 1 | 6 | 30 | 61,445,246,358 | 2,048,174,878 | 31,002,204 | 29,111,070,345 | 2026-09-30 | 2026-10-06 | spent |
| measured heads of length 16 | 2 | 4 | 170 | 356,008,257,188 | 2,094,166,218 | 870,303,956 | 29,590,334,512 | 2026-08-25 | 2026-08-25 | spent |
| all-boundary sound cores x 1-segment uncarried sound endings, 2026-09-20 | 1 | 2 | 84 | 177,531,391,422 | 2,113,468,945 | 1,305,377,878 | 1,305,377,878 | 2026-09-20 | 2026-09-20 | live |
| all-boundary sound cores x uncarried sound endings, 1 segment(s), top 300000 | 1 | 2 | 54 | 116,405,048,396 | 2,155,649,044 | 1,662,912,897 | 3,063,320,893 | 2026-08-29 | 2026-08-29 | live |
| first twenty ceiling-dropped cold war sound beginnings | 1 | 1 | 4 | 8,704,378,914 | 2,176,094,728 | 2,176,094,728 | 2,176,094,728 | 2026-08-29 | 2026-08-29 | untried |
| confirmed-only all-boundary uncarried six-segment sound endings bo4 | 1 | 1 | 7 | 15,384,053,839 | 2,197,721,977 | 2,197,721,977 | 2,197,721,977 | 2026-09-02 | 2026-09-02 | untried |
| ab snowball r1 sound: new slotswap cores x all endings | 1 | 7 | 12 | 26,807,968,077 | 2,233,997,339 | 255,602,556 | 2,309,863,098 | 2026-09-29 | 2026-10-06 | cooling |
| sound harvested decorations | 1 | 1 | 21 | 47,049,001,300 | 2,240,428,633 | 2,240,428,633 | 2,240,428,633 | 2026-09-02 | 2026-09-02 | untried |
| cold war uncarried two-segment endings current depth-matched | 1 | 1 | 5 | 11,227,712,276 | 2,245,542,455 | 2,245,542,455 | 2,245,542,455 | 2026-09-01 | 2026-09-01 | untried |
| ab snowball r6 sound: all cores x new name tails | 1 | 1 | 1 | 2,271,469,570 | 2,271,469,570 | 2,271,469,570 | 2,271,469,570 | 2026-10-01 | 2026-10-01 | untried |
| sound alias cores borrowed, sound alias decorations measured | 1 | 6 | 838 | 1,969,209,530,400 | 2,349,892,041 | 69,920,243 | 2,962,280,400 | 2026-08-24 | 2026-08-30 | spent |
| cold war all-boundary uncarried endings current | 1 | 1 | 14 | 33,666,336,660 | 2,404,738,332 | 2,404,738,332 | 2,404,738,332 | 2026-09-01 | 2026-09-01 | untried |
| uncarried endings ranks 3001-6000 over published cores | 1 | 1 | 1 | 2,409,887,028 | 2,409,887,028 | 2,409,887,028 | 2,409,887,028 | 2026-08-26 | 2026-08-26 | untried |
| measured tails of length 40 | 1 | 2 | 40 | 97,801,973,850 | 2,445,049,346 | 1,397,171,055 | 1,397,171,055 | 2026-08-25 | 2026-08-25 | live |
| uncarried endings ranks 6001-9000 over published cores | 1 | 2 | 2 | 4,893,496,622 | 2,446,748,311 | 2,409,887,028 | 2,483,609,594 | 2026-08-26 | 2026-09-03 | live |
| uncarried endings ranks 12001-15000 over published cores | 1 | 1 | 1 | 2,483,609,594 | 2,483,609,594 | 2,483,609,594 | 2,483,609,594 | 2026-09-03 | 2026-09-03 | untried |
| heads of length 3, head-measured alphabet | 1 | 3 | 81 | 201,629,990,289 | 2,489,259,139 | 1,737,854,928 | 4,058,229,717 | 2026-08-23 | 2026-08-27 | live |
| sound all-boundary uncarried one-segment endings current | 1 | 2 | 18 | 45,395,181,202 | 2,521,954,511 | 638,364,337 | 17,590,675,905 | 2026-09-01 | 2026-09-01 | spent |
| sound all-boundary cores with uncarried two-segment endings | 2 | 2 | 13 | 33,006,930,066 | 2,538,994,620 | 2,062,883,128 | 3,300,773,007 | 2026-08-30 | 2026-08-30 | live |
| confirmed-only all-boundary uncarried four-segment sound endings bo4 | 1 | 1 | 6 | 15,374,753,746 | 2,562,458,957 | 2,562,458,957 | 2,562,458,957 | 2026-09-02 | 2026-09-02 | untried |
| measured heads of length 24 | 1 | 2 | 114 | 296,486,731,600 | 2,600,760,803 | 1,629,047,975 | 6,445,363,730 | 2026-08-25 | 2026-08-25 | cooling |
| ab snowball r5 visual: new slotswap cores x all endings | 1 | 2 | 2 | 5,461,518,205 | 2,730,759,102 | 719,702,399 | 4,741,815,806 | 2026-10-01 | 2026-10-05 | cooling |
| sound all-boundary cores with uncarried three-segment endings | 2 | 2 | 12 | 33,009,330,090 | 2,750,777,507 | 2,063,120,631 | 2,063,120,631 | 2026-08-30 | 2026-08-30 | live |
| sound all-boundary cores with uncarried four-segment endings | 1 | 1 | 6 | 16,506,165,060 | 2,751,027,510 | 2,751,027,510 | 2,751,027,510 | 2026-08-30 | 2026-08-30 | untried |
| measured tails of length 8 | 2 | 6 | 271 | 753,428,154,966 | 2,780,177,693 | 1,435,820,931 | 2,357,317,948 | 2026-08-25 | 2026-08-25 | live |
| measured tails of length 4 | 1 | 4 | 69 | 192,512,386,856 | 2,790,034,592 | 1,850,196,005 | 3,210,073,152 | 2026-08-25 | 2026-08-25 | live |
| measured heads of length 28 | 1 | 2 | 92 | 257,912,038,902 | 2,803,391,727 | 2,433,132,442 | 2,433,132,442 | 2026-08-25 | 2026-08-25 | live |
| scoped all-boundary cores (published+confirmed) x uncarried 3-segment endings, top 300000 | 1 | 3 | 54 | 151,763,305,876 | 2,810,431,590 | 1,009,989,366 | 50,638,368,794 | 2026-09-02 | 2026-09-03 | spent |
| all-boundary general cores x top-100k 3-segment uncarried endings, 2026-09-20 | 1 | 2 | 133 | 375,404,754,010 | 2,822,592,135 | 2,040,243,228 | 2,040,243,228 | 2026-09-20 | 2026-09-20 | live |
| cold war sound all-boundary uncarried one-segment endings current | 1 | 2 | 16 | 45,395,181,202 | 2,837,198,825 | 729,559,242 | 17,590,675,905 | 2026-09-01 | 2026-09-01 | spent |
| ab snowball r3 visual: old slotswap cores x new endings | 1 | 2 | 2 | 6,070,227,000 | 3,035,113,500 | 2,949,113,412 | 2,949,113,412 | 2026-10-01 | 2026-10-01 | live |
| blackop7 verified image complete stem pairs crossed with witnessed suffixes | 1 | 1 | 73 | 222,486,555,075 | 3,047,761,028 | 3,047,761,028 | 3,047,761,028 | 2026-10-09 | 2026-10-09 | untried |
| confirmed-only all-boundary uncarried sound endings cw snowball | 1 | 1 | 5 | 15,368,153,680 | 3,073,630,736 | 3,073,630,736 | 3,073,630,736 | 2026-09-02 | 2026-09-02 | untried |
| all-boundary sound cores x top-100k uncarried sound endings, refreshed 2026-09-20 | 1 | 2 | 160 | 505,364,053,590 | 3,158,525,334 | 1,844,394,356 | 1,844,394,356 | 2026-09-20 | 2026-09-20 | live |
| all-boundary sound cores x uncarried sound endings, 2 segment(s), top 200000 | 1 | 4 | 222 | 706,593,023,282 | 3,182,851,456 | 1,889,437,774 | 3,569,271,122 | 2026-08-29 | 2026-09-09 | live |
| ab snowball r6 sound: new slotswap cores x all endings | 1 | 1 | 1 | 3,222,432,224 | 3,222,432,224 | 3,222,432,224 | 3,222,432,224 | 2026-10-01 | 2026-10-01 | untried |
| all-boundary sound cores x uncarried sound endings | 1 | 64 | 1,788 | 6,234,167,318,119 | 3,486,670,759 | 304,356,933 | 59,321,595,135 | 2026-08-25 | 2026-09-01 | spent |
| measured tails of length 28 | 1 | 2 | 57 | 199,395,031,004 | 3,498,158,438 | 1,917,259,913 | 1,917,259,913 | 2026-08-25 | 2026-08-25 | live |
| v2 xanim borrowed endings, ranks 3001-4000 | 1 | 2 | 8 | 28,690,662,000 | 3,586,332,750 | 2,009,436,000 | 14,624,610,000 | 2026-08-28 | 2026-09-01 | cooling |
| all-boundary sound cores x uncarried sound endings, 4 segment(s), top 200000 | 1 | 2 | 21 | 76,315,981,578 | 3,634,094,360 | 3,468,780,980 | 3,815,939,079 | 2026-09-09 | 2026-09-09 | live |
| cold war uncarried two-segment endings | 2 | 3 | 56 | 204,946,704,804 | 3,659,762,585 | 33,648,412 | 33,648,412 | 2026-08-26 | 2026-08-31 | live |
| scoped all-boundary sound cores x all uncarried 2-segment sound endings, refreshed lists, 2026-09-04 | 1 | 1 | 8 | 29,638,797,165 | 3,704,849,645 | 3,704,849,645 | 3,704,849,645 | 2026-09-04 | 2026-09-04 | untried |
| measured tails of length 32 | 1 | 2 | 46 | 178,589,946,540 | 3,882,390,142 | 2,289,614,699 | 2,289,614,699 | 2026-08-25 | 2026-08-25 | live |
| rule-substituted all-boundary endings, visual | 1 | 2 | 4 | 15,634,952,992 | 3,908,738,248 | 3,908,738,248 | 3,908,738,248 | 2026-09-26 | 2026-09-26 | live |
| measured heads of length 56 | 1 | 2 | 3 | 12,027,546,336 | 4,009,182,112 | 3,006,886,584 | 3,006,886,584 | 2026-08-25 | 2026-08-25 | live |
| slotswap-substituted all-boundary cores, visual, delta 2026-09-29 | 1 | 2 | 6 | 24,946,883,156 | 4,157,813,859 | 4,157,813,859 | 4,157,813,859 | 2026-09-29 | 2026-09-29 | live |
| measured tails of length 9 | 1 | 2 | 64 | 266,568,581,576 | 4,165,134,087 | 3,920,126,199 | 4,442,809,692 | 2026-08-25 | 2026-08-25 | live |
| scoped all-boundary cores (published+confirmed) x uncarried 4-segment endings, top 300000 | 1 | 1 | 12 | 50,524,368,414 | 4,210,364,034 | 4,210,364,034 | 4,210,364,034 | 2026-09-02 | 2026-09-02 | untried |
| all-boundary sound cores x uncarried sound endings, 3 segment(s), top 200000, blkops04 | 1 | 1 | 8 | 34,537,372,686 | 4,317,171,585 | 4,317,171,585 | 4,317,171,585 | 2026-09-01 | 2026-09-01 | untried |
| general beginnings the 700 ceiling drops | 1 | 8 | 103 | 453,678,445,820 | 4,404,645,105 | 177,450,092 | 588,650,610 | 2026-08-29 | 2026-09-03 | cooling |
| ab snowball r4 visual: all cores x new name tails | 1 | 1 | 4 | 17,679,454,619 | 4,419,863,654 | 4,419,863,654 | 4,419,863,654 | 2026-10-05 | 2026-10-05 | untried |
| packed twc/tw codes, second of four slots over every number | 1 | 4 | 1,604 | 7,095,515,214,404 | 4,423,637,914 | 1,404,348,606 | 114,126,638,454 | 2026-10-09 | 2026-10-09 | spent |
| uncarried two-segment endings | 1 | 1 | 23 | 102,361,883,258 | 4,450,516,663 | 4,450,516,663 | 4,450,516,663 | 2026-08-26 | 2026-08-26 | untried |
| uncarried endings ranks 60001-120000 over published cores | 1 | 2 | 21 | 95,849,557,466 | 4,564,264,641 | 2,995,298,670 | 9,584,955,746 | 2026-08-23 | 2026-08-23 | cooling |
| sound ceiling-dropped beginnings | 1 | 1 | 5 | 23,995,372,275 | 4,799,074,455 | 4,799,074,455 | 4,799,074,455 | 2026-09-09 | 2026-09-09 | untried |
| all-boundary cores x confirmed-only-discovered 1-segment endings (general), 2026-09-22 | 1 | 1 | 1 | 4,837,572,675 | 4,837,572,675 | 4,837,572,675 | 4,837,572,675 | 2026-09-22 | 2026-09-22 | untried |
| measured tails of length 5 | 2 | 8 | 105 | 533,600,850,606 | 5,081,912,862 | 2,214,417,335 | 4,556,006,356 | 2026-08-25 | 2026-08-25 | live |
| confirmed-only all-boundary uncarried five-segment sound endings cw | 1 | 1 | 3 | 15,379,053,789 | 5,126,351,263 | 5,126,351,263 | 5,126,351,263 | 2026-09-02 | 2026-09-02 | untried |
| measured tails of length 7 | 1 | 3 | 51 | 262,284,435,218 | 5,142,832,063 | 3,013,818,603 | 12,497,565,171 | 2026-08-25 | 2026-08-25 | cooling |
| core ring 20260915-20260924 x all tails | 1 | 2 | 6 | 30,864,257,112 | 5,144,042,852 | 5,144,042,852 | 5,144,042,852 | 2026-09-30 | 2026-09-30 | live |
| measured tails of length 10 | 2 | 7 | 262 | 1,357,535,317,614 | 5,181,432,509 | 2,868,533,268 | 11,751,144,491 | 2026-08-25 | 2026-08-25 | cooling |
| all-boundary cores x confirmed-only-discovered endings (general), 2026-09-22 | 1 | 2 | 14 | 73,282,859,660 | 5,234,489,975 | 3,331,039,075 | 3,331,039,075 | 2026-09-22 | 2026-09-22 | live |
| cross-title ceiling-dropped sound beginnings | 1 | 1 | 12 | 64,376,209,800 | 5,364,684,150 | 5,364,684,150 | 5,364,684,150 | 2026-09-09 | 2026-09-09 | untried |
| all-boundary sound cores x uncarried sound endings, 2 segments | 1 | 1 | 37 | 198,601,685,997 | 5,367,613,135 | 5,367,613,135 | 5,367,613,135 | 2026-08-23 | 2026-08-23 | untried |
| all-boundary cores x confirmed-only-discovered 3-segment endings (general), 2026-09-22 | 1 | 2 | 22 | 118,250,103,816 | 5,375,004,718 | 3,477,944,229 | 3,477,944,229 | 2026-09-22 | 2026-09-22 | live |
| ab snowball r4 sound: new cores x every known tail | 1 | 2 | 7 | 38,467,723,626 | 5,495,389,089 | 645,992,250 | 6,303,621,896 | 2026-10-01 | 2026-10-05 | cooling |
| xanim cores borrowed, xanim decorations measured | 1 | 14 | 391 | 2,379,936,774,200 | 6,086,794,818 | 26,167,942 | 50,169,424,421 | 2026-08-24 | 2026-08-31 | spent |
| measured heads of length 14 | 1 | 2 | 15 | 92,163,619,882 | 6,144,241,325 | 5,760,226,242 | 6,583,115,705 | 2026-08-25 | 2026-08-25 | live |
| all-boundary cores x uncarried endings, 2 segment(s), top 300000 | 1 | 3 | 257 | 1,627,767,625,874 | 6,333,726,170 | 2,467,636,992 | 21,036,254,736 | 2026-08-29 | 2026-09-09 | cooling |
| confirmed-only all-boundary sound cores x uncarried 5-segment sound endings, blkops04 | 1 | 1 | 7 | 44,441,848,139 | 6,348,835,448 | 6,348,835,448 | 6,348,835,448 | 2026-09-02 | 2026-09-02 | untried |
| current uncarried two-segment endings | 1 | 1 | 2 | 12,744,671,401 | 6,372,335,700 | 6,372,335,700 | 6,372,335,700 | 2026-09-08 | 2026-09-08 | untried |
| all-boundary cores x uncarried endings | 1 | 86 | 2,248 | 14,391,837,192,458 | 6,402,062,808 | 219,308,075 | 90,475,954,750 | 2026-08-25 | 2026-09-01 | spent |
| all-boundary general cores x top-100k 1-segment uncarried endings, 2026-09-20 | 1 | 2 | 58 | 375,434,154,304 | 6,473,002,660 | 4,171,490,603 | 4,171,490,603 | 2026-09-20 | 2026-09-20 | live |
| measured tails of length 6 | 2 | 7 | 91 | 628,969,016,333 | 6,911,747,432 | 1,977,717,171 | 9,578,231,709 | 2026-08-25 | 2026-08-25 | cooling |
| build strings under measured decorations | 1 | 3 | 152 | 1,074,926,265,000 | 7,071,883,322 | 853,253,716 | 853,253,716 | 2026-08-24 | 2026-09-02 | live |
| measured tails of length 16 | 2 | 4 | 137 | 972,904,993,300 | 7,101,496,301 | 3,833,611,586 | 6,380,104,314 | 2026-08-25 | 2026-08-25 | live |
| confirmed-only all-boundary bo4 sound cores x uncarried endings | 1 | 1 | 2 | 14,335,743,356 | 7,167,871,678 | 7,167,871,678 | 7,167,871,678 | 2026-08-29 | 2026-08-29 | untried |
| all-boundary cores x uncarried endings, 2 segment(s), top 100000 | 1 | 5 | 77 | 552,927,929,224 | 7,180,882,197 | 311,036,443 | 9,114,946,148 | 2026-08-31 | 2026-09-09 | spent |
| measured tails of length 18 | 1 | 2 | 51 | 370,685,626,016 | 7,268,345,608 | 5,451,259,206 | 10,902,518,412 | 2026-08-25 | 2026-08-25 | live |
| core ring 20260901-20260914 x all tails | 1 | 2 | 7 | 51,607,375,144 | 7,372,482,163 | 6,450,921,893 | 8,601,229,190 | 2026-09-30 | 2026-09-30 | live |
| confirmed-only all-boundary sound cores x uncarried 4-segment sound endings, blkops04 | 1 | 1 | 6 | 44,437,348,124 | 7,406,224,687 | 7,406,224,687 | 7,406,224,687 | 2026-09-02 | 2026-09-02 | untried |
| uncarried two-segment endings current depth-matched | 1 | 2 | 3 | 22,455,424,552 | 7,485,141,517 | 5,613,856,138 | 5,613,856,138 | 2026-09-01 | 2026-09-01 | live |
| scoped all-boundary cores (published+confirmed) x uncarried 1-segment endings | 1 | 1 | 4 | 30,324,661,319 | 7,581,165,329 | 7,581,165,329 | 7,581,165,329 | 2026-09-02 | 2026-09-02 | untried |
| cold war confirmed-only all-boundary uncarried endings current | 1 | 1 | 1 | 7,600,476,004 | 7,600,476,004 | 7,600,476,004 | 7,600,476,004 | 2026-09-01 | 2026-09-01 | untried |
| all-boundary sound cores x uncarried sound endings, 5 segment(s), top 100000 | 1 | 2 | 5 | 38,165,181,648 | 7,633,036,329 | 6,360,930,275 | 6,360,930,275 | 2026-09-09 | 2026-09-09 | live |
| all-boundary general cores x top-300k 2-segment uncarried endings, 2026-09-20 | 1 | 2 | 147 | 1,126,389,154,618 | 7,662,511,255 | 4,732,727,540 | 4,732,727,540 | 2026-09-20 | 2026-09-20 | live |
| confirmed-only all-boundary uncarried six-segment sound endings cw | 1 | 1 | 2 | 15,384,053,839 | 7,692,026,919 | 7,692,026,919 | 7,692,026,919 | 2026-09-02 | 2026-09-02 | untried |
| confirmed-only all-boundary uncarried seven-segment sound endings cw | 1 | 1 | 2 | 15,387,853,877 | 7,693,926,938 | 7,693,926,938 | 7,693,926,938 | 2026-09-02 | 2026-09-02 | untried |
| measured tails of length 14 | 2 | 5 | 165 | 1,278,003,497,385 | 7,745,475,741 | 3,983,905,894 | 96,886,917,891 | 2026-08-25 | 2026-08-25 | spent |
| current uncarried three-segment endings | 1 | 1 | 1 | 7,781,927,881 | 7,781,927,881 | 7,781,927,881 | 7,781,927,881 | 2026-09-08 | 2026-09-08 | untried |
| xanim cores under borrowed xanim endings | 1 | 4 | 55 | 432,450,304,500 | 7,862,732,809 | 3,978,275,000 | 21,734,716,500 | 2026-08-24 | 2026-08-25 | cooling |
| purely self-referential all-boundary sound cores x confirmed-only sound endings, 2026-09-24 | 1 | 2 | 6 | 47,769,933,152 | 7,961,655,525 | 5,971,241,644 | 11,942,483,288 | 2026-09-24 | 2026-09-24 | live |
| measured tails of length 12 | 2 | 8 | 190 | 1,547,737,441,906 | 8,145,986,536 | 477,783,178 | 477,783,178 | 2026-08-25 | 2026-08-25 | live |
| all-boundary sound cores x uncarried sound endings, 3 segments, top 200k | 1 | 1 | 49 | 406,230,831,144 | 8,290,425,125 | 8,290,425,125 | 8,290,425,125 | 2026-08-29 | 2026-08-29 | untried |
| all-boundary sound cores x confirmed-only-discovered sound endings, 2026-09-22 | 1 | 2 | 37 | 308,172,375,252 | 8,328,983,114 | 4,531,946,694 | 51,362,062,542 | 2026-09-22 | 2026-09-22 | spent |
| vox alias grid, slots composed rather than redistributed | 1 | 1 | 184 | 1,585,821,032,397 | 8,618,592,567 | 8,618,592,567 | 8,618,592,567 | 2026-08-23 | 2026-08-23 | untried |
| all-boundary sound cores x uncarried sound endings, 4 segments, top 300k | 1 | 1 | 66 | 609,361,431,198 | 9,232,748,957 | 9,232,748,957 | 9,232,748,957 | 2026-08-29 | 2026-08-29 | untried |
| material cores borrowed, material decorations measured | 1 | 15 | 496 | 4,606,530,586,700 | 9,287,360,053 | 333,052,312 | 60,987,886,400 | 2026-08-24 | 2026-08-31 | spent |
| measured tails of length 20 | 2 | 4 | 85 | 820,774,633,936 | 9,656,172,163 | 6,347,905,763 | 11,151,898,505 | 2026-08-25 | 2026-08-25 | live |
| measured tails of length 13 | 1 | 2 | 40 | 398,901,306,104 | 9,972,532,652 | 8,671,767,524 | 8,671,767,524 | 2026-08-25 | 2026-08-25 | live |
| black ops 1 build vocabulary | 1 | 2 | 204 | 2,038,307,570,080 | 9,991,703,774 | 6,575,185,709 | 20,799,056,837 | 2026-08-22 | 2026-08-22 | cooling |
| all-boundary cores x uncarried endings, 3 segment(s), top 300000 | 1 | 3 | 159 | 1,634,381,747,921 | 10,279,130,490 | 3,702,088,367 | 136,735,205,782 | 2026-08-29 | 2026-09-09 | spent |
| all-boundary sound cores x uncarried sound endings, 4 segment(s), top 300000, blkops04 | 1 | 1 | 5 | 51,912,773,042 | 10,382,554,608 | 10,382,554,608 | 10,382,554,608 | 2026-09-01 | 2026-09-01 | untried |
| measured tails of length 11 | 1 | 2 | 33 | 346,197,974,320 | 10,490,847,706 | 9,110,473,008 | 9,110,473,008 | 2026-08-25 | 2026-08-25 | live |
| all-boundary sound cores x top-100k 3-segment uncarried sound endings, 2026-09-20 | 1 | 2 | 48 | 505,505,655,006 | 10,531,367,812 | 6,651,390,197 | 6,651,390,197 | 2026-09-20 | 2026-09-20 | live |
| v2 sound alias borrowed endings, ranks 16001-19155 | 1 | 2 | 13 | 138,052,908,000 | 10,619,454,461 | 6,275,132,181 | 34,513,227,000 | 2026-08-28 | 2026-08-28 | cooling |
| all-boundary sound cores x uncarried sound endings, 2 segment(s), top 300000 | 1 | 2 | 6 | 64,249,519,095 | 10,708,253,182 | 6,424,856,670 | 32,125,235,745 | 2026-09-09 | 2026-09-09 | cooling |
| all-boundary general cores x top-100k uncarried endings, after +18k merge, 2026-09-25 | 1 | 2 | 35 | 377,821,978,182 | 10,794,913,662 | 7,556,439,563 | 7,556,439,563 | 2026-09-25 | 2026-09-25 | live |
| cold war all-boundary uncarried three-segment endings current | 1 | 1 | 3 | 33,677,936,776 | 11,225,978,925 | 11,225,978,925 | 11,225,978,925 | 2026-09-01 | 2026-09-01 | untried |
| rule-substituted all-boundary cores, visual | 1 | 1 | 4 | 45,099,750,332 | 11,274,937,583 | 11,274,937,583 | 11,274,937,583 | 2026-09-25 | 2026-09-25 | untried |
| scoped all-boundary cores x all uncarried 4-segment endings | 1 | 2 | 29 | 329,909,647,446 | 11,376,194,739 | 6,474,622,101 | 42,011,023,725 | 2026-09-03 | 2026-09-04 | cooling |
| measured tails of length 24 | 2 | 4 | 54 | 627,132,483,832 | 11,613,564,515 | 3,309,040,403 | 64,813,595,798 | 2026-08-25 | 2026-08-25 | spent |
| all-boundary cores x confirmed-only-discovered 4-segment endings (general), 2026-09-22 | 1 | 1 | 6 | 71,364,999,303 | 11,894,166,550 | 11,894,166,550 | 11,894,166,550 | 2026-09-22 | 2026-09-22 | untried |
| image cores borrowed, image decorations measured | 1 | 14 | 868 | 10,326,616,706,000 | 11,897,023,854 | 1,015,745,750 | 39,462,327,692 | 2026-08-24 | 2026-08-31 | spent |
| sound uncarried three-segment endings top512000 | 2 | 2 | 2 | 23,897,249,316 | 11,948,624,658 | 11,948,624,658 | 11,948,624,658 | 2026-09-09 | 2026-09-09 | live |
| xmodel cores borrowed, xmodel decorations measured | 1 | 11 | 101 | 1,233,339,419,100 | 12,211,281,377 | 145,020,750 | 91,535,164,000 | 2026-08-24 | 2026-08-31 | spent |
| all-boundary sound cores x uncarried sound endings, 3 segment(s), top 200000 | 1 | 4 | 72 | 888,824,644,101 | 12,344,786,723 | 4,238,398,969 | 4,768,423,842 | 2026-08-29 | 2026-09-09 | live |
| measured heads of length 20 | 2 | 4 | 36 | 456,964,818,448 | 12,693,467,179 | 6,682,647,252 | 21,184,377,456 | 2026-08-25 | 2026-08-25 | cooling |
| all-boundary sound cores x uncarried sound endings, 5 segment(s), top 200000 | 1 | 2 | 6 | 76,333,181,664 | 12,722,196,944 | 7,633,238,166 | 38,166,990,834 | 2026-09-09 | 2026-09-09 | cooling |
| all-boundary sound cores x uncarried sound endings, 5 segment(s), top 300000, blkops04 | 1 | 1 | 4 | 51,978,173,260 | 12,994,543,315 | 12,994,543,315 | 12,994,543,315 | 2026-09-01 | 2026-09-01 | untried |
| head of one name, tail of another | 1 | 2 | 7 | 96,000,800,000 | 13,714,400,000 | 8,000,066,666 | 8,000,066,666 | 2026-08-22 | 2026-08-22 | live |
| v2 xanim borrowed endings, ranks 5001-6000 | 1 | 1 | 1 | 14,078,064,000 | 14,078,064,000 | 14,078,064,000 | 14,078,064,000 | 2026-08-28 | 2026-08-28 | untried |
| v2 xanim borrowed endings, ranks 6001-7000 | 1 | 2 | 2 | 28,171,143,000 | 14,085,571,500 | 14,085,571,500 | 14,085,571,500 | 2026-08-28 | 2026-08-28 | live |
| all-boundary sound cores x uncarried sound endings, 3 segment(s), top 300000 | 1 | 1 | 4 | 57,223,690,745 | 14,305,922,686 | 14,305,922,686 | 14,305,922,686 | 2026-09-09 | 2026-09-09 | untried |
| all-boundary cores x uncarried endings, 4 segment(s), top 300000 | 1 | 2 | 75 | 1,087,517,125,045 | 14,500,228,333 | 7,507,820,859 | 182,318,007,724 | 2026-08-29 | 2026-09-09 | spent |
| blackop6 images from frozen verified modern-image pairs witnessed in bo7 | 1 | 1 | 15 | 222,486,555,075 | 14,832,437,005 | 14,832,437,005 | 14,832,437,005 | 2026-10-09 | 2026-10-09 | untried |
| sound ceiling-dropped beginnings over current all-boundary cores 20260830 | 1 | 1 | 28 | 450,263,412,045 | 16,080,836,144 | 16,080,836,144 | 16,080,836,144 | 2026-08-30 | 2026-08-30 | untried |
| measured shells, head 6 tail 6, top 600 | 1 | 1 | 12 | 194,426,913,079 | 16,202,242,756 | 16,202,242,756 | 16,202,242,756 | 2026-09-04 | 2026-09-04 | untried |
| all-boundary uncarried four-segment endings current | 1 | 1 | 2 | 33,678,536,782 | 16,839,268,391 | 16,839,268,391 | 16,839,268,391 | 2026-09-01 | 2026-09-01 | untried |
| xmodel cores borrowed wide, stripped shallow | 1 | 1 | 1 | 17,342,167,500 | 17,342,167,500 | 17,342,167,500 | 17,342,167,500 | 2026-08-24 | 2026-08-24 | untried |
| material cores borrowed wide, stripped shallow | 1 | 2 | 6 | 106,477,308,000 | 17,746,218,000 | 13,309,663,500 | 13,309,663,500 | 2026-08-24 | 2026-08-24 | live |
| modern visual verified full-corpus tails of length 4 | 1 | 1 | 95 | 1,727,070,269,592 | 18,179,687,048 | 18,179,687,048 | 18,179,687,048 | 2026-10-08 | 2026-10-08 | untried |
| all-boundary sound cores x uncarried sound endings, 4 segment(s), top 300000 | 1 | 3 | 39 | 719,488,798,288 | 18,448,430,725 | 4,393,314,644 | 9,540,731,802 | 2026-08-29 | 2026-09-09 | live |
| measured tails of length 15 | 1 | 2 | 22 | 406,264,584,852 | 18,466,572,038 | 11,948,958,378 | 40,626,458,485 | 2026-08-25 | 2026-08-25 | cooling |
| all-boundary sound cores x all 187k uncarried sound endings, 2026-09-20b | 1 | 2 | 51 | 945,903,699,378 | 18,547,131,360 | 12,446,101,307 | 12,446,101,307 | 2026-09-21 | 2026-09-21 | live |
| all-boundary cores x uncarried endings, 2 segment(s), top 150000 | 1 | 2 | 28 | 546,903,345,998 | 19,532,262,357 | 16,085,392,529 | 24,859,242,999 | 2026-09-09 | 2026-09-09 | live |
| all-boundary sound cores x top-100k uncarried sound endings, after +18k merge, 2026-09-25 | 1 | 2 | 26 | 509,470,494,654 | 19,595,019,025 | 15,920,952,957 | 15,920,952,957 | 2026-09-25 | 2026-09-25 | live |
| all-boundary sound cores x confirmed-only-discovered 1-segment sound endings, 2026-09-22 | 1 | 2 | 3 | 58,864,563,696 | 19,621,521,232 | 14,716,140,924 | 29,432,281,848 | 2026-09-22 | 2026-09-22 | live |
| slotswap-substituted all-boundary cores, sound, slices 5-8 | 1 | 1 | 76 | 1,511,869,118,540 | 19,893,014,717 | 19,893,014,717 | 19,893,014,717 | 2026-09-28 | 2026-09-28 | untried |
| scoped all-boundary cores x all uncarried 5-segment endings | 1 | 1 | 8 | 163,703,135,601 | 20,462,891,950 | 20,462,891,950 | 20,462,891,950 | 2026-09-03 | 2026-09-03 | untried |
| harvested strings, tails of length 3 | 1 | 1 | 4 | 86,898,811,198 | 21,724,702,799 | 21,724,702,799 | 21,724,702,799 | 2026-08-24 | 2026-08-24 | untried |
| all-boundary sound cores x confirmed-only-discovered 3-segment sound endings, 2026-09-22 | 1 | 2 | 23 | 506,393,663,886 | 22,017,115,821 | 21,099,735,995 | 23,017,893,813 | 2026-09-22 | 2026-09-22 | live |
| all-boundary general cores x top-100k 4-segment uncarried endings, 2026-09-20 | 1 | 2 | 16 | 375,435,754,320 | 23,464,734,645 | 14,439,836,704 | 14,439,836,704 | 2026-09-20 | 2026-09-20 | live |
| scoped all-boundary cores x all uncarried 6-segment endings | 1 | 1 | 6 | 144,551,713,541 | 24,091,952,256 | 24,091,952,256 | 24,091,952,256 | 2026-09-03 | 2026-09-03 | untried |
| all-boundary cores x uncarried endings, 3 segment(s), top 100000 | 1 | 2 | 15 | 364,606,846,032 | 24,307,123,068 | 15,191,951,918 | 15,191,951,918 | 2026-09-09 | 2026-09-09 | live |
| black ops 3 build vocabulary | 1 | 2 | 293 | 7,358,148,299,220 | 25,113,134,127 | 15,655,634,679 | 63,432,312,924 | 2026-08-22 | 2026-08-22 | cooling |
| harvested strings, heads of length 3 | 1 | 3 | 10 | 253,271,342,362 | 25,327,134,236 | 192,093,060 | 192,093,060 | 2026-08-24 | 2026-09-02 | live |
| all-boundary cores x uncarried endings, 3 segment(s), top 200000 | 1 | 2 | 28 | 729,219,246,078 | 26,043,544,502 | 24,307,308,202 | 28,046,894,079 | 2026-09-09 | 2026-09-09 | live |
| all-boundary cores x uncarried endings, 5 segment(s), top 100000 | 1 | 1 | 7 | 182,310,923,091 | 26,044,417,584 | 26,044,417,584 | 26,044,417,584 | 2026-09-09 | 2026-09-09 | untried |
| uncarried beginnings slice 0-26 | 1 | 1 | 1 | 26,086,235,266 | 26,086,235,266 | 26,086,235,266 | 26,086,235,266 | 2026-08-28 | 2026-08-28 | untried |
| rule-substituted all-boundary endings, sound | 1 | 1 | 18 | 475,079,032,827 | 26,393,279,601 | 26,393,279,601 | 26,393,279,601 | 2026-09-26 | 2026-09-26 | untried |
| all-boundary cores x uncarried endings, 4 segment(s), top 100000 | 1 | 2 | 7 | 186,050,560,487 | 26,578,651,498 | 1,870,318,703 | 36,461,984,616 | 2026-09-02 | 2026-09-09 | spent |
| images derived from materials | 1 | 23 | 6,555 | 34,890,725,561,940 | 26,777,226,064 | 13,498,822,351 | 47,834,576,565 | 2026-08-19 | 2026-09-10 | cooling |
| all-boundary sound cores x top-100k 4-segment uncarried sound endings, 2026-09-20 | 1 | 2 | 18 | 505,520,655,156 | 28,084,480,842 | 15,797,520,473 | 15,797,520,473 | 2026-09-20 | 2026-09-20 | live |
| confirmed-only sound all-boundary uncarried endings current | 1 | 1 | 1 | 30,069,300,690 | 30,069,300,690 | 30,069,300,690 | 30,069,300,690 | 2026-09-01 | 2026-09-01 | untried |
| slotswap sound cores shared with the visual list, slices 2-8, x sound endings | 1 | 1 | 14 | 461,196,811,922 | 32,942,629,423 | 32,942,629,423 | 32,942,629,423 | 2026-09-30 | 2026-09-30 | untried |
| sound beginnings the 700 ceiling drops | 1 | 14 | 219 | 7,418,556,758,288 | 33,874,688,394 | 1,235,117,520 | 478,682,361,787 | 2026-08-29 | 2026-09-20 | spent |
| v2 material borrowed endings, ranks 1001-2000 | 1 | 2 | 12 | 426,823,897,500 | 35,568,658,125 | 23,561,037,500 | 71,591,520,000 | 2026-08-25 | 2026-08-28 | cooling |
| all-boundary sound cores x confirmed-only-discovered 4-segment sound endings, 2026-09-22 | 1 | 2 | 14 | 506,410,464,054 | 36,172,176,003 | 23,018,657,457 | 23,018,657,457 | 2026-09-22 | 2026-09-22 | live |
| all-boundary sound cores x uncarried sound endings, 5 segment(s), top 300000 | 1 | 2 | 18 | 662,121,707,065 | 36,784,539,281 | 35,846,695,959 | 52,727,875,759 | 2026-08-29 | 2026-08-31 | live |
| v2 xanim borrowed endings, ranks 16001-24000 | 1 | 2 | 6 | 221,211,648,000 | 36,868,608,000 | 28,137,516,750 | 28,137,516,750 | 2026-08-25 | 2026-08-28 | live |
| xmodel cores under borrowed xmodel endings | 1 | 2 | 71 | 2,638,444,407,000 | 37,161,188,830 | 29,316,048,966 | 50,739,315,519 | 2026-08-24 | 2026-08-24 | live |
| dotted sound basenames, last 3 characters replaced, modwar22 tails | 1 | 1 | 9 | 344,520,026,516 | 38,280,002,946 | 38,280,002,946 | 38,280,002,946 | 2026-10-09 | 2026-10-09 | untried |
| uncarried beginnings | 1 | 18 | 121 | 4,685,401,723,688 | 38,722,328,294 | 6,897,183,362 | 42,547,681,320 | 2026-08-23 | 2026-09-08 | cooling |
| uncarried beginnings, optics and prefixed families | 1 | 2 | 7 | 271,475,197,760 | 38,782,171,108 | 27,147,519,776 | 67,868,799,440 | 2026-08-22 | 2026-08-22 | live |
| slotswap-substituted all-boundary cores, visual, slices 2-8 | 1 | 1 | 235 | 9,191,496,338,219 | 39,112,750,375 | 39,112,750,375 | 39,112,750,375 | 2026-09-28 | 2026-09-28 | untried |
| image cores borrowed wide, stripped shallow | 1 | 2 | 6 | 243,078,381,000 | 40,513,063,500 | 30,384,797,625 | 30,384,797,625 | 2026-08-24 | 2026-08-24 | live |
| all-boundary general cores x top-100k uncarried endings, refresh 2026-09-25 | 1 | 2 | 9 | 375,974,959,712 | 41,774,995,523 | 37,597,495,971 | 46,996,869,964 | 2026-09-24 | 2026-09-24 | live |
| all-boundary general cores x top-300k 3-segment uncarried endings, 2026-09-20b | 1 | 2 | 26 | 1,126,471,954,894 | 43,325,844,419 | 31,290,887,635 | 31,290,887,635 | 2026-09-21 | 2026-09-21 | live |
| v2 xanim borrowed endings, ranks 24001-32000 | 1 | 2 | 5 | 219,351,415,500 | 43,870,283,100 | 36,644,580,000 | 36,644,580,000 | 2026-08-26 | 2026-08-26 | live |
| all-boundary cores x uncarried three-segment endings, black ops 4 | 1 | 1 | 4 | 177,157,271,555 | 44,289,317,888 | 44,289,317,888 | 44,289,317,888 | 2026-08-29 | 2026-08-29 | untried |
| all-boundary cores x uncarried endings, 2 segment(s), top 200000 | 1 | 1 | 8 | 364,624,023,111 | 45,578,002,888 | 45,578,002,888 | 45,578,002,888 | 2026-09-09 | 2026-09-09 | untried |
| tails of length 4 | 1 | 25 | 658 | 30,689,202,911,832 | 46,640,126,005 | 5,032,108,457 | 66,730,608,959 | 2026-08-22 | 2026-09-14 | spent |
| rule-substituted all-boundary endings, sound, unfolded | 1 | 1 | 10 | 475,079,032,827 | 47,507,903,282 | 47,507,903,282 | 47,507,903,282 | 2026-09-27 | 2026-09-27 | untried |
| v2 material borrowed endings, ranks 6001-7000 | 1 | 3 | 13 | 644,194,551,000 | 49,553,427,000 | 26,853,389,062 | 26,853,389,062 | 2026-08-27 | 2026-08-28 | live |
| v2 material borrowed endings, ranks 9001-10000 | 1 | 3 | 13 | 644,377,734,000 | 49,567,518,000 | 30,670,926,000 | 107,420,313,000 | 2026-08-27 | 2026-08-28 | cooling |
| v2 material borrowed endings, ranks 5001-6000 | 1 | 4 | 17 | 856,345,990,500 | 50,373,293,558 | 35,804,268,500 | 107,412,805,500 | 2026-08-25 | 2026-08-28 | live |
| all-boundary sound cores x top-100k 5-segment uncarried sound endings, refresh 2026-09-24 | 1 | 1 | 5 | 253,363,633,611 | 50,672,726,722 | 50,672,726,722 | 50,672,726,722 | 2026-09-24 | 2026-09-24 | untried |
| heads of length 4, slash-bearing beginnings | 1 | 5 | 19 | 1,002,949,411,050 | 52,786,811,107 | 24,929,570,784 | 101,225,594,025 | 2026-08-24 | 2026-08-27 | cooling |
| v2 xanim borrowed endings, ranks 48001-56000 | 1 | 1 | 2 | 110,209,774,500 | 55,104,887,250 | 55,104,887,250 | 55,104,887,250 | 2026-08-26 | 2026-08-26 | untried |
| v2 material borrowed endings, ranks 2001-3000 | 1 | 4 | 15 | 856,342,987,500 | 57,089,532,500 | 21,198,927,750 | 71,614,042,500 | 2026-08-25 | 2026-08-28 | cooling |
| v2 material borrowed endings, ranks 7001-8000 | 1 | 3 | 11 | 644,394,250,500 | 58,581,295,500 | 30,693,234,000 | 214,852,638,000 | 2026-08-27 | 2026-08-28 | cooling |
| all-boundary cores x uncarried endings, 4 segment(s), top 200000 | 1 | 1 | 6 | 364,632,423,153 | 60,772,070,525 | 60,772,070,525 | 60,772,070,525 | 2026-09-09 | 2026-09-09 | untried |
| confirmed-only sound endings x cores, after +18k merge, 2026-09-25 | 1 | 1 | 3 | 186,860,385,789 | 62,286,795,263 | 62,286,795,263 | 62,286,795,263 | 2026-09-25 | 2026-09-25 | untried |
| material cores under borrowed material endings | 1 | 4 | 128 | 8,470,420,821,000 | 66,175,162,664 | 35,223,652,406 | 101,779,003,800 | 2026-08-24 | 2026-08-24 | live |
| slotswap-substituted all-boundary cores, visual | 1 | 1 | 151 | 10,504,567,415,108 | 69,566,671,623 | 69,566,671,623 | 69,566,671,623 | 2026-09-29 | 2026-09-29 | untried |
| all-boundary general cores x top-300k uncarried endings, after +18k merge, 2026-09-25 | 1 | 2 | 14 | 1,133,518,978,384 | 80,965,641,313 | 47,229,957,432 | 283,379,744,596 | 2026-09-25 | 2026-09-25 | cooling |
| ceiling-dropped sound beginnings over current sound cores | 1 | 1 | 1 | 81,366,616,800 | 81,366,616,800 | 81,366,616,800 | 81,366,616,800 | 2026-09-01 | 2026-09-01 | untried |
| v2 sound alias borrowed endings, ranks 8001-16000 | 1 | 2 | 4 | 334,133,761,500 | 83,533,440,375 | 57,019,126,500 | 57,019,126,500 | 2026-08-25 | 2026-08-26 | live |
| v2 material borrowed endings, ranks 4001-5000 | 1 | 4 | 10 | 856,398,543,000 | 85,639,854,300 | 42,934,791,900 | 214,842,127,500 | 2026-08-25 | 2026-08-28 | cooling |
| tails of length 5 | 1 | 5 | 729 | 62,471,271,397,845 | 85,694,473,796 | 10,653,467,440 | 723,042,398,138 | 2026-08-22 | 2026-08-25 | spent |
| all-boundary general cores x top-100k 5-segment uncarried endings, refresh 2026-09-24 | 1 | 1 | 2 | 187,988,279,864 | 93,994,139,932 | 93,994,139,932 | 93,994,139,932 | 2026-09-24 | 2026-09-24 | untried |
| sound beginnings the 700 ceiling drops, over all-boundary sound cores | 1 | 1 | 9 | 884,193,668,358 | 98,243,740,928 | 98,243,740,928 | 98,243,740,928 | 2026-08-29 | 2026-08-29 | untried |
| v2 material borrowed endings, ranks 3001-4000 | 1 | 3 | 6 | 641,527,887,000 | 106,921,314,500 | 106,007,401,500 | 107,421,063,750 | 2026-08-25 | 2026-08-28 | live |
| v2 sound alias borrowed endings, ranks 1-8000 | 1 | 2 | 3 | 325,972,741,500 | 108,657,580,500 | 81,460,181,250 | 163,052,379,000 | 2026-08-25 | 2026-08-25 | live |
| v2 xanim borrowed endings, ranks 56001-64000 | 1 | 1 | 1 | 109,885,734,000 | 109,885,734,000 | 109,885,734,000 | 109,885,734,000 | 2026-08-26 | 2026-08-26 | untried |
| v2 xanim borrowed endings, ranks 72001-80000 | 1 | 2 | 2 | 221,415,673,500 | 110,707,836,750 | 108,865,606,500 | 112,550,067,000 | 2026-08-25 | 2026-08-28 | live |
| rule-substituted all-boundary cores, sound | 1 | 1 | 26 | 2,893,174,431,455 | 111,275,939,671 | 111,275,939,671 | 111,275,939,671 | 2026-09-25 | 2026-09-25 | untried |
| v2 xanim borrowed endings, ranks 8001-16000 | 1 | 2 | 2 | 222,651,828,000 | 111,325,914,000 | 108,889,609,500 | 113,762,218,500 | 2026-08-25 | 2026-08-29 | live |
| sound files and aliases | 1 | 83 | 54,258 | 2,865,470,869,780,563 | 113,808,518,142 | 5,134,885,824 | 5,134,885,824 | 2026-08-19 | 2026-10-08 | live |
| measured shells, head 6 tail 6, top 1600 | 1 | 3 | 33 | 4,127,396,973,451 | 125,072,635,559 | 62,447,265,963 | 459,905,757,026 | 2026-09-03 | 2026-09-04 | cooling |
| image cores under borrowed image endings | 1 | 4 | 66 | 8,319,045,063,000 | 126,046,137,318 | 47,775,902,275 | 173,376,335,343 | 2026-08-24 | 2026-08-24 | cooling |
| v2 material borrowed endings, ranks 8001-9000 | 1 | 3 | 5 | 644,545,902,000 | 128,909,180,400 | 107,346,739,500 | 107,463,105,750 | 2026-08-27 | 2026-08-28 | live |
| measured shells, head 7 tail 7, top 800 | 1 | 2 | 5 | 653,293,536,624 | 130,658,707,324 | 81,661,692,078 | 81,661,692,078 | 2026-09-02 | 2026-09-02 | live |
| measured shells, head 6 tail 6, top 800 | 1 | 2 | 5 | 687,770,607,960 | 137,554,121,592 | 85,971,325,995 | 85,971,325,995 | 2026-09-02 | 2026-09-02 | live |
| v2 material borrowed endings, ranks 21001-22000 | 1 | 2 | 3 | 435,188,754,000 | 145,062,918,000 | 107,357,250,000 | 220,474,254,000 | 2026-08-27 | 2026-09-03 | live |
| measured shells, head 8 tail 8, top 1600 | 1 | 1 | 8 | 1,241,389,002,712 | 155,173,625,339 | 155,173,625,339 | 155,173,625,339 | 2026-09-03 | 2026-09-03 | untried |
| v2 material borrowed endings, ranks 11001-12000 | 1 | 3 | 4 | 644,581,938,000 | 161,145,484,500 | 107,352,745,500 | 214,938,223,500 | 2026-08-27 | 2026-08-28 | live |
| v2 material borrowed endings, ranks 8001-16000 | 1 | 1 | 10 | 1,695,151,867,500 | 169,515,186,750 | 169,515,186,750 | 169,515,186,750 | 2026-08-25 | 2026-08-25 | untried |
| all-boundary cores x uncarried endings, 3 segment(s), top 400000 | 1 | 1 | 4 | 729,269,023,168 | 182,317,255,792 | 182,317,255,792 | 182,317,255,792 | 2026-09-09 | 2026-09-09 | untried |
| measured shells, head 6 tail 6, top 1200 | 1 | 2 | 8 | 1,500,901,899,758 | 187,612,737,469 | 150,090,189,975 | 250,150,316,626 | 2026-08-25 | 2026-08-25 | live |
| v2 material borrowed endings, ranks 16001-24000 | 1 | 1 | 9 | 1,695,319,888,500 | 188,368,876,500 | 188,368,876,500 | 188,368,876,500 | 2026-08-25 | 2026-08-25 | untried |
| v2 material borrowed endings, ranks 24001-32000 | 1 | 1 | 9 | 1,695,727,939,500 | 188,414,215,500 | 188,414,215,500 | 188,414,215,500 | 2026-08-25 | 2026-08-25 | untried |
| info removed | 1 | 8 | 428 | 87,647,273,961,206 | 204,783,350,376 | 6,559 | 2,241,115,004,915 | 2026-08-23 | 2026-08-23 | spent |
| v2 material borrowed endings, ranks 1-1000 | 1 | 3 | 3 | 641,356,716,000 | 213,785,572,000 | 212,022,310,500 | 214,667,953,500 | 2026-08-25 | 2026-08-27 | live |
| v2 material borrowed endings, ranks 10001-11000 | 1 | 1 | 1 | 214,703,989,500 | 214,703,989,500 | 214,703,989,500 | 214,703,989,500 | 2026-08-27 | 2026-08-27 | untried |
| v2 material borrowed endings, ranks 12001-13000 | 1 | 1 | 1 | 214,708,494,000 | 214,708,494,000 | 214,708,494,000 | 214,708,494,000 | 2026-08-27 | 2026-08-27 | untried |
| v2 material borrowed endings, ranks 13001-14000 | 1 | 1 | 1 | 214,709,995,500 | 214,709,995,500 | 214,709,995,500 | 214,709,995,500 | 2026-08-27 | 2026-08-27 | untried |
| v2 material borrowed endings, ranks 17001-18000 | 1 | 1 | 1 | 214,711,497,000 | 214,711,497,000 | 214,711,497,000 | 214,711,497,000 | 2026-08-27 | 2026-08-27 | untried |
| v2 material borrowed endings, ranks 19001-20000 | 1 | 1 | 1 | 214,712,998,500 | 214,712,998,500 | 214,712,998,500 | 214,712,998,500 | 2026-08-27 | 2026-08-27 | untried |
| v2 material borrowed endings, ranks 24001-25000 | 1 | 3 | 3 | 655,476,822,000 | 218,492,274,000 | 214,717,503,000 | 220,379,659,500 | 2026-08-27 | 2026-09-03 | live |
| v2 material borrowed endings, ranks 23001-24000 | 1 | 1 | 1 | 220,493,773,500 | 220,493,773,500 | 220,493,773,500 | 220,493,773,500 | 2026-09-03 | 2026-09-03 | untried |
| v2 image borrowed endings, ranks 8001-16000 | 1 | 1 | 6 | 1,386,725,319,000 | 231,120,886,500 | 231,120,886,500 | 231,120,886,500 | 2026-08-26 | 2026-08-26 | untried |
| v2 image borrowed endings, ranks 1-8000 | 1 | 2 | 12 | 2,773,570,653,000 | 231,130,887,750 | 173,348,165,812 | 173,348,165,812 | 2026-08-25 | 2026-08-25 | live |
| measured shells, head 7 tail 5, top 1600 | 1 | 2 | 12 | 2,839,960,064,774 | 236,663,338,731 | 141,998,003,238 | 709,990,016,193 | 2026-09-03 | 2026-09-03 | cooling |
| untargeted-pool cores dropped into observed name frames | 1 | 3 | 117 | 28,958,381,160,000 | 247,507,531,282 | 89,190,992,967 | 1,109,926,190,769 | 2026-09-05 | 2026-09-05 | spent |
| measured shells, head 7 tail 7, top 1600 | 1 | 1 | 5 | 1,304,976,893,120 | 260,995,378,624 | 260,995,378,624 | 260,995,378,624 | 2026-09-03 | 2026-09-03 | untried |
| rule-substituted all-boundary cores, sound, unfolded | 1 | 1 | 10 | 2,893,174,431,455 | 289,317,443,145 | 289,317,443,145 | 289,317,443,145 | 2026-09-27 | 2026-09-27 | untried |
| bo3 mod tools vocabulary under measured decorations | 1 | 2 | 19 | 5,624,859,212,000 | 296,045,221,684 | 281,242,960,600 | 312,492,178,444 | 2026-08-24 | 2026-08-24 | live |
| measured shells, head 8 tail 8, top 800 | 1 | 1 | 1 | 310,731,213,906 | 310,731,213,906 | 310,731,213,906 | 310,731,213,906 | 2026-09-02 | 2026-09-02 | untried |
| general search | 2 | 114 | 121,959 | 5,340,315,064,562,252 | 405,521,684,604 | 25,274,434,642 | 25,274,434,642 | 2026-08-19 | 2026-10-08 | live |
| measured shells, head 6 tail 5, top 1600 | 1 | 2 | 7 | 2,852,940,114,638 | 407,562,873,519 | 356,617,514,329 | 356,617,514,329 | 2026-09-03 | 2026-09-03 | live |
| v2 material borrowed endings, ranks 56001-64000 | 1 | 2 | 8 | 3,394,468,255,500 | 424,308,531,937 | 339,049,575,900 | 566,406,792,000 | 2026-08-26 | 2026-08-26 | live |
| v2 material borrowed endings, ranks 80001-88000 | 1 | 1 | 4 | 1,698,956,343,000 | 424,739,085,750 | 424,739,085,750 | 424,739,085,750 | 2026-08-26 | 2026-08-26 | untried |
| heads of length 4 | 1 | 4 | 15 | 8,064,939,064,064 | 537,662,604,270 | 220,031,196,218 | 2,041,581,679,232 | 2026-08-24 | 2026-09-02 | cooling |
| measured shells, head 5 tail 5, top 1000 | 1 | 1 | 1 | 560,093,508,975 | 560,093,508,975 | 560,093,508,975 | 560,093,508,975 | 2026-09-02 | 2026-09-02 | untried |
| v2 material borrowed endings, ranks 1-8000 | 1 | 1 | 3 | 1,694,983,846,500 | 564,994,615,500 | 564,994,615,500 | 564,994,615,500 | 2026-08-25 | 2026-08-25 | untried |
| newer-title cores respelled | 1 | 2 | 61 | 34,510,658,565,958 | 565,748,501,081 | 367,134,665,595 | 1,232,523,520,212 | 2026-08-22 | 2026-08-22 | cooling |
| mw19 middles decorated | 1 | 1 | 51 | 29,134,495,063,900 | 571,264,609,096 | 571,264,609,096 | 571,264,609,096 | 2026-08-24 | 2026-08-24 | untried |
| broad all-boundary uncarried sound four-segment endings current | 1 | 1 | 2 | 1,229,240,297,454 | 614,620,148,727 | 614,620,148,727 | 614,620,148,727 | 2026-09-03 | 2026-09-03 | untried |
| borrowed decorations over held cores | 1 | 5 | 33 | 21,060,872,662,800 | 638,208,262,509 | 22,720,788,300 | 947,724,507,000 | 2026-08-24 | 2026-08-31 | spent |
| v2 material borrowed endings, ranks 64001-72000 | 1 | 3 | 7 | 5,089,812,147,000 | 727,116,021,000 | 565,158,636,000 | 566,326,782,000 | 2026-08-26 | 2026-08-26 | live |
| v2 image borrowed endings, ranks 16001-24000 | 1 | 3 | 5 | 4,199,720,899,500 | 839,944,179,900 | 468,370,539,000 | 1,405,111,617,000 | 2026-08-26 | 2026-08-28 | live |
| measured shells, head 5 tail 7, top 1600 | 1 | 2 | 3 | 2,644,392,954,876 | 881,464,318,292 | 661,098,238,719 | 1,322,196,477,438 | 2026-09-03 | 2026-09-03 | live |
| v2 material borrowed endings, ranks 48001-56000 | 1 | 3 | 5 | 5,090,196,195,000 | 1,018,039,239,000 | 565,186,639,500 | 1,699,076,358,000 | 2026-08-25 | 2026-08-26 | cooling |
| v2 material borrowed endings, ranks 72001-80000 | 1 | 2 | 3 | 3,394,432,251,000 | 1,131,477,417,000 | 847,761,957,000 | 1,698,908,337,000 | 2026-08-26 | 2026-08-26 | live |
| v2 material borrowed endings, ranks 40001-48000 | 1 | 2 | 3 | 3,413,430,625,500 | 1,137,810,208,500 | 859,169,382,750 | 859,169,382,750 | 2026-08-26 | 2026-08-28 | live |
| cold war broad all-boundary uncarried sound four-segment endings current | 1 | 1 | 1 | 1,229,240,297,454 | 1,229,240,297,454 | 1,229,240,297,454 | 1,229,240,297,454 | 2026-09-03 | 2026-09-03 | untried |
| measured shells, head 7 tail 8, top 1600 | 1 | 1 | 1 | 1,253,448,863,417 | 1,253,448,863,417 | 1,253,448,863,417 | 1,253,448,863,417 | 2026-09-03 | 2026-09-03 | untried |
| measured shells, head 6 tail 7, top 1600 | 1 | 1 | 1 | 1,313,248,342,747 | 1,313,248,342,747 | 1,313,248,342,747 | 1,313,248,342,747 | 2026-09-03 | 2026-09-03 | untried |
| measured shells, head 8 tail 6, top 1600 | 1 | 1 | 1 | 1,360,231,817,077 | 1,360,231,817,077 | 1,360,231,817,077 | 1,360,231,817,077 | 2026-09-03 | 2026-09-03 | untried |
| v2 material borrowed endings, ranks 32001-40000 | 1 | 1 | 1 | 1,695,955,968,000 | 1,695,955,968,000 | 1,695,955,968,000 | 1,695,955,968,000 | 2026-08-25 | 2026-08-25 | untried |
| not recorded | 1 | 194 | 9,878 | - | - | - | - | 2026-08-19 | 2026-10-10 | unmeasured |
| bo3 techset tag sweep | 1 | 2 | 1,673 | - | - | - | - | 2026-08-18 | 2026-08-19 | unmeasured |
| general search, confirmed seeds only | 1 | 4 | 531 | - | - | - | - | 2026-08-20 | 2026-08-31 | unmeasured |
| cutting at underscores and recombining | 1 | 1 | 435 | - | - | - | - | 2026-08-19 | 2026-08-19 | unmeasured |
| sound token swaps | 1 | 1 | 6 | - | - | - | - | 2026-08-19 | 2026-08-19 | unmeasured |
| stream-key grammar sweep | 1 | 7 | 0 | - | - | - | - | 2026-08-19 | 2026-08-19 | unmeasured |
| stream-tree zone peel | 1 | 1 | 0 | - | - | - | - | 2026-08-19 | 2026-08-19 | unmeasured |
| map name reconstruction and stream key templating, transferred from cold war | 1 | 1 | 0 | - | - | - | - | 2026-08-19 | 2026-08-19 | unmeasured |
| materials to images | 1 | 1 | 0 | - | - | - | - | 2026-08-19 | 2026-08-19 | unmeasured |
| attachment and weapon unfolding | 1 | 2 | 0 | - | - | - | - | 2026-08-19 | 2026-08-19 | unmeasured |
| path-shaped pools | 1 | 2 | 0 | - | - | - | - | 2026-08-19 | 2026-08-19 | unmeasured |
| model-derived pools | 1 | 2 | 0 | - | - | - | - | 2026-08-19 | 2026-08-19 | unmeasured |
| cross-pool decorations | 1 | 2 | 0 | - | - | - | - | 2026-08-19 | 2026-08-19 | unmeasured |
| numbers in place | 1 | 2 | 0 | - | - | - | - | 2026-08-19 | 2026-08-19 | unmeasured |
| cross-pool decorations over the whole vocabulary | 1 | 2 | 0 | - | - | - | - | 2026-08-19 | 2026-08-19 | unmeasured |
| streamkey templating | 1 | 1 | 0 | - | - | - | - | 2026-08-19 | 2026-08-19 | unmeasured |
| map name reconstruction (map-prefixed tokens harvested from the tables, left-anchored | 1 | 1 | 0 | - | - | - | - | 2026-08-19 | 2026-08-19 | unmeasured |
| parameterised stream keys | 2 | 2 | 0 | - | - | - | - | 2026-08-19 | 2026-08-19 | unmeasured |
| map name reconstruction + stream key templating | 1 | 1 | 0 | - | - | - | - | 2026-08-19 | 2026-08-19 | unmeasured |
| sound dotted tails as a cross product | 1 | 1 | 0 | - | - | - | - | 2026-08-19 | 2026-08-19 | unmeasured |
| weapon vocabulary growth, then attachment unfolding | 1 | 1 | 0 | - | - | - | - | 2026-08-19 | 2026-08-19 | unmeasured |
| names already found and verified, but never sent | 1 | 1 | 0 | - | - | - | - | 2026-08-19 | 2026-08-19 | unmeasured |

1515 distinct methods, run 1884 ways between them, across 5088 runs. `names` is what each run
found new to the machine that ran it. A blank candidate count means no run of that method
recorded one, so it cannot be ranked -- see `--unattributed`.
<!-- END GENERATED REGISTRY -->

---

## The shape of the problem

**Regenerate these rather than trusting them:** `python scripts/coverage.py --five`.

| | Cold War | Black Ops 4 |
|---|---|---|
| assets captured | 1,626,209 | 1,023,902 |
| filled pools | 202 | 156 |
| unnamed in pools worth searching | 204,407 | 185,686 |
| **unnamed in the five types that matter** | **136,467** | **141,889** |

Per pool, the five types, unnamed / total:

| | Cold War | Black Ops 4 |
|---|---|---|
| `image` | 46,198 / 245,235 | 60,316 / 167,360 |
| `material` | 37,758 / 158,158 | 50,551 / 122,750 |
| `xmodel` | 20,826 / 85,612 | 20,922 / 61,139 |
| `xanim` | 12,386 / 28,468 | 10,001 / 21,968 |
| `sound_asset` (files) | 19,301 / 97,217 | **70,878 / 79,263** |
| `sound_alias` (alias names) | **43,603 / 50,890** | 23,790 / 50,043 |
| `sound` (banks — not wanted) | — | 99 / 100 |

**The two sound pools are not loader assets and had to be put there.** Sound files live in SAB
files Cordycep never opens; alias names live inside the bank assets as hashes. Both were read out
of the games — the SABs directly, the aliases through Amadeus, which knows those record layouts —
and injected. Cold War's aliases are only **14.3% named**, which makes them the least-worked
ground in either game.

They go to *different* tables upstream — files to `fnv1a_xsounds.csv`, aliases to
`fnv1a_soundbanks_aliases.csv` — so the pools must not be confused. Aliases need no `--no-fold`;
their names carry no backslashes.

Nobody has come close to finishing either, and the two games are not the same problem:

- **Cold War** is where most of the work has been done, and its sound pool is worth 19,301 names.
- **Black Ops 4 is now the bigger prize outright.** It is image and material rich and under 60%
  named in both, and its `sound_asset` pool — injected from the SAB files, since the loader never
  sees those sounds — is **70,878 unnamed of 79,263, only 10.6% named**. That is the single largest
  untouched pool in either game. Grind it with `--no-fold`.

Both games use the same hash and the same normalisation, so one implementation serves both, and
`--game BLKOPS04` on any search is all it takes to switch.

**Grind both.** Until recently the project ground only Cold War, because `config.toml` does not
exist in a fresh clone and the fallback was Cold War -- so a repository calling itself a Cold War
and Black Ops 4 solver got its Black Ops 4 work from exactly one contributor. `start` alternates by
how many passes each game has had on the machine, findings are kept per game in `findings/<game>/`,
and `submit` opens one pull request per game titled `[BLKOPS04] findings from ...`. Setting `game`
in `config.toml` turns the alternation off and that choice is then respected.

### Two figures that were wrong, and are corrected here

> **`xmodelmesh` in Cold War is 271,840 ids, not 827,935.** The larger figure came from a line in
> `confirm_cw` that subtracted the wanted set from *every* unnamed id and attributed the whole
> difference to the mesh pool. Most of that difference was pools the machine simply was not asked
> to search — `streamkey` alone is 420,229. The line now reports the two separately.

> **An earlier version called Black Ops 4 an animation goldmine, worthless for materials, citing
> xanim 259,051 and material 100.** The pool counts had been labelled with Cold War's enum, and
> the games number their types differently. The 259,051 was `xmodelmesh`. `snapshots/*.pools.txt`
> is now correct for both, and the table above is generated from the snapshots themselves.

### What is not reachable, and why the counts shrink

**`xmodelmesh`.** A mesh name is `<model>_s1_geo_rigid_bs_` plus twenty-six characters of base32
that are a hash of the mesh itself. No rule can produce it, and leaving these in *doubles* the ids
a candidate can hit by coincidence, so they are dropped as unreachable rather than counted as work
remaining.

**Everything the tables resolve.** By far the largest saving: 1,626,209 Cold War assets narrow to
136,467 actually hunted.

---

## "New" means new to the community, not new to your machine

Read this before quoting a number at anybody, including yourself.

A run reports what it was the first *on this clone* to reach. On a fresh clone that is everything
it finds, which makes a first pass look spectacular and means almost nothing: the 430 the general
search returns on a fresh clone are the same 430 that five contributors have already submitted,
and the honest figure for them is **zero**.

Measured here, 2026-08-19 — four Cold War runs on a clone that started with no findings at all:

| run | found | new to the community |
|---|---|---|
| general search, committed lists | 430 | **0** |
| per-prefix continuations | 496 | **5** |
| family gap filling | 1 | **1** |
| general search, widened sound corpus | 102 | **24** |
| **distinct across all four** | **1,029** | **30** |

`submit` gets this right on its own — it drops everything already merged or sitting in an open pull
request, so those four runs send 30 names rather than 1,029. The trap is in the *reporting*: a run
note saying `new: 496` means new to this machine, and quoting that as the method's yield overstates
it by two orders of magnitude. That is exactly how the entry for method 2 above came to be wrong
the first time it was written down.

And the same pass on Black Ops 4, where the gap is far starker:

| run | found | new to the community |
|---|---|---|
| general search, Black Ops 4, 51 minutes | 15,747 | **16** |

Fifty minutes of every core, and 15,731 of those names were already claimed — almost the whole of
GoastcraftHD's earlier 13,858-name submission, re-derived from scratch.

**Judge a method by what `submit` actually sent.** And note which way the surprise ran on Cold War:
the widened sound corpus looked like the weakest of the four by run-note figures and was in fact
the strongest by a factor of five.

### The searches now exclude claimed names too, which is why that pass could happen

That Black Ops 4 run was possible because `wanted` was built from the **published tables alone**.
The tables lag the community by days, so a name merged into `submissions/` here — or sitting in an
open pull request — was still "unnamed" as far as cod-name-db was concerned, and the search kept
hunting it.

`loader::wanted_for_search` now also drops everything in `state/claimed.txt`, which `start` writes.
Measured immediately afterwards:

| | ids hunted before | after |
|---|---|---|
| Black Ops 4 | 141,881 | **124,758** |
| Cold War | 136,467 | **135,416** |

Twelve percent off a Black Ops 4 pass, and the saving grows every time anybody submits. It buys
accuracy as well as time: fewer ids means proportionally fewer coincidental matches. It also makes
a run's own figures honest by construction rather than by the reader remembering to check them.

---

## Duplicates are now handled by the software

The long instruction that used to live here — check `submissions/`, remove what somebody else
already sent — was correct and did not work, because a contributor cannot see a pull request that
is still open. It is now enforced instead of requested:

- `start` reads every open pull request and every merged submission, and writes what is claimed.
- `submit` re-reads them at the moment of sending and drops anything already claimed.
- Every run carries a **fingerprint** of its inputs, and a search whose fingerprint has already
  been submitted refuses to start.

Independent rediscovery is still not a finding. You no longer have to remember that.

---

## How to read a method

- **Builds from** — what raw material it recombines. Never thin air.
- **Reaches** — the slice of unnamed ids only this gets at. The reason to run it.
- **Run it with** — the command.
- **Spent when** — the signal it has stopped paying.

---

## 1. The general search

**Builds from** every seed there is: the published tables for this game, every name already
confirmed, everybody's merged submissions, strings scraped from a build, names borrowed from the
other game.

**Reaches** anything expressible as *beginning + stem + ending*. The workhorse and the widest net.

**Run it with** `confirm_cw` for models, materials, images and anims, and `confirm_cw --sounds`
for sound files and aliases — two passes, not one. Add `--no-fold` to a Black Ops 4 sound pass.

They are separate because a sound ending tried against a model id can only ever be a coincidence,
never a match: the vocabularies cannot reach each other's targets. Sharing one run made both
halves worse, and sharing one capped list made them worse again — sound displaced endings covering
115,606 published names while contributing endings the general pass could never use. Apart, each
gets its own measured pair (`data/sound.*.txt`), its own full ceiling, and hunts only the ids it
can reach: 121,549 and 94,668 on Black Ops 4 rather than 216,217 mixed.

**Check the ceiling before blaming the method.** `python scripts/reach.py` reports what share of
*known* names each list pair could rebuild — if it cannot express a name we already have, it will
never find the unnamed ones beside it. That measurement found Black Ops 4's sound names 19.2%
reachable: deep paths were contributing one hyper-specific beginning each, `fly/footsteps/
stakeout_overrides/asphalt_walk/` heading 158 names, and never `fly/`, which heads thousands.
Counting every leading segment took it to 100%.

`confirm_cw seeds` uses only confirmed names, which is small enough
to run in minutes and worth repeating after a long pass to pick up siblings.

**Measured**, 2026-08-19, Cold War, committed lists (700 beginnings, 4,800 endings), fresh clone:

```
12,395,196 distinct pieces   41.72 T equivalent candidates   1058 s   430 names
```

**Spent — and this is the important part.** That 430 is the same 430 for everybody. Five
contributors have submitted it, **byte for byte identical in every file**, because the method is
deterministic and a fresh clone gives everyone identical inputs. Two more submitted the same 372
from method 3 the same way. The fingerprint now stops the sixth.

**"Spent" here is not temporary, and re-measuring the lists does not undo it.** This paragraph
used to say the opposite — one command, new lists, new fingerprint, a genuinely different search —
and it was measured false: three consecutive folds returned 55 names, then 294, then 51, the last
on a corpus two and a half times larger. A new fingerprint is a new *name* for the search, not new
ground for it, and the guard that reads the fingerprint cannot tell the difference. Between them,
that advice and a fingerprint nobody could collide with (it mixed in machine-local counts, so one
method grew 48 of them) took this project from 165 names a pass to 2 in an evening.

Re-measure when the lists have lost vocabulary and `derive_lists.py` says so. To find names, take
a method that reaches somewhere the general search cannot.

**The sound vocabulary was missing and is now not.** `COLD_WAR_TABLES` named only the legacy
`fnv1a_xsounds.csv` (57,593 names). The twelve per-language files Saluki actually loads hold
**825,316 distinct names**, with *zero* rows in common with the legacy file. Every general pass
before this had one fourteenth of the sound vocabulary. See `docs/HASHES.md`. **The first pass
after this fix is a different search with a much larger corpus; expect it to pay.**

The engine peels endings off the wanted ids rather than appending them to stems, because the hash
runs backwards. Read the comments in `src/search.rs` before touching any of it.

## 2. Per-prefix continuations

**Builds from** every prefix that occurs in a known name, and the tokens measured to follow *that
prefix* — not the tokens that are common overall.

**Reaches** the families the global lists structurally cannot express. The general search offers
`mc/` and `i_c_t8_mp_spe_` the same 700 beginnings and 4,800 endings, when what actually follows
them has almost nothing in common.

**Run it with**

```
python scripts/continuations.py --depth 2 --cap 24 \n    | confirm_list - --label "per-prefix continuations" --script scripts/continuations.py
```

**Measured**, first run, Cold War, 2026-08-19:

```
39,490,781 candidates   51 s   1,837 matched   496 new to this clone   5 new to the community
```

It reaches ground the general search's committed lists do not: 496 names in 51 seconds against 430
from an 18-minute exhaustive pass. **But only 5 of those 496 were new to the community.** The other
491 had already been found by other contributors, mostly through `images_from_materials` and
`confirm_variants`. So this reaches *differently*, not *further* — worth running because it gets at
families the global lists cannot express, not because it out-yields what already exists.

The generator was the bottleneck, not the search — `confirm_list` sustains 64.3 M candidates/s from
a file and saw 0.8 M/s through a Python pipe.

Directory prefixes are given the entire vocabulary rather than a capped list, because there are
only about fifty of them and they head a large share of what this recovers.

**Spent when** a round adds little *and* re-running after folding the finds back in adds little.
It is self-feeding like the general search: each new name is a new prefix and a new continuation.
Then raise `--depth` or `--cap`, which is a different search again.

## 3. Materials to images

**Builds from** confirmed and published material names.

**Reaches** `image`, through the strongest cross-type relationship there is. **Measured**:
material and image share **15,770 cores — 11.7% of material's, 12.8% of image's**, far above any
other pair. Strip `mtl_`, try `i_` plus every semantic suffix (`_c _n _g _o _m _s _r`, which are
image's seven commonest trailing tokens by a distance), and also try it with no prefix at all.

**Run it with** `images_from_materials`.

**Spent when** the confirmed material set has not grown. Purely derivative — it yields exactly
nothing on unchanged input, so run it *after* a general pass, never before.

> **RUN TO COMPLETION, 2026-08-21. The measurement the note below asked for now exists.**
> The whole 4.35 trillion candidates, 8,096 seconds on an idle machine against Cold War:
> **43 names** -- 37 material, 5 image, 1 xmodel, 260 raw matches. That is **1 name per 101
> billion candidates**, and it is the most expensive slot in the rotation by a wide margin.
>
> For scale, the general search on the same machine the same night returned 56 names in 2,306
> seconds. Per hour of machine, `images_from_materials` is roughly a fortieth as productive.
>
> **So it earns its place only when nothing better is idle.** It is genuinely not exhausted --
> it is derivative, so every general pass that adds materials reopens it -- but it should run
> last, after the list re-measure, and never in front of a general pass or `swaps`.
>
> Still true and still worth fixing: it is the one confirming binary with **no checkpointed run
> folder**, so a pass killed part way through leaves nothing submittable. Over two and a quarter
> hours that is a real exposure. `confirm_cw` and `confirm_list` write theirs every sixty seconds
> and now mark them `.incomplete` until the run ends; this does neither.

Material names are paths, and there are **twelve** directories: `mc/ wc/ clt/ splm/ vd/ mcs/ ei/
cltp/ vdd/ el/ mcp/ ec/`. Verified against the tables — `mc/` heads 496,666 names and `ec/` heads
25. Popularity ranking keeps the first two and discards the naming of everything under the other
ten. Carry all twelve.

## 4. Numbers in place

**Builds from** confirmed names containing a number.

**Reaches** family members that beginning-stem-ending rules structurally cannot, because the number
usually sits in the *middle*. `p7_jun_brick_pillar_128` and `p7_jun_brick_pillar_32` differ where
no prefix or suffix rule can vary.

**Run it with** `confirm_variants`, or `confirm_variants swaps` to substitute whole tokens.

**This is the method that fits `xanim`.** Published xanim names run to ten and more segments, so
an ends-only rule under-reaches them badly — the middle of a ten-segment name only exists as a
stem if a nearly identical sibling was already cut. The tables hold 50,427 whole xanim names, and
walking their numbered fields in place is exactly what this does.

**Spent when** the ranges around known members have been walked past their natural end. Widen with
`swaps` before concluding it is finished.

### `swaps`' own token-pool size is a second, independent widening knob — measured 2026-09-10

`confirm_variants swaps` takes an optional trailing number: the count of most-used tokens it
substitutes at every position (default 1,024, per `COMMON_TOKENS` in `src/bin/confirm_variants.rs`).
This is completely separate from the general search's beginning/ending lists, and had never been
pushed past the default on this machine. Measured on Cold War, against the corpus as it stood at
each step (so later runs benefit from earlier ones' seeds too, and the counts are not directly
comparable for that reason alone — but the trend held anyway):

| token pool | candidates | new names |
|---|---|---|
| 1,024 (default) | not recorded exactly, order 160M | 5 |
| 4,000 | 172,336,688 | 6 |
| 4,000 (re-run later same session, grown corpus) | 121,811,572,000¹ | 24 |
| 8,000 | 243,624,552,000 | 122 |
| 16,000 | 487,268,192,000 | 128 |

¹ This jump in candidate count between the two 4,000-token rows is not the token pool changing --
it is the corpus's own vocabulary growing between runs (each `swaps` invocation re-measures its
common-token list and its seed names from whatever is confirmed *at that moment*, so a run late in
a productive session sees a materially larger `names to vary` list than one early in it). Read the
table as "wider pool + bigger corpus, run in sequence," not as a controlled single-variable
experiment -- the qualitative result holds regardless: yield kept climbing as the pool widened, and
the tokens beyond the default 1,024 were nowhere near exhausted. 122 names from the 8,000-token
run, concentrated in `xanim`, was the single best haul of this session at the time.

**The 16,000-token run has since completed: 128 names** (image 34, material 56, sound_alias 15,
sound_asset 12, xanim 4, xmodel 7 -- note the mix shifted hard away from `xanim`, which dominated
the 8,000-token haul, toward `image` and `material`). Candidates roughly doubled as expected
(243.6B -> 487.3B) but yield did not: 122 -> 128 is a 5% gain on a 100% larger pass, so the
per-candidate rate roughly halved (5.0 x 10^-10 per candidate at 8,000 tokens, 2.6 x 10^-10 at
16,000). **This is the first step in the series that did not pay for its own doubling** -- the
earlier steps (1,024 -> 4,000 -> 8,000) each returned proportionally more, not less, as the pool
widened; 16,000 is where that reverses. Read together with the type mix flip, the likeliest
explanation is that the *most* common tokens (which every pool size up to 8,000 already includes)
were carrying the productive substitutions, and the newly-added 8,000-16,000 rank band is
increasingly rare tokens that mostly just add candidates without adding hits. A 32,000-token run
would cost roughly another doubling of wall-clock time for a haul this trend predicts to be smaller
than 128, not larger -- **treat this dimension as past its knee, not exhausted outright**, and do
not widen it again without a new reason to expect otherwise.

### The same widening, tried on Black Ops 4 for the first time, pays far better -- 2026-09-10

Every row above is Cold War. This session's `swaps` widening had never been run against Black
Ops 4 at all, and CLAUDE.md is explicit about why that gap exists: only one contributor has ever
ground Black Ops 4, so almost nothing here has been tried against it twice, let alone tuned.

`confirm_variants swaps 4000 --game BLKOPS04`: 121,807,200,000 candidates, **117 new names**
(material 76, sound_alias 26, image 7, xmodel 7, xanim 1). Cold War's *own* 4,000-token row
returned 6 the first time and 24 on a re-run against a grown corpus -- so the identical method, at
the identical pool size, returned **roughly 5-20x more on Black Ops 4**, consistent with Black Ops
4 being the far less picked-over of the two games. **Do not assume a Cold War yield curve
transfers to Black Ops 4** -- re-measure each widening step there independently before deciding
it has plateaued the way Cold War's did at 16,000.

**8,000 tokens, same game**: 243,626,880,000 candidates, **133 new names** (sound_alias 87,
material 28, image 8, xanim 5, xmodel 5) -- still climbing (117 -> 133), and the mix flipped
toward `sound_alias`, which barely featured at 4,000. Cold War's 4,000 -> 8,000 step was where its
own per-candidate rate was still improving too; the two games agree on that much so far. The
`derive_closure` round after each `swaps` gain adds a handful more on top (1 name after the
4,000-token run once the `final_byte`/`sound_languages` fix below was in place; 4 after the
8,000-token run) -- small next to `swaps` itself, but free.

**16,000 tokens: 118 new names** (image 34, sound_alias 58, material 14, xanim 8, xmodel 4) against
487,268,768,000 candidates -- **down from 133 at 8,000.** So Black Ops 4's knee is at 8,000 tokens,
not 16,000 like Cold War's: both games' yield eventually turns over on this widening, but not at
the same pool size, and Black Ops 4's turnover arrived one doubling earlier despite (or perhaps
because of) starting from a far less picked-over corpus. **Do not extrapolate a knee position
between games either** -- each has now been measured to its own turnover point independently, and
that is the only way either was found. `derive_closure --game BLKOPS04` after this step added a
further 4 (`image_channels` +3, `final_byte` +1), closing in two rounds.

**Combined session tally for this widening series, both games, both directions: 128 + 10 (Cold
War) + 117 + 60 + 133 + 4 + 118 + 4 (Black Ops 4) = 574 names across eight pull requests**, from a
single knob (`swaps`'s own token-pool size) applied to two corpora it had only ever been run
against at its 1,024 default before this session. **Treat both games' `swaps` widening as spent
past their respective knees** (16,000 for Cold War, 8,000-16,000 for Black Ops 4) **unless the
corpus has grown substantially since** -- re-measuring the knee position after a large enough
gain elsewhere is a cheap check, re-running the same pool size on an unchanged corpus is not.

**Follow-up: the dedicated Black Ops 4 sound pass (`confirm_cw --game BLKOPS04 --sounds
--no-fold`), run right after, on the corpus this widening series had just grown.** 181.9 billion
forward hashes swept in 2,302s, hunting 75,859 sound ids the tables did not already resolve:
**111 new `sound_alias` names, 0 `sound_asset`.** The single largest haul of this session's Black
Ops 4 work, and it landed entirely in the pool that has an existing table to feed from
(`fnv1a_soundbanks_aliases`) rather than the injected `sound_asset` pool -- consistent with the
standing note that `sound_asset`'s 70,878-of-79,263 unnamed count is a ceiling, not a yield
estimate, and that the general search's committed lists were built to describe alias-shaped
names, not the SAB-derived asset ones. `derive_closure --game BLKOPS04` afterward added 2 more
(`materials_from_images` +1, `final_byte` +1) and closed cleanly. **This pass had not been run
against Black Ops 4 at all this session before now** -- worth remembering that the dedicated
sound pass and `swaps` are different methods over overlapping ground, and running one is not a
substitute for having run the other.

### `derive_closure.py --game` did not reach two of its seven derivations -- found and fixed 2026-09-10

Running the closure against Black Ops 4 after the `swaps 4000` gain above surfaced a real bug.
`run_derivation` built the generator command as `[python, script] + entry["args"]` and only
appended `--game <forced>` to the **confirm** step, never to the **generate** step. Five of the
seven derivations (`image_siblings.py`, `materials_from_images.py`, `image_channels.py`,
`families.py --gaps`, the `tails.py`-built plan) read confirmed names from *both* games
unconditionally and so were unaffected. **Two were not**: `final_byte.py` and
`sound_languages.py` each take their own `--game`, defaulting to whatever `state/game.txt` last
held when it is absent -- so a forced `--game BLKOPS04` run was silently peeling final bytes and
building language variants for Cold War's unnamed ids while testing the results against Black Ops
4's. The mismatch never errors: it just returns "found nothing new" for the forced game, which
reads exactly like a closed derivation.

Confirmed by re-running `final_byte.py` with and without an explicit `--game BLKOPS04`: without
it, `game: BLKOPSCW` printed in its own banner despite `--game BLKOPS04` having been passed to
`confirm_list` right after it, and the run added 0; with it, `game: BLKOPS04` printed and the run
added 1. **Fixed in `scripts/derive_closure.py`**: `generate` now carries `["--game", game]`
whenever one is forced, exactly like `confirm_args` already did. It is a no-op for the five
game-agnostic derivations, which parse argv with plain `"--game" in argv` checks or ignore argv
entirely, so passing the flag costs them nothing. Covered by `--self-test`, which still passes.

Manually closing Black Ops 4 over three rounds with the fix (materials-from-images, final-byte,
tails-3, and family-gap-filling all reaching genuinely) added 27 + 1 + 2 + 27 = 57 names in round
1 and 3 more in round 2 (a `family gap filling` gap the round-1 xmodel gains opened up) before
round 3 closed at 0 -- **60 names total**, on top of the 117 from `swaps`. Every prior
`derive_closure --game BLKOPS04` run on any machine before this fix landed would have understated
`final_byte` and `sound_languages` for Black Ops 4 specifically; worth a deliberate re-run of
those two there if the corpus has grown since.

## 5. Family gap filling

**Builds from** numbered families with two or more confirmed members, across *everybody's*
submissions rather than one run's.

**Reaches** the holes. A family with `_01`, `_02` and `_04` confirmed is evidence about `_03` that
no popularity-ranked ending list can match.

**Run it with** `python scripts/families.py --gaps | confirm_list - --label "family gap filling"`.

**Measured**: 22,594 candidates, under a second, **1 new name**. Thin, because method 4 already
walks numbered families thoroughly. Worth running anyway — it costs a second and it works across
contributors, which `confirm_variants` does not. Do not spend a night on it.

`python scripts/families.py` with no arguments is the more valuable half: it reports the shape of
what has been found, which is what suggests the next generator.

## 6. Cross-type spelling

**Builds from** the *cores* of one asset type's names — the name with its own type's decorations
stripped — spelled with another type's decorations.

**Reaches** assets whose sibling in another type is already named. **Measure the seam first**, with
`python scripts/cross_type.py --measure`. Measured shared cores, 2026-08-19:

| from → to | shared cores | share of source |
|---|---|---|
| material ↔ image | 15,770 | 11.7% / 12.8% |
| xmodel ↔ material | 3,318 | 3.5% / 2.5% |
| xanim → xmodel | 478 | 3.7% |
| xmodel → image | 195 | 0.2% |
| material ↔ xanim | 22 | 0.0% |
| image ↔ xanim | 13 | 0.0% |

**Two pairs are worth mining and the rest are not.** A model→image method or anything involving
`xanim` and a non-model type would be a night thrown away, and that is now a measurement rather
than an opinion.

**Run it with** `python scripts/cross_type.py --from xmodel --to material | confirm_list - --label
"model to material"`.

**Spent when** the source type stops gaining names.

## 7. Sound dotted tails

**Builds from** confirmed sound names and their tails, like `.rn75.pc.en.snd`.

**Reaches** sound names the general search structurally cannot, because it treats a dot as the end
of a name and can never put one back on. Everything past the first dot is invisible to every other
method.

**Run it with** `confirm_sounds`.

It searches four pools -- `sound_asset`, `sound`, `sound_bank`, `sound_duck` -- and that has been
read as scope drift. It is not. In Cold War `sound_asset` holds 97,217 ids against `sound_bank`'s
107 and `sound_duck`'s 191, so the other three widen the wanted set by **0.3%** and are peeled in
the same batch. Widening is cheap exactly when the added pools are small; widening into
`streamkey` would add 420,229 ids and quadruple the coincidence rate. `python
scripts/coverage.py` is how to tell those two cases apart, and it is what to run before widening
anything.

**Reopened.** The tail vocabulary was measured from a table holding 57,593 names when 825,316 were
available, and the two use *different* tail conventions — `.ln75.pc.all.snd` against
`.rn75.pc.<lang>.snd`. Cold War's `sound_asset` has 19,301 unnamed.

**Black Ops 4's sounds were invisible and now are not.** Its `sound` pool holds a hundred assets
because that pool is *banks* — the one entry of it that resolves is `mp_embassy.all` — while the
individual sounds live in SAB files the loader never opens. Confirmed against a live Cordycep
session with a full 1,023,902-asset load, matching the committed snapshot exactly.

Those SAB files have since been read and their ids injected as **`sound_asset`, index 170**:
**79,263 sound ids, 70,878 of them unnamed**, which makes it the largest single opportunity in
either game. Three things about them are not optional:

- **They are `sound_asset`, never `sound`.** Files and banks go to different tables upstream.
- **Their names keep their backslashes**, and the id is the hash of exactly that. Grind them with
  `--no-fold`. Measured: 8,385 of 8,385 known names reproduce unfolded, **0** folded. Without the
  flag the search matches nothing and looks completely healthy doing it.
- **The dotted-tail method still applies** — these names end `.ln100.pc.snd` and the like.

## 8. Reading the tables and extending them

**Builds from** what the tables already resolve — read for shape, then generate the neighbours that
are missing.

**Reaches** whatever the community half-finished. If a table holds `..._01` through `..._07` and
the game has more, this finds them. The most open-ended method here and the least automated: it is
somebody *looking* and noticing.

**Run it** by writing a generator that prints the neighbours and piping it into `confirm_list`.
That is now a script rather than a Rust binary, which is the whole reason this method is worth
listing.

**Spent when** — it does not, in the way the others do. It depends on noticing, and the tables grow.

**One trap, already paid for.** Feeding the tables in as candidate *input* is a closed loop: every
name in a table is resolved by definition, so it cannot be a find. It was 87% of `consolidate`'s
work for **zero** names. The tables are a source of *vocabulary* and an *exclusion list*, never a
candidate set.

## 9. Cross-game techset pairs, and the whole-tag sweep

**Builds from** a sibling game that ships the same thing unhashed. Black Ops III ships its
techsetdefs as plain files, and the newer games carry assets left over from it, so one material
exported from two games pairs a plain name with the newer game's hash. Three such pairs turn a
found transformation into a proof.

**Reaches** the techset pools, which nothing else touches. A techset name is `<base>#<8 hex>`, and
the tag is a 32-bit compile stamp that cannot be predicted — but 32 bits is small enough to
**sweep whole**: with per-digit hash-state reuse, all 4.29 billion tags for one base cost about two
seconds. A base is therefore *proved or conclusively ruled out*, never merely unswept.

**Run it with** `techset_probe` (a file of candidate bases) and `techset_pair` (known
`target_hash,plain_name` pairs).

Established 2026-08-18/19:

- **Black Ops 4** `technique_set` (3,597 ids, zero previously named): names are `<base>#<8hex>`
  with BO3's base vocabulary. Material-class sets carry `mc/` (`mc/lit_backlit#f4b74e85`);
  screen/2d/compute sets are bare (`zombie_blood#a60c435b`). Tags are per-permutation and
  `#a60c435b` is commonest. 1,322 names fell in the first 53-minute sweep.
- **BO4 simplified BO3's stems** — `lit_weapon` → `lit`, `lit_emissive_scroll` → `lit_emissive` —
  so trailing-qualifier truncation of known stems is a real seed transform.
- **Cold War** `techset` (7,096 unnamed): *not* reachable from BO3 stems under any 32-bit tag.
  Full sweeps of every stem × every tag came back empty, which is a conclusive no for that shape.

**Spent when** the base vocabulary stops growing. The tag side is never the problem.

> These names currently have **nowhere upstream to land** — cod-name-db has no techset table.
> Proposing one is worth more than another night of grinding. See `docs/HASHES.md`.

---

## 10. Sibling token substitution

**Contributed by GoastcraftHD**, 2026-08-19. This is the first method in this registry that an
assistant invented, wrote and submitted rather than one that shipped with the repository.

**Builds from** the corpus's own vote on what may stand in a given place. For every known name and
every token slot in it, the slot's *context* is the token before and the token after; every name
in the corpus votes on what has been seen in that context, and each word so measured is then
offered to every other name carrying the same two neighbours. Numbers fold to `#` when forming a
context, so `_01_` and `_07_` count as the same neighbour and a family shares one vocabulary
instead of splitting it per member.

**Reaches** the commonest kind of sibling in this game's naming, and the one the first three
methods structurally cannot produce: two names identical but for a single **non-numeric** word in
the middle. The general search recombines `beginning + stem + ending`, so it can replace a head or
a tail but never a middle with both sides intact. `confirm_variants` does change a middle token,
but only a numeric one -- `_01` becomes `_02`, `_wood` never becomes `_metal`. Continuations grow a
prefix rightwards, so a known tail cannot be preserved.

**Run it with**

```
python scripts/contributed/slotswap_20260819-225818.py | bin\windows\confirm_list.exe - ^
    --label "sibling token substitution" --script scripts/contributed/slotswap_20260819-225818.py
```

Measured, all Black Ops 4 unless stated:

| run | form | names |
|---|---|---|
| `20260819-215128` | slot alphabets, both neighbours | **1,081** |
| `20260819-215527` | same, Cold War | **76** |
| `20260819-222734` | widened: `--cap 40`, digits allowed | **972** |
| `20260819-225513` | `--context left` only | **660** |

**Spent by** its own success at one setting, and reopened by loosening the context. Keying a slot
on *both* neighbours is precise and cannot reach a name whose other neighbour is also unknown --
it requires the pair to have been seen together already. `--context left` or `--context right`
keys on one side, which is looser and less certain but reaches names the two-sided form cannot;
that change alone returned 660 more after the two-sided form had stopped paying.

---

## 11. Family column cross product

**Contributed by GoastcraftHD**, 2026-08-19.

**Builds from** a family treated as a table. Names are bucketed by their leading tokens and token
count so that members line up column for column, each column's alphabet is measured across the
bucket, and columns with a *small* measured alphabet are taken to be the family's axes. Every
member is then re-emitted with the full cross product of those alphabets.

**Reaches** names that differ from everything known in **two or more places at once** -- the slice
no other method here can produce, because every one of them moves a single degree of freedom:
the general search varies the stem, `confirm_variants` a number, method 10 one token, family gap
filling one numeric axis. One degree of freedom cannot reach two, however long it runs, and a grid
is mostly more than one step from any published corner of it.

**Run it with**

```
python scripts/contributed/templates_20260819-220821.py | bin\windows\confirm_list.exe - ^
    --label "family column cross product" --script scripts/contributed/templates_20260819-220821.py
```

Returned **115** on Black Ops 4 (`20260819-220550`) — immediately after method 10 had swept the
same corpus, so that number is what multi-axis reached *on top of* single-axis, which is the only
honest way to read it.

**The guard that makes it safe, and why it is not optional.** Columns with a *large* alphabet are
deliberately left alone: they identify the individual asset rather than offering a choice. Drop
that rule and the method walks straight into the largest trap in the repository. The image table's
highest-scoring grid is

```
volume0_state0_gi_xyz_texture_mip2_f788ac97_3        187,200 cells
```

where `f788ac97` is a **content hash**. Treated as an axis it has 32 attested values and looks
perfectly healthy, and the grid is densely populated, so a fill-ratio check passes it too. The
result would be 187,200 candidates spent guessing hash tails — unpredictable by construction. That
is `streamkey` in a new costume, and an upper bound on column alphabet is the only thing that
stops it.

**Spent by** the bucket key. `--key 3` fixes three leading tokens; families that share a shape but
not a prefix are never compared. Re-run with a different `--key` before calling it exhausted.

---

## 12. Sound language and encoding variants

**Builds from** the fact that every shipped language is a separate asset with its own id, and the
name differs by two characters. Measured across the twelve per-language tables: `en` 123,368,
`ru` 121,209, `es` 121,207, `fj` 121,155, `fr` 121,115, `ea` 121,097, `bp` 121,083, `ge` 121,082,
`ko` 121,032, `po` 121,011, `it` 120,930, `ms` 112,060. Those being so close is the argument — the
sets are near-parallel, so a name in one is evidence about eleven ids.

**Reaches** `sound_asset`, and it is the only method that gets there without rebuilding the whole
path from the lists.

**Run it with** `python scripts/sound_languages.py | confirm_list - --no-fold` (Black Ops 4).

Measured: **38 on Black Ops 4, 0 on Cold War.** The zero is the useful half — Cold War's twelve
language tables are already complete, so this is spent there and will stay spent. Black Ops 4's
SAB names have **no language segment at all** (`fly\emotes	eddybear_in.ln100.pc.snd` is stem,
encoding, platform), and a first version that required one silently skipped every Black Ops 4
name — that is, it skipped the entire pool it was written for while looking like it ran.

**Spent by** the language tables being complete. Re-run only after a pass that confirms new sound
files.

---

## 13. Image channel completion

**Builds from** a texture being authored once and exported as several maps. Measured on
`fnv1a_ximages`: **110,517 of 124,417 distinct cores (88.8%) already appear under more than one
channel**, so the odds a confirmed image is the only channel that exists are under one in eight.

**Reaches** `image`, from confirmed **images**. Method 3 (`images_from_materials`) reaches the same
pool from confirmed **materials**, so the two seed from disjoint material and feed each other: a
channel found here is a core for the next material pass and vice versa.

**Run it with** `python scripts/image_channels.py | confirm_list -`.

Measured: **456 on Black Ops 4, 59 on Cold War**, from 2.35 M candidates.

**Spent by** the channel list. Widen it from the table when new suffixes appear; it is measured,
not guessed.

---

## 14. Token insertion and deletion

**Builds from** the observation that every other method here *substitutes* and none changes a
name's length. The general search rebuilds `beginning + stem + ending`; `confirm_variants` swaps a
number; `slotswap` swaps one token; `templates` swaps several. All keep the token count the seed
had. So a name that is a known name **plus or minus one word** is unreachable by all of them,
however long they run:

```
p9_rus_apartment_tower_sign_01
p9_rus_apartment_stone_tower_sign_01      an insertion -- reachable by nothing else
```

That shape is common here because artists qualify a name as an asset set grows — a `wall` becomes
a `stone_wall` when a second material appears — and both spellings survive in the build.

**Reaches** all four of model, material, image and anim.

**Run it with** `python scripts/token_edits.py --type model | confirm_list -`.

Measured, one pass each: Black Ops 4 **model 139, material 423, image 72, anim 66**; Cold War
**model 21, material 179, image 112, anim 72**. 13.1 M candidates for models.

Deletions need no vocabulary and are the higher-precision half (`--no-insert`). Insertions are
seeded per position *and per leading token*, so a name beginning `p9_` is offered what follows
`p9_` elsewhere rather than the type's globally common words — a global vocabulary at every
position produces more candidates than the general search and reaches less.

**Spent by** `--cap` and the corpus. Deletions exhaust in one pass against a fixed corpus;
insertions reopen whenever either changes.

---

## 15. Affix sweep

**Contributed 2026-08-20.** The only method here that does not require a token to have been
measured before it can be offered.

**Builds from** nothing but the alphabet. For each stem it emits every combination of a short
leading and trailing token — `a_stem_a`, `a_stem_b`, … `aa_stem_a`, … `aba_stem_zz` — over the
36 characters real affixes actually use.

**Reaches** a permanent blind spot in every other method. Everything else recombines *measured*
vocabulary, and a frequency-ranked list of 4,800 endings structurally **cannot hold a token used
once**. Measured across the four general tables there are 341 distinct leading tokens of one to
three characters and 2,044 trailing ones; the common ones are carried by every list, and the long
tail — which is most of the distinct values — is carried by none.

Brute force is the *right* tool here, and only here, because the space is genuinely small: 36
characters over four positions is 1.7 million, a rounding error beside the 2^63 that makes word
composition hopeless. Point the same idea at whole words and it becomes the mistake `Order of
resort` warns about.

**Run it with**

```
python scripts/affix_sweep.py --type model --stems 200 | bin\windows\confirm_list.exe - ^
    --label "affix sweep" --script scripts/affix_sweep.py
```

### Targeted, not scheduled — and the measurement says so plainly

A blind run on Black Ops 4 models: **62 stems, 532,497,168 candidates, 1 name.**

| method, BO4 models | names per candidate |
|---|---|
| `token_edits` | 1 per 94,000 |
| **affix sweep, blind** | **1 per 532,000,000** |

That is roughly **5,600× less efficient per candidate**, and it is the whole argument. An hour buys
about 500 stems against a corpus of 250,000 — 0.2% coverage. As a rotation item it is poor value
next to almost anything else here.

**Its value is entirely in choosing the stems.** Use it when you have a reason to believe a
particular family holds more — a set a pass has just cracked open, a map whose assets are half
recovered — and sweep *those* stems exhaustively. It answers "is there more here?" completely,
which no other method can, rather than "what is there?" cheaply, which several do better.

The one it found blind shows the shape it reaches:
`c_t8_zmb_dlc3_mannequin_female_static_standpose_body_color_01` — a common `c_` prefix *and* a
common `_01` suffix, on the same stem, which needs both ends varying at once on a stem the general
search never cut as a piece.

**A negative result here is worth recording.** A targeted sweep is exhaustive over its stems, so if
a family you expected to be productive returns nothing, that is a strong measured statement about
that family rather than a shrug — and it is expensive to rediscover.

### Sized before it runs, and it refuses to exceed it

Candidates go as `stems x (L+1) x 36^L` for combined affix length `L`, so `L` is solved for rather
than chosen: 186,624 candidates per stem at L=3, 8.4 million at L=4. `--hours` sets the budget
(default 1) and the script prints the plan before emitting a line. There is no flag to force a
longer sweep, because one that takes a fortnight is not a method, it is a mistake nobody notices
for a fortnight.

**Do not reach for this when a pass returns little.** Low findings usually mean the *lists* need
re-measuring, not that brute force is needed — re-measuring took sound-file ending reach from 27.8%
to 96.7% in one command. Running a sweep when a starved list is the real problem burns an hour and
finds nothing.

**Separators are gated per type, and that is measured.** `/` appears 98,384 times in short material
affixes but always closing a directory code (`mc/`, `wc/`), never scattered through one — so it is
applied as a separator rather than swept as a character, which is both correct and 1.12x cheaper at
L=4. `.` is swept nowhere: sound dots live in long fixed tails the endings list already reaches.

**Spent by** its stems, never by the alphabet. Re-running over the same stems at the same length
returns exactly what it returned before; re-running over new ones is a new search.

---

## 17. The build itself, read off this disk — 2026-08-24

**Every dead end recorded against Black Ops 4 `sound_asset` ends with the same sentence:**
*"anything reaching this pool has to come from outside the naming -- the SAB files, a build, or
the game's own strings."* Three recombination shapes have returned 0 against 70,707 unnamed ids,
`sabpaths` returned 0 in 187 billion candidates, and every older- and newer-title corpus is
measured dead. The file has been pointing at an outside source for four days and nobody had
checked whether one was reachable.

Both games are installed on this machine, and so is the extracted SAB tree:

    D:\Battlenet\Call of Duty Black Ops 4              142 GB
    D:\Battlenet\Call of Duty Black Ops Cold War       100 GB
    D:\Battlenet\BO4_Extracted_Sab                      30 GB

### The SAB files are not the source, and that is now measured rather than assumed

`zone/snd/**/*.sabl` and `*.sabs`, 414 files: magic `2UX#`, a hash table, FLAC payload, and the
only printable string in any of them is `reference libFLAC 1.2.1 20070917`. **No plaintext
whatsoever.** That is why the pool is 89% unnamed and why `sabpaths` had to guess at path
structure in the first place. Do not spend a session extracting SABs for names; they hold none.

### The build is the source, and it reads

| | |
|---|---|
| `LPC/*.ff` — twelve loose fast files, 10.4 MB | **2,135 name-shaped strings → 7 new names, 1 per 305** |
| `Data/data/data.NNN` — 148 CASC archives, 141 GB | first 0.5 GB of one archive: 3,637 strings → **10 new names, 1 per 364** |

**1 per 305 is the second-best rate ever measured here**, behind `final_byte` at 1 per 18 and
ahead of image siblings at 1 per 394 — and unlike either it is not bounded by the corpus, because
its vocabulary is not drawn from the corpus at all. `outfit_northern_lights_legendary3_firebreak`
and `loot_ui_icon_stickers_safari_animals_4_large` are not recombinations of anything this project
holds. That is the whole point of §1473: *what finds names is a method whose vocabulary comes from
outside the region the named corpus already covers.*

`contrib/harvest_bo4.py` does it, and three details are the method:

- **Oodle.** Black Ops 4 fast files are the same block chain Cold War uses — four little-endian
  words per block, the last of which is the block's own offset, which is what proves the chain was
  found rather than guessed. The game ships its own decompressor (`oo2core_6_win64.dll`), and Cold
  War's `oo2core_8` reads Black Ops 4's streams too.
- **BLTE, and this is the part that decides whether it works at all.** CASC frames every archive
  entry into 256 KB chunks, **each prefixed by a one-byte mode**. So even an uncompressed chunk is
  not contiguous with the next, and a block chain whose offsets are relative to the fast file's own
  start dies at the first boundary. Walking the frame in place returned **11 names an archive**;
  reassembling the frame first returned **3,637 from half of one**. The entry's own size sits in
  the 30-byte header in front of the frame, which is what bounds a single-chunk frame carrying no
  chunk table.
- **A density check before the text filter.** Compressed payload decodes as printable often enough
  to pass `harvest_retail.py`'s name filter: the first probe produced 6,092 strings of which **0**
  matched any id, all of them noise like `0/2och5p`. A frame is only read as text if 60% of its
  first 4 KB is printable.

**Nothing decompressed is written down.** A chunk is decompressed into memory, scanned, and
dropped; the only output is the name list.

### What the same harvester says about the rest of the build — 2026-08-24

Measured while the archive sweep ran, so nobody repeats any of it:

| | |
|---|---|
| **Cold War's archives** | 105 archives, 100 GB, same layout, same reader: **5,795 strings, 0 matched.** Cold War fast files are AES-256-CTR encrypted (already recorded in the dead ends), so the frames reassemble and hold nothing readable. Black Ops 4's are not. **The harvestable game is Black Ops 4.** |
| `BlackOps4.exe`, the launcher, `Data/ecache`, `Data/viper`, `Data/indices`, `Data/config` | 117 MB, 5,493 strings, **0 matched.** Consistent with the loader-string-pool dead end: an asset is reachable from the binary only if the engine addresses it by name, and these are addressed by hash. |
| `KAPI` frames — Black Ops 4's xpak containers, 135 in one archive | Cold War keeps its real asset names in an xpak's plain-text metadata section, so these looked like the richest thing in the build. **They are not: 3,763 strings and every one is noise** (`b57/.mk`, `sgxd/cp`). Black Ops 4's xpak has no plaintext metadata section. The 60% printable gate was right to drop them. |
| Frames dropped for size | 276 of 2,101, all of them entries over 256 MB — payload, not zones. The one sampled that did reassemble (953 chunks, 244 MB) yielded nothing. |
| Coverage | **2,101 frames across 141 GB, 1,825 reassembled (87%), 532 fast files walked.** One frame per 67 MB: these archives hold whole zones as single entries, so this is close to complete rather than a sample. |

**And where the names land is the useful part.** Of the first 92, **56 were `sound_alias`** against 18 image and 18 material. Black Ops 4 sound aliases are written in plaintext inside the zones, which is precisely the pool three recombination shapes and 379 billion candidates could not touch. No backslash-bearing sound *file* paths appear anywhere in the build, so `sound_asset` is still not reached this way.

### The other builds on the disk, and what each one is worth — 2026-08-24

Once the Black Ops 4 reader worked, the question stopped being *"is a build readable"* and became
*"which builds are on this machine, and what does each cost to read"*. Steam and Battle.net between
them hold ten Call of Duty installs here. Measured, all against both games' unnamed ids:

| source | what it is | names it printed | verbatim | under `data/prefixes.txt` x `data/suffixes.txt` |
|---|---|---|---|---|
| **Black Ops 4 zones** | Oodle block chains inside CASC BLTE frames, 141 GB | 273,138 | **145 matched, 92 new** | **6 new** |
| **Black Ops 3 mod tools** | ~~the source assets Steam ships beside the game~~ | ~~867,766~~ | 11 + 11 | 10 + 9 | **retired — the tree is not the shipped game. See below.** |
| **`.iwd` archives** | 208 ZIP files across Black Ops, World at War, Modern Warfare 1-3 and Remastered | 528,740 | **0 both games** | -- |
| **Cold War zones** | same CASC layout, fast files AES-256-CTR | 5,795 | 0 | -- |
| **`BlackOps4.exe` and the aux data dirs** | 117 MB raw | 5,493 | 0 | -- |

**The mod tools are the cheapest source on the disk and nobody had opened them.**
`contrib/harvest_bo3.py` reads Black Ops 3's shipped `zone/*.ff`, which is the compressed half of
that install; the mod tools are the other half, and they need **no format work at all** -- a source
asset is named by its filename, and a `.gdt` is a plain-text table whose keys are asset names
spelled the way the engine wants them. 248,726 files walked, 9,213 read as text, 867,766 distinct
names -- but from a tree that is not the shipped game. Replaced by
`scripts/harvest_bo3_assetlist.py`, which reads only the shipped manifests; see below.

`.iwd` is the same trick one title further back: it is a ZIP with the extension changed, so
`zipfile` lists every path inside without decompressing anything. Half a million names for two
minutes of work, and **zero**, which is the answer METHODS already predicts for verbatim
older-title names and is worth having measured on a corpus this size.
`contrib/harvest_iwd.py`.

### Every install on this machine, and why the unread ones are unread — 2026-08-29

The table above measured five sources and left the rest looking merely unvisited. They are not
unvisited. **They are encrypted**, and that is a different problem with a different answer, so
here is the whole disk with the reason per install. `scripts/contributed/survey_builds_20260829-154201.py`
regenerates it, with `--probe` for the payload test.

| install | containers | state |
|---|---|---|
| Black Ops 4 | CASC, 148 archives + 12 loose `TAff0000` | **read.** `harvest_bo4.py`; the index and BLTE censuses above prove it complete |
| Black Ops III | 283 `TAff0000`, 10.95 GB | **read.** `harvest_bo3.py` |
| Cold War | CASC, no `.ff` | frames reassemble, fast files AES-256-CTR inside |
| Black Ops II | 297 `TAff0100` v147, 3.84 GB | **encrypted, and the best-specified lead here.** Header carries the `PHEEBs71` marker at +0x0C, then the zone name; Salsa20 with a per-title key schedule. 37.0% printable, no zlib stream anywhere in the header |
| Modern Warfare 3 | 94 `IWffu100` + 65 `IWff0100`, 5.28 GB | encrypted. 36.5% printable, no zlib |
| Modern Warfare 2 | 52 `IWffu100` + 44 `IWff0100`, 4.70 GB | encrypted, same |
| Black Ops | 146 `IWffu100`, 2.99 GB | encrypted. 35.8% printable |
| World at War | 130 `IWffu100`, 2.43 GB | encrypted. 10.1% printable |
| Call of Duty 4 | 83 `IWffu100`, 2.72 GB | encrypted |
| Modern Warfare Remastered | `.dcache`, `.h1` | no `.ff`; newer engine, and re-hashing newer titles is measured 0 |
| Call of Duty, Call of Duty 2 | `.pk3`, `.iwd` | already covered by the `.iwd` sweep, which returned 0 |

**`IWffu100` does not mean plaintext, and this is the trap worth writing down.** The flag describes
the container, not the payload. Every one of these reads 10-36% printable with strings like
`XK_gsO` and `7Al_Sd_z` -- long enough and underscore-bearing enough to pass a loose name filter,
and pure noise. A harvester pointed at them without the printable gate `harvest_bo4.py` already
uses would produce hundreds of thousands of confident non-names. Neither spelling holds a zlib
stream at any offset in its header, so they are not merely compressed differently.

**So "walk the builds nobody has walked" is not a cheap lead and should not be listed as one.**
Every unread container on this disk is behind a cipher. The cheap external ground is finished; what
is left is a key, and Black Ops II is the one with a published key schedule to go and find.

### Do not walk a mod tools install. Only `zone/` is the shipped game — 2026-08-24

The first version of this walked the whole Black Ops 3 install and printed 867,766 names, and
**that was wrong, for a reason worth more than the 41 names it found.**

Most people using this repository *have* the Black Ops 3 mod tools — it is largely why they want
these names unhashed in the first place. And a mod tools tree is not the shipped game: it is a
working directory. `model_export/`, `source_data/`, `texture_assets/` and `share/raw/` are where
a modder's own and the community's assets land, in the thousands.

**The only path in a Black Ops 3 install that can be trusted is `zone/` in its root** — the
official `.ff`, `.sab` and the rest, which ship and which nobody writes to. `contrib/harvest_bo3.py`
already reads exactly that, so the safe source was already covered and the walk added only risk.

Measured on the install this was written on, which is **the cleanest in the community** — its owner
uses the tools only to release their own work — and therefore a **floor** rather than a typical
case: one modder's folder, `model_export/_ninjaman829_bo6_guns/`, contributed **1,216 names**.

They are the dangerous shape, not obvious rubbish:

    t10_ar_coslo723_anim
    wpn_t10_p01_ar_coslo723_barrel_v0_c
    att_t10_ammo_unspent_556_v0_c

`t10` is **Black Ops 6**. Those read exactly like official Treyarch names, they can never be in
either title this project searches, and this file already records all eight `_v2` tables as
**measured dead** — so every one of them is waste dressed as vocabulary.

Three things follow, and the third is the one that generalises:

- **Nothing bad was published.** Of the 1,216, **0** reached a submission: a candidate only becomes
  a finding by hashing to a real unnamed id, and a Black Ops 6 name does not. The 41 names the
  tools vocabulary did find are hash-verified and genuine — `i_t7_wood_white_birch_worn_c`,
  `veh_t7_civ_city_flat_tire_fl` — and they stay.
- **The waste is the contributor's night**, not the tables. On an install with a real mod library
  this is most of the corpus, and it is being asked about a game it cannot be in.
- **A method seeded from a user-writable directory is not a method.** It gives a different corpus
  on every disk, so it cannot be reproduced, and its fingerprint — the whole mechanism that stops
  two people grinding the same ground — means nothing. That is the general rule: **seed only from
  something every contributor has identical bytes of.** Published tables, shipped containers,
  `findings/`. Never a working directory.

**`scripts/harvest_bo3_assetlist.py` replaces it**, and keeps the value without the risk. Two
paths in a Black Ops 3 install are trustworthy, and both are shipped:

| path | what it is | read by |
|---|---|---|
| `zone/` | the official `.ff` and `.sab` containers | `scripts/harvest_bo3.py` |
| `zone_source/all/assetlist/*.csv` | 19 shipped per-zone manifests, one `type,name` row per asset | `scripts/harvest_bo3_assetlist.py` |

The manifests give **106,836 distinct names** -- 36,617 image, 23,691 xanim, 10,484 material,
5,271 xmodel -- with **0** matches for `ninjaman`, `_t10_` or any other community string, because
nobody has a reason to write to them. The script finds the install through the **`TA_TOOLS_PATH`**
environment variable the tools set, rather than a hardcoded Steam path, so it works on anybody's
machine.

`scripts/contributed/harvest_bo3_tools_20260824-032954.py` remains as the record of the submission
that carried the walking version. Do not run it. `contrib/harvest_iwd.py` had the same fault — it was reading
`World at War/mods/HumorModTWO/HumorModTwo.iwd` — and now refuses to walk `mods/`, `usermaps/`,
`workshop/`, `raw/` or `downloaded/`.

### Black Ops 4 `sound_asset` is not in the shipped build either — 2026-08-24

Worth stating plainly, because the build was the last place the dead ends pointed and it has now
been read. **No backslash-bearing sound path appears anywhere in Black Ops 4's 141 GB**, and
neither does a forward-slash one: `.snd`, `vox/` and `/vox_` match **0** of the 273,138 strings
harvested. The `.sabl`/`.sabs` files hold a hash table and FLAC payload and no plaintext at all.

The reason is structural rather than a matter of looking harder: the engine addresses a sound file
through its **alias**, and the alias resolves to a hash. The file paths existed in the developers'
source tree at build time and were never shipped. That is consistent with what *did* come out --
**56 of the first 92 names were `sound_alias`**, the by-name-addressed half of the sound system,
against 0 `sound_asset`.

So the 70,707 unnamed `sound_asset` ids are not reachable from this build, from the SAB files, or
from any recombination of the 8,584 that are known. What would reach them is a source outside the
shipped game entirely -- a leaked build, a developer tree, or the Black Ops 4 mod tools if they
ever ship.

### What is left of this

- **Cold War.** Identical layout, 100 GB, and `scripts/harvest_retail.py` still points at
  `D:\_CW_FILES`, which is empty. The same harvester needs only its root changed.
- **The `.idx` files -- measured 2026-08-29, and the answer is no.** They do map every content
  key to an archive, offset and size, and reading them is easy once written down (standard CASC
  v7: 9 byte key, 5 byte big-endian storage offset packing `archive:offset` at 30 offset bits,
  4 byte little-endian size, and over half the records are markers at exactly 30 bytes). But the
  index lists **2,028 real frames for Black Ops 4 and the magic hunt already found 2,101**, so it
  reaches nothing the hunt cannot see -- there is no hidden tail of the build, and `harvest_bo4`
  was already complete. Verified rather than assumed: every frame the index names has `BLTE` at
  exactly +30, 40 of 40 checked. Cold War indexes 2,953 frames over 214 GB and stays unreadable
  for the separate reason already recorded, that its fast files are AES-256-CTR encrypted.
  Reader: `scripts/contributed/casc_index_20260829-063030.py`.
- **Encrypted frames -- counted 2026-08-29, and there are none.** Mode `E` is Salsa20 against the
  build's key ring and mode `F` is a recursive frame, and both were dropped rather than guessed at
  because nobody had counted them. Counted now, by walking every frame the index names and reading
  the one mode byte in front of each chunk: **Black Ops 4 is 674,771 chunks, 442,577 `Z` and
  232,194 `N`, and zero `E` or `F`.** Cold War is 3,271,834 chunks, 3,271,820 `N` and 14 `Z`,
  also zero of either. So nothing is being skipped for want of a key at this layer and the
  harvester was never dropping anything: Cold War's frames really do reassemble and hold nothing
  readable, because its encryption is AES-256-CTR **inside the fast file**, a layer below BLTE.
  Together with the `.idx` count above this closes the build: there is no unread remainder.
  Census: `scripts/contributed/blte_modes_20260829-151441.py`.

---

## 18. The typed cross: an external corpus, kept type by type — 2026-08-24

**The single change that made an external corpus pay, and it is one line of principle.**

Every cross this project has run pools its stems and asks one beginning list and one ending list
about all of them. §6 already says why that is wrong -- *"Measure conventions, never guess them"* --
and `snapshot.confirmed_names(kind=...)` exists precisely for it, with a docstring that is blunt:
*"mixing types silently destroys exactly the measurement being taken."* An image wears `i_` and
`_c`; a material wears `mc/mtl_`; an xanim wears neither. Pooling them spends almost every
candidate asking a question no name of that type could answer.

Measured on the same corpus, the same day, against both games:

| | candidates | names |
|---|---|---|
| pooled, untyped (`bo3_dec`) | 346 B | **0** |
| typed, 250 begin x 1,200 end | 5.5 B | **50** |
| typed, 600 x 3,000 | 28 B | **54** |
| typed, 1,500 x 8,000, depth 4 | 159 B | **305** |
| typed, 4,000 x 25,000, depth 5 | 1.1 T | **108 and counting** |

**Zero against fifty on a sixtieth of the machine**, and it keeps climbing as the lists widen --
which is the *ending list is the bottleneck* result of §1355, now confirmed from the outside rather
than by re-measuring our own corpus. `scripts/typed_cross.py`.

### What makes it runnable is a typed external corpus

A cross needs the two halves to come from different places (§1473), and the external half has to
carry its type or there is nothing to keep apart. Black Ops 3's **shipped manifests** are exactly
that: `zone_source/*/assetlist/*.csv`, one `type,name` row per asset, 247 files across thirteen
locales, given away with no harvesting at all --

    29,514 image     18,091 xanim     8,715 material     4,157 xmodel

against `zone/`, which holds every asset in the game but only as strings that have to be pulled out
of Oodle containers and that carry no type whatsoever. `scripts/harvest_bo3_assetlist.py`.

### The shape, per type

- **cores** -- that type's external names with *their own* measured decorations stripped, so what
  crosses is the borrowed thing rather than Black Ops 3's spelling of it;
- **beginnings and endings** -- measured on *our* names of the same type, published and confirmed.

`xanim` leads consistently. It is the least-named type in both games -- 68.9% and 64.0% -- and
Black Ops 3 ships 18,091 of them, so the one type where our corpus is thinnest is the one the
external corpus is fattest in.

### Which external corpora it works on, measured

The method is not about Black Ops 3. It is about **any** corpus that carries its type, and three
were to hand:

| source | typed how | image | material | xmodel | xanim | sound_alias | sound_asset |
|---|---|---|---|---|---|---|---|
| Black Ops 3 shipped manifests | `type,name` rows | 277 + 197 | 107 + 110 | 13 + 17 | 41 + 37 | -- | -- |
| cod-name-db `_v2` tables | one table per type | -- + 30 | 12 + 81 | no table | 24 + 10 | **199 + 473** | 0 |

*(Black Ops 4 + Cold War, at 4,000 x 25,000 for the manifests and 600 x 3,000 upward for `_v2`.)*

Two results in that table are worth more than the names.

**The `_v2` tables are recorded dead in this file** -- all eight, 1,175,524 names hashed verbatim
against 336,505 unnamed ids, **zero** -- and `cross_era`, which respells their cores our way but
pools every type together, managed **61 names for 34.5 trillion candidates**. Typed, the same
tables give hundreds. Nothing about the corpus changed; only whether an image core was asked to
wear image decorations.

**`sound_alias` is the richest of the lot.** `fnv1a_soundbanks_aliases_v2` is 20,564 names, the
smallest external corpus tried, and it returned **339 on Cold War in one pass** and 134 more when
widened, plus 199 on Black Ops 4. An alias is a bare underscore name with no directory and no
channel code, so it is the type that suffers *most* from being pooled with images -- which is
exactly why it had never paid before.

**`sound_asset` returned 0**, and that is the expected answer rather than a disappointment: the
sound-file dead ends in this file are extensive, and nothing about typing was going to make a
recording's path transfer between titles. Note the Black Ops 4 half of that pool needs `fold: no`
-- a plan crossing it folded matches nothing while looking healthy (§5), so a zero from a folded
plan means nothing at all and was not counted here.

### And it is spent by

Widening its own lists, eventually. Each step has returned more than the last so far, and the
cores *shrink* as the lists widen -- deeper stripping leaves less middle -- so the two move against
each other and there is a width past which it stops. Nobody has found it yet.

### Why they move against each other: one flag was driving both — 2026-08-24

The sentence above describes a real effect and gets its cause wrong, and the cause is fixable.
`typed_cross.py` calls `decorations()` twice with the **same** `(depth, begins, ends)`:

    heads, tails             = decorations(mine,   depth, begins, ends)   # the plan's columns
    their_heads, their_tails = decorations(theirs, depth, begins, ends)   # used to STRIP

The two uses are opposites. The first is **reach** -- every beginning and ending our names are
measured to wear, and more of it is strictly better. The second is **stripping** -- the longest
matching decoration is cut off each external name, and what survives is the core being borrowed.
Widen that and there is less middle left to borrow. So "the two move against each other" is not a
property of the method; it is one flag wired to both ends of it.

Measured on the Black Ops 3 manifests (`contrib/measure_core_collapse.py`):

| type | cores at depth 3, 250x1200 | at depth 6, 8000x50000 | lost |
|---|---|---|---|
| image | 10,121 | 6,206 | -39% |
| material | 4,438 | 2,461 | -45% |
| xmodel | 1,456 | 797 | -45% |
| **xanim** | **2,268** | **883** | **-61%** |

`xanim` is the type this method leads with, the least-named type in both games, and the one Black
Ops 3 ships most of -- and the widest configuration ever run threw away **61% of its borrowed
vocabulary** to buy ending-list reach. The ceiling nobody could find is largely this artefact: past
a certain width each step is paying for reach with the very cores it is meant to decorate.

**`scripts/contributed/typed_cross_split_20260824-155834.py` separates them.** `--depth/--begins/--ends` size our decorations;
`--strip-depth/--strip-begins/--strip-ends` size theirs. Wide reach with shallow stripping gives
xanim **2,249 cores against 883 at the same 8,000 x 50,000** -- 2.55x the vocabulary, and 1,366 of
those cores are ones the coupled version cannot express *at any setting*, because the widening that
would reach them is what destroys them.

The general lesson is the one §1272 already records in a different costume: **a method has inputs
as well as a shape, and a flag that means two things measures neither.** Check what a knob is wired
to before concluding the method has a ceiling.

---

## 19. Borrowed endings, kept type by type — 2026-08-24

**The mirror of §18, and the same one-line fix applied to a script that already existed.**

`scripts/borrowed_decorations.py` already takes decorations from a build we are not searching and
wears them on cores we already hold. It is the right idea and it has no `--kind`: one `--source`,
one set of beginnings and one set of endings, asked about every asset type at once. §18 measured
what that costs in the other direction -- pooled 0 against typed 50 -- and nothing had applied the
result to the mirror.

### Why a borrowed ending reaches what a measured one cannot

Our ending lists are measured on names we already know, so an ending our games use is in the list
**if the names using it have been found**. An ending used in Black Ops 4 only on assets nobody has
named is invisible to that measurement. Black Ops 3 is Black Ops 4's direct predecessor -- same
studio, same engine, same conventions -- so it can see them. That is the `uncarried.py` argument
pointed at an external corpus instead of at our own cap.

The overlap is the control, measured with `contrib/measure_borrowed_decorations.py`:

| type | their endings | we already carry | new to us |
|---|---|---|---|
| xanim | 19,274 | 6,086 (**31.6%**) | 13,188 |
| xmodel | 8,664 | 1,449 (16.7%) | 7,215 |
| material | 21,991 | 3,182 (14.5%) | 18,809 |
| image | 60,000 | 4,985 (8.3%) | 55,015 |

A third of Black Ops 3's animation endings are ones our corpus independently arrived at. The
borrowing is meaningful rather than two unrelated vocabularies being stapled together.

### Only the endings transfer, and the same measurement says so

Their *beginnings* do not: `t7_icon_attach_`, `mc/mtl_zmb_t7_`, `attach_t7_loot_`. A beginning
carries the title tag and an ending carries the part, so beginnings stay ours. This is worth
stating because `borrowed_decorations.py` borrows both, and half of what it borrows cannot match.

### What it returned

First run, 107 B candidates per game, 1,500 of our beginnings x 8,950 of our cores x 8,000
borrowed endings:

| | new names |
|---|---|
| Cold War `xanim` | **27** |
| Black Ops 4 `xanim` | **22** |

`scripts/contributed/typed_borrowed_endings_20260824-161029.py`.

### And it is spent by

The external corpus. Black Ops 3's manifests are 106,836 names and every ending in them is now
either carried or tried at the 8,000 cap. Widening the cap is the next step and the same
core-collapse caveat applies -- see §18's note on the coupled flags. A second external build with
shipped manifests would reopen it entirely.

---

## 31. Beginnings the ceiling drops

```
python contrib/ceiling_dropped_begins.py --sound --plan plans/ceiling_sound.txt
bin\windows\confirm_plan.exe plans/ceiling_sound.txt --game BLKOPSCW
```

Methods 22 and 23 mine the endings `data/suffixes.txt` **never measured**. This mines the
beginnings it *did* measure and then threw away, which is a different failure and needs the
opposite remedy.

`reach.py` puts `xsounds` at **100% reached and 10.7% named** -- the endings can express these
names, the beginnings almost never can. That reads exactly like a stale list asking to be
re-measured, and it is the trap. `derive_lists.py` already says what is happening, in its own
summary line:

    sound.prefixes.txt: 839 measured, 14 carried, 153 past the ceiling of 700 dropped
    the ceiling cut 153 measured beginnings, the largest being vox/scripted/sims/ (454 names)

The measurement finds the vocabulary. **The cap discards it.** So re-measuring cannot raise reach
-- it discards a different 153 -- which is the same displacement recorded above for the general
lists, where three consecutive folds gave 55 names, then 294, then 51 on a corpus two and a half
times larger.

**A plan has no cap.** That is the entire method: put the discarded beginnings in front of the
engine directly. Nothing shared changes and no fingerprint moves, because `data/` is never
written -- the generator lifts the ceiling, takes the measurement, and restores the four committed
lists from a backup in a `finally`.

### What it returned

153 beginnings x 1,985,997 all-boundary sound cores x 2,890 sound endings, **884 billion
candidates on Cold War: 9 names**, at 0.0114 expected by coincidence. `derive_closure.py` then
turned those 9 seeds into **18 more**, which is the usual multiple and the reason a small pass is
still worth submitting.

The 153 are not exotic. They are ordinary Cold War sound paths too deep for a 700-line file:
`bik_execution_` -- which `reach.py` separately reports as heading 136 names with no cut carried
-- `amb/cp_rus_amerika/control_room/emt_`, `cp/level/cp_nam_prisoner/bridge/evt_`.

### And it is spent by

Nothing yet, and it does not decay the way a recombination does: the cut list is recomputed from
the corpus, so **every pass that confirms names changes which beginnings the ceiling drops**. Re-run
it after any gain.

**The general half is measured too, and it is much the thinner of the two.** `prefixes.txt` drops
27 beginnings against `sound.prefixes.txt`'s 153, and 27 x 1,771,555 all-boundary cores x 4,629
endings -- 230 billion candidates -- returned **1 name**, with the closure adding nothing on top.
Two reasons, and both were visible beforehand: five of the 27 are `mcdp/` cuts, which method 19
already mined for 2,846, and the rest are single deep paths (`vdd/gfx_english/sound/vox/...`,
`zombietron_raw/portuguese/...`) rather than families. The sound side is where this method lives:
there the cap is binding on a list that is genuinely short of slots, and `xsounds` sits at 10.7%
named because of it.

Black Ops 4 was given the same general plan and returned **0** over the same 230 billion
candidates against its own 158,818 unnamed ids. That is the expected answer rather than a
surprise -- the 27 are Cold War's cuts (`mcdp/`, `cp_`-flavoured paths), and a beginning list
measured across both games' published tables drops whatever ranks lowest globally, not per
title. Worth the twenty minutes to have it measured, and worth knowing before anybody aims
this at Black Ops 4 again: **the cut list is only as title-specific as the corpus that ranked
it**, so the sound side's 153 are Cold War's too.

The obvious follow-up -- rank a beginning list on Black Ops 4 alone and drop *its* tail -- is
already answered in the dead ends, and answered no: *uncarried beginnings crossed with the whole
corpus* measured **0 on Black Ops 4** across 945 M candidates, because those beginnings have
private vocabularies rather than borrowed ones. Rank by borrowed share first
(`scripts/contributed/redecorations_20260823-023757.py`) if anybody tries anyway; on the
2026-08-29 corpus the best non-`mcdp/` candidates top out at 52 cores, against `mcdp/`'s 692.

The honest ceiling on it is the cap itself: 153 beginnings is all a 700-slot file is currently
hiding, so this is a seam rather than a mine. Raising `MOST_PREFIXES` would close it altogether,
and is a decision about shared state rather than a pass.

---

---

## 32. Cores from the pools nobody files, dropped into observed frames — 2026-09-05

```
python contrib/untargeted_pool_cores.py <untargeted names>... > contrib/untargeted_cores.txt
python contrib/boundary_frames.py --heads --limit 45000 > contrib/frame_heads.txt
python contrib/boundary_frames.py --tails --limit 45000 > contrib/frame_tails.txt
bin\windows\confirm_plan.exe plans/frames_untargeted.txt
```

`contrib/untargeted_pool_cores.py`, `contrib/boundary_frames.py` | **13** (CW), **91** (BO4) |
6.4 T and 8.1 T candidates

Two halves, and neither works without the other. That is the whole entry, because each half was
measured alone first and both returned zero.

**The vocabulary.** Every method here seeds from names known to be real, and the sources are
always the published tables and this project's findings — which between them describe only the
five *targeted* types. But a game holds tens of thousands of assets in types nobody submits: ai
types, script bundles, fx, characters, vehicles, destructibles, beams, cameras. Those names are
obtained a different way — they are read out of the build rather than cracked, several of those
pools carrying their name as a plaintext string in the asset — and their vocabulary had never
been fed back into the search.

That corpus has the one property the cross-era corpora lack. Re-hashing a newer title's published
names returns **zero** against these two games (see the dead ends) because the newer engines
renamed rather than inherited. Untargeted-pool names are *game-native*: a spawner called
`spawner_zm_gegenees` and a script bundle called `aib_t9_vign_cust_zm_silver_steiner_left_levitate`
are Black Ops 4 and Cold War strings, so the characters and systems they name are the ones these
games' models, materials and images are named after too.

From 15,114 such names: 9,880 kept after dropping the code-and-data pools (a lua file or a script
parse tree is named after a **source file**, so its vocabulary describes the program and no model
is ever named after a widget — this filter is worth 5,236 names of pure noise), 39,575 cores, and
**4,008 carrying at least one token no held name has ever used**.

**The frames.** `heads` cuts a name once and keeps the front; `tails` cuts once and keeps the
back. This keeps **both sides of the same cut** — everything before one token, and everything
after it — so the question stops being *what else begins like this* or *what else ends like this*
and becomes **what else goes here**. Cut at every underscore, slash and dot, so a frame can sit
five segments deep. Measured off 1.66 M names describing Black Ops 4: 528,180 distinct heads and
3,365,044 tails.

**What it reaches that nothing else does:** a name whose every decoration is ordinary and whose
*subject* is a word only an untargeted asset ever named. `ui_icon_general_feedback_demented_echo_head`
is unreachable by any method seeded from the targeted types, because nothing they contain says
`demented_echo` — an ai type does. The Cold War pass landed across five asset types off two such
words, `tormentor` and `demented_echo`, which is the thesis in miniature: a character named in a
pool nobody files has models, materials, images, anims and sounds named after it.

**Both halves were measured alone and both are zero.** The same 4,008 cores against the committed
`data/prefixes.txt` × `data/suffixes.txt` — 13.0 B candidates — returned **0**. The ending list is
short tails (`_c`, `_n`, `_01`), so a candidate could only ever be `<prefix><core>_c` while the
real name is `ui_icon_general_feedback_<core>_head`; the middle was inexpressible and the core had
nowhere to land. The lists were not wrong, they were the wrong *shape* for the question. Equally,
frames crossed with the corpus's own vocabulary is just the general search, which has been swept
since the second day.

**Spent by:** the size of the untargeted corpus, not the frames. 4,008 cores is a small stem list
by this project's standards and it is the entire supply — every further name recovered from a pool
nobody files widens it, and nothing else does. Widening the frames is the cheap knob and it decays
the usual way; widening the *vocabulary* is what reopens this.

**Note for whoever runs it next:** the engine sustains ~813 M candidates a second here, so 13 B is
twenty seconds and a pass worth starting is measured in trillions. The first run of this method was
sized in billions out of habit and finished before it was worth watching.


---

## 33. Sound aliases named from the aliases they point at — 2026-09-05

```
python contrib/alias_edges.py <aliases.csv> | bin\windows\confirm_list.exe - --game BLKOPSCW
```

`contrib/alias_edges.py` | **3** (CW), 0 (BO4) | 38,993 and 42,606 candidates

**Read the alias definition table first — this entry is really about that.** Both games' tables
had never been used here: nothing in this file or in `scripts/` referenced them before today, and
between them they cover the two sound pools completely.

| | Black Ops 4 | Cold War |
|---|---|---|
| alias ids in the table | 50,043 — **the whole `sound_alias` pool** | 50,890 — **the whole pool** |
| file ids in the table | 78,609 of 79,263 `sound_asset` | 96,777 |
| rows | 476,693 | 241,595 |

Every row carries, in **plain text**, the zone the sound is banked in, its bus, its volume group
and its duck group — and in `secondaryaliasname` and `stopalias`, the **hash of another alias**.
That last part is the method. An edge with a known name at one end and an unknown at the other is
a name you are one edit away from, on the game's own authority rather than on a guess about what
the corpus looks like.

The edit is measured, not invented. The same tables hold **172,830 edges with a known name at
both ends**, and each is a worked example:

```
mpl_hud_notify_camo           ->  mpl_hud_notify_camo_riff
wpn_flame_thrower_start_plr   ->  wpn_flame_thrower_cooldown
uin_aar_bar_fill_tail         ->  uin_aar_bar_fill_main
tst_front_left_1              ->  tst_front_right_1
```

A rule is the pair of tails that differ after the longest shared run of whole tokens, which
covers appending, replacing and swapping in one form. Rules seen twice or more are replayed onto
the open edges.

**What it reaches that nothing else does:** an individual unnamed alias, identified by name, in
the one pool where every recombination shape has returned a total zero. It does not ask what the
corpus looks like in general — it says *this* unknown is the partner of *that* known one.

**The rate is the reason to keep it.** 3 names from 38,993 candidates is **1 per 13,000**, against
a registry whose best rows sit between 1 per 810 and 1 per 94,000. Black Ops 4 returned 0 from a
comparable list, so this is a Cold War result so far.

**Spent by:** the number of known names sitting at the end of an open edge — 395 in Cold War, 351
in Black Ops 4, out of tens of thousands of edges, because a handful of known aliases anchor most
of them. That count rises every time an alias is named by any method, so unlike most things here
this one is refilled by everybody else's work.

**What is still unmined in those tables.** The alias → file mapping. 78,609 real `sound_asset`
ids sit in the Black Ops 4 table each attached to a named-or-nameable alias, and `sound_asset` is
the largest single opportunity in either game at 70,878 unnamed of 79,263. The published relation
between the two vocabularies is weak — 0.7% of file stems are exactly an alias name — but nobody
has tried it *per edge*, with the alias's zone and sequence number in hand, which is a different
question from the corpus-wide one that measured 0.7%.


## 34. Family grid completion, past the top 20 — 2026-09-14

```
python scripts/family_grid.py --top 30 | bin\windows\confirm_list.exe - --game BLKOPSCW
```

Every prior run of this method — the original method 30 pass, the `--top 20` generic sweep
(Black Ops 4 only, 2026-09-02), and the twenty hand-written `*_shared_tail_grid_*.py` variants
(both games, 2026-09-09) — stopped at the twenty largest grid-shaped families: `vox`, `i`, `fly`,
`vm`, `ui`, `wpn`, `p8`, `mp`, `p7`, `amb`, `jup`, `p9`, `zmb`, `sat`, `evt`, `callingcards`,
`icon`, `pt`, `weap`, `mus`. All twenty are recorded dead on Cold War. Nobody had asked
`family_grid.py --audit` what sits *below* rank 20 — `melee` (41,151 cells), `veh` (18,150),
`pb` (15,725), `ai` (14,654), `att` (11,592), `volume0` (9,892), `uin` (9,170), `mm` (9,156),
and others down to rank 30.

`--top 30` re-sweeps the already-dead top 20 (harmless — they contribute 0 as before) and reaches
the ten families below them for the first time. **4,709,171 candidates in 18s, 10 new
`sound_alias` names.** Every hit landed in a family outside the previously-covered twenty, which
is the point: the shared-tail grid restriction is not spent in general, only spent on the specific
families that had actually been tried. `derive_closure` afterward added 0 — these ten did not
feed any of the seven registered derivations, all of which key off image/material/xmodel.

**Spent by:** all 61 families it can currently find. The obvious next step, `--top 61` (every
family `family_grid.py --audit` will admit at the standing `--min-members 200` / `--min-axis 3` /
`--min-tails 20` thresholds), was run immediately after: 4,764,491 candidates, **0 new** — ranks
31-61 add nothing beyond what the top 30 already found. So this is now fully spent for Cold War
at this corpus size, not merely spent past rank 20. Reopens only if the corpus grows enough to
push a currently-too-small family over `--min-members 200`, or if the thresholds themselves are
loosened. **Re-run for Black Ops 4 immediately after, same 4,764,491 candidates (`--game BLKOPS04`): 0
new.** Extends the 2026-09-02 `--top 20` Black Ops 4 negative to the full 61-family set — ranks
21-61 do not open anything there either, even though Black Ops 4 is otherwise the far less
picked-over game (see the `swaps` widening section, where the identical token-pool step returned
5-20x more on Black Ops 4 than Cold War). So this specific method's ceiling is not a
picked-over-corpus effect — the shared-tail grid restriction itself is what is exhausted here,
on both games, at the current corpus size.

**Loosening the thresholds instead of the rank cutoff was tried next and also closed.**
`--min-members 80 --min-axis 3 --min-tails 10` (down from the defaults of 200/3/20) admits 97
families instead of 61, but the extra 36 are so small they add only 14,823 cells on top of the
4,764,491 the full default sweep already emits. **0 new on both games.** So every knob this
generator exposes — rank cutoff and admission threshold alike — is now exhausted at this corpus
size; reopening it needs either a much larger corpus or a different notion of "family" than
`head_<axis>_<tail>` split on the first underscore.

## 35. Saluki's own recovered-hash databases, outside the six wanted pools — 2026-09-14

```
python contrib/saluki_beams.py "path/to/beams_recovered.csv" | bin\windows\confirm_list.exe - --game BLKOPS04
```

Saluki (the live Cordycep-backed browser this project's confirmations are checked against) ships
recovered names for the `beam` pool specifically -- a real Black Ops 4 pool, 130 ids total, that
sits outside this project's default six pools and so is invisible to every search here unless
`all_pools = true` is set in `config.toml` for the run. Requested via the user's own Saluki
session (with BO4 loaded, no live game process involved -- Saluki reads the CASC containers
directly) and exported as `hash,name`, 34 lines.

**26 of 34 confirmed new** against Black Ops 4's `beam` pool with `all_pools = true` -- a 76% hit
rate, the highest of anything run this session. `cod-name-db` has no dedicated `beam` table, so
these are filed under `submit`'s general "every pool" handling the same way Kenshin9977's earlier
`fx`/`xcam`/`sanim`/etc. finds were (see their 2026-09-11 submission, which already carries a
`beam` pool from a *different* recovered-hash source, FiggleFX's `beams_recovered.csv` --
`scripts/contributed/figglefx_bo4_fx_beams_20260904-070316.py`). The two sources evidently do not
fully overlap, since this session's 26 were confirmed new against everything already published and
claimed. **95 of 130 beam ids remain unnamed** after this session.

**Why this is worth more than 26 names.** Saluki bundling its own recovered-hash list for one
untargeted pool raises the obvious question of whether it has similar lists for others -- this was
not investigated further this session, but is worth asking about directly: any other "recover" or
"database" feature in Saluki's UI beyond the four browsable pools (Model/Material/Image/Animation)
is a candidate source nobody here has tried. **Spent by:** whatever Saluki's own beam database
already knows; a larger or updated Saluki release could reopen this the way a table refresh
reopens the general search.

**Practical note:** `all_pools = true` must be set for `confirm_list`/`confirm_cw` to even look at
a non-standard pool's ids -- without it the pool is not part of `wanted_for_search` at all, and a
correct candidate simply will not be checked (not "found nothing," genuinely never asked). Unset
it again afterward; leaving it on turns every subsequent default search into a much slower
every-pool sweep, which CLAUDE.md §5 explains is the single most reliable way to waste a night.

## 36. `name_field_probe`, extended to Black Ops 4 for the first time — 2026-09-14

`name_field_probe` and `loader_strings` (§ "Infrastructure, not generators" above) had only ever
been run against Cold War, for lack of a live Black Ops 4 loader to point them at. The user
opened Black Ops 4 in Cordycep for an unrelated reason (the `beam` pool export in method 35) and
offered the same session for this. No Rust toolchain was available on the machine, so
`contrib/name_field_probe.py` reimplements the Rust binary's exact algorithm in pure Python via
`ctypes` (`OpenProcess` + `ReadProcessMemory` against Cordycep's own process, read-only, no game
process involved) rather than installing one.

**Every one of the wanted-adjacent pools stores only its id at a fixed header offset, never a
name.** `xanim`=3 at `+0x70`, `xmodel`=4/`material`=6 at `+0x00`, `xmodelmesh`=5 at `+0x00`,
`technique_set`=8 at `+0x00`, `image`=9 at `+0x20` — confirmed over 156 of 172 pools, sampling 128
assets per pool then verifying the winning offset over the whole pool (100% coverage in every
row). The `xanim`-at-`+0x70` figure matches the Rust tool's own docstring exactly, which is the
strongest evidence the Python reimplementation is faithful. **This closes the "hidden plaintext
name in the header" hypothesis for the five wanted types on Black Ops 4 the same way it was
already closed on Cold War** — the id really is all the header holds; nothing here would ever
find these names.

**What the header approach did find:** four *other* pools store a name as readable text,
hash-verified by construction: `sound`=10 (30, bank names like `core_bootstrap.all`), `sanim`=77
(399), `storagefile`=128 (41), `storecategory`=132 (8) — 478 names total. **All 478 already
published or claimed** (`all_pools = true`, 0 matched) — these pools are evidently already well
covered by other contributors' "every pool" sweeps (Kenshin9977's submissions already carry
`sanim`). Zero net names, but a clean, useful negative: the header-text approach is not a source
of anything new here, on top of confirming it cannot reach the five wanted types at all.

**The bigger implication is the one worth acting on.** Cordycep decrypts whatever it loads before
this ever touches it — so the standing "Cold War's fast files are still AES-256-CTR encrypted,
key unknown, single largest untapped source" barrier (see "Why the yield per submission keeps
falling") does not apply to a live Cordycep session the way it applies to reading the files
directly. **Nobody has pointed this probe, or `loader_strings`' live string-pool cross-check, at a
*live Cold War* Cordycep session** — only ever at a Cold War session for the header-offset
question specifically, historically, and never at Black Ops 4 until today. Loading Cold War the
same way and re-running both scripts is the direct, concrete next step this result points at.

## Method 31 (ceiling-dropped beginnings) re-measured, both games, 2026-09-20

Re-ran `contrib/ceiling_dropped_begins.py --sound` (the `borrowed/ab_*_cores.txt` all-boundary
stem lists it needs were missing from this clone -- `borrowed/` doesn't exist on disk here and
never got committed, being gitignored working data; recreated from the same-shape lists already
sitting in `contrib/ab_cores.txt`/`contrib/ab_sound_cores.txt` from early September, which are
stale by roughly two weeks of corpus growth but still the same all-boundary shape method 25
established). The measurement itself found real, fresh displaced vocabulary: **376 sound
beginnings** past the 700 cap now (largest unlisted: deep `vox/scripted/...` and `amb/...`
paths), up from the 153 recorded in 2026-08-29 -- the corpus has grown enough that more gets cut.

Ran the resulting plan (376 beginnings x 182,295 all-boundary sound cores x 3,014 sound endings,
207.2B candidates) against Cold War: **0 matched, 0 new.** The general-lists half was checked too
but not run -- only 7 beginnings are currently past that cap (versus 700 carried), matching the
original finding that the general half is the minor of the two, and 7 was not worth an hour of
machine for a plan this small to write up.

The same plan (same beginnings, same all-boundary sound cores, same sound endings -- nothing
about it is game-specific except which unnamed-id set it is checked against) was then run with
`--game BLKOPS04`: only 4.4B candidates there, since Black Ops 4's `sound_asset`/`sound_alias`
pools have been cut down enormously by other contributors since this method was invented (70,878
unnamed in 2026-08-29 down to roughly 14,586 now). **0 matched, 0 new** there too.

So the method that returned 9 (then 18 more via closure) three weeks ago on a smaller corpus
returns nothing on this one, on both games. Two readings, and no way to distinguish them from a
single re-run: either the specific 153-then-376 beginnings the cap displaces are exhausted at this
corpus size and a much larger displaced set is needed to reopen it, or the two-week-stale
all-boundary core lists this run reused are missing cores the current, larger corpus would offer.
**Re-run with freshly regenerated `ab_cores.txt`/`ab_sound_cores.txt` (method 25's own generator,
`uncarried_endings_allboundary_20260823-134935.py` or its 2026-08-29 successor) before concluding
this is dead** -- this run did not control for that variable and should not be read as closing it.

**Done immediately after, same session.** Regenerated `ab_sound_cores.txt` fresh
(`uncarried_endings_allboundary_20260829-172236.py --sound-pass`, no arguments changed): 2,526,795
all-boundary sound cores against the current corpus, up from the ~182,000 the stale contrib/ copy
held. Re-ran the ceiling-dropped-beginnings plan with this fresh stem list (376 beginnings x
2,526,795 cores x 3,014 endings, 2.87T candidates): **0 matched, 0 new**, settling the open
question above -- the stale core list was not what was holding this method back at this corpus
size. Genuinely closed now, not just unmeasured.

**The productive half turned out to be a different generator entirely.** While regenerating,
`--sound-pass --confirmed-only` was also run: cores that exist *only* in this project's own
findings and merged submissions, never in the published tables, crossed against the **committed**
(capped) `data/sound.suffixes.txt` rather than the uncapped list -- a combination method 25's
"confirmed-only" flag supports but nobody appears to have actually run at this corpus size (387,199
cores, 1.17B candidates, seconds to finish). **6 new names** (3 image, 2 material, 1 xmodel) --
landing outside the sound pools despite an all-*sound*-cores source, because a segment boundary cut
from a sound path can equally be a valid image/material core; the search checks every wanted pool
regardless of which vocabulary a candidate's pieces came from. `derive_closure` afterward reported
`image siblings of confirmed materials +11`, run against a baseline (`confirmed_total()`, 466) that
had already been overtaken by the plan runs above (472) by the time it started -- the exact
shared-repo measurement artifact the 2026-09-14 session flagged for this same derivation. **Trust
`submit`'s own ledger over either number**: it sent **11 names total** (8 image, 2 material, 1
xmodel) as [#2135](https://github.com/KingslayerKyle/hash-slinging-slasher/pull/2135), which is the
one count here actually re-verified against the tables and open pull requests at send time.

Note for whoever re-runs this: the confirmed-only plan and the full-corpus plan above were run
concurrently (the confirmed-only cores are a subset of the full set), and both independently
converged on the same 6 real ids -- `confirm_plan` correctly wrote them to two separate run
folders with identical contents rather than deduplicating across concurrent processes, which
`submit` then resolved. Not a bug, just a reason a run folder's own count and the true new-name
count can diverge when two of this method's variants run at the same time.

## Method 25 (all-boundary cores), the *general* half, is far from spent -- 2026-09-20

The sound half above turned out closed once genuinely fresh cores were used. The general
(non-sound) half was never actually re-checked at this corpus size, on the theory it would be
similarly stale. It was not.

Regenerated `ab_cores.txt`/`ab_ends.txt` the same way (`uncarried_endings_allboundary_20260829-172236.py`,
no arguments changed): **1,877,196 all-boundary cores**, up an order of magnitude from whatever the
stale Sep-4 copy held, crossed with the same top-100,000 uncarried endings the method has always
used. Run as `stem: @borrowed/ab_cores.txt`, `end: @contrib/ab_ends.txt`, `bare: yes` -- no `begin:`
line, since an all-boundary core is already a complete prefix from position 0 and adding
`data/prefixes.txt` on top would triple-count it as a 700x-wider cross product for no reason (caught
at `--size`: 131.5T candidates with a spurious `begin:` line, 187.7T without it -- ~700x apart,
exactly the beginning-list size, confirming the mistake before it cost an hour).

**Cold War: 187.7B candidates, 51 new names** -- 9 image, 14 material, **26 xanim**, 2 xmodel.
`xanim` is normally the hardest pool here (least-named of the five, per every coverage snapshot in
this file) and the biggest single share of this haul. `derive_closure` afterward added 5 more
(1 image siblings, 1 materials-from-images, 3 image channels). Submitted as
[#2137](https://github.com/KingslayerKyle/hash-slinging-slasher/pull/2137) (56 names total).

**The same stem and ending lists, unchanged, against Black Ops 4** via `--game BLKOPS04` -- nothing
about the lists is game-specific, only the wanted-id set checked against them -- and the
**confirmed-only** cut of the same cores (`--confirmed-only`, cores that exist only in this
project's own findings/submissions, 85,305 of them, crossed with the *committed* `data/suffixes.txt`
rather than the uncapped list, 410M candidates) found **35 new Black Ops 4 names**: 9 image, 11
material, 1 xanim, 14 xmodel. The confirmed-only sound cores crossed the same way against Black Ops
4 (unfolded, per CLAUDE.md §6) added **8 more**: 1 image, 3 material, 2 xanim, 2 xmodel. Submitted
together as [#2136](https://github.com/KingslayerKyle/hash-slinging-slasher/pull/2136).

**The general lesson from both halves together:** this method's yield tracks the *size of the core
list*, not the size of the ending list or how many times the method has been run before. A core
list regenerated fresh from whatever the corpus holds *today* keeps paying every time the corpus
has grown meaningfully since the list was last built -- which for a shared, actively-submitted
project happens continuously. **Treat `ab_cores.txt`/`ab_sound_cores.txt` in `contrib/` as
perishable working data with a shelf life measured in days, not as a settled input.** Regenerating
them costs under a minute and should be the default before running any method that reads them,
not an afterthought reached for only after a stale run comes back suspiciously empty.

**The confirmed-only cut deserves its own line, separately from "regenerate the cores."** It is
not a smaller, cheaper version of the full sweep -- it targets a *different* vocabulary
(names this project alone has found, never in any published table) against the *committed,
capped* ending list rather than the uncapped one, and it is cheap enough (hundreds of millions to
low billions of candidates) to run after every single batch of new confirms, on both games, without
it ever being a real cost. Do this before reaching for anything more expensive.

**And the full sweep against Black Ops 4 is where this really paid off.** The same 1,877,196-core,
100,000-ending general plan that found 51 on Cold War, run unchanged against Black Ops 4 --
187.7B candidates, same lists, only the wanted-id set differs -- returned **324 names**: 54 image,
136 material, 2 sound_alias, 42 xanim, 90 xmodel. `derive_closure` afterward added **75 more** across
three rounds (`family gap filling` alone contributing, plus the usual image/material derivations
feeding off 136 fresh materials). Submitted as
[#2138](https://github.com/KingslayerKyle/hash-slinging-slasher/pull/2138) -- 380 names sent, 19
dropped as already claimed by somebody else's submission or open pull request in the few minutes
between this run starting and `submit` sending, which on a repository this actively shared is the
expected outcome rather than a problem.

Black Ops 4 paying roughly 6x what Cold War did from the *identical* candidate list is worth
sitting with. Both games share the same all-boundary core vocabulary (cores are pooled from
confirmed names and published tables across both titles), so the difference is not what was
offered -- it is that Black Ops 4's unnamed remainder was, at this exact moment, unusually
reachable by this shape. That can flip; it does not mean Black Ops 4 is now the better game to
point this at *in general*, only that it was on 2026-09-20. Re-measure rather than assume next
time.

**The sound half of the same fresh-cores approach pays too, once run as the full sweep rather than
just the ceiling-dropped-beginnings subset.** `stem: @borrowed/ab_sound_cores.txt` (the same
2,526,795 fresh all-boundary sound cores from above), `end: @contrib/ab_sound_ends.txt` (the
matching fresh 100,000-ending list, uncapped rather than the committed `data/sound.suffixes.txt`),
`bare: yes`, no beginning -- 252.7B candidates. **Cold War: 23 new** (4 image, 8 material, 10
sound_alias, 1 xmodel). Run unchanged against **Black Ops 4: 137 new** (14 image, 75 material, 17
sound_alias, 9 xanim, 22 xmodel) -- sound_alias folds normally on both games (it is the SAB
`sound_asset` paths specifically that need `--no-fold` on Black Ops 4, and this run used the
default fold and still landed 17 real Black Ops 4 sound_alias names, so the fold/no-fold choice
was not actually a live concern here). `derive_closure` added 0 more on Cold War and 11 more on
Black Ops 4 (7 image siblings, 4 materials-from-images). Submitted as
[#2140](https://github.com/KingslayerKyle/hash-slinging-slasher/pull/2140) (Cold War, 23) and
[#2139](https://github.com/KingslayerKyle/hash-slinging-slasher/pull/2139) (Black Ops 4).

**Running total for method 25's general and sound halves together, both games, this session:**
Cold War 51 + 5 + 23 + 0 = **79**. Black Ops 4 35 + 8 + 324 + 75 + 137 + 11 = **590**. From one
regenerated core list each, reused across four plan variants (general full, general
confirmed-only, sound full, sound confirmed-only) and both games. Regenerating stale working data
was the entire trigger for all of it.

**The ending list's segment depth is a fifth axis worth varying, not just a knob to set once.**
`--segments` controls which trailing-N-underscore-segment shape counts as "an ending" when
*measuring* the uncarried gap -- it does not touch the cores at all, so re-running it is cheap (one
more `--segments N` invocation) and produces a genuinely different top-100,000 ending list each
time. Tried `--segments 3` (the default is 2) fresh, same 1,877,005 general cores: **Cold War 41
new** (5 image, 7 material, 2 sound_alias, **27 xanim**), **Black Ops 4 92 new** (5 image, 43
material, 8 sound_alias, 12 xanim, 24 xmodel). `derive_closure` added 3 more on Cold War, 22 more
on Black Ops 4 (5 image siblings, 13 final-byte, 3 tails, 1 family gap). Submitted as
[#2142](https://github.com/KingslayerKyle/hash-slinging-slasher/pull/2142) (Cold War, 44) and
[#2141](https://github.com/KingslayerKyle/hash-slinging-slasher/pull/2141) (Black Ops 4).

Two segment depths, same core list, same order of magnitude of new names each time (41+3=44 and
23 and 51+5=56 on Cold War; 92+22=114 and 324+75=399 and 137+11=148 on Black Ops 4) -- this is not
a knee that exhausts after one pull. **Untried at this corpus size: `--segments 1` and
`--segments 4`.** Worth doing before assuming the ending-depth axis is spent; each costs one
regeneration (under a minute) plus one ~190B-candidate pass per game.

**`--segments 1` tried next, same session:** smaller ending vocabulary (181,488 uncarried at depth
1 against 820,404 at depth 3), and the yield shrank with it -- **Cold War 13 new** (3 image, 7
material, 3 sound_alias), **Black Ops 4 45 new** (4 image, 25 material, 3 sound_alias, 3 xanim, 10
xmodel). `derive_closure` added 1 more on Cold War, 19 more on Black Ops 4. Submitted as
[#2144](https://github.com/KingslayerKyle/hash-slinging-slasher/pull/2144) (Cold War) and
[#2143](https://github.com/KingslayerKyle/hash-slinging-slasher/pull/2143) (Black Ops 4). Smaller
than depths 2 and 3, but still real -- not yet the point where widening this axis stops paying.

**`--segments 4` closes the axis, at least for now.** Cold War **3 new** (all material), Black Ops
4 **13 new** (12 material, 1 sound_alias) plus 2 more from closure -- both a clear step down from
depths 2 and 3, matching the shape of the original 2026-08-23 combined-both-games measurement
(1 seg 316, 2 seg 2,553, 3 seg 1,523, 4 seg 381: 2 and 3 are the strongest, 1 and 4 fall off on
both sides). Submitted as [#2146](https://github.com/KingslayerKyle/hash-slinging-slasher/pull/2146)
(Cold War) and [#2145](https://github.com/KingslayerKyle/hash-slinging-slasher/pull/2145) (Black
Ops 4). **Stop varying general segment depth here** -- depths 1 through 4 are now all freshly
measured at this corpus size and the shape matches the original finding closely enough that 5+
is unlikely to reopen anything without a much larger corpus.

**Running total, four segment depths combined:** Cold War 137 + 3 = **140**. Black Ops 4
768 + 15 = **783**.

**Done immediately after, same session -- the sound side pays the same way.** `--sound-pass
--segments 3` (default is 2): 100,000 endings x 2,527,503 cores, 252.75B candidates. **Cold War 10
new** (1 image, 5 material, 4 sound_alias), **Black Ops 4 38 new** (6 image, 17 material, 9
sound_alias, 2 xanim, 4 xmodel). `derive_closure` added 0 more on Cold War, 10 more on Black Ops
4. Submitted as [#2148](https://github.com/KingslayerKyle/hash-slinging-slasher/pull/2148) (Cold
War) and [#2147](https://github.com/KingslayerKyle/hash-slinging-slasher/pull/2147) (Black Ops 4).

**`--sound-pass --segments 1` next:** a much smaller uncarried-ending vocabulary at this depth
(35,118, under the 100,000 cap, so every one of them is used rather than a top-N cut) --
88.8B candidates. **Cold War 16 new** (3 image, 3 material, 6 sound_alias, **2 sound_asset**, 1
xanim, 1 xmodel) -- the first `sound_asset` hit from any of this session's all-boundary runs.
**Black Ops 4 68 new** (4 image, 32 material, 31 xmodel). `derive_closure` added 0 more on Cold
War, 7 more on Black Ops 4. Submitted as
[#2150](https://github.com/KingslayerKyle/hash-slinging-slasher/pull/2150) (Cold War) and
[#2149](https://github.com/KingslayerKyle/hash-slinging-slasher/pull/2149) (Black Ops 4).

**`--sound-pass --segments 4` closes the sound side of the axis the same way depth 4 closed the
general side:** Cold War **2 new** (material), Black Ops 4 **16 new** (5 image, 11 sound_alias)
plus 7 more from closure. Submitted as
[#2152](https://github.com/KingslayerKyle/hash-slinging-slasher/pull/2152) (Cold War) and
[#2151](https://github.com/KingslayerKyle/hash-slinging-slasher/pull/2151) (Black Ops 4).

**Segment-depth axis, both general and sound, now fully swept 1 through 4 on both games. Stop
here** -- the shape is consistent everywhere it was checked (2 and 3 strong, 1 and 4 weaker), and
widening further (5+) is very unlikely to pay without a substantially larger corpus than the one
measured today.

**Final running total for this session's method-25 work, general + sound, all four segment
depths, both games:** Cold War **169**. Black Ops 4 **929**. Roughly 1,100 names total from one
initial insight (the working core lists in `contrib/` were weeks stale) multiplied across four
plan shapes (general/sound x full/confirmed-only) and four ending-segment depths, on top of the
turn-taking this project already does between the two games.

## Redecoration re-ranked fresh: `mcdp/`'s trick does not generalise past it -- 2026-09-20

Method 19's insight (`mcdp/` is a re-decoration of the general material vocabulary, not its own
namespace -- 692 of 692 cores borrowed, 2,846 names) came with a diagnostic,
`scripts/contributed/redecorations_20260823-023757.py`, that ranks every uncarried beginning by
*borrowed vocabulary share* rather than by how many names it heads. It had never been re-run since
2026-08-23, and the corpus has grown roughly 2x since. Re-ranked fresh: `launcher_`, `volume8_`,
`volume9_`, `volume12_`, `volume17_`, `[korea15]fxt8_`, `[korea15]fxt9_` all score **100%
borrowed**, and a further ~20 score 25-98%, none of them examined before now.

Tested the top 60 (three batches of ~10-30 `begin:` lines each, one shared 954,662-core held-
vocabulary stem list, `bare: yes`, a few million to ten million candidates per batch -- this shape
is nearly free): **0 new on Cold War, across all three batches and all 60 beginnings.** Black Ops
4: **1 new** (material), from batch 1, closure added 0 more. Submitted as
[#2153](https://github.com/KingslayerKyle/hash-slinging-slasher/pull/2153).

**A 100% borrowed-vocabulary share predicted nothing here, the same way high overlap has failed to
predict yield everywhere else this file has tried it** (material↔image cores, BO3 SAB stems,
newer-title cores -- see "Structural overlap has now failed to predict yield three times" above,
now effectively a fourth and fifth instance). `mcdp/` was not a generalisable trick; it was a
specific, large (second-biggest material directory in Cold War) exception, and the diagnostic that
explains *why* it worked does not identify other cases that will. **Do not re-run this ranking
expecting another `mcdp/`** -- treat it as closed unless the corpus grows by an order of magnitude,
not the ~2x it has grown since the ranking was last taken.

## Widening `--top` beyond 100,000 endings still pays at this corpus size -- 2026-09-20

`uncarried_endings_allboundary_20260829-172236.py`'s own docstring calls 100,000 "the measured
sweet spot" from 2026-08-23 (20,000 gave 602, 100,000 gave 2,553, 300,000 gave 1,470, combined
both games on a much smaller corpus). Worth re-checking after everything above, since the corpus
driving the ending ranking has grown several times over since that sweet spot was measured.

`--top 300000` (2 segments, general, otherwise identical to the depth-2 run earlier in this
session): 1,877,309 cores x 300,000 endings, 563.2B candidates. **Cold War: 28 new** (5 image, 21
material, 1 sound_alias, 1 xmodel) -- on top of the 51 the top-100,000 cut of the same corpus
already found, so this is genuinely additional reach from the extra 200,000 endings, not a
re-discovery. Run against Black Ops 4 with the identical plan: **119 new** (8 image, 67 material,
8 xanim, 36 xmodel). `derive_closure` afterward added 11 more on Cold War, 17 more on Black Ops 4
(`final_byte` solved-backwards contributing 6 of those). Submitted as
[#2155](https://github.com/KingslayerKyle/hash-slinging-slasher/pull/2155) (Cold War, 39) and
[#2154](https://github.com/KingslayerKyle/hash-slinging-slasher/pull/2154) (Black Ops 4).

The 2026-08-23 conclusion ("100,000 is the sweet spot, 300,000 is worse") was measured on a
smaller, combined-both-games corpus and should not be treated as fixed -- like the segment-depth
axis, the right cut of the endings list moves as the corpus that generates it grows. Re-check
`--top` sizing the same way segment depth was re-checked here, rather than trusting a
three-week-old sweet spot. **`--top 300000` at segment depth 3, done next session:** 1,878,102 cores x 300,000 endings,
563.4B candidates. **Cold War 8 new** (material), **Black Ops 4 18 new** (1 image, 11 material, 6
xmodel), closure adding 0 and 2 respectively. Submitted as
[#2157](https://github.com/KingslayerKyle/hash-slinging-slasher/pull/2157) (Cold War) and
[#2156](https://github.com/KingslayerKyle/hash-slinging-slasher/pull/2156) (Black Ops 4). Smaller
than depth 2's top-300k result (28/119) but still real -- the two strong depths do not scale
identically when the ending cap is widened, and both are now worth diminishing but nonzero returns
at 300k. **The sound side's own `--top` widening, done next session:** sound only has 187,100 uncarried
endings total at this corpus size (all of it, not a top-N cut), against the 100,000-cap used
throughout the earlier sound runs -- so this is the full sound ending vocabulary, not an arbitrary
wider number. 2,527,789 cores x 187,100 endings, 472.9B candidates. **Cold War: 13 new** (1 image,
6 material, 6 sound_alias), **Black Ops 4: 38 new** (8 image, 12 material, 2 sound_alias, 14
xanim, 2 xmodel). Closure added 10 more on Cold War, 1 more on Black Ops 4. Submitted as
[#2159](https://github.com/KingslayerKyle/hash-slinging-slasher/pull/2159) (Cold War) and
[#2158](https://github.com/KingslayerKyle/hash-slinging-slasher/pull/2158) (Black Ops 4).

**Both the segment-depth axis and the `--top` widening axis are now explored for general and
sound, both games.** Further widening either axis without a substantially larger corpus is
unlikely to pay based on the diminishing pattern already measured (depths 1 and 4 weaker than 2
and 3; `--top` widening from 100k to the full/300k vocabulary added roughly half again what the
default found, not another multiple). The next step change here needs either real corpus growth
from other contributors, or a genuinely different candidate-generation shape.

**Quick re-check, `family_grid.py --top 61`, both games, 2026-09-21:** still fully spent (0 new,
both games) despite the corpus having grown by roughly 1,300 confirmed names since the last check.
Confirms the earlier finding was not a stale-corpus artifact -- the shared-tail grid restriction
itself is exhausted at every threshold this generator's own knobs can reach; corpus growth alone
does not reopen it. Do not re-check again without a new admission threshold or a much larger jump.

**`confirm_variants swaps` at its established Cold War knee (16,000 tokens), re-checked again
2026-09-21.** Method 4's own note says to re-measure the knee after a large enough gain elsewhere,
and this session's all-boundary work added roughly 900 Cold War names since the 2026-09-14 re-check
(which found only 3 new off a much smaller gain). 502.3B variants in 6,512s, **34 new** this time --
18 material, 7 sound_alias, 6 image, 2 xanim, 1 xmodel. An order of magnitude more than the last
check, off the same fixed 16,000-token knee: this method's yield tracks total corpus growth, not
just growth in the specific pools it targets, and is worth re-running after *any* large batch of
gains, not only ones in the same asset types.

Run against Black Ops 4 with the same knee: 495.7B variants, **120 new** (18 image, 70 material, 5
sound_alias, 5 xanim, 22 xmodel) plus 5 more from closure. Submitted as
[#2160](https://github.com/KingslayerKyle/hash-slinging-slasher/pull/2160) (Cold War) and
[#2161](https://github.com/KingslayerKyle/hash-slinging-slasher/pull/2161) (Black Ops 4). Both
games paid substantially more than their last check, confirming this is a method worth
re-triggering after any large gain rather than one to leave at its last-measured knee
indefinitely.

**Plain (non-swap) `confirm_variants`, re-checked 2026-09-22.** Last checked 2026-09-14 at 0 new.
10.7B variants, ~355s per game (free next to `swaps`). **Cold War: 4 new** (sound_alias). **Black
Ops 4: 3 new** (image). Closure added 0 on both. Submitted as PR #2163 (Cold War) and #2162 (Black
Ops 4). Small, but the point of re-running this one specifically is that it costs six minutes
total for both games -- worth doing after every large batch regardless of how small the last
result was, since the cost of checking is close to zero.

## A new method: all-boundary cores crossed with endings this project alone discovered — 2026-09-22

Every all-boundary run so far (`uncarried_endings_allboundary_20260829-172236.py`, this session's
segment-depth and `--top`-widening sweeps) takes its ending vocabulary from the *union* of
published and confirmed names, and `--confirmed-only` restricts the **core** side to names this
project alone found. Nothing restricted the **ending** side the same way.

`contrib/confirmed_only_endings.py` (new, written this session) does that mirror: it counts
endings only on names in `findings/` and merged submissions, throws away any ending that also
appears on a *published* name, and crosses the survivors against the full (published + confirmed)
core list. The idea: an ending this project discovered but no published table has ever shown is
evidence the corpus's own vocabulary never carried it -- so it is worth asking of every core, not
just the handful it was first found on.

**Cold War, general:** 19,504 endings appear only on this project's own confirmed names (heading
68,297 of them -- a fifth of everything this machine has confirmed ends in something no published
name does), crossed with 1,878,566 all-boundary cores, 36.6B candidates. **3 new** (sound_alias).
**Cold War, sound:** 60,857 confirmed-only sound endings (heading 190,221 confirmed sound names)
x 2,531,897 sound cores, 154B candidates. **34 new**, all material. Black Ops 4: general **11 new**
(2 image, 5 material, 3 sound_alias, 1 xmodel), sound **3 new** (2 material, 1 xmodel). Closure
added 0 on both games. Submitted as
[#2165](https://github.com/KingslayerKyle/hash-slinging-slasher/pull/2165) (Cold War, 37) and
[#2164](https://github.com/KingslayerKyle/hash-slinging-slasher/pull/2164) (Black Ops 4, 14).

**The sound half paying 34 material names off a sound-vocabulary ending list is the interesting
part**, and it repeats the pattern from the confirmed-only-cores work earlier this session: a
candidate assembled from sound-shaped pieces is still checked against every wanted pool, and
segment-cut fragments do not respect the sound/general boundary the way whole names do. `--script
contrib/confirmed_only_endings.py` is carried into the pull request, so this is now a repeatable
method rather than a one-off script. **Worth re-running after any batch of new confirms**, since
the confirmed-only ending list grows with the corpus the same way the confirmed-only core list
does.

**Segment depth 3, done immediately after, same session:** the new script takes `--segments` the
same way the all-boundary generator does. General: 31,472 confirmed-only endings x 1,879,251 cores,
59.1B candidates -- **Cold War 5 new**, **Black Ops 4 17 new**. Sound: 104,782 confirmed-only sound
endings (capped at the default 100,000) x 2,531,943 sound cores, 253.2B candidates -- **Cold War 12
new**, **Black Ops 4 11 new**. Closure added 3 more on Cold War, 0 on Black Ops 4. Submitted as
[#2167](https://github.com/KingslayerKyle/hash-slinging-slasher/pull/2167) (Cold War, 20) and
[#2166](https://github.com/KingslayerKyle/hash-slinging-slasher/pull/2166) (Black Ops 4, 31). Same
shape as the all-boundary segment-depth axis: depth 3 pays roughly as well as depth 2, worth the
same 1-and-4 check before calling this axis closed.

**Depths 1 and 4, general only, closed the axis the same way as the all-boundary sweep did:**
depth 1 (2,574 confirmed-only endings, 4.8B candidates) gave **1 new on Cold War, 0 on Black Ops
4**; depth 4 (37,986 endings, 8.9B candidates) gave **0 on Cold War, 6 on Black Ops 4** (closure
added 0 further on both). Submitted as
[#2169](https://github.com/KingslayerKyle/hash-slinging-slasher/pull/2169) (Cold War) and
[#2168](https://github.com/KingslayerKyle/hash-slinging-slasher/pull/2168) (Black Ops 4). Confirms
the same 2-and-3-strong, 1-and-4-weak shape found on the all-boundary sweep proper -- this new
method's segment-depth axis is now closed the same way, at general depths 1-4 (sound only checked
at 2 and 3, both strong; 1 and 4 untried for sound specifically and lower priority given the
general pattern).

**Sound depths 1 and 4, done to close the sound side out too:** depth 1 (11,623 endings, 29.4B
candidates) gave **2 new on Cold War, 1 on Black Ops 4**; depth 4 (100,000-capped from 120,534,
253.2B candidates) gave **3 new on Cold War, 11 on Black Ops 4**. Submitted as
[#2171](https://github.com/KingslayerKyle/hash-slinging-slasher/pull/2171) (Cold War) and
[#2170](https://github.com/KingslayerKyle/hash-slinging-slasher/pull/2170) (Black Ops 4). Sound
depth 4 outperforming depth 1 here (11 vs 1 on Black Ops 4) breaks from the general-side pattern
where 1 and 4 were both weak -- worth remembering that the two halves' segment-depth curves are
not identical, so closing one does not tell you the other is closed too.

**Running total for the confirmed-only-endings method, this session, all depths both halves:**
Cold War 3+34+5+12+1+0+2+3 = **60**. Black Ops 4 11+3+17+11+0+6+1+11 = **60**.

**Routine refresh, 2026-09-24, after `cod-name-db` advanced two days (published names 2,247,023 ->
2,252,063).** Regenerated the default-depth (2 segments, top 100,000) general all-boundary cores
and re-ran the plain sweep: **5 new on Cold War, 4 on Black Ops 4**, closure adding 0 to either.
Small, as expected from two days of upstream growth rather than a large local batch, but the
pattern holds -- this stem list is worth regenerating and re-running on the cheap default
configuration any time `start` reports the tables moved, not only after a big session of one's
own.

## Purely self-referential recombination: dead for general, weakly live for sound — 2026-09-24

Added `--confirmed-only-cores` to `contrib/confirmed_only_endings.py`, so both the core *and*
ending vocabulary can be restricted to names this project alone confirmed at once -- nothing
published on either side. This tests the strongest form of the standing "recombining across names
is dead" lesson: not just reusing pieces from different names, but reusing pieces from names
*this project itself invented*, with no published material anywhere in the candidate.

**General: 19,507 endings x 87,483 cores, 1.7B candidates -- 0 on both games.** Consistent with
every other cross-type and cross-name recombination measured dead in this file.

**Sound: 60,858 endings x 392,464 cores, 23.9B candidates -- 4 new on Cold War (1 image, 3
material), 2 new on Black Ops 4 (2 xmodel).** Small, but not zero, and the only shape in this
purely-self-referential family that returns anything. Submitted as
[#2183](https://github.com/KingslayerKyle/hash-slinging-slasher/pull/2183). Consistent with the
pattern already seen twice this session (confirmed-only-cores, confirmed-only-endings): sound
vocabulary generalises slightly better across the general/sound wanted-pool boundary than general
vocabulary does, likely because sound path segments are more numerous and more loosely coupled to
a single asset's identity than a material or model core is. **Not worth pursuing further as a
dedicated method** -- the yield here is small enough that it is better understood as confirming
where the boundary of "recombination is dead" sits than as a productive method in its own right.

## Segment depth 5, fresh, both halves — the all-boundary axis's true floor — 2026-09-24

`contrib/ab_sound_cores_seg5.txt`/`ab_sound_ends_seg5.txt` sat in `contrib/` since 2026-09-02,
evidence depth 5 had been tried before (registry rows exist from 2026-09-01/09), but never
re-checked with a refreshed corpus the way depths 1-4 were earlier this session. Regenerated
fresh and ran both halves, both games: **general, 998,300 uncarried 5-segment endings (top
100,000) x 1,880,519 cores, 188.1B candidates -- 0 on Cold War, 2 on Black Ops 4. Sound, 624,647
endings (top 100,000) x 2,533,611 cores, 253.4B candidates -- 0 on Cold War, 5 on Black Ops 4.**
Closure added 0 to either game.

This is the clearest confirmation yet that the segment-depth curve genuinely peaks at 2-3 and
decays past it rather than merely looking that way on a stale sample: even a fully fresh depth-5
core and ending list, on the same corpus that made depths 2 and 3 pay 30-100+ names each, returns
single digits. **The segment-depth axis is closed for real now** -- 1 through 5 measured fresh
this session, on both the original all-boundary method and its confirmed-only-endings variant,
and the shape holds every time. Submitted as
[#2184](https://github.com/KingslayerKyle/hash-slinging-slasher/pull/2184) (Black Ops 4, 7).

## The third confirmed-only axis, beginnings, is dead — 2026-09-24

Cores and endings each had a confirmed-only variant that paid; the natural third leg is
beginnings. `contrib/confirmed_only_beginnings.py` (new) finds leading segments (the
`uncarried.py`/`redecorations.py` convention) that appear only on names this project confirmed,
never on any published name: **654 general beginnings** (>=3 names each, heading 95,039 confirmed
names) and **820 sound beginnings** (heading 167,946 confirmed names) qualify -- large sets, on
the same order as the confirmed-only endings lists that worked.

Crossed against the held/all-boundary vocabulary (general: 955,217 stems, 625.7M candidates;
sound: 2,527,789 stems, 2.1B candidates), both cheap: **0 matched, every combination, both
general and sound, both games.**

This closes the confirmed-only family at three for three tried, two live (cores, endings) and one
dead (beginnings). It also extends the redecoration finding from earlier this session -- beginning
vocabulary discovered by this project does not generalise across cores any better than beginning
vocabulary discovered from the published tables did. **The asymmetry is now measured rather than
assumed: whatever makes a core or an ending transferable across names does not hold for a
beginning**, on either the published or the confirmed-only cut of it. Not worth trying a fourth
beginning-shaped variant without a reason to expect this specific asymmetry to break.

**One more check while sound tooling was already at hand:** re-ran confirmed-only sound
endings/cores against Black Ops 4 with `--no-fold`, on the theory that some confirmed-only sound
fragments might carry literal backslashes reachable only unfolded. **0 new.** The candidates this
generator builds are overwhelmingly folded-convention strings already (most confirmed sound names
in the corpus are Cold War's), so `--no-fold` was mostly a no-op on them rather than a real test
of the backslash-preserving Black Ops 4 SAB convention -- worth remembering that this flag only
matters when the *candidate itself* contains a backslash, not just because the target pool does.

**Widening confirmed-only sound endings past the 100,000 cap at depth 4** (120,548 total, all of
them this time): 305.4B candidates, **0 on Cold War, 1 on Black Ops 4** -- and even that 1 was
independently found and claimed by another contributor in the minutes between the pass finishing
and `submit` running, so the net send was 0. A clean, honest zero on a repository this actively
shared, not a bug. **The confirmed-only-endings family, across every depth, every `--top` size,
and now every cap-widening tried, is genuinely at its floor for this corpus size.** Stop widening
this specific axis; the next reopening comes from real corpus growth, not from re-slicing the
same vocabulary a different way.

## Checking out other contributors' methods, and a real find in one — 2026-09-25

Rebasing onto three days of upstream merges (301,776 -> 320,090 names, a jump of over 18,000)
pulled in several new generators from other contributors, registered in the raw efficiency table
but never written up here narratively: `coordinated_identifiers.py`, `coordinated_sound_phrases.py`,
`single_to_coordinated_sound.py`, `sound_seed_siblings.py`, four `paired_animation_rules.py`
variants, `image_delta_derivations.py`, `material_delta_plan.py`, `model_counterpart_offsets.py`,
`attachment_triplet_plan.py`, and two `bo4_reflection_probes.py` variants. Ran the general-shaped
ones fresh against the current corpus rather than assuming their registry "spent"/"untried" tags
still held.

**`coordinated_identifiers.py` -- the real find.** Finds tokens that repeat *within the same name*
(e.g. two occurrences of a word), builds a template with every occurrence of that token masked,
and looks for other names sharing that exact template shape with a *different* repeated token
filling it. Two such sibling fills, seen twice, become a substitution rule -- and unlike ordinary
slot substitution, applying the rule changes **every** occurrence of the token in a name at once,
not just one. Run fresh: sound_asset alone offered 7,234 supported rules from 86,420 sibling
controls and reconstructed 1,552,246 already-known names as a positive control (out of 696,655
sound candidates); material and image each supported a handful of rules too. **6 new Cold War
`sound_asset` names** -- the hardest pool in either game to reach, per every dead-end this file
already records against it. 0 on Black Ops 4 either fold direction, and 0 on the visual (image/
material/xanim/xmodel) candidates on both games. `derive_closure` afterward added 19 more on Cold
War and 81 more on Black Ops 4 -- almost all of that second number is the corpus jump reopening
derivations that had gone stale, not this method directly, but running it was what triggered
checking. Submitted as [#2190](https://github.com/KingslayerKyle/hash-slinging-slasher/pull/2190)
(Cold War, 25) and #2189 (Black Ops 4, 81).

**`model_counterpart_offsets.py` -- clever, and already spent.** Learns pairs of (label token,
paired numeric offset) that change together at a fixed relative distance in xmodel names -- e.g. a
component name change that always comes with the same +N shift in a nearby number -- requiring
three independent sibling frames and three distinct source values before trusting a rule. Fresh
run: 2,194 total rules across the sixteen measured offsets (-8 to +8), tens of thousands of control
hits confirming the rules reconstruct real names, 1,892,715 final candidates. **0 new on either
game.** The generator's own controls prove the relation is real; the corpus this project already
holds has already had every reachable instance of it extracted (consistent with this being
registered "spent" in the table already).

**`attachment_triplet_plan.py` -- correct shape, no headroom left.** The `i_attach_` image family
specifically: learns *triplets* of fields that change together across independently-witnessed
texture cores (2+ frames required), then crosses the recombined cores with the 8 measured channel
suffixes. 664 rules, 1,638 controls, 3,498 new cores x 8 channels = 31,482 candidates. **0 on
either game.** Same story as the offsets method -- well-designed, well-controlled, and this
specific attachment-texture corner of the image family has nothing left in it right now.

**Not re-run: the four `paired_animation_rules.py` variants, `image_delta_derivations.py`,
`material_delta_plan.py`, `coordinated_sound_phrases.py`, `single_to_coordinated_sound.py`,
`sound_seed_siblings.py`, and both `bo4_reflection_probes.py` variants.** The delta-shaped ones
(`image_delta_derivations`, `material_delta_plan`) take an explicit list of *newly confirmed*
names as their argument rather than reading the whole corpus -- they are a human's hand-tool for
following up one specific discovery batch immediately, not a fresh search in their own right, and
`derive_closure.py`'s `image_channels`/`materials_from_images`/`image_siblings` derivations already
re-run the same relations over the *entire* corpus every round, which is a superset of what a delta
tool targeted at one batch could reach. Worth reading before reinventing the same idea, not worth
running separately when the closure already covers the ground. The sound- and animation-specific
ones were not read closely enough this session to judge; flagging them here so the next session
does not have to re-discover that they exist.

**Following that, the all-boundary methods invented earlier this session were re-run against the
same +18,000-name jump.** General: fresh cores (1,889,746) x top-100,000 endings -- **10 new on
Cold War, 25 on Black Ops 4.** Sound: fresh cores (2,547,327) x top-100,000 sound endings -- **10
new on Cold War (including 2 sound_alias), 16 on Black Ops 4.** Closure added 6 more on Cold War,
11 more on Black Ops 4. Submitted as [#2192](https://github.com/KingslayerKyle/hash-slinging-slasher/pull/2192)
(Cold War, 26) and #2191 (Black Ops 4, 52). **Confirms directly, on the same corpus jump, that
regenerating these lists after any large merge event pays about as well as it did the first time
this session discovered the lists were stale** -- this is now a routine to run after `start`
reports a large jump in merged submissions, not a one-off insight.

**The confirmed-only-endings variant paid the same way, and Black Ops 4's image pool had a real
vein in it.** General: 31,248 confirmed-only endings x 1,889,792 cores, 59.1B candidates -- **12
new on Cold War (11 material, 1 xmodel), 74 new on Black Ops 4 (73 image, 1 xmodel).** The 73-image
figure landed almost entirely in the last slice of the run, consistent with one dense pocket of
reachable names rather than a uniform spread. Sound: 73,352 confirmed-only sound endings x
2,547,413 cores, 186.9B candidates -- 0 on Cold War, 3 on Black Ops 4. Closure added 4 more on
Cold War, 0 on Black Ops 4. Submitted as
[#2194](https://github.com/KingslayerKyle/hash-slinging-slasher/pull/2194) (Cold War, 16) and
#2193 (Black Ops 4, 77).

**Widened to `--top 300000` to chase the dense Black Ops 4 image vein** (566.9B candidates, same
1,889,847 cores): the vein did not repeat -- **12 new on Black Ops 4** this time (4 material, 1
xanim, 7 xmodel, no additional image), **2 new on Cold War** (material, sound_alias). Closure
added 0 on Cold War, 2 on Black Ops 4. Submitted as
[#2196](https://github.com/KingslayerKyle/hash-slinging-slasher/pull/2196) (Cold War) and #2195
(Black Ops 4). Consistent with the standing lesson that a rich pocket found at one ending-cap size
does not mean widening further finds more of the *same* pocket -- it finds whatever else is
reachable at the new size, which can be a different pool entirely.

Re-run per method 4's own note ("re-measuring the knee position after a large enough gain
elsewhere is a cheap check") after the corpus grew from 245,673 to 295,855+ merged names via a
rebase onto three days of upstream PRs. 487.3 billion candidates, 7,139s, **16 matched, 3 new**
(all `xanim`) — submitted as [#2124](https://github.com/KingslayerKyle/hash-slinging-slasher/pull/2124).
Small next to the original 128-name run at this same pool size (2026-08-29), consistent with the
standing "treat as spent past the knee unless the corpus has grown substantially" guidance: the
corpus did grow, and it paid a little, not a lot. Plain (non-swap) `confirm_variants` was re-run
alongside it for the first time in a while: 10.5 billion candidates, 6 matched, **0 new**.

**A measurement artifact worth flagging for whoever next trusts `derive_closure`'s own delta.**
Immediately after submitting the 3 `swaps` names, `derive_closure.py --anyway` reported "image
siblings of confirmed materials +10" with no corresponding new run folder under
`findings/blkopscw/`, and the following `submit` found nothing pending. The likely cause: this
repository is shared by several very active contributors (Kenshin9977 and ImSimpy alone merged
dozens of pull requests in the hours around this session), and `derive_closure.py` measures a
derivation's yield as `confirmed_total()` before vs. after — a raw count that includes merged
submissions, not just this run's own output. If somebody else's batch merges in the few seconds
between those two reads, it is counted as this derivation's gain. `submit`'s own ledger (which
tracks specific run folders rather than a raw total) is the trustworthy number here, and it said
zero. Worth fixing in `derive_closure.py` — diff the actual run folder's contents, not a global
total — on a repository this actively shared.

## A new idea from reading `coordinated_identifiers.py`: pool the evidence across asset types — dead, cleanly — 2026-09-25

`coordinated_identifiers.py` (previous section) learns its substitution rules once per asset type,
with each type's names as a closed world: a rule like `usa<->rus` can only be *supported* by two
xmodel siblings sharing a template, never by an xmodel sibling and a material sibling together,
even though the token itself is game vocabulary (operator codes, faction names, camo colours,
weapon variants) with no reason to respect the type boundary. Wrote
`contrib/coordinated_identifiers_crosstype.py` to test the obvious fix: pool every type's known
names (xmodel, material, image, xanim, sound_asset, sound_alias) into one flat evidence set before
looking for repeated-token templates, learn rules from whichever frames support them regardless of
type, then apply the rules back across every type's names.

Caught one thing before running it: the first draft computed a "how many rules pooled across
types" diagnostic with a second nested pass back over every row for every supported pair, which
does not belong in a script touching low millions of rows. Restructured so `groups` maps
`template -> {token: set(kinds it wore)}` and the cross-kind check falls out of the one existing
pass over `groups.items()` instead.

Run against the corpus: 1,173,159 known names pooled, 320,048 repeated-token rows, 7,246 supported
rules, 926,631 candidates (rebuilding 1,557,954 already-known names as a positive control — a
healthy ratio, same shape as the per-type original). But **`cross_kind_supported_pairs: 0`** —
of every supported rule, not one drew its two required sibling observations from more than one
asset kind. Confirmed against the game anyway, all four configurations (Cold War visual, Cold War
sound, Black Ops 4 visual, Black Ops 4 sound both folds): **0 new names in every case** — the
candidate files were classified back down into the same per-type rows as the original method's own
run and added nothing beyond what it already found.

**The hypothesis was clean and the falsification is just as clean.** Template shape here is the
*entire* token sequence around the masked position, not just the token itself — and each asset
type's naming convention is specific enough (segment count, which fields sit next to which, which
separators appear) that a material name and an xmodel name essentially never produce the identical
template even when they share the exact vocabulary word. Pooling the evidence sets costs nothing to
try and answers a real question (does this project's naming convention share structure across
types, at the template-shape granularity `coordinated_identifiers` uses) with a firm no. A future
attempt at cross-type transfer would need a looser template — matching on token identity and
position-from-edge rather than the full masked sequence — to have any chance; that is a different,
larger rewrite and not attempted here since the per-type original is already registered and the
loosening could just as easily explode false-positive rule pairs as find real ones.

## A new method: substitution rules applied to fragments, not whole names — 2026-09-25

Built after the cross-type pooling test above closed clean: `coordinated_identifiers.py` learns a
substitution rule (e.g. a faction code or camo colour interchangeable with another) from two whole
names sharing an identical masked template, then only ever applies the rule back onto other WHOLE
names that already contain the token repeated. That is a narrow use of a fact that is not itself
narrow — token A and token B being the same *kind* of thing in this game's naming does not depend
on the particular name it was witnessed in.

`contrib/rule_substituted_cores.py` applies each learned rule to every **all-boundary core**
(method 25: a known name cut at every segment boundary) that carries the token anywhere, repeated
or not, and keeps only the substituted cores that are **not already in today's base all-boundary
core list** — the base list against these same endings is stale ground this session already
measured today, so only the incremental new fragments are worth spending candidates on. Rules are
still learned **per type** (a fresh test the same day found cross-type template pooling supports
zero rules — see above) but applied to the **pooled** core list, since a core is already
type-agnostic in every other all-boundary run here.

Crossed the new fragments only against the standing wide ending lists with the plan engine:

| pass | new cores | endings | candidates | Cold War | Black Ops 4 |
|---|---|---|---|---|---|
| visual (xmodel/material/image/xanim) | 150,356 (from 7 rule pairs, mostly image/material) | `ab_ends.txt`, 300,000 | 45.1B | **4** (3 image, 1 material) | 0 |
| sound (sound_asset/sound_alias) | 28,931,455 (from 3,618 rule pairs, almost all `sound_asset`) | `ab_sound_ends.txt`, 100,000, folded | 2.89T across 8 slices | **26** (6 image, 12 material, 8 sound_alias) | **10** (7 material, 2 xmodel, 1 sound_alias) -- finished 2026-09-27, 221m8s solo, no contention |

`derive_closure` afterward added 3 more Cold War names off the visual seeds (image siblings) and
reported 13 more off the sound seeds (7 image siblings, 2 materials from image cores, 2 image
channels, 2 final-byte solves) -- but only **10** of those 13 actually landed in the pull request.
This is the same measurement artifact this file already recorded on 2026-08-22: `derive_closure`
reports its yield as a raw confirmed-count delta, and `submit`'s ledger (which tracks the actual
run folder) is the trustworthy number on a repository this actively shared -- three of the
"closure" names had evidently already been claimed by another contributor's merge in the seconds
between the two counts. Recording the true number rather than the closure's self-report. 30 direct
names plus 13 closure-*reported* (10 closure-*landed*) is still a strong multiplier for free.
Submitted as
[#2197](https://github.com/KingslayerKyle/hash-slinging-slasher/pull/2197) (visual, 4),
[#2198](https://github.com/KingslayerKyle/hash-slinging-slasher/pull/2198) (visual closure, 3),
[#2199](https://github.com/KingslayerKyle/hash-slinging-slasher/pull/2199) (sound, 26), and
[#2200](https://github.com/KingslayerKyle/hash-slinging-slasher/pull/2200) (sound closure, 10).

**The ending-side mirror, `contrib/rule_substituted_endings.py`, 2026-09-26.** The core-side pass
above only ever offers a substituted CORE against the standing endings; a rule-eligible token can
just as easily sit in the ending half of a name, which the core-side pass cannot reach no matter
how it is run. Mirrors the same logic onto `ab_ends.txt` / `ab_sound_ends.txt` instead, keeping
only the endings not already in the standing lists, and crosses them against the *standing*
(unchanged) core lists -- the untested quarter of the 2x2 (new cores x new endings remains
untested and is not expected to pay much given how sparse the visual rule set is).

| pass | new endings | cores | candidates | Cold War | Black Ops 4 |
|---|---|---|---|---|---|
| visual | 4,137 | `ab_cores.txt`, 1,889,847 | 7.8B | **2** (material) | **2** (material) |
| sound | 186,500 | `ab_sound_cores.txt`, 2,547,327 | 475.2B | **exhausted without running** | **10** (3 image, 3 material, 2 xanim, 2 xmodel) |

Submitted as [#2202](https://github.com/KingslayerKyle/hash-slinging-slasher/pull/2202) (Cold War
visual-endings, 2) and [#2201](https://github.com/KingslayerKyle/hash-slinging-slasher/pull/2201)
(Black Ops 4 visual-endings, 2). Finished 2026-09-27: the Cold War sound-ending fingerprint turned
out identical to an already-submitted pass ([#2203](https://github.com/KingslayerKyle/hash-slinging-slasher/pull/2203),
2026-09-25) and `confirm_plan` declined in 3 seconds rather than reproduce it -- so nothing was lost
by finishing this method's Cold War half, there was simply nothing left on it. Black Ops 4 ran
clean in 31 minutes and found 10, submitted as
[#2208](https://github.com/KingslayerKyle/hash-slinging-slasher/pull/2208).

**Why the sound half paid so much more than the visual half.** `coordinated_identifiers` itself
found this earlier the same day -- `sound_asset` alone offered 7,234 supported rules against a
handful each for material and image -- so a much richer rule vocabulary was always going to turn
into a much richer substituted-core list once applied to the pooled all-boundary cores (28.9M new
sound cores against 150K new visual ones, roughly 200x). The sound pass needed 8 engine-managed
slices (~27 minutes each, ~3.5 hours total) purely because of that size, not because of anything
unusual in the search itself.

**Spent by:** the same axis that limits `coordinated_identifiers` itself -- the number of
repeated-token sibling frames available to learn a rule from in the first place. Re-run whenever
the corpus grows enough to teach the base method new rules; a stale rule set applied to a fresh
core list is still bounded by what the rules know, not by what the cores offer.

**Finished 2026-09-27** (the prior session's run had been killed with the terminal, not completed
-- nothing was actually still running when this session started, despite the note above; a fresh
solo run was needed regardless). Both remaining pieces confirmed: the Black Ops 4 sound core-side
pass (10 names, 221 minutes solo, no contention -- compare the 27 min/slice, ~3.5h total figure
above, which was under three-way contention) and the sound-ending pass (Black Ops 4 10 names in 31
minutes; Cold War turned out already exhausted by a different-looking pass with the same
fingerprint, so it declined in 3 seconds rather than repeat #2203). `rule_substituted_cores` /
`rule_substituted_endings` are now fully run on both games, both halves -- nothing left queued on
this method. The core-side visual pass returned 0 on Black Ops 4, but the ending-side visual pass
found 2, so "0 on Black Ops 4" was a property of that one pass rather than of the game, and almost
all of the rule vocabulary and yield sits on the sound side regardless of game.

## A second fragment-generalisation: slotswap's context vocabulary applied to cores — 2026-09-26

Method 10 (`slotswap.py` / sibling token substitution) measures, for every token slot in every
known name, what the corpus has seen filling a slot with the same left/right neighbours -- then
only ever substitutes inside WHOLE known names, the same restriction `rule_substituted_cores.py`
found and removed for `coordinated_identifiers.py` the day before. `contrib/slotswap_cores.py`
applies the identical fix here: measure slotswap's own alphabet unchanged, then walk every
all-boundary core and substitute at every INTERIOR slot (every token except the one sitting at the
core's own cut boundary, which the ending half of the cross product already varies), keep only
cores not already in the base all-boundary list, and cross the new fragments against the standing
wide ending lists.

Slotswap's context vocabulary turned out to be far richer than `coordinated_identifiers`' repeated-
token rules (111,143 slot contexts against 7 rule pairs for visual), so this reaches much further:
**35.0M new visual cores** and **30.2M new sound cores**, against 150K and 28.9M respectively from
the first fragment method. Crossed against the same standing wide ending lists (`ab_ends.txt`
300,000 / `ab_sound_ends.txt` 100,000): 10.5T visual candidates, 3.0T sound candidates -- run
against Cold War only so far, in engine-managed 8-slice batches, competing for CPU against the
Black Ops 4 sound-core rulesub pass and each other, which slowed every pass's own throughput
without losing any work (three-way scheduling fairness, not corruption or restart -- confirmed by
watching stem counts only ever increase within a slice).

**Partial results, as of this pause (both passes still running, several slices left):**

| pass | new cores | slices done | found so far |
|---|---|---|---|
| visual, Cold War | 35,015,108 (from 111,143 slot contexts) | 2 of 8 | 25 (slice 1), slice 2 in progress |
| sound, Cold War | 30,237,084 (same alphabet) | 4 of 8 | 21 + 2 + 2 = 25 across slices 1/3/4, slice 2 clean |

Submitted incrementally as each slice checkpoints (never wait for the whole run — a checkpoint is
already safe): visual slice 1 in
[#2206](https://github.com/KingslayerKyle/hash-slinging-slasher/pull/2206) (7 landed of 25 found --
the rest were claimed by other contributors during an unusually long `submit` queue delay under
three-way CPU contention, which is the system working as designed, not a bug); sound slices in
[#2204](https://github.com/KingslayerKyle/hash-slinging-slasher/pull/2204) (21),
[#2207](https://github.com/KingslayerKyle/hash-slinging-slasher/pull/2207) (2). Still to run when
resumed: the remaining slices of both Cold War passes, then both Black Ops 4 folds of each, then
`derive_closure`, then a final tally to replace this partial entry.

**A submit-latency lesson worth keeping.** Running three CPU-saturating searches at once is fine
for the searches themselves (fair scheduling, no corruption), but it starves anything else on the
box -- `submit.exe` took over 40 minutes with zero output on one occasion here, confirmed alive
throughout by process inspection rather than log output. Nothing was wrong; it was just waiting for
a CPU timeslice the searches were not giving up. Worth knowing before assuming a silent submit has
hung.

**Status as of 2026-09-27: still exactly where the table above left it.** The processes above did
not survive the session that started them -- there was nothing running when this session opened
(`tasklist` showed no `confirm_*` process), and the accumulated 7-run empty streak in
`state/empty_runs.txt` says at least some continuation was attempted and came back empty before the
machine went idle. This session spent its time budget finishing `rule_substituted_*` instead (see
above) and did not touch `slotswap_cores`.

**Important for whoever resumes this: `confirm_plan` has no partial-slice resume.** The "8 slices"
are all run inside one process invocation (`src/bin/confirm_plan.rs`, `SLICES = 8`, one call to
`run_best` per chunk of the stem list, checkpointed after each) -- there is no flag or state file
that lets a fresh invocation pick up at slice 5. Re-running `plans/slotswap_cores_visual.txt`
verbatim redoes all 8 slices, including the ~2 already confirmed done. To actually resume only the
remaining ground: the stem files are written `sorted()` by the generator, so slice boundaries are
positional chunks of that sorted order (`plan.stems.chunks(ceil(N/8))`) -- take the last N/8 * (8 -
done) lines of `contrib/slotswap_cores_new.txt` (or `_sound_`) into a new file, point a copy of the
plan at that instead, and only the untested tail gets searched. Nobody has built that trimmed plan
yet.

**Still queued, in priority order:** Cold War sound (4 of 8 slices remain, ~1.5T of the original
3.0T), Cold War visual (6 of 8 remain, ~7.9T of the original 10.5T), then both Black Ops 4 folds of
each (10.5T visual + 3.0T sound, neither started). At the ~230M candidates/s this machine sustains
solo (measured across two `rule_substituted` passes today, both close to the GPU.md forward-hash
figure), the full remaining set is upwards of 24 hours of machine time -- comfortably more than any
single session's budget, so plan to take it in pieces via the trimmed-plan approach above rather
than as one sitting.

**Cold War sound finished -- 2026-09-28: 76 more names, and the second half paid better than the
first.** The trimmed plan was built exactly as described above: the stem file read the way
`confirm_plan` reads it (trimmed, `hash,name` split, sorted bytewise, deduplicated -- 30,237,084
stems, none repeated), chunked at `ceil(N/8)` = 3,779,636, and everything from position 15,118,544
on written to `contrib/slotswap_sound_cores_tail_s5-8.txt` (15,118,540 stems). The plan is
`plans/slotswap_cores_sound_tail.txt`; 1.51T candidates, 0.017 expected by chance, about 1h50m at
229-235M/s with nothing else on the box. Its first slice returned nothing, and the rest returned
**76 names** ([#2213](https://github.com/KingslayerKyle/hash-slinging-slasher/pull/2213)), all kept
by `submit` -- against 45 from slices 1-4, so the ground did not thin towards the end of the sort.

What they are is the useful part: **54 material, 12 sound_alias, 5 xmodel, 4 xanim, 1 image, 0
sound_asset.** The cores are sound-shaped, but the endings list crosses them into material paths
far more often than into sound files. So the Black Ops 4 sound fold is not the obvious next run
it looks like, and the unfolded BO4 plan (`slotswap_cores_sound_nofold.txt`) is aimed at the one
pool this pass returned nothing in.

`derive_closure --game BLKOPSCW` after it: **16** (5 image siblings, 10 final byte, 1 three-byte
tail; [#2214](https://github.com/KingslayerKyle/hash-slinging-slasher/pull/2214)). Its round 2
then *reported* the corpus closed while six of its seven derivations had actually been refused by
the futility guard -- three empty derivations in a row trip it partway through a round, and
`derive_closure` counted each refusal as a zero. A rerun with `--anyway` ran all seven and did
return 0, so it was closed; `derive_closure.py` now reports a round with refusals as unknown rather
than closed and says to rerun with `--anyway`.

**Cold War visual is further back than the table says.** Its log ends with slice 2 at 97.5% and no
checkpoint, so only slice 1 of 8 is done. (`contrib/slotswap_cores_new.txt` holds 35,017,591
lines against the 35,015,108 stems the run read, which looks like a regeneration but is not: the
2,483 extra lines are duplicates, and deduplicated the file is exactly the stems that run read, so
the slice boundaries line up.) Resumed 2026-09-28 as `plans/slotswap_cores_visual_tail.txt`: slices
2-8, 30,638,219 stems, 9.19T candidates, 0.10 expected by chance.

**Cold War visual finished -- 2026-09-28: 235 names**, every one kept by `submit` (#2215-#2219).
It ran at 340-363M/s, about 55 minutes a slice -- half again faster than the ~230M/s measured
while it shared the box, so run these alone. By slice of the resumed run:

| slice | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
|---|---|---|---|---|---|---|---|
| names | 58 | 46 | 4 | 72 | 8 | 15 | 17 |

**112 image, 95 material, 20 xmodel, 8 xanim, 0 sound.** Because the stems are sorted, each slice
is a band of the alphabet, and the yield is lumpy by band rather than decaying: the first two
slices were almost entirely images and the fourth almost entirely materials. Together with the
original slice 1's 25, the whole visual plan returned **260 names from 10.5T** (1 per ~40B).
`derive_closure` after it added **48** (21 image siblings, 13 materials from image cores, 11 image
channels, 2 three-byte tails, 1 final byte; #2220) and its second round ran all seven derivations
to zero. With the sound half's 121 and its 16 of closure, slotswap cores is **445 names on Cold
War**.

**Black Ops 4 visual -- 2026-09-29: 151 names** from the full 10.5T plan, unchanged, against 52,183
unnamed ids (#2221-#2224). By slice: 77, 13, 11, 17, 8, 16, 2, 7. **78 xanim, 32 material, 24
image, 14 xmodel, 3 sound_alias** -- anims are over half of it here, against 8 of Cold War's 235, so
the same cores land on a different pool in each game and both folds are worth running.
`derive_closure --game BLKOPS04` after it: **79** (43 family gap filling off the new anims, 13
image siblings, 11 final byte, 5 channels, 4 materials from images, 2 tails, then 1 more final
byte on an `--anyway` rerun, since the guard refused 5 of 7 in round 2 -- the fixed script now says
so rather than calling it closed; #2225). The
unfolded Black Ops 4 sound plan does not need running whole: only 1,048,952 of the 30.2M sound
cores keep a backslash, and only those can reach an unfolded `sound_asset` name -- the rest would
repeat the folded search. That subset (`plans/slotswap_cores_sound_backslash_bo4.txt`, 0.10T,
about ten minutes) returned **0** on 2026-09-29. With Cold War's 0 as well, slotswap cores do not
reach `sound_asset` in either game; that pool wants a method built on SAB file structure, not on
recombined alias vocabulary.

**Black Ops 4 folded sound -- 2026-09-30: 14 names from 0.84T instead of 3.03T.** Slice 1 of the
full plan (0.38T) returned 0. Rather than run the other seven, the attribution measured on Cold War
(73 of 76 sound-pass names came from sound cores that are also visual cores) was applied directly:
the 4,611,922 shared cores in the sorted range after slice 1, x the sound endings, 0.46T
(`plans/slotswap_sound_shared_bo4.txt`): **14 names** -- 10 image, 3 xmodel, 1 material -- one per
~33B, the same density as the visual passes, #2239. The 21M sound-only cores left unsearched are
the part Cold War showed to be barren. **When a plan's yield has been attributed to part of its
stem list, run that part first on the next game.**

**The half of the cross product neither pass ran -- measured 2026-09-29.** The two plans only ever
crossed each core list with its own endings. Of the 30.2M sound cores, only 5.1M are also visual
cores, and the two endings lists share 25,761 of their 300,000 + 100,000 entries -- so sound cores
had almost never met the visual endings, although the Cold War sound pass showed they reach
material paths (54 of its 76). `plans/xcross_soundcores_visualends.txt` is exactly that missing
block: 25,151,469 sound-only cores × 274,239 visual-only endings, 6.90T, with no overlap with either
pass.

**It is dead: 0 names from the first two slices, 1.72T, on Cold War**, against roughly one name per
40B for the visual plan. Stopped there. The premise was wrong, and it could have been checked in a
minute before spending the hours: of the Cold War sound pass's 76 names, **73 came from cores that
are also visual cores**, 1 from a sound-only core, 2 from neither. The sound pass reached materials
through the 5.1M cores the two lists share -- exactly the ones this plan removed as already
searched -- so what was left was the barren part. **Before crossing two lists, attribute the finds
of the passes that motivate it** to the part of each list that produced them.

## The all-boundary snowball: this week's finds are next week's best cores -- 2026-09-29

The lesson under method 25 ("treat `ab_cores.txt` as perishable") turned out to be much stronger
than it reads. After the slotswap-cores passes above confirmed ~900 names, rebuilding the lists
with the unchanged method-25 generator (`--top 300000`) added only **1,160 cores and 144
endings** to 1.89M and 300k. Searching exactly that delta, both games:

| block | candidates / game | Cold War | Black Ops 4 |
|---|---|---|---|
| new cores x all endings | 0.35B | **161** | **39** |
| all cores x new endings | 0.27B | 7 | 3 |
| slotswap cores of the rebuilt base, not seen before (28,860) x all endings | 8.7B | 16 | 25 |
| all slotswap cores x the 144 new endings | 5.0B | 0 | 0 |
| `derive_closure` after | -- | 6 | 5 |

**262 names for about 30B candidates in total -- minutes of machine.** The new-cores block ran at one
name per ~1.7M candidates, four orders of magnitude denser than the slotswap pass (one per ~40B)
that produced the names those cores were cut from. A core cut from a name confirmed three days ago
is a fragment of something real that nobody has crossed with the endings yet; the endings already
carry the rest of the vocabulary. (#2226-#2231.)

That makes it a loop with a natural stop, so it is now `contrib/ab_snowball.py`: per round and per
half (visual, then sound), rebuild the lists, search only cores, endings and slotswap cores not in
its ledger (`contrib/ab_snowball_seen_*`, seeded from whatever is on disk the first time), close,
submit, and stop on the first round that confirms nothing. It is not a rotation -- every round's
input is the previous round's output, and an empty round ends it.

**Run it after any pass that confirms a meaningful number of names**, not on a timer: its whole
yield is the corpus growth since the last run.

First run, straight after the table above: **116 names over three rounds (93, 14, 9), then an empty
fourth**, #2232-#2236, about 40 minutes. Most of it came from the new-cores blocks again (the sound
half's 1,914 new cores gave 44 on the first round, from 0.19B) and from Black Ops 4's new slotswap
cores (25). Crossing the old lists with new endings returned 1 name in every round combined -- the
endings list barely moves, so almost all the value is in the cores.

**Two extensions measured 2026-09-30:**

- **The endings half does pay, just not through `ab_ends.txt`.** Only 144 of the week's endings
  ever reach the top-300k list, but the 1,411 names confirmed since 2026-09-25 have 8,861 boundary
  tails, 7,409 of them in neither `ab_ends.txt` nor `data/suffixes.txt`. Those tails x all 1.89M
  cores: **27 names** (19 Cold War, 8 Black Ops 4) from 28B, about one per billion
  (`plans/newname_tails_20260930.txt`, #2237/#2238). Added to `ab_snowball.py` as a fifth block,
  with its own ledger seeded from every tail that existed at the time.
- **`rule_substituted_cores.py` regenerated on the rebuilt base does not.** 258 new visual and
  28,337 new sound cores, crossed with their ending lists on both games: 3 names in total. Its
  seven repeated-token rules move far less than slotswap's 111,000 slot contexts when the corpus
  grows, so it is left out of the snowball.

**Fresh families want the whole tail universe, not the ranked endings -- 2026-09-30.** The 2,929
all-boundary cores cut from the 1,479 names confirmed since 2026-09-25 had already met the top-300k
endings through the snowball. Crossed instead with **every boundary tail of every published or
confirmed name** (5,217,100 tails; `plans/hot_cores_all_tails_20260930.txt`), 15.3B per game:
**202 names** (87 Cold War, 115 Black Ops 4), then 49 more from closure (#2243/#2244). One per
~150M.

Walking the same idea back through older confirmations (`contrib/core_rings.py`, one date ring at
a time, never re-crossing a core) shows where it comes from:

| cores of names confirmed | cores | Cold War | Black Ops 4 |
|---|---|---|---|
| 2026-09-25 to 09-30 | 2,929 | 87 | 115 |
| 2026-09-15 to 09-24 | 2,958 | 3 | 3 |
| 2026-09-01 to 09-14 | 5,139 | 4 | 3 |
| 2026-08 | 341 | 0 | 0 |

Same core counts, same tails, a 30x cliff after one week. It is not "recent cores are good"; it
is **a family found days ago meeting the tails of its own siblings**, which were confirmed at the
same moment and have not been crossed with anything. So it is now a block in every
`ab_snowball.py` round (new cores x every known tail) rather than a sweep, and `core_rings.py` is
kept for measuring rather than for grinding.

Two neighbours of it, both measured the same day and both nearly dry, so nobody need rebuild them:

- **Method 10 slotswap on the fresh names only** (`contrib/fresh_slotswap.py`, whole names,
  every slot, the corpus's own slot alphabet): 4,733 names confirmed since 2026-09-04, 169,109
  candidates, **0** on both games. A fresh family's missing members are two known pieces joined
  at a new place, not one word changed.
- **The fresh tails x the prefixes `ab_cores.txt` leaves out**: only 78,013 prefixes of known
  names are missing from it, 0.9B, **2** names. The ranked core list already carries nearly every
  prefix, so the cross that pays is fresh cores x the whole tail universe, not the reverse.
- **All cores x the long tail is not worth running.** The obvious generalisation -- every
  all-boundary core (1.89M) x the 5.0M tails `ab_ends.txt` does not carry, 9.4T -- was measured
  on a random 1% of the cores first (`plans/ab_cores_sample_x_long_tails.txt`, seed 20260930):
  **0 names from 94B on Cold War.** The long tail only pays where a fresh family's own tails are
  in it, which the snowball block already covers.
- **A second slotswap substitution on the proven substituted cores** (`contrib/second_swap.py`):
  the 556 slotswap finds rest on only 43 substituted cores that are still in the current lists,
  and a second substitution of those produces nothing the lists do not already hold. 0 candidates.
- **`xskeleton` is not a source.** Its 85,613 Cold War ids are exactly the 85,612 `xmodel` ids plus
  one -- the same names hashed -- and `xcollision` shares 57,460 of its 60,670. Naming one names the
  others; nothing flows between them.

**Sound files named after their aliases -- a thin seam into `sound_asset`, 2026-09-30.** Nothing
built on recombined alias vocabulary reaches `sound_asset` (see above). But 2,245 published sound
files have a basename -- the text before the first `.` -- that is exactly an alias name.
`contrib/alias_to_file.py` places every named alias into each folder whose files share its first
two tokens, with each extension chain that folder uses: 829,676 candidates, **3 Cold War
`sound_asset` names** (`fly/weapon/reload/sniper_cannon/fly_sniper_cannon_inspect_p1..3.ln75.pc.all.snd`),
0 on Black Ops 4 unfolded, #2247. One per 280k candidates, and the first `sound_asset` names this
project has found in a week. The convention is real but rare -- most sound files do not carry
their alias's name -- so this is worth re-running after the aliases table grows, not a mine.

## The unnamed names are made of tokens nobody has seen -- and a dictionary supplies them -- 2026-10-01

**The measurement that decides it.** `contrib/token_markov.py` learns P(token | previous two tokens)
over every name one game is known to hold in one pool, and enumerates names best-first by
threshold (OMEN-style depth-first walk, banded so nothing is held in memory). As a positive control
it is trained with 10% of the known names held out (`--holdout 0.1`):

| pool (Cold War) | held-out names regenerated within 2M candidates |
|---|---|
| `xanim` | **56%** (1 per 1,600) |
| `xmodel` | **27%** (1 per 1,060) |

Pointed at the real unnamed ids, the same walk returned **9 names from about 206M** across all five
types in both games (6 Black Ops 4 specialist-outfit images in its first 5M; nothing past ~5M in
any pool). A model that rebuilds half of a random sample of known names and none of the unnamed ones
says the unnamed remainder is *not* a random sample of the name distribution: almost every unnamed
name holds a token, or a junction between tokens, that no known name holds. That is why every
recombination shape decays to zero however it is cut, and it says where to look instead -- at
sources of tokens the corpus has never contained.

**Open slots filled from a dictionary** (`contrib/open_slot_words.py`). A *frame* is an exact known
prefix and an exact known suffix around one token. A frame whose slot holds at least 5 distinct
fillers, 60% or more of them English words, is a word slot -- an open class whose unseen members
are words too. Each such frame (10,226 in Black Ops 4, 11,592 in Cold War) is offered the top 30,000
English words from `wordfreq` (`pip install --user wordfreq`), on its own, never mixed with another
frame's pieces:

| game | candidates | new | of which |
|---|---|---|---|
| Black Ops 4 | 306.7M | **41** | image 10, material 12, xmodel 11, alias 7, anim 1 |
| Cold War | 347.7M | **135** | alias 106, material 17, image 12 |

One per ~2.6M in Cold War, four minutes a game -- and the words are exactly ones the corpus could
never have produced: `amateurs`, `terminated`, `reclaimed`, `suspensions`, `eisenhower`,
`michigan`, `disgusted` (#2250/#2251). The hits skew to rarer words, so the widenings were
measured the same day, each disjoint from what ran before:

| widening | Cold War | Black Ops 4 | rate |
|---|---|---|---|
| top 30k words, frames with >= 5 fillers (above) | 135 / 348M | 41 / 307M | 1 per 3.7M |
| words ranked 30k-150k, same frames (`--word-from 30000 --words 150000`) | 53 / 1.39B | 44 / 1.23B | 1 per 27M |
| top 30k, frames with 3-4 fillers (`--min 3 --max-fill 5`) | 21 / 829M | 22 / 693M | 1 per 35M |
| top 30k, frames with exactly 2 fillers whose prefix holds >= 5 word fillers across all its tails (`--head-class`) | 9 / 692M | 8 / 653M | 1 per 79M |
| German, Spanish, Russian, Vietnamese, French, Italian words not in English's top 150k (`--lang`) | **0** / 747M | -- | dead |

**Ranking by meaning instead of frequency** (`contrib/open_slot_neighbours.py`). A slot's fillers
are a semantic class, so each frame is offered the 3,000 GloVe words (6B, 100d) nearest the
centroid of its own fillers, from the whole 400k vocabulary: **18 Cold War / 105M, 26 Black Ops 4 /
94M** -- 1 per 4.5M, five times the deep-frequency rate, reaching words no frequency cut would get
to. The union of each filler's own 200 nearest words instead of the centroid (`--mode knn`) adds
almost nothing beyond it: 1 name from 54M across both games.

Two non-dictionary vocabularies through the same frames (`--vocab-file`), each excluding English's
top 30k so nothing is offered twice:

| vocabulary | words | Cold War | Black Ops 4 |
|---|---|---|---|
| tokens of the newer titles' `_v2` tables that no table or find of ours holds (seen >= 2 times) | 17,558 | 14 / 204M | 12 / 180M |
| tokens of our own tables and finds, offered to every word slot rather than only the contexts they were seen in | 18,658 | 8 / 217M | 19 / 191M |

**`submit` could not open a pull request for a large batch on Windows -- fixed in source,
2026-10-01.** It passed the PR body to `gh` as a `-f body=...` argument; a batch of 20 runs writes a
body past Windows' 32,767-character command-line limit and `gh` fails to start ("The filename or
extension is too long", os error 206). Worse, the batch folder had already been written into
`submissions/` and its branch pushed, so the next `submit` dropped those names as "already
claimed" and they were never sent. `src/bin/submit.rs` now sends the request as JSON on stdin
(`--input -`), as blobs, trees and commits already did. **`bin/windows/submit.exe` has not been
rebuilt** (no Rust toolchain on the machine that found it); until it is, a failed batch can be
rescued by opening the PR for its already-pushed branch with `gh api repos/<repo>/pulls --input -`
and appending its runs (the `### run_...` headings of its `about_*.md`) to `submissions/.submitted`.

`--ledger` on `open_slot_words.py` records the frames each word range has covered, so a re-run
after the corpus grows offers words only to frames that are new since.

Two more cuts of the embedding ranking, both weak: ranks 3,000-15,000 on frames with >= 5 fillers
(`--skip 3000 --per 15000`) returned **0 / 112M on Black Ops 4 and 2 / 112M on Cold War**; and
every English word in every *single- or two-filler* frame swapped for its 40 nearest neighbours
(`--mode knn --knn 40 --min 1 --max-fill 3`) returned **1 / 74M on Cold War but 12 / 59M on Black
Ops 4**. A word with no siblings is rarely sitting in an open class; where the game has filled a
slot several times, it is. Black Ops 4 kept paying further out: 150 neighbours per word instead of 40
(`--knn 150`) returned **14 more / 220M**.

*Not built, for size:* letting a word slot's exact prefix take **any** tail seen after it with another
filler (a new word arriving with a sibling's continuation rather than one exact known suffix). Counted
2026-10-01: 8,392 qualifying heads in Cold War and 6,473 in Black Ops 4, **32B and 26B** candidates
with the top 30k words as exact per-head frames -- far past a Python generator -- and as one engine
plan the heads and their 878k distinct tails cross-mix into **75 trillion**. It needs either a
per-head mode in `confirm_plan` (one literal beginning, its own ending file, many plans in one
process) or a much tighter tail filter before it is worth running.

**Sound files, which every split on `_` alone had missed** (`contrib/sound_word_slots.py`). A sound
file is a path -- `amb/environment/wind/gusts/sand/dunes/sand_dune_gusts_01.rn75.pc.all.snd` -- so
splitting on `_` glues its directories and extension chain into single tokens and leaves almost no
frames. Split on `_`, `/` and `.`, every directory component and basename word is a slot. Frames
with >= 4 word fillers, each offered the top 30k frequency words plus its 3,000 GloVe centroid
neighbours:

| game | frames | candidates | new `sound_asset` |
|---|---|---|---|
| Cold War | 4,160 | 127M | **107**, then **36** more from `derive_closure` |
| Black Ops 4 (backslashes, `--no-fold`) | 3,235 | 99.5M | 2 |

143 Cold War sound files in one pass, against 3 for the best `sound_asset` method of the day
before -- the largest batch into that pool in weeks. The aliases the same lines belong to had
already come out of the word sweep over `sound_alias` that morning: re-deriving aliases from the
new files' basenames matched 107, all already found. The two pools agree.

That also exposed a hole in `contrib/alias_to_file.py`: it placed an alias into a folder as the
bare basename, but these files are `<alias>_00.rn75.pc.en.snd` -- the alias plus a take number --
and run straight after the aliases landed it had found none of them. It now takes `--takes`, which
offers each folder the take suffixes its own files use (commonest 8): 2.9M candidates, and it
reproduces **all 141** of the day's Cold War sound files (0 new, since they were already found).
Run it with `--takes` after any batch of aliases.

It was also reading only `fnv1a_xsounds.csv`, while Black Ops 4's voice files are published in the
per-language tables (`fnv1a_english_xsounds.csv`, ...), so it never saw an `en/vox/...` folder. It now
reads every non-`_v2` `*xsounds*` table, and `--takes=N` sets how many takes a folder offers. The
convention is strong in Black Ops 4 -- 35,469 of its 68,028 known sound files are a known alias plus a
take -- and the fixed generator does rebuild those known files, yet `--takes=30 --backslash` against
the unnamed ids: **16.96M candidates, 0.** Every Black Ops 4 alias anyone has named already has its
files named; the open alias->file seam was Cold War's.

**And the snowball multiplied all of it.** `ab_snowball.py` straight after the first word sweeps
(the fresh families' cores against every known tail): **587 names over three rounds**, then an
empty fourth -- the fresh-family effect of 2026-09-29 again, but seeded by tokens that came from a
dictionary rather than from the corpus. Run the snowball after every word-sweep batch.

**Hot word frames** (`contrib/hot_word_frames.py`). The cores lesson of 2026-09-30 in word-slot
form: a frame that has just yielded a dictionary word is the likeliest frame to hold more, and a few
thousand hot frames can afford no frequency or similarity cut at all. Every name the word methods
confirmed today, each alphabetic token of it taken as the slot (splitting on `_`, `/` and `.`), and
each frame offered the union of wordfreq's whole English list and the GloVe vocabulary -- 383,157
words:

| game | hot names | frames | candidates | new |
|---|---|---|---|---|
| Cold War | 445 | 2,717 | 1.04B | **90** (aliases 38, sound files 36, materials 11, images 4, model 1) |
| Black Ops 4 | 206 | 968 | 371M | 5 |

One per 11.6M in Cold War, three times the deep-frequency rate on the same game, because the frames
are chosen by having just paid. It feeds itself: `--ledger` records every frame offered (`--seed`
records the frames of a run made before the ledger existed), so each re-run offers the whole
vocabulary only to the frames the previous round's finds created. Round 2 (477 new Cold War frames,
183M; 28 Black Ops 4, 11M): **2 names** -- it closes after one round. `--sibling-tails 30000`
(each hot prefix x every tail at least two words lead into under it, top 200 per prefix x the top
30k words): 298M candidates, 166 matches but only **5 new** -- the snowball reaches the same names
from the cores side.

**Grids whose rows are each too thin to qualify** (`contrib/open_slot_rows.py`). In a grid -- forty
speakers, fifty skins -- most rows hold one or two known words, so no single row's frame passes the
threshold while the column is plainly open. The evidence is pooled by wildcarding every *other*
short-code token (2-5 chars, a letter in it); a pooled slot with >= 8 fillers across >= 3 rows is
open, and each of its rows with fewer than 3 fillers of its own (so no earlier sweep reached it) is
offered the top 30k words, still as its own exact frame. 26,776 thin rows: **40 Cold War (37 aliases)
/ 803M, 6 Black Ops 4 / 803M.** The 37 new aliases then gave **35 sound files** through
`alias_to_file.py --takes`. The same rows offered the 3,000 GloVe words nearest the pooled fillers
instead (`--vectors`): **0 / 80M in each game.**

**Compounds nobody has seen, built from halves everybody has** (`contrib/compound_slots.py`). A
quarter of the fillers in open word slots are two English words glued with no separator -- 1,714 of
6,865 in Cold War, 1,433 of 6,408 in Black Ops 4 (`licenseplate`, `wirefence`, `gunboat`,
`bonusroom`, `quickscope`) -- and a new compound is in no dictionary. Each open frame that glues
words (>= 4 fillers, at least one compound) offers its own left halves x its own right halves, and
each half joined to the top 5,000 English words on the other side:

| game | frames | candidates | matched | new |
|---|---|---|---|---|
| Cold War | 10,583 | 693M | 114 | **12** |
| Black Ops 4 | 6,849 | 532M | 146 | **43** (materials 27, images 15) |

The matched-but-not-new counts are names the day's other word methods and the snowball had already
reached, so the method is independently re-deriving that ground as well as adding to it. Black Ops
4 responds to compounds far better than to the plain dictionary at the same depth. Deeper on Black
Ops 4, halves x words ranked 5k-30k (`--from 5000 --top 30000`): 2.66B, 85 matched, **12 new** --
the snowball running alongside reached most of the rest first. Ranking the new halves by meaning
instead (`--vectors`: each side offered the 2,000 GloVe words nearest the centroid of that side's
own halves) is weak: **5 / 213M on Black Ops 4, 0 / 276M on Cold War.**

**Two-word slots** (`contrib/open_slot_bigrams.py`). Many open slots span two tokens that vary as a
unit -- `..._paint_dead_mpx_...`. A frame here is an exact prefix and suffix around two adjacent
English words, qualifying with >= 5 distinct pairs (15,241 frames in Cold War, 15,012 in Black Ops 4),
and each is offered the 20,000 commonest adjacent English word pairs found in any published or
confirmed name of any title:

| game | candidates | new |
|---|---|---|
| Cold War | 305M | **37** (materials 21, images 11, models 4, alias 1) |
| Black Ops 4 | 300M | **45** (aliases 40, models 3, image 1, anim 1) |

The pairs themselves are not new words -- they are known pairs placed in two-token slots they have
never been seen in, which no one-token substitution (slotswap) can express.

Unlike every one-token widening, going *deeper* paid more, not less: pairs ranked 20k-120k
(`--from 20000 --pairs 120000`, 1.5B a game) returned **129 Cold War (aliases 73, materials 29,
models 12) and 103 Black Ops 4 (anims 86)**. Rare pairs are specific -- a character and an action, a
scene and a prop -- and specific is what a grid's missing cells are. Three-word slots (`--n 3`, the
top 20k word triples into 13,448 / 12,6xx frames) returned 7 Cold War and 9 Black Ops 4. Pairs ranked
past 120k (the remaining 145k, 2.2B a game): **57 Black Ops 4** (anims 20, materials 12, images 11),
**59 Cold War** (materials 30). Triples ranked past 20k (`--n 3 --from 20000`, the remaining 300k,
4B a game): **62 Black Ops 4** across all five types, **112 Cold War** (materials 46, images 40,
models 22). Four-word slots (`--n 4`, every corpus word 4-gram, 1.8B a game): **45 Black Ops 4, 60 Cold War**.
And pairs offered to *one-word* slots (`--into-single`: insertion and substitution at once, which
no same-length sweep expresses), top 20k pairs into frames with >= 5 word fillers: **30 Black Ops 4
/ 179M (anims 22), 42 Cold War / 198M (images 21, anims 11)**.
Crossing each two-word frame's own first words with its own second words (`--inner`, 0.8-0.9M a
game) returned **0 in both** -- that recombination is slotswap's ground; the value is in pairs
brought from elsewhere.
Pairs that are *not* both English words (`--mixed`: any letter-bearing tokens -- codes, names,
abbreviations -- into the frames such pairs fill, top 30k): **3 Black Ops 4 / 243M, 0 Cold War /
370M.** The pairs that pay are English.

**Two-word slots inside sound paths** (`contrib/sound_pair_slots.py`). The pair sweep splits on `_`
only, so it never saw sound files; this splits on `_`, `/` and `.` and takes pairs of adjacent English
words joined by the same separator (inside a basename with `_`, across folders with `/`), frames with
>= 4 distinct pairs, offered the commonest 30k pairs of that separator from every sound table and find:
**70 Cold War / 119M and 61 Black Ops 4 / 102M** -- the first batch of Black Ops 4 sound files of the
day worth the name (single-word slots had returned 2). Their basenames then gave **14 Black Ops 4
aliases** through `aliases_from_files.py`. Unlike the visual pools, rarer pairs do not pay here:
pairs ranked past 30k (`--from 30000`), **1 Cold War / 278M, 3 Black Ops 4 / 239M.**

**English web bigrams -- the phrases voice lines are made of** (2026-10-05). `open_slot_bigrams.py
--pair-file` with the top 100k two-word pairs of Norvig's `count_2w.txt` (web text,
https://norvig.com/ngrams/) that the corpus does not already use, offered to the same two-word
frames: **365 Cold War (357 aliases) / 1.53B, 7 Black Ops 4 / 1.51B.** Cold War's voice lines are
ordinary English phrases the game's own names never contained; Black Ops 4's frames are mostly not
voice. Then `alias_to_file.py --takes` turned the 357 aliases into **357 sound files** -- one file
per alias, `<alias>_00`. So: **714 names from one external phrase list.**

**Phrase grids: detect a phrase on two speakers, then fill the cast** (`contrib/phrase_grid.py`).
All 357 of those aliases were one family, `vox_<spk>_mtx_execute_<phrase>`, and each phrase exists
for ~35 of the 37 operators. A phrase only has to be *detected* once, so the vocabulary can be huge.
For every Cold War voice category whose phrases are shared across >= 10 speakers (58 of them),
`--probe` offers every phrase of a 3.07M vocabulary -- wordfreq's whole list, GloVe's vocabulary,
every web bigram (2-letter words allowed: `line_up`, `move_up`), 1.29M trigrams chained from
frequent bigrams, and every word pair and triple in the corpus -- to the two speakers holding the
most phrases: **18 hits from 356M**. `--fill` then crosses every phrase now known for any speaker
of a category with all its speakers: **66 aliases**, and `alias_to_file.py --takes` gave **284
sound files**. The web bigrams ranked past 100k, run the same day: **178 more** in Cold War.

The loop is: any batch of new voice aliases -> `phrase_grid.py --fill` -> `alias_to_file.py
--takes` -> submit.

Pushed further the same day, every probe on one speaker (`hdsn`, who holds every quip):

| probe vocabulary | candidates | new quips | then `--fill` | then sound files |
|---|---|---|---|---|
| 12.3M phrases chained from web bigrams (tri- and 4-grams, each also with function words dropped) | 24.5M | 11 | 165 | 176 |
| 26.7M deeper chains (`contrib/quip_phrases.py`) | 26.7M | 6 | 102 | 108 |
| every word and ordered pair of the 3,000 GloVe words nearest the quips' own words (`contrib/glove_phrase_pairs.py`) | 9.3M | 13 | (in the next row's fill) | |
| the same with 8,000 words | 64M | 5 | | |

The topic pairs run at one quip per ~715k candidates, far denser than chained web text: an unseen
quip is two words from the grid's own subject, not a common English bigram.
Two more shapes of the same topic idea (`glove_phrase_pairs.py`), each followed by `--fill` and
`alias_to_file.py --takes`:

| probe | candidates | new quips | fill | files | total |
|---|---|---|---|---|---|
| a topic word x one of the 30k commonest English words, both orders (`--open 30000`) | 183M | 12 | 374 | 386 | **772** (#2346) |
| the same with 150k common words | 920M | 1 | | | |
| every ordered triple of the 300 nearest topic words + 100 function words + the quips' own words (`--triples 300`) | 108M | 9 | 306 | 316 | **632** (#2347) |

Each quip found on one speaker is worth ~60 names once the cast and their files follow, which is
why probes this sparse still pay.
The widest of these then came up dry, which is where the seam stands: triples from the 500 nearest
topic words (284M) gave 1 quip, and topic pairs on *every* operator rather than one (348M, looking
for operator-specific quips like `baseball_bat`, `took_down`) gave 0.

**Cross fill: the grid inside a category** (`phrase_grid.py --cross`). Most categories are not
phrases but a second grid -- `ss_<killstreak>_<event>`, `ping_item_<gear>`, `se_kill_<event>`. Each
category's phrases split at the first word into rows and remainders, and every row x every
remainder x every speaker: **442 aliases from 650k candidates**, which `alias_to_file.py --takes`
turned into **460 sound files** (#2330). A second round, splits after two or three words, and Black
Ops 4's categories all returned 0: the open grid was streak x event, once.

**Never run two `submit`s at once.** On 2026-10-05 a background chain's `submit` and a manual one
overlapped by seconds and both opened PRs for the same two batches (#2318/#2319, #2320/#2321; the
copies were closed). `submit` takes no lock, and `ab_snowball.py` submits after every round, so
keep `submit` out of background chains and run it by hand when nothing else is submitting.

**Black Ops 4 zombies voice files: the alias reordered, in every map's folder**
(`contrib/bo4_zm_plr_files.py`, 2026-10-05). Black Ops 4's zombies lines break the
basename-equals-alias convention every other alias->file method assumes: the alias puts the event
first, the file puts the map code and speaker first, and the alias's index *is* the file's take --

    vox_box_smg_plr_17_3        ->  en\vox\scripted\zmb\orange\vox_oran_plr_17_box_smg_3.sn100.pc.snd
    vox_boss_success_ncom_1     ->  en\vox\scripted\zmb\<map>\vox_<code>_ncom_boss_success_1.sn100.pc.snd

(map-specific lines add a separate take, `..._ready_0_0`, and some carry `_s`). The only unknown is
the map, and the zombies voice folders are nine (`bod`, `common`/`cmn`, `fiv`, `man`, `orange`/`oran`,
`red`, `tow`, `white`/`whi`, `zod`). Every known `vox_<event>_plr_<n>_<idx>` alias in every map with
each form: **370 sound files from 763k**; the same for non-player lines `vox_<event>_<npc>_<idx>`
(`--npc`): **248 more**; known files read back as aliases (`--aliases`): **40 aliases**. Afterwards
3 player aliases in the tables are without a file, so the seam is closed; an event x player x
index grid (`--grid --grid-files`, 851k) and every other voice folder (`--all-folders`, 17.9M) both
returned 0 -- lines exist only for the players who say them, and only the zombies folders reorder.

**Cold War's zombies voice lines use the same reordering** (`contrib/cw_zm_line_files.py`,
2026-10-05). The 950 known files under `vox/scripted/zmb/` (`zm_silver`, `zm_audiologs`,
`zm_onslaught`, ...) are `vox_<mapcode>_<speaker>_<line>_<take>`, and no known alias contained a
map code. Every file read back under eleven candidate orderings (4,759 candidates) returned **412
aliases**, all of one form -- `vox_<line>_<speaker>_<take>`, Black Ops 4's convention exactly
(`vox_dark_aether_audiolog_05_alic_6`, `vox_mq_def_count_final_psys_2`). The other direction --
every known alias of that shape placed into the six known folders (16,746), and the 414 aliases led
by a map code (`vox_zber_..._jagr_0`) placed into 84 guessed `zm_<map>` folders (68,724) -- returned
0: the remaining maps' folder names or codes are not the guessed ones.

**Numbered sound templates** (`contrib/sound_number_templates.py`, 2026-10-05). The numeric
methods only ever read the visual pools, and a sound path often carries its number twice -- Cold
War's execution sounds are `mpl/executions/exec_<NNN>/<NNN>_<part>.ln75.pc.all.snd`, one folder per
numbered execution, with 46 of the folders named. Every 2-3 digit number in a sound name becomes a
placeholder holding the same value wherever it appears, names group by template, and each template
seen with >= 3 numbers is filled with every number of its width: **772 Cold War sound files from
1.06M candidates**, all executions (#2337), then 0 on a second round. Cold War aliases, Black Ops 4
files and aliases: 0 -- their numbered families were already complete.
The same idea for *words* (`contrib/sound_word_templates.py`): a token repeated between a sound
path's folder and its basename (`wpn/smg/cqb/plr/wpn_smg_cqb_loop`) made a placeholder and filled
with every value its family (first two path components) uses there: **7 Cold War / 2.1M, 35 Black
Ops 4 / 1.7M**; two repeated words crossed (`--two 30`): **0 / 1.55M and 0 / 1.17M**; templates whose repeated word
already takes >= 3 values offered the top 30k English words, written into both places at once
(`--dictionary 30000`): **0 Cold War / 112M, 12 Black Ops 4 / 110M**.

**Images named for a material's part, not the whole material** (`contrib/material_prefix_images.py`,
2026-10-05). Cold War's vehicles have 11,674 materials and 5,336 images: materials stack paint, wear
and skin variants on a part (`..._exterior_c_carpaint_b_mpx_bp_bomber`), while the part's images
carry their own endings (`i_mtl_veh_t9_mil_ru_air_attack_frogfoot_canopy_maps1_r`, `..._canopy_o`).
Every material at every prefix of >= 4 tokens, as `i_mtl_<prefix>_<ending>` and `i_<prefix>_<ending>`
for the 60 commonest image endings measured per game: **92 Cold War / 23M, 13 Black Ops 4 / 18M**;
the next 140 endings added 1 each, and endings measured inside each part's own family instead
(`--per-family 40`) 3 each. The reverse (`contrib/image_base_materials.py`: each image minus
its channel ending, as `mc/mtl_<base>` with the 200 commonest material endings): **11 / 18M, 9 / 14M.**

**Alphanumeric designations** (`contrib/open_slot_alnum.py`). Slots holding codes that mix letters
and digits -- `mp5`, `ak47`, `sh385` -- sit between the word sweeps (letters only) and the short-code
brute force (<= 3 characters). Frames with >= 4 such fillers, offered every such token of 2-8
characters in any name of any title (21,141): **133 Black Ops 4 anims from 42M** -- one per 316k --
and 1 Cold War model from 99M. Nearly all were cinematic shots, `ch_zm_<map>_<scene>_sh<NNN>_<who>`,
which led to a dedicated generator:

**Cinematic shot grids** (`contrib/cinematic_shots.py`). Every scene prefix carrying `_sh<digits>_`
gets every shot sh000-sh995 in steps of 5, a/b/c variants of its known shots and its siblings'
shots, x every character or object seen in that scene or any sibling scene of the same map. Run to
a fixpoint: **117 Black Ops 4 anims from about 130k candidates** (47, 0, 70 after the snowball fed it
new characters, 0) -- one per ~1,100 -- and 3 Cold War.

Two generalisations of it, both nearly dry -- the shot grid was the open one:
`contrib/numeric_slots.py` (every exact frame whose fillers are `<letters><digits>[<letter>]`,
enumerated over the counter's whole range) **16 Black Ops 4 anims / 3.4M, 0 Cold War / 4.3M**;
`contrib/designation_grids.py` (any lettered counter x every tail its siblings continue with --
the shot grid's two axes for every prefix) **0 / 0.5M and 1 / 1.3M**, and with bare counters
(`--bare`, `_01_` style) **0 / 1.8M and 0 / 3.9M**.

**Three neighbours, same reasoning, weaker:**

- `contrib/token_inflect.py` -- every word token re-inflected (-s, -es, -ed, -ing, -er, -ies, doubled
  consonants, and each stripped again): 29M candidates, **4 names** (1 Cold War, 3 Black Ops 4).

- `contrib/token_abbrev.py` -- each alphabetic token replaced by its truncations, consonant
  skeleton and doubled-letter collapse, and short tokens by the corpus words they prefix: 27M
  candidates, **11 names** (9 Cold War aliases, 2 Black Ops 4). The aliases are one new family,
  `vox_zber_eg_pwr_pufs_<l><n>_<speaker>_0`, reached by `puffs` -> `pufs`: the game ships both
  spellings.
- `contrib/open_slot_codes.py` -- the same frames for *short-code* slots (1-4 chars, middle slots
  only, since `affix_sweep` owns final ones), every 1-3 char code: 326M candidates, **2 names**.
  Short-code classes are already complete; word classes are not.

**Spent by:** the dictionary, not the corpus. Every confirmed name adds frames (and fillers that
promote thin frames past the threshold), so it refills a little after any pass, but the large
step only comes from a new vocabulary: a deeper word list, proper nouns (places, people, units),
other languages' words where the game uses them.

## Candidates worth building, with the measurement that decides each

**Read this before inventing a method from scratch.** These are ideas that have been thought
through but not built, each with the cheap check that says whether it is worth the effort. Measuring
first killed three plausible-sounding ideas in an hour on 2026-08-20 — the seams below marked as
dead are *measured* dead, not guessed.

### The ranking metric

A method's worth is what it returns **per candidate**, not what it returns in a pass. Measured on
Black Ops 4 models:

| method | names per candidate |
|---|---|
| `token_edits` | 1 per 94,000 |
| `affix_sweep`, run blind | 1 per 532,000,000 |

**5,600× apart.** Estimate this before committing CPU, not after.

And note that **pool size does not predict yield**: Black Ops 4 `sound_asset` has 70,878 unnamed ids
— more than anything else — and a dedicated pass returned 169, while the general search returned
5,869 the same day. Unnamed-id count tells you what is *left*, not what is *reachable*.

### Measured seams

| seam | measured | verdict |
|---|---|---|
| material ↔ image cores | **15,770 shared** — 11.7% of material's, 12.8% of image's | **strong**, ~60× the model/image pair |
| sound alias names as sound file stems | 706 of 101,673 (0.7%) | dead |
| model cores vs anim cores | **0** shared of 154,525 / 30,337 | dead |
| anim minus last token → model core | 16 of 30,337 (0.1%) | dead |
| model cores vs material cores | 3,300 of 154,525 / 266,575 (~2%) | too weak to pass |
| loader string pool as candidates | **0** of the 159,170 ids a Cold War pass hunts | dead |
| Black Ops 4 SAB paths, recombined from Black Ops 4 names only | **2 new** of 240,000; tail swap **0 new** of 63,165 | dead |
| Cold War sound paths, recombined -- with a corpus **8x denser** | **0 new** of 400,000; tail swap **0 new** of 36,679 | dead |
| Black Ops 4 SAB paths, seeded with **BO2/BO3 SAB directories** | BO3 shares **9.18%** of stems, BO2 1.35% | ~~live~~ **dead** -- the overlap is real and the yield is not; see below |
| Names published for the **newer titles** (`_v2` tables) hashed against our games | **0** of 1,175,524 names, against 336,505 unnamed ids in the two games | dead |
| loader string pool, all pools | 23,301 of 1,480,510 ids (1.6%), 18,691 unnamed — but `scriptbundle` is 17,304 of them | free names, wrong pools |
| material→image with a **different reduction each side** (`no head` / `no ends`) | **75,964 shared — 59.98% of image**, 5× the row above; 181,466 cores only in material | **relation real, ground dead** — see below |
| material→xmodel, same treatment (`no ends` / `no tail`) | **15,270 shared — 15.57% of xmodel**, 5× the "too weak to pass" row above | **relation real, ground dead** — see below |

### Timings measured on 2026-08-22 between 11:19 and 18:55 are not trustworthy — 2026-08-22

A background loop was left running for seven and a half hours without anybody realising, competing
for all sixteen cores with every pass launched in that window. It was believed killed at 11:20:
the `confirm_plan` **child** was killed and the shell was not, so the loop simply started its next
stage. `pkill -f` had matched nothing under Git Bash on Windows and exited quietly, and the absence
of an error was read as success.

**Name counts from that window are unaffected** -- each run writes its own folder and its own
`new` count, and nothing about a hash depends on how busy the machine was. So `692` for heads k=3,
`61` for `cross_era` and the rest all stand.

**Wall-clock figures from that window do not.** Anything quoting how long a pass took, and every
`names/hr` the report derives from `ran for` for a run stamped in it, was measured on a machine
sharing itself with a hidden loop. Do not compare them against a figure measured on an idle one,
and re-measure before quoting any of them as a method's cost.

Figures from **before 11:19 are clean** -- the k=1 to k=5 tails sizings, the overnight run, and the
1-per-18 for `final_byte` were all taken on an idle machine.

Two habits worth keeping:

- **Kill the parent, then check the parent is gone.** Verifying that the current pass died says
  nothing about the loop that will start the next one.
- **`python scripts/running.py`** answers "is anything grinding right now?" -- worth running before
  timing anything, and before assuming the machine is idle.

### A long unattended runner gets silently blocked at twelve hours — 2026-08-22

Worth knowing before writing one. `readiness::require` refuses to search if `start` last passed
more than twelve hours ago, which is right: the tables move and other people submit.

Inside a multi-stage script it does not read as a refusal. A long stage ran, the next stage
was blocked, printed its message into its own log, exited, and **the runner carried on to the
following stage as though it had searched.** The blocked pass reported nothing, found nothing, and
looked exactly like an exhausted method. It was noticed only by reading the log by hand.

If you write a runner that will outlive twelve hours, **re-run `start` between stages**, and check
that each stage actually reported a result rather than assuming it did.

### Nobody had ever replaced the *front* of a name — 2026-08-22

`tails.py` replaces a known name's last *k* characters and works. It exists in that direction for
a historical reason and not a principled one: the end is where the hash keeps a resemblance, which
is what let `final_byte` solve one character, so attention went there and stayed.

The front had never been tried. It is the same cross product with the lists swapped -- stems are
known names with their heads cut off, the k-character strings become the *beginnings* -- and it
costs the same 46 billion candidates.

**692 new names on Cold War in a single pass, none dropped as already claimed.** The best single
pass of the day, from ground nothing had ever asked about.

Two things worth taking from it beyond the names:

- **Check the mirror of anything that works.** The asymmetry here was an accident of how the
  hash's invertibility drew attention, and it left half the space unexamined for the life of the
  project. `--head` is nine lines.
- **`bare` flips meaning between the two.** Replacing tails there is no `begin:` line, so
  `bare: yes` supplies the only opening column and the pass tests nothing without it. Replacing
  heads the k-character strings *are* the beginnings, so `bare` would instead add the headless
  stem alone -- a truncation, which is a different method. Getting this wrong does not fail; it
  reports billions of candidates and scans none.

### And it was blind to a third of the corpus, for one character — 2026-08-24

`--head` was added as "the same cross product with the lists swapped", and that is true of the
stems and the beginnings. It is not true of the **alphabet**. `alphabet_of` counts `name[-4:]`,
the characters names *end* in, because the function was written for tails; the head flag reused it
unchanged.

Names do not begin the way they end. Measured over 958,424 published and confirmed names:

| | |
|---|---|
| characters names end in, top 37 | `_e0lnar1tocsdim2gphw34byku6f5v7x89zjq` — alnum and `_` |
| characters names begin with | the same, plus `/` `*` `[` `$` |
| first 3 characters inside the tail alphabet | **65.3%** |
| first 4 characters inside the tail alphabet | **64.1%** |
| first 5 characters inside the tail alphabet | **62.2%** |

and the whole of that shortfall is one character:

    blocked in the first four positions:   /  340,786 names    *  3,410    [  354    $  87

`/` is the directory separator. METHODS already records that material names are paths under
twelve directories and that `mc/` heads 496,666 published names — so **every `mc/ wc/ clt/ splm/
vd/ mcs/ ei/ cltp/ vdd/ el/ mcp/ ec/ mcdp/` name has a slash inside its first four characters, and
no head run has ever been able to spell one.** The 692-name pass was blind to a third of the
ground it was pointed at, and the reach measurement did not show it because `reach.py` measures
the committed beginning and ending lists rather than a method's own alphabet.

**Fixed in `scripts/tails.py`**: `--head` now widens the alphabet with the characters names begin
with and never end with, above a floor of 50,000 blocked fronts — which carries `/` and correctly
declines `*`, a mesh-hash marker that is unreachable anyway. The cost is `((n+1)/n) ** k`, 11% at
k=4.

**And the ground itself is cheaper than the fix suggests.** Re-running the widened alphabet redoes
the 1,874,161 beginnings of 2,085,136 that the narrow one already swept — 90% of the work for
ground already covered. `contrib/heads_slash.py` writes the **complement** instead: only the
210,975 four-character beginnings that carry a slash. 199 billion candidates, against 899 billion
if `*`, `[` and `$` are carried too.

Two things worth taking from this beyond the names:

- **A method has an alphabet as well as a list, and nothing measures it.** `reach.py --missing`
  reports what `data/prefixes.txt` and `data/suffixes.txt` cannot express and is run constantly.
  It says nothing about a generator that builds its own vocabulary, and this one had been wrong
  since the day it was written.
- **Check the mirror's *inputs*, not only its shape.** The lesson recorded above was to try the
  mirror of anything that works. The mirror was tried; what came with it unexamined was the
  measurement feeding it.

### Structural overlap has now failed to predict yield three times — 2026-08-22

Every time this project has measured that two name sets *share structure* and concluded a method
was worth building, the method has returned approximately nothing. Three for three:

| what was measured | what it predicted | what it returned |
|---|---|---|
| material↔image cores, 75,964 shared, 59.98% of image | a strong seam | **0 matched** in 190 M candidates |
| BO3 shares 9.18% of Black Ops 4's SAB stems | `sabpaths` rated **live** | **0** in 187 B candidates |
| 2,394,179 newer-title cores absent from our corpus | fresh vocabulary | 61 in 34.5 T -- 1 per 565 billion |

**Overlap says two things are made of similar pieces. It says nothing about whether the pieces
recombine into names that exist.** Treat any "N% shared" figure as a reason to *test*, never as a
result, and put the test result in this file rather than the overlap.

The SAB one is worth spelling out because it was carefully controlled. `scripts/sab_plan.py` asks
`sabpaths`' whole vocabulary product -- 13,311 directories x 93,092 basenames x 150 tails,
187,111,289,412 candidates, unfolded -- against a pool with **70,878 unnamed of 79,263**, the
largest unnamed ground in either game. It returned 0. And the positive control passed: **387 of
391** known Black Ops 4 SAB names *are* reproducible from those three lists, so the plan covered
the right space and the space is empty. The vocabulary of Black Ops 2 and 3 does not carry into
Black Ops 4's sound tree, whatever the stem overlap says.

Older-title corpora hashed **verbatim** were tested at the same time -- `bo2_sab`, `bo3_sab`,
`bo2_ipak`, `cod_constants`, `cod_semantics`, `cod_techsets`, `fnv1a_strings`, 944,345 names: **0
matched folded on either game, 2 matched unfolded on Black Ops 4.**

### The closure multiplies a method's yield, and nothing measures that — 2026-08-22

`cross_era` returned **61** names for 34.5 trillion candidates, which by every column in
`methods_report.py` is among the worst methods ever run here.

Then `derive_closure` ran over what it had confirmed and found **416 more** -- `final_byte` +235,
`tails` +96, image siblings +75, channels +10 -- and round 2 correctly returned 0. Those 61 seeds
became 477 names.

**A method's worth is its own yield plus whatever the closure extracts from its seeds, and the
report can only see the first.** The closure's names are credited to the derivations, which is
correct provenance and misleading economics: it makes seeding methods look worthless and
derivations look better than they are.

Two consequences worth acting on:

- **Run the closure after everything**, including after a method you are about to write off. It is
  free and it has now multiplied one pass by 6.8x.
- **Do not retire a method on its direct yield alone** if it adds names in families nothing else
  reaches. `cross_era` is not worth its machine time twice, but its 61 names were not the point.

### Recombining *across* names is dead; varying *within* one is not — 2026-08-22

Three independent measurements now say the same thing, and together they are the most useful
generalisation this file has.

**Dead — pieces taken from different names and recombined:**

| what | measured |
|---|---|
| cross-type core seams (material→image, material→xmodel), the two strongest ever found here | **0 matched ids** in 190 M candidates, both games |
| head of one name + tail of another, cut at underscores (`scripts/splice.py`) | **7 names in 96 B candidates** — 1 per 13.7 billion |

**Live — one name varied in place:**

| what | measured |
|---|---|
| `final_byte` — last character solved | **1 per 18** |
| `image siblings` / `image channels` — a name respelled for its sibling asset | 1 per 394 / 1 per 5,160 |
| `tails` — last three characters replaced | 1,151 names, **free** (21 s) |
| `gaps`, `variants` — a number moved in place | 1 per 377 |

The reading is that asset names are **not freely recombinable**. A head constrains its tail
semantically, so a head and a tail that never appeared together mostly never will. What is
productive is taking one real name and moving one thing about it.

`splice.py` was listed under *Candidates worth building* from the beginning and never built,
because as a generator it is 4.2e13 candidates and a Python generator emits a million a second.
It is a plan now, it ran in under two minutes a game, and it is dead. **That is the point of the
plan engine** — an idea that sat unbuilt for want of a year and a half of generator time got
settled in four minutes, and the answer is written down instead of waiting for somebody else to
have the same idea.

Before building anything that joins pieces of different names, weigh it against these numbers.

### How far the final-byte solve extends: two characters, and no further — 2026-08-22

The obvious follow-up to the solve below is to extend it to longer tails. It does not extend, and
this is the measurement so nobody spends an evening finding that out.

Shared leading hex digits between the hashes of two names differing in their last *k* characters,
against **0.03** for two entirely unrelated names:

| k | 1 | 2 | 3 | 4 |
|---|---|---|---|---|
| mean shared leading digits | **4.26** | 1.41 | 0.11 | 0.07 |

One character is strongly visible in the hash. Two is faint. **From three the pair is
indistinguishable from any two unrelated names** — XOR does not commute with the multiply, so each
further step scatters what the last one left. There is no proximity to filter on and no solve to
generalise.

**What works instead is not proximity but peeling**, which the engine already does. "Is this id a
known name with its last *k* characters replaced" is a plan: stems are known names cut short by
*k*, endings are every *k*-character string over the measured alphabet. `scripts/tails.py` writes
it. Sizes against 922k names and the 37 characters names end in:

| k | endings | candidates | time |
|---|---|---|---|
| 2 | 1,369 | 1.3 B | seconds |
| 3 | 50,653 | 31.7 B | **21 seconds** |
| 4 | 1.87 M | 1.14 T | ~15 minutes |

Each k subsumes the ones below it. **k=3 returned 266 on Cold War and 885 on Black Ops 4, in
twenty-one seconds each.**

### The hash runs backwards for the final byte, and that is a method — 2026-08-22

Contributed as an observation: `p9_example_model_name_1` and `..._2` hash to nearly the same
number. They do, and the reason is exact rather than approximate.

FNV-1a is `h = (h ^ byte) * prime`. For two names differing only in their **last** character the
XOR touches only the low eight bits, so

    h(A) - h(B) = ((h_prefix ^ a) - (h_prefix ^ b)) * prime

and that first term is an integer in [-255, 255]. The difference between the two hashes is always
an exact small multiple of the prime — `_2` is -3x, `_3` is -2x, `_a` is -80x. A few times 1.1e12
apart in a space of 1.8e19, which is what "nearly the same hash" is.

**It holds for the final byte and no other.** One position further in, the difference is carried
through another XOR, XOR does not commute with the multiply, and the multiplier is already 7.1e18
— random. Do not try to generalise it; that is measured, not assumed.

**The relation inverts, so this is a solve rather than a search.** The prime is odd, so

    u = (h(prefix) ^ byte) * prime   =>   byte = (u * prime_inverse) ^ h(prefix)

Take every known name's prefix, ask whether `u * prime_inverse` differs from one of them in the
low eight bits only, and the answer *is* the character. 256 lookups per unnamed id, no strings
built, no candidates hashed.

**Measured, Black Ops 4: 2,523 candidates, 138 confirmed — one name per 18.** The next best method
in this file is image siblings at one per 394. Sweeping the same ground the obvious way took
35,068,642 candidates for 75 names, so solving backwards is ~14,000x cheaper *and* covers more,
because it tests all 256 bytes rather than the 39 a measured alphabet would carry.

Two traps, both paid for:

- **Hash the solved name back.** The solve gives the byte the hash wants; the game hashes a
  *normalised* name. A solved byte that is uppercase or a backslash cannot survive normalisation
  and will never hash to that id. Without the check it reported 11,003 solutions where 63 were
  real, and `confirm_list` matched 0.6% of what it was handed.
- **Its 138 landed as 3.** A brute sweep of the same ground an hour earlier had already claimed
  them. That is `found` against `landed` in `methods_report.py`, and it is the normal case.

### Cross-type core seams are stronger than recorded and yield nothing — 2026-08-22

Both rows above are worth reading carefully, because they are the clearest example in this file of
a measurement that looks like a find and is not.

`cross_type.py --measure` applies **one** reduction to both sides of a pair. `scripts/seams.py`
applies every reduction to each side independently, and under the right pair the material→image
seam is **75,964 shared cores against the recorded 15,770** — 59.98% of every image name in the
corpus. The relation is real and it was being measured five times too weakly. The spelling is real
too: **85.9% of those shared cores reconstruct an actual published image name** when spelled
`begin + core + end` with image's own commonest decorations.

Then it was run. `confirm_plan` put the 181,466 cores material has and image has not through the
engine with those decorations — 113,416,250 candidates against Cold War and the same again against
Black Ops 4 — and matched **0 unnamed ids on either game**. Not zero new: zero matched. The
material→xmodel seam, 78,208,750 candidates each way, likewise **0 and 0**.

So the seam is genuine, thoroughly mined, and **its non-overlapping half does not extend**. A core
that one type has and another has not is overwhelmingly a core the second type never had.

**The lesson is about the headroom column, and it cost four passes to learn.** `seams.py` reports
`only in A` as what a derivation would produce, and both these seams had six figures of it. It
predicted nothing. Relation strength says the relation exists; it does not say the missing side is
missing *because nobody has named it yet*. Only running it says that — and running it is now
minutes, so **run it rather than reasoning about it**.

### The two cheapest checks with the biggest upside

**1. Do confirmed image cores appear as material cores?** — **built and measured, 2026-08-20.**
See method 16 below. The seam is real and the yield is poor: 7 names in Cold War, 10 in Black Ops
4. Do not re-derive it.

**2. Do confirmed model names hash into the `xcollision` and `xskeleton` pools?** `odd_for_pool` in
`src/lib.rs` notes a model id "with the usual `xcollision` and `xskeleton` beside it". If those
siblings share the model's name, every one of ~6,444 confirmed model names is a free name in two
more pools. Ten minutes to test: hash confirmed model names and look for the ids in those pools.
**Ask before grinding it** — neither is among the five wanted types, and check cod-name-db has a
destination table, since a name with nowhere to land is worth less than one that can be published.

### Others, briefly

- ~~**`numbered_grids.py`**~~ — families numbered on *two* axes. **Built and measured dead,
  2026-08-24 — see the dead ends.** The measurement this line asked for came back healthy (a third
  of the corpus carries two numeric runs) and the pass came back **0 in both games**, on a
  generator whose positive control rebuilds 100% of the observed cells. Do not rebuild it.
- **`suffix_chains.py`** — endings compose (`_01` + `_c`). The list is capped at 4,800 *observed*
  endings, so rare compositions are structurally absent. Measure: how many pairwise compositions of
  the top 50 endings are already published but missing from `data/suffixes.txt`.
- **`compound_splice.py`** — head of one name, tail of another, joined at a shared token. Distinct
  from `slotswap` (substitutes in place) and `templates` (crosses within one family). Cap by
  requiring a *rare* shared token or the pair count is quadratic.
- **`token_order.py`** — permute two adjacent middle tokens. Nothing here reorders anything.
  Measure: do any permutations of confirmed names already appear in the tables? If none do, the
  convention is stable and this finds nothing.
- **`cross_game.py`** — try a name confirmed in one title verbatim in the other. `confirm_cw` seeds
  *pieces* across games already, but nothing tries whole names. Nearly free: no generation, just
  hashing a list that exists.
- **`cross_era.py`** — the `_v2` tables (Vanguard, MWII, MWIII, BO6, BO7) re-hashed under *this*
  era's rules. Those games reuse older assets. Note they use a different mask — see `docs/HASHES.md`
  — so re-hash their *names*, never reuse their ids.
- **`map_sets.py`** — map prefixes (`p9_` heads 77,248 published names, `p8_` 66,172, `p7_` 42,516)
  crossed with faction codes and confirmed bodies. Overlaps `slotswap`; measure what it reaches that
  slotswap does not.
- **Black Ops 4 `sound_asset`** — 70,878 unnamed and ~102 ever found, the largest untouched ground.
  The general sound pass gets ~169 a time because its beginnings cannot express deep SAB paths.
  Characterise the 8,385 known SAB names first; a generator built from their path structure is the
  most valuable unbuilt thing here *if* the structure is learnable.
- **`methods_report.py --efficiency`** — not a generator. Every run folder records candidates,
  matches and time. Nothing computes names-per-candidate across them, so the ranking above will go
  stale. Once computed, the rotation could order itself by measured yield.

### Infrastructure, not generators

- **`images_from_materials` has no checkpointed run folder.** `confirm_cw` and `confirm_list` write
  theirs every sixty seconds so a killed pass stays submittable; this one does not. It is also the
  most expensive slot in the rotation, now measured at 2h15m for 43 names — see the note under
  method 3. The checkpointing is the part still missing.
- **`--shard i/n` on `confirm_cw`.** Needed before anyone runs several machines. The search is
  deterministic, so N machines running one method produce identical output.
- **Feed the in-flight survey into `suggest`.** `start` surveys every open pull request and then
  never passes it to `suggest`, so every fresh clone is told to do the same thing. Also break the
  fresh-clone game tie randomly rather than by list order.
- **`snapshot` will silently destroy an injected pool.** Run with no argument it rewrites
  `snapshots/<game>.ids` purely from the loader — which drops Cold War's 50,890 injected
  `sound_alias` ids and Black Ops 4's 79,263 SAB `sound_asset` ids, because Cordycep has no pool
  for either. It takes an output path; a guard that refuses to overwrite a file holding pools the
  loader does not have would be better than remembering to pass one.
- **`name_field_probe` and `loader_strings` need the game open**, and answer two questions that
  have now cost more than one session each: where a pool keeps its name, and what the string pool
  can reach. Both are Cold War-measured only — the Black Ops 4 halves are unrun.

---

## Adding a method

**This is the highest-value thing anybody does here**, and it no longer requires writing Rust.
`confirm_list` takes candidate names on standard input and does the careful half. A method is a
program that prints names.

A new method earns its place by answering the **reaches** question: what slice of the unnamed ids
does it get at that nothing above does? A method that covers ground the general search already
covers is not a new method, it is a slower one.

When you add one:

1. **Name the generator when you confirm:** `confirm_list - --label "..." --script <path>`. It is
   copied into the run and `submit` puts it in the pull request under `scripts/contributed/`.
   Anything in `contrib/`, and any new file in `scripts/`, is carried too. Give it the docstring
   `scripts/README.md` asks for.
2. **Read the library first.** `start` prints every script and what it is for, so that inventing
   something that already exists under another name takes a deliberate effort rather than an
   ordinary lapse of memory.
3. Add a section here in the same shape, with the numbers your run measured.
4. Say honestly what it is spent by.
5. **If it did not work, put it in the dead ends below.** A measured negative is worth as much as
   a find, and costs the next person nothing.

---

## Order of resort

Seeded methods first, always. That is where the yield is and they compound.

Exhaustive or random character combination is a legitimate **last** resort once seeded methods are
genuinely exhausted — never a starting point. The arithmetic says why: the median confirmed name
has seven or eight underscore-separated segments, and the space of sequences that long passes 2^63
long before the name does. Past four segments the hash stops being a filter and becomes a
checksum: there are more candidate strings than there are hashes, every one an equally valid
preimage, and no amount of speed changes that. Only a prior can. Fragment recombination *is* that
prior.

If you do get there, constrain it with what has been measured — known directories, known prefixes,
known segment shapes, known endings. This is also the only regime where collisions matter: a
41.7 T candidate pass expects 0.617 coincidental matches, and a seeded pass of forty million
expects 0.0000. Every binary prints the figure.

---

## 16. Materials from image cores

`scripts/materials_from_images.py` | **7** (CW), **10** (BO4) | 4.57M candidates per game

The material ↔ image seam run backwards. `images_from_materials` (method 3) goes material → image;
this strips an image name to its core — directory, a leading `i_`, one channel suffix — and offers
that core as a material under all twelve directories, in both the `mtl_` prefixed and bare
spellings. Both forms are needed: of 329,846 material names measured, **67.4% carry `mtl_` and
32.6% do not**, so emitting only the prefixed form gives up a third of the space.

**What it reaches that nothing else does:** material names whose core was only ever confirmed as an
image. There are far more published image names than confirmed materials, so the reverse direction
has the larger corpus — which is why it looked promising.

**Spent by:** its own corpus. It reopens only when new image names are confirmed.

**The estimate was wrong, and how it was wrong is the useful part.** Beforehand this was measured
at 158 hits for Black Ops 4 (1 per 14,456 candidates, against `token_edits` at 1 per 94,000) and it
returned 10. The estimate excluded only names in the *published tables*; the real run also excludes
the **9,583 ids already claimed** by merged submissions and open pull requests, which is what
`wanted_for_search` does and a hand-rolled estimate does not. Estimate against the claimed set, not
the tables, or expect to be out by an order of magnitude.

---

## The compounding loop, measured over one night

`AGENTS.md` §7 says every confirmed name is a new beginning, a new ending and a new numbered
family, so re-measuring the lists reopens a method that reported itself exhausted. That is true.
This is how much, and how fast it decays -- measured 2026-08-20/21 on one machine, both games,
the same binary each time.

| pass | Black Ops 4 | Cold War | lists |
|---|---|---|---|
| 1 | **55** | **56** | as committed |
| 2 | **294** | **303** | after folding in ~800 newly merged names |
| 3 | **51** | -- | after folding in ~2,000 more |

**The second pass is worth five times the first, and the third is worth less than the first.**

The reason is not the *number* of names folded in but where they came from. Fold 1 took in 1,218
names from another contributor's evening -- vocabulary this machine had never seen. Fold 2 took in
~2,000 names, mostly found by *these same passes*, so the beginnings and endings it added were
largely ones the search had just finished using. A corpus that grows by rediscovering its own
neighbourhood does not widen what the lists can express.

**So the loop is fed by other people's names, not by your own.** Re-measure after merging a batch
from somebody else, and expect little from re-measuring after your own pass. `python
scripts/reach.py` will not tell you this -- reach stayed at 94.3% / 92.8% on models across all
three folds, because the ceiling was never what moved.

---

## The ending list is the bottleneck, and it is measurable

Written 2026-08-23, after `mcdp/` and `uncarried_endings` returned 9,520 names between them in one
evening from the same idea.

Both wins came from the same place, and it is not a clever recombination -- it is the observation
that **the committed lists are a cap, and everything outside them is unreachable no matter what
method is pointed at it.** `data/prefixes.txt` carries 700 beginnings and `data/suffixes.txt`
carries 4,629 endings. Measured against the published tables:

    endings carried                4,629      (2,798 of one segment, 1,086 of two, 745 of three)
    uncarried, 1 segment         178,016  heading   620,830 published names
    uncarried, 2 segments        471,768  heading 1,610,162 published names
    uncarried, 3 segments        786,512  heading 4,155,796 published names

**Better than a quarter of the published corpus ends in something no generator here can put on a
name**, and the commonest are not exotic -- `_thermalmap` heads 16,000 alone, and at two segments
the ranking is animation transitions: `_to_walk`, `_to_sprint`, `_to_jog`, `_offset_additive`,
`_empty_ads`.

### Why this was not found by re-measuring

CLAUDE.md §8 is right that re-running `derive_lists.py` does not reopen ground: it changes what a
search is *called* without changing what it can *reach*. That is exactly why this was invisible.
The ending list is **capped**, `derive_lists.py` reports what its ceiling cut, and re-measuring
cannot lift a cap -- so the cut vocabulary was reported honestly every single run and never once
acted on. The fix was not to measure again. It was to take what the cap threw away.

### What it costs, and the shape that works

The cores come from the published names with the same number of segments removed, so a core that
wears `_c` in the tables can be asked about wearing `_thermalmap`. Two things keep it runnable:

  - **Drop dotted endings.** Sound names carry a dotted tail, and at three segments they crowd out
    every ending the other four types use. §5 already says a sound ending tried against a model id
    can only ever be a coincidence. `--sounds` keeps them if a sound pass wants them.
  - **Restrict the cores to one game past two segments.** The ending vocabulary grows faster than
    the core list shrinks, and the published core list makes the plan unrunnable.

### The core list mattered more than the ending list

Added later the same day, and it is the single most productive change made to this method.

Every ending sweep above built its cores the same way: a published name with **exactly as many
trailing segments removed as the ending has**. A two-segment ending could therefore only ever
attach to a name cut two segments from its end. That is an arbitrary restriction, and it was
costing most of the yield.

Cutting every known name at **every** segment boundary instead gives 1,334,022 cores, so a core
that sits five segments deep in one name gets asked about wearing a two-segment ending from
another. Measured 2026-08-23, both games together:

    all-boundary cores x  20,000 endings        602 names
    all-boundary cores x 100,000 endings      2,553 names
    all-boundary cores x 300,000 endings      1,470 names

against 2,065 for the original depth-matched sweep at 200,000 endings. Repeated at the other
depths, both games: 1 segment **316**, 3 segments **1,523**, 4 segments **381**.

It transfers to sound, which breaks at path separators as well as underscores. 839,743 sound
cores against 100,000 uncarried sound endings returned **1,746 names in one pass** -- more than
the entire depth-matched sound sweep (1,385) had returned across six. **The ending list was
never the binding constraint -- the core list was**, and the two multiply: widening the endings
five-fold over the wide core list quadrupled the yield, where widening them over the narrow one
had gone flat.

> **Read those figures as a shape, not as a quota.** They were all taken on 2026-08-23 against
> the corpus as it stood that morning. Reproduced independently that afternoon, after roughly
> 187,000 further names had been claimed by merged and open submissions, the same method on
> Cold War returned **163** at 100,000 endings and **37** on the sound half -- the method is
> intact, the ground under it is not the same ground. This is the ordinary decay every method
> here shows, and it is the reason a yield is only ever a fact about a corpus at a moment. If
> you run this and see tens rather than thousands, nothing is broken; check
> `methods_report.py --efficiency` for where it has decayed to before concluding otherwise.
> The generator that implements this is
> `scripts/contributed/uncarried_endings_allboundary_20260823-134935.py`; it rebuilds the
> all-boundary core list from whatever the corpus holds now, which is the only thing that
> genuinely reopens this ground.

The lesson generalises past this method. When a cross product underperforms, work out which of
the three lists is actually restricting it before widening whichever one is easiest to widen.

### And the cores this project made itself

The corpus grew by roughly 24,000 confirmed names on 2026-08-23, and that changes the core list
in a way re-measuring never can. Cut at every boundary, **156,178 non-sound cores and 319,592
sound cores exist only in `findings/` and the merged submissions** -- they occur nowhere in the
published tables, so no ending sweep had ever crossed them with the ending vocabulary.

    confirmed-only cores x 505,416 endings            746 names
    confirmed-only SOUND cores x 184,215 endings      583 names

This is the distinction §8 is drawing and it is worth stating in the positive. Re-running
`derive_lists.py` reopens nothing because it renames the same reach. New **material** reopens
ground properly, and confirming names is the only thing that produces it -- which is why the
right move after any productive pass is to rebuild the core list and run again, and the wrong
move is to re-measure and run the same thing.

### Where it is spent, and where it is not

Yield by depth, both games, 2026-08-23: 1 segment **1,191**, 2 segments **2,065**, 3 segments
**1,800**, 4 segments **1,054**, 5 segments **564**. It decays with depth rather than with
re-running, because each depth is a different vocabulary rather than a deeper sweep of one.

The obvious next question is the mirror. This is all endings. The beginning list is capped at 700
the same way, and `mcdp/` is one beginning out of that cap worth 2,846 names on its own.
`scripts/contributed/redecorations_20260823-023757.py` ranks uncarried beginnings by how
much of their vocabulary is borrowed, and the general sweep over all 1,075 of them returned
only 7 -- but that sweep used **bare stems and no endings**.

**That question has since been answered, and the answer is no.** Crossing the uncarried beginnings
with the uncarried endings was measured the same day at 229 billion candidates for **0 names** --
see *doubly uncarried* in the dead ends below. A name is reachable through one cap or the other,
not through both at once: the middles that survive stripping a segment off each end are too short
to identify anything. This paragraph originally closed by calling the cross unmeasured, which was
true when it was written and was overtaken within the day; it is kept because the reasoning that
motivated it is still the right reasoning, and only its conclusion moved.

### Which segment depth pays, measured across all five — 2026-08-29

Method 25 is usually run at the depth somebody happened to pick. Swept properly against Cold War
sound on one afternoon, on freshly generated lists each time, the depths are not close:

| segments | endings offered | names | closure on top |
|---|---|---|---|
| 1 | 28,627 | 46 | -- |
| **2** | **157,824** | **634** | **47** |
| 3 | 200,000 | 49 | 2 |
| 4 | 300,000 | 66 | 0 |
| 5 | 300,000 | 17 | 21 |

**Depth 2 is worth roughly ten times any other**, and it is not because it was offered more
endings -- depths 3, 4 and 5 were each offered more and returned a fraction. Two segments is
simply where a sound name's ending actually lives: long enough to identify a real tail
(`.ln100.pc.snd`), short enough that the core in front of it is still shared across many names.

Depth 2 is also the one that *exhausts*: the corpus holds only 157,846 uncarried two-segment sound
endings, so `--top 200000` already takes all of them and a larger `--top` changes nothing. The
deeper lists are nowhere near exhausted and still return little, which is the same statement from
the other side.

**And it does reach Black Ops 4, weakly.** The same depth-2 plan against Black Ops 4's own
158,563 unnamed ids returns **12**, against Cold War's 219 on the non-sound side and 634 on
sound. Worth stating precisely because the retracted row above claimed the opposite from a
sweep that read stale lists: the seam is not absent in Black Ops 4, it is about twenty times
thinner, which is consistent with every other Black Ops 4 result here rather than a new
mystery.

**Run depth 2 first, and take the whole list.** 418 of the 634 came back already claimed by
another contributor working the same seam the same day, which is what a productive seam looks
like rather than a problem -- `submit` dropped them and sent the 216 that were new.

## Aim at the unnamed distribution, not the published one

Written 2026-08-23. It is the most useful hour of that day and it cost no machine time at all.

Every list here is measured off what is **known** -- the published tables and the confirmed
names. The target is what is **unknown**. Nobody had checked whether those are the same shape.
They are not, and there is a direct sample of the unknown population sitting in `findings/`:
**every name this project has confirmed was unnamed until somebody found it.**

Profiled against the published tables -- 1,560,882 published against 68,596 recovered:

                            published   recovered
        median segments             8           6
        contains `/`            44.6%       20.0%
        contains `*`            16.0%        0.0%
        contains a digit        93.2%       54.4%
        average length           38.1        32.2

**The unnamed names are shorter, flatter and far less numeric than the corpus every generator
here is tuned on.** And the beginnings say where they are:

        vox_           35.05% of everything recovered   against  0.02% of published
        mcdp/           4.64%                                     0.04%
        fly_            4.29%                                     0.00%
        evt_            2.21%                                     0.00%
        callingcards_   1.81%                                     0.00%
        amb_            1.75%                                     0.00%

`vox_` is **a third of every name this project has ever recovered** and two hundredths of a
percent of the published tables. The endings agree: `_mtxitem`, then `_use`, `_threat`, `_dyn`,
`_dstr`, `_npc`, `_plr`, `_vox`.

Those are sound aliases and UI strings, and Cold War's largest unnamed pool is `sound_alias` at
43,603. The published tables barely contain that family, which is *why* it is unnamed -- and why
a method measured against the published corpus will never point at it.

`scripts/unnamed_profile.py` prints all of this, and `--grid` ranks the families that are
grid-shaped. Run it before choosing where to spend a night. The figures above move as the corpus
grows, so read them from the tool rather than from here.

## What a ceiling does and does not predict

`--reach`-style measurements ask what fraction of *known* names a method could express at all.
They cost a minute and they are worth taking, but they mislead in two ways that cost a night
each.

**1. Measure it held out, or it is circular.** A ceiling built by cutting up the same corpus you
then measure against is asking whether a method can reproduce its own input. Cold War item bodies
crossed with Cold War variant tokens -- `mtl_c_t9_usa_canteen_02_woods` and its siblings, where
the item stays and the skin word swaps -- measured **61.96%** that way, the highest figure ever
recorded here. Split the corpus in half and build the vocabulary from one half only: **22.62%**.

**2. Even an honest ceiling predicts nothing on its own**, because it measures reach over *named*
names. That 22.62% method returned **0** over 311,550 candidates. The reason is the part worth
keeping:

> **Recombining a corpus with itself is bounded by that corpus.** Every name Cold War's own
> bodies and Cold War's own variants can compose lies inside the region Cold War's vocabulary
> already covers -- and that region is, by definition, the named one. The unnamed assets are
> unnamed *because* they are outside it.

So the question to ask of a method is not "how high is its ceiling" but **"where is its
vocabulary from"**. A ceiling is useful for ruling out a method whose vocabulary comes from
somewhere else, and useless for ranking one that recombines the corpus you are already searching
-- that one is bounded whatever it measures.

## The beginning list is capped too, and nobody has measured it until now

Method 22 is *uncarried endings*: `data/suffixes.txt` carries 4,629 endings while the corpus holds
178,016, and mining the difference returned 6,674 names -- the largest method here. The same
question had never been asked of the **beginning** list.

    beginnings carried by data/prefixes.txt            700
    distinct beginnings in the corpus            1,134,831
    uncarried                                    1,134,131   heading 7,432,611 names

The commonest are not exotic and no generator here can emit them:

    twc/ 229,447   jup_ 58,965   m/ 54,088   jup_vm_ 41,154   i_mtl_p8_ 30,826
    tm/ 26,375     i_mtl_p9_ 25,110   i_c_t9_ 21,315   i_c_t8_ 20,529   tw/ 19,579

`i_c_t9_` heads 21,315 names on its own -- the image prefix for Cold War character assets -- and
the list cannot say it. `scripts/uncarried_beginnings.py` measures and writes the list.

**Read the dead ends before building on this.** *Uncarried beginnings crossed with the whole
corpus* returned 7 names and *doubly uncarried* returned 0, because both crossed these beginnings
with **Cold War's own** stems -- a corpus recombined with itself, bounded by the region it already
covers. The cap matters when the stems come from **outside** it.

### And on the sound side the ceiling is the binding constraint, not the measurement — 2026-08-29

`reach.py` reports `xsounds` at **100% reached and 10.7% named**: the ending list can express
these names, and the beginning list almost never can. The obvious reading is that the sound
beginnings have gone stale and want re-measuring. They have not, and re-measuring does not help.

`derive_lists.py` measures 839 sound beginnings against a ceiling of 700, and says what it did
with the rest:

    sound.prefixes.txt: 839 measured, 14 carried, 153 past the ceiling of 700 dropped
    the ceiling cut 153 measured beginnings, the largest being vox/scripted/sims/ (454 names)

So the measurement already finds the vocabulary and the **cap throws it away** -- and a re-measure
throws away a different 153, which is the same displacement recorded above for the general lists
(55 names, then 294, then 51, on a corpus two and a half times larger). Re-measuring a list whose
ceiling is already binding reshuffles which beginnings survive; it does not raise reach.

**What does reach past it is a plan**, which has no cap: `begin: @<the full measured list>` puts
all 839 in front of the engine at once. That is the difference between the search everybody runs
and one aimed at the ground the cap is hiding, and it costs no re-measurement and no fingerprint
change to the shared lists. Note before building one that the `vox_` families this would reach
are heavily worked already -- *the `vox_` slot grid* and *vox speaker x line grid* are both in the
registry and the latter has decayed to 163,662 candidates a name.

### The all-boundary ending sweep's own `--top` cap has the same hole — 2026-09-03

`scripts/contributed/uncarried_endings_allboundary_20260829-172236.py --top` defaults to 100,000
and its docstring calls that "the measured sweet spot: 20,000 gave 602 names and 300,000 gave
1,470, against 2,553 here" (both games, 2026-08-23 corpus). That measurement is the same shape of
mistake this file already warns about above: a cap that looked optimal on the corpus it was
measured against silently throws away vocabulary once the corpus grows, and nobody re-checked it.

Run repeatedly against Black Ops 4 alone as the corpus grew through this session, `--top 300000`
kept paying — 46, then 31, then 6, then 4, then 1 name per cycle at 2 segments. That decay reads
exactly like a spent method. It was not: it was the same **300,000 endings**, re-offered to a
slowly growing core list, while the pool of endings the cap was dropping — **492,271 uncarried
2-segment endings existed, 792,271 uncarried at 3 segments, 957,772 at 4** — never got touched.

Passing `--top` high enough to carry the *entire* uncarried-ending list rather than a capped slice
(`--top 500000` at 2 segments, `--top 900000` at 3, `--top 1000000` at 4 — any value at or above
the actual count) reopened it immediately: **41 new names at 2 segments, then 621 at 3 segments**
against Black Ops 4's unnamed ids — the single largest result of this project's session on this
machine, and larger than every other method run that day combined. The 3-segment run landed
**545 of the 621 in `sound_alias`**, the pool `reach.py` had already flagged as ending-reachable
but beginning-starved (see above) — the wide ending sweep found the matching half of that gap.

**The lesson generalises past this one script: any generator with a `--top` / ranked-list cap is
worth re-running uncapped once the corpus it draws from has grown meaningfully past whatever
corpus the cap was tuned on**, and the tuning note in a script's docstring is a snapshot of a
past corpus size, not a permanent ceiling. Check what a cap is actually cutting
(`derive_lists.py`, or the generator's own reported "N uncarried endings" line against what
`--top` kept) before trusting a "sweet spot" measured on a smaller corpus.

### The endings list has the same hole, in the channel codes

`data/suffixes.txt` does not carry **1,162** of the codes Cold War's own names end in, including
`_cm`, `_sg`, `_r1`--`_r3` and the whole `_NNn` family. `_cm` alone appears 12,727 times in the
published material and image names. A method that swaps a trailing code cannot reach any of them
while the list is capped, whatever else it gets right.

## Why the yield per submission keeps falling — measured 2026-08-29

Names per pull request have gone `26 -> 20 -> 15 -> 100 -> 27 -> 9 -> 4` (median, by day) while
submissions per day rose from 166 to 355. Four explanations were tested against the run record in
`submissions/`. **Three are wrong**, and knowing which matters, because each implies a different
fix and two of them would waste a week.

### It is not the pool running out

    recovered by this project        326,275 names
    still unnamed in wanted pools    320,924   (176,664 BO4 + 144,260 CW)

Roughly half the job is left. Nothing is running out of targets.

### It is not contributors colliding

The opposite, and it has been fixed so thoroughly it now looks like a different project:

    date        kept   dropped as already claimed   kept share
    2026-08-19  1,179,635        16,924               98.5%
    2026-08-20     57,076        12,481               81.8%
    2026-08-22      4,547         6,030               16.5%
    2026-08-26      5,064            61               98.8%
    2026-08-29      1,145            27               97.7%

Claim-drops fell from 16,924 a day to 27. Since the fingerprint and the open-pull-request check
landed, 97.7% of everything found is genuinely new. Duplicate suppression is not the constraint.

### It is not a failure to invent

This was the expected answer and it is flatly contradicted. **New methods per day is rising:**

    date        methods run   first seen that day   names   from new methods
    2026-08-23      56              41             30,177        85.4%
    2026-08-25     106              92              5,504        87.8%
    2026-08-27      77              50              1,852        24.7%
    2026-08-28      93              68              1,887        94.0%

More invention, less yield. **Names per new method: 736 -> 166 -> 60 -> 132 -> 37 -> 28.**

### What it actually is: the reachable set is finite, and the corpus cannot grow it

Sorting every run by what kind of method it was makes it plain. Nearly all yield is *structural*
— methods that exploit a gap between what the lists can express and what the game holds
(uncarried endings, all-boundary cores, the final byte, image channels, the beginning ceiling):

    2026-08-29   structural 1,032   external 0   perturbation 59   other 23

and the yield of a structural run is collapsing on rising effort:

    names per structural run   199 -> 24 -> 19 -> 11 -> 7

**A structural gap is a seam, not a mine.** Sweeping it consumes it, and the corpus growing does
not open another — a new confirmed name is more of the vocabulary already held, so it deepens a
seam nobody can re-sweep rather than cutting a new one. That is why `derive_closure` returned 0 on
2026-08-29 against a corpus 900 names larger than the run before it, and why re-measuring the
lists never reopens anything.

### And the one channel that adds new information is now provably closed

*External* methods — reading the build, another title's archives, a mod tools tree — are the only
ones that inject information the corpus does not already contain. They returned 3,020 names on
2026-08-24 and **zero since**, because the source was read once and finished. That is now measured
rather than assumed, in both directions:

- the CASC index names 2,028 frames for Black Ops 4 and the magic hunt already found 2,101, so
  nothing was being missed; and
- the BLTE census finds **0 encrypted and 0 recursive chunks** in either build, so nothing was
  being skipped for want of a key.

### What follows from this

**The project is information-limited, not effort-limited.** More passes, more contributors and
more scripts do not change the answer, and the record shows exactly what happens when they are
applied anyway: 336 of the 401 generators contributed on 2026-08-27 were perturbations of a known
name — reversals, rotations, character swaps, rot13, atbash — and they returned **121 names, 0.36
per script**, against roughly **16** per script for structural work in the same window. Permuting
names you already hold cannot tell you a name you do not.

So the next step change comes from a **new source, not a new recombination**. In descending order
of what is actually on this disk:

1. **Cold War's fast files.** 100 GB, AES-256-CTR, and the cipher is already identified. The key
   is the single largest untapped source in the project and the only remaining barrier is
   cryptographic rather than structural.
2. **Black Ops II's fast files.** 297 of them, 3.84 GB, `TAff0100` v147 behind the `PHEEBs71`
   Salsa20 marker. This is the *only* unread container on the disk with a published key
   schedule. Everything else unread -- Black Ops, World at War, Call of Duty 4, Modern Warfare
   2 and 3, eleven installs surveyed -- is encrypted too, so "walk the builds nobody has
   walked" is not the cheap lead it looks like. See the survey under method 17.
3. **Anything that reads the game rather than the names** — the loader, a memory dump, a running
   process.

Ranking methods by past yield will not find these, because a ranking cannot rank a method nobody
has written, and everything it *can* rank is a seam somebody is already finishing.

## Black Ops 7 seams the short-channel scripts could not express -- 2026-10-09

Four generators, all in `scripts/contributed/`, measured on BLACKOP7 (images 8.5% named, the
largest gap in any game). Spent by: the corpora as they stand; each snowballs after the others.

| method | what it reaches | BO7 result |
|---|---|---|
| `long_channel_grid.py` | material / image core + any measured channel up to three segments. The seam scripts cut channels with `[a-z]{1,4}\d?`, so BO7's most common one (`_thermalmap`, 3,843 named on a material core) and every two-segment one (`_m0_v2`, `_dmg_v2`) were never offered. Writes two plans; `_rev` puts the 49 measured material directories on every core | **348 images + 394 materials**, then 11 + 18 after the corpus grew |
| `slot_swap.py --kind <k>` | fixed beginning P, one token slot after it swapped for every value siblings under P take, every sibling tail kept. Unlike shared-tails it transfers a tail attested once | **721** (316 img, 291 mat, 60 alias, 52 anim, 2 snd); `--max-slot 3000 --max-tails 30000` added 43 |
| `slot_swap.py --width 2`, `--also material` | a two-token slot (class + weapon); and image candidates built over the image + material-core corpus | **112** (80 mat, 17 img, 10 anim, 4 snd, 1 alias); `--also` **20** images |
| closure of all of the above | re-run in turn until a round adds nothing | **+38**, then **0** -- converged 2026-10-09 |
| `title_prefix_swap.py --kind <k>` | leading codename (`jup_`, `sat_`, `cer_`, `iw9_` ...) swapped, dropped or added -- the first token `slot_swap` cannot vary | **71** (57 mat, 10 img, 4 alias, 0 anim) |
| `sound_tail_swap.py` | every sound-file stem under the 40 most common encoding tails (`.tnn.75.48000.all` ...) | **35** sound files |
| `packed_material_codes.py` | `twc/*<k>n_<k>dn[_...]` numeric material codes, k < 2,500 | 2 tokens **25**; 3 tokens (1.7T candidates, 0.26 chance matches) ran past 30 min, ~240 recovered by `submit` |

## Dead ends

Do not spend a night rediscovering these. Each cost real time.

| Tried | Outcome |
|---|---|
| **BO7 packed image suffix as a non-FNV hash**, 2026-10-09 | 300 `A&B~N` names from `fnv1a_ximages_v2` (45% of that table is packed): N against xxh64 (seed 0 and the modern basis), xxh3, murmur3 x64 both halves, md5/sha1/sha256 first 8 bytes in both byte orders, and both FNV bases, over the whole text, the parts joined bare / by newline / by comma, and each part alone, upper and lower case, masked 64/63/32: **0 hits.** Likely a content hash; packed images are unreachable from names. |
| **BO7 terrain tile grid**, 2026-10-09 | `saw_sierra_<hex>_<x>_<y>_<z>_emissivitymap`: every integer x,y in [-400,400] under the 16 known hexes, z -8..8, 16 channels: **0.** Each hex names one tile. |
| **BO7 weapon sound files across sibling weapons**, 2026-10-09 | `weapon_sound_swap.py`: 66,280 `<title>/wpn/<class>/{W}/...` templates filled with every weapon of the class (436k): **0.** Same result as Cold War's weapon event grid. |
| **BO7 operator voice files: operator x line**, 2026-10-09 | `operator_vo_files.py`: 827 operators x 21,786 (ctx, code, phrase) lines of their root (9.8M): **0.** Phrases are written per operator. |
| **BO7 voice files in other languages**, 2026-10-09 | 2,000 named `.english` stems under 15 language tails: **0.** The capture holds English only. |
| **BO7 model names as image cores**, 2026-10-09 | 175k published xmodel names against BO7's named images: 73 have one as core (14 not also a material core). Not worth a pass. |
| **Public dialogue transcripts as vocabulary** (Call of Duty wiki), 2026-10-07 | 68 quote, intel and transcript pages (Cold War zombies intel, campaign transcripts, character quotes, the BO4 zombies maps' quotes) pulled as wikitext through the wiki API, split into sentences, and every run of 1-5 words kept as written and with function words dropped: 425,839 phrases, 64,142 word pairs, 2,771 uncommon words. Phrase probe of every shared voice category, then fill and files: **2 phrases -> 33 aliases + 35 files** (Cold War; 0 Black Ops 4); the pairs in every two-word slot (~1B a game): **5 / 0**; the uncommon words in every word slot: **4 / 0.** The game does not name its lines from their text: apart from the execution quips, voice names are event codes (`ss_uav_dstr`, `zm_ping_perk_juggernog`, `mq_def_count_final`), so a transcript is the wrong key. |
| **Shared visual grids: camo icons, camo names, vehicle paint jobs**, 2026-10-06 | Looking for another "detect once, fill the cast" grid like the execution quips. Black Ops 4 camo icons `<weapon>_t8_camo_<camo>_icon` (56 weapons x 107 camos, 2,710 holes): **0**; new camo names on the weapon with the most (`ar_accurate`), 540k candidates from 60k words with `dlc<N>_`, `_zm`, `_wz` forms: **0**; Cold War vehicle materials `<part>_mpx_<skin>`, every part x every skin within each of 88 vehicle families (86k): **0.** The visual pools' shared grids are complete; a camo or skin covers exactly the weapons and parts it was made for. |
| **Character skins: part grid and new skin names**, 2026-10-05 | `contrib/skin_part_grid.py`: every `c_t9_`/`c_t8_` skin key x every part ending (`_viewarms`, `_lowerbody_viewbody`, `_torso_sy`, ...) its faction uses: **12,027 Cold War + 620 Black Ops 4 candidates, 0.** Then each of 27 Cold War operators' skin slot (`c_t9_<faction>_pl_<op>_<skin>_viewarms`) probed with every word of wordfreq and GloVe (397k): **7.5M, 0.** Skins are complete as grids, and the unnamed ones are not single dictionary words. |
| **Topic pairs on every other shared voice category**, Cold War, 2026-10-05 | The probe that found the execution quips (`glove_phrase_pairs.py`: every pair of the 2,000 GloVe words nearest a category's own phrase words, on its top speaker) run on the other 57 categories shared by >= 10 speakers (`se_kill`, `eq`, `kill`, `ping_item`, `ss_*`, `zm_*`, ...): **226M candidates, 0.** Their phrases are game-system vocabulary (killstreaks, gear, events) that the grids already hold in full; only the quips were an open class. |
| **Weapon sound aliases for weapons only the models name**, both games, 2026-10-05 | `contrib/weapon_event_grid.py`: weapons from `wpn_<class>_<weapon>_*` aliases *and* `wpn_t<N>_<class>_<weapon>_*` models, each offered every event its class's aliases use: **4,833 Cold War + 16,772 Black Ops 4 candidates, 0.** Every weapon's sound set is already named. |
| **Sound aliases built from a file's path**, both games, 2026-10-05 | `contrib/aliases_from_paths.py`: Cold War's effect aliases are visibly built from the path (`fly/weapon/reload/sniper_quick/bullet_in/sniper_quick_bullet_in_00` -> `fly_sniper_quick_bullet_in`; `.../ww/electric/crystal_empty/crystal_empty_00` -> `zmb_ww_crystal_empty`), so every known file offered top folder + any ordered choice of up to two folder names + basename minus take, with `_plr`/`_npc`: **8 Cold War / 1.09M, 0 Black Ops 4 / 706k.** The convention is real but already mined -- the aliases of every known file are named, and the unnamed effect aliases sit with unnamed files. |
| **Cold War zombies voice folders for the maps nobody has a file for**, 2026-10-05 | Only `zm_silver`, `zm_audiologs` and `zm_onslaught` have known voice files. Three probes for the rest, all **0**: the 383 aliases led by a map code (`zamr`, `zber`, `zdtp`) placed into `vox/scripted/zmb/<zm_word or word>/` for every GloVe word, as the reordered basename (43M) and as the alias itself with and without a take (52M); and `z` + every 3 letters as the file's map code, in ten guessed folders (`zm_gold`, `zm_tungsten`, `zm_platinum`, ...), on 30 `zm_silver` lines (5.3M). Either those maps' lines are speaker-specific or their files are named another way. |
| **Phrase-grid fill and cross fill on Cold War's sound-effect alias families**, 2026-10-05 | `phrase_grid.py --family <fly|wpn|zmb|evt|amb|prj|veh|mus|mpl|uin> --fill --cross --speakers 5 --phrases 3`, the second token playing the speaker (`wpn_<weapon>_...`): 78k candidates across ten families, **0.** Only the operator voice lines are shared grids. |
| **Phrase grids in Black Ops 4**, 2026-10-05 | `phrase_grid.py --game BLKOPS04`: its 10 voice categories shared by >= 10 speakers (`ae`, `callout`, `threat`, `ult_*`, ...) probed with the 3.07M-phrase vocabulary on two speakers each (61M), filled, and cross-filled at splits 1 and 2: **0 everywhere.** Its voice lines are not shared grids the way Cold War's operator lines are. |
| **Black Ops 4 voice lines x every speaker of their group**, 2026-10-05 | `contrib/vox_line_grid.py`: every `en/vox/scripted/<group>/<spk>/vox_<spk>_<line>_<take>` line seen with >= 2 speakers of a group, offered to every speaker of that group with the line's takes (plus 00-03), as files and as bare aliases. **129,280 file + 31,507 alias candidates, 0.** A line exists for exactly the speakers who recorded it; the sound-pair finds of 2026-10-01 were new *lines* reaching many speakers at once, not holes in old lines. |
| **Compounds inside sound paths**, both games, 2026-10-01 | `compound_slots.py --sound`: the glued-compound method of the visual pools on sound-file paths split at `_`, `/` and `.` (1,300 frames per game). **92M Cold War + 97M Black Ops 4, 0 new.** Sound paths take words and word pairs (`sound_word_slots.py`, `sound_pair_slots.py`), not new compounds. |
| **Cold War weapon-blueprint attachment models, as a grid and as new names**, 2026-10-01 | `contrib/blueprint_grid.py`. `attach_t9_<part>_<class>_<weapon>_<blueprint>_<view|world>` is 11,437 of Cold War's 68,354 named models. Completing it per weapon (every part seen on a weapon x every blueprint seen on it x view/world x its suffixes; parts pooled across the class with `--across-classes`): **800,901 candidates, 0.** Probing every weapon's three most-blueprinted parts with 212,256 candidate blueprint names (wordfreq's top 200k, our corpus tokens, the newer titles' tokens; `--probe`): **70M, 0.** A blueprint carries exactly the parts it carries, and the blueprint list is complete; Cold War's 17k unnamed models are not here. |
| **Misspellings and UK/US respellings of every word token**, both games, 2026-10-01 | `contrib/token_typos.py`: each alphabetic token of 4+ letters in every known name replaced by every adjacent transposition, single deletion and single doubling, plus -our/-or, -ise/-ize, -re/-er, -ll-/-l-, grey/gray and similar. **26M Cold War + 19M Black Ops 4 candidates, 0.** The unseen tokens are real words (`open_slot_words.py`), inflections and abbreviations, not typos. |
| **Foreign-language words in English word slots**, Cold War, 2026-10-01 | `open_slot_words.py --lang de,es,ru,vi,fr,it --words 20000`, accents folded to ASCII, minus every word in English's top 150k: 64,276 words x 11,616 word-slot frames, **747M candidates, 0.** Cold War is set in Germany, Cuba, Vietnam and the USSR and still names its assets in English; the same frames returned 135 from English's top 30k. |
| **Cross-game token swaps learned from the two games' own named sets**, 2026-10-01 | `contrib/era_token_swap.py`. Every name present in one game is indexed by "its tokens with one slot blanked"; a name present in the other game under the same blank is a pair differing in exactly one token, and recurring pairs (`lt`->`bot`, `heavy`->`plr`, `katana`->`brawler`, ...) form a translation table, down-weighted where the same swap already links siblings *inside* the target. Hex-hash image tokens (`_ec5b0b30`) dominate the raw counts and are filtered out. Top 20,000 swaps applied to every name present in the source and not the target: **2.69M candidates BO4->CW, 3.22M CW->BO4, 0 new either way.** Together with the 3-name verbatim transfer this closes cross-game transfer at one-token distance: the shared content is already named in both. |
| **Sound alias names read off sound-file basenames**, both games, 2026-10-01 | `contrib/aliases_from_files.py` -- the reverse of `alias_to_file.py`. Every published or confirmed `sound_asset` basename, raw and with its trailing take number stripped (`vox_x_congrat_sml_03` -> `vox_x_congrat_sml`): 476,458 candidates. 1,127 Black Ops 4 aliases matched, **all already named; 0 new in either game.** Every alias whose file anyone knows is already named, so the unnamed aliases sit with unnamed files. |
| **Exhaustive 3-4 character speaker codes, Cold War**, 2026-10-01 | The Black Ops 4 version returned 176 names; Cold War never had one. `contrib/cw_speaker_codes.py`: `vox_` + every unseen code of 3-4 chars from [a-z0-9] (1,726,149) + the 1,054 lines at least three known Cold War speakers share, as a plan: 1.8B candidates, **0.** Cold War's voice cast is fully known at that length; its ~490-line speaker grids are already filled. |
| **Snapshot order as locality**, 2026-10-01 | Consecutive named records share a 3-token family 52-54% of the time in `image` against 5-9% shuffled, which looks like load-order information. It is not: both snapshots are **sorted by id**, and the locality is FNV's own -- names differing only in their final byte hash to ids a small multiple of 2^40 apart. That is exactly what `final_byte` already solves backwards. The snapshot carries no order beyond the hash. |
| **The lighting-bake map stamp as a hash of the map name**, 2026-10-01 | The 38 distinct 8-hex stamps in `volume<V>_state<S>_<kind>_<stamp>_<i>` against 841 `mp_`/`zm_`/`cp_`/`wz_` map tokens in seven spellings (`mp_x`, `maps/mp/mp_x.d3dbsp`, ...), under CRC32, FNV-1a 32 and the low, high and 63-bit-shifted halves of FNV-1a 64: **0 matches.** The stamp is a bake identifier, not derivable from the map, so the bake grid's ceiling stays the published maps. |
| Pooling `coordinated_identifiers.py`'s evidence across asset types instead of per-type, 2026-09-25 | `contrib/coordinated_identifiers_crosstype.py`. Hypothesis: a substitution rule like `usa<->rus` is game vocabulary, not naming-convention vocabulary, so it should be learnable from sibling evidence in *any* asset type, not just the type it is applied to. Pooled all six types' names into one evidence set: 7,246 supported rules, 926,631 candidates, but **`cross_kind_supported_pairs: 0`** — no rule's two required sibling frames ever came from different kinds, because the per-type naming convention makes the full masked-template shape (not just the token) type-specific. Confirmed anyway, all four game/fold configurations: **0 new everywhere.** The per-type original already covers this ground; pooling only adds candidates the per-type run already tried under a different fingerprint. |
| `sab_plan.py`, the full directory x basename x tail product (not sampled), Black Ops 4, 2026-09-04 | Method 20's generator (`sabpaths`) capped itself at 36.4M candidates to finish as a pipe and returned 5 names. This asks the *same vocabulary, same convention* completely, as a plan the engine runs instead of a piped generator: 13,315 directories x 93,743 basenames x 150 tails, **188.5B candidates, 0 matched.** Extends the existing extensive `sound_asset` dead-end record (numbered takes, directory x basename recombination, all-boundary cores x uncarried endings, cross-title respelling -- all recorded dead above) with the one shape none of them tried: the full product at once, unsampled. Consistent with the standing conclusion that this pool's unnamed 70,697 are not built from pieces the named ~8,600 are built from, under any recombination shape measured so far. |
| `cross_era.py` with widened `--heads`/`--tails` caps (5,000/20,000, up from the 1,200/6,000 defaults), Black Ops 4, 2026-09-03 | The `--top`-cap lesson above paid off huge for the ending sweep (621 names), so the same fix was tried on `cross_era.py`'s own rank caps -- same shape of parameter, same corpus that had grown 5x since the defaults were last measured. 120T candidates over 8 slices; **5 of 8 slices run (62%), 0 matched in every one.** Not a full run -- `confirm_plan` has no slice-resume flag, so finishing the last 3 would mean redoing the first 5 from scratch, which was not worth it once 5 straight zeros were in. Unlike the ending-sweep cap, widening this one did not reopen anything: the newer titles' vocabulary, respelled with our own decorations, still does not land on Black Ops 4's specific unnamed ids at this corpus size. Consistent with the standing "engines renamed rather than inherited" conclusion. Worth a full 8-slice run if the corpus grows substantially again, but do not expect the same shape of win twice from the same trick. |
|---|---|
| `tails.py --head --length 3`, re-run on the 2026-09-06 corpus against BLKOPSCW (1,004,856 known names, up from ~692k when it first returned 692) | The single best invented pass in the project's history, re-tried on the theory that a much larger corpus might reopen it the way it reopened the ending sweep above. 54,872 measured head-alphabet beginnings x 992,714 stems, **54.47B candidates, 0 new.** Matches its `spent` verdict in the registry (last paid 2026-08-29): unlike the ending list, which had a live `--top` cap quietly discarding vocabulary, this generator already offers every known 3-character head over the full measured alphabet, so a bigger corpus mostly just means more of the same short heads repeating. Re-check after the corpus grows by an order of magnitude, not a few thousand names. |
| `cw_mcdp_redecoration.py`, re-run on the 2026-09-06 corpus (2,827 confirmed, well past the 2026-08-29 corpus that still returned 3) | `mcdp/` is a re-decoration of the general material vocabulary, not a namespace of its own (see method 19 and the redecoration entries above) — every re-run offers it the material cores confirmed since the last one. The yield has now gone **2,846 -> 5 -> 5 -> 3 -> 0**: 621,924 material cores, 1,214,373 candidates against BLKOPSCW, **0 new.** Unlike the `--top`-cap fix above, there was no capped list here to widen — this generator already offers every known core — so the trend is a genuine decay, not a measurement artifact. Re-run again only once a meaningfully larger batch of material names has landed; running it every session is now pure overhead. |
| Sound **alias** names as sound **file** stems | 706 of 101,673 distinct file stems are exactly an alias name — **0.7%**. The two vocabularies are unrelated: aliases are bare underscore names (`amb_computer_loop_1`), files are deep paths with encoding tails. Do not build a generator on this seam. |
| Model cores against anim cores | **Zero** shared, out of 154,525 model and 30,337 anim cores. Taking an anim's name minus its last token as a model name hits 16 of 30,337 (**0.1%**). There is no model/anim seam to exploit. |
| Model cores against material cores | 3,300 shared of 154,525 and 266,575 — about 2%, against the 15,770 that material and image share. Weak enough not to be worth a pass. |
| Recombining **sound file** paths, in either game, at any corpus density | This is the general form of the Black Ops 4 result below, and it settles what that one could not. Cold War `sound_asset` is **40.3% named** -- 39,178 known of 97,217, against Black Ops 4's 5.3% -- so it has eight times the material to recombine from, 2,679 directories and 38,574 basenames. Directory x basename: **0 new of 400,000**. Tail swap across the four commonest endings: **0 new of 36,679**. Importing Black Ops 2 and 3 basenames under Cold War's own directories: **0 new of 600,000**. So corpus density was never the obstacle, and the earlier "the corpus is too small to rebuild from" was the wrong diagnosis even after it was corrected once. A sound file is a *recording*, and its name belongs to the directory it sits in; basenames and directories are not independently combinable the way a material's core and its directory are. Anything reaching these pools has to come from outside the naming -- the SAB files, a build, or the game's own strings. |
| Re-hashing the newer titles' names against these two games | Candidate 15 below proposed this as costing "almost nothing -- no generation at all, just hashing an existing list", which was true, and it returns nothing. Every name in all eight `_v2` tables -- Vanguard, MWII, MWIII, BO6, BO7: `xmaterials`, `ximages`, `xanims`, `xsounds`, `soundbanks`, `soundbanks_aliases`, `animpkgs`, `bones`, **1,175,524 names** -- hashed under *our* rules, folded and unfolded, against the **336,505** ids still unnamed in the wanted types across both games. **Zero.** Not a weak seam; an empty one. The newer engines renamed rather than inherited, so their published vocabulary describes nothing these two titles hold. Costs three minutes to reproduce and needs no game. |
| Recombining Black Ops 4 `sound_asset` (SAB) paths | The largest single opportunity in either game -- **70,876 unnamed of 79,263** -- and recombination does not reach it. Everything anybody knows is **4,212 names, 5.3% of the pool**, and they do not generalise to the rest. Measured 2026-08-20, all against ids nobody can already name: filling holes in numbered families **0 of 1,847**; extending a family past its highest number **0 of 59,052**; swapping the extension tail (`.ln100.pc.snd` -> `.ll100.pc.snd` and the other 15) **78 hits but 0 new** -- every one was a name already published; directory x basename cross product **2 new of 240,000**, or 1 per 120,000, worse than `token_edits` at 1 per 94,000. The structure *is* learnable (24 leading segments, 16 extension tails, depth 2-6) which is what makes this worth writing down: the shape being legible is not the same as the corpus being big enough to rebuild from. Anything that reaches this pool has to come from outside the known names -- the SAB files themselves, or a build. **Corrected 2026-08-21, and the correction is the useful part:** GoastcraftHD's `sabpaths` found that outside source *inside this repository*. `bo2_sab.csv` and `bo3_sab.csv` hold 400,815 Black Ops 2 and 3 audio paths that nothing here had ever used, because they are SDBM-hashed and so are not "our games" for exclusion -- but their *directory* structure transfers, BO3 sharing **9.18%** of its stems against the 0.7% / 0.1% / 0 of the seams recorded dead above. Two further things this measurement got wrong: it read only three sound tables and recovered **4,212** known names where a full sweep finds **8,446**, so "the corpus is too small to rebuild from" was argued from half a corpus; and it tested recombination of Black Ops 4 names against each other, which is the one shape the pool's own structure predicts will fail, since names average 3.7 per directory and a known directory is mostly *unknown* members. Recombining what is already known is dead here. Importing directories from an older title is not. |
| Harvesting the loader's **script string pool** for candidates | Plausible and completely dead for the grind. Every string the loader holds, hashed against the live game: 23,301 of 1,480,510 ids, **1.6%** — and **0 of the 159,170 ids a Cold War pass actually hunts**. The 4,038 hits that do land in targeted pools (2,467 image, 1,567 xmodel) are *all* already in the tables. The reason is structural, not a matter of trying harder: an asset type is reachable from the string pool only if the engine addresses it **by name**, and models, materials and images are addressed by hash. Measure with `loader_strings`. |
| Scanning `xsub` files for names | They hold none. 85 GB of nothing. |
| A NUL-terminated-only string scanner over xpak/ff/fd | Misses roughly 800,000 names. |
| Suspecting the captured id is a **name pointer** rather than a hash | It is a hash. `snapshot` stores `entry.id`, the loader's own pool-entry field, never a dereferenced header. Measured over every asset in all 202 live Cold War pools: bits 0-62 uniform, bit 63 always clear, 12.5% 8-byte aligned (random gives 1/8), and tens of thousands of published names hash straight into it. Separately, `header+0x00` *is* the id in 180 of 202 pools and something else in 22 — `xanim` keeps its id at **+0x70** — but nothing reads that field, so it changes nothing. Re-measure with `name_field_probe`. |
| Salsa20 for the encrypted fast files | Wrong cipher. It is AES-256-CTR, little-endian counter. |
| Training a name classifier on the `_v2` tables | Those are MW2022/BO6 and teach the wrong conventions. |
| Stripping `_geo_rigid_bs_` as its own rule | Underscore truncation already covers it, and mesh names are unobtainable anyway. |
| Feeding the hash tables in as candidate input | A closed loop. 87% of `consolidate`'s work, zero names. |
| Hunting `localizeentry` | The entry holds a pointer to its own unhashed string — the plain text is already in the build. 8,667 confirmed in one pass, all worthless. `confirm_localize` now refuses to run. |
| Hunting `streamkey` | ~290,000 genuine, useless hashes, mostly sequential `d3dbsp` terrain. The largest pool in both games, so anything that "opens up every pool" lands here first. `submit` refuses to send them. |
| Widening `pools` to ~40 asset types by guesswork | One submission did. Nothing useful came of it, and the real findings were buried among the rest. |
| Searching four pools because they had "sound" in the name | `sound`, `sound_asset`, `sound_bank`, `sound_duck`. Only `sound_asset` is worth anything, and only in Cold War. |
| Cross-type generation involving `xanim` and a non-model type | Measured: 13 to 22 shared cores out of tens of thousands. There is no seam. |
| Recombining the **zombies** family into Black Ops 4 xmodels | `contrib/zombie_models.py`, 20260821: every model name already known to carry `zombie`/`zmb`/`zm_` cut into 46,306 stems and recombined against 24 model beginnings and 407 endings. **452,317,008 candidates, 0 matched** -- not a low yield, a zero, against 20,922 unnamed BO4 model ids. The family's vocabulary is not the constraint: the unnamed models are not spelled out of pieces the named zombies models use. A wider ending set is the obvious next try and the measurement says not to bother with the same stems. |
| Re-measuring the lists to reopen a spent method | `derive_lists.py` folds the confirmed names in, the fingerprint changes, and the tool stops saying the search is swept — so it looks like the method reopened. Three consecutive folds: **55 names, then 294, then 51**, the last on a corpus two and a half times larger. The lists are capped, so a fold displaces as much vocabulary as it adds; what reopens a method is different ground. This was `next_step`'s standing advice for a month and is most of how a 165-name pass became a 2-name one. |
| Uncarried beginnings crossed with the whole corpus, in general | The shape that returned 2,846 for `mcdp/` returns almost nothing anywhere else. Measured 2026-08-23: all 1,075 uncarried beginnings against the 879,325-core held vocabulary gave **0 on Black Ops 4 and 7 on Cold War** in 945 M candidates. `mcdp/` worked because 692 of 692 of its cores were borrowed from other directories -- it was a re-decoration of a vocabulary already held. Rank by *borrowed share* before building one of these (`scripts/contributed/redecorations_20260823-023757.py`); the rest of the uncarried beginnings have private vocabularies and this shape cannot reach them. |
| Cold War sound files, numbered takes | 36,971 of the 39,199 recovered basenames end in a number, so this looked like the obvious shape. Swept every index in every measured width against every measured tail on 2026-08-23: **0**. Verified not to be a plumbing failure -- 2,783 of 2,816 numbered seeds reconstruct exactly from the stem and ending lists. The game's take runs are already fully named. |
| Cold War sound files, directory x basename recombination | The same corpus, 248 real directories x 103,120 cores x the 16 commonest tails, 436 M candidates: **0**. Verified the same way -- 31,842 of 31,845 recovered names reconstruct exactly as directory + basename + tail. A Cold War sound basename does not appear under a directory the tables have not already caught it under. |
| Black Ops 4 sound files, numbered takes and recombination | The largest pool in either game (70,878 unnamed of 79,263) and the most expensive negative here: 2,572 directories x 10,538 cores x 13,995 numbered-take endings, **379 billion candidates unfolded, 0 matched** -- not 0 new, 0 hits of any kind. Whatever the unnamed 70,878 are, they are not recombinations of the 5,977 that are named. **Independently checked 2026-08-23** (`scripts/contributed/bo4_sound_plumbing_check_20260823-140622.py`): a zero this total is also the signature of a sweep that never built a valid candidate, so the vocabulary was rebuilt exactly as `bo4_sounds.py` builds it and asked whether it can express the names that *are* known. It can -- **8,581 of 8,583, 100.0%**, against the 99.99% the Cold War negatives were certified at. The plumbing is sound and this zero is a real property of the game. Two scope notes, neither of which reopens it: the engine hunts only *unnamed* ids, so a candidate rebuilding a known sound is correctly not counted as a hit and "0 hits" is consistent with working plumbing; and the recovered corpus has since grown from 5,977 to **8,583**, so the claim is exact for the vocabulary measured and slightly narrower than the corpus now available. |
| Black Ops 4 `sound_asset`, all-boundary cores x uncarried endings | The standing Black Ops 4 sound negative closed *numbered takes* and *directory x basename recombination*, both of which recombine within one segment depth. Method 25 is a different relation -- cores cut at every backslash, underscore and dot, so a core five segments deep in one path can wear a two-segment ending from another -- so it was not covered and was worth one pass. Measured 2026-08-23 against the recovered corpus (8,584 names, method 21, not the 178 in `all_names/`): 35,456 all-boundary cores x 4,434 endings this pool's own names wear and `data/sound.suffixes.txt` cannot express, 157 M candidates unfolded, **0**. The ending gap here is real and large -- 7,424 of 8,584 recovered names, 86%, end in something the carried list cannot say -- so this is not a vocabulary failure. It is the third distinct shape to return zero against this pool, and together they say the unnamed 70,679 are not built from the pieces the named 8,584 are built from, under any recombination tried so far. Generator: `scripts/contributed/bo4_sound_allboundary_20260823-151952.py`. |
| Black Ops 3 SAB names respelled as Black Ops 4 | Black Ops 4 is Black Ops 3's direct sequel on the same audio pipeline, same directories, same dotted-tail grammar -- so the paths ought to carry over. 3.06 billion candidates, lower cased, language directory dropped, every Black Ops 4 tail restored: **0**. |
| Cross-game sound transfer at full recovered vocabulary | METHODS lists this at 27 names, found when the seed corpora were 148 and 172 names. Re-run on 2026-08-23 with the recovered corpora -- 39,199 Cold War paths against Black Ops 4 unfolded, 5,977 Black Ops 4 paths against Cold War folded, both slash spellings: **0 each way**. The bigger corpus does not reopen it. |
| Doubly uncarried -- an uncarried beginning over an uncarried ending | Both halves are productive alone (6,674 names from endings, 2,846 from `mcdp/`), so the cross looked like the obvious next question. 100 uncarried beginnings x 458k middles x 5,000 uncarried two-segment endings, **229 billion candidates: 0**. A name is reachable through one cap or the other, not through both at once -- the middles that survive stripping a segment off each end are too short to identify anything. |
| The animation transition grid, composed rather than observed | `xanim` is the least-named type in both games and has a real grammar: 6,149 published names match `<core>_<from>_to_<to>` over 1,446 cores, 101 from-states and 129 to-states. That grid is 18.8 M combinations and the tables hold 0.03% of it, so composing the two state vocabularies looked like free ground. 50k cores x 13,029 composed transitions: **1 name a game**. The unobserved pairings are unobserved because they do not exist -- a weapon has the transitions its state machine allows and no others. |
| Materials from image cores through the thirteenth directory | `mcdp/` swept against every published material core returned 2,846, so asking the same directory from the image side looked like the other half of the seam. **0 both games.** The material-core sweep had already taken it; image cores add nothing `mcdp/` did not already reach. |
| The `vox_` slot grid composed three deep, on Black Ops 4 | The same shape returned 184 on Cold War, so it looked like a method rather than a coincidence. 425 speakers x 381 x 423 composed slots, **68.5 M candidates against Black Ops 4: 0**. Pairing a speaker with a *whole observed tail* still pays there -- 17 of the 23 that method 30 found were `sound_alias` -- so what fails is composing the slots, not the family. Black Ops 4 records fewer lines per speaker than Cold War does, and the unobserved combinations are unobserved because they were never recorded. |
| The cosmetic-bundle grid -- store themes crossed with store item wrappers | The one family this project owns outright: **5,652 names end in `_mtxitem` and 0 of them are published**, so unlike every other seed family its unnamed remainder cannot already have been claimed upstream. It is also a genuine product grid rather than a recombination -- a season ships one theme as a calling card *and* an emblem *and* a charm *and* a blueprint -- and the record proves the axes cross: **213 of 3,982 theme cores (5.3%) already appear under two or more item families** (`quartermaster`, `moonshiner`, `zombiepark`, `jacklinks`, `sovietnavy`), with calling-card/emblem carrying most of them. 336 learned wrappers x 15,647 themes x 120 `_mtxitem`-terminated tails, 636 M candidates: **0 on Black Ops 4 and 0 on Cold War.** Positive control passed -- **5,547 of 5,652 known `_mtxitem` names, 98.1%, are expressible** from those three lists, so the plan covered the space and the space is empty. This is the fourth grid to answer this way after the animation transition grid and the `vox_` slot grid, and together they say the same thing: **a store shipped the cells it shipped.** An unobserved cell in a product grid is unobserved because it was never made, not because nobody recorded it. Generator: `scripts/contributed/mtx_bundle_grid.py`. |
| Every confirmed name of one title, tried verbatim in the other | Listed under *Candidates worth building* as `cross_game.py` from the beginning and never built, on the reasoning that Cold War carries a great deal of Black Ops 4's content so the two corpora are not independent. Built 2026-08-24: 173,046 spellings -- every name in `findings/` and `submissions/` for both games, folded and unfolded -- against each game's unnamed ids. **0 matched, both directions.** Nothing published can land here by construction, since the tables *are* the exclusion set, so this tested exactly the names cod-name-db has not caught up with; the answer is that shared content is already named on both sides. Costs two minutes and needs no plan. Generator: `scripts/contributed/cross_game_verbatim.py`. |
| The lighting bake's own grid -- `volume<V>_state<S>_<kind>_<map>_<index>` | Every grid recorded dead above is **authored**, and the dead ends draw one conclusion from them: *a store shipped the cells it shipped*. This one is emitted by the lighting bake, so that argument does not apply -- a compiler that writes cell 41 and cell 43 wrote cell 42 -- and the density says so before anything is hashed: 380 (map, volume, state, kind) groups over 31 maps, **288 of them, 76%, with a completely contiguous index run 0..max**, and 18,350 indices missing inside the runs that are not. 4,816,896 candidates over three bands -- gaps inside observed runs, extension past each run's maximum, and the (volume, state, kind) cells never observed for a map that is observed -- **0 matched in both games, and not 0 new but 0 hits of any kind.** Positive control run precisely because a zero that total is the signature of a sweep that never built a valid candidate: of the family's 41,537 distinct published hashes, **23,216 are present in the Cold War snapshot and 0 in Black Ops 4**, so the vocabulary is exactly expressible, the ids really are there, and the family simply does not exist in Black Ops 4. Cold War's bake output is already fully named, and the holes are cells that title never baked. The map stamp is 8 hex digits and unguessable, so this could only ever reach the 31 maps already published -- but that ceiling is not what stopped it. **The generalisation worth keeping: a tool-generated grid is dense but still complete, so its unobserved cells are just as empty as an authored one's.** Generator: `scripts/contributed/baked_volume_grid_20260829-061359.py`. |
| ~~Method 25 on Black Ops 4, every segment depth~~ | **Retracted the same day it was written, 2026-08-29 -- the sweep never varied its input.** The claim was depths 1 to 5 returning 0, 0, 4, 0, 0 against Black Ops 4. The generator writes its two lists to `contrib/ab_ends.txt` and `contrib/ab_cores.txt`; the plans were written against `borrowed/ab_*.txt`, which is a different pair left over from 2026-08-23. So every "depth" ran the *same* stale lists, the four names came from the first run, and the four zeros after it are what re-sweeping identical ground looks like. Nothing about segment depth was measured. The real result for Black Ops 4 at depth 3 on freshly generated lists is recorded separately below; the lesson worth keeping is that **a plan naming a `@path` that exists but is stale fails silently and looks exactly like a negative** -- `confirm_plan` prints its stem and ending counts before it runs, and those numbers not matching what the generator just reported is the check that catches it. |
| Numbered families as grids on **two** axes | `families.py --gaps` walks the *last* numeric run in a name and fills holes in it. A name carrying two numbers sits in a rectangle, and `families.py` keys its family on everything before the last number -- so `p7_..._01` and `p8_..._01` are unrelated families to it and it can never propose a cell by reasoning across them. Listed under *Candidates worth building* as `numbered_grids.py` from the beginning and never built. Built 2026-08-24: roughly **a third of every name in the corpus carries exactly two numeric runs** (material 36.6%, image 36.8%, xmodel 35.4%, xanim 20.8%), giving 983 rectangles of at least 2x2 whose cells the corpus has never shown. 128,899 candidates at margin 2, against **both** games: **0 matched, 0 hits of any kind** -- against 126,331 unnamed Cold War ids and 166,703 Black Ops 4 ones. Positive control passed and is the part worth keeping: **1,482 of 1,482 observed cells, 100.0%**, rebuild byte for byte from the template, and 543 of them (36.6%) hash to an id the Cold War snapshot actually holds -- so the plumbing is sound and the holes are genuinely empty. This is the **fifth** grid to answer this way after the animation transition grid, the `vox_` slot grid and the cosmetic-bundle grid, and it is the most general of them: those three each composed a *semantic* vocabulary, where this composes bare integers and so carries no assumption about meaning at all. Together they close the shape rather than three instances of it -- **an unobserved cell is unobserved because it was never made.** Do not build a sixth. Generator: `scripts/contributed/numbered_grids_20260824-155834.py`. |
| Reading candidates with `BufRead::lines()` | Not a search dead end but the same lesson: the `String` per candidate *was* the program, capping `confirm_list` at 5.2M/s against 64.3M/s for raw bytes. |
| `material` cores (`no tail`) spelled as `image` (`no ends`), Black Ops 4 only | `seam_stems.py --from material --from-reduce "no tail" --to image --to-reduce "no ends"` measured 18,868 shared cores and 169,141 only-in-material, which looked promising next to the already-dead `no head`/`no ends` pairing. Capped at 20,000 stems x 24 measured image beginnings x 24 endings, **12.5M candidates against Black Ops 4's unnamed ids only: 0.** Consistent with the existing material/image dead entries above: `seam_stems.py` pools both games' names by default (it has no `--game`/`held` narrowing, unlike `seams.py` itself), so a shared-core count measured across both games overstates what is reachable in one. |
| `xmodel` cores (`no tail`) spelled as `xanim` (`no tail`), Black Ops 4 only | Untested pairing -- METHODS' dead-seam table only covers material/image and material/xmodel, not xmodel/xanim. `seam_stems.py` measured 537 shared cores of 101,587 xmodel / 16,838 xanim, alphabetically-first 30,000 of the 101,050 xmodel-only cores x 24 measured xanim beginnings/endings. **18.75M candidates against Black Ops 4's unnamed ids: 0.** Matches the existing "cross-type generation involving `xanim` and a non-model type: no seam" entry above; this extends it to model↔anim specifically under the all-boundary reduction pair. |
| `material` cores (`no head, no numbers`) spelled as `xmodel` (`no numbers`), Black Ops 4 only | The material/xmodel dead entry above only covers the `no ends`/`no tail` reduction pair. This one measured higher overlap -- 13,193 shared of 217,858 material / 135,508 xmodel cores -- so it looked like a different cut of the same seam might reach further. 30,000 of 204,665 material-only cores x 24 measured xmodel beginnings/endings, **18.75M candidates against Black Ops 4: 0.** Third seam-based zero in a row this session (after material→image and xmodel→xanim above); together they support what METHODS already concluded about the strongest rows here -- shared-core counts under `seam_stems.py` describe both games pooled and do not translate into hits against either game's specific unnamed remainder. |
| `cross_era.py` (newer-title cores respelled) on Black Ops 4, 2026-09-01, at 1,038 confirmed names | The doc's own pitch for this method is strong -- importing vocabulary from *outside* the corpus is what's measured live, against recombination which is measured dead -- so it looked like the best untried big swing left this session. `python scripts/cross_era.py --write-plan`: 1,178,593 newer-title names (Vanguard/MWII/MWIII/BO6/BO7) reduced to 2,431,781 cores new to us, spelled with our 1,200 measured beginnings and 6,000 endings. **17.5T candidates against Black Ops 4 specifically, run in 8 slices: 0 matched in every slice, 0 total.** This narrows the existing "newer-title `_v2` tables hashed verbatim: 0" dead entry -- that measurement hashed the newer names *as spelled*, and the standing theory was that only the *cores* survive an engine change. Respelling those cores with our own conventions still returns zero against Black Ops 4's specific unnamed remainder. Consistent with the "engines renamed rather than inherited" conclusion already on record; extends it from "verbatim spelling doesn't transfer" to "the underlying vocabulary doesn't obviously transfer either, at this corpus size." The lifetime `cooling` figure in the efficiency table predates this run and mixes in Cold War and an earlier, smaller corpus -- worth re-checking there before assuming this is dead everywhere. |
| `family_grid.py --top 20`, Black Ops 4 only, 2026-09-02 | Composes the unseen cells of the 20 largest numbered/grid-shaped families (`vox_`, `i_`, `fly_`, `vm_`, `ui_`, `wpn_`, `p8_`, `mp_`, `p7_`, `amb_`, `jup_`, `p9_`, `melee_`, `sat_`, `zmb_`, `callingcards_`, `evt_`, `icon_`, `pt_`, `weap_`) against the 2.2M-name corpus at that point. **4.3M candidates against Black Ops 4: 0.** Consistent with `scripts/contributed/` already carrying dozens of per-family `*_shared_tail_grid_*.py` variants for most of these exact families (`amb`, `att`, `evt`, `fly`, `i`, `icon`, `jup`, `mpl`, `mus`, `p7`, `p8`, `p9`, `pt`, `sat`, `ui`, `uie`, `vm`, `weap`, `wpn`, `zmb`) -- the generic top-N sweep is ground several other contributors have already picked over cell by cell. |
| Uncarried beginnings (212 of them, everything but `mcdp/`) crossed with the whole corpus, Black Ops 4 only, 2026-09-01 | Re-run of the dead-ends entry above ("uncarried beginnings crossed with the whole corpus, in general") scoped to Black Ops 4 only rather than both games, on the corpus as it stood after this session's other passes (1,038 confirmed). `scripts/uncarried.py --least 20 --write-plan` -- 212 beginnings no cut of which `data/prefixes.txt` carries (`collision_`, `o_`, `icon_`, `ach_`, `s4_`, `electrical_`, `debris_`, `special_`, `core_`, `server_`, `hue_`, `lut_`, `volume14_/15_`, `cob_`, `bo3_`, `day_`, `un_`, ...), 236,465 stems, all 4,629 general endings. **232B candidates, 0 new.** Confirms the earlier finding was not a Cold War artifact: `mcdp/` really was the one uncarried beginning with a re-decoration story (692 of 692 cores borrowed from other directories), and the rest of this list has private vocabulary this shape cannot reach, in Black Ops 4 either. |
| A legacy name corpus found on disk, diffed against the published tables | The complement of the *re-hashing the newer titles' names* row above: that one asked whether the tables' **newest** sources reach these two games, this one asks whether their **oldest** ones were folded in completely. An earlier generation of community name data shipped its sources as plain CSVs under a hash function that means nothing to us, so only the name strings matter. **1,782,690 distinct names** across eleven files, compared by string against all 3,565,276 names the current tables hold: **2,434 absent, 0.14%**, and all 2,434 come from a single image file whose names are in a composite spelling (`colour&spec~<decimal>`, `*reflection_probe_octahedron_N`) that neither of our two titles uses. Offered verbatim plus every decomposition of that spelling -- 7,946 candidates -- against both games: **0 and 0.** **Confirming against the snapshots is the whole point of this one:** a legacy index like this is a community artefact, not a dump, and a large share of what it holds is not a real asset in *any* of these games -- so a name being absent from the tables says nothing on its own, and only a hash landing on an id the snapshot actually holds is evidence. The scrape was not sloppy; it was essentially complete, and the one file it half-carried holds nothing either game could hold. Worth knowing for the reach figure it produced on the way: the legacy corpus lands on **194,257** real Black Ops 4 ids and **520,874** real Cold War ids, overwhelmingly in the wanted types, so this vocabulary genuinely describes these games -- it is simply already all in the tables. Generator: `scripts/contributed/legacy_index_gap.py`. |
| The store's loot-icon grid, filled in past what is observed | Black Ops 4 names store icons on a strict four-axis grid -- `<family>_ui_icon_<kind>_<theme>_<tier>_<subject>`, as in `loot02_ui_icon_outfit_northern_lights_legendary3_seraph` -- and every axis is a closed vocabulary measured straight off the corpus: 8 families, 17 themes, 15 tiers, 99 subjects. That multiplies to 201,960 cells against **3,452 observed**, so 98% of the grid looked open. The counts made it look better still: the thirteen specialists appear 19, 19, 20, 20, 20, 20, 21, 21, 22, 22 and 23 times, which is the signature of a grid the game filled in rather than a sparse one. **0 of 201,960.** This is the same answer the animation transition grid gave and for the same reason -- the unobserved cells are unobserved because they do not exist. A bundle ships for the specialists it ships for. **The general lesson, now measured twice: an axis vocabulary being closed and a grid being dense do not imply the empty cells are real, and regular counts are not evidence either.** Enumerate a grid only where something outside the naming says the cell exists. Generator: `scripts/contributed/loot_icon_grid.py`. |
| Recombining sound aliases **inside the cell the game files them in** | The standing sound negatives could all be read as "the corpus was too coarse" -- recombination over one undifferentiated pool spends everything on pairs that were never going to go together. The alias definition tables let that be fixed exactly: every alias carries a plaintext zone, volume group and duck group, so the pool splits into 1,301 (BO4) and 761 (CW) cells of sounds that genuinely belong together, and the cells are tight -- the commonest two-token prefix covers a median 45-48% of a cell, and the best of them hold 661 unnamed aliases beside 216 known names sharing **one** prefix between them. Fourteen plans over Cold War's biggest cells, each recombining a cell's own heads x cores x tails and nothing else: **0.** So the coarseness was never the problem. Partitioning the corpus perfectly, using the game's own filing rather than a guess, does not reach these names either -- which closes the last reading under which recombination might have worked here and says the unnamed aliases are not built from the named ones at any granularity. Generator: `scripts/contributed/alias_cells.py`, which writes one plan per cell. |
| `mp_<operator>_<tail>` shared-tail grid, Cold War only, 2026-09-08 | `unnamed_profile.py --grid` flags `mp` as one of the largest unexplored grid-shaped families (263 axes x 13,476 tails observed, millions of raw cells). Restricting to tails attested with more than one operator axis -- the same restriction every other `*_shared_tail_grid` generator in `scripts/contributed/` uses -- cuts it to a plan-free 263 axes x 530 shared tails = 138,072 candidates. **0 matched on Cold War.** This is consistent with, and extends to Cold War, the existing "`family_grid.py --top 20`, Black Ops 4 only, 2026-09-02" entry above, which already swept `mp_` (among 19 other families) on Black Ops 4 for 0. Between the two runs `mp_` is now measured dead on both games under the shared-tail restriction. Generator: `contrib/mp_shared_tail_grid_20260908.py`. |
| `token_edits.py`, all four applicable types, Cold War, 2026-09-08 at 3,660,753 known names | Method 14 (token insertion/deletion) had not been re-run since the corpus was much smaller (13.1M candidates quoted for models back then). Re-measured fresh against the grown corpus: model 13,825,895 candidates, material 33,293,881, image 33,166,554, anim 3,115,436 -- **0 matched, 0 new, in every one of the four.** Deletions need no vocabulary and are the higher-precision half per the method's own notes, so this is a real exhaustion rather than a vocabulary gap: the corpus's growth since the method was last run added nothing an insertion or deletion could reach. Re-check only after the corpus grows substantially again. |
| `slotswap.py --context left`, Cold War, 2026-09-08 at 3,660,753 known names | Re-run of method 10's looser one-sided form (previously measured at 660 names on Black Ops 4, 2026-08-19) against the grown Cold War corpus. 354,998,635 candidates, **14 matched, 0 of them new** -- every match was already known. The two-sided form (`--context both`) found 12 new names earlier the same session on the same corpus; the one-sided widening did not add to that this time. `--context right` on the same corpus did pay -- 313,996,264 candidates, 4 new xanim names -- so the asymmetry is real: the token *after* a slot generalises better here than the token before it. |
| `templates.py --key 2`, Cold War, 2026-09-08 at 3,660,786 known names | Method 11's own note says it is "spent by the bucket key" and to re-run with a different one. `--key 2` (two leading tokens fixed instead of three) actually produces *fewer* candidates than the default -- 19,784,200 against the default's 55,113,580 -- because looser bucketing pulls more members into each family, which pushes more columns over `--max-axis 8` and disqualifies them as axes rather than opening more up. **0 matched.** The default `--key 3` run earlier the same session, on the same corpus, found 2 new xanim names; this confirms that result rather than extending it -- the two bucket widths are not independently productive here, at least not in this direction. `--key 4` (tighter bucketing) is untried and would cut the other way -- smaller, more homogeneous families, likely more qualifying axes -- but was not measured this session. |
| `templates.py --max-axes 4`, Cold War, 2026-09-09 at 3,660,894 known names | Default caps at 3 columns varied at once; widening to 4 -- letting a candidate differ from every known name in one more place simultaneously -- produces 62,461,822 candidates against the default's 55,113,580. **146 matched, 0 of them new.** Run right after this session's general search and sound pass had already pulled in 35 fresh names (17 sound_alias, 13 from the general search's xanim/xmodel, 5 from `confirm_variants swaps`), so this had genuinely new seed material to work with and still found nothing beyond what 3 axes already reaches. Widening the axis count is not where this method's remaining reach is, if any is left. |
| **All twenty `*_shared_tail_grid` generators, both games, 2026-09-09 -- and a real bug found and fixed on the way** | These generators (`amb`, `callingcards`, `emblems`, `evt`, `fly`, `i`, `icon`, `jup`, `mpl`, `mus`, `p7`, `p8`, `p9`, `pt`, `sat`, `ui`, `uie`, `vm`, `weap`, `zmb`) were listed by `start` as part of the script library and had been counted as "already covered ground" earlier in this session on that basis. **They could not actually run.** Every one of them resolves its own path with `ROOT = pathlib.Path(__file__).resolve().parent.parent; sys.path.insert(0, str(ROOT / "scripts"))` -- correct if the file lived two directories above the repository root, which is where `contrib/` scripts sit, but wrong once `submit` promotes a script into `scripts/contributed/`, three directories down: `ROOT` there is already `scripts/`, so the inserted path is a doubled scripts/scripts folder that does not exist, `import snapshot` fails with `ModuleNotFoundError`, and the generator produces nothing at all. Every one of the twenty had this exact bug, meaning **none of them has run successfully since being committed to the library** -- the sibling method that seeded this session's own `mp_shared_tail_grid` (`wpn_shared_tail_grid`) uses the older, robust pattern (`while ROOT != os.path.dirname(ROOT) and not os.path.isfile(...): ROOT = os.path.dirname(ROOT)`), which is why it worked and looked identical in shape to the twenty that did not. **Fixed** with a one-line change per file (`sys.path.insert(0, str(ROOT))`, since `ROOT` already *is* the `scripts/` folder) and verified each runs standalone afterward. Then actually run, all twenty, both games: `amb` 95,089 candidates, `callingcards` 22,655, `emblems` 13,050, `evt` 21,669, `fly` 440,760, `i` 701,768 (the single largest shared-tail grid measured anywhere this session), `icon` 19,291, `jup` 78,586, `mpl` 2,688, `mus` 11,330, `p7` 121,273, `p8` 172,114, `p9` 59,920, `pt` 15,517, `sat` 29,925, `ui` 215,157, `uie` 10,814, `vm` 343,028, `weap` 13,046, `zmb` 40,144 -- roughly 2.43M candidates in total. **0 matched, in every one of the forty runs (twenty generators x two games).** So the shared-tail restriction that works for `wpn_` and `mp_` (both measured dead earlier) does not reach anything for these twenty families either, now that they have actually been asked. The value here is not the zero -- it is that the zero is now a *real* measurement instead of an assumed one, and the fix means the next contributor who reads `start`'s script list and picks one of these twenty gets a working method rather than a silent no-op. |
| Sound take-number gap filling, both games, 2026-09-08 | `scripts/families.py`'s numbered-family regex matches the **last** run of digits in a whole name, and sound alias/file names routinely end `..._00.rn75.pc.en.snd` -- a fixed codec/language tag whose own digits (`rn75`'s `75`) sit *after* the real take number, so `families.py` groups on the codec tag and the take-number axis is structurally invisible to it. Confirmed directly against the published sound tables (`fnv1a_soundbanks_aliases[_v2]`, `fnv1a_xsounds[_v2]`, all twelve per-language `xsounds` tables) plus this project's confirmed and merged names: **909,650 names** carry a `_<NN>.<anything>` shape across 214 codec/language extension combinations, and of the 285,259 families that shape implies, **219,177 already have two or more members observed** -- a missing take is the common case, not the rare one. Applying `families.py --gaps`'s own algorithm (same margin, same `WIDEST` cap) with a regex anchored on `_(\d{2,3})\.` instead of the last digit run: 915,696 candidates, **0 matched on Cold War, 0 matched on Black Ops 4** -- checked on both since this is exactly the shape of gap that could matter most for Black Ops 4's `sound_asset` pool (70,649 of 79,263 unnamed, the largest in either game), and it did not. A clean, complete zero on real structure at real scale, not a vocabulary or margin problem: the take numbers the game actually shipped are exactly the ones already in the tables, and the gaps between them are gaps in what was recorded, not in what was recorded *of*. Extends the standing "structural overlap has now failed to predict yield three times" lesson to a fourth and fifth case. Worth fixing in `families.py` itself regardless -- it is a real blind spot in a report as well as a generator, and the next family it silently misclassifies may not be a dead end. Generator: `contrib/sound_take_gaps_20260908.py`. |
| `sound_languages.py`, Black Ops 4, folded and unfolded, 2026-09-10 | `derive_closure.py` runs this derivation labelled "Black Ops 4 only" and has returned 0 every round for days, which raised a real question: `derive_closure.py` never passes `--no-fold` to any derivation it runs, and CLAUDE.md §6 measures that Black Ops 4's sound ids only reproduce **unfolded** (8,385 of 8,385 known names reproduce unfolded, 0 folded) -- so every one of those zeros could have been the fold bug rather than a real negative. Tested directly against the corpus as it stood after this session's `images_from_materials` gains (3,369 confirmed): 4,155,817 candidates (13 language codes x 3 encodings, every seed from `fnv1a_english_xsounds` and the eleven other per-language tables plus this machine's confirmed names) run twice, once folded and once with `--no-fold`, both against the same 118,272-id wanted set (`sound_asset` included and confirmed present in both runs' pool list). **0 matched both ways.** So the missing flag was a real gap in `derive_closure.py` worth fixing regardless -- a Black-Ops-4-only derivation that can structurally never match half the time is a bug independent of what it finds -- but it is not the reason this method has returned nothing: the respelling itself does not reach any currently-unnamed Black Ops 4 sound id, fold or unfold. Extends the standing sound-asset dead-end record with the one variant (language/encoding respelling) it had not yet covered under a controlled fold test. |
| `final_byte.py`, Cold War, re-run 2026-09-11 at 1,677,099 assets / 8,443,027 resolved hashes | Last run 2026-09-08/09 solved ~10,150 candidates off a smaller table refresh; re-run after this session's clone update and hash-table refresh to see whether the intervening growth reopened it. 12,051 candidates (up from ~10,186), **0 matched, 0 new** -- the extra ~1,900 candidates are ids the backwards solve can now reach that it could not before, and every one of them is either already published or already in this machine's own `findings/`. Consistent with the general pattern that this method is bounded by how many *known-name prefixes* exist to solve against rather than by how many unnamed ids there are, and that count has not moved enough since the last run to open anything new. Free to re-check (12K candidates, under two minutes even sharing the machine with a 173B-candidate pass), so worth re-running after any batch of new confirms lands rather than left for days. |
| Dedicated Cold War sound pass (`confirm_cw --sounds`), re-run 2026-09-11 less than a day after the 2026-09-10 run (1 new then, off a `sound_asset` vocabulary of 12 confirmed names) | Re-run after `sound_languages.py` more than doubled the confirmed `sound_asset` seed count (12 -> 27) via the closure gain above, on the theory that a vocabulary jump that size might open new stems even on a one-day-old pass. 91.0B forward hashes, **0 matched, 0 new.** The extra confirmed sound names did not translate into new stems or endings the sound-specific lists hadn't already captured. Re-check after a larger or more structurally different batch of sound names lands, not after an ordinary closure round. |
| `derive_lists.py`, then the Cold War sound pass again immediately after, 2026-09-11 | `python scripts/derive_lists.py` (no `--game`; the lists are shared across both games) reported `sound.prefixes.txt` was **over its 700 cap by 101 measured beginnings**, the largest being `fly_emote_` at 324 names -- a real ceiling cut, not the "re-measuring to dodge a fingerprint" pattern CLAUDE.md §8 warns against, since the report itself is what flagged lost vocabulary. The refresh genuinely changed the list (`git diff` shows new deep prefixes such as `vox/scripted/mpl/`, `mpl/mpl_casino/chips/`, `wpn/zmb/freezegun/zombie/shatter/` that were not there before) and produced a fresh fingerprint -- the immediately following sound pass ran clean rather than hitting the exact-duplicate guard. **0 matched anyway**, same 91.0B forward hashes, same 0 new as the run five minutes earlier on the old lists. So this extends the standing "re-measuring the lists is not the way out" lesson one step further: it holds even in the one case that looked like the documented exception (a real, measured ceiling cut rather than routine growth). The displaced vocabulary evidently was not where this pool's remaining names are. |
| `images_from_materials`, Cold War, full run to completion 2026-09-11 (`--anyway`, futility guard cleared -- last 7 confirming runs on this machine were the 2026-09-08/09/10 dead-end measurements recorded above, not carelessness) | The 2026-09-10 attempt at this exact pass got to 96% of its single largest slice and stopped mid-run without a final tally -- interrupted, not measured, since the binary checkpoints its finds but not its slice position. Re-run clean start to finish: 575,703 published materials plus this machine's 141 confirmed, 891,626 stems total, sliced 16 ways over 518,556 endings taken from both the material and image tables, **16 slices x ~173.4B candidates = 2.77T candidates against Cold War's unnamed image/material/xmodel/xanim/sound ids, 0 matched in every slice, 0 total.** Matches `scripts/README.md`'s standing "near-spent: 7 names in Cold War" note and extends it to fully spent at the current corpus and table state -- unlike Black Ops 4, where the same binary is still adding names most times it runs (58 the same week), Cold War's material/image seam has nothing left for this shape at this corpus size. Re-check only after a large batch of new Cold War materials or images lands, not on the ordinary week-to-week growth from table refreshes alone. |
| General search (`confirm_cw`), Cold War, re-run 2026-09-14 after a stale local clone was rebased onto three days of upstream merges (245,673 -> 295,855 merged names on disk, almost all Black Ops 4 sound_alias/sound_asset from Kenshin9977's and ImSimpy's recent sessions) | Cold War itself had gone untouched by that activity, and `derive_lists.py` re-measured right after the rebase to see whether the influx moved the committed general lists at all -- it barely did (`data/prefixes.txt` and `data/suffixes.txt` each changed by 4 lines; the sound lists did not change at all), which already predicted a thin result before anything was searched. Ran anyway since the fingerprint (method, game, pools, flags, the two lists) had not been exercised by anyone since the refresh: 700 beginnings x 4,800 endings x every stem, sliced 13 ways, **295.6 billion forward hashes in 3,951s, 0 matched, 0 new.** Consistent with the standing "the loop is fed by other people's names, not your own" lesson (the compounding-loop section above) -- three days of a *different* game's sound-alias vocabulary does not move Cold War's general (non-sound) lists, so a rebase alone is not a reason to expect this method to reopen. `submit` correctly reported nothing to send. |
| Dedicated Cold War sound pass (`confirm_cw --sounds`), re-run 2026-09-14 right after the general search above and the rebase merge | Same shape as the 2026-09-10/09-11 runs recorded above, re-checked once more since the clone had just pulled in three days of upstream merges. 700 beginnings x 3,014 sound endings, sliced 4 ways, **91.0 billion forward hashes in 1,337s, 0 matched, 0 new** -- the exact same candidate count as the 2026-09-11 runs, confirming `derive_lists.py` really did leave `data/sound.prefixes.txt` and `data/sound.suffixes.txt` byte-identical this time (see the general-search entry above: the merge was almost entirely Black Ops 4 vocabulary). A third consecutive zero at an unchanged fingerprint; do not re-run this exact configuration again without a Cold-War-specific vocabulary gain. |
| `final_byte.py`, Cold War, re-run 2026-09-14 after the `derive_closure` image-siblings gain (+2) | Free re-check per the 2026-09-11 note's own advice ("worth re-running after any batch of new confirms lands rather than left for days"). 16,642 candidates in 112s, **2 matched, 0 new** -- both matches were the two names `derive_closure` had just confirmed reaching back into the solve's own seed set, not new ground. Two names is not the "materially larger prefix set" this method needs to reopen. |

### `derive_closure.py` could not run at all under the futility guard, and `sound_languages.py` is live on Cold War where it is dead on Black Ops 4 -- 2026-09-11

Running `derive_closure.py` after the images_from_materials pass above (itself a real zero, so the
machine's empty-run streak was already at 9) surfaced a bug that had likely been silently eating
every closure run since the guard was added: `run_derivation`/`run_plan` `Popen` a generator into
`confirm_list`/`confirm_plan` without ever passing `--anyway`, so the confirmer prints the futility
message and exits immediately, closing its end of the pipe -- and the generator's next
`sys.stdout.write` then raises `OSError: [Errno 22] Invalid argument` on Windows instead of a clean
`BrokenPipeError`. Every one of the seven derivations crashed this way in identical fashion; the
round completed and reported "added 0" only because each crash was caught at the subprocess level,
not because anything actually ran. **Fixed** by adding a `--anyway` flag to `derive_closure.py`
itself, threaded into both `run_derivation`'s `confirm_args` and `run_plan`'s `command` -- the
closure is meant to be free and run after *any* pass including a zero, so it needs to survive the
same guard a direct search would clear with the flag.

With the fix, the same round actually ran and added **16** Cold War names: `image siblings of
confirmed materials` +1, `sound language and encoding variants` (`sound_languages.py`) +15, the
rest 0. The second is the interesting one -- `sound_languages.py` is recorded dead on Black Ops 4
just above this entry (0 matched, both folded and unfolded, 4.16M candidates), and the two games
share the same generator and the same derivation slot in `derive_closure.py`. **The relation is
real on Cold War and dead on Black Ops 4 specifically**, not dead in general as the single BO4
measurement might have suggested -- Cold War's sound tables evidently still have language/encoding
respellings the corpus hasn't caught, where Black Ops 4's do not. Worth a dedicated (non-closure)
pass on Cold War beyond what one closure round surfaces, and a reminder that a method measured dead
on one game is a per-game result, not a per-generator one, until it has actually been tried on both.

**The same bug was silently eating Black Ops 4's closure runs too.** Re-run with the fix, `--game
BLKOPS04 --anyway`, immediately after the Cold War one above (so the machine's empty-run streak was
still well past the guard threshold): **13** names in round 1 -- `image siblings of confirmed
materials` +8, `materials from image cores` +3, `final byte solved backwards` +2 -- with round 2
correctly at 0. None of this is new ground; every one of these derivations is already in
`DERIVATIONS` and has run before. What changed is that a closure invoked while three or more recent
passes had returned nothing -- which, per this file's own advice, is closure's best moment, since it
is free and is explicitly recommended as *the* thing to run when a streak of zeros says the corpus
looks closed to what is being tried -- was exactly the condition under which it could not actually
run at all. **The guard and its own recommended remedy were silently incompatible**, and probably
have been since whichever session first hit three empty confirming runs after `futility.rs` shipped.
There is no way to tell from the historical logs how many past closure invocations quietly did
nothing this way; treat any run of `derive_closure.py` recorded as "added 0" without `--anyway`
during a documented empty-run streak as unverified rather than as a real negative.

**Follow-up, same session:** the general search (`confirm_cw`, defaults, `--anyway`) was not
actually spent for Cold War either -- its efficiency-table figures are dominated by Black Ops 4's
much larger run count. The last real full run before this one (2026-09-09) added 16; re-run
2026-09-11 after the corpus had grown by the closure gains above, it swept the same ~295.6B forward
hashes in 3,927s and added **9 more** (3 image, 4 material, 2 xmodel), and the closure that followed
picked up 1 further name from `image_channels.py`. The general search only *looks* dead in aggregate
because most of its recorded runs are against Black Ops 4, which has had 118 passes on this machine
against Cold War's ~28 -- a method's own registry entry can hide a per-game split this wide, and the
efficiency ranking has no per-game breakdown to catch it. Worth remembering next to the standing
"a ranking rules things out, it does not choose" lesson: it can rule out the wrong game's worth of
runs along with the right one's. |

---

## A quirk worth knowing, and deliberately not fixed: ids in two of the five types

**This is not a correctness problem and it does not block anything.** It is written down so the
next person who notices the numbers does not spend an evening on it.

`loader::unnamed` maps each id to **one** pool, and the one it keeps is whichever has the lowest
index — `wanted.entry(id).or_insert(pool)`. Where an id sits in two of the five targeted types at
once, that choice is arbitrary rather than correct, and the name is written to the wrong file
locally.

Measured 2026-08-19: **141 such ids in Black Ops 4, 94 in Cold War.** Regenerate with

```
python scripts/coverage.py            # per-pool totals
```

and a short script over `snapshot.read(...).records` grouping pools by id.

**Almost all of it is `image` + `material`** — 139 of the 141 in Black Ops 4, 90 of the 94 in Cold
War. And an id in both pools means exactly what it says: the game holds an image *and* a material
under that one name, because the id is the hash of the name and both assets carry it. Filing it as
either is **true**. What happens is that it is not *also* listed under the other, so one CSV
upstream is short a row it could have had.

So this under-reports; it does not mis-report. `validate` passes it because the id genuinely is in
the pool it was filed under, and nothing wrong reaches the community tables. The remaining four
ids across both games are single instances of `xanim`+`xmodel`, `image`+`xmodel` and
`material`+`xmodel`.

**Fixing it means `wanted` becoming `id -> Vec<pool>` and every search emitting a row per pool** —
a signature change through six binaries, to gain a couple of hundred duplicate rows. Not worth it
now. If somebody does it, drive the choice from name shape the way `misfiled` does: three separate
bugs in this codebase have come from guessing an asset type against the wrong evidence, and every
one of them looked perfectly reasonable in the log.

---

## What is still not recorded

The fingerprint records that a *configuration* was swept. It does not record which *ranges* within
a method were swept — so `confirm_variants` walking `_01` to `_64` of one family and stopping is
still invisible to the next assistant.

That is the obvious next improvement to how this project remembers itself, and it is smaller than
it looks now that `RunNote` carries arbitrary measurements: a method that records the ranges it
covered into its run note would make this file far more useful than it currently is.
