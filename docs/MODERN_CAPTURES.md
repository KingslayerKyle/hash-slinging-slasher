# Modern game support and combined snapshots

The snapshot searches support MODWAR22 (MWII), YAMYAMOK (MWIII), BLACKOP6, BLACKOP7 and MODWAR7, alongside BLKOPS04 and BLKOPSCW. A tag identifies the game; filenames do not determine its hash policy.

Keep one complete capture per game in the configured snapshot directory. For modern captures, an adjacent `.pools.txt` map is required. Native and artificially injected pool indexes are both resolved through that capture's map. Unknown mappings and multiple captures with the same tag are refused. The older BO4/CW maps retain their existing injected sound-file and alias indexes.

MP/SP captures are merged by asset type name, preserving the first input's indexes and appending types absent from it. A shared `(id, type)` appears once. Source files are preserved, and `.merge.json` records checksums and remapping. These canonical indexes are for the merged file; they must never be used to read a live game's pools.

```text
python scripts/merge_snapshots.py --game MODWAR22 --out snapshots/modwar22.ids mp.ids sp.ids
```

The repository ships one `.ids` file and adjacent `.pools.txt` map per game in `snapshots/`. MWII, MWIII and BO6 contain their combined captured MP/SP modes. Separate source-mode captures and private merge reports stay outside the tracked snapshot directory. MW7 uses `modwar7.ids` for the current capture and later retail replacement; no separate beta slot is created. A capture establishes only the assets present in that loaded build.

Ordinary modern asset names use FNV-1a 64 with offset `0x47F5817A5EF961BA`; sound aliases use `0xCBF29CE484222325`. Capture lookups use 63 bits. Modern alias output retains all 64 bits; ordinary results use 63. Names are lowercased for hashing and backslashes fold to `/`, except BO4 SAB sound-file names, which retain their backslashes. Bones and script-string hashes are separate families; these changes do not add bone/string extraction.

The `_v2` tables provide modern seed names and exclusions. Their stored keys remain authoritative when Saluki's displayed sound paths have replaced original periods/backslashes with directory separators. Sound seeds are restored only when a candidate spelling reproduces that key. Unsupported display transformations are skipped as seeds, while the stored key still excludes the already-known asset. Findings contain the verified original spelling, so the string after `hash,` reproduces the written hash under its game's policy.

Generate vocabulary from reproducible published names actually held in the chosen capture:

```text
python scripts/derive_modern_lists.py --game BLACKOP6
```

This writes ignored `data/modern/<game>/` lists, separate from the committed legacy vocabulary. `confirm_cw` uses these lists for modern tags; `confirm_list` and `confirm_plan` can use supplied candidate lists directly. Searches split ordinary assets and aliases into their proper hash policies. `validate --game <TAG> <folder>` checks the hash, its output width, and its actual capture pool.

`start` and the local-only `next_game` command rotate through available captures in this order: BO4, CW, MWII, MWIII, BO6, BO7, then MODWAR7 if installed. Each selection advances one slot; older accumulated pass counts cannot starve existing games while new ones catch up. `--game <TAG>` pins a selection without consuming a rotation turn. Set `games = ["BLACKOP6", "YAMYAMOK"]` in `[search]` to restrict the rotation, or `alternate_games = false` to pin the configured game. Rotation chooses a game; it does not prescribe a rotation of search methods.

`next_game` only saves the game choice. It does not refresh tables, run startup network checks or grant a readiness receipt. The existing deliberate offline `--anyway` override still leaves published-name exclusions enabled. Local development can proceed without running `start`, `submit`, committing or pushing.

An isolated published-name replay exercises all six searchable types, forward searches, inverse/fragment searches, mixed-pool routing, normal exclusions and result writing. Modern models use reproducible names shared with ordinary source tables, since the database has no dedicated modern model table; every fixture must match that game's actual model pool:

```text
verify_capture --game BLACKOP6 --out replay-output
validate --game BLACKOP6 replay-output
python scripts/test_merge_snapshots.py
```

Replay output is test evidence, not new findings. The replay temporarily withholds sampled names only in its own exclusion set; normal search exclusions and readiness checks are unchanged. Use a fresh output directory for each replay. Test counts establish these policies for sampled names; they do not prove every asset or displayed sound path is recoverable.

## Modern-games release milestone

The modern-games support change adds MWII, MWIII, BO6, BO7 and MW7 while retaining BO4/CW. Its commit title and annotated release tag should explicitly identify this milestone. Snapshot record counts:

| Game | File | Records |
|---|---|---:|
| BO4 | `blkops04.ids` | 1,153,208 |
| Cold War | `blkopscw.ids` | 1,677,099 |
| MWII | `modwar22.ids` | 1,594,748 |
| MWIII | `yamyamok.ids` | 1,915,075 |
| BO6 | `blackop6.ids` | 2,075,902 |
| BO7 | `blackop7.ids` | 3,438,755 |
| MW7 | `modwar7.ids` | 489,098 |

The existing game choice is preserved when the new rotation cursor is first created. From then on the seven captured games take turns, with CLI overrides leaving the cursor alone.

Optional live-loader builds also search modern games from the combined snapshots: canonical
merged and injected indexes must never be mistaken for the live loader's native pool indexes.

## Reading original database spellings

Resolved FNV names pass through one source-table-aware conversion in the Rust table readers, direct CSV candidate/plan readers, Python table readers, vocabulary derivation, submission exclusions and validator published-name checks. Correct spellings are kept; export-directory separators are restored to periods or original BO4 sound backslashes only when the candidate reproduces the stored source key. The database files themselves are read-only.

The source table determines its offset, width and case rules, independent of the game currently selected for searching. Legacy CSVs also contain earlier 60-bit and case-sensitive entries; these are verified under their original source rules. Modern full-width aliases still require all 64 bits.

A row that cannot be restored is skipped as a resolved-name seed. Its stored key is always retained for exclusion, so it is never reported as an unknown asset merely because its export spelling differs. Display paths that do not reproduce their key are never rehashed into additional exclusion keys. Written findings retain the actual spelling verified against their game capture.
