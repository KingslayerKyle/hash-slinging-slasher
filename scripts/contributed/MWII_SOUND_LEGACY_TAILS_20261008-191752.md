# MWII sound, part two: the legacy voice-line axis, and four measured negatives

Addendum to `MWII_SOUND_METHODS.md`, same evening, 2026-10-08. Written after the first document had
already gone up in a pull request, so it stands alone and names the earlier one.

## The finding: BO4/Cold War voice lines are MWII's largest reachable sound ground

Everything in part one drew its vocabulary from tables that hash with the offset MWII uses. There is
a corpus this project has always had and that cannot be used that way: the **twelve legacy
per-language sound tables**, 825,316 names across 136 MB.

They are Treyarch-hashed and backslash-separated, so their *names* are not MWII sound-file
candidates and their directories are worthless. But look at what a name is made of:

```
vox/scripted/zm_operators/frs2/vox_frs2_zm_pick_up_weapon_lmg_00.rn75.pc.en.snd
                    iw9/op/alejandro/dx_op_alej_ping_alej_plrg_gotreconhere_ogr2.sn.75.48000.english
```

The speaker code (`frs2`, `alej`) and the prefix (`vox_`, `dx_op_`) are era-specific. **The line text
is not** — `pick_up_weapon_lmg`, `ping_item_rad_vest`, `exert_concuss`, `gotreconhere` are the same
English phrases in both, and that is exactly the trailing-token-run axis the shared-tail plan needs.

Harvested as **tails only**, judged on their own directory support:

| | |
|---|---:|
| attested underscore cuts across the twelve tables | 7,871,959 |
| distinct trailing token runs | 117,289 |
| carried at >=2 legacy directories | **11,581** |
| MWII tail list, modern-only -> modern+legacy | 13,663 -> **24,786** |

And the return, against the two neighbouring widenings run the same evening:

| plan | candidates | matched | new |
|---|---:|---:|---:|
| MWII tails + take axis | 188,237,814,336 | 364 | 364 |
| + all modern games' tails, no takes | 12,529,777,117 | 16 | 16 |
| **+ legacy voice-line tails, no takes** | 22,730,224,374 | **273** | 53 |

A 1.8x wider tail list returned **17x** the matches of the narrower modern-only one. The extra
vocabulary was not better tails of the same kind — it was a pool of line text that no modern table
contributes at all.

**The generalisable form.** When a game has been published for years, its own tables are mined out
and the cheap widening returns nothing (section 3 below measured exactly that). The remaining
vocabulary is usually in a corpus that *cannot* be hashed into the target game — wrong offset, wrong
separator — and therefore looks useless. It is not useless: **strip it to the part the two eras
share and use that as an axis.** For names built from a speaker code plus a phrase, the phrase is
the shareable part.

## Negative 1 — the execution take grid is already full

`mp.executions.` is the largest group in MWII's sound pool (2,953 published names, 962 of them in
MWII's capture) and the cleanest: 163 cores, a take index, and an encoding, always in that order.
Takes run `_01`..`_17`, **4.87 per core on average, 16 at most**.

Aimed at it directly -- every measured MWII head, no token tail at all, just every take index
`00..29` padded and unpadded crossed with all 22 measured encodings, 15,226,640 candidates -- it
returned **nothing new**. The earlier plan's endings column had already covered the same ground with
a wider take range.

This is what a filled grid looks like from outside, and it is worth stating plainly: the take-index
axis is **not** where MWII's remaining 203,952 unnamed sound ids are. The decaying per-batch counts
on the take-bearing plan (78, 49, 92, 63, 172, 25, 21, 0) were already telling you.

## Negative 2 — modern-only cross-game tails are spent

Widening tails to every modern game while dropping the take axis returned **16 names from 12.5
billion candidates**, one per 783 million, against the take-bearing plan's one per 516 million over
188 trillion. Those tails are the same *kind* of token the MWII tables already carry, so the first
plan had already taken them.

## Negative 3 — re-widening a spent method

The alias head/tail method, run three times, each a widening of the last:

| run | vocabulary | found | already claimed |
|---|---|---:|---:|
| MWII only | 9,088 x 3,451 | 2,121 | 0 |
| + MWIII/BO6/BO7/MW7 | 15,903 x 5,504 | 2,048 | 1,047 (51%) |
| + BO4/CW aliases | 53,643 x 19,517 | 1,720 | 1,562 (91%) |

The first plan already filled the cells the extra words reach. **`submit` prints this ratio for a
reason** — "51% of what this run found was already claimed" is the run telling you its own method is
finished, and the cheapest response is to go somewhere the method cannot reach, not to widen it once
more.

## Negative 4 — a whole-product plan on a game with unique basenames

Recorded in full in part one, repeated because it is the most expensive mistake available here:
`directory x basename x tail` over 3.56 trillion candidates found **nothing in 345 billion** and
never would have, because MWII holds 44,077 distinct basenames across 45,049 names. One line of
measurement -- basenames per name -- decides whether a whole-product plan is worth anything at all.

## An operational note worth having: `submit`'s ledger can outrun its own push

`submit` records a run in `submissions/.submitted` when it sends it. Killing it between that write
and the `gh pr create` leaves a run marked sent whose pull request **does not exist**, and the names
are then dropped forever as "already claimed" — by the ledger that was written about them.

It happened here on a truncated pipe: 53 confirmed names sat in `findings/` and in an orphaned
`submissions/` folder, and two subsequent `submit` runs both reported zero to send. The repair is
three steps, and each is safe on its own:

1. confirm the names are still in `findings/<game>/` -- if they are not, nothing can be recovered;
2. move the orphaned folder **out** of `submissions/`, because that tree is scanned as "merged
   submissions" and its names are excluded from resending even when no pull request carries them;
3. delete that one run's line from `submissions/.submitted` and submit again.

Do not rewrite the ledger wholesale. It is append-only by design -- "so a crash cannot lose the
record and cause the same names to be submitted twice" -- and editing it with `Set-Content
-NoNewline` concatenates every line into one and disables it entirely. Write it back with an
explicit `join("\n")`.

## Two sizing lessons, both of which cost hours

**The stem list is a memory cost, and it is not the candidate count.** The cross-game take-bearing
plan was 1.27 *trillion* candidates, which reads as a long pleasant grind and ran at a sensible
105M/s. Its stem list was **73,138,039 strings in a 2.8 GB text file**, on a machine with 7.9 GB of
RAM in total and 0.9 GB free. It was killed before it scanned a single candidate. The fix was
`--most-variant 0`, which drops the take multiplier and takes the same plan to 12.5 billion
candidates and 26 MB -- and, per section 3, that version was worth less, so the honest cost was one
run's time. **Size the stem list against free memory, not the candidate count against your night.**

**Fold endings into the stem column.** With an `end:` line the engine peels endings off the wanted
ids instead of hashing forward, and peeling is only nearly free when the ending list is short next
to the candidate count. On the take-bearing plan it announced "about 23.5B of work against 262.0B
peeling" and spent **32 minutes of eight cores** building the peeled set without sweeping one
forward hash. Write no `end:` line and the identical candidate count runs at ~96M/s in half an hour.

## Where this leaves MWII

| pool | unnamed at session start | recovered | left |
|---|---:|---:|---:|
| `sound_alias` | 137,948 | 3,280 | ~134,700 |
| `sound_asset` | 203,952 | 436 | ~203,500 |

Every axis measured tonight against `sound_asset` is now either exhausted (the take index, the
modern-only tails, the executions grid) or already carried into the merged tables. What is left is
**invention, not widening**, and the honest signal that a machine should idle rather than keep
running a spent plan is exactly the one the last two runs gave.

One thing a successor should not have to rediscover: **`python scripts/derive_modern_lists.py
--game MODWAR22` did not exist before this session and no modern game could be searched without it.**
`state/swept.txt` held 3,434 exhausted configurations and not one was MWII, MWIII, BO6 or BO7 --
not because nobody chose them, but because `data/modern/` was empty, so every modern search had zero
beginnings, zero endings, tested no candidate, and reported success.