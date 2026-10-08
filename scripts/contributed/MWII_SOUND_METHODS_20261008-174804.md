# Modern Warfare II sound, and the separator nobody measured

Written 2026-10-08 from a first MWII (`MODWAR22`) grind. Four entries and one dead end, in the shape
`METHODS.md` uses. Every number here was measured on this machine against MWII's own capture.

## The context: MWII had never been searched at all

`state/swept.txt` held 3,434 exhausted configurations and **not one of them was a modern game**:
1,821 Black Ops 4, 1,605 Cold War, 5 MW7, and zero for MWII, MWIII, BO6 or BO7. The reason is not
that nobody chose MWII. `confirm_cw` reads its vocabulary from `data/modern/<game>/`, and **no
`data/modern/` directory existed at all** before `python scripts/derive_modern_lists.py --game
MODWAR22` was run. Until it is, a modern search has no beginnings and no endings, tests no
candidate, and reports success. Deriving it is the first hour of any modern game and is worth
saying so out loud.

Ground, from `coverage.py --game MODWAR22`:

| pool | unnamed | total | named |
|---|---:|---:|---:|
| `sound_asset` (pool 197, named `sndasset`) | 203,952 | 249,863 | 18.4% |
| `sound_alias` (pool 216) | 137,948 | 147,867 | 6.7% |
| `xanim` | 10,782 | 55,778 | 80.7% |

Those two sound pools are **341,900 ids**, against 90,213 unnamed across MWII's other four wanted
types. Sound is where MWII is.

## 1. MWII sound-file names are dot-separated paths, and that is a fact not an artefact

The published `_v2` sound tables store Saluki *display* paths, which use `/`. They are not what was
hashed. Taking the rows a game's own capture holds and asking which candidate spelling reproduces
the stored key:

| game | `sound_asset` verifies with `/` | with `.` |
|---|---:|---:|
| MODWAR22 | 29 | **45,882** |

So a modern sound-file id is the FNV-1a 64 hash, IW offset `0x47F5817A5EF961BA`, of a name like
`iw9.dst.iw9_dst_street_barricade_03.ln.75.48000.all` — periods, a basename, and a four-component
encoding tail.

**Why this matters more than it sounds.** `derive_modern_lists.py` finds a name's directory with
`rpartition("/")`. On a dotted name that finds nothing, the directory collapses into the basename,
and the measured prefix list can only ever express a path component that happens to contain no
underscore. That is the whole reason `sound_asset` sits at 18.4% while `xanim` in the same capture
sits at 80.7%: **nothing in the carried vocabulary can spell a five-segment path.**

Two smaller traps in the same family, both of which fail silently:

* The channelspec is `[a-z]{1,4}`, **not** something containing an `n`. `ll` and `sl` are real and
  sizeable (vehicles, ambiences) and a stricter pattern drops 862 real MWII names while reporting
  success.
* Sound **aliases** are the opposite convention: flat underscore names, no path at all
  (`wpn_pi_usugar9_fire1_plr_fcg`), so a path-shaped method reaches none of them.

`contrib/measure_mwii_sound_spelling.py` and `contrib/measure_mwii_sound_paths.py` are the
measurements.

## 2. The three lists, and the fact that holds them together

Strip the encoding tail, and the component before it is the basename, and everything before that is
the directory. Rebuilt from those three pieces, **45,876 of 45,911 verified MWII names (99.92%)
hash back to their own id** — so the decomposition is lossless and a `beginning + stem + ending`
plan can express a real name. `contrib/validate_mwii_sound_composition.py` checks that without
running a search, which is the cheapest possible test of a new method's premise.

Measured over MWII's own corpus: **1,194 directories, 44,077 distinct basenames across 45,049
names, 22 encodings, 1,499 of 13,620 directory×tail cells filled (11%)**.

That 11% is the tell. A directory×tail grid that is 89% empty is a grid; a basename vocabulary
where nearly every entry is unique to one name is not.

