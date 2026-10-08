# Which file is which, and which hash it uses

Everything this project checks against lives in [cod-name-db](https://github.com/echo000/cod-name-db),
and its files do not all use the same hash. Getting the mask wrong is the commonest reason a
correct name fails to resolve, and it fails silently — the name simply looks unknown.

This is the mapping, from Saluki's own loading code (`name_db_manager.rs` for which file belongs to
which game, `constant.rs` / `search.rs` / `sound.rs` for the offsets and masks). It comes from the
author of both Saluki and cod-name-db, which makes it the strongest available statement of what is
correct. Every rule below was verified empirically against the file contents.

## The table

| File | Game(s) | Hash of the name | Key stored as |
|---|---|---|---|
| `fnv1a_xmodels.csv` | **BO4, BOCW** | FNV-1a 64, Treyarch offset | 63-bit (bit 63 cleared) |
| `fnv1a_xanims.csv` | **BO4, BOCW** | FNV-1a 64, Treyarch offset | 63-bit |
| `fnv1a_ximages.csv` | **BO4, BOCW** | FNV-1a 64, Treyarch offset | 63-bit |
| `fnv1a_xmaterials.csv` | **BO4, BOCW** | FNV-1a 64, Treyarch offset | 63-bit |
| `fnv1a_<language>_xsounds.csv` (×12) | **BO4, BOCW** | FNV-1a 64, Treyarch offset | 63-bit |
| `fnv1a_xsounds.csv` | **BO4, BOCW** *(legacy — superseded by the per-language files; not loaded by current Saluki)* | FNV-1a 64, Treyarch offset | 63-bit |
| `fnv1a_soundbanks_aliases.csv` | **BO4, BOCW** *(not loaded by current Saluki, but where both games' alias names belong)* | FNV-1a 64, Treyarch offset | 63-bit |
| `fnv1a_strings.csv` | **BOCW** (bone names, notify/script strings) | FNV-1a 64, Treyarch offset | **60-bit** (top 4 bits cleared) |
| `fnv1a_xanims_v2.csv` | MWIII, BO6, BO7, WZ Mobile | FNV-1a 64, **IW offset** | 63-bit |
| `fnv1a_ximages_v2.csv` | MWII, MWIII, BO6, BO7, WZM | FNV-1a 64, IW offset | 63-bit |
| `fnv1a_xmaterials_v2.csv` | MWII, MWIII, BO6, BO7, WZM | FNV-1a 64, IW offset | 63-bit |
| `fnv1a_xsounds_v2.csv` | Vanguard, MWII, MWIII, BO6, BO7, WZM | FNV-1a 64, IW offset | 63-bit |
| `fnv1a_soundbanks_v2.csv` | MWII, MWIII, BO6, BO7, WZM | FNV-1a 64, IW offset | 63-bit |
| `fnv1a_animpkgs_v2.csv` | MWII, MWIII, BO6, BO7, WZM | FNV-1a 64, IW offset | 63-bit |
| `fnv1a_soundbanks_aliases_v2.csv` | Vanguard, MWII, MWIII, BO6, BO7, WZM | FNV-1a 64, **Treyarch offset** | **full 64-bit, no mask** |
| `fnv1a_bones.csv` | MWII, MWIII | **FNV-1a 32** | full 32-bit |
| `fnv1a_bones_v2.csv` | BO6, BO7, WZM | FNV-1a 64, **Treyarch offset** | **full 64-bit, no mask** |
| `bo2_sab.csv` | BO2 `.sab` audio | **SDBM**, seed 5381, lowercased | 32-bit |
| `bo3_sab.csv` | BO3 `.sab` audio | SDBM, seed 5381, lowercased | 32-bit |
| `bo2_ipak.csv` | BO2 `.ipak` images | *not a hash of the name* — native ipak entry keys | 64-bit |
| `cod_semantics.csv` | all games | *not derivable* — engine-provided semantic hashes | 32-bit |
| `cod_constants.csv` | all games | *not derivable* — engine-provided constant hashes | 32-bit |

## Where to get them, and why it is git rather than the releases

cod-name-db publishes **both**, and they are not the same thing:

| | what it is | how fresh |
|---|---|---|
| `csv/` in the git repository | **the source of truth.** The README says so in its first line, and every rule above is a statement about these files. | the commit itself |
| a GitHub release (`hash_pkg.zip`) | the **compiled** `.cdb` binaries Saluki loads, built from those csv | published minutes *after* the commit — 0.0.279 went out at 22:09 for a csv commit at 22:07 |

So `fetch-tables` clones `csv/` with a shallow, blobless, sparse checkout, and that is correct
rather than a shortcut: the release is downstream of the thing we need, arrives later, and is in a
format this project would have to decompile to read. Releases are for Saluki users; the csv are
for anyone computing against the names.

`start` reports which upstream commit the local checkout is on, and it deliberately does *not*
report file modification times — those are set by our own fetch, so a freshly downloaded copy of
month-old data would report itself as brand new, which is precisely backwards.

## The offsets

One algorithm, two starting offsets. That is the only difference between the plain files and the
`_v2` files.

```
Treyarch era (BO4, BOCW, and the aliases/bones exceptions): 0xCBF29CE484222325
IW era (the _v2 files)                                    : 0x47F5817A5EF961BA
prime                                                     : 0x100000001B3

hash = offset
for each byte of the lowercase name:
    hash = (hash XOR byte) * prime          64-bit wrapping multiply
```

Fold backslashes to forward slashes before hashing. Asset names are lowercase in every game.

**Masking.** The engines use the top bit of an asset hash as a flag, so most keys are stored with
bit 63 cleared: `key = hash & 0x7FFFFFFFFFFFFFFF`. The exceptions are in the table above.

## What this means for this repository

The solver routes ordinary modern asset searches through the IW offset and modern sound aliases through the Treyarch offset. It compares 63-bit capture ids but writes modern aliases at full width. Legacy BO4/CW hashes and the BO4 SAB backslash exception retain their existing policies. See [modern capture setup](MODERN_CAPTURES.md).

Published sound strings may be Saluki display paths rather than their original hash spellings. Their stored database keys are authoritative for exclusion. A restored spelling is used as a seed or result only after it reproduces that key; written findings always contain the actual verified spelling. The live legacy snapshot utility cannot capture modern games or their injected pools; use hash-capture and then merge mode captures by type.

---

*Source: the cod-name-db README by its author, cross-checked against Saluki's loading code. Last
verified against the repository contents 2026-08-19 (33 csv files present).*

## Reading original database spellings

Resolved FNV names pass through one source-table-aware conversion in the Rust table readers, direct CSV candidate/plan readers, Python table readers, vocabulary derivation, submission exclusions and validator published-name checks. Correct spellings are kept; export-directory separators are restored to periods or original BO4 sound backslashes only when the candidate reproduces the stored source key. The database files themselves are read-only.

The source table determines its offset, width and case rules, independent of the game currently selected for searching. Legacy CSVs also contain earlier 60-bit and case-sensitive entries; these are verified under their original source rules. Modern full-width aliases still require all 64 bits.

A row that cannot be restored is skipped as a resolved-name seed. Its stored key is always retained for exclusion, so it is never reported as an unknown asset merely because its export spelling differs. Display paths that do not reproduce their key are never rehashed into additional exclusion keys. Written findings retain the actual spelling verified against their game capture.
