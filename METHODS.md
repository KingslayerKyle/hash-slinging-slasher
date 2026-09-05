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
| 30 | family grid completion | `sound_alias` above all | `scripts/unnamed_profile.py --grid`, `contrib/family_grid.py` -> `confirm_list` | **23 on Black Ops 4, and `derive_closure` turned those into 102 more.** Rank families by tails shared across more than one axis value, not by raw product: `i_` looks like 158 M cells and collapses to 694 K under that, because it is not a grid, it is every name beginning `i_` |
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
| sound final byte solved backwards | 1 | 1 | 7 | 7 | 1 | 1 | 1 | 2026-08-31 | 2026-08-31 | untried |
| richkiller bo4 decoded texture ledger | 1 | 1 | 7,488 | 22,210 | 2 | 2 | 2 | 2026-09-04 | 2026-09-04 | untried |
| black ops 4 source literals | 1 | 1 | 546 | 23,249 | 42 | 42 | 42 | 2026-08-26 | 2026-08-26 | untried |
| sound alias two byte solve | 1 | 1 | 5 | 521 | 104 | 104 | 104 | 2026-09-02 | 2026-09-02 | untried |
| cold war source literals | 1 | 1 | 251 | 35,278 | 140 | 140 | 140 | 2026-08-26 | 2026-08-26 | untried |
| build strings, lpc fast files | 1 | 1 | 7 | 2,135 | 305 | 305 | 305 | 2026-08-24 | 2026-08-24 | untried |
| build strings, casc blte 0.5gb probe | 1 | 1 | 10 | 3,637 | 363 | 363 | 363 | 2026-08-24 | 2026-08-24 | untried |
| weapon anim grid | 1 | 2 | 77 | 46,426 | 602 | 446 | 927 | 2026-09-03 | 2026-09-03 | live |
| black market character spray tag images | 1 | 1 | 10 | 8,316 | 831 | 831 | 831 | 2026-09-04 | 2026-09-04 | untried |
| final byte solved backwards | 1 | 128 | 3,132 | 2,776,961 | 886 | 18 | 6,784 | 2026-08-22 | 2026-09-04 | spent |
| gaps | 2 | 5 | 376 | 346,722 | 922 | 190 | 50,180 | 2026-08-20 | 2026-08-27 | spent |
| figglefx bo4 verified general exports | 1 | 1 | 134 | 159,569 | 1,190 | 1,190 | 1,190 | 2026-09-04 | 2026-09-04 | untried |
| reverse final-byte solve after source refresh | 1 | 1 | 3 | 4,051 | 1,350 | 1,350 | 1,350 | 2026-09-03 | 2026-09-03 | untried |
| two byte pool solve | 1 | 1 | 2 | 3,124 | 1,562 | 1,562 | 1,562 | 2026-09-04 | 2026-09-04 | untried |
| hashindex bo4 bocw global and script labels | 1 | 1 | 160 | 352,925 | 2,205 | 2,205 | 2,205 | 2026-09-04 | 2026-09-04 | untried |
| final-byte-after-xanim-seed | 1 | 1 | 16 | 35,919 | 2,244 | 2,244 | 2,244 | 2026-08-29 | 2026-08-29 | untried |
| black ops 4 final byte after upstream corpus refresh | 1 | 1 | 1 | 2,267 | 2,267 | 2,267 | 2,267 | 2026-09-01 | 2026-09-01 | untried |
| final-byte after current findings | 1 | 1 | 5 | 11,775 | 2,355 | 2,355 | 2,355 | 2026-09-01 | 2026-09-01 | untried |
| black ops 1 build names, verbatim | 1 | 2 | 271 | 651,912 | 2,405 | 1,940 | 3,164 | 2026-08-22 | 2026-08-22 | live |
| black ops 3 build names, respelled, full harvest | 1 | 2 | 148 | 473,642 | 3,200 | 1,691 | 29,602 | 2026-08-22 | 2026-08-22 | spent |
| anim symmetry | 2 | 2 | 5 | 18,464 | 3,692 | 3,098 | 3,098 | 2026-09-03 | 2026-09-04 | live |
| early black ops 4 source literals | 1 | 1 | 4 | 16,198 | 4,049 | 4,049 | 4,049 | 2026-08-26 | 2026-08-26 | untried |
| animation symmetry | 1 | 1 | 2 | 9,297 | 4,648 | 4,648 | 4,648 | 2026-09-04 | 2026-09-04 | untried |
| build strings, casc archives | 1 | 4 | 139 | 659,480 | 4,744 | 1,316 | 273,138 | 2026-08-24 | 2026-08-24 | spent |
| black market loot stream, itemshop, and contract icons | 1 | 1 | 7 | 43,712 | 6,244 | 6,244 | 6,244 | 2026-09-04 | 2026-09-04 | untried |
| anim game cross | 1 | 1 | 4 | 26,532 | 6,633 | 6,633 | 6,633 | 2026-09-03 | 2026-09-03 | untried |
| final byte closure, guard cleared | 1 | 1 | 2 | 15,218 | 7,609 | 7,609 | 7,609 | 2026-08-25 | 2026-08-25 | untried |
| image siblings | 3 | 5 | 529 | 4,621,863 | 8,736 | 1,734 | 68,329 | 2026-08-20 | 2026-08-21 | spent |
| early cold war source literals | 1 | 1 | 3 | 26,471 | 8,823 | 8,823 | 8,823 | 2026-08-26 | 2026-08-26 | untried |
| channels | 2 | 4 | 916 | 9,598,953 | 10,479 | 2,732 | 602,442 | 2026-08-20 | 2026-08-20 | spent |
| family gap filling | 1 | 63 | 528 | 6,272,341 | 11,879 | 654 | 3,142 | 2026-08-19 | 2026-09-04 | cooling |
| paired-token-blocks-anim | 1 | 1 | 33 | 410,321 | 12,433 | 12,433 | 12,433 | 2026-08-20 | 2026-08-20 | untried |
| black ops 3 build names, verbatim, full harvest | 1 | 2 | 177 | 2,462,622 | 13,913 | 8,858 | 32,402 | 2026-08-22 | 2026-08-22 | cooling |
| cold war source filenames and text | 1 | 1 | 151 | 2,102,012 | 13,920 | 13,920 | 13,920 | 2026-08-27 | 2026-08-27 | untried |
| \ bo4 image siblings from confirmed materials 20260830\ | 1 | 1 | 135 | 2,163,297 | 16,024 | 16,024 | 16,024 | 2026-08-30 | 2026-08-30 | untried |
| alias slot substitution | 4 | 9 | 1,354 | 21,780,323 | 16,085 | 6,535 | 2,047,927 | 2026-08-20 | 2026-08-21 | spent |
| rare-token-compound-splice-anim | 1 | 3 | 30 | 521,194 | 17,373 | 10,849 | 17,385 | 2026-08-20 | 2026-08-20 | live |
| black ops 4 final-byte solve after refreshed tables | 1 | 2 | 2 | 35,304 | 17,652 | 17,652 | 17,652 | 2026-08-27 | 2026-08-27 | live |
| black ops 3 build names, verbatim | 1 | 1 | 4 | 73,303 | 18,325 | 18,325 | 18,325 | 2026-08-22 | 2026-08-22 | untried |
| \ bo4 final-byte after upstream corpus refresh\ | 1 | 1 | 1 | 19,466 | 19,466 | 19,466 | 19,466 | 2026-08-29 | 2026-08-29 | untried |
| bo3 mod tools asset file list | 1 | 1 | 3 | 65,355 | 21,785 | 21,785 | 21,785 | 2026-08-22 | 2026-08-22 | untried |
| rare shared-token splices | 1 | 2 | 7 | 158,622 | 22,660 | 13,212 | 79,348 | 2026-08-28 | 2026-08-29 | cooling |
| external sound paths with one directory dropped | 1 | 1 | 1 | 23,776 | 23,776 | 23,776 | 23,776 | 2026-09-04 | 2026-09-04 | untried |
| reversible endpoint token swaps | 1 | 1 | 2 | 49,872 | 24,936 | 24,936 | 24,936 | 2026-09-04 | 2026-09-04 | untried |
| bo3 mod tools gdt asset names | 1 | 2 | 3 | 84,078 | 28,026 | 21,019 | 42,039 | 2026-08-22 | 2026-08-22 | live |
| rare shared-token splices family size 13-30 | 1 | 1 | 10 | 325,039 | 32,503 | 32,503 | 32,503 | 2026-08-28 | 2026-08-28 | untried |
| black ops 4 family gap filling after refreshed corpus | 1 | 2 | 6 | 200,472 | 33,412 | 33,412 | 33,412 | 2026-08-27 | 2026-08-27 | live |
| paired-token-blocks-alias-deterministic | 1 | 2 | 14 | 481,544 | 34,396 | 24,067 | 60,216 | 2026-08-20 | 2026-08-20 | live |
| paired-token-blocks-anim-deterministic | 1 | 9 | 104 | 3,708,652 | 35,660 | 15,884 | 206,784 | 2026-08-20 | 2026-08-20 | spent |
| final-byte-after-image-channel-seed | 1 | 1 | 1 | 36,014 | 36,014 | 36,014 | 36,014 | 2026-08-29 | 2026-08-29 | untried |
| \ cw final-byte after upstream corpus refresh\ | 1 | 1 | 1 | 37,273 | 37,273 | 37,273 | 37,273 | 2026-08-29 | 2026-08-29 | untried |
| numbered families on two axes | 1 | 2 | 7 | 265,407 | 37,915 | 22,119 | 22,119 | 2026-08-27 | 2026-08-27 | live |
| external source filenames | 1 | 1 | 28 | 1,226,186 | 43,792 | 43,792 | 43,792 | 2026-08-27 | 2026-08-27 | untried |
| image siblings of confirmed materials | 1 | 145 | 6,111 | 279,684,144 | 45,767 | 393 | 2,396,685 | 2026-08-19 | 2026-09-04 | spent |
| image interior counterparts after richkiller | 1 | 1 | 18 | 904,787 | 50,265 | 50,265 | 50,265 | 2026-09-04 | 2026-09-04 | untried |
| \ cold war rare shared-token splice family 2401-2700 xanim\ | 1 | 1 | 8 | 409,075 | 51,134 | 51,134 | 51,134 | 2026-08-28 | 2026-08-28 | untried |
| continuations | 1 | 1 | 776 | 39,892,300 | 51,407 | 51,407 | 51,407 | 2026-08-20 | 2026-08-20 | untried |
| older-title vocabulary | 1 | 2 | 59 | 3,144,542 | 53,297 | 34,939 | 112,305 | 2026-08-21 | 2026-08-21 | cooling |
| image siblings from confirmed materials current | 1 | 1 | 43 | 2,307,057 | 53,652 | 53,652 | 53,652 | 2026-09-01 | 2026-09-01 | untried |
| black ops 3 build names, respelled | 1 | 1 | 1 | 54,358 | 54,358 | 54,358 | 54,358 | 2026-08-22 | 2026-08-22 | untried |
| alias slot substitution, left context only | 3 | 6 | 1,934 | 109,332,515 | 56,531 | 8,885 | 2,932,361 | 2026-08-20 | 2026-08-20 | spent |
| image siblings from confirmed materials | 1 | 1 | 35 | 2,001,561 | 57,187 | 57,187 | 57,187 | 2026-08-26 | 2026-08-26 | untried |
| cod-ultimate source literals | 1 | 2 | 12 | 686,330 | 57,194 | 49,023 | 49,023 | 2026-08-31 | 2026-08-31 | live |
| image siblings of richkiller-derived materials | 1 | 1 | 39 | 2,396,589 | 61,451 | 61,451 | 61,451 | 2026-09-04 | 2026-09-04 | untried |
| edits anim | 2 | 5 | 208 | 12,868,629 | 61,868 | 15,318 | 15,318 | 2026-08-20 | 2026-08-20 | live |
| cold war animation token edits after new findings | 2 | 2 | 93 | 5,989,742 | 64,405 | 32,080 | 3,038,360 | 2026-08-26 | 2026-08-31 | spent |
| adjacent-token-order-anim | 1 | 1 | 2 | 136,243 | 68,121 | 68,121 | 68,121 | 2026-08-20 | 2026-08-20 | untried |
| rare compound material splice | 1 | 1 | 3 | 208,316 | 69,438 | 69,438 | 69,438 | 2026-09-04 | 2026-09-04 | untried |
| rare shared-token splices family size 31-60 | 1 | 2 | 23 | 1,691,810 | 73,556 | 42,295 | 42,295 | 2026-08-28 | 2026-08-28 | live |
| paired-token-blocks-anim-lengths2-5-rare | 1 | 5 | 72 | 5,466,329 | 75,921 | 34,115 | 547,307 | 2026-08-20 | 2026-08-20 | spent |
| bo3 mod tools asset names | 1 | 2 | 22 | 1,735,532 | 78,887 | 78,887 | 78,887 | 2026-08-24 | 2026-08-24 | live |
| rare-token-compound-splice-model | 1 | 2 | 60 | 5,611,060 | 93,517 | 80,164 | 80,164 | 2026-08-20 | 2026-08-20 | live |
| family grid current | 1 | 1 | 38 | 3,786,603 | 99,647 | 99,647 | 99,647 | 2026-08-31 | 2026-08-31 | untried |
| \ cw sound-alias token insertion and deletion 20260830\ | 1 | 1 | 70 | 7,641,905 | 109,170 | 109,170 | 109,170 | 2026-08-30 | 2026-08-30 | untried |
| rare shared token splice 13 30 current | 1 | 1 | 3 | 331,149 | 110,383 | 110,383 | 110,383 | 2026-09-02 | 2026-09-02 | untried |
| rare-token-compound-splice-batch | 1 | 4 | 236 | 26,219,346 | 111,098 | 48,548 | 3,278,056 | 2026-08-20 | 2026-08-20 | spent |
| sound language and encoding variants | 1 | 1 | 38 | 4,296,303 | 113,060 | 113,060 | 113,060 | 2026-08-20 | 2026-08-20 | untried |
| cold war two-token suffix precedents current | 1 | 1 | 1 | 124,990 | 124,990 | 124,990 | 124,990 | 2026-09-03 | 2026-09-03 | untried |
| rare shared-token splices family size 61-120 | 1 | 1 | 18 | 2,355,489 | 130,860 | 130,860 | 130,860 | 2026-08-28 | 2026-08-28 | untried |
| figglefx cold war community export | 1 | 1 | 1 | 132,659 | 132,659 | 132,659 | 132,659 | 2026-09-04 | 2026-09-04 | untried |
| alias slot substitution, right context only | 1 | 2 | 146 | 22,349,656 | 153,079 | 121,544 | 121,544 | 2026-08-20 | 2026-08-20 | live |
| rare shared-token splices families 18901-19200 | 1 | 1 | 20 | 3,237,958 | 161,897 | 161,897 | 161,897 | 2026-08-29 | 2026-08-29 | untried |
| vox speaker x line grid, unseen cells | 1 | 1 | 34 | 5,564,535 | 163,662 | 163,662 | 163,662 | 2026-08-23 | 2026-08-23 | untried |
| image siblings after suffix | 1 | 1 | 14 | 2,307,537 | 164,824 | 164,824 | 164,824 | 2026-09-02 | 2026-09-02 | untried |
| correlated-token-blocks-alias-wide | 1 | 2 | 7 | 1,175,308 | 167,901 | 146,934 | 146,934 | 2026-08-20 | 2026-08-20 | live |
| cold war image siblings from current confirmed materials | 1 | 1 | 13 | 2,281,761 | 175,520 | 175,520 | 175,520 | 2026-09-01 | 2026-09-01 | untried |
| adjacent-token-order-model | 1 | 2 | 10 | 1,765,338 | 176,533 | 110,332 | 441,340 | 2026-08-20 | 2026-08-20 | cooling |
| family grid completion, shared tails only | 1 | 1 | 23 | 4,076,970 | 177,259 | 177,259 | 177,259 | 2026-08-24 | 2026-08-24 | untried |
| image siblings closure followup | 1 | 1 | 13 | 2,309,889 | 177,683 | 177,683 | 177,683 | 2026-09-02 | 2026-09-02 | untried |
| image channel completion | 1 | 115 | 1,603 | 290,175,523 | 181,020 | 5,159 | 654,189 | 2026-08-20 | 2026-09-04 | spent |
| rare shared-token splices family sizes 10201-10500 | 1 | 1 | 14 | 2,725,854 | 194,703 | 194,703 | 194,703 | 2026-08-28 | 2026-08-28 | untried |
| modern warfare 2 build names, verbatim | 1 | 1 | 1 | 209,784 | 209,784 | 209,784 | 209,784 | 2026-08-22 | 2026-08-22 | untried |
| rare compound image splice | 1 | 1 | 1 | 223,738 | 223,738 | 223,738 | 223,738 | 2026-09-04 | 2026-09-04 | untried |
| cross-game verbatim transfer | 1 | 1 | 3 | 702,081 | 234,027 | 234,027 | 234,027 | 2026-08-25 | 2026-08-25 | untried |
| token edits anim | 1 | 1 | 13 | 3,067,026 | 235,925 | 235,925 | 235,925 | 2026-09-03 | 2026-09-03 | untried |
| mcdp material redecorations after pr971 | 1 | 1 | 5 | 1,198,438 | 239,687 | 239,687 | 239,687 | 2026-08-27 | 2026-08-27 | untried |
| refreshed mcdp material core redecorations | 1 | 1 | 5 | 1,198,717 | 239,743 | 239,743 | 239,743 | 2026-08-28 | 2026-08-28 | untried |
| speaker grids re-run cw | 1 | 1 | 6 | 1,466,925 | 244,487 | 244,487 | 244,487 | 2026-08-24 | 2026-08-24 | untried |
| an unnamed method | 1 | 13 | 279 | 73,702,110 | 264,165 | 1 | 46,049 | 2026-09-02 | 2026-09-04 | spent |
| paired-token-blocks-model-deterministic | 1 | 6 | 148 | 39,959,454 | 269,996 | 96,527 | 475,923 | 2026-08-20 | 2026-08-20 | cooling |
| mined substitution equivalence classes | 1 | 2 | 211 | 58,068,971 | 275,208 | 151,043 | 1,529,932 | 2026-08-25 | 2026-08-25 | spent |
| token-insertion-deletion-alias | 1 | 2 | 28 | 7,924,449 | 283,016 | 233,070 | 233,070 | 2026-08-20 | 2026-08-20 | live |
| corpus-mined substitutions, top 1500 | 1 | 2 | 371 | 105,553,541 | 284,510 | 178,297 | 703,699 | 2026-08-25 | 2026-08-25 | cooling |
| adjacent-token-order-batch | 1 | 2 | 26 | 7,517,953 | 289,152 | 250,599 | 250,599 | 2026-08-20 | 2026-08-20 | live |
| per-prefix continuations | 3 | 4 | 538 | 159,447,283 | 296,370 | 79,618 | 1,430,530 | 2026-08-19 | 2026-08-21 | spent |
| image siblings bo4 | 1 | 1 | 6 | 1,879,167 | 313,194 | 313,194 | 313,194 | 2026-08-26 | 2026-08-26 | untried |
| rare shared-token splices family size 241-480 | 1 | 2 | 89 | 28,268,386 | 317,622 | 224,352 | 543,622 | 2026-08-28 | 2026-08-28 | live |
| token insertion and deletion | 5 | 20 | 1,160 | 380,455,078 | 327,978 | 34,598 | 6,143,127 | 2026-08-20 | 2026-08-23 | spent |
| animation token insertion and deletion after pr983 | 1 | 1 | 9 | 2,961,267 | 329,029 | 329,029 | 329,029 | 2026-08-27 | 2026-08-27 | untried |
| deep image channel completion after pr977 | 1 | 1 | 11 | 3,767,092 | 342,462 | 342,462 | 342,462 | 2026-08-27 | 2026-08-27 | untried |
| sound-alias context length completion | 1 | 1 | 1 | 353,063 | 353,063 | 353,063 | 353,063 | 2026-09-04 | 2026-09-04 | untried |
| external bo4-source core respelling | 1 | 2 | 9 | 3,192,200 | 354,688 | 319,220 | 319,220 | 2026-08-28 | 2026-08-28 | live |
| deep image channel completion after pr979 | 1 | 1 | 10 | 3,766,987 | 376,698 | 376,698 | 376,698 | 2026-08-27 | 2026-08-27 | untried |
| \ refreshed mcdp material core redecorations\ | 1 | 1 | 3 | 1,199,830 | 399,943 | 399,943 | 399,943 | 2026-08-29 | 2026-08-29 | untried |
| rare shared-token splices family size 121-240 | 1 | 2 | 29 | 12,188,574 | 420,295 | 320,751 | 320,751 | 2026-08-28 | 2026-08-28 | live |
| cross-game sound stem transfer | 1 | 1 | 27 | 11,737,632 | 434,727 | 434,727 | 434,727 | 2026-08-20 | 2026-08-20 | untried |
| materials from image cores | 1 | 115 | 1,242 | 548,550,336 | 441,666 | 9,045 | 5,012,736 | 2026-08-20 | 2026-09-04 | spent |
| incremented basename digits | 1 | 1 | 2 | 887,360 | 443,680 | 443,680 | 443,680 | 2026-09-04 | 2026-09-04 | untried |
| shared-tail family grid follow-up | 1 | 1 | 8 | 3,578,096 | 447,262 | 447,262 | 447,262 | 2026-08-26 | 2026-08-26 | untried |
| rare shared-token splices families 13801-14100 | 1 | 2 | 15 | 7,293,903 | 486,260 | 260,496 | 260,496 | 2026-08-28 | 2026-08-28 | live |
| slotswap | 3 | 6 | 1,903 | 928,681,787 | 488,009 | 183,556 | 5,712,231 | 2026-08-20 | 2026-09-03 | spent |
| black ops 4 materials from image cores current | 1 | 1 | 9 | 4,838,880 | 537,653 | 537,653 | 537,653 | 2026-09-01 | 2026-09-01 | untried |
| mined substitutions, ranking tail | 1 | 1 | 237 | 129,160,520 | 544,981 | 544,981 | 544,981 | 2026-08-25 | 2026-08-25 | untried |
| token edits material after pr828 | 1 | 1 | 4 | 2,186,916 | 546,729 | 546,729 | 546,729 | 2026-08-26 | 2026-08-26 | untried |
| cold war legacy multi-axis numbered grids | 1 | 1 | 7 | 3,858,203 | 551,171 | 551,171 | 551,171 | 2026-08-29 | 2026-08-29 | untried |
| rare shared-token splices family size 481-960 | 1 | 2 | 128 | 73,051,283 | 570,713 | 314,886 | 314,886 | 2026-08-28 | 2026-08-28 | live |
| cold war same-directory outer-inner cross | 1 | 3 | 9 | 5,196,762 | 577,418 | 577,418 | 577,418 | 2026-08-27 | 2026-08-27 | live |
| final byte substitution | 1 | 2 | 121 | 70,135,764 | 579,634 | 467,581 | 467,581 | 2026-08-22 | 2026-08-22 | live |
| \ cw adjacent material token order 20260830\ | 1 | 1 | 4 | 2,374,577 | 593,644 | 593,644 | 593,644 | 2026-08-30 | 2026-08-30 | untried |
| rare shared token splice 61 120 current | 1 | 2 | 8 | 4,761,390 | 595,173 | 396,782 | 396,782 | 2026-09-02 | 2026-09-02 | live |
| locally evidenced adjacent token order | 1 | 1 | 2 | 1,205,866 | 602,933 | 602,933 | 602,933 | 2026-08-26 | 2026-08-26 | untried |
| cold war same-directory token graft | 1 | 2 | 10 | 6,114,860 | 611,486 | 611,486 | 611,486 | 2026-08-27 | 2026-08-27 | live |
| rare shared token splice 481 960 current | 1 | 2 | 118 | 74,610,250 | 632,290 | 414,501 | 1,332,325 | 2026-09-02 | 2026-09-02 | cooling |
| templates | 3 | 5 | 395 | 265,290,228 | 671,620 | 286,113 | 3,386,404 | 2026-08-20 | 2026-09-03 | spent |
| high-control terminal token counterparts | 1 | 2 | 6 | 4,130,040 | 688,340 | 516,254 | 516,254 | 2026-09-04 | 2026-09-04 | live |
| mined classes over indel-augmented pairs | 1 | 2 | 75 | 55,459,097 | 739,454 | 396,848 | 8,962,006 | 2026-08-25 | 2026-08-25 | spent |
| correlated-token-blocks-material-image-wide | 1 | 6 | 563 | 425,162,272 | 755,172 | 270,359 | 5,907,185 | 2026-08-20 | 2026-08-20 | spent |
| corpus-mined substitutions | 7 | 38 | 1,354 | 1,042,097,492 | 769,643 | 25,953 | 1,289,462 | 2026-08-25 | 2026-09-02 | spent |
| rare shared-token splices family sizes 9901-10200 | 1 | 1 | 9 | 7,174,482 | 797,164 | 797,164 | 797,164 | 2026-08-28 | 2026-08-28 | untried |
| length-sorted interior tokens | 1 | 1 | 1 | 816,286 | 816,286 | 816,286 | 816,286 | 2026-08-27 | 2026-08-27 | untried |
| \ bo4 sound-alias token insertion and deletion 20260830\ | 1 | 1 | 9 | 7,647,725 | 849,747 | 849,747 | 849,747 | 2026-08-30 | 2026-08-30 | untried |
| rare shared token splice 31 60 current | 1 | 1 | 1 | 861,934 | 861,934 | 861,934 | 861,934 | 2026-09-02 | 2026-09-02 | untried |
| paired-token-blocks-model-lengths2-4 | 1 | 2 | 21 | 18,272,811 | 870,133 | 702,844 | 702,844 | 2026-08-20 | 2026-08-20 | live |
| last-three token rotation | 1 | 2 | 2 | 1,746,976 | 873,488 | 873,488 | 873,488 | 2026-08-27 | 2026-08-27 | live |
| complemented basename digits | 1 | 1 | 1 | 887,359 | 887,359 | 887,359 | 887,359 | 2026-09-04 | 2026-09-04 | untried |
| family grid completion | 1 | 1 | 4 | 3,639,611 | 909,902 | 909,902 | 909,902 | 2026-08-27 | 2026-08-27 | untried |
| \ sound-alias positional token substitutions\ | 1 | 2 | 8 | 7,395,792 | 924,474 | 528,252 | 3,698,022 | 2026-08-30 | 2026-08-30 | cooling |
| zigzag basename token recombination | 1 | 1 | 1 | 939,211 | 939,211 | 939,211 | 939,211 | 2026-08-27 | 2026-08-27 | untried |
| zigzag basename tokens | 1 | 2 | 2 | 1,878,438 | 939,219 | 939,219 | 939,219 | 2026-08-27 | 2026-08-27 | live |
| cold war material token edits after new findings | 2 | 3 | 101 | 98,466,866 | 974,919 | 360,669 | 5,500,996 | 2026-08-26 | 2026-08-31 | spent |
| animation token insertion and deletion after pr986 | 1 | 1 | 3 | 2,962,200 | 987,400 | 987,400 | 987,400 | 2026-08-27 | 2026-08-27 | untried |
| \ cold war animation token edits refreshed 20260830\ | 1 | 1 | 3 | 2,995,208 | 998,402 | 998,402 | 998,402 | 2026-08-29 | 2026-08-29 | untried |
| rare shared-token splices family size 961-1200 | 1 | 2 | 33 | 34,762,466 | 1,053,408 | 1,022,406 | 1,086,347 | 2026-08-28 | 2026-08-28 | live |
| edits material | 2 | 5 | 139 | 150,302,473 | 1,081,312 | 439,383 | 1,589,712 | 2026-08-20 | 2026-08-20 | cooling |
| cold war corpus-mined substitutions rank 401-500 | 1 | 2 | 6 | 6,492,678 | 1,082,113 | 1,082,113 | 1,082,113 | 2026-08-27 | 2026-08-27 | live |
| rare shared token splice 1921 3840 current | 1 | 2 | 261 | 290,452,894 | 1,112,846 | 580,905 | 13,202,404 | 2026-09-02 | 2026-09-02 | spent |
| cold war adjacent material token order | 1 | 1 | 2 | 2,403,554 | 1,201,777 | 1,201,777 | 1,201,777 | 2026-09-03 | 2026-09-03 | untried |
| \ bo4 adjacent xmodel token order 20260830\ | 1 | 1 | 1 | 1,238,704 | 1,238,704 | 1,238,704 | 1,238,704 | 2026-08-30 | 2026-08-30 | untried |
| sibling token substitution, right context only | 1 | 1 | 369 | 461,529,482 | 1,250,757 | 1,250,757 | 1,250,757 | 2026-08-19 | 2026-08-19 | untried |
| rare shared token splice 121 240 current | 1 | 1 | 5 | 6,312,219 | 1,262,443 | 1,262,443 | 1,262,443 | 2026-09-02 | 2026-09-02 | untried |
| token edits material current | 1 | 2 | 48 | 65,328,704 | 1,361,014 | 759,636 | 759,636 | 2026-08-29 | 2026-08-29 | live |
| sound alias slot substitution | 1 | 2 | 3 | 4,119,600 | 1,373,200 | 1,028,660 | 2,062,280 | 2026-08-21 | 2026-08-22 | live |
| sibling token substitution | 6 | 13 | 2,719 | 3,893,091,224 | 1,431,809 | 206,904 | 153,883,448 | 2026-08-19 | 2026-09-02 | spent |
| token edits model cap30 | 1 | 1 | 21 | 31,607,140 | 1,505,101 | 1,505,101 | 1,505,101 | 2026-09-03 | 2026-09-03 | untried |
| refreshed token insertion/deletion | 1 | 1 | 9 | 13,694,727 | 1,521,636 | 1,521,636 | 1,521,636 | 2026-08-27 | 2026-08-27 | untried |
| animation token insertion and deletion | 1 | 1 | 2 | 3,043,656 | 1,521,828 | 1,521,828 | 1,521,828 | 2026-09-02 | 2026-09-02 | untried |
| token edits material after new findings | 1 | 1 | 21 | 32,170,813 | 1,531,943 | 1,531,943 | 1,531,943 | 2026-08-25 | 2026-08-25 | untried |
| precedents top50 | 1 | 1 | 40 | 61,822,767 | 1,545,569 | 1,545,569 | 1,545,569 | 2026-09-02 | 2026-09-02 | untried |
| material cores spelled as image | 5 | 13 | 1,006 | 1,578,450,625 | 1,569,036 | 289,958 | 42,125,208 | 2026-08-25 | 2026-09-03 | spent |
| \ bo4 material token edits cap20 minseen4 20260830\ | 1 | 1 | 34 | 53,634,909 | 1,577,497 | 1,577,497 | 1,577,497 | 2026-08-29 | 2026-08-29 | untried |
| \ cold war rare shared-token splice family 3601-3900 material\ | 1 | 1 | 3 | 4,744,802 | 1,581,600 | 1,581,600 | 1,581,600 | 2026-08-28 | 2026-08-28 | untried |
| precedents top10 | 2 | 2 | 19 | 31,423,294 | 1,653,857 | 1,122,260 | 1,122,260 | 2026-09-02 | 2026-09-02 | live |
| material token edits after new findings | 1 | 2 | 38 | 64,915,906 | 1,708,313 | 1,708,313 | 1,708,313 | 2026-08-26 | 2026-08-26 | live |
| \ bo4 rare shared-token splice family 2701-3000 material\ | 1 | 1 | 5 | 8,580,314 | 1,716,062 | 1,716,062 | 1,716,062 | 2026-08-28 | 2026-08-28 | untried |
| same-directory outer/interior cross 20260827 | 1 | 1 | 1 | 1,732,344 | 1,732,344 | 1,732,344 | 1,732,344 | 2026-08-27 | 2026-08-27 | untried |
| rare shared-token splices family sizes 7501-7800 | 1 | 1 | 2 | 3,574,174 | 1,787,087 | 1,787,087 | 1,787,087 | 2026-08-28 | 2026-08-28 | untried |
| deep image channel completion after pr980 | 1 | 1 | 2 | 3,767,176 | 1,883,588 | 1,883,588 | 1,883,588 | 2026-08-27 | 2026-08-27 | untried |
| deep image channel closure after new seed | 1 | 1 | 2 | 3,790,183 | 1,895,091 | 1,895,091 | 1,895,091 | 2026-08-29 | 2026-08-29 | untried |
| mcdp | 1 | 1 | 2,846 | 5,545,804,740 | 1,948,631 | 1,948,631 | 1,948,631 | 2026-08-23 | 2026-08-23 | untried |
| deep image channel completion after richkiller ledger | 1 | 1 | 2 | 3,906,974 | 1,953,487 | 1,953,487 | 1,953,487 | 2026-09-04 | 2026-09-04 | untried |
| mined indels, anchored | 1 | 2 | 116 | 226,836,463 | 1,955,486 | 1,435,681 | 3,065,341 | 2026-08-25 | 2026-08-25 | live |
| rare shared-token splices family sizes 11101-11400 | 1 | 1 | 4 | 7,916,087 | 1,979,021 | 1,979,021 | 1,979,021 | 2026-08-28 | 2026-08-28 | untried |
| rare shared-token splices families 21601-21900 | 1 | 1 | 1 | 1,980,622 | 1,980,622 | 1,980,622 | 1,980,622 | 2026-08-29 | 2026-08-29 | untried |
| sound character substitution | 1 | 1 | 490 | 983,467,758 | 2,007,077 | 2,007,077 | 2,007,077 | 2026-08-24 | 2026-08-24 | untried |
| rare shared-token splices family sizes 6601-6900 | 1 | 2 | 13 | 26,110,812 | 2,008,524 | 1,450,600 | 1,450,600 | 2026-08-28 | 2026-08-28 | live |
| family grid, shared tails, cold war | 1 | 1 | 2 | 4,076,947 | 2,038,473 | 2,038,473 | 2,038,473 | 2026-08-24 | 2026-08-24 | untried |
| family column cross product | 3 | 9 | 349 | 711,519,426 | 2,038,737 | 456,163 | 54,076,619 | 2026-08-19 | 2026-09-02 | spent |
| rare shared splice 121 240 cw 20260903 | 1 | 1 | 3 | 6,315,365 | 2,105,121 | 2,105,121 | 2,105,121 | 2026-09-03 | 2026-09-03 | untried |
| corpus-mined substitutions, top 200 | 1 | 5 | 30 | 63,659,860 | 2,121,995 | 1,273,098 | 3,183,216 | 2026-08-27 | 2026-08-27 | live |
| rare shared-token splices family size 1501-1800 | 1 | 2 | 18 | 38,218,845 | 2,123,269 | 1,194,361 | 1,194,361 | 2026-08-28 | 2026-08-28 | live |
| family grid next families | 1 | 1 | 2 | 4,259,269 | 2,129,634 | 2,129,634 | 2,129,634 | 2026-08-31 | 2026-08-31 | untried |
| \ cw image siblings after bo4 gain 20260830\ | 1 | 1 | 1 | 2,163,297 | 2,163,297 | 2,163,297 | 2,163,297 | 2026-08-30 | 2026-08-30 | untried |
| material token insertion and deletion after pr982 | 1 | 1 | 15 | 32,495,105 | 2,166,340 | 2,166,340 | 2,166,340 | 2026-08-27 | 2026-08-27 | untried |
| rare shared-token splices families 15001-15300 | 1 | 1 | 1 | 2,199,697 | 2,199,697 | 2,199,697 | 2,199,697 | 2026-08-28 | 2026-08-28 | untried |
| \ cold war material token edits cap30 minseen3 20260830\ | 1 | 1 | 36 | 79,633,756 | 2,212,048 | 2,212,048 | 2,212,048 | 2026-08-29 | 2026-08-29 | untried |
| precedents top70 | 1 | 1 | 36 | 81,027,780 | 2,250,771 | 2,250,771 | 2,250,771 | 2026-09-02 | 2026-09-02 | untried |
| sibling token substitution, left context only | 2 | 3 | 1,401 | 3,216,420,428 | 2,295,803 | 769,926 | 3,368,815 | 2026-08-19 | 2026-08-20 | cooling |
| \ cold war material token edits cap20 minseen4 20260830\ | 1 | 1 | 23 | 53,630,368 | 2,331,755 | 2,331,755 | 2,331,755 | 2026-08-29 | 2026-08-29 | untried |
| \ bo4 adjacent material token order 20260830\ | 1 | 1 | 1 | 2,374,563 | 2,374,563 | 2,374,563 | 2,374,563 | 2026-08-30 | 2026-08-30 | untried |
| \ sound-alias two-token substitutions\ | 1 | 1 | 2 | 4,861,240 | 2,430,620 | 2,430,620 | 2,430,620 | 2026-08-30 | 2026-08-30 | untried |
| image channel completion, measured channel list | 1 | 2 | 36 | 88,257,624 | 2,451,600 | 2,451,600 | 2,451,600 | 2026-08-23 | 2026-08-23 | live |
| \ cold war rare shared-token splice family 2401-2700 image\ | 1 | 1 | 1 | 2,507,207 | 2,507,207 | 2,507,207 | 2,507,207 | 2026-08-28 | 2026-08-28 | untried |
| \ cw adjacent image token order 20260830\ | 1 | 1 | 1 | 2,509,437 | 2,509,437 | 2,509,437 | 2,509,437 | 2026-08-30 | 2026-08-30 | untried |
| token insertion and deletion material | 1 | 1 | 13 | 32,998,295 | 2,538,330 | 2,538,330 | 2,538,330 | 2026-08-31 | 2026-08-31 | untried |
| sound uncarried two-segment endings top 500 | 1 | 1 | 10 | 25,397,193 | 2,539,719 | 2,539,719 | 2,539,719 | 2026-08-26 | 2026-08-26 | untried |
| high-control terminal token counterparts after bo4 texture ledger | 1 | 1 | 2 | 5,190,062 | 2,595,031 | 2,595,031 | 2,595,031 | 2026-09-04 | 2026-09-04 | untried |
| xhash external core respelling | 1 | 2 | 15 | 39,142,720 | 2,609,514 | 2,446,420 | 2,446,420 | 2026-08-28 | 2026-08-28 | live |
| seeded sound-alias token edits | 1 | 1 | 2 | 5,339,594 | 2,669,797 | 2,669,797 | 2,669,797 | 2026-09-05 | 2026-09-05 | untried |
| interior token duplication | 1 | 2 | 4 | 10,737,038 | 2,684,259 | 2,684,259 | 2,684,259 | 2026-08-27 | 2026-08-27 | live |
| character deletion and transposition | 1 | 2 | 50 | 134,487,400 | 2,689,748 | 1,601,046 | 1,601,046 | 2026-08-24 | 2026-08-24 | live |
| model token insertion and deletion after pr987 | 1 | 1 | 5 | 13,695,779 | 2,739,155 | 2,739,155 | 2,739,155 | 2026-08-27 | 2026-08-27 | untried |
| \ cold war rare shared-token splice family 2401-2700 material\ | 1 | 1 | 3 | 8,787,217 | 2,929,072 | 2,929,072 | 2,929,072 | 2026-08-28 | 2026-08-28 | untried |
| \ cold war material token edits refreshed 20260830\ | 1 | 1 | 11 | 32,738,853 | 2,976,259 | 2,976,259 | 2,976,259 | 2026-08-29 | 2026-08-29 | untried |
| \ cold war rare shared-token splice family 3001-3300 material\ | 1 | 1 | 2 | 5,966,595 | 2,983,297 | 2,983,297 | 2,983,297 | 2026-08-28 | 2026-08-28 | untried |
| token order transpositions | 1 | 2 | 3 | 8,952,148 | 2,984,049 | 2,238,036 | 4,476,076 | 2026-08-24 | 2026-08-24 | live |
| token edits anim current | 1 | 2 | 2 | 6,031,597 | 3,015,798 | 2,980,123 | 3,051,474 | 2026-08-29 | 2026-09-02 | live |
| cold war animation token edits current | 1 | 1 | 1 | 3,041,844 | 3,041,844 | 3,041,844 | 3,041,844 | 2026-09-01 | 2026-09-01 | untried |
| rare shared-token splices family size 1201-1500 | 1 | 2 | 17 | 51,936,301 | 3,055,076 | 2,596,884 | 2,596,884 | 2026-08-28 | 2026-08-28 | live |
| \ cw same-directory sibling token graft\ | 1 | 1 | 1 | 3,063,893 | 3,063,893 | 3,063,893 | 3,063,893 | 2026-08-29 | 2026-08-29 | untried |
| family grid completion: head x axis x tail, unseen cells | 1 | 1 | 15 | 50,326,771 | 3,355,118 | 3,355,118 | 3,355,118 | 2026-08-23 | 2026-08-23 | untried |
| token edits anim cap30 | 1 | 2 | 4 | 13,523,498 | 3,380,874 | 3,380,865 | 3,380,883 | 2026-09-03 | 2026-09-03 | live |
| rare shared-token splices families 33901-34000 | 1 | 1 | 29 | 100,204,390 | 3,455,323 | 3,455,323 | 3,455,323 | 2026-08-29 | 2026-08-29 | untried |
| cold war amb sound family | 1 | 1 | 2 | 6,956,252 | 3,478,126 | 3,478,126 | 3,478,126 | 2026-08-30 | 2026-08-30 | untried |
| rare shared-token splices families 15901-16200 | 1 | 1 | 8 | 28,031,004 | 3,503,875 | 3,503,875 | 3,503,875 | 2026-08-28 | 2026-08-28 | untried |
| cold war image token edits | 2 | 2 | 18 | 64,416,665 | 3,578,703 | 2,662,730 | 5,410,649 | 2026-08-26 | 2026-08-31 | live |
| bounded family column cross product | 1 | 1 | 3 | 10,956,657 | 3,652,219 | 3,652,219 | 3,652,219 | 2026-08-27 | 2026-08-27 | untried |
| wide materials from images | 1 | 1 | 1 | 3,699,887 | 3,699,887 | 3,699,887 | 3,699,887 | 2026-09-02 | 2026-09-02 | untried |
| mined substitutions with left context | 1 | 1 | 29 | 108,352,260 | 3,736,284 | 3,736,284 | 3,736,284 | 2026-08-25 | 2026-08-25 | untried |
| token edits alias cap30 | 1 | 1 | 3 | 11,246,872 | 3,748,957 | 3,748,957 | 3,748,957 | 2026-09-03 | 2026-09-03 | untried |
| precedents top60 | 1 | 1 | 19 | 71,618,728 | 3,769,406 | 3,769,406 | 3,769,406 | 2026-09-02 | 2026-09-02 | untried |
| character substitution cw | 1 | 1 | 333 | 1,256,444,745 | 3,773,107 | 3,773,107 | 3,773,107 | 2026-08-24 | 2026-08-24 | untried |
| \ bo4 material token edits cap30 minseen3 20260830\ | 1 | 1 | 21 | 79,628,070 | 3,791,812 | 3,791,812 | 3,791,812 | 2026-08-29 | 2026-08-29 | untried |
| black ops 4 per-suffix precedents, five-token mirror | 1 | 2 | 159 | 603,737,878 | 3,797,093 | 2,251,087 | 12,083,685 | 2026-08-26 | 2026-08-26 | cooling |
| rare shared-token splices family sizes 5101-5400 | 1 | 2 | 6 | 22,972,418 | 3,828,736 | 2,871,552 | 2,871,552 | 2026-08-28 | 2026-08-28 | live |
| alias one token current | 1 | 1 | 1 | 3,881,516 | 3,881,516 | 3,881,516 | 3,881,516 | 2026-09-02 | 2026-09-02 | untried |
| sound-alias token substitutions | 1 | 1 | 1 | 3,935,920 | 3,935,920 | 3,935,920 | 3,935,920 | 2026-09-05 | 2026-09-05 | untried |
| \ bo4 rare shared-token splice family 3301-3600 material\ | 1 | 1 | 2 | 7,888,925 | 3,944,462 | 3,944,462 | 3,944,462 | 2026-08-28 | 2026-08-28 | untried |
| material token insertion and deletion after pr983 | 1 | 1 | 8 | 32,496,827 | 4,062,103 | 4,062,103 | 4,062,103 | 2026-08-27 | 2026-08-27 | untried |
| cold war sound stems, black ops 4 spelling | 1 | 1 | 3 | 12,257,370 | 4,085,790 | 4,085,790 | 4,085,790 | 2026-08-21 | 2026-08-21 | untried |
| per-suffix precedents, five-token mirror | 1 | 1 | 73 | 301,603,209 | 4,131,550 | 4,131,550 | 4,131,550 | 2026-08-26 | 2026-08-26 | untried |
| wide image siblings of confirmed materials | 1 | 3 | 88 | 364,446,747 | 4,141,440 | 2,190,637 | 8,819,755 | 2026-09-02 | 2026-09-04 | cooling |
| \ cold war rare shared-token splice family 2701-3000 material\ | 1 | 1 | 2 | 8,580,309 | 4,290,154 | 4,290,154 | 4,290,154 | 2026-08-28 | 2026-08-28 | untried |
| confirmed-only sound all-boundary cores, refreshed | 1 | 2 | 47 | 202,544,928 | 4,309,466 | 2,596,729 | 2,596,729 | 2026-08-29 | 2026-08-29 | live |
| edits model | 2 | 4 | 12 | 52,757,566 | 4,396,463 | 1,876,636 | 6,607,769 | 2026-08-20 | 2026-08-20 | cooling |
| rare shared-token splices families 12901-13200 | 1 | 2 | 6 | 27,286,700 | 4,547,783 | 3,410,837 | 3,410,837 | 2026-08-28 | 2026-08-28 | live |
| rare shared-token splices family sizes 6001-6300 | 1 | 2 | 3 | 14,089,319 | 4,696,439 | 3,522,329 | 3,522,329 | 2026-08-28 | 2026-08-28 | live |
| \ bo4 rare shared-token splice family 3601-3900 material\ | 1 | 1 | 1 | 4,744,803 | 4,744,803 | 4,744,803 | 4,744,803 | 2026-08-28 | 2026-08-28 | untried |
| token edits alias | 1 | 2 | 2 | 9,502,376 | 4,751,188 | 4,751,138 | 4,751,238 | 2026-09-03 | 2026-09-03 | live |
| rare shared-token splices family sizes 7201-7500 | 1 | 2 | 6 | 28,650,319 | 4,775,053 | 2,865,031 | 2,865,031 | 2026-08-28 | 2026-08-28 | live |
| cold war materials from image cores current | 1 | 1 | 1 | 4,838,880 | 4,838,880 | 4,838,880 | 4,838,880 | 2026-09-01 | 2026-09-01 | untried |
| materials from images after gain | 1 | 1 | 1 | 4,846,608 | 4,846,608 | 4,846,608 | 4,846,608 | 2026-09-02 | 2026-09-02 | untried |
| xmodel cores spelled as material | 4 | 9 | 110 | 551,720,250 | 5,015,638 | 1,297,902 | 49,307,187 | 2026-08-28 | 2026-09-03 | spent |
| precedents top40 | 1 | 1 | 10 | 51,576,111 | 5,157,611 | 5,157,611 | 5,157,611 | 2026-09-02 | 2026-09-02 | untried |
| rare shared-token splices family sizes 9001-9300 | 1 | 1 | 2 | 10,475,702 | 5,237,851 | 5,237,851 | 5,237,851 | 2026-08-28 | 2026-08-28 | untried |
| \ bo4 rare shared-token splice family 2401-2700 xmodel\ | 1 | 1 | 1 | 5,281,185 | 5,281,185 | 5,281,185 | 5,281,185 | 2026-08-28 | 2026-08-28 | untried |
| \ cold war material token edits cap40 minseen2 20260830\ | 1 | 1 | 20 | 105,800,678 | 5,290,033 | 5,290,033 | 5,290,033 | 2026-08-29 | 2026-08-29 | untried |
| token edits image after new findings | 1 | 1 | 6 | 31,740,887 | 5,290,147 | 5,290,147 | 5,290,147 | 2026-08-25 | 2026-08-25 | untried |
| rare shared-token splices family sizes 6901-7200 | 1 | 1 | 1 | 5,494,443 | 5,494,443 | 5,494,443 | 5,494,443 | 2026-08-28 | 2026-08-28 | untried |
| cold war material token edits current | 1 | 1 | 6 | 33,028,500 | 5,504,750 | 5,504,750 | 5,504,750 | 2026-09-01 | 2026-09-01 | untried |
| token edits material current bo4 20260903 | 1 | 1 | 6 | 33,095,322 | 5,515,887 | 5,515,887 | 5,515,887 | 2026-09-03 | 2026-09-03 | untried |
| corpus-mined substitutions, top 500 | 1 | 5 | 21 | 121,661,444 | 5,793,402 | 2,714,810 | 24,268,543 | 2026-08-27 | 2026-08-27 | cooling |
| rare shared-token splices family sizes 5401-5700 | 1 | 1 | 1 | 5,806,329 | 5,806,329 | 5,806,329 | 5,806,329 | 2026-08-28 | 2026-08-28 | untried |
| \ bo4 rare shared-token splice family 3001-3300 material\ | 1 | 1 | 1 | 5,966,596 | 5,966,596 | 5,966,596 | 5,966,596 | 2026-08-28 | 2026-08-28 | untried |
| corpus-mined substitutions, top 1000 | 1 | 4 | 24 | 145,853,160 | 6,077,215 | 4,050,931 | 18,234,083 | 2026-08-27 | 2026-08-27 | cooling |
| black ops 4 amb sound family | 1 | 1 | 1 | 6,962,026 | 6,962,026 | 6,962,026 | 6,962,026 | 2026-08-30 | 2026-08-30 | untried |
| rare shared-token splices family sizes 4501-4800 | 1 | 1 | 5 | 34,844,158 | 6,968,831 | 6,968,831 | 6,968,831 | 2026-08-28 | 2026-08-28 | untried |
| rare shared token splice 241 480 current | 1 | 2 | 4 | 28,939,012 | 7,234,753 | 4,823,168 | 14,469,506 | 2026-09-02 | 2026-09-02 | live |
| sab directory and basename recombination | 1 | 1 | 5 | 36,351,762 | 7,270,352 | 7,270,352 | 7,270,352 | 2026-08-21 | 2026-08-21 | untried |
| precedents top30 | 2 | 2 | 11 | 81,245,056 | 7,385,914 | 4,062,252 | 40,622,528 | 2026-09-02 | 2026-09-02 | cooling |
| rare shared-token splice families 481-960 | 1 | 1 | 5 | 37,321,382 | 7,464,276 | 7,464,276 | 7,464,276 | 2026-09-03 | 2026-09-03 | untried |
| rare shared token splice 961 1920 current | 1 | 2 | 19 | 142,465,412 | 7,498,179 | 7,123,270 | 7,914,745 | 2026-09-02 | 2026-09-02 | live |
| edits image | 2 | 3 | 12 | 91,292,882 | 7,607,740 | 5,048,388 | 30,538,103 | 2026-08-20 | 2026-08-20 | cooling |
| \ seeded sound-alias token edits\ | 1 | 1 | 1 | 7,651,395 | 7,651,395 | 7,651,395 | 7,651,395 | 2026-08-30 | 2026-08-30 | untried |
| sound character deletion and transposition | 1 | 2 | 13 | 101,307,572 | 7,792,890 | 4,221,125 | 50,654,061 | 2026-08-24 | 2026-08-24 | spent |
| \ cold war rare shared-token splice family 3301-3600 material\ | 1 | 1 | 1 | 7,888,923 | 7,888,923 | 7,888,923 | 7,888,923 | 2026-08-28 | 2026-08-28 | untried |
| black ops 4 image token edits | 1 | 1 | 4 | 32,464,572 | 8,116,143 | 8,116,143 | 8,116,143 | 2026-08-31 | 2026-08-31 | untried |
| \ bo4 material token edits cap40 minseen2 20260830\ | 1 | 1 | 13 | 105,807,354 | 8,139,027 | 8,139,027 | 8,139,027 | 2026-08-29 | 2026-08-29 | untried |
| \ bo4 material token edits refreshed 20260830\ | 1 | 1 | 4 | 32,739,897 | 8,184,974 | 8,184,974 | 8,184,974 | 2026-08-29 | 2026-08-29 | untried |
| black ops 4, uncarried two-segment endings | 1 | 1 | 1,468 | 12,179,260,896 | 8,296,499 | 8,296,499 | 8,296,499 | 2026-08-23 | 2026-08-23 | untried |
| rare shared-token splices family sizes 6301-6600 | 1 | 2 | 6 | 51,290,334 | 8,548,389 | 5,129,036 | 5,129,036 | 2026-08-28 | 2026-08-28 | live |
| \ cold war material token edits cap50 minseen2 20260830\ | 1 | 1 | 15 | 131,595,356 | 8,773,023 | 8,773,023 | 8,773,023 | 2026-08-30 | 2026-08-30 | untried |
| material token insertion and deletion | 1 | 2 | 7 | 66,040,581 | 9,434,368 | 8,255,060 | 11,006,779 | 2026-09-02 | 2026-09-02 | live |
| per-prefix-continuations-depth2-cap24 | 1 | 1 | 4 | 39,983,007 | 9,995,751 | 9,995,751 | 9,995,751 | 2026-08-20 | 2026-08-20 | untried |
| rare shared-token splices family sizes 4201-4500 | 1 | 1 | 1 | 10,130,357 | 10,130,357 | 10,130,357 | 10,130,357 | 2026-08-28 | 2026-08-28 | untried |
| \ bo4 rare shared-token splice family 2101-2400\ | 1 | 1 | 2 | 21,030,543 | 10,515,271 | 10,515,271 | 10,515,271 | 2026-08-28 | 2026-08-28 | untried |
| image token insertion and deletion | 1 | 2 | 6 | 64,948,181 | 10,824,696 | 8,118,449 | 16,237,192 | 2026-09-02 | 2026-09-02 | live |
| token edits material current cw 20260903 | 1 | 1 | 3 | 33,095,190 | 11,031,730 | 11,031,730 | 11,031,730 | 2026-09-03 | 2026-09-03 | untried |
| token edits material | 1 | 1 | 3 | 33,118,937 | 11,039,645 | 11,039,645 | 11,039,645 | 2026-09-03 | 2026-09-03 | untried |
| precedents top20 | 2 | 2 | 5 | 57,508,152 | 11,501,630 | 7,188,519 | 7,188,519 | 2026-09-02 | 2026-09-02 | live |
| cold war uncarried four-segment endings current | 1 | 1 | 5 | 60,407,129 | 12,081,425 | 12,081,425 | 12,081,425 | 2026-08-31 | 2026-08-31 | untried |
| \ cold war material token edits cap60 minseen1 20260830\ | 1 | 1 | 13 | 158,177,067 | 12,167,466 | 12,167,466 | 12,167,466 | 2026-08-30 | 2026-08-30 | untried |
| sibling token substitution right context current | 1 | 1 | 23 | 296,853,548 | 12,906,676 | 12,906,676 | 12,906,676 | 2026-08-25 | 2026-08-25 | untried |
| token edits model current | 1 | 2 | 2 | 27,434,480 | 13,717,240 | 13,717,240 | 13,717,240 | 2026-08-29 | 2026-08-29 | live |
| token insertion and deletion model | 1 | 1 | 1 | 13,782,014 | 13,782,014 | 13,782,014 | 13,782,014 | 2026-08-31 | 2026-08-31 | untried |
| token edits model | 1 | 1 | 1 | 13,801,977 | 13,801,977 | 13,801,977 | 13,801,977 | 2026-09-03 | 2026-09-03 | untried |
| \ bo4 material token edits cap70 minseen1 20260830\ | 1 | 1 | 13 | 184,040,349 | 14,156,949 | 14,156,949 | 14,156,949 | 2026-08-30 | 2026-08-30 | untried |
| rare shared-token splice families 241-480 | 1 | 2 | 2 | 29,082,266 | 14,541,133 | 14,541,133 | 14,541,133 | 2026-09-03 | 2026-09-03 | live |
| \ bo4 material token edits cap50 minseen2 20260830\ | 1 | 1 | 9 | 131,591,450 | 14,621,272 | 14,621,272 | 14,621,272 | 2026-08-30 | 2026-08-30 | untried |
| sibling token substitution left context current | 1 | 1 | 23 | 337,560,590 | 14,676,547 | 14,676,547 | 14,676,547 | 2026-08-25 | 2026-08-25 | untried |
| character substitution | 1 | 1 | 81 | 1,256,307,739 | 15,509,972 | 15,509,972 | 15,509,972 | 2026-08-24 | 2026-08-24 | untried |
| black ops 4 material token edits after new findings | 1 | 1 | 2 | 33,006,487 | 16,503,243 | 16,503,243 | 16,503,243 | 2026-08-31 | 2026-08-31 | untried |
| material cores spelled as xmodel | 4 | 9 | 48 | 838,814,750 | 17,475,307 | 90,750 | 28,702,083 | 2026-08-28 | 2026-09-03 | spent |
| suffix precedents current | 2 | 2 | 35 | 622,623,642 | 17,789,246 | 10,042,077 | 77,829,809 | 2026-09-02 | 2026-09-02 | cooling |
| rare shared-token splices family sizes 11701-12000 | 1 | 1 | 1 | 17,801,434 | 17,801,434 | 17,801,434 | 17,801,434 | 2026-08-28 | 2026-08-28 | untried |
| corpus-mined substitutions, top 300 | 1 | 4 | 6 | 109,732,535 | 18,288,755 | 13,715,940 | 27,434,695 | 2026-08-27 | 2026-08-27 | live |
| suffix-chain completion | 2 | 2 | 10 | 187,289,550 | 18,728,955 | 10,404,975 | 10,404,975 | 2026-09-01 | 2026-09-01 | live |
| character insertion | 1 | 2 | 135 | 2,577,959,172 | 19,095,993 | 16,740,545 | 16,740,545 | 2026-08-24 | 2026-08-24 | live |
| token edits mat cap30 | 1 | 1 | 4 | 79,362,695 | 19,840,673 | 19,840,673 | 19,840,673 | 2026-09-03 | 2026-09-03 | untried |
| sound character substitution cw | 1 | 1 | 49 | 983,905,838 | 20,079,710 | 20,079,710 | 20,079,710 | 2026-08-24 | 2026-08-24 | untried |
| cold war, uncarried two-segment endings | 1 | 1 | 597 | 12,179,260,896 | 20,400,772 | 20,400,772 | 20,400,772 | 2026-08-23 | 2026-08-23 | untried |
| rare shared-token splices family size 1801-2100 | 1 | 2 | 2 | 43,513,608 | 21,756,804 | 21,756,771 | 21,756,837 | 2026-08-28 | 2026-08-28 | live |
| corpus-mined substitutions, deep cut | 1 | 1 | 2 | 43,582,606 | 21,791,303 | 21,791,303 | 21,791,303 | 2026-08-25 | 2026-08-25 | untried |
| \ per-suffix precedents bo4 20260830\ | 1 | 1 | 14 | 307,108,676 | 21,936,334 | 21,936,334 | 21,936,334 | 2026-08-30 | 2026-08-30 | untried |
| token edits img cap30 | 1 | 2 | 7 | 154,739,211 | 22,105,601 | 12,894,940 | 12,894,940 | 2026-09-03 | 2026-09-03 | live |
| black ops 4 sound, uncarried two-segment endings | 1 | 1 | 509 | 11,274,140,892 | 22,149,589 | 22,149,589 | 22,149,589 | 2026-08-23 | 2026-08-23 | untried |
| image cores spelled as material | 2 | 3 | 10 | 221,738,750 | 22,173,875 | 14,270,250 | 39,518,125 | 2026-08-28 | 2026-08-28 | live |
| char edits current | 1 | 1 | 3 | 68,250,824 | 22,750,274 | 22,750,274 | 22,750,274 | 2026-08-29 | 2026-08-29 | untried |
| \\ cold war image token length stream\\ | 1 | 1 | 2 | 45,579,875 | 22,789,937 | 22,789,937 | 22,789,937 | 2026-08-29 | 2026-08-29 | untried |
| keyword sweep: zombie models | 1 | 1 | 4 | 100,074,665 | 25,018,666 | 25,018,666 | 25,018,666 | 2026-08-21 | 2026-08-21 | untried |
| cold war, uncarried five-segment endings | 1 | 1 | 382 | 9,963,115,100 | 26,081,453 | 26,081,453 | 26,081,453 | 2026-08-23 | 2026-08-23 | untried |
| \ bo4 material token edits cap60 minseen1 20260830\ | 1 | 1 | 6 | 158,173,101 | 26,362,183 | 26,362,183 | 26,362,183 | 2026-08-30 | 2026-08-30 | untried |
| tails of length 1 | 1 | 1 | 1 | 27,486,426 | 27,486,426 | 27,486,426 | 27,486,426 | 2026-09-03 | 2026-09-03 | untried |
| \ per-suffix precedents cw 20260830\ | 1 | 1 | 11 | 307,102,800 | 27,918,436 | 27,918,436 | 27,918,436 | 2026-08-30 | 2026-08-30 | untried |
| rare splice 961 1920 | 1 | 2 | 5 | 142,066,503 | 28,413,300 | 17,758,312 | 17,758,312 | 2026-09-03 | 2026-09-03 | live |
| cold war, uncarried four-segment endings | 1 | 1 | 645 | 18,715,524,480 | 29,016,317 | 29,016,317 | 29,016,317 | 2026-08-23 | 2026-08-23 | untried |
| material interior character substitutions refreshed | 1 | 1 | 17 | 496,757,656 | 29,221,038 | 29,221,038 | 29,221,038 | 2026-08-27 | 2026-08-27 | untried |
| image siblings wide | 1 | 2 | 8 | 241,732,438 | 30,216,554 | 20,144,369 | 20,144,369 | 2026-09-03 | 2026-09-03 | live |
| rare shared-token splices families 21301-21600 | 1 | 2 | 3 | 91,884,529 | 30,628,176 | 22,971,132 | 22,971,132 | 2026-08-29 | 2026-08-29 | live |
| \ cold war material token edits cap70 minseen1 20260830\ | 1 | 1 | 6 | 184,036,838 | 30,672,806 | 30,672,806 | 30,672,806 | 2026-08-30 | 2026-08-30 | untried |
| image token edits after new findings | 1 | 1 | 1 | 31,952,764 | 31,952,764 | 31,952,764 | 31,952,764 | 2026-08-26 | 2026-08-26 | untried |
| image token insertion and deletion after pr984 | 1 | 1 | 1 | 31,982,799 | 31,982,799 | 31,982,799 | 31,982,799 | 2026-08-27 | 2026-08-27 | untried |
| rare shared token splice 3841 7680 current | 1 | 2 | 11 | 353,828,962 | 32,166,269 | 17,691,448 | 17,691,448 | 2026-09-02 | 2026-09-02 | live |
| token edits image | 1 | 1 | 1 | 32,542,333 | 32,542,333 | 32,542,333 | 32,542,333 | 2026-09-03 | 2026-09-03 | untried |
| rare shared-token splices families 17101-17400 | 1 | 2 | 2 | 66,750,923 | 33,375,461 | 33,375,461 | 33,375,461 | 2026-08-28 | 2026-08-28 | live |
| per-prefix-continuations-depth2-cap48 | 1 | 1 | 2 | 72,302,925 | 36,151,462 | 36,151,462 | 36,151,462 | 2026-08-20 | 2026-08-20 | untried |
| heads of length 1 | 1 | 1 | 1 | 36,707,544 | 36,707,544 | 36,707,544 | 36,707,544 | 2026-08-27 | 2026-08-27 | untried |
| cold war sound, uncarried 1-segment endings | 1 | 2 | 560 | 20,953,836,251 | 37,417,564 | 29,431,729 | 29,431,729 | 2026-08-23 | 2026-08-23 | live |
| black ops 4, uncarried three-segment endings | 1 | 2 | 1,058 | 42,578,054,890 | 40,243,908 | 16,329,961 | 157,676,083 | 2026-08-23 | 2026-08-23 | cooling |
| xmodel cores spelled as image | 2 | 2 | 4 | 162,828,125 | 40,707,031 | 33,660,000 | 33,660,000 | 2026-09-02 | 2026-09-04 | live |
| cold war uncarried one-segment endings top 500 after pr969 | 1 | 1 | 1 | 41,080,998 | 41,080,998 | 41,080,998 | 41,080,998 | 2026-08-27 | 2026-08-27 | untried |
| sound character insertion | 1 | 2 | 49 | 2,032,746,695 | 41,484,626 | 22,585,574 | 254,098,957 | 2026-08-24 | 2026-08-24 | spent |
| per-prefix continuations depth2 cap24 | 1 | 1 | 1 | 41,529,671 | 41,529,671 | 41,529,671 | 41,529,671 | 2026-08-27 | 2026-08-27 | untried |
| \ cold war material token edits cap50 minseen1 20260830\ | 1 | 1 | 3 | 132,268,164 | 44,089,388 | 44,089,388 | 44,089,388 | 2026-08-30 | 2026-08-30 | untried |
| two mined substitutions composed | 1 | 1 | 1 | 45,000,000 | 45,000,000 | 45,000,000 | 45,000,000 | 2026-08-25 | 2026-08-25 | untried |
| measured image channels | 1 | 2 | 2 | 90,670,236 | 45,335,118 | 45,049,731 | 45,620,505 | 2026-08-27 | 2026-08-31 | live |
| black ops 4, uncarried four-segment endings | 1 | 1 | 409 | 18,715,524,480 | 45,759,228 | 45,759,228 | 45,759,228 | 2026-08-23 | 2026-08-23 | untried |
| anim substitutions bo4 | 1 | 1 | 1 | 46,101,284 | 46,101,284 | 46,101,284 | 46,101,284 | 2026-08-26 | 2026-08-26 | untried |
| per-prefix-continuations-depth3-cap24 | 1 | 2 | 10 | 472,580,559 | 47,258,055 | 26,254,247 | 236,292,329 | 2026-08-20 | 2026-08-20 | cooling |
| rare shared-token splices family sizes 8401-8700 | 1 | 1 | 1 | 48,782,460 | 48,782,460 | 48,782,460 | 48,782,460 | 2026-08-28 | 2026-08-28 | untried |
| char substitutions bo4 sounds | 1 | 1 | 21 | 1,035,667,459 | 49,317,498 | 49,317,498 | 49,317,498 | 2026-08-24 | 2026-08-24 | untried |
| material substitutions cw | 1 | 1 | 9 | 492,105,760 | 54,678,417 | 54,678,417 | 54,678,417 | 2026-08-25 | 2026-08-25 | untried |
| black ops 4, uncarried five-segment endings | 1 | 1 | 182 | 9,963,115,100 | 54,742,390 | 54,742,390 | 54,742,390 | 2026-08-23 | 2026-08-23 | untried |
| cold war, uncarried three-segment endings | 1 | 2 | 742 | 42,578,054,890 | 57,382,823 | 23,804,371 | 203,050,496 | 2026-08-23 | 2026-08-23 | cooling |
| cold war sound, uncarried two-segment endings | 1 | 1 | 195 | 11,273,898,861 | 57,814,865 | 57,814,865 | 57,814,865 | 2026-08-23 | 2026-08-23 | untried |
| uncarried two-segment endings over the full published core list | 1 | 2 | 264 | 20,951,727,534 | 79,362,604 | 72,749,053 | 87,298,864 | 2026-08-23 | 2026-08-23 | live |
| confirmed-only all-boundary cores x uncarried endings | 2 | 17 | 1,187 | 109,498,794,977 | 92,248,352 | 29,860,502 | 2,300,323,003 | 2026-08-26 | 2026-08-29 | spent |
| character substitution material current | 1 | 1 | 5 | 466,937,880 | 93,387,576 | 93,387,576 | 93,387,576 | 2026-08-25 | 2026-08-25 | untried |
| confirmed-only all-boundary uncarried endings bo4 | 1 | 1 | 44 | 4,110,141,101 | 93,412,297 | 93,412,297 | 93,412,297 | 2026-09-02 | 2026-09-02 | untried |
| char substitutions cw | 1 | 3 | 41 | 3,975,824,680 | 96,971,333 | 66,239,055 | 265,122,255 | 2026-08-24 | 2026-08-25 | cooling |
| confirmed-only all-boundary cores x uncarried two-segment endings | 1 | 2 | 79 | 7,918,179,181 | 100,230,116 | 59,160,293 | 59,160,293 | 2026-09-01 | 2026-09-01 | live |
| cold war suffix precedents resume | 1 | 1 | 3 | 310,645,123 | 103,548,374 | 103,548,374 | 103,548,374 | 2026-09-01 | 2026-09-01 | untried |
| char substitutions bo4 | 1 | 2 | 23 | 2,650,269,779 | 115,229,120 | 94,629,420 | 147,273,098 | 2026-08-24 | 2026-08-24 | live |
| confirmed-only sound all-boundary cores x uncarried endings | 2 | 7 | 717 | 91,609,516,086 | 127,767,804 | 42,055,113 | 79,082,077 | 2026-08-26 | 2026-08-26 | live |
| uncarried beginnings over the held vocabulary | 1 | 1 | 7 | 945,274,375 | 135,039,196 | 135,039,196 | 135,039,196 | 2026-08-23 | 2026-08-23 | untried |
| confirmed-only all-boundary cores x uncarried five-segment endings | 1 | 1 | 26 | 3,959,839,598 | 152,301,523 | 152,301,523 | 152,301,523 | 2026-09-01 | 2026-09-01 | untried |
| confirmed-only all-boundary cores x uncarried 2-segment endings, top 300000, blkops04 | 1 | 1 | 71 | 11,310,637,702 | 159,304,756 | 159,304,756 | 159,304,756 | 2026-09-01 | 2026-09-01 | untried |
| sound character substitution current | 1 | 1 | 6 | 985,045,956 | 164,174,326 | 164,174,326 | 164,174,326 | 2026-08-25 | 2026-08-25 | untried |
| wrapper decorations, suffix side | 1 | 8 | 1,071 | 185,010,310,334 | 172,745,387 | 1,985,948 | 159,762,864 | 2026-08-23 | 2026-08-23 | spent |
| confirmed-only all-boundary cores x uncarried 3-segment endings, top 300000, blkops04 | 1 | 1 | 64 | 11,293,237,644 | 176,456,838 | 176,456,838 | 176,456,838 | 2026-09-01 | 2026-09-01 | untried |
| cold war sound, uncarried 3-segment endings | 1 | 2 | 121 | 22,865,684,520 | 188,972,599 | 181,473,686 | 181,473,686 | 2026-08-23 | 2026-08-23 | live |
| measured heads of length 6 | 2 | 2 | 92 | 17,483,482,820 | 190,037,856 | 135,677,462 | 135,677,462 | 2026-08-25 | 2026-08-25 | live |
| confirmed-only all-boundary cores x uncarried three-segment endings | 1 | 2 | 41 | 7,911,079,110 | 192,953,149 | 113,035,416 | 113,035,416 | 2026-09-01 | 2026-09-01 | live |
| confirmed-only all-boundary cold war cores x uncarried endings | 1 | 3 | 75 | 14,592,745,926 | 194,569,945 | 67,600,676 | 758,467,584 | 2026-08-29 | 2026-08-31 | spent |
| scoped all-boundary cores x all uncarried 3-segment endings | 1 | 1 | 621 | 134,101,557,623 | 215,944,537 | 215,944,537 | 215,944,537 | 2026-09-03 | 2026-09-03 | untried |
| uncarried endings over all-boundary truncation cores | 1 | 6 | 4,625 | 1,120,036,280,202 | 242,170,006 | 76,634,118 | 518,821,573 | 2026-08-23 | 2026-08-23 | cooling |
| uncarried three-segment endings over the full published core list | 1 | 2 | 56 | 13,564,678,200 | 242,226,396 | 165,422,904 | 165,422,904 | 2026-08-23 | 2026-08-23 | live |
| uncarried three-segment endings over all-boundary cores | 1 | 2 | 1,523 | 400,012,766,734 | 262,647,909 | 221,982,667 | 221,982,667 | 2026-08-23 | 2026-08-23 | live |
| confirmed-only all-boundary uncarried two-segment endings current | 1 | 1 | 28 | 7,610,476,104 | 271,802,718 | 271,802,718 | 271,802,718 | 2026-09-01 | 2026-09-01 | untried |
| model character substitutions refreshed | 1 | 1 | 1 | 286,924,916 | 286,924,916 | 286,924,916 | 286,924,916 | 2026-08-27 | 2026-08-27 | untried |
| all-boundary confirmed cores x uncarried endings | 1 | 8 | 243 | 70,412,103,724 | 289,761,743 | 22,567,795 | 2,875,461,397 | 2026-09-03 | 2026-09-03 | spent |
| measured heads of length 5 | 1 | 3 | 31 | 9,541,037,394 | 307,775,399 | 210,743,705 | 210,743,705 | 2026-08-25 | 2026-08-26 | live |
| uncarried endings over published cores | 1 | 6 | 1,191 | 385,019,657,854 | 323,274,271 | 17,624,983 | 4,062,515,784 | 2026-08-23 | 2026-08-23 | spent |
| black ops 4 confirmed-only all-boundary uncarried two-segment endings | 1 | 1 | 22 | 7,125,471,254 | 323,885,057 | 323,885,057 | 323,885,057 | 2026-08-30 | 2026-08-30 | untried |
| sound, uncarried endings over all-boundary cores | 1 | 8 | 3,397 | 1,105,024,531,644 | 325,294,239 | 92,280,373 | 902,952,472 | 2026-08-23 | 2026-08-23 | cooling |
| char insertions bo4 | 1 | 1 | 4 | 1,358,281,948 | 339,570,487 | 339,570,487 | 339,570,487 | 2026-08-24 | 2026-08-24 | untried |
| confirmed-only all-boundary uncarried endings cw | 1 | 1 | 12 | 4,110,141,101 | 342,511,758 | 342,511,758 | 342,511,758 | 2026-09-02 | 2026-09-02 | untried |
| confirmed-only cores over the full uncarried ending vocabulary | 1 | 8 | 1,576 | 555,022,909,612 | 352,171,896 | 141,523,942 | 3,319,756,536 | 2026-08-23 | 2026-08-23 | spent |
| sound dotted tails | 1 | 3 | 126 | 29,595,227,882 | 352,324,141 | 343,483,821 | 361,595,696 | 2026-08-19 | 2026-08-24 | live |
| confirmed-only all-boundary uncarried sound endings bo4 | 1 | 1 | 43 | 15,363,253,631 | 357,284,968 | 357,284,968 | 357,284,968 | 2026-09-02 | 2026-09-02 | untried |
| measured heads of length 4 | 2 | 3 | 15 | 6,149,861,538 | 409,990,769 | 115,289,728 | 3,152,328,598 | 2026-08-25 | 2026-08-25 | spent |
| confirmed-only all-boundary black ops 4 cores x uncarried endings | 1 | 3 | 41 | 17,821,278,211 | 434,665,322 | 118,435,559 | 118,435,559 | 2026-08-29 | 2026-08-31 | live |
| cold war confirmed-only all-boundary uncarried two-segment endings | 1 | 1 | 16 | 7,124,171,241 | 445,260,702 | 445,260,702 | 445,260,702 | 2026-08-30 | 2026-08-30 | untried |
| composed numeric endings | 1 | 2 | 14 | 6,497,838,750 | 464,131,339 | 406,114,921 | 406,114,921 | 2026-08-23 | 2026-08-23 | live |
| wrapper decorations, prefix side | 1 | 4 | 22 | 10,237,404,404 | 465,336,563 | 39,559,390 | 1,180,777,075 | 2026-08-23 | 2026-08-23 | spent |
| older-title decorations | 1 | 3 | 20 | 9,365,249,044 | 468,262,452 | 6,372,899 | 6,372,899 | 2026-08-23 | 2026-08-30 | live |
| confirmed-only all-boundary cores x uncarried six-segment endings | 1 | 1 | 8 | 3,962,339,623 | 495,292,452 | 495,292,452 | 495,292,452 | 2026-09-01 | 2026-09-01 | untried |
| measured tails of length 56 | 1 | 1 | 5 | 2,521,780,812 | 504,356,162 | 504,356,162 | 504,356,162 | 2026-08-25 | 2026-08-25 | untried |
| all-boundary sound cores x uncarried sound endings, 2 segments, top 200k | 1 | 1 | 634 | 320,548,256,700 | 505,596,619 | 505,596,619 | 505,596,619 | 2026-08-29 | 2026-08-29 | untried |
| first twenty ceiling-dropped black ops 4 sound beginnings | 1 | 1 | 17 | 8,705,046,735 | 512,061,572 | 512,061,572 | 512,061,572 | 2026-08-29 | 2026-08-29 | untried |
| scoped all-boundary sound cores x all uncarried 2-segment sound endings (full vocabulary), re-run at grown corpus | 1 | 1 | 54 | 28,168,563,166 | 521,640,058 | 521,640,058 | 521,640,058 | 2026-09-03 | 2026-09-03 | untried |
| affix sweep | 1 | 1 | 1 | 532,497,168 | 532,497,168 | 532,497,168 | 532,497,168 | 2026-08-20 | 2026-08-20 | untried |
| confirmed-only all-boundary cores x uncarried 1-segment endings, blkops04 | 1 | 1 | 12 | 6,800,804,899 | 566,733,741 | 566,733,741 | 566,733,741 | 2026-09-01 | 2026-09-01 | untried |
| measured heads of length 48 | 1 | 2 | 51 | 30,025,694,930 | 588,739,116 | 428,938,499 | 938,302,966 | 2026-08-25 | 2026-08-25 | live |
| external bo4 xhash cores under uncarried endings | 1 | 1 | 2 | 1,196,624,742 | 598,312,371 | 598,312,371 | 598,312,371 | 2026-09-01 | 2026-09-01 | untried |
| all-boundary cores x uncarried endings, 1 segment(s), top 100000 | 1 | 1 | 6 | 3,777,037,770 | 629,506,295 | 629,506,295 | 629,506,295 | 2026-09-02 | 2026-09-02 | untried |
| all-boundary confirmed sound cores x uncarried sound endings | 1 | 6 | 148 | 95,632,345,436 | 646,164,496 | 132,076,779 | 1,655,224,416 | 2026-09-03 | 2026-09-03 | spent |
| animation transition grid | 1 | 2 | 2 | 1,295,625,020 | 647,812,510 | 647,812,510 | 647,812,510 | 2026-08-23 | 2026-08-23 | live |
| confirmed-only all-boundary cores x uncarried four-segment endings | 1 | 1 | 6 | 3,955,839,558 | 659,306,593 | 659,306,593 | 659,306,593 | 2026-09-01 | 2026-09-01 | untried |
| cold war sound harvested decorations | 1 | 1 | 105 | 71,392,088,600 | 679,924,653 | 679,924,653 | 679,924,653 | 2026-09-02 | 2026-09-02 | untried |
| heads of length 3 | 1 | 9 | 717 | 495,967,132,221 | 691,725,428 | 66,983,541 | 53,101,554,920 | 2026-08-22 | 2026-08-29 | spent |
| xanim cores borrowed wide, stripped shallow | 1 | 2 | 78 | 54,150,768,000 | 694,240,615 | 466,816,965 | 466,816,965 | 2026-08-24 | 2026-08-24 | live |
| double deletion | 1 | 1 | 1 | 712,525,298 | 712,525,298 | 712,525,298 | 712,525,298 | 2026-08-24 | 2026-08-24 | untried |
| measured heads of length 40 | 1 | 2 | 116 | 83,913,981,368 | 723,396,391 | 599,385,581 | 912,108,493 | 2026-08-25 | 2026-08-25 | live |
| confirmed-only all-boundary cores x uncarried 4-segment endings, top 300000, blkops04 | 1 | 1 | 15 | 11,319,937,733 | 754,662,515 | 754,662,515 | 754,662,515 | 2026-09-01 | 2026-09-01 | untried |
| char double deletions cw | 1 | 1 | 1 | 780,126,906 | 780,126,906 | 780,126,906 | 780,126,906 | 2026-08-24 | 2026-08-24 | untried |
| confirmed-only all-boundary cores x uncarried one-segment endings | 1 | 2 | 10 | 7,929,679,296 | 792,967,929 | 495,917,459 | 495,917,459 | 2026-09-01 | 2026-09-01 | live |
| confirmed-only all-boundary sound cores x uncarried 2-segment sound endings, blkops04 | 1 | 1 | 30 | 23,859,316,386 | 795,310,546 | 795,310,546 | 795,310,546 | 2026-09-01 | 2026-09-01 | untried |
| confirmed-only all-boundary cold war sound cores x uncarried sound endings | 1 | 1 | 17 | 14,337,543,374 | 843,384,904 | 843,384,904 | 843,384,904 | 2026-08-29 | 2026-08-29 | untried |
| confirmed-only all-boundary uncarried three-segment sound endings cw | 1 | 1 | 18 | 15,368,253,681 | 853,791,871 | 853,791,871 | 853,791,871 | 2026-09-02 | 2026-09-02 | untried |
| confirmed-only all-boundary uncarried five-segment sound endings bo4 | 1 | 1 | 18 | 15,379,053,789 | 854,391,877 | 854,391,877 | 854,391,877 | 2026-09-02 | 2026-09-02 | untried |
| cold war sound files, core tails of length 1 and 2 | 1 | 1 | 1 | 881,657,430 | 881,657,430 | 881,657,430 | 881,657,430 | 2026-08-23 | 2026-08-23 | untried |
| family walking, numbers in place | 1 | 36 | 1,739 | 218,819,348,829 | 882,336,083 | 200,051,105 | 10,482,007,837 | 2026-08-19 | 2026-09-02 | spent |
| all-boundary cores with uncarried three-segment endings | 2 | 3 | 58 | 53,493,592,404 | 922,303,317 | 446,051,682 | 1,943,570,114 | 2026-08-30 | 2026-08-31 | cooling |
| all-boundary cores with uncarried four-segment endings | 1 | 1 | 16 | 16,060,860,607 | 1,003,803,787 | 1,003,803,787 | 1,003,803,787 | 2026-08-30 | 2026-08-30 | untried |
| confirmed-only all-boundary uncarried sound endings cw | 1 | 1 | 15 | 15,363,253,631 | 1,024,216,908 | 1,024,216,908 | 1,024,216,908 | 2026-09-02 | 2026-09-02 | untried |
| confirmed-only all-boundary uncarried three-segment sound endings bo4 | 1 | 1 | 15 | 15,368,253,681 | 1,024,550,245 | 1,024,550,245 | 1,024,550,245 | 2026-09-02 | 2026-09-02 | untried |
| confirmed-only all-boundary uncarried endings cw snowball | 1 | 1 | 4 | 4,115,041,150 | 1,028,760,287 | 1,028,760,287 | 1,028,760,287 | 2026-09-02 | 2026-09-02 | untried |
| uncarried four-segment endings over all-boundary cores | 1 | 2 | 381 | 400,012,766,734 | 1,049,902,274 | 1,020,440,731 | 1,020,440,731 | 2026-08-23 | 2026-08-23 | live |
| char insertions bo4 sounds | 1 | 1 | 1 | 1,068,730,763 | 1,068,730,763 | 1,068,730,763 | 1,068,730,763 | 2026-08-24 | 2026-08-24 | untried |
| confirmed-only all-boundary sound cores x uncarried 1-segment sound endings, blkops04 | 1 | 1 | 4 | 4,300,971,681 | 1,075,242,920 | 1,075,242,920 | 1,075,242,920 | 2026-09-02 | 2026-09-02 | untried |
| all-boundary cores x uncarried endings, 2 segments | 1 | 1 | 163 | 177,157,271,555 | 1,086,854,426 | 1,086,854,426 | 1,086,854,426 | 2026-08-23 | 2026-08-23 | untried |
| family walking, whole words | 1 | 50 | 13,764 | 6,231,301,971,832 | 1,087,677,076 | 149,450,943 | 1,150,451,712 | 2026-08-19 | 2026-09-01 | cooling |
| all-boundary uncarried three-segment endings current | 1 | 1 | 30 | 33,669,536,692 | 1,122,317,889 | 1,122,317,889 | 1,122,317,889 | 2026-09-01 | 2026-09-01 | untried |
| v2 xanim borrowed endings, ranks 2001-3000 | 1 | 2 | 24 | 28,120,092,000 | 1,171,670,500 | 639,093,000 | 7,030,023,000 | 2026-08-28 | 2026-08-28 | spent |
| external bo4 xhash cores under uncarried endings ranks 3001-6000 | 1 | 2 | 2 | 2,393,249,484 | 1,196,624,742 | 1,196,624,742 | 1,196,624,742 | 2026-09-01 | 2026-09-04 | live |
| measured heads of length 32 | 1 | 2 | 162 | 196,053,608,608 | 1,210,207,460 | 1,113,940,958 | 1,324,686,544 | 2026-08-25 | 2026-08-25 | live |
| tails of length 3 | 1 | 129 | 3,499 | 4,373,100,918,904 | 1,249,814,495 | 35,873,048 | 11,530,285,596 | 2026-08-22 | 2026-09-04 | spent |
| black ops 4 confirmed-only all-boundary uncarried three-segment endings | 1 | 1 | 17 | 21,379,271,264 | 1,257,604,192 | 1,257,604,192 | 1,257,604,192 | 2026-08-30 | 2026-08-30 | untried |
| all-boundary sound cores x uncarried sound endings, 1 segment, top 300k | 1 | 1 | 46 | 58,151,913,260 | 1,264,172,027 | 1,264,172,027 | 1,264,172,027 | 2026-08-29 | 2026-08-29 | untried |
| measured heads of length 12 | 2 | 4 | 160 | 204,300,194,532 | 1,276,876,215 | 579,736,120 | 3,832,699,909 | 2026-08-25 | 2026-08-25 | cooling |
| measured tails of length 64 | 1 | 1 | 1 | 1,336,663,110 | 1,336,663,110 | 1,336,663,110 | 1,336,663,110 | 2026-08-25 | 2026-08-25 | untried |
| v2 xanim borrowed endings, ranks 1001-2000 | 1 | 2 | 21 | 28,271,743,500 | 1,346,273,500 | 738,975,078 | 7,115,608,500 | 2026-08-28 | 2026-08-29 | cooling |
| uncarried five-segment endings over all-boundary cores | 1 | 2 | 597 | 804,758,082,518 | 1,348,003,488 | 906,259,101 | 906,259,101 | 2026-08-23 | 2026-08-23 | live |
| sound all-boundary cores with uncarried one-segment endings | 2 | 2 | 7 | 9,456,617,520 | 1,350,945,360 | 1,182,077,190 | 1,576,102,920 | 2026-08-30 | 2026-08-30 | live |
| heads of length 2 | 1 | 1 | 1 | 1,419,111,216 | 1,419,111,216 | 1,419,111,216 | 1,419,111,216 | 2026-09-03 | 2026-09-03 | untried |
| measured heads of length 10 | 2 | 4 | 94 | 134,357,271,610 | 1,429,332,676 | 965,246,055 | 1,093,886,252 | 2026-08-25 | 2026-08-25 | live |
| confirmed-only all-boundary sound cores x uncarried 3-segment sound endings, blkops04 | 1 | 1 | 30 | 44,393,847,979 | 1,479,794,932 | 1,479,794,932 | 1,479,794,932 | 2026-09-01 | 2026-09-01 | untried |
| cold war sound all-boundary uncarried two-segment endings current | 1 | 1 | 22 | 35,173,151,728 | 1,598,779,624 | 1,598,779,624 | 1,598,779,624 | 2026-09-01 | 2026-09-01 | untried |
| measured heads of length 8 | 2 | 3 | 30 | 48,116,742,888 | 1,603,891,429 | 1,199,252,869 | 1,199,252,869 | 2026-08-25 | 2026-08-25 | live |
| uncarried one-segment endings over all-boundary cores | 1 | 2 | 316 | 522,511,859,758 | 1,653,518,543 | 1,326,172,232 | 2,195,427,982 | 2026-08-23 | 2026-08-23 | live |
| scoped all-boundary cores x all uncarried 3-segment endings, refreshed lists, 2026-09-04 | 1 | 1 | 82 | 139,188,724,500 | 1,697,423,469 | 1,697,423,469 | 1,697,423,469 | 2026-09-04 | 2026-09-04 | untried |
| confirmed-only all-boundary uncarried four-segment sound endings cw | 1 | 1 | 9 | 15,374,753,746 | 1,708,305,971 | 1,708,305,971 | 1,708,305,971 | 2026-09-02 | 2026-09-02 | untried |
| scoped all-boundary cores x all uncarried 2-segment endings, refreshed lists, 2026-09-04 | 1 | 2 | 99 | 172,356,537,460 | 1,740,975,125 | 878,739,411 | 86,240,075,140 | 2026-09-04 | 2026-09-04 | spent |
| cold war sound all-boundary uncarried three-segment endings current | 1 | 1 | 20 | 35,176,151,758 | 1,758,807,587 | 1,758,807,587 | 1,758,807,587 | 2026-09-01 | 2026-09-01 | untried |
| all-boundary sound cores x uncarried sound endings, 2 segment(s), top 100000 | 1 | 3 | 128 | 233,689,336,870 | 1,825,697,944 | 1,476,094,760 | 1,476,094,760 | 2026-08-31 | 2026-09-02 | live |
| scoped all-boundary cores (published+confirmed) x uncarried 2-segment endings, top 300000 | 1 | 3 | 83 | 151,735,705,784 | 1,828,141,033 | 1,097,599,310 | 8,438,228,127 | 2026-09-02 | 2026-09-02 | cooling |
| all-boundary cores x uncarried endings, 4 segment(s), top 100000 | 1 | 1 | 2 | 3,740,637,406 | 1,870,318,703 | 1,870,318,703 | 1,870,318,703 | 2026-09-02 | 2026-09-02 | untried |
| sound all-boundary uncarried endings current | 1 | 1 | 18 | 35,154,751,544 | 1,953,041,752 | 1,953,041,752 | 1,953,041,752 | 2026-09-01 | 2026-09-01 | untried |
| scoped all-boundary cores x all uncarried 2-segment endings | 1 | 1 | 41 | 83,095,021,328 | 2,026,707,837 | 2,026,707,837 | 2,026,707,837 | 2026-09-03 | 2026-09-03 | untried |
| measured heads of length 16 | 2 | 4 | 170 | 356,008,257,188 | 2,094,166,218 | 870,303,956 | 29,590,334,512 | 2026-08-25 | 2026-08-25 | spent |
| all-boundary sound cores x uncarried sound endings, 1 segment(s), top 300000 | 1 | 2 | 54 | 116,405,048,396 | 2,155,649,044 | 1,662,912,897 | 3,063,320,893 | 2026-08-29 | 2026-08-29 | live |
| first twenty ceiling-dropped cold war sound beginnings | 1 | 1 | 4 | 8,704,378,914 | 2,176,094,728 | 2,176,094,728 | 2,176,094,728 | 2026-08-29 | 2026-08-29 | untried |
| confirmed-only all-boundary uncarried six-segment sound endings bo4 | 1 | 1 | 7 | 15,384,053,839 | 2,197,721,977 | 2,197,721,977 | 2,197,721,977 | 2026-09-02 | 2026-09-02 | untried |
| sound harvested decorations | 1 | 1 | 21 | 47,049,001,300 | 2,240,428,633 | 2,240,428,633 | 2,240,428,633 | 2026-09-02 | 2026-09-02 | untried |
| cold war uncarried two-segment endings current depth-matched | 1 | 1 | 5 | 11,227,712,276 | 2,245,542,455 | 2,245,542,455 | 2,245,542,455 | 2026-09-01 | 2026-09-01 | untried |
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
| sound all-boundary cores with uncarried three-segment endings | 2 | 2 | 12 | 33,009,330,090 | 2,750,777,507 | 2,063,120,631 | 2,063,120,631 | 2026-08-30 | 2026-08-30 | live |
| sound all-boundary cores with uncarried four-segment endings | 1 | 1 | 6 | 16,506,165,060 | 2,751,027,510 | 2,751,027,510 | 2,751,027,510 | 2026-08-30 | 2026-08-30 | untried |
| measured tails of length 8 | 2 | 6 | 271 | 753,428,154,966 | 2,780,177,693 | 1,435,820,931 | 2,357,317,948 | 2026-08-25 | 2026-08-25 | live |
| measured tails of length 4 | 1 | 4 | 69 | 192,512,386,856 | 2,790,034,592 | 1,850,196,005 | 3,210,073,152 | 2026-08-25 | 2026-08-25 | live |
| measured heads of length 28 | 1 | 2 | 92 | 257,912,038,902 | 2,803,391,727 | 2,433,132,442 | 2,433,132,442 | 2026-08-25 | 2026-08-25 | live |
| scoped all-boundary cores (published+confirmed) x uncarried 3-segment endings, top 300000 | 1 | 3 | 54 | 151,763,305,876 | 2,810,431,590 | 1,009,989,366 | 50,638,368,794 | 2026-09-02 | 2026-09-03 | spent |
| cold war sound all-boundary uncarried one-segment endings current | 1 | 2 | 16 | 45,395,181,202 | 2,837,198,825 | 729,559,242 | 17,590,675,905 | 2026-09-01 | 2026-09-01 | spent |
| confirmed-only all-boundary uncarried sound endings cw snowball | 1 | 1 | 5 | 15,368,153,680 | 3,073,630,736 | 3,073,630,736 | 3,073,630,736 | 2026-09-02 | 2026-09-02 | untried |
| all-boundary sound cores x uncarried sound endings, 2 segment(s), top 200000 | 1 | 2 | 196 | 642,349,141,010 | 3,277,291,535 | 2,310,125,571 | 5,635,819,063 | 2026-08-29 | 2026-08-29 | live |
| all-boundary sound cores x uncarried sound endings | 1 | 64 | 1,788 | 6,234,167,318,119 | 3,486,670,759 | 304,356,933 | 59,321,595,135 | 2026-08-25 | 2026-09-01 | spent |
| measured tails of length 28 | 1 | 2 | 57 | 199,395,031,004 | 3,498,158,438 | 1,917,259,913 | 1,917,259,913 | 2026-08-25 | 2026-08-25 | live |
| v2 xanim borrowed endings, ranks 3001-4000 | 1 | 2 | 8 | 28,690,662,000 | 3,586,332,750 | 2,009,436,000 | 14,624,610,000 | 2026-08-28 | 2026-09-01 | cooling |
| cold war uncarried two-segment endings | 2 | 3 | 56 | 204,946,704,804 | 3,659,762,585 | 33,648,412 | 33,648,412 | 2026-08-26 | 2026-08-31 | live |
| all-boundary cores x uncarried endings, 3 segment(s), top 300000 | 1 | 1 | 146 | 540,504,901,677 | 3,702,088,367 | 3,702,088,367 | 3,702,088,367 | 2026-08-29 | 2026-08-29 | untried |
| scoped all-boundary sound cores x all uncarried 2-segment sound endings, refreshed lists, 2026-09-04 | 1 | 1 | 8 | 29,638,797,165 | 3,704,849,645 | 3,704,849,645 | 3,704,849,645 | 2026-09-04 | 2026-09-04 | untried |
| measured tails of length 32 | 1 | 2 | 46 | 178,589,946,540 | 3,882,390,142 | 2,289,614,699 | 2,289,614,699 | 2026-08-25 | 2026-08-25 | live |
| measured heads of length 56 | 1 | 2 | 3 | 12,027,546,336 | 4,009,182,112 | 3,006,886,584 | 3,006,886,584 | 2026-08-25 | 2026-08-25 | live |
| measured tails of length 9 | 1 | 2 | 64 | 266,568,581,576 | 4,165,134,087 | 3,920,126,199 | 4,442,809,692 | 2026-08-25 | 2026-08-25 | live |
| scoped all-boundary cores (published+confirmed) x uncarried 4-segment endings, top 300000 | 1 | 1 | 12 | 50,524,368,414 | 4,210,364,034 | 4,210,364,034 | 4,210,364,034 | 2026-09-02 | 2026-09-02 | untried |
| all-boundary sound cores x uncarried sound endings, 3 segment(s), top 200000, blkops04 | 1 | 1 | 8 | 34,537,372,686 | 4,317,171,585 | 4,317,171,585 | 4,317,171,585 | 2026-09-01 | 2026-09-01 | untried |
| general beginnings the 700 ceiling drops | 1 | 8 | 103 | 453,678,445,820 | 4,404,645,105 | 177,450,092 | 588,650,610 | 2026-08-29 | 2026-09-03 | cooling |
| uncarried two-segment endings | 1 | 1 | 23 | 102,361,883,258 | 4,450,516,663 | 4,450,516,663 | 4,450,516,663 | 2026-08-26 | 2026-08-26 | untried |
| uncarried endings ranks 60001-120000 over published cores | 1 | 2 | 21 | 95,849,557,466 | 4,564,264,641 | 2,995,298,670 | 9,584,955,746 | 2026-08-23 | 2026-08-23 | cooling |
| all-boundary cores x uncarried endings, 2 segment(s), top 300000 | 1 | 2 | 231 | 1,080,825,002,738 | 4,678,896,115 | 2,467,636,992 | 45,034,375,114 | 2026-08-29 | 2026-08-29 | spent |
| measured tails of length 5 | 2 | 8 | 105 | 533,600,850,606 | 5,081,912,862 | 2,214,417,335 | 4,556,006,356 | 2026-08-25 | 2026-08-25 | live |
| confirmed-only all-boundary uncarried five-segment sound endings cw | 1 | 1 | 3 | 15,379,053,789 | 5,126,351,263 | 5,126,351,263 | 5,126,351,263 | 2026-09-02 | 2026-09-02 | untried |
| measured tails of length 7 | 1 | 3 | 51 | 262,284,435,218 | 5,142,832,063 | 3,013,818,603 | 12,497,565,171 | 2026-08-25 | 2026-08-25 | cooling |
| measured tails of length 10 | 2 | 7 | 262 | 1,357,535,317,614 | 5,181,432,509 | 2,868,533,268 | 11,751,144,491 | 2026-08-25 | 2026-08-25 | cooling |
| all-boundary sound cores x uncarried sound endings, 2 segments | 1 | 1 | 37 | 198,601,685,997 | 5,367,613,135 | 5,367,613,135 | 5,367,613,135 | 2026-08-23 | 2026-08-23 | untried |
| all-boundary cores x uncarried endings, 2 segment(s), top 100000 | 1 | 3 | 33 | 188,330,083,282 | 5,706,972,220 | 311,036,443 | 311,036,443 | 2026-08-31 | 2026-09-02 | live |
| xanim cores borrowed, xanim decorations measured | 1 | 14 | 391 | 2,379,936,774,200 | 6,086,794,818 | 26,167,942 | 50,169,424,421 | 2026-08-24 | 2026-08-31 | spent |
| measured heads of length 14 | 1 | 2 | 15 | 92,163,619,882 | 6,144,241,325 | 5,760,226,242 | 6,583,115,705 | 2026-08-25 | 2026-08-25 | live |
| confirmed-only all-boundary sound cores x uncarried 5-segment sound endings, blkops04 | 1 | 1 | 7 | 44,441,848,139 | 6,348,835,448 | 6,348,835,448 | 6,348,835,448 | 2026-09-02 | 2026-09-02 | untried |
| all-boundary cores x uncarried endings | 1 | 86 | 2,248 | 14,391,837,192,458 | 6,402,062,808 | 219,308,075 | 90,475,954,750 | 2026-08-25 | 2026-09-01 | spent |
| measured tails of length 6 | 2 | 7 | 91 | 628,969,016,333 | 6,911,747,432 | 1,977,717,171 | 9,578,231,709 | 2026-08-25 | 2026-08-25 | cooling |
| build strings under measured decorations | 1 | 3 | 152 | 1,074,926,265,000 | 7,071,883,322 | 853,253,716 | 853,253,716 | 2026-08-24 | 2026-09-02 | live |
| measured tails of length 16 | 2 | 4 | 137 | 972,904,993,300 | 7,101,496,301 | 3,833,611,586 | 6,380,104,314 | 2026-08-25 | 2026-08-25 | live |
| confirmed-only all-boundary bo4 sound cores x uncarried endings | 1 | 1 | 2 | 14,335,743,356 | 7,167,871,678 | 7,167,871,678 | 7,167,871,678 | 2026-08-29 | 2026-08-29 | untried |
| measured tails of length 18 | 1 | 2 | 51 | 370,685,626,016 | 7,268,345,608 | 5,451,259,206 | 10,902,518,412 | 2026-08-25 | 2026-08-25 | live |
| confirmed-only all-boundary sound cores x uncarried 4-segment sound endings, blkops04 | 1 | 1 | 6 | 44,437,348,124 | 7,406,224,687 | 7,406,224,687 | 7,406,224,687 | 2026-09-02 | 2026-09-02 | untried |
| uncarried two-segment endings current depth-matched | 1 | 2 | 3 | 22,455,424,552 | 7,485,141,517 | 5,613,856,138 | 5,613,856,138 | 2026-09-01 | 2026-09-01 | live |
| all-boundary cores x uncarried endings, 4 segment(s), top 300000 | 1 | 1 | 72 | 540,563,101,871 | 7,507,820,859 | 7,507,820,859 | 7,507,820,859 | 2026-08-29 | 2026-08-29 | untried |
| scoped all-boundary cores (published+confirmed) x uncarried 1-segment endings | 1 | 1 | 4 | 30,324,661,319 | 7,581,165,329 | 7,581,165,329 | 7,581,165,329 | 2026-09-02 | 2026-09-02 | untried |
| cold war confirmed-only all-boundary uncarried endings current | 1 | 1 | 1 | 7,600,476,004 | 7,600,476,004 | 7,600,476,004 | 7,600,476,004 | 2026-09-01 | 2026-09-01 | untried |
| confirmed-only all-boundary uncarried six-segment sound endings cw | 1 | 1 | 2 | 15,384,053,839 | 7,692,026,919 | 7,692,026,919 | 7,692,026,919 | 2026-09-02 | 2026-09-02 | untried |
| confirmed-only all-boundary uncarried seven-segment sound endings cw | 1 | 1 | 2 | 15,387,853,877 | 7,693,926,938 | 7,693,926,938 | 7,693,926,938 | 2026-09-02 | 2026-09-02 | untried |
| measured tails of length 14 | 2 | 5 | 165 | 1,278,003,497,385 | 7,745,475,741 | 3,983,905,894 | 96,886,917,891 | 2026-08-25 | 2026-08-25 | spent |
| xanim cores under borrowed xanim endings | 1 | 4 | 55 | 432,450,304,500 | 7,862,732,809 | 3,978,275,000 | 21,734,716,500 | 2026-08-24 | 2026-08-25 | cooling |
| measured tails of length 12 | 2 | 8 | 190 | 1,547,737,441,906 | 8,145,986,536 | 477,783,178 | 477,783,178 | 2026-08-25 | 2026-08-25 | live |
| all-boundary sound cores x uncarried sound endings, 3 segments, top 200k | 1 | 1 | 49 | 406,230,831,144 | 8,290,425,125 | 8,290,425,125 | 8,290,425,125 | 2026-08-29 | 2026-08-29 | untried |
| vox alias grid, slots composed rather than redistributed | 1 | 1 | 184 | 1,585,821,032,397 | 8,618,592,567 | 8,618,592,567 | 8,618,592,567 | 2026-08-23 | 2026-08-23 | untried |
| all-boundary sound cores x uncarried sound endings, 4 segments, top 300k | 1 | 1 | 66 | 609,361,431,198 | 9,232,748,957 | 9,232,748,957 | 9,232,748,957 | 2026-08-29 | 2026-08-29 | untried |
| material cores borrowed, material decorations measured | 1 | 15 | 496 | 4,606,530,586,700 | 9,287,360,053 | 333,052,312 | 60,987,886,400 | 2026-08-24 | 2026-08-31 | spent |
| measured tails of length 20 | 2 | 4 | 85 | 820,774,633,936 | 9,656,172,163 | 6,347,905,763 | 11,151,898,505 | 2026-08-25 | 2026-08-25 | live |
| measured tails of length 13 | 1 | 2 | 40 | 398,901,306,104 | 9,972,532,652 | 8,671,767,524 | 8,671,767,524 | 2026-08-25 | 2026-08-25 | live |
| black ops 1 build vocabulary | 1 | 2 | 204 | 2,038,307,570,080 | 9,991,703,774 | 6,575,185,709 | 20,799,056,837 | 2026-08-22 | 2026-08-22 | cooling |
| all-boundary sound cores x uncarried sound endings, 4 segment(s), top 300000, blkops04 | 1 | 1 | 5 | 51,912,773,042 | 10,382,554,608 | 10,382,554,608 | 10,382,554,608 | 2026-09-01 | 2026-09-01 | untried |
| measured tails of length 11 | 1 | 2 | 33 | 346,197,974,320 | 10,490,847,706 | 9,110,473,008 | 9,110,473,008 | 2026-08-25 | 2026-08-25 | live |
| v2 sound alias borrowed endings, ranks 16001-19155 | 1 | 2 | 13 | 138,052,908,000 | 10,619,454,461 | 6,275,132,181 | 34,513,227,000 | 2026-08-28 | 2026-08-28 | cooling |
| cold war all-boundary uncarried three-segment endings current | 1 | 1 | 3 | 33,677,936,776 | 11,225,978,925 | 11,225,978,925 | 11,225,978,925 | 2026-09-01 | 2026-09-01 | untried |
| scoped all-boundary cores x all uncarried 4-segment endings | 1 | 2 | 29 | 329,909,647,446 | 11,376,194,739 | 6,474,622,101 | 42,011,023,725 | 2026-09-03 | 2026-09-04 | cooling |
| measured tails of length 24 | 2 | 4 | 54 | 627,132,483,832 | 11,613,564,515 | 3,309,040,403 | 64,813,595,798 | 2026-08-25 | 2026-08-25 | spent |
| image cores borrowed, image decorations measured | 1 | 14 | 868 | 10,326,616,706,000 | 11,897,023,854 | 1,015,745,750 | 39,462,327,692 | 2026-08-24 | 2026-08-31 | spent |
| xmodel cores borrowed, xmodel decorations measured | 1 | 11 | 101 | 1,233,339,419,100 | 12,211,281,377 | 145,020,750 | 91,535,164,000 | 2026-08-24 | 2026-08-31 | spent |
| measured heads of length 20 | 2 | 4 | 36 | 456,964,818,448 | 12,693,467,179 | 6,682,647,252 | 21,184,377,456 | 2026-08-25 | 2026-08-25 | cooling |
| all-boundary sound cores x uncarried sound endings, 5 segment(s), top 300000, blkops04 | 1 | 1 | 4 | 51,978,173,260 | 12,994,543,315 | 12,994,543,315 | 12,994,543,315 | 2026-09-01 | 2026-09-01 | untried |
| head of one name, tail of another | 1 | 2 | 7 | 96,000,800,000 | 13,714,400,000 | 8,000,066,666 | 8,000,066,666 | 2026-08-22 | 2026-08-22 | live |
| v2 xanim borrowed endings, ranks 5001-6000 | 1 | 1 | 1 | 14,078,064,000 | 14,078,064,000 | 14,078,064,000 | 14,078,064,000 | 2026-08-28 | 2026-08-28 | untried |
| v2 xanim borrowed endings, ranks 6001-7000 | 1 | 2 | 2 | 28,171,143,000 | 14,085,571,500 | 14,085,571,500 | 14,085,571,500 | 2026-08-28 | 2026-08-28 | live |
| all-boundary sound cores x uncarried sound endings, 3 segment(s), top 100000 | 1 | 1 | 1 | 14,766,047,659 | 14,766,047,659 | 14,766,047,659 | 14,766,047,659 | 2026-09-02 | 2026-09-02 | untried |
| all-boundary sound cores x uncarried sound endings, 3 segment(s), top 200000 | 1 | 2 | 55 | 812,531,662,638 | 14,773,302,957 | 11,607,595,180 | 20,313,291,565 | 2026-08-29 | 2026-08-29 | live |
| sound ceiling-dropped beginnings over current all-boundary cores 20260830 | 1 | 1 | 28 | 450,263,412,045 | 16,080,836,144 | 16,080,836,144 | 16,080,836,144 | 2026-08-30 | 2026-08-30 | untried |
| measured shells, head 6 tail 6, top 600 | 1 | 1 | 12 | 194,426,913,079 | 16,202,242,756 | 16,202,242,756 | 16,202,242,756 | 2026-09-04 | 2026-09-04 | untried |
| all-boundary uncarried four-segment endings current | 1 | 1 | 2 | 33,678,536,782 | 16,839,268,391 | 16,839,268,391 | 16,839,268,391 | 2026-09-01 | 2026-09-01 | untried |
| xmodel cores borrowed wide, stripped shallow | 1 | 1 | 1 | 17,342,167,500 | 17,342,167,500 | 17,342,167,500 | 17,342,167,500 | 2026-08-24 | 2026-08-24 | untried |
| material cores borrowed wide, stripped shallow | 1 | 2 | 6 | 106,477,308,000 | 17,746,218,000 | 13,309,663,500 | 13,309,663,500 | 2026-08-24 | 2026-08-24 | live |
| measured tails of length 15 | 1 | 2 | 22 | 406,264,584,852 | 18,466,572,038 | 11,948,958,378 | 40,626,458,485 | 2026-08-25 | 2026-08-25 | cooling |
| all-boundary sound cores x uncarried sound endings, 4 segment(s), top 300000 | 1 | 2 | 33 | 662,244,407,474 | 20,068,012,347 | 4,393,314,644 | 4,393,314,644 | 2026-08-29 | 2026-08-31 | live |
| scoped all-boundary cores x all uncarried 5-segment endings | 1 | 1 | 8 | 163,703,135,601 | 20,462,891,950 | 20,462,891,950 | 20,462,891,950 | 2026-09-03 | 2026-09-03 | untried |
| sound beginnings the 700 ceiling drops | 1 | 13 | 213 | 4,546,462,587,563 | 21,344,894,777 | 1,235,117,520 | 49,657,959,936 | 2026-08-29 | 2026-09-03 | spent |
| harvested strings, tails of length 3 | 1 | 1 | 4 | 86,898,811,198 | 21,724,702,799 | 21,724,702,799 | 21,724,702,799 | 2026-08-24 | 2026-08-24 | untried |
| images derived from materials | 1 | 20 | 6,385 | 26,563,766,295,132 | 23,445,513,058 | 13,498,822,351 | 18,958,992,303 | 2026-08-19 | 2026-09-01 | live |
| scoped all-boundary cores x all uncarried 6-segment endings | 1 | 1 | 6 | 144,551,713,541 | 24,091,952,256 | 24,091,952,256 | 24,091,952,256 | 2026-09-03 | 2026-09-03 | untried |
| black ops 3 build vocabulary | 1 | 2 | 293 | 7,358,148,299,220 | 25,113,134,127 | 15,655,634,679 | 63,432,312,924 | 2026-08-22 | 2026-08-22 | cooling |
| harvested strings, heads of length 3 | 1 | 3 | 10 | 253,271,342,362 | 25,327,134,236 | 192,093,060 | 192,093,060 | 2026-08-24 | 2026-09-02 | live |
| uncarried beginnings slice 0-26 | 1 | 1 | 1 | 26,086,235,266 | 26,086,235,266 | 26,086,235,266 | 26,086,235,266 | 2026-08-28 | 2026-08-28 | untried |
| confirmed-only sound all-boundary uncarried endings current | 1 | 1 | 1 | 30,069,300,690 | 30,069,300,690 | 30,069,300,690 | 30,069,300,690 | 2026-09-01 | 2026-09-01 | untried |
| v2 material borrowed endings, ranks 1001-2000 | 1 | 2 | 12 | 426,823,897,500 | 35,568,658,125 | 23,561,037,500 | 71,591,520,000 | 2026-08-25 | 2026-08-28 | cooling |
| all-boundary sound cores x uncarried sound endings, 5 segment(s), top 300000 | 1 | 2 | 18 | 662,121,707,065 | 36,784,539,281 | 35,846,695,959 | 52,727,875,759 | 2026-08-29 | 2026-08-31 | live |
| v2 xanim borrowed endings, ranks 16001-24000 | 1 | 2 | 6 | 221,211,648,000 | 36,868,608,000 | 28,137,516,750 | 28,137,516,750 | 2026-08-25 | 2026-08-28 | live |
| xmodel cores under borrowed xmodel endings | 1 | 2 | 71 | 2,638,444,407,000 | 37,161,188,830 | 29,316,048,966 | 50,739,315,519 | 2026-08-24 | 2026-08-24 | live |
| tails of length 4 | 1 | 20 | 627 | 24,286,531,383,662 | 38,734,499,814 | 5,032,108,457 | 617,020,047,369 | 2026-08-22 | 2026-09-03 | spent |
| uncarried beginnings, optics and prefixed families | 1 | 2 | 7 | 271,475,197,760 | 38,782,171,108 | 27,147,519,776 | 67,868,799,440 | 2026-08-22 | 2026-08-22 | live |
| image cores borrowed wide, stripped shallow | 1 | 2 | 6 | 243,078,381,000 | 40,513,063,500 | 30,384,797,625 | 30,384,797,625 | 2026-08-24 | 2026-08-24 | live |
| v2 xanim borrowed endings, ranks 24001-32000 | 1 | 2 | 5 | 219,351,415,500 | 43,870,283,100 | 36,644,580,000 | 36,644,580,000 | 2026-08-26 | 2026-08-26 | live |
| all-boundary cores x uncarried three-segment endings, black ops 4 | 1 | 1 | 4 | 177,157,271,555 | 44,289,317,888 | 44,289,317,888 | 44,289,317,888 | 2026-08-29 | 2026-08-29 | untried |
| v2 material borrowed endings, ranks 6001-7000 | 1 | 3 | 13 | 644,194,551,000 | 49,553,427,000 | 26,853,389,062 | 26,853,389,062 | 2026-08-27 | 2026-08-28 | live |
| v2 material borrowed endings, ranks 9001-10000 | 1 | 3 | 13 | 644,377,734,000 | 49,567,518,000 | 30,670,926,000 | 107,420,313,000 | 2026-08-27 | 2026-08-28 | cooling |
| v2 material borrowed endings, ranks 5001-6000 | 1 | 4 | 17 | 856,345,990,500 | 50,373,293,558 | 35,804,268,500 | 107,412,805,500 | 2026-08-25 | 2026-08-28 | live |
| uncarried beginnings | 1 | 15 | 77 | 3,923,160,508,528 | 50,950,136,474 | 7,310,746,850 | 120,455,080,080 | 2026-08-23 | 2026-09-04 | spent |
| heads of length 4, slash-bearing beginnings | 1 | 5 | 19 | 1,002,949,411,050 | 52,786,811,107 | 24,929,570,784 | 101,225,594,025 | 2026-08-24 | 2026-08-27 | cooling |
| v2 xanim borrowed endings, ranks 48001-56000 | 1 | 1 | 2 | 110,209,774,500 | 55,104,887,250 | 55,104,887,250 | 55,104,887,250 | 2026-08-26 | 2026-08-26 | untried |
| v2 material borrowed endings, ranks 2001-3000 | 1 | 4 | 15 | 856,342,987,500 | 57,089,532,500 | 21,198,927,750 | 71,614,042,500 | 2026-08-25 | 2026-08-28 | cooling |
| v2 material borrowed endings, ranks 7001-8000 | 1 | 3 | 11 | 644,394,250,500 | 58,581,295,500 | 30,693,234,000 | 214,852,638,000 | 2026-08-27 | 2026-08-28 | cooling |
| material cores under borrowed material endings | 1 | 4 | 128 | 8,470,420,821,000 | 66,175,162,664 | 35,223,652,406 | 101,779,003,800 | 2026-08-24 | 2026-08-24 | live |
| ceiling-dropped sound beginnings over current sound cores | 1 | 1 | 1 | 81,366,616,800 | 81,366,616,800 | 81,366,616,800 | 81,366,616,800 | 2026-09-01 | 2026-09-01 | untried |
| v2 sound alias borrowed endings, ranks 8001-16000 | 1 | 2 | 4 | 334,133,761,500 | 83,533,440,375 | 57,019,126,500 | 57,019,126,500 | 2026-08-25 | 2026-08-26 | live |
| v2 material borrowed endings, ranks 4001-5000 | 1 | 4 | 10 | 856,398,543,000 | 85,639,854,300 | 42,934,791,900 | 214,842,127,500 | 2026-08-25 | 2026-08-28 | cooling |
| tails of length 5 | 1 | 5 | 729 | 62,471,271,397,845 | 85,694,473,796 | 10,653,467,440 | 723,042,398,138 | 2026-08-22 | 2026-08-25 | spent |
| sound beginnings the 700 ceiling drops, over all-boundary sound cores | 1 | 1 | 9 | 884,193,668,358 | 98,243,740,928 | 98,243,740,928 | 98,243,740,928 | 2026-08-29 | 2026-08-29 | untried |
| v2 material borrowed endings, ranks 3001-4000 | 1 | 3 | 6 | 641,527,887,000 | 106,921,314,500 | 106,007,401,500 | 107,421,063,750 | 2026-08-25 | 2026-08-28 | live |
| v2 sound alias borrowed endings, ranks 1-8000 | 1 | 2 | 3 | 325,972,741,500 | 108,657,580,500 | 81,460,181,250 | 163,052,379,000 | 2026-08-25 | 2026-08-25 | live |
| v2 xanim borrowed endings, ranks 56001-64000 | 1 | 1 | 1 | 109,885,734,000 | 109,885,734,000 | 109,885,734,000 | 109,885,734,000 | 2026-08-26 | 2026-08-26 | untried |
| v2 xanim borrowed endings, ranks 72001-80000 | 1 | 2 | 2 | 221,415,673,500 | 110,707,836,750 | 108,865,606,500 | 112,550,067,000 | 2026-08-25 | 2026-08-28 | live |
| v2 xanim borrowed endings, ranks 8001-16000 | 1 | 2 | 2 | 222,651,828,000 | 111,325,914,000 | 108,889,609,500 | 113,762,218,500 | 2026-08-25 | 2026-08-29 | live |
| measured shells, head 6 tail 6, top 1600 | 1 | 3 | 33 | 4,127,396,973,451 | 125,072,635,559 | 62,447,265,963 | 459,905,757,026 | 2026-09-03 | 2026-09-04 | cooling |
| image cores under borrowed image endings | 1 | 4 | 66 | 8,319,045,063,000 | 126,046,137,318 | 47,775,902,275 | 173,376,335,343 | 2026-08-24 | 2026-08-24 | cooling |
| v2 material borrowed endings, ranks 8001-9000 | 1 | 3 | 5 | 644,545,902,000 | 128,909,180,400 | 107,346,739,500 | 107,463,105,750 | 2026-08-27 | 2026-08-28 | live |
| measured shells, head 7 tail 7, top 800 | 1 | 2 | 5 | 653,293,536,624 | 130,658,707,324 | 81,661,692,078 | 81,661,692,078 | 2026-09-02 | 2026-09-02 | live |
| measured shells, head 6 tail 6, top 800 | 1 | 2 | 5 | 687,770,607,960 | 137,554,121,592 | 85,971,325,995 | 85,971,325,995 | 2026-09-02 | 2026-09-02 | live |
| v2 material borrowed endings, ranks 21001-22000 | 1 | 2 | 3 | 435,188,754,000 | 145,062,918,000 | 107,357,250,000 | 220,474,254,000 | 2026-08-27 | 2026-09-03 | live |
| measured shells, head 8 tail 8, top 1600 | 1 | 1 | 8 | 1,241,389,002,712 | 155,173,625,339 | 155,173,625,339 | 155,173,625,339 | 2026-09-03 | 2026-09-03 | untried |
| v2 material borrowed endings, ranks 11001-12000 | 1 | 3 | 4 | 644,581,938,000 | 161,145,484,500 | 107,352,745,500 | 214,938,223,500 | 2026-08-27 | 2026-08-28 | live |
| v2 material borrowed endings, ranks 8001-16000 | 1 | 1 | 10 | 1,695,151,867,500 | 169,515,186,750 | 169,515,186,750 | 169,515,186,750 | 2026-08-25 | 2026-08-25 | untried |
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
| measured shells, head 7 tail 7, top 1600 | 1 | 1 | 5 | 1,304,976,893,120 | 260,995,378,624 | 260,995,378,624 | 260,995,378,624 | 2026-09-03 | 2026-09-03 | untried |
| bo3 mod tools vocabulary under measured decorations | 1 | 2 | 19 | 5,624,859,212,000 | 296,045,221,684 | 281,242,960,600 | 312,492,178,444 | 2026-08-24 | 2026-08-24 | live |
| measured shells, head 8 tail 8, top 800 | 1 | 1 | 1 | 310,731,213,906 | 310,731,213,906 | 310,731,213,906 | 310,731,213,906 | 2026-09-02 | 2026-09-02 | untried |
| measured shells, head 6 tail 5, top 1600 | 1 | 2 | 7 | 2,852,940,114,638 | 407,562,873,519 | 356,617,514,329 | 356,617,514,329 | 2026-09-03 | 2026-09-03 | live |
| v2 material borrowed endings, ranks 56001-64000 | 1 | 2 | 8 | 3,394,468,255,500 | 424,308,531,937 | 339,049,575,900 | 566,406,792,000 | 2026-08-26 | 2026-08-26 | live |
| v2 material borrowed endings, ranks 80001-88000 | 1 | 1 | 4 | 1,698,956,343,000 | 424,739,085,750 | 424,739,085,750 | 424,739,085,750 | 2026-08-26 | 2026-08-26 | untried |
| heads of length 4 | 1 | 4 | 15 | 8,064,939,064,064 | 537,662,604,270 | 220,031,196,218 | 2,041,581,679,232 | 2026-08-24 | 2026-09-02 | cooling |
| measured shells, head 5 tail 5, top 1000 | 1 | 1 | 1 | 560,093,508,975 | 560,093,508,975 | 560,093,508,975 | 560,093,508,975 | 2026-09-02 | 2026-09-02 | untried |
| v2 material borrowed endings, ranks 1-8000 | 1 | 1 | 3 | 1,694,983,846,500 | 564,994,615,500 | 564,994,615,500 | 564,994,615,500 | 2026-08-25 | 2026-08-25 | untried |
| newer-title cores respelled | 1 | 2 | 61 | 34,510,658,565,958 | 565,748,501,081 | 367,134,665,595 | 1,232,523,520,212 | 2026-08-22 | 2026-08-22 | cooling |
| mw19 middles decorated | 1 | 1 | 51 | 29,134,495,063,900 | 571,264,609,096 | 571,264,609,096 | 571,264,609,096 | 2026-08-24 | 2026-08-24 | untried |
| general search | 2 | 110 | 117,265 | 4,897,882,290,410,713 | 577,921,214,207 | 35,073,084,706 | 53,517,243,822,400 | 2026-08-19 | 2026-09-04 | spent |
| broad all-boundary uncarried sound four-segment endings current | 1 | 1 | 2 | 1,229,240,297,454 | 614,620,148,727 | 614,620,148,727 | 614,620,148,727 | 2026-09-03 | 2026-09-03 | untried |
| borrowed decorations over held cores | 1 | 5 | 33 | 21,060,872,662,800 | 638,208,262,509 | 22,720,788,300 | 947,724,507,000 | 2026-08-24 | 2026-08-31 | spent |
| v2 material borrowed endings, ranks 64001-72000 | 1 | 3 | 7 | 5,089,812,147,000 | 727,116,021,000 | 565,158,636,000 | 566,326,782,000 | 2026-08-26 | 2026-08-26 | live |
| v2 image borrowed endings, ranks 16001-24000 | 1 | 3 | 5 | 4,199,720,899,500 | 839,944,179,900 | 468,370,539,000 | 1,405,111,617,000 | 2026-08-26 | 2026-08-28 | live |
| sound files and aliases | 1 | 76 | 31,777 | 2,347,298,060,327,192 | 870,336,692,742 | 166,345,024,102 | 1,646,312,729,581 | 2026-08-19 | 2026-09-04 | cooling |
| measured shells, head 5 tail 7, top 1600 | 1 | 2 | 3 | 2,644,392,954,876 | 881,464,318,292 | 661,098,238,719 | 1,322,196,477,438 | 2026-09-03 | 2026-09-03 | live |
| v2 material borrowed endings, ranks 48001-56000 | 1 | 3 | 5 | 5,090,196,195,000 | 1,018,039,239,000 | 565,186,639,500 | 1,699,076,358,000 | 2026-08-25 | 2026-08-26 | cooling |
| v2 material borrowed endings, ranks 72001-80000 | 1 | 2 | 3 | 3,394,432,251,000 | 1,131,477,417,000 | 847,761,957,000 | 1,698,908,337,000 | 2026-08-26 | 2026-08-26 | live |
| v2 material borrowed endings, ranks 40001-48000 | 1 | 2 | 3 | 3,413,430,625,500 | 1,137,810,208,500 | 859,169,382,750 | 859,169,382,750 | 2026-08-26 | 2026-08-28 | live |
| cold war broad all-boundary uncarried sound four-segment endings current | 1 | 1 | 1 | 1,229,240,297,454 | 1,229,240,297,454 | 1,229,240,297,454 | 1,229,240,297,454 | 2026-09-03 | 2026-09-03 | untried |
| measured shells, head 7 tail 8, top 1600 | 1 | 1 | 1 | 1,253,448,863,417 | 1,253,448,863,417 | 1,253,448,863,417 | 1,253,448,863,417 | 2026-09-03 | 2026-09-03 | untried |
| measured shells, head 6 tail 7, top 1600 | 1 | 1 | 1 | 1,313,248,342,747 | 1,313,248,342,747 | 1,313,248,342,747 | 1,313,248,342,747 | 2026-09-03 | 2026-09-03 | untried |
| measured shells, head 8 tail 6, top 1600 | 1 | 1 | 1 | 1,360,231,817,077 | 1,360,231,817,077 | 1,360,231,817,077 | 1,360,231,817,077 | 2026-09-03 | 2026-09-03 | untried |
| v2 material borrowed endings, ranks 32001-40000 | 1 | 1 | 1 | 1,695,955,968,000 | 1,695,955,968,000 | 1,695,955,968,000 | 1,695,955,968,000 | 2026-08-25 | 2026-08-25 | untried |
| not recorded | 1 | 106 | 4,517 | - | - | - | - | 2026-08-19 | 2026-09-04 | unmeasured |
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