## 3. DEAD END — the whole `directory x basename x tail` product

`contrib/modern_sound_plan.py` is `scripts/sab_plan.py`'s shape pointed at a different separator:
every measured directory crossed with every measured basename and every encoding tail. Cross-game
harvest makes the vocabulary genuinely large — 1,906 directories, 253,249 basenames, 73 encodings,
**3.56 trillion candidates**.

It found **nothing in its first 345 billion**, and one measured number says why it never would:
44,077 distinct basenames across 45,049 names means a basename is nearly unique to its name, so the
product asks 482 million directory/basename pairs to reach the ~253,000 real ones. It buys
essentially no reach per candidate.

This is `sab_plan`'s shape failing for the same reason `sab_plan` itself is weak on Black Ops 4
(36,351,762 candidates, 5 names). **Do not carry a whole-product plan to a game whose basenames are
unique.** Measure the basename-to-name ratio first; it is one line and it decides the method.

A second, cheaper lesson from the same run: **honouring the widest variant index cost a factor of a
hundred.** Fourteen names in the corpus carry a four-digit variant, and taking the widest width
pushed the endings from 7,373 to 730,073 and the plan from 3.6T to 352T. Every binary prints its
expected coincidental matches, and that figure went from **0.28 to 28.1**. Twenty-eight wrong names
in `findings/` seed every later derivation and pass CI, which re-verifies by hash. Pick the variant
width by **coverage** — the narrowest width covering 99.9% of observed indices — never by the widest
one seen.

## 4. What works instead: the trailing token run is the axis

The repetition in these names is not the basename, it is the tail. Every underscore boundary in a
basename is a possible cut; a *head* is `directory + tokens before the cut`, a *tail* is the tokens
after it. Carry a tail only where the corpus attests it in **at least two directories**, so it is
repetition that exists rather than a word that happened to occur once:

| tails attested in | tails carried | heads x tails |
|---:|---:|---:|
| 1 directory | 20,531 | that is just the whole product |
| 2 directories | 4,896 | 84,715,488 |
| 5 directories | 1,257 | 21,749,871 |
| 10 directories | 511 | 8,841,833 |

`npc` is attested in 179 directories, `ads` in 97, `end` in 95, `raise` in 87, and compounds hold up
too: `fire_npc_med` in 73, `reload_end` in 72, `empty_end` in 68.

Because heads are carried at **every** cut, the correct (head, tail) pairing is always in the
product; the mismatched pairings are harmless, they simply do not hash to anything the game holds.
`contrib/mwii_shared_tail_plan.py`.

## 5. Sound aliases are flat, and they answer far better

No directory axis exists for aliases, so the same head/tail cut applies to the whole name. Support
counts (`contrib/measure_mwii_shared_tails_alias.py`): `npc` under **2,928** heads, `plr` under
1,945, `hit_npc` under 1,024, `fatal_npc` under 928, `atmo` under 482. A two-axis grid shows up
directly: `0_hit_npc`, `1_hit_npc`, `2_hit_npc` and `3_hit_npc` are each attested under **exactly
256** heads — the `pri_0..3` slot crossed with a material/polymer pair.

9,088 heads x 3,451 tails = 31,362,688 candidates returned **2,121 names**, one per 14,800
candidates, in 22 seconds. Compare the sound files at one per 301 million. **The difference is
20,000x, and it is the difference between a pool whose event vocabulary is shared and one whose is
per-directory.** When choosing where to point a shared-tail plan, measure the support counts first:
they predict the yield by four orders of magnitude.

**And it is spent.** Three runs of the same method, each a widening of the last:

| run | vocabulary | found | dropped as already claimed |
|---|---|---:|---:|
| MWII only | 9,088 x 3,451 | 2,121 | 0 |
| + MWIII/BO6/BO7/MW7 | 15,903 x 5,504 | 2,048 | 1,047 (51%) |
| + BO4/CW aliases | 53,643 x 19,517 | 1,720 | 1,562 (91%) |

