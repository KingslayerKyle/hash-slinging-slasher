# Current committed binaries cannot target `sound_asset` in any modern game

Found 2026-10-09 while grinding MWII, and it is not specific to anything I wrote. **Every search
tool in `bin/` currently resolves four pools for MWII instead of six and silently never looks at
MWII's 203,952 unnamed `sound_asset` ids.**

## What it looks like

    bin\windows\confirm_list.exe - --game MODWAR22 --label "anything"
    config.toml lists a pool this game has no name for: sound_asset
    searching 4 pool(s): image, material, sound_alias, xanim

Four pools, not six, and one of the six defaults is missing. The run reports success. It is the
same for `confirm_plan` and `confirm_cw`:

    bin\windows\confirm_plan.exe plans\mwii_melee.txt --game MODWAR22 --size
    config.toml lists a pool this game has no name for: sound_asset
    searching 4 pool(s): image, material, sound_alias, xanim

`xmodel` is also absent, but that one is **intended**: commit `99079ddf` deliberately excludes modern
model names behind a `search_modern_models` opt-in. `sound_asset` is not intended by anything.

## Why, exactly

`src/config.rs`, in `targets_from_text`, resolving the configured pool names against the capture's
own census:

```rust
match table.iter().position(|kind| *kind == crate::games::canonical(name)) {
    Some(index) => { if allowed(table[index]) { pools.insert(index); } }
    None => eprintln!("config.toml lists a pool this game has no name for: {name}"),
}
```

`table` is `pools_for(game)` -- the capture's census, read from `snapshots/<game>.pools.txt`, holding
the names **as the capture spells them**. For every modern game the sound-file pool is spelled
`sndasset`, not `sound_asset`. So `*kind` is `"sndasset"` and never equals a canonicalised config
name.

`games::canonical` maps in one direction only:

```rust
pub fn canonical(kind: &str) -> &str {
    match kind { "sndasset" => "sound_asset", other => other }
}
```

so the comparison cannot succeed from either side:

| config name | `canonical(name)` | census entry | equal? |
|---|---|---|---|
| `sound_asset` | `sound_asset` | `sndasset` | no |
| `sndasset` | `sound_asset` | `sndasset` | no |

**There is no spelling of the setting that resolves it.** The census side is never canonicalised.

## The fix

Canonicalise both sides:

```rust
match table.iter().position(|kind| {
    crate::games::canonical(kind) == crate::games::canonical(name)
}) {
```

Census `sndasset` canonicalises to `sound_asset`, which then equals the canonicalised config name.
Legacy games are unaffected: their pools are already spelled `sound_asset`, and `canonical` is the
identity on everything else.

## Which commit introduced it

`99079ddf Exclude embedded modern model names from default searches` (Kyle, 2026-10-08 22:35). The
binaries are tracked in git, so the pull that brings it in brings the behaviour with it:

    git log --oneline b51517ca..HEAD -- bin/windows/confirm_list.exe
    99079ddf Exclude embedded modern model names from default searches

The previous binaries do resolve all six, which is the cleanest possible confirmation:

    # bin/ as of b51517ca
    searching 6 pool(s): image, material, sndasset, sound_alias, xanim, xmodel

Before that commit the lookup went through `pool_index`, which carries an explicit fallback list
containing `sndasset` (`src/lib.rs`: `&["sound_asset", "sound", "sndasset"]`). The rewrite replaced a
lookup that had the fallback with one that canonicalises a single side of the comparison, and the
fallback went with it.

## Why no test caught it

That commit reports *"118 Rust tests and 25 Python tests passed"*, and it very likely did. What is
missing is a test that asserts a **modern** game resolves all six default targets -- every pool test
in `config.rs` builds its table from `crate::POOLS` or `BO4_POOLS`, which are the legacy enums where
`sound_asset` is spelled correctly. The regression is invisible to a suite that never constructs a
modern census.

One test pins it:

```rust
/// Every default target must resolve in a modern capture too, whose census spells the sound-file
/// pool `sndasset`. Before this, `sound_asset` matched nothing and every modern sound id went
/// unsearched while the run reported success.
#[test]
fn modern_games_resolve_every_default_target() {
    let table = crate::games::pools_for("MODWAR22");
    for name in crate::config::DEFAULT_POOLS {
        assert!(
            table.iter().any(|kind| crate::games::canonical(kind) == crate::games::canonical(name)),
            "{name} does not resolve against the MODWAR22 census"
        );
    }
}
```

`xmodel` needs care: it is absent from a modern census by design after `99079ddf`, so either assert
over `["xanim", "image", "material", "sound_asset", "sound_alias"]` or check the modern census
directly for the pool that is supposed to be there.

## What it cost, measured

Not a theory. `derive_closure.py` on MWII ran seven derivations and reported
`image siblings`, `materials from images`, `image channel completion`, `final byte`, `tails of
length 3`, `family gap filling` and `sound language and encoding variants` -- and **none of them
could see a sound id**, because every one of them feeds candidates to `confirm_list`. The run
returned 737 names and not one was a sound file.

The same is true of every generator written for this repository that pipes into `confirm_list`,
which is all of them.

## How it was worked around, so a successor need not

The previous binaries are in git and can be used without disturbing the clone:

    git checkout b51517ca -- bin/windows
    copy bin\windows\*.exe <somewhere outside the repo>
    git checkout HEAD -- bin/windows        # leave the tree clean

Run those copies instead. They resolve all six pools, at the cost of not having `99079ddf`'s
deliberate modern-model exclusion -- so also expect `xmodel` in the target list, which for MWII means
hunting 72,942 unnamed model ids with BO4/Cold War vocabulary. Harmless (every match is still proven
by hash) and merely slower.

## One thing worth fixing while in there

`canonical()` is named as though it canonicalises a kind, and it is applied to exactly one side of a
two-sided comparison in the one place that matters. Either canonicalise both sides at every call
site, or give the census a canonical form once when it is read -- `pools_for` is the single place it
is built, and canonicalising there would fix every caller at once and stop the trap being
rediscovered. The second is the better shape, and it is a three-line change to the same function the
first fix touches.