663 distinct methods, run 746 ways between them, across 2641 runs. `names` is what each run
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

## Dead ends

Do not spend a night rediscovering these. Each cost real time.

| Tried | Outcome |
|---|---|
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
| A legacy name corpus found on disk, diffed against the published tables | The complement of the *re-hashing the newer titles' names* row above: that one asked whether the tables' **newest** sources reach these two games, this one asks whether their **oldest** ones were folded in completely. An earlier generation of community name data shipped its sources as plain CSVs under a hash function that means nothing to us, so only the name strings matter. **1,782,690 distinct names** across eleven files, compared by string against all 3,565,276 names the current tables hold: **2,434 absent, 0.14%**, and all 2,434 come from a single image file whose names are in a composite spelling (`colour&spec~<decimal>`, `*reflection_probe_octahedron_N`) that neither of our two titles uses. Offered verbatim plus every decomposition of that spelling -- 7,946 candidates -- against both games: **0 and 0.** **Confirming against the snapshots is the whole point of this one:** a legacy index like this is a community artefact, not a dump, and a large share of what it holds is not a real asset in *any* of these games -- so a name being absent from the tables says nothing on its own, and only a hash landing on an id the snapshot actually holds is evidence. The scrape was not sloppy; it was essentially complete, and the one file it half-carried holds nothing either game could hold. Worth knowing for the reach figure it produced on the way: the legacy corpus lands on **194,257** real Black Ops 4 ids and **520,874** real Cold War ids, overwhelmingly in the wanted types, so this vocabulary genuinely describes these games -- it is simply already all in the tables. Generator: `scripts/contributed/legacy_index_gap.py`. |

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