Widening the alias vocabulary buys almost nothing after the first pass. Both legacy and
cross-game alias names hash with the **same Treyarch offset** and are flat, so they are legal MWII
candidates — that is why the harvest is possible at all — but MWII's alias ids are a finite set and
the first plan already reached the cells the extra words fill.

## 6. An engine fact worth knowing before a long plan

With an `end:` column the engine peels endings off the wanted ids instead of hashing forward, and
peeling is only nearly free when the ending list is short next to the candidate count. On
`plans/mwii_shared.txt` (17,303 beginnings, 2,222 endings) it announced "about 23.5B of work
against 262.0B peeling" and then spent **32 minutes of eight cores** building the peeled set
without sweeping a single forward hash.

**Fold the endings into the stem column and write no `end:` line.** The engine cannot peel, sweeps
`beginnings x stems` forward, and the identical candidate count runs at ~96M/s. Same candidates,
same exclusions, same fingerprint inputs — asked in the cheaper order.

## 7. Sound files: what it returned, and where it is spent

`plans/mwii_shared.txt`, 188,237,814,336 candidates at 0.0150 expected coincidental matches,
16 batches, **364 names** from 188 trillion candidates — one per 516 million. Per-batch it decayed
78, 49, 92, 63, 172, 25, 21, 0: real but thin, and thinning.

Harvesting the tails cross-game — heads still restricted to directories MWII has actually been seen
to use, because a head borrowed from BO7 reaches nothing in MWII, while a tail is just a token run
and the more games attest one the likelier MWII's unnamed ids wear it — widens the tails from 4,896
to 13,663 and the encodings from 22 to 53. That is the plan still worth running.

**It did find what only MWII could have held.** Crossing MWII's directories against sound cores
harvested from the other modern games produced `iw9.uin.main_iw8.iw8_leavelobby_alert_v1.ln.75.48000.all`
— a Black Ops 4-era IW8 asset still shipping inside MWII — alongside `mp.emp_expl_npc_lfe.ln.75.48000.all`
and `iw9.exp.exp_105mm_boom3.ln.75.48000.all`.

## 8. An honest limit on aiming

An unnamed id is a bare hash. It carries **no directory, no basename and no tail**, so nothing can
be pointed at one group of unnamed ids rather than another. There is no per-directory targeting
available for any pool. Vocabulary breadth is the only lever, which is why the entries above are
about what the vocabulary can express rather than about which ids to hunt.

## Reproducing any of it

```
python scripts/derive_modern_lists.py --game MODWAR22        # without this, nothing runs
py contrib\measure_mwii_sound_spelling.py   --game MODWAR22
py contrib\validate_mwii_sound_composition.py --game MODWAR22
py contrib\measure_mwii_shared_tails.py      --game MODWAR22
py contrib\measure_mwii_shared_tails_alias.py --game MODWAR22
py contrib\mwii_shared_tail_plan.py --two-column --write-plan plans/mwii_shared.txt
py contrib\mwii_alias_grid_plan.py --harvest MODWAR22,YAMYAMOK,BLACKOP6,BLACKOP7,MODWAR7 --write-plan plans/mwii_alias_xgame.txt
bin\windows\confirm_plan.exe plans\mwii_alias_xgame.txt --game MODWAR22 --size
bin\windows\confirm_plan.exe plans\mwii_alias_xgame.txt --game MODWAR22
bin\windows\validate.exe --game MODWAR22 findings\modwar22\run_<stamp>_plan
```

`validate` is worth running on every batch and is cheap. On the first alias run it reported
*"every name re-derives: the hash matches the name, the game holds the id, and the asset type is one
the id is actually in"* for 2,121 names — an independent check on the hash policy, the output width
and the pool attribution, which are the three things that fail silently here.