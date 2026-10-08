//! Captures every asset the loader holds, as a file anyone can confirm names against.
//!
//! This is the one tool that needs Cordycep, and it is the reason nobody else does. Confirming
//! a name asks one question -- is this hash the id of an asset the game holds -- and the answer
//! is a set of numbers. Written down once by someone who owns the game, that set lets anyone
//! else grind against it on any machine, with no game, no loader and no Windows.
//!
//! It walks pool *indexes* rather than asset types, so it needs no asset type enum and works on
//! any title the loader can open. A pool this project has no name for is still captured; it is
//! filed under its index, and someone can put a name to it later. That is what makes this
//! usable for Black Ops 4 without first working out Black Ops 4's enum.

use std::collections::BTreeSet;
use std::fmt::Write as _;
use std::fs;
use std::path::PathBuf;

use slasher::cordycep::{CordycepInstance, POOL_COUNT};
use slasher::{snapshot, ID_MASK, POOLS};

/// A full load. Well short of it means the loader is still mapping files, and a snapshot taken
/// then would silently be a fraction of the game -- which is worse than no snapshot, because
/// every name checked against it afterwards would be judged against that fraction.
const A_FULL_LOAD: usize = 100_000;

fn main() {
    let instance = match CordycepInstance::open() {
        Ok(instance) => instance,
        Err(error) => {
            eprintln!("the loader is not readable: {error}");
            eprintln!("open Cordycep with the game you want and run `loadall`, then try again.");
            return;
        }
    };

    // Whatever the loader has open. Deliberately not checked against one game: the point of this
    // tool is to work for any title, and the game it captured is recorded in the file itself so
    // a snapshot can never be mistaken for another game's.
    let game = instance.game_id();
    if slasher::games::modern(&game) {
        eprintln!("Use hash-capture for modern native pools and injected sounds; combined snapshot indexes are not live pool indexes.");
        std::process::exit(1);
    }
    println!("the loader has {game} open");

    let out = std::env::args().nth(1).map(PathBuf::from).unwrap_or_else(|| {
        PathBuf::from("snapshots").join(format!("{}.ids", game.to_lowercase()))
    });

    println!("\n{:<8} {:<26} {:>12}", "index", "type", "assets");

    // Sorted and deduplicated as it is built: the file is searched by binary search, and an id
    // held in several pools is several records rather than a lost one.
    let mut records: BTreeSet<(u64, u16)> = BTreeSet::new();
    let mut named_total = 0_usize;
    let mut unnamed_total = 0_usize;
    let mut unnamed_pools = 0_usize;

    for index in 0..POOL_COUNT {
        let mut count = 0_usize;

        for asset in instance.assets(index) {
            records.insert(((asset.id as u64) & ID_MASK, index as u16));
            count += 1;
        }

        if count == 0 {
            continue;
        }

        let name = POOLS
            .get(index)
            .map(|name| (*name).to_owned())
            .unwrap_or_else(|| format!("pool_{index} (unidentified)"));

        if index < POOLS.len() {
            named_total += count;
        } else {
            unnamed_total += count;
            unnamed_pools += 1;
        }

        println!("{index:<8} {name:<26} {count:>12}");
    }

    let total = named_total + unnamed_total;

    println!("\nin the {} pools this project names: {named_total}", POOLS.len());
    println!("in pools it does not: {unnamed_total} across {unnamed_pools} pool(s)");
    println!("total: {total}, distinct records: {}", records.len());

    if total < A_FULL_LOAD {
        eprintln!(
            "\nonly {total} assets are loaded, far short of a full load. A snapshot taken now \
             would be a fraction of the game, and every name checked against it afterwards \
             would inherit that. Run `loadall` and try again."
        );
        return;
    }

    if let Some(parent) = out.parent() {
        if let Err(error) = fs::create_dir_all(parent) {
            eprintln!("\n{} could not be made: {error}", parent.display());
            return;
        }
    }

    match snapshot::write(&out, game, records.iter().copied()) {
        Ok(bytes) => {
            println!("\nwritten to {} ({:.1} MB)", out.display(), bytes as f64 / 1e6);
            println!("this file is what someone without the game grinds against.");
        }
        Err(error) => eprintln!("\nthe snapshot could not be written: {error}"),
    }

    // A plain listing beside it, so the pools can be eyeballed and named without a reader.
    let census = out.with_extension("pools.txt");
    let mut text = String::new();
    for index in 0..POOL_COUNT {
        let count = records.iter().filter(|(_, pool)| *pool == index as u16).count();
        if count > 0 {
            let name = POOLS.get(index).copied().unwrap_or("unidentified");
            let _ = writeln!(text, "{index},{name},{count}");
        }
    }
    let _ = fs::write(&census, text);
    println!("pool census written to {}", census.display());
}
