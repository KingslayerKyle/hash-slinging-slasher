//! Checks a set of found names against what the loader actually holds.
//!
//! A name is only a fact if the game refers to it, and the evidence for that is the loader: the
//! hash of the name has to equal the id of an asset it is holding. This asks that of every row
//! and answers three things about each, because "is it loaded" on its own is not enough.
//!
//! Whether the row's own key is the hash of its own name, since a row can be wrong about itself
//! and every later check would inherit the error. Whether that hash is among the loaded ids at
//! all. And whether the type it was filed under is one the loader actually holds it in, since
//! several pools share a name's hash and a row can be genuinely loaded and still misfiled.

use std::collections::HashMap;
use std::fs;
use std::path::PathBuf;

use slasher::cordycep::CordycepInstance;
use slasher::{config, pool_index, pools_for, read_rows, ID_MASK};

/// A full load of this game. Well short of it means the loader is still mapping files, and a
/// name reported missing would be missing only because it has not got there yet.
const A_FULL_LOAD: usize = 100_000;

/// How many examples of a problem are worth printing before the count speaks for itself.
const EXAMPLES: usize = 30;

fn main() {
    let checking = std::env::args()
        .nth(1)
        .unwrap_or_else(|| slasher::paths::findings().display().to_string());

    let instance = match CordycepInstance::open() {
        Ok(instance) => instance,
        Err(error) => {
            eprintln!("the loader is not readable: {error}");
            return;
        }
    };

    // Whatever the loader actually has open, not a compile-time constant. This used to insist on
    // Cold War, so the tool simply refused on a Black Ops 4 session -- and Black Ops 4 is the game
    // most in need of checking against a live loader, because its sounds are not readable from the
    // game at all and have to be loaded from SABs separately.
    let game = instance.game_id().to_owned();
    if !config::GAMES.contains(&game.as_str()) {
        eprintln!("the loader has {game} open, which this holds no pool names for");
        return;
    }
    println!("the loader has {game} open");

    // The pool names of *that* game. The two number their asset types differently, so labelling a
    // Black Ops 4 pool index out of Cold War's enum reports the wrong type with total confidence.
    let pool_names = pools_for(&game);

    // Every pool an id appears in, since several share a name's hash.
    let mut loaded: HashMap<u64, Vec<usize>> = HashMap::new();
    let mut total = 0_usize;

    for index in 0..pool_names.len() {
        for asset in instance.assets(index) {
            total += 1;
            loaded
                .entry((asset.id as u64) & ID_MASK)
                .or_default()
                .push(index);
        }
    }

    println!("loaded assets: {total}, distinct ids: {}", loaded.len());

    if total < A_FULL_LOAD {
        eprintln!(
            "\nOnly {total} assets are loaded, far short of a full load. Any name reported \
             missing here would be missing because the loader has not got to it yet. Load \
             everything and run this again."
        );
        return;
    }

    let Ok(entries) = fs::read_dir(&checking) else {
        eprintln!("nothing to check at {checking}");
        return;
    };

    let mut files: Vec<PathBuf> = entries
        .flatten()
        .map(|entry| entry.path())
        .filter(|path| path.extension().and_then(|e| e.to_str()) == Some("txt"))
        .collect();
    files.sort();

    println!("\nchecking {checking}");
    println!(
        "\n{:<16} {:>7} {:>9} {:>10} {:>10} {:>9}",
        "file", "rows", "confirmed", "not loaded", "wrong pool", "bad key"
    );

    let mut all_rows = 0_usize;
    let mut all_good = 0_usize;
    let mut missing: Vec<(String, String)> = Vec::new();
    let mut bad_key: Vec<(String, String)> = Vec::new();
    let mut elsewhere: Vec<(String, String, String)> = Vec::new();

    for path in files {
        let kind = path
            .file_stem()
            .and_then(|s| s.to_str())
            .unwrap_or_default()
            .to_owned();

        let expected = pool_index(&kind);

        let mut rows = 0;
        let mut good = 0;
        let mut absent = 0;
        let mut misfiled = 0;
        let mut wrong_key = 0;

        for (stated, name) in read_rows(&path) {
            rows += 1;
            let actual = slasher::games::output_key(&game, &kind, &name, true);

            // The row has to be right about itself before anything else means much.
            if stated != actual {
                wrong_key += 1;
                bad_key.push((kind.clone(), name));
                continue;
            }

            match loaded.get(&(actual & ID_MASK)) {
                None => {
                    absent += 1;
                    missing.push((kind.clone(), name));
                }

                Some(pools) => {
                    if expected.is_some_and(|index| pools.contains(&index)) {
                        good += 1;
                    } else {
                        misfiled += 1;
                        let held = pools
                            .iter()
                            .map(|index| pool_names[*index])
                            .collect::<Vec<_>>()
                            .join("/");
                        elsewhere.push((kind.clone(), name, held));
                    }
                }
            }
        }

        println!("{kind:<16} {rows:>7} {good:>9} {absent:>10} {misfiled:>10} {wrong_key:>9}");
        all_rows += rows;
        all_good += good;
    }

    println!(
        "{:<16} {all_rows:>7} {all_good:>9} {:>10} {:>10} {:>9}",
        "TOTAL",
        missing.len(),
        elsewhere.len(),
        bad_key.len()
    );

    for (label, rows) in [("not loaded", &missing), ("bad key", &bad_key)] {
        if !rows.is_empty() {
            println!("\n{label}:");
            for (kind, name) in rows.iter().take(EXAMPLES) {
                println!("  {kind:<14} {name}");
            }
            if rows.len() > EXAMPLES {
                println!("  ... and {} more", rows.len() - EXAMPLES);
            }
        }
    }

    if !elsewhere.is_empty() {
        println!("\nloaded, but in a pool other than the file they are filed under:");
        for (kind, name, held) in elsewhere.iter().take(EXAMPLES) {
            println!("  filed {kind:<14} held {held:<24} {name}");
        }
        if elsewhere.len() > EXAMPLES {
            println!("  ... and {} more", elsewhere.len() - EXAMPLES);
        }
    }
}